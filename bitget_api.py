import aiohttp
import asyncio
import logging
from tradingview_ta import Interval, get_multiple_analysis

# Отримуємо існуючий логер
logger = logging.getLogger("Nexus")

BASE_URL = "https://api.bitget.com/api/v2/spot/market"

def get_tv_interval(granularity):
    """Мапінг таймфреймів для TradingView-TA"""
    intervals = {
        "1m": Interval.INTERVAL_1_MINUTE,
        "5m": Interval.INTERVAL_5_MINUTES,
        "15m": Interval.INTERVAL_15_MINUTES,
        "1h": Interval.INTERVAL_1_HOUR,
        "4h": Interval.INTERVAL_4_HOURS,
        "1d": Interval.INTERVAL_1_DAY
    }
    return intervals.get(granularity, Interval.INTERVAL_5_MINUTES)

async def get_all_rsi_data(symbols, granularity="5m"):
    """
    Отримує RSI для всіх символів одним запитом.
    """
    try:
        tv_symbols = [f"BITGET:{s}" for s in symbols]
        interval = get_tv_interval(granularity)
        
        analysis = await asyncio.to_thread(
            get_multiple_analysis,
            screener="crypto",
            interval=interval,
            symbols=tv_symbols
        )
        
        results = {}
        for full_name, data in analysis.items():
            symbol = full_name.split(":")[1]
            results[symbol] = data.indicators.get("RSI") if data and hasattr(data, 'indicators') else None
        return results
    except Exception as e:
        logger.error(f"Помилка пакетного отримання RSI: {e}")
        return {s: None for s in symbols}

async def get_bitget_price(session, symbol, retries=3):
    """
    Отримує поточну ціну через Bitget API з повторними спробами.
    """
    url = f"{BASE_URL}/tickers?symbol={symbol}"
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and data['data']:
                        return float(data['data'][0]['lastPr'])
                elif response.status == 429:
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Помилка Ticker API ({symbol}): статус {response.status}")
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Критична помилка ціни ({symbol}) після {retries} спроб: {e}")
            await asyncio.sleep(0.5)
    return None
