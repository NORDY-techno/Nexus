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

# Налаштування списку активів (10 штук)
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"
]
GRANULARITY = "5m"
COLOR_THRESHOLD = 0.1    # Поріг для зміни кольору в терміналі
TG_THRESHOLD = 0.01      # Поріг для відправки в Telegram

# Словник для збереження останніх цін кожного активу
last_prices = {}

logger.info(f"Nexus Active | Monitoring {len(SYMBOLS)} assets | M5")
send_telegram_msg(f"🚀 <b>Nexus Multi-Active</b>\nAssets: {', '.join(SYMBOLS)}\nTimeframe: {GRANULARITY}")

while True:
    for symbol in SYMBOLS:
        price, rsi = get_bitget_data(symbol, GRANULARITY)
        
        if price is not None:
            rsi_text = f" | RSI: {rsi:.1f}" if rsi is not None else ""
            
            # Перевіряємо, чи є попередня ціна для цього активу
            if symbol in last_prices and last_prices[symbol] is not None:
                old_price = last_prices[symbol]
                change = ((price - old_price) / old_price) * 100
                
                # Визначаємо колір та емодзі
                if change >= COLOR_THRESHOLD: 
                    color, sign, emoji = GREEN, "+", "🟢"
                elif change <= -COLOR_THRESHOLD: 
                    color, sign, emoji = RED, "", "🔴"
                else: 
                    color, sign, emoji = "", "", "⚪"
                
                # Повідомлення
                clean_msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_text}"
                
                # 1. Вивід у консоль
                sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}{RESET}\n")
                
                # 2. Запис у лог-файл
                with open("nexus.log", "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] {clean_msg}\n")
                
                # 3. Відправка в Telegram (тільки якщо зміна суттєва)
                if abs(change) >= TG_THRESHOLD:
                    rsi_val_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                    tg_msg = f"{emoji} <b>{symbol}</b>\nPrice: {price} USDT\nChange: {sign}{change:.2f}%\nRSI: {rsi_val_str}"
                    send_telegram_msg(tg_msg)
            
            # Оновлюємо останню ціну для активу
            last_prices[symbol] = price
        else:
            logger.error(f"API Error for {symbol} | Skipping...")
            
    # Пауза після того, як перевірили всі активи
    animate_wait(30)
