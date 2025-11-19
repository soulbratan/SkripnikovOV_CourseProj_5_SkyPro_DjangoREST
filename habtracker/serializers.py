from rest_framework import serializers
from .models import Habit, HabitCompletion
from .validators import validate_habit
from django.core.exceptions import ValidationError


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = [
            "id", "user", "place", "time", "action", "is_pleasant",
            "related_habit", "frequency", "reward", "duration",
            "is_public", "created_at"
        ]
        read_only_fields = ["user", "created_at"]

    def validate(self, data):
        instance = Habit(**data)
        try:
            validate_habit(instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек"""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id", "user_email", "place", "time", "action",
            "frequency", "duration", "created_at"
        ]
        read_only_fields = fields


class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = ["id", "habit", "completed_at", "is_successful"]
        read_only_fields = ["completed_at"]
