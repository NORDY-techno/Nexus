import asyncio, aiohttp, sys, time, ccxt.async_support as ccxt
from bitget_api import get_all_bitget_prices
from indicators import get_all_rsi_data
from volume_analyzer import get_bitget_volume_data
from oi_analyzer import check_oi_anomaly
from logger import setup_logger
from telegram_bot import send_telegram_msg
from utils import get_rsi_emoji, get_change_info, get_volume_emoji
import config

logger, last_prices = setup_logger(), {}

async def process_symbol(session, spot_ex, swap_ex, symbol, rsi, price):
    global last_prices
    try:
        # Об'єм беремо зі споту, OI — з ф'ючерсів (swap)
        vol_task = get_bitget_volume_data(spot_ex, symbol, config.GRANULARITY)
        oi_task = check_oi_anomaly(swap_ex, symbol, price)
        
        vol_change, oi_data = await asyncio.gather(vol_task, oi_task)
        
        if price is None: return

        rsi_txt = f" | {get_rsi_emoji(rsi)} RSI: {rsi:.1f}" if rsi is not None else ""
        vol_txt = f" | {get_volume_emoji(vol_change)} Vol: {vol_change:+.1f}%" if vol_change is not None else ""
        
        # Визначаємо чи є дані OI для логування та ТГ
        oi_val_for_log = ""
        if oi_data:
            oi_val_for_log = f" | 🔍 OI: {oi_data['oi_change']:+.2f}%"

        if symbol in last_prices:
            old = last_prices[symbol]
            change = (price - old) / old * 100
            color, sign, p_emoji = get_change_info(change, config.COLOR_THRESHOLD)
            
            # Повний лог для консолі/файлу
            msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_txt}{vol_txt}{oi_val_for_log}"
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{msg}\033[0m\n")
            logger.info(f"DATA: {msg}")
            
            # Умова відправки в ТГ: ціна, об'єм АБО будь-яка зміна OI (якщо ми встановили поріг 0.1%)
            price_moved = abs(change) >= config.TG_THRESHOLD
            vol_spiked = vol_change is not None and vol_change >= 100.0
            
            if price_moved or vol_spiked or oi_data:
                hdr = f"{p_emoji} <b>{symbol}</b>"
                # Пріоритет заголовка для OI аномалії
                if oi_data: 
                    hdr = f"📊 <b>{symbol} (OI Alert)</b>"
                elif vol_spiked and not price_moved: 
                    hdr = f"🔥 <b>{symbol} (Vol Spike)</b>"
                
                v_val = f"{vol_change:+.1f}%" if vol_change is not None else "N/A"
                r_val = f"{rsi:.1f}" if rsi is not None else "N/A"
                
                # Завжди додаємо рядок OI, якщо є дані від oi_analyzer
                oi_txt = ""
                if oi_data:
                    oi_txt = f"\n🔍 OI: <b>{oi_data['status']}</b> (OI: {oi_data['oi_change']:+.2f}%)"
                
                tg_msg = f"{hdr}\n💰 Price: <code>{price}</code> USDT\n📈 Change: <b>{sign}{change:.2f}%</b>\n{get_rsi_emoji(rsi)} RSI: <code>{r_val}</code>\n{get_volume_emoji(vol_change)} Volume: <b>{v_val}</b>{oi_txt}"
                await send_telegram_msg(session, tg_msg)
        else:
            msg = f"{symbol}: {price} USDT{rsi_txt}{vol_txt} (initialization)"
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            logger.info(msg)
        last_prices[symbol] = price
    except Exception as e: logger.error(f"Error {symbol}: {e}")

async def run_cycle(session, spot_ex, swap_ex):
    symbols = list(set(config.SYMBOLS))
    
    # Отримуємо RSI та Ціни пакетно (це сильно економить ліміти API)
    rsi_task = get_all_rsi_data(symbols, config.GRANULARITY)
    price_task = get_all_bitget_prices(session, symbols)
    
    rsi_data, price_data = await asyncio.gather(rsi_task, price_task)
    
    tasks = [
        process_symbol(session, spot_ex, swap_ex, symbol, rsi_data.get(symbol), price_data.get(symbol)) 
        for symbol in symbols
    ]
    await asyncio.gather(*tasks)

async def main():
    logger.info(f"Nexus Active | {len(config.SYMBOLS)} assets")
    async with aiohttp.ClientSession() as session:
        # Ініціалізуємо окремі інстанси для Spot та Swap (Futures)
        spot_ex = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
        swap_ex = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})
        
        try:
            await send_telegram_msg(session, f"🚀 <b>Nexus Active</b>\nMonitoring: {len(config.SYMBOLS)} assets")
            interval = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}.get(config.GRANULARITY, 300)
            while True:
                await run_cycle(session, spot_ex, swap_ex)
                wait = interval - (time.time() % interval) + config.UPDATE_DELAY
                sys.stdout.write(f"[*] Next run: {time.strftime('%H:%M:%S', time.localtime(time.time() + wait))}\n")
                await asyncio.sleep(wait)
        finally: 
            await asyncio.gather(spot_ex.close(), swap_ex.close())

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: logger.info("Stopped")
    except Exception as e: logger.critical(f"Fatal: {e}"); sys.exit(1)
