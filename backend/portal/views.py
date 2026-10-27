import csv
from datetime import timedelta

from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Attempt,
    AttemptAnswer,
    AuditLog,
    Batch,
    Exam,
    ExamBatch,
    ExamNotification,
    ExamQuestion,
    Option,
    ProctoringFlag,
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
        student_ids = set(
            User.objects.filter(role="STUDENT", is_active=True, batches__in=batches).values_list("id", flat=True)
        )
        ExamNotification.objects.bulk_create(
            [
                ExamNotification(student_id=student_id, exam=exam, notification_type="SCHEDULED")
                for student_id in student_ids
            ],
            ignore_conflicts=True,
        )
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



class StartAttempt(APIView):
    """Start an eligible exam without returning answer-key fields."""

    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        now = timezone.now()
        exam = get_object_or_404(
            Exam.objects.select_for_update().filter(
                batches__students=request.user,
                start_time__lte=now,
                end_time__gt=now,
                total_marks__gt=0,
            ).distinct(),
            pk=pk,
        )
        if not ExamQuestion.objects.filter(exam=exam).exists():
            raise ValidationError("This exam has no configured questions.")
        attempt, created = Attempt.objects.get_or_create(student=request.user, exam=exam)
        if created:
            AuditLog.objects.create(actor=request.user, action="ATTEMPT_STARTED", target=str(attempt.id))
        questions = (
            ExamQuestion.objects.filter(exam=exam)
            .select_related("question")
            .prefetch_related("question__options")
        )
        return Response(
            {
                "attempt_id": str(attempt.id),
                "submitted": attempt.submitted_at is not None,
                "questions": [
                    {
                        "question_id": str(row.question_id),
                        "sequence": row.sequence,
                        "text": row.question.text,
                        "marks": str(row.question.default_marks),
                        "options": [
                            {"option_id": str(option.id), "text": option.text}
                            for option in row.question.options.all()
                        ],
                    }
                    for row in questions
                ],
            },
            status=200 if not created else 201,
        )


class SubmitAttempt(APIView):
    """Evaluate answers server-side and make submission idempotent."""

    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(
            Attempt.objects.select_for_update().select_related("exam"),
            pk=pk,
            student=request.user,
        )
        if attempt.submitted_at is not None:
            return Response({"attempt_id": str(attempt.id), "submitted": True, "score": str(attempt.score)})
        now = timezone.now()
        deadline = min(
            attempt.started_at + timedelta(minutes=attempt.exam.duration_minutes),
            attempt.exam.end_time,
        )
        if now >= deadline:
            raise ValidationError("The submission deadline has passed.")
        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            raise ValidationError({"answers": "Expected a list of question_id/option_id objects."})
        submitted = {}
        for item in answers:
            if not isinstance(item, dict) or "question_id" not in item:
                raise ValidationError({"answers": "Each answer requires a question_id."})
            question_id = str(serializers.UUIDField().run_validation(item["question_id"]))
            if question_id in submitted:
                raise ValidationError({"answers": "A question may be answered only once."})
            submitted[question_id] = item.get("option_id")
        mappings = list(
            ExamQuestion.objects.filter(exam=attempt.exam)
            .select_related("question")
            .prefetch_related("question__options")
        )
        allowed = {str(row.question_id): row.question for row in mappings}
        if set(submitted) - set(allowed):
            raise ValidationError({"answers": "Answers must refer only to questions in this exam."})
        total = 0
        answer_rows = []
        for question_id, question in allowed.items():
            option_id = submitted.get(question_id)
            selected = None
            awarded = 0
            if option_id is not None:
                selected = Option.objects.filter(pk=option_id, question_id=question_id).first()
                if selected is None:
                    raise ValidationError({"answers": "Selected option does not belong to its question."})
                if selected.is_correct:
                    awarded = question.default_marks
                else:
                    awarded = -question.negative_marks
            total += awarded
            answer_rows.append(
                AttemptAnswer(attempt=attempt, question=question, selected_option=selected, awarded_marks=awarded)
            )
        # An exam cannot award a negative overall score.
        attempt.score = total
        attempt.submitted_at = now
        attempt.save(update_fields=["score", "submitted_at"])
        AttemptAnswer.objects.bulk_create(answer_rows)
        AuditLog.objects.create(actor=request.user, action="ATTEMPT_SUBMITTED", target=str(attempt.id))
        return Response({"attempt_id": str(attempt.id), "submitted": True, "score": str(attempt.score)})


class AttemptResult(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        attempt = get_object_or_404(Attempt.objects.select_related("exam"), pk=pk, student=request.user)
        if attempt.submitted_at is None:
            raise ValidationError("This attempt has not been submitted.")
        if timezone.now() < attempt.exam.result_visible_from:
            return Response({"detail": "Results are not released yet."}, status=403)
        if attempt.is_disqualified:
            return Response({"detail": "This result is currently disqualified."}, status=403)
        return Response(
            {
                "attempt_id": str(attempt.id),
                "exam_id": str(attempt.exam_id),
                "score": str(attempt.score),
                "total_marks": str(attempt.exam.total_marks),
                "submitted_at": attempt.submitted_at.isoformat(),
            }
        )


class AttemptProctoringEvent(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(Attempt.objects.select_for_update(), pk=pk, student=request.user)
        if attempt.submitted_at is not None:
            raise ValidationError("Proctoring events cannot be added after submission.")
        if attempt.is_disqualified:
            raise ValidationError("This attempt is disqualified.")
        event_type = request.data.get("event_type")
        if event_type not in {"TAB_SWITCH", "WINDOW_BLUR"}:
            raise ValidationError({"event_type": "Use TAB_SWITCH or WINDOW_BLUR."})
        raw_time = request.data.get("occurred_at")
        occurred_at = timezone.now()
        if raw_time:
            from django.utils.dateparse import parse_datetime

            parsed = parse_datetime(raw_time) if isinstance(raw_time, str) else None
            if parsed is None or timezone.is_naive(parsed):
                raise ValidationError({"occurred_at": "Use an ISO-8601 timestamp with a timezone."})
            occurred_at = parsed
        flag = ProctoringFlag.objects.create(
            attempt=attempt, event_type=event_type, occurred_at=occurred_at
        )
        AuditLog.objects.create(actor=request.user, action=f"PROCTOR_{event_type}", target=str(attempt.id))
        return Response({"event_id": str(flag.id), "event_type": flag.event_type}, status=201)


class AdminAttemptList(generics.ListAPIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Attempt.objects.select_related("student", "exam").prefetch_related("proctoring_flags")
        exam_id = request.query_params.get("exam_id")
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        return Response(
            {
                "results": [
                    {
                        "attempt_id": str(attempt.id),
                        "student_id": str(attempt.student_id),
                        "student_name": attempt.student.name,
                        "exam_id": str(attempt.exam_id),
                        "score": str(attempt.score) if attempt.score is not None else None,
                        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                        "is_disqualified": attempt.is_disqualified,
                        "flags": [
                            {"event_type": flag.event_type, "occurred_at": flag.occurred_at.isoformat()}
                            for flag in attempt.proctoring_flags.all()
                        ],
                    }
                    for attempt in queryset
                ]
            }
        )


class AdminAttemptOverride(APIView):
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(Attempt.objects.select_for_update(), pk=pk)
        disqualified = request.data.get("disqualified")
        if not isinstance(disqualified, bool):
            raise ValidationError({"disqualified": "A boolean value is required."})
        reason = request.data.get("reason", "")
        if not isinstance(reason, str) or len(reason) > 500:
            raise ValidationError({"reason": "Reason must be at most 500 characters."})
        if disqualified and not reason.strip():
            raise ValidationError({"reason": "A reason is required to disqualify an attempt."})
        attempt.is_disqualified = disqualified
        attempt.disqualification_reason = reason.strip() if disqualified else ""
        attempt.overridden_at = timezone.now()
        attempt.overridden_by = request.user
        attempt.save(
            update_fields=[
                "is_disqualified", "disqualification_reason", "overridden_at", "overridden_by"
            ]
        )
        action = "ATTEMPT_DISQUALIFIED" if disqualified else "ATTEMPT_REPERMITTED"
        AuditLog.objects.create(actor=request.user, action=action, target=str(attempt.id))
        return Response(
            {"attempt_id": str(attempt.id), "is_disqualified": attempt.is_disqualified}
        )



class AdminClassReport(APIView):
    """Class-level score summary; only released, submitted, permitted attempts count."""

    permission_classes = [IsAdmin]

    def get(self, request):
        exam = get_object_or_404(Exam, pk=request.query_params.get("exam_id"))
        if timezone.now() < exam.result_visible_from:
            raise ValidationError("Reports are unavailable until results are released.")
        attempts = (
            Attempt.objects.filter(exam=exam, submitted_at__isnull=False, is_disqualified=False)
            .select_related("student")
            .order_by("student__name", "student__usn")
        )
        rows = [
            {
                "student_id": str(attempt.student_id),
                "student_name": attempt.student.name,
                "usn": attempt.student.usn or "",
                "score": str(attempt.score),
                "total_marks": str(exam.total_marks),
            }
            for attempt in attempts
        ]
        if request.query_params.get("format") == "csv":
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="class-report.csv"'
            writer = csv.DictWriter(response, fieldnames=["student_id", "student_name", "usn", "score", "total_marks"])
            writer.writeheader()
            writer.writerows(rows)
            return response
        return Response({"exam_id": str(exam.id), "results": rows})


class AdminQuestionReport(APIView):
    """Question difficulty summary based on submitted, released and permitted attempts."""

    permission_classes = [IsAdmin]

    def get(self, request):
        exam = get_object_or_404(Exam, pk=request.query_params.get("exam_id"))
        if timezone.now() < exam.result_visible_from:
            raise ValidationError("Reports are unavailable until results are released.")
        attempts = list(
            Attempt.objects.filter(exam=exam, submitted_at__isnull=False, is_disqualified=False)
            .prefetch_related("answers__question")
        )
        mappings = ExamQuestion.objects.filter(exam=exam).select_related("question")
        rows = []
        for mapping in mappings:
            answers = [
                answer
                for attempt in attempts
                for answer in attempt.answers.all()
                if answer.question_id == mapping.question_id
            ]
            answered = len(answers)
            correct = sum(answer.awarded_marks > 0 for answer in answers)
            incorrect = sum(answer.awarded_marks < 0 for answer in answers)
            rows.append(
                {
                    "question_id": str(mapping.question_id),
                    "difficulty": mapping.question.difficulty,
                    "subject": mapping.question.subject,
                    "topic": mapping.question.topic,
                    "submitted_attempts": len(attempts),
                    "correct": correct,
                    "incorrect": incorrect,
                    "unanswered": len(attempts) - answered,
                }
            )
        if request.query_params.get("format") == "csv":
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="question-report.csv"'
            writer = csv.DictWriter(
                response,
                fieldnames=[
                    "question_id", "difficulty", "subject", "topic",
                    "submitted_attempts", "correct", "incorrect", "unanswered",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
            return response
        return Response({"exam_id": str(exam.id), "results": rows})
