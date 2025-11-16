from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_execution_time(value):
    """Валидатор времени выполнения - не более 120 секунд"""
    if value > 120:
        raise ValidationError('Время выполнения не должно превышать 120 секунд.')


def validate_periodicity(value):
    """Валидатор периодичности - от 1 до 7 дней"""
    if value < 1 or value > 7:
        raise ValidationError('Периодичность должна быть от 1 до 7 дней.')


def validate_related_habit_or_reward(habit):
    """
    Исключить одновременный выбор связанной привычки и указания вознаграждения.
    Можно заполнить только одно из двух полей.
    """
    if habit.related_habit and habit.reward:
        raise ValidationError({
            'related_habit': 'Нельзя одновременно указывать связанную привычку и вознаграждение.',
            'reward': 'Нельзя одновременно указывать связанную привычку и вознаграждение.'
        })


def validate_related_habit_is_pleasant(habit):
    """В связанные привычки могут попадать только привычки с признаком приятной привычки"""
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError({
            'related_habit': 'В связанные привычки могут попадать только приятные привычки.'
        })


def validate_pleasant_habit_no_reward_or_related(habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки"""
    if habit.is_pleasant:
        if habit.reward:
            raise ValidationError({
                'reward': 'У приятной привычки не может быть вознаграждения.'
            })
        if habit.related_habit:
            raise ValidationError({
                'related_habit': 'У приятной привычки не может быть связанной привычки.'
            })


def validate_habit_completion_frequency(habit):
    """
    Нельзя выполнять привычку реже, чем 1 раз в 7 дней.
    Нельзя не выполнять привычку более 7 дней.
    """
    if habit.last_completed:
        days_since_last = (timezone.now().date() - habit.last_completed.date()).days
        if days_since_last > 7:
            raise ValidationError(
                'Нельзя не выполнять привычку более 7 дней. '
                'За одну неделю необходимо выполнить привычку хотя бы один раз.'
            )


def validate_habit_creation(habit):
    """
    Комплексная валидация при создании/обновлении привычки
    """
    # Основные проверки
    validate_execution_time(habit.execution_time)
    validate_periodicity(habit.periodicity)
    validate_related_habit_or_reward(habit)
    validate_related_habit_is_pleasant(habit)
    validate_pleasant_habit_no_reward_or_related(habit)

    # Дополнительные бизнес-правила
    if habit.is_pleasant and habit.reward:
        raise ValidationError(
            'Приятная привычка не должна иметь вознаграждения.'
        )

    if habit.related_habit and habit.related_habit.owner != habit.owner:
        raise ValidationError(
            'Можно связывать только свои привычки.'
        )


def validate_habit_before_save(habit):
    """
    Валидация перед сохранением привычки
    """
    errors = {}

    # Проверка времени выполнения
    try:
        validate_execution_time(habit.execution_time)
    except ValidationError as e:
        errors['execution_time'] = e.message

    # Проверка периодичности
    try:
        validate_periodicity(habit.periodicity)
    except ValidationError as e:
        errors['periodicity'] = e.message

    # Проверка связанной привычки и вознаграждения
    try:
        validate_related_habit_or_reward(habit)
    except ValidationError as e:
        errors.update(e.message_dict)

    # Проверка типа связанной привычки
    try:
        validate_related_habit_is_pleasant(habit)
    except ValidationError as e:
        errors.update(e.message_dict)

    # Проверка приятной привычки
    try:
        validate_pleasant_habit_no_reward_or_related(habit)
    except ValidationError as e:
        errors.update(e.message_dict)

    if errors:
        raise ValidationError(errors)