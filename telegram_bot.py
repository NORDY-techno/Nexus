import requests
import logging

# Отримуємо логер
logger = logging.getLogger("Nexus")

# Конфігурація Telegram (Сюди потрібно вставити твої дані)
TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_msg(message):
    """
    Відправляє повідомлення у Telegram бот.
    """
    if TOKEN == "YOUR_BOT_TOKEN" or CHAT_ID == "YOUR_CHAT_ID":
        # Якщо дані не заповнені, просто нічого не робимо (щоб не було помилок)
        return False
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Telegram Error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Telegram Exception: {e}")
        return False
