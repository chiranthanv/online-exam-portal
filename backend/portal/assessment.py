from decimal import Decimal

from django.utils import timezone

from .models import ExamAttempt, Option


def evaluate_attempt(attempt, now=None):
    """Score saved answers exactly once using correct marks minus wrong-answer penalties."""
    if attempt.status not in {ExamAttempt.SUBMITTED, ExamAttempt.AUTO_SUBMITTED}:
        return False
    if attempt.evaluated_at is not None:
        return False

    score = Decimal("0.00")
    for answer in attempt.answers.select_related("question"):
        if answer.selected_option_id is None:
            continue
        selected = (
            Option.objects.filter(
                pk=answer.selected_option_id,
                question_id=answer.question_id,
            )
            .only("is_correct")
            .first()
        )
        if selected is not None and selected.is_correct:
            score += answer.question.default_marks
        else:
            score -= answer.question.negative_marks

    attempt.score = score
    attempt.evaluated_at = now or timezone.now()
    attempt.save(update_fields=["status", "submitted_at", "score", "evaluated_at"])
    return True
