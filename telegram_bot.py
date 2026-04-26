import requests
import logging
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

# Отримуємо логер
logger = logging.getLogger("Nexus")

# Конфігурація Telegram (Беремо дані з .env)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_msg(message):
    """
    Відправляє повідомлення у Telegram бот.
    """
    if not TOKEN or not CHAT_ID or TOKEN == "YOUR_BOT_TOKEN":
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
            # Додаємо логування успішної відправки (тільки у файл, щоб не спамити в консоль)
            with open("nexus.log", "a", encoding="utf-8") as f:
                f.write(f"{logging.Formatter().formatTime(logging.LogRecord('Nexus', logging.INFO, '', 0, '', None, None))} [DEBUG] Telegram message sent\n")
            return True
        else:
            logger.error(f"Telegram Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram Exception: {e}")
        return False
