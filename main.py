import time
import sys
from bitget_api import get_bitget_data
from logger import setup_logger
from utils import animate_wait
from telegram_bot import send_telegram_msg

# Ініціалізація логера
logger = setup_logger()

# Коди кольорів (тільки для консолі)
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Налаштування
SYMBOL = "KITEUSDT"
GRANULARITY = "5m"
COLOR_THRESHOLD = 0.1    # Поріг для зміни кольору в терміналі
TG_THRESHOLD = 0.01      # Поріг для відправки в Telegram (знизив, щоб повідомлення приходили частіше)

last_price = None

logger.info(f"Nexus Active | {SYMBOL} | M5")
send_telegram_msg(f"🚀 <b>Nexus Active</b>\nSymbol: {SYMBOL}\nTimeframe: {GRANULARITY}")

while True:
    price, rsi = get_bitget_data(SYMBOL, GRANULARITY)
    
    if price is not None:
        rsi_text = f" | RSI: {rsi:.1f}" if rsi is not None else ""
        
        if last_price is not None:
            change = ((price - last_price) / last_price) * 100
            
            # Визначаємо колір для термінала
            if change >= COLOR_THRESHOLD: 
                color, sign, emoji = GREEN, "+", "🟢"
            elif change <= -COLOR_THRESHOLD: 
                color, sign, emoji = RED, "", "🔴"
            else: 
                color, sign, emoji = "", "", "⚪"
            
            # Повідомлення для логів та консолі
            clean_msg = f"{price} USDT | {sign}{change:.2f}%{rsi_text}"
            
            # 1. Вивід у консоль
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}{RESET}\n")
            
            # 2. Запис у лог-файл
            with open("nexus.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] {clean_msg}\n")
            
            # 3. Відправка в Telegram (тільки якщо зміна суттєва для TG)
            if abs(change) >= TG_THRESHOLD:
                rsi_val_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                tg_msg = f"{emoji} <b>{SYMBOL}</b>\nPrice: {price} USDT\nChange: {sign}{change:.2f}%\nRSI: {rsi_val_str}"
                send_telegram_msg(tg_msg)
        
        last_price = price
        animate_wait(30)
    else:
        logger.error("API Error | Retry in 5s")
        time.sleep(5)
