from rest_framework import serializers
from .models import Habit
from .validators import (
    validate_execution_time,
    validate_periodicity,
    validate_related_habit_or_reward,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_no_reward_or_related
)
from users.serializers import PublicUserSerializer


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    time_only = serializers.TimeField(source='time.time', read_only=True)
    date_only = serializers.DateField(source='time.date', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'owner', 'place', 'time', 'time_only', 'date_only', 'action', 'is_pleasant',
            'related_habit', 'periodicity', 'reward', 'execution_time',
            'is_public', 'created_at', 'last_completed'
        ]
        read_only_fields = ('owner', 'created_at', 'last_completed', 'time_only', 'date_only')

    def validate(self, data):
        """Дополнительная валидация в сериализаторе"""
        # Создаем временный объект для валидации
        habit = Habit(**data)
        habit.owner = self.context['request'].user

        # Если это обновление, используем существующий экземпляр
        if self.instance:
            for attr, value in data.items():
                setattr(self.instance, attr, value)
            habit = self.instance

        # Применяем валидаторы
        validate_related_habit_or_reward(habit)
        validate_related_habit_is_pleasant(habit)
        validate_pleasant_habit_no_reward_or_related(habit)

        # Валидация отдельных полей
        execution_time = data.get('execution_time')
        if execution_time:
            validate_execution_time(execution_time)

        periodicity = data.get('periodicity', habit.periodicity)
        validate_periodicity(periodicity)

        return data

    def create(self, validated_data):
        """Создание привычки с автоматическим назначением владельца"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек"""

    owner = PublicUserSerializer(read_only=True)
    time_only = serializers.TimeField(source='time.time', read_only=True)
    date_only = serializers.DateField(source='time.date', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'owner', 'place', 'time', 'time_only', 'date_only', 'action',
            'execution_time', 'is_public', 'periodicity', 'is_pleasant'
        ]
        read_only_fields = fields


class HabitCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания привычки"""

    class Meta:
        model = Habit
        fields = [
            'place', 'time', 'action', 'is_pleasant', 'related_habit',
            'periodicity', 'reward', 'execution_time', 'is_public'
        ]

    def validate(self, data):
        """Валидация при создании"""
        habit = Habit(**data)
        habit.owner = self.context['request'].user

        validate_related_habit_or_reward(habit)
        validate_related_habit_is_pleasant(habit)
        validate_pleasant_habit_no_reward_or_related(habit)

        execution_time = data.get('execution_time')
        if execution_time:
            validate_execution_time(execution_time)

        periodicity = data.get('periodicity', 1)
        validate_periodicity(periodicity)

        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class HabitListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка привычек (с удобным форматом даты)"""

    time_display = serializers.SerializerMethodField()
    date_display = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'place', 'time_display', 'date_display', 'action', 'is_pleasant',
            'periodicity', 'execution_time', 'is_public', 'last_completed'
        ]

    def get_time_display(self, obj):
        return obj.time.strftime('%H:%M')

    def get_date_display(self, obj):
        return obj.time.strftime('%d.%m.%Y')