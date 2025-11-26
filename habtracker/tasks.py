import pytz
from celery import shared_task
from django.utils import timezone
# from datetime import timedelta
from .models import Habit
from .services import send_tg_message


def create_reminder_message(habit):
    """Создание сообщения напоминания"""
    user_name = habit.user.first_name or "друг"

    message = f"""
👋 Привет, {user_name}!

Напоминание о твоей привычке:
Место📍 {habit.place}
Начало🕐 {habit.time.strftime('%H:%M')}
Действие💪 {habit.action}
Время⏱ {habit.duration} секунд

Удачи!
""".strip()

    return message


@shared_task
def send_habit_reminders():
    """Простая отправка напоминаний за 5 минут до привычки"""

    # Текущее время
    local_tz = pytz.timezone("Asia/Novosibirsk")
    now = timezone.now().astimezone(local_tz)
    current_time = now.time()
    today = now.date()

    print(f"⏰ Проверка привычек в {current_time.strftime('%H:%M')}")

    # Все привычки с Telegram пользователями
    habits = Habit.objects.filter(
        user__tg_id__isnull=False
    ).exclude(user__tg_id="").select_related("user")

    reminders_sent = 0

    for habit in habits:
        # 1. Проверяем время (за 5 минут до привычки)
        habit_time = habit.time
        time_diff_minutes = (habit_time.hour * 60 + habit_time.minute) - (current_time.hour * 60 + current_time.minute)

        if time_diff_minutes != 5:  # Ровно за 5 минут
            continue

        # 2. Проверяем периодичность
        days_passed = (today - habit.start_date).days
        if days_passed < 0:
            continue

        if days_passed % habit.frequency != 0:
            continue

        # 3. Отправляем уведомление
        message = create_reminder_message(habit)
        if send_tg_message(habit.user.tg_id, message):
            print(f"✅ Напоминание: {habit.action} для {habit.user.email}")
            reminders_sent += 1
        else:
            print(f"❌ Ошибка: {habit.action}")

    print(f"📤 Отправлено напоминаний: {reminders_sent}")
    return f"Отправлено: {reminders_sent}"


@shared_task
def check_habits_now():
    """Проверка какие привычки сейчас должны сработать"""

    local_tz = pytz.timezone("Asia/Novosibirsk")
    now = timezone.now().astimezone(local_tz)
    current_time = now.time()
    today = now.date()

    print(f"🔍 Проверка в {current_time.strftime('%H:%M:%S')}")

    habits = Habit.objects.all().select_related("user")

    for habit in habits:
        habit_time = habit.time
        time_diff = (habit_time.hour * 60 + habit_time.minute) - (current_time.hour * 60 + current_time.minute)
        days_passed = (today - habit.start_date).days

        status = "❌"
        if days_passed >= 0 and days_passed % habit.frequency == 0 and time_diff == 5:
            status = "✅ СЕЙЧАС"
        elif days_passed >= 0 and days_passed % habit.frequency == 0:
            status = "⚠️ Подходит по дате"

        print(f"{status} {habit.action} - {habit_time.strftime('%H:%M')} (через {time_diff} мин)")

    return "Проверка завершена"
