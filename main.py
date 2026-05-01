import asyncio
import aiohttp
import sys
import time
from bitget_api import get_all_rsi_data, get_bitget_price
from logger import setup_logger
from telegram_bot import send_telegram_msg
from utils import get_rsi_emoji, get_change_info
import config

# Ініціалізація логера
logger = setup_logger()

# Словник для збереження останніх цін кожного активу
last_prices = {}

async def process_symbol(session, symbol, rsi):
    """
    Обробка одного активу: запит ціни, розрахунок зміни та відправка сповіщень.
    """
    global last_prices
    try:
        price = await get_bitget_price(session, symbol)
        if price is None:
            return

        rsi_emoji = get_rsi_emoji(rsi)
        rsi_text = f" | {rsi_emoji} RSI: {rsi:.1f}" if rsi is not None else ""
        
        if symbol in last_prices and last_prices[symbol] is not None:
            old_price = last_prices[symbol]
            change = ((price - old_price) / old_price) * 100
            
            color, sign, price_emoji = get_change_info(change, config.COLOR_THRESHOLD)
            clean_msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_text}"
            
            # Вивід у консоль та лог
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{clean_msg}\033[0m\n")
            logger.info(f"DATA: {clean_msg}")
            
            # Відправка в Telegram
            if abs(change) >= config.TG_THRESHOLD:
                rsi_val_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                tg_msg = f"{price_emoji} <b>{symbol}</b>\nPrice: {price} USDT\nChange: {sign}{change:.2f}%\n{rsi_emoji} RSI: {rsi_val_str}"
                await send_telegram_msg(session, tg_msg)
        else:
            # Перший запуск
            msg = f"{symbol}: {price} USDT {rsi_text} (ініціалізація)"
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            logger.info(msg)
        
        last_prices[symbol] = price
    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}")

async def run_cycle(session):
    """
    Один цикл опитування всіх активів.
    """
    rsi_data = await get_all_rsi_data(config.SYMBOLS, config.GRANULARITY)
    tasks = [process_symbol(session, symbol, rsi_data.get(symbol)) for symbol in config.SYMBOLS]
    await asyncio.gather(*tasks)

async def main():
    logger.info(f"Nexus Active | {len(config.SYMBOLS)} assets | {config.GRANULARITY}")
    
    async with aiohttp.ClientSession() as session:
        # Початкове сповіщення
        await send_telegram_msg(session, f"🚀 <b>Nexus Active</b>\nMonitoring: {len(config.SYMBOLS)} assets\nTimeframe: {config.GRANULARITY}")
        
        # Словник інтервалів у секундах
        intervals = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}
        interval = intervals.get(config.GRANULARITY, 300)

        while True:
            try:
                start_time = time.time()
                await run_cycle(session)
                
                # Рахуємо час до наступної свічки
                passed = time.time() % interval
                wait_time = interval - passed + config.UPDATE_DELAY
                
                next_run = time.strftime('%H:%M:%S', time.localtime(time.time() + wait_time))
                sys.stdout.write(f"[*] Наступний запит о {next_run}\n")
                
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Cycle Error: {e}. Reconnecting in 10s...")
                await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Nexus stopped by user")
    except Exception as e:
        logger.critical(f"Fatal Error: {e}")
        sys.exit(1)
