from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, Batch, Exam, ExamBatch, ExamQuestion, Question, StudentBatch, User
from .permissions import IsAdmin, IsStudent
from .roster import import_roster
from .serializers import (
    BatchIDsSerializer,
    BatchSerializer,
    ExamSerializer,
    IDListSerializer,
    QuestionSelectionSerializer,
    QuestionSerializer,
    UserSerializer,
)
from .services import require_not_started, select_questions


class Conflict(APIException):
    status_code = 409
    default_detail = "This resource is in use."


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({"status": "ok"})


class StudentList(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.filter(role="STUDENT").prefetch_related("batches").order_by("name", "id")


class BulkImport(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "A CSV or XLSX file is required."})
        result = import_roster(upload, request.user)
        return Response(result, status=207 if result["errors"] else 201)


class BatchList(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = BatchSerializer
    queryset = Batch.objects.prefetch_related("students").all()

    @transaction.atomic
    def perform_create(self, serializer):
        batch = serializer.save()
        AuditLog.objects.create(actor=self.request.user, action="BATCH_CREATED", target=str(batch.id))


class BatchStudents(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        batch = get_object_or_404(Batch, pk=pk)
        return Response(
            {
                "batch_id": str(pk),
                "students": UserSerializer(batch.students.prefetch_related("batches"), many=True).data,
            }
        )

    @transaction.atomic
    def post(self, request, pk):
        batch = get_object_or_404(Batch.objects.select_for_update(), pk=pk)
        payload = IDListSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        ids = set(payload.validated_data["student_ids"])
        students = list(User.objects.filter(pk__in=ids, role="STUDENT", is_active=True))
        if len(students) != len(ids):
            raise ValidationError("Every ID must identify an active student.")
        mapped = 0
        for student in students:
            _, created = StudentBatch.objects.get_or_create(batch=batch, student=student)
            mapped += int(created)
        AuditLog.objects.create(actor=request.user, action="BATCH_STUDENTS_ADDED", target=str(pk))
        return Response({"batch_id": str(pk), "mapped": mapped})


class QuestionList(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        query = Question.objects.prefetch_related("options").all()
        for field in ("subject", "topic", "difficulty"):
            value = self.request.query_params.get(field)
            if value:
                if field == "difficulty" and value not in ("EASY", "MEDIUM", "HARD"):
                    raise ValidationError({"difficulty": "Use EASY, MEDIUM or HARD."})
                query = query.filter(**{field: value})
        return query

    @transaction.atomic
    def perform_create(self, serializer):
        question = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(actor=self.request.user, action="QUESTION_CREATED", target=str(question.id))


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = QuestionSerializer
    queryset = Question.objects.prefetch_related("options").all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        question = get_object_or_404(Question.objects.select_for_update(), pk=kwargs["pk"])
        if ExamQuestion.objects.filter(question=question).exists():
            raise Conflict(
                "Question belongs to an exam. Create a new question or remove its exam mappings first."
            )
        payload = self.get_serializer(question, data=request.data, partial=kwargs.get("partial", False))
        payload.is_valid(raise_exception=True)
        payload.save()
        AuditLog.objects.create(actor=request.user, action="QUESTION_UPDATED", target=str(question.id))
        return Response(payload.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        question = get_object_or_404(Question.objects.select_for_update(), pk=kwargs["pk"])
        if ExamQuestion.objects.filter(question=question).exists():
            raise Conflict("Question belongs to an exam and cannot be deleted.")
        target = str(question.id)
        question.delete()
        AuditLog.objects.create(actor=request.user, action="QUESTION_DELETED", target=target)
        return Response(status=204)


class ExamList(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ExamSerializer
    queryset = Exam.objects.prefetch_related("questions", "batches").all()

    @transaction.atomic
    def perform_create(self, serializer):
        if serializer.validated_data["start_time"] <= timezone.now():
            raise ValidationError("Schedule a future start time before configuring questions and batches.")
        exam = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(actor=self.request.user, action="EXAM_CREATED", target=str(exam.id))


class ExamDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ExamSerializer
    queryset = Exam.objects.prefetch_related("questions", "batches").all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam.objects.select_for_update(), pk=kwargs["pk"])
        require_not_started(exam)
        payload = self.get_serializer(exam, data=request.data, partial=kwargs.get("partial", False))
        payload.is_valid(raise_exception=True)
        if payload.validated_data.get("start_time", exam.start_time) <= timezone.now():
            raise ValidationError("Start time must remain in the future.")
        payload.save()
        AuditLog.objects.create(actor=request.user, action="EXAM_UPDATED", target=str(exam.id))
        return Response(payload.data)


class ExamQuestions(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        mappings = (
            ExamQuestion.objects.filter(exam=exam)
            .select_related("question")
            .prefetch_related("question__options")
        )
        return Response(
            {
                "exam_id": str(pk),
                "results": [dict(QuestionSerializer(x.question).data, sequence=x.sequence) for x in mappings],
            }
        )

    def post(self, request, pk):
        payload = QuestionSelectionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        get_object_or_404(Exam, pk=pk)
        exam = select_questions(pk, payload.validated_data, request.user)
        return Response(
            {
                "exam_id": str(pk),
                "question_count": exam.questions.count(),
                "total_marks": str(exam.total_marks),
            }
        )


class ExamBatches(APIView):
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request, pk):
        exam = get_object_or_404(Exam.objects.select_for_update(), pk=pk)
        require_not_started(exam)
        payload = BatchIDsSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        ids = set(payload.validated_data["batch_ids"])
        batches = list(Batch.objects.filter(pk__in=ids))
        if len(batches) != len(ids):
            raise ValidationError("One or more batch IDs do not exist.")
        # Replace the assignment set atomically, matching question selection semantics.
        ExamBatch.objects.filter(exam=exam).delete()
        ExamBatch.objects.bulk_create([ExamBatch(exam=exam, batch=b) for b in batches])
        AuditLog.objects.create(actor=request.user, action="EXAM_BATCHES_SET", target=str(pk))
        return Response({"exam_id": str(pk), "batches_assigned": len(batches)})


class AvailableExams(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        now = timezone.now()
        exams = Exam.objects.filter(
            batches__students=request.user, start_time__lte=now, end_time__gt=now, total_marks__gt=0
        ).distinct()
        return Response(
            {
                "results": [
                    {
                        "exam_id": str(e.id),
                        "title": e.title,
                        "start_time": e.start_time.isoformat(),
                        "end_time": e.end_time.isoformat(),
                        "duration_minutes": e.duration_minutes,
                    }
                    for e in exams
                ]
            }
        )


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "actor", "action", "target", "timestamp"]
        read_only_fields = fields


class AuditList(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AuditSerializer
    queryset = AuditLog.objects.all()
