from django.db import models
from django.conf import settings
from django.utils import timezone
from .validators import validate_habit_before_save


class Habit(models.Model):
    """Модель привычки"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="habits"
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку"
    )
    time = models.DateTimeField(
        verbose_name="Дата и время",
        help_text="Дата и время, когда необходимо выполнять привычку"
    )
    action = models.CharField(
        max_length=500,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Привычка, которую можно привязать к выполнению полезной привычки"
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой"
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
        help_text="Периодичность выполнения привычки для напоминания в днях"
    )
    reward = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения"
    )
    execution_time = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Привычки можно публиковать в общий доступ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    last_completed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последнее выполнение"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner.email}: {self.action} в {self.time.strftime('%d.%m.%Y %H:%M')}"

    def clean(self):
        """Валидация данных при сохранении"""
        validate_habit_before_save(self)

    def save(self, *args, **kwargs):
        """Переопределение save с валидацией"""
        self.full_clean()
        super().save(*args, **kwargs)

    def mark_completed(self):
        """Отметить привычку как выполненную"""
        self.last_completed = timezone.now()
        self.save()

    @property
    def time_only(self):
        """Возвращает только время (для обратной совместимости)"""
        return self.time.time()

    @property
    def date_only(self):
        """Возвращает только дату"""
        return self.time.date()