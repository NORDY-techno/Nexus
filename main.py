import time
import sys
from bitget_api import get_bitget_data
from logger import setup_logger
from utils import animate_wait

# Ініціалізація логера
logger = setup_logger()

# Коди кольорів (тільки для print, щоб не псувати лог-файл)
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

SYMBOL = "ETHUSDT"
GRANULARITY = "5m"
last_price = None

logger.info(f"Nexus Active | {SYMBOL} | M5")

while True:
    price, rsi = get_bitget_data(SYMBOL, GRANULARITY)
    
    if price is not None:
        rsi_text = f" | RSI: {rsi:.1f}" if rsi is not None else ""
        
        if last_price is not None:
            change = ((price - last_price) / last_price) * 100
            
            # Визначаємо колір
            if change >= 0.1: color, sign = GREEN, "+"
            elif change <= -0.1: color, sign = RED, ""
            else: color, sign = "", ""
            
            # Чисте повідомлення для лог-файлу
            clean_msg = f"{price} USDT | {sign}{change:.2f}%{rsi_text}"
            
            # Кольорове повідомлення тільки для консолі
            # Використовуємо sys.stdout.write, щоб мати повний контроль над виводом
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}{RESET}\n")
            
            # Записуємо в файл БЕЗ кольорів
            with open("nexus.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] {clean_msg}\n")
        
        last_price = price
        animate_wait(30)
    else:
        logger.error("API Error | Retry in 5s")
        time.sleep(5)
