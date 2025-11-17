from django.core.exceptions import ValidationError


def validate_habit(habit):
    """Валидация привычки"""

    # Исключить одновременный выбор связанной привычки и указания вознаграждения
    if habit.related_habit and habit.reward:
        raise ValidationError(
            "Нельзя одновременно указывать связанную привычку и вознаграждение"
        )

    # Время выполнения должно быть не больше 120 секунд
    if habit.duration > 120:
        raise ValidationError(
            "Время выполнения не может быть больше 120 секунд"
        )

    # В связанные привычки могут попадать только привычки с признаком приятной привычки
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError(
            "В связанные привычки могут попадать только приятные привычки"
        )

    # У приятной привычки не может быть вознаграждения или связанной привычки
    if habit.is_pleasant:
        if habit.reward:
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения"
            )
        if habit.related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки"
            )

    # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
    if habit.frequency == 'weekly':
        # Для еженедельной привычки проверяем, что она выполняется не реже раза в неделю
        pass  # Реализовано через выбор FREQUENCY_CHOICES в модели.