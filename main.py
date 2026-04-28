import asyncio
import aiohttp
import sys
import time
from bitget_api import get_bitget_data
from logger import setup_logger
from utils import async_animate_wait
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

async def process_symbol(session, symbol):
    """
    Обробка одного активу: запит даних, розрахунок зміни та відправка сповіщень.
    """
    global last_prices
    price, rsi = await get_bitget_data(session, symbol, GRANULARITY)
    
    if price is not None:
        rsi_text = f" | RSI: {rsi:.1f}" if rsi is not None else ""
        
        if symbol in last_prices and last_prices[symbol] is not None:
            old_price = last_prices[symbol]
            change = ((price - old_price) / old_price) * 100
            
            if change >= COLOR_THRESHOLD: 
                color, sign, emoji = GREEN, "+", "🟢"
            elif change <= -COLOR_THRESHOLD: 
                color, sign, emoji = RED, "", "🔴"
            else: 
                color, sign, emoji = "", "", "⚪"
            
            clean_msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_text}"
            
            # Вивід у консоль
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}{RESET}\n")
            
            # Запис у лог-файл
            with open("nexus.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] {clean_msg}\n")
            
            # Відправка в Telegram
            if abs(change) >= TG_THRESHOLD:
                rsi_val_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                tg_msg = f"{emoji} <b>{symbol}</b>\nPrice: {price} USDT\nChange: {sign}{change:.2f}%\nRSI: {rsi_val_str}"
                await send_telegram_msg(session, tg_msg)
        
        last_prices[symbol] = price
    else:
        logger.error(f"API Error for {symbol} | Skipping...")

async def main():
    logger.info(f"Nexus Active | Monitoring {len(SYMBOLS)} assets (ASYNC) | M5")
    
    async with aiohttp.ClientSession() as session:
        # Початкове повідомлення в Telegram
        await send_telegram_msg(session, f"🚀 <b>Nexus Async Active</b>\nAssets: {', '.join(SYMBOLS)}\nTimeframe: {GRANULARITY}")
        
        while True:
            # Створюємо список завдань для всіх активів
            tasks = [process_symbol(session, symbol) for symbol in SYMBOLS]
            
            # Запускаємо всі завдання одночасно
            await asyncio.gather(*tasks)
            
            # Анімована пауза
            await async_animate_wait(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Nexus stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled Exception: {e}")
        sys.exit(1)
