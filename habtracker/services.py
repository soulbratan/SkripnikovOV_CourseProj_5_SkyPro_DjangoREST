from config import settings
import requests


def send_tg_message(chat_id, message):
    """Простая отправка сообщения в Telegram"""
    try:
        url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"

        params = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        print(f"✅ Сообщение отправлено в Telegram для chat_id: {chat_id}")
        return True

    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False
