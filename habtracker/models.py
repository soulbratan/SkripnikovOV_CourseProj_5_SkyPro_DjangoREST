from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
    ]

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
    time = models.DateTimeField(
        verbose_name="Время",
        help_text="Дата и время, когда необходимо выполнять привычку"
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
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой"
    )
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default='daily',
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки"
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}: {self.action}"

    def clean(self):
        from .validators import validate_habit
        validate_habit(self)