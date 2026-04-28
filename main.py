import asyncio
import aiohttp
import sys
import time
from bitget_api import get_all_rsi_data, get_bitget_price
from logger import setup_logger
from utils import async_animate_wait
from telegram_bot import send_telegram_msg
import config

# Ініціалізація логера
logger = setup_logger()

# Коди кольорів (тільки для консолі)
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Словник для збереження останніх цін кожного активу
last_prices = {}

async def process_symbol(session, symbol, rsi):
    """
    Обробка одного активу: запит ціни, розрахунок зміни та відправка сповіщень.
    RSI вже отримано пакетним запитом.
    """
    global last_prices
    try:
        # Отримуємо тільки ціну
        price = await get_bitget_price(session, symbol)
        
        if price is not None:
            rsi_text = f" | RSI: {rsi:.1f}" if rsi is not None else ""
            
            if symbol in last_prices and last_prices[symbol] is not None:
                old_price = last_prices[symbol]
                change = ((price - old_price) / old_price) * 100
                
                if change >= config.COLOR_THRESHOLD: 
                    color, sign, emoji = GREEN, "+", "🟢"
                elif change <= -config.COLOR_THRESHOLD: 
                    color, sign, emoji = RED, "", "🔴"
                else: 
                    color, sign, emoji = "", "", "⚪"
                
                clean_msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_text}"
                
                # Вивід у консоль з кольором
                sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}{RESET}\n")
                
                # Запис у лог через централізований логер (він сам пише у файл)
                logger.info(f"LOG: {clean_msg}")
                
                # Відправка в Telegram
                if abs(change) >= config.TG_THRESHOLD:
                    rsi_val_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                    tg_msg = f"{emoji} <b>{symbol}</b>\nPrice: {price} USDT\nChange: {sign}{change:.2f}%\nRSI: {rsi_val_str}"
                    await send_telegram_msg(session, tg_msg)
            else:
                # Перший запуск
                msg = f"{symbol}: {price} USDT {rsi_text} (ініціалізація)"
                sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
                logger.info(msg)
            
            last_prices[symbol] = price
        else:
            logger.error(f"API Error for {symbol} | Skipping...")
    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}")

async def main():
    logger.info(f"Nexus Active | Monitoring {len(config.SYMBOLS)} assets (ASYNC) | {config.GRANULARITY}")
    
    async with aiohttp.ClientSession() as session:
        # Початкове повідомлення в Telegram
        await send_telegram_msg(session, f"🚀 <b>Nexus Active</b>\nMonitoring: {len(config.SYMBOLS)} assets\nTimeframe: {config.GRANULARITY}\nSync: Candle Close")
        
        while True:
            # 1. Отримуємо RSI пакетно
            rsi_data = await get_all_rsi_data(config.SYMBOLS, config.GRANULARITY)
            
            # 2. Обробляємо всі активи паралельно
            tasks = [process_symbol(session, symbol, rsi_data.get(symbol)) for symbol in config.SYMBOLS]
            await asyncio.gather(*tasks)
            
            # 3. Рахуємо час до наступної свічки
            now = time.time()
            interval = 300 # 5m = 300s
            if config.GRANULARITY == "1m": interval = 60
            elif config.GRANULARITY == "15m": interval = 900
            
            passed = now % interval
            wait_time = interval - passed + config.UPDATE_DELAY
            
            next_run = time.strftime('%H:%M:%S', time.localtime(now + wait_time))
            sys.stdout.write(f"[*] Наступний запит о {next_run} (після закриття свічки)\n")
            
            # 4. Пауза
            await async_animate_wait(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Nexus stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled Exception: {e}")
        sys.exit(1)
