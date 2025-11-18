# validators.py - полная версия
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

def validate_habit(habit):
    """Полная валидация привычки согласно заданию"""
    errors = {}

    # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения
    if habit.related_habit and habit.reward:
        errors['__all__'] = "Нельзя одновременно указывать связанную привычку и вознаграждение"

    # 2. Время выполнения должно быть не больше 120 секунд
    if habit.duration > 120:
        errors['duration'] = "Время выполнения не может быть больше 120 секунд"

    # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки
    if habit.related_habit and not habit.related_habit.is_pleasant:
        errors['related_habit'] = "В связанные привычки могут попадать только приятные привычки"

    # 4. У приятной привычки не может быть вознаграждения или связанной привычки
    if habit.is_pleasant:
        if habit.reward:
            errors['reward'] = "У приятной привычки не может быть вознаграждения"
        if habit.related_habit:
            errors['related_habit'] = "У приятной привычки не может быть связанной привычки"

    # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней
    if habit.frequency > 7:
        errors['frequency'] = "Нельзя выполнять привычку реже, чем 1 раз в 7 дней"

    # 6. Проверка циклических зависимостей
    if habit.related_habit and habit.related_habit.related_habit == habit:
        errors['related_habit'] = "Обнаружена циклическая зависимость привычек"

    # 7. Проверка, что пользователь не ссылается на чужую привычку
    if habit.related_habit and habit.related_habit.user != habit.user:
        errors['related_habit'] = "Нельзя использовать чужую привычку как связанную"

    if errors:
        raise ValidationError(errors)