import csv
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, Exam, ExamAttempt, ExamQuestion, Option, ProctoringEvent
from .permissions import IsAdmin, IsStudent


def _report_rows(exam):
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status__in=[ExamAttempt.SUBMITTED, ExamAttempt.AUTO_SUBMITTED],
        submitted_at__isnull=False,
        evaluated_at__isnull=False,
    ).filter(disqualification_reason="").select_related("student").order_by("student__name", "student__usn")
    return [
        {
            "attempt_id": str(a.id),
            "student_id": str(a.student_id),
            "student_name": a.student.name,
            "usn": a.student.usn or "",
            "score": str(a.score or "0.00"),
            "total_marks": str(exam.total_marks),
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else "",
        }
        for a in attempts
    ]


def _export(request, title, fields, rows, filename):
    kind = request.query_params.get("export", "").lower()
    if kind == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        return response
    if kind == "pdf":
        try:
            from xml.sax.saxutils import escape

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as exc:
            raise ValidationError("PDF export dependency is not installed.") from exc
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        data = [[Paragraph(escape(str(v)), styles["BodyText"]) for v in fields]]
        data.extend([[Paragraph(escape(str(row.get(k, ""))), styles["BodyText"]) for k in fields] for row in rows])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        doc.build([Paragraph(escape(title), styles["Title"]), Spacer(1, 12), table])
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return response
    if kind:
        raise ValidationError({"export": "Use csv or pdf."})
    return None


class AttemptResult(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        attempt = get_object_or_404(ExamAttempt.objects.select_related("exam"), pk=pk, student=request.user)
        if attempt.status == ExamAttempt.IN_PROGRESS or attempt.submitted_at is None:
            raise ValidationError("This attempt has not been submitted.")
        if attempt.disqualification_reason:
            return Response({"detail": "This result is withheld by an administrator."}, status=403)
        if timezone.now() < attempt.exam.result_visible_from:
            return Response({"detail": "Results are not released yet.", "result_visible_from": attempt.exam.result_visible_from}, status=403)
        return Response({
            "attempt_id": str(attempt.id),
            "exam_id": str(attempt.exam_id),
            "score": str(attempt.score or "0.00"),
            "total_marks": str(attempt.exam.total_marks),
            "submitted_at": attempt.submitted_at.isoformat(),
            "evaluated_at": attempt.evaluated_at.isoformat() if attempt.evaluated_at else None,
        })


class AttemptProctoringEvent(APIView):
    permission_classes = [IsStudent]

    def post(self, request, pk):
        attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user)
        if request.headers.get("X-Exam-Session") != str(attempt.session_key):
            return Response({"detail": "Invalid exam session."}, status=409)
        if attempt.status != ExamAttempt.IN_PROGRESS:
            raise ValidationError("Proctoring events are accepted only during an active attempt.")
        event_type = request.data.get("event_type")
        if event_type not in {ProctoringEvent.TAB_SWITCH, ProctoringEvent.WINDOW_BLUR}:
            raise ValidationError({"event_type": "Use TAB_SWITCH or WINDOW_BLUR."})
        occurred_at = timezone.now()
        raw = request.data.get("occurred_at")
        if raw:
            occurred_at = parse_datetime(raw) if isinstance(raw, str) else None
            if occurred_at is None or timezone.is_naive(occurred_at):
                raise ValidationError({"occurred_at": "Use a timezone-aware ISO-8601 timestamp."})
        event = ProctoringEvent.objects.create(attempt=attempt, event_type=event_type, occurred_at=occurred_at)
        AuditLog.objects.create(actor=request.user, action="PROCTOR_" + event_type, target=str(attempt.id))
        return Response({"event_id": str(event.id), "event_type": event.event_type}, status=201)


