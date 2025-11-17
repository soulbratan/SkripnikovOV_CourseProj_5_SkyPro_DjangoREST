import pytz
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Habit
from .services import send_tg_message


@shared_task
def send_habit_reminders():
    """Простая отправка напоминаний за 5 минут до привычки"""
    local_tz = pytz.timezone('Asia/Novosibirsk')
    now_utc = timezone.now()
    now = now_utc.astimezone(local_tz)
    reminder_time = now + timedelta(minutes=5)

    print(f"🔔 Проверяем привычки для напоминаний в {now}")

    # Находим привычки, которые начинаются через 5 минут
    habits = Habit.objects.filter(
        time__hour=reminder_time.hour,
        time__minute=reminder_time.minute,
        user__tg_id__isnull=False
    ).exclude(user__tg_id='')

    for habit in habits:
        message = f"""
👋 Привет, {habit.user.first_name or 'друг'}!

Напоминание о твоей привычке:
📍 Место: {habit.place}
🕐 Время: {habit.time.strftime('%H:%M')}
💪 Действие: {habit.action}
⏱ Время на выполнение: {habit.duration} секунд

У тебя всё получится! 💫
        """.strip()

        send_tg_message(habit.user.tg_id, message)
        print(f"✅ Напоминание отправлено для: {habit.action}")

    return f"Отправлено напоминаний: {habits.count()}"