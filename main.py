import asyncio, aiohttp, sys, time, ccxt.async_support as ccxt
from bitget_api import get_all_bitget_prices
from indicators import get_all_rsi_data
from volume_analyzer import get_bitget_volume_data
from logger import setup_logger
from telegram_bot import send_telegram_msg
from utils import get_rsi_emoji, get_change_info, get_volume_emoji
import config

logger, last_prices = setup_logger(), {}

async def process_symbol(session, exchange, symbol, rsi, price):
    global last_prices
    try:
        vol_change = await get_bitget_volume_data(exchange, symbol, config.GRANULARITY)
        if price is None: return

        rsi_txt = f" | {get_rsi_emoji(rsi)} RSI: {rsi:.1f}" if rsi is not None else ""
        vol_txt = f" | {get_volume_emoji(vol_change)} Vol: {vol_change:+.1f}%" if vol_change is not None else ""
        
        if symbol in last_prices:
            old = last_prices[symbol]
            change = (price - old) / old * 100
            color, sign, p_emoji = get_change_info(change, config.COLOR_THRESHOLD)
            msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_txt}{vol_txt}"
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{msg}\033[0m\n")
            logger.info(f"DATA: {msg}")
            
            # Умова: значна зміна ціни АБО сплеск об'єму (лише ріст >= 100%)
            price_moved = abs(change) >= config.TG_THRESHOLD
            vol_spiked = vol_change is not None and vol_change >= 100.0
            
            if price_moved or vol_spiked:
                hdr = f"{p_emoji} <b>{symbol}</b>"
                if vol_spiked and not price_moved:
                    hdr = f"🔥 <b>{symbol} (Vol Spike)</b>"
                
                v_val = f"{vol_change:+.1f}%" if vol_change is not None else "N/A"
                r_val = f"{rsi:.1f}" if rsi is not None else "N/A"
                tg_msg = f"{hdr}\n💰 Price: <code>{price}</code> USDT\n📈 Change: <b>{sign}{change:.2f}%</b>\n{get_rsi_emoji(rsi)} RSI: <code>{r_val}</code>\n{get_volume_emoji(vol_change)} Volume: <b>{v_val}</b>"
                await send_telegram_msg(session, tg_msg)
        else:
            msg = f"{symbol}: {price} USDT{rsi_txt}{vol_txt} (initialization)"
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            logger.info(msg)
        last_prices[symbol] = price
    except Exception as e: logger.error(f"Error {symbol}: {e}")

async def run_cycle(session, exchange):
    symbols = list(set(config.SYMBOLS))
    rsi_data, price_data = await asyncio.gather(get_all_rsi_data(symbols, config.GRANULARITY), get_all_bitget_prices(session, symbols))
    await asyncio.gather(*[process_symbol(session, exchange, s, rsi_data.get(s), price_data.get(s)) for s in symbols])

async def main():
    logger.info(f"Nexus Active | {len(config.SYMBOLS)} assets")
    async with aiohttp.ClientSession() as session:
        ex = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
        try:
            await send_telegram_msg(session, f"🚀 <b>Nexus Active</b>\nMonitoring: {len(config.SYMBOLS)} assets")
            interval = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}.get(config.GRANULARITY, 300)
            while True:
                await run_cycle(session, ex)
                wait = interval - (time.time() % interval) + config.UPDATE_DELAY
                sys.stdout.write(f"[*] Next run: {time.strftime('%H:%M:%S', time.localtime(time.time() + wait))}\n")
                await asyncio.sleep(wait)
        finally: await ex.close()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: logger.info("Stopped")
    except Exception as e: logger.critical(f"Fatal: {e}"); sys.exit(1)