class AdminAttemptList(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = ExamAttempt.objects.select_related("student", "exam").prefetch_related("proctoring_events")
        exam_id = request.query_params.get("exam_id")
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        results = []
        for attempt in queryset.order_by("-started_at"):
            results.append({
                "attempt_id": str(attempt.id),
                "student_id": str(attempt.student_id),
                "student_name": attempt.student.name,
                "exam_id": str(attempt.exam_id),
                "status": attempt.status,
                "score": str(attempt.score) if attempt.score is not None else None,
                "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                "disqualification_reason": attempt.disqualification_reason,
                "flags": [{"event_type": e.event_type, "occurred_at": e.occurred_at.isoformat()} for e in attempt.proctoring_events.all()],
            })
        return Response({"results": results})


class AdminAttemptOverride(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        from django.db import transaction
        with transaction.atomic():
            attempt = get_object_or_404(ExamAttempt.objects.select_for_update(), pk=pk)
            disqualified = request.data.get("disqualified")
            reason = request.data.get("reason", "")
            if not isinstance(disqualified, bool):
                raise ValidationError({"disqualified": "A boolean value is required."})
            if not isinstance(reason, str) or len(reason) > 500:
                raise ValidationError({"reason": "Reason must be at most 500 characters."})
            if disqualified:
                if attempt.status not in {ExamAttempt.SUBMITTED, ExamAttempt.AUTO_SUBMITTED, ExamAttempt.DISQUALIFIED}:
                    raise ValidationError("Only terminal attempts can be disqualified.")
                if not reason.strip():
                    raise ValidationError({"reason": "A reason is required."})
                attempt.status = ExamAttempt.DISQUALIFIED
                attempt.disqualification_reason = reason.strip()
                action = "ATTEMPT_DISQUALIFIED"
            else:
                if attempt.status != ExamAttempt.DISQUALIFIED:
                    raise ValidationError("This attempt is not disqualified.")
                attempt.status = ExamAttempt.SUBMITTED if attempt.submitted_at else ExamAttempt.AUTO_SUBMITTED
                attempt.disqualification_reason = ""
                action = "ATTEMPT_REPERMITTED"
            attempt.overridden_at = timezone.now()
            attempt.overridden_by = request.user
            attempt.save(update_fields=["status", "disqualification_reason", "overridden_at", "overridden_by"])
            AuditLog.objects.create(actor=request.user, action=action, target=str(attempt.id))
        return Response({"attempt_id": str(attempt.id), "status": attempt.status, "disqualified": bool(attempt.disqualification_reason)})


class AdminClassReport(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        exam = get_object_or_404(Exam, pk=request.query_params.get("exam_id"))
        if timezone.now() < exam.result_visible_from:
            raise ValidationError("Reports are unavailable until the scheduled result release.")
        fields = ["attempt_id", "student_id", "student_name", "usn", "score", "total_marks", "submitted_at"]
        rows = _report_rows(exam)
        exported = _export(request, "Class report — " + exam.title, fields, rows, "class-report")
        return exported or Response({"exam_id": str(exam.id), "results": rows})


class AdminQuestionReport(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        exam = get_object_or_404(Exam, pk=request.query_params.get("exam_id"))
        if timezone.now() < exam.result_visible_from:
            raise ValidationError("Reports are unavailable until the scheduled result release.")
        attempts = list(ExamAttempt.objects.filter(
            exam=exam, status__in=[ExamAttempt.SUBMITTED, ExamAttempt.AUTO_SUBMITTED],
            submitted_at__isnull=False, evaluated_at__isnull=False, disqualification_reason=""
        ).prefetch_related("answers"))
        rows = []
        for mapping in ExamQuestion.objects.filter(exam=exam).select_related("question").order_by("sequence"):
            answers = [a for attempt in attempts for a in attempt.answers.all() if a.question_id == mapping.question_id]
            selected = [a for a in answers if a.selected_option_id is not None]
            correct = sum(1 for a in selected if Option.objects.filter(pk=a.selected_option_id, question_id=a.question_id, is_correct=True).exists())
            rows.append({
                "question_id": str(mapping.question_id), "difficulty": mapping.question.difficulty,
                "subject": mapping.question.subject, "topic": mapping.question.topic,
                "submitted_attempts": len(attempts), "correct": correct,
                "incorrect": len(selected) - correct, "unanswered": len(attempts) - len(selected),
            })
        fields = ["question_id", "difficulty", "subject", "topic", "submitted_attempts", "correct", "incorrect", "unanswered"]
        exported = _export(request, "Question report — " + exam.title, fields, rows, "question-report")
        return exported or Response({"exam_id": str(exam.id), "results": rows})
