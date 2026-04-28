import aiohttp
import logging
from utils import calculate_rsi

# Отримуємо існуючий логер
logger = logging.getLogger("Nexus")

async def get_bitget_data(session, symbol, granularity="5m"):
    """
    Асинхронно отримує поточну ціну та розраховує RSI через API Bitget.
    Повертає кортеж (price, rsi_val).
    """
    try:
        # 1. Отримуємо поточну ціну
        ticker_url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
        async with session.get(ticker_url, timeout=10) as response:
            if response.status != 200:
                logger.error(f"Помилка Ticker API ({symbol}): статус {response.status}")
                return None, None
            
            ticker_data = await response.json()
            if 'data' not in ticker_data or not ticker_data['data']:
                logger.error(f"Ticker API ({symbol}) повернув порожні дані")
                return None, None
            
            current_price = float(ticker_data['data'][0]['lastPr'])

        # 2. Отримуємо дані для RSI
        bitget_granularity = "5min" if granularity == "5m" else granularity
        candles_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={symbol}&granularity={bitget_granularity}&limit=100"
        
        async with session.get(candles_url, timeout=10) as response:
            rsi_val = None
            if response.status == 200:
                candles_data = await response.json()
                if 'data' in candles_data and candles_data['data']:
                    candles = candles_data['data']
                    close_prices = [float(c[4]) for c in candles]
                    close_prices.reverse()
                    close_prices.append(current_price)
                    rsi_val = calculate_rsi(close_prices, period=14)
                else:
                    logger.warning(f"Candles API повернув порожні дані для {symbol}")
            else:
                logger.error(f"Помилка Candles API ({symbol}): статус {response.status}")
            
        return current_price, rsi_val
        
    except Exception as e:
        logger.error(f"Критична помилка в get_bitget_data ({symbol}): {e}")
        return None, None
