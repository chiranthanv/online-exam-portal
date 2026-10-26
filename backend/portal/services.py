import random
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import AuditLog, Exam, ExamQuestion, Question


def require_not_started(exam):
    if timezone.now() >= exam.start_time:
        raise ValidationError("This exam has started; its schedule, questions and batches are frozen.")


@transaction.atomic
def select_questions(exam_id, data, actor):
    exam = Exam.objects.select_for_update().get(pk=exam_id)
    require_not_started(exam)
    # Question-row locks also synchronize with question edits/deletion.
    if data["mode"] == "manual":
        ids = data["question_ids"]
        questions = list(Question.objects.select_for_update().filter(pk__in=ids).order_by("id"))
        if len(questions) != len(ids):
            raise ValidationError("One or more question IDs do not exist.")
        lookup = {q.id: q for q in questions}
        questions = [lookup[pk] for pk in ids]
    else:
        pool = Question.objects.all()
        for field in ("subject", "topic"):
            if field in data:
                pool = pool.filter(**{field: data[field]})
        pool = list(pool.select_for_update().order_by("id"))
        rng = random.SystemRandom()
        mix = data.get("difficulty_mix")
        if mix is None:
            if len(pool) < data["random_count"]:
                raise ValidationError("Not enough matching questions.")
            questions = rng.sample(pool, data["random_count"])
        else:
            questions = []
            for difficulty, count in sorted(mix.items()):
                candidates = [q for q in pool if q.difficulty == difficulty]
                if len(candidates) < count:
                    raise ValidationError(f"Not enough {difficulty} questions.")
                questions.extend(rng.sample(candidates, count))
            rng.shuffle(questions)
    total = sum((q.default_marks for q in questions), Decimal("0"))
    if total > Decimal("9999.99"):
        raise ValidationError("Exam total exceeds 9999.99 marks.")
    ExamQuestion.objects.filter(exam=exam).delete()
    ExamQuestion.objects.bulk_create(
        [ExamQuestion(exam=exam, question=q, sequence=i) for i, q in enumerate(questions, 1)]
    )
    exam.total_marks = total
    exam.save(update_fields=["total_marks"])
    AuditLog.objects.create(actor=actor, action="EXAM_QUESTIONS_SET", target=str(exam.id))
    return exam
