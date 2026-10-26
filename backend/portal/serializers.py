from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Batch, Exam, Option, Question, User


class UserSerializer(serializers.ModelSerializer):
    batch_ids = serializers.PrimaryKeyRelatedField(source="batches", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "usn", "role", "batch_ids", "must_reset_password"]
        read_only_fields = fields


class BatchSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(source="students.count", read_only=True)

    class Meta:
        model = Batch
        fields = ["id", "name", "year", "student_count"]

    def validate_year(self, value):
        if not 2000 <= value <= 2100:
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return value


class OptionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=2000)

    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    text = serializers.CharField(max_length=10000)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "subject",
            "topic",
            "difficulty",
            "default_marks",
            "negative_marks",
            "options",
        ]

    def validate(self, data):
        options = data.get("options")
        if options is not None:
            if any("text" not in x for x in options):
                raise serializers.ValidationError("Each replacement option requires text.")
            if not 2 <= len(options) <= 6 or sum(x.get("is_correct", False) for x in options) != 1:
                raise serializers.ValidationError("Provide 2–6 options with exactly one correct answer.")
            if len({x["text"].strip().casefold() for x in options}) != len(options):
                raise serializers.ValidationError("Option text must be distinct.")
        if data.get("default_marks", Decimal("1")) <= 0 or data.get("negative_marks", Decimal("0")) < 0:
            raise serializers.ValidationError(
                "Marks must be positive and the negative-mark penalty cannot be negative."
            )
        return data

    @transaction.atomic
    def create(self, data):
        options = data.pop("options")
        question = Question.objects.create(**data)
        Option.objects.bulk_create([Option(question=question, **x) for x in options])
        return question

    @transaction.atomic
    def update(self, instance, data):
        options = data.pop("options", None)
        instance = super().update(instance, data)
        if options is not None:
            instance.options.all().delete()
            Option.objects.bulk_create([Option(question=instance, **x) for x in options])
        return instance


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions.count", read_only=True)
    batch_ids = serializers.PrimaryKeyRelatedField(source="batches", many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "duration_minutes",
            "start_time",
            "end_time",
            "result_visible_from",
            "total_marks",
            "question_count",
            "batch_ids",
        ]
        read_only_fields = ["total_marks"]

    def validate(self, data):
        def value(name):
            return data.get(name, getattr(self.instance, name, None))

        duration, start, end = value("duration_minutes"), value("start_time"), value("end_time")
        if duration is not None and not 1 <= duration <= 1440:
            raise serializers.ValidationError("Duration must be between 1 and 1440 minutes.")
        if start and end and end <= start:
            raise serializers.ValidationError("End time must be after start time.")
        # A short remaining exam window is allowed; the future attempt engine must
        # use min(started_at + duration, exam.end_time) as its authoritative deadline.
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=256, trim_whitespace=False)


class IDListSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False, max_length=1000)


class BatchIDsSerializer(serializers.Serializer):
    batch_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False, max_length=1000)


class QuestionSelectionSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["manual", "random"])
    question_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=False, max_length=500
    )
    random_count = serializers.IntegerField(required=False, min_value=1, max_value=500)
    subject = serializers.CharField(required=False, max_length=50)
    topic = serializers.CharField(required=False, max_length=50)
    difficulty_mix = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=500), required=False
    )

    def validate(self, data):
        if data["mode"] == "manual":
            ids = data.get("question_ids", [])
            if not ids or len(set(ids)) != len(ids):
                raise serializers.ValidationError("Supply distinct question_ids for manual selection.")
        else:
            count = data.get("random_count")
            mix = data.get("difficulty_mix")
            if count is None:
                raise serializers.ValidationError("random_count is required.")
            if mix is not None and (set(mix) - {"EASY", "MEDIUM", "HARD"} or sum(mix.values()) != count):
                raise serializers.ValidationError(
                    "difficulty_mix must use EASY/MEDIUM/HARD and sum to random_count."
                )
        return data
