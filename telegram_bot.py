import logging, os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("Nexus")
TOKEN, CHAT_ID = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_msg(session, text):
    if not TOKEN or not CHAT_ID or "YOUR_BOT_TOKEN" in TOKEN: return False
    try:
        async with session.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10) as resp:
            if resp.status == 200: return True
            logger.error(f"TG Error: {resp.status} - {await resp.text()}")
    except Exception as e: logger.error(f"TG Exception: {e}")
    return False
