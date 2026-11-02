from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class ExistingAttemptMigrationTests(TransactionTestCase):
    """The Sprint 2 additive migrations must preserve real pre-existing attempts."""

    migrate_from = ("portal", "0004_alter_examattempt_status")
    migrate_to = ("portal", "0007_attempt_disqualification_restore_state")

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps

        User = old_apps.get_model("portal", "User")
        Exam = old_apps.get_model("portal", "Exam")
        Question = old_apps.get_model("portal", "Question")
        Option = old_apps.get_model("portal", "Option")
        ExamAttempt = old_apps.get_model("portal", "ExamAttempt")
        AttemptAnswer = old_apps.get_model("portal", "AttemptAnswer")

        admin = User.objects.create(
            username="migration-admin",
            email="migration-admin@example.test",
            name="Migration Admin",
            role="ADMIN",
            password="!",
        )
        student = User.objects.create(
            username="migration-student",
            email="migration-student@example.test",
            name="Migration Student",
            role="STUDENT",
            password="!",
        )
        now = timezone.now()
        exam = Exam.objects.create(
            title="Existing attempt migration",
            duration_minutes=30,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            result_visible_from=now + timedelta(hours=1),
            total_marks="2.00",
            created_by=admin,
        )
        question = Question.objects.create(
            text="Existing question",
            subject="Migration",
            topic="Compatibility",
            difficulty="EASY",
            default_marks="2.00",
            negative_marks="0.50",
            created_by=admin,
        )
        option = Option.objects.create(question=question, text="Saved option", is_correct=True)
        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=student,
            status="SUBMITTED",
            deadline_at=now - timedelta(minutes=30),
            submitted_at=now - timedelta(minutes=30),
        )
        answer = AttemptAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option_id=option.id,
        )
        self.attempt_id = attempt.id
        self.student_id = student.id
        self.answer_id = answer.id
        self.question_id = question.id
        self.option_id = option.id
        self.deadline_at = attempt.deadline_at
        self.submitted_at = attempt.submitted_at
        self.saved_at = answer.saved_at

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        self.apps = executor.loader.project_state([self.migrate_to]).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_attempt_and_saved_answer_survive_additive_migrations(self):
        ExamAttempt = self.apps.get_model("portal", "ExamAttempt")
        AttemptAnswer = self.apps.get_model("portal", "AttemptAnswer")
        NotificationOutbox = self.apps.get_model("portal", "NotificationOutbox")
        ScheduledExamNotification = self.apps.get_model("portal", "ScheduledExamNotification")

        attempt = ExamAttempt.objects.get(pk=self.attempt_id)
        answer = AttemptAnswer.objects.get(pk=self.answer_id)
        self.assertEqual(attempt.student_id, self.student_id)
        self.assertEqual(attempt.status, "SUBMITTED")
        self.assertEqual(attempt.deadline_at, self.deadline_at)
        self.assertEqual(attempt.submitted_at, self.submitted_at)
        self.assertEqual(answer.question_id, self.question_id)
        self.assertEqual(answer.selected_option_id, self.option_id)
        self.assertEqual(answer.saved_at, self.saved_at)
        self.assertIsNone(attempt.score)
        self.assertIsNone(attempt.evaluated_at)
        self.assertEqual(attempt.disqualification_reason, "")
        self.assertEqual(attempt.status_before_disqualification, "")
        self.assertEqual(NotificationOutbox.objects.count(), 0)
        self.assertEqual(ScheduledExamNotification.objects.count(), 0)
