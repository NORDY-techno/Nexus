import asyncio, aiohttp, sys, time, ccxt.async_support as ccxt
from bitget_api import get_all_bitget_prices
from indicators import get_all_rsi_data
from volume_analyzer import get_bitget_volume_data
from oi_analyzer import check_oi_anomaly
from logger import setup_logger
from telegram_bot import send_telegram_msg
from utils import get_rsi_emoji, get_change_info, get_volume_emoji
from ws_client import BitgetWS
import config

logger, last_prices = setup_logger(), {}
# Глобальні змінні для збереження актуальних даних
current_rsi, current_volumes, current_oi = {}, {}, {}

async def process_ticker(symbol, price, session, spot_ex, swap_ex):
    """Обробка ціни в реальному часі через WebSocket"""
    global last_prices
    try:
        rsi = current_rsi.get(symbol)
        vol_change = current_volumes.get(symbol)
        oi_data = current_oi.get(symbol)
        
        rsi_txt = f" | {get_rsi_emoji(rsi)} RSI: {rsi:.1f}" if rsi is not None else ""
        vol_txt = f" | {get_volume_emoji(vol_change)} Vol: {vol_change:+.1f}%" if vol_change is not None else ""
        oi_log = f" | 🔍 OI: {oi_data['oi_change']:+.2f}%" if oi_data else ""

        if symbol in last_prices:
            old = last_prices[symbol]
            change = (price - old) / old * 100
            
            # Вивід у консоль тільки при значній зміні ціни (> порогу), щоб не спамити кожну мс
            if abs(change) >= config.COLOR_THRESHOLD:
                color, sign, p_emoji = get_change_info(change, config.COLOR_THRESHOLD)
                msg = f"{symbol}: {price} USDT | {sign}{change:.2f}%{rsi_txt}{vol_txt}{oi_log}"
                sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {color}{msg}\033[0m\n")
                
                if abs(change) >= config.TG_THRESHOLD or (vol_change is not None and vol_change >= 100.0) or oi_data:
                    hdr = f"{p_emoji} <b>{symbol}</b>"
                    if oi_data: hdr = f"📊 <b>{symbol} (OI Alert)</b>"
                    elif vol_change and vol_change >= 100.0 and abs(change) < config.TG_THRESHOLD: 
                        hdr = f"🔥 <b>{symbol} (Vol Spike)</b>"
                    
                    v_val = f"{vol_change:+.1f}%" if vol_change is not None else "N/A"
                    r_val = f"{rsi:.1f}" if rsi is not None else "N/A"
                    oi_txt = f"\n🔍 OI: <b>{oi_data['status']}</b> (OI: {oi_data['oi_change']:+.2f}%)" if oi_data else ""
                    
                    tg_msg = f"{hdr}\n💰 Price: <code>{price}</code> USDT\n📈 Change: <b>{sign}{change:.2f}%</b>\n{get_rsi_emoji(rsi)} RSI: <code>{r_val}</code>\n{get_volume_emoji(vol_change)} Volume: <b>{v_val}</b>{oi_txt}"
                    await send_telegram_msg(session, tg_msg)
                    last_prices[symbol] = price # Оновлюємо ціну тільки після відправки пуша або великої зміни
        else:
            last_prices[symbol] = price
            logger.info(f"Initialized {symbol}: {price} USDT")
            
    except Exception as e:
        logger.error(f"Error processing ticker {symbol}: {e}")

async def update_heavy_indicators(session, spot_ex, swap_ex):
    """Фонове оновлення важких індикаторів (RSI, Vol, OI) кожні N секунд"""
    global current_rsi, current_volumes, current_oi, last_prices
    symbols = list(set(config.SYMBOLS))
    
    while True:
        try:
            # 1. Пакетне оновлення RSI
            rsi_data = await get_all_rsi_data(symbols, config.GRANULARITY)
            current_rsi.update(rsi_data)
            
            # 2. Пакетне оновлення Цін для розрахунку Vol та OI (через REST)
            price_data = await get_all_bitget_prices(session, symbols)
            
            # 3. Оновлення Volume та OI для кожного символу
            for s in symbols:
                p = price_data.get(s)
                if p:
                    vol_task = get_bitget_volume_data(spot_ex, s, config.GRANULARITY)
                    oi_task = check_oi_anomaly(swap_ex, s, p)
                    vol_change, oi_data = await asyncio.gather(vol_task, oi_task)
                    
                    current_volumes[s] = vol_change
                    current_oi[s] = oi_data
            
            logger.info(f"Heavy indicators updated for {len(symbols)} assets")
            
            # Чекаємо до наступного закриття свічки або заданий інтервал
            interval = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}.get(config.GRANULARITY, 300)
            await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Error updating heavy indicators: {e}")
            await asyncio.sleep(10)

async def main():
    logger.info(f"Nexus v2 (WebSocket) Active | {len(config.SYMBOLS)} assets")
    
    async with aiohttp.ClientSession() as session:
        spot_ex = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
        swap_ex = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})
        
        try:
            await send_telegram_msg(session, f"🚀 <b>Nexus v2 Active</b>\nMode: WebSocket Real-time\nAssets: {len(config.SYMBOLS)}")
            
            # Callback для обробки даних з WebSocket
            async def ws_callback(symbol, price):
                await process_ticker(symbol, price, session, spot_ex, swap_ex)

            # Запускаємо WebSocket клієнт
            ws_client = BitgetWS(config.SYMBOLS, ws_callback)
            
            # Запускаємо фонове оновлення RSI/Vol/OI та WebSocket клієнт паралельно
            await asyncio.gather(
                ws_client.connect(),
                update_heavy_indicators(session, spot_ex, swap_ex)
            )
            
        finally:
            await asyncio.gather(spot_ex.close(), swap_ex.close())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Nexus stopped")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
