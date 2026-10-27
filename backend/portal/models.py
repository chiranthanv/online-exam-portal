import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=150, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=10, choices=[("ADMIN", "Admin"), ("STUDENT", "Student")], default="STUDENT"
    )
    usn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    failed_logins = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    auth_version = models.PositiveIntegerField(default=0)
    must_reset_password = models.BooleanField(default=False)

    class Meta:
        db_table = "users"
        constraints = [models.UniqueConstraint(Lower("email"), name="unique_email_casefold")]


class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    year = models.PositiveIntegerField()
    students = models.ManyToManyField(User, through="StudentBatch", related_name="batches")

    class Meta:
        db_table = "batches"
        ordering = ["name"]


class StudentBatch(models.Model):
    pk = models.CompositePrimaryKey("student_id", "batch_id")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    class Meta:
        db_table = "student_batches"


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    subject = models.CharField(max_length=50)
    topic = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=6, choices=[(x, x) for x in ["EASY", "MEDIUM", "HARD"]])
    default_marks = models.DecimalField(max_digits=5, decimal_places=2)
    negative_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions"
        ordering = ["created_at", "id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(default_marks__gt=0), name="positive_question_marks"),
            models.CheckConstraint(condition=models.Q(negative_marks__gte=0), name="nonnegative_penalty"),
        ]


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "options"
        ordering = ["id"]


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    duration_minutes = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    result_visible_from = models.DateTimeField()
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    questions = models.ManyToManyField(Question, through="ExamQuestion")
    batches = models.ManyToManyField(Batch, through="ExamBatch")

    class Meta:
        db_table = "exams"
        ordering = ["start_time", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")), name="exam_end_after_start"
            ),
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gte=1), name="positive_exam_duration"
            ),
        ]


class ExamQuestion(models.Model):
    pk = models.CompositePrimaryKey("exam_id", "question_id")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    sequence = models.PositiveIntegerField()

    class Meta:
        db_table = "exam_questions"
        ordering = ["sequence"]
        constraints = [models.UniqueConstraint(fields=["exam", "sequence"], name="unique_exam_sequence")]


class ExamBatch(models.Model):
    pk = models.CompositePrimaryKey("exam_id", "batch_id")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)

    class Meta:
        db_table = "exam_batches"


class ExamAttempt(models.Model):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    AUTO_SUBMITTED = "AUTO_SUBMITTED"
    STATUS_CHOICES = [
        (IN_PROGRESS, "In progress"),
        (SUBMITTED, "Submitted"),
        (AUTO_SUBMITTED, "Automatically submitted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="attempts")
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name="exam_attempts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    started_at = models.DateTimeField(default=timezone.now)
    deadline_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_saved_at = models.DateTimeField(null=True, blank=True)
    session_key = models.UUIDField(default=uuid.uuid4)

    class Meta:
        db_table = "exam_attempts"
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "student"], name="unique_exam_attempt_per_student")
        ]


class AttemptAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_option_id = models.UUIDField(null=True, blank=True)
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attempt_answers"
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_answer_per_attempt_question")
        ]


class ImmutableAuditQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Audit records are append-only.")

    def delete(self):
        raise ValueError("Audit records are append-only.")


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = ImmutableAuditQuerySet.as_manager()

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp", "-id"]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Audit records are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit records are append-only.")


class PasswordResetGrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "password_reset_grants"
