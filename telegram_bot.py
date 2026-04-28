import aiohttp
import logging
import os
import time
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

# Отримуємо логер
logger = logging.getLogger("Nexus")

# Конфігурація Telegram (Беремо дані з .env)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_msg(session, message):
    """
    Асинхронно відправляє повідомлення у Telegram бот.
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
        async with session.post(url, json=payload, timeout=10) as response:
            if response.status == 200:
                # Додаємо логування успішної відправки (тільки у файл)
                try:
                    with open("nexus.log", "a", encoding="utf-8") as f:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"{timestamp} [DEBUG] Telegram message sent\n")
                except:
                    pass
                return True
            else:
                resp_text = await response.text()
                logger.error(f"Telegram Error: {response.status} - {resp_text}")
                return False
    except Exception as e:
        logger.error(f"Telegram Exception: {e}")
        return False
