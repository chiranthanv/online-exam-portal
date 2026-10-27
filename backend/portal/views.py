import uuid
from datetime import timedelta

from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AttemptAnswer,
    AuditLog,
    Batch,
    Exam,
    ExamAttempt,
    ExamBatch,
    ExamQuestion,
    Option,
    Question,
    StudentBatch,
    User,
)
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


def _expire_attempt_if_due(attempt, now=None):
    now = now or timezone.now()
    if attempt.status == ExamAttempt.IN_PROGRESS and now >= attempt.deadline_at:
        attempt.status = ExamAttempt.AUTO_SUBMITTED
        attempt.submitted_at = now
        attempt.save(update_fields=["status", "submitted_at"])
        AuditLog.objects.create(
            actor=attempt.student,
            action="EXAM_ATTEMPT_AUTO_SUBMITTED",
            target=str(attempt.id),
        )
    return attempt


def _require_attempt_session(request, attempt):
    value = request.headers.get("X-Exam-Session", "")
    try:
        session_key = uuid.UUID(value)
    except (TypeError, ValueError, AttributeError):
        raise Conflict("This attempt session is missing or invalid. Reopen the same exam session.")
    if session_key != attempt.session_key:
        raise Conflict("This attempt is active in another session. Return to the original exam session.")
    return attempt


def _attempt_payload(attempt):
    server_now = timezone.now()
    mappings = (
        ExamQuestion.objects.filter(exam=attempt.exam)
        .select_related("question")
        .prefetch_related("question__options")
        .order_by("sequence")
    )
    saved = {
        str(answer.question_id): (
            str(answer.selected_option_id) if answer.selected_option_id else None
        )
        for answer in attempt.answers.all()
    }
    questions = []
    for mapping in mappings:
        question = mapping.question
        questions.append(
            {
                "id": str(question.id),
                "sequence": mapping.sequence,
                "text": question.text,
                "subject": question.subject,
                "topic": question.topic,
                "marks": str(question.default_marks),
                "options": [
                    {"id": str(option.id), "text": option.text}
                    for option in question.options.all()
                ],
                "selected_option_id": saved.get(str(question.id)),
            }
        )
    return {
        "attempt_id": str(attempt.id),
        "exam_id": str(attempt.exam_id),
        "exam_title": attempt.exam.title,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat(),
        "deadline_at": attempt.deadline_at.isoformat(),
        "server_now": server_now.isoformat(),
        "remaining_seconds": max(0, int((attempt.deadline_at - server_now).total_seconds() + 0.999)),
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "last_saved_at": attempt.last_saved_at.isoformat() if attempt.last_saved_at else None,
        "answers": saved,
        "questions": questions,
    }


class StudentExamAttempt(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        try:
            session_key = uuid.UUID(str(request.data.get("session_id", "")))
            header_session = uuid.UUID(request.headers.get("X-Exam-Session", ""))
        except (TypeError, ValueError, AttributeError):
            raise ValidationError(
                {"session_id": "Provide the same valid UUID in session_id and X-Exam-Session."}
            )
        if header_session != session_key:
            raise Conflict("The exam session header does not match the requested session.")

        exam = get_object_or_404(Exam.objects.select_for_update(), pk=pk)
        attempt = (
            ExamAttempt.objects.select_for_update()
            .filter(exam=exam, student=request.user)
            .first()
        )
        now = timezone.now()
        if attempt:
            _expire_attempt_if_due(attempt, now)
            _require_attempt_session(request, attempt)
            # The body session ID is also checked during resume/start.
            if session_key != attempt.session_key:
                raise Conflict("An attempt already exists in another session for this exam.")
            return Response(_attempt_payload(attempt))

        if not exam.start_time <= now < exam.end_time:
            raise ValidationError("This exam is outside its scheduled availability window.")
        if exam.total_marks <= 0 or not exam.questions.exists():
            raise ValidationError("This exam is not ready to be attempted.")
        if not ExamBatch.objects.filter(exam=exam, batch__students=request.user).exists():
            raise ValidationError("This exam is not assigned to your batch.")
        deadline = min(now + timedelta(minutes=exam.duration_minutes), exam.end_time)
        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=request.user,
            session_key=session_key,
            started_at=now,
            deadline_at=deadline,
        )
        AuditLog.objects.create(
            actor=request.user, action="EXAM_ATTEMPT_STARTED", target=str(attempt.id)
        )
        return Response(_attempt_payload(attempt), status=201)


class ExamAttemptDetail(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def get(self, request, pk):
        attempt = get_object_or_404(
            ExamAttempt.objects.select_for_update().select_related("exam"),
            pk=pk,
            student=request.user,
        )
        _require_attempt_session(request, attempt)
        _expire_attempt_if_due(attempt)
        return Response(_attempt_payload(attempt))


class ExamAttemptAnswers(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def patch(self, request, pk):
        attempt = get_object_or_404(
            ExamAttempt.objects.select_for_update().select_related("exam"),
            pk=pk,
            student=request.user,
        )
        _require_attempt_session(request, attempt)
        _expire_attempt_if_due(attempt)
        if attempt.status != ExamAttempt.IN_PROGRESS:
            raise Conflict("This attempt is already submitted; answers can no longer be changed.")

        try:
            question_id = uuid.UUID(str(request.data.get("question_id", "")))
        except (TypeError, ValueError, AttributeError):
            raise ValidationError({"question_id": "Provide a valid question UUID."})
        if not ExamQuestion.objects.filter(exam=attempt.exam, question_id=question_id).exists():
            raise ValidationError({"question_id": "This question is not part of the attempt."})
        if "option_id" not in request.data:
            raise ValidationError({"option_id": "Provide an option UUID or null to clear the answer."})
        option_value = request.data.get("option_id")
        option_id = None
        if option_value is not None:
            try:
                option_id = uuid.UUID(str(option_value))
            except (TypeError, ValueError, AttributeError):
                raise ValidationError({"option_id": "Provide a valid option UUID or null."})
            if not Option.objects.filter(pk=option_id, question_id=question_id).exists():
                raise ValidationError({"option_id": "The option does not belong to this question."})

        AttemptAnswer.objects.update_or_create(
            attempt=attempt,
            question_id=question_id,
            defaults={"selected_option_id": option_id},
        )
        attempt.last_saved_at = timezone.now()
        attempt.save(update_fields=["last_saved_at"])
        return Response(
            {
                "question_id": str(question_id),
                "selected_option_id": str(option_id) if option_id else None,
                "saved_at": attempt.last_saved_at.isoformat(),
                "deadline_at": attempt.deadline_at.isoformat(),
            }
        )


class ExamAttemptSubmit(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(
            ExamAttempt.objects.select_for_update().select_related("exam"),
            pk=pk,
            student=request.user,
        )
        _require_attempt_session(request, attempt)
        now = timezone.now()
        _expire_attempt_if_due(attempt, now)
        if attempt.status == ExamAttempt.IN_PROGRESS:
            attempt.status = ExamAttempt.SUBMITTED
            attempt.submitted_at = now
            attempt.save(update_fields=["status", "submitted_at"])
            AuditLog.objects.create(
                actor=request.user, action="EXAM_ATTEMPT_SUBMITTED", target=str(attempt.id)
            )
        return Response(_attempt_payload(attempt))


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "actor", "action", "target", "timestamp"]
        read_only_fields = fields


class AuditList(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AuditSerializer
    queryset = AuditLog.objects.all()
