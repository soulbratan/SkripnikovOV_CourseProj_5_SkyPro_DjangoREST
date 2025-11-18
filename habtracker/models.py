from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.utils import timezone


class Habit(models.Model):
    """Модель пользователя приложения"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits"
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку"
    )
    time = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Время, когда необходимо выполнять привычку"
    )
    action = models.CharField(
        max_length=500,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой"
    )
    frequency = models.PositiveIntegerField(  # ⚡ ИЗМЕНЕНО: число вместо строки
        default=1,
        verbose_name="Периодичность (в днях)",
        help_text="Периодичность выполнения привычки в днях (1-7)",
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности"
    )
    start_date = models.DateField(  # ⚡ ДОБАВЛЕНО: дата начала привычки
        default=timezone.now,
        verbose_name="Дата начала привычки"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.action}"

    def clean(self):
        from .validators import validate_habit
        validate_habit(self)


class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        verbose_name="Привычка",
        related_name="completions"
    )
    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время выполнения"
    )
    is_successful = models.BooleanField(
        default=True,
        verbose_name="Успешно выполнено"
    )

    class Meta:
        verbose_name = "Выполнение привычки"
        verbose_name_plural = "Выполнения привычек"
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.habit.action} - {self.completed_at.strftime('%Y-%m-%d %H:%M')}"