import aiohttp
import asyncio
import logging
from tradingview_ta import TA_Handler, Interval, Exchange, get_multiple_analysis

# Отримуємо існуючий логер
logger = logging.getLogger("Nexus")

def get_tv_interval(granularity):
    """Мапінг таймфреймів для TradingView-TA"""
    tv_intervals = {
        "1m": Interval.INTERVAL_1_MINUTE,
        "5m": Interval.INTERVAL_5_MINUTES,
        "15m": Interval.INTERVAL_15_MINUTES,
        "1h": Interval.INTERVAL_1_HOUR,
        "4h": Interval.INTERVAL_4_HOURS,
        "1d": Interval.INTERVAL_1_DAY
    }
    return tv_intervals.get(granularity, Interval.INTERVAL_5_MINUTES)

async def get_all_rsi_data(symbols, granularity="5m"):
    """
    Отримує RSI для всіх символів одним запитом, щоб уникнути помилки 429.
    """
    try:
        # Формуємо список у форматі "BITGET:BTCUSDT"
        tv_symbols = [f"BITGET:{s}" for s in symbols]
        interval = get_tv_interval(granularity)
        
        # Виконуємо блокуючий запит у окремому потоці
        analysis = await asyncio.to_thread(
            get_multiple_analysis,
            screener="crypto",
            interval=interval,
            symbols=tv_symbols
        )
        
        # Витягуємо RSI для кожного символу
        rsi_results = {}
        for full_name, data in analysis.items():
            symbol = full_name.split(":")[1]
            if data and hasattr(data, 'indicators'):
                rsi_results[symbol] = data.indicators.get("RSI")
            else:
                rsi_results[symbol] = None
        
        return rsi_results
    except Exception as e:
        logger.error(f"Помилка пакетного отримання RSI: {e}")
        return {s: None for s in symbols}

async def get_bitget_price(session, symbol):
    """
    Отримує тільки поточну ціну через Bitget API.
    """
    try:
        ticker_url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
        async with session.get(ticker_url, timeout=10) as response:
            if response.status == 200:
                ticker_data = await response.json()
                if 'data' in ticker_data and ticker_data['data']:
                    return float(ticker_data['data'][0]['lastPr'])
        return None
    except Exception as e:
        logger.error(f"Помилка отримання ціни ({symbol}): {e}")
        return None
