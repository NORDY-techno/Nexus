import aiohttp
import logging
from utils import calculate_rsi

# Отримуємо існуючий логер
logger = logging.getLogger("Nexus")

async def get_bitget_data(session, symbol, granularity="5m"):
    """
    Отримує дані з Bitget: поточну ціну та RSI.
    Використовує лише один запит до свічок для максимальної точності та швидкості.
    """
    try:
        # Granularity для Bitget API v2: 1min, 5min, 15min, 30min, 1h, 4h, 1day тощо.
        bitget_granularity = "5min" if granularity == "5m" else granularity
        
        # Запитуємо 200 свічок. Чим більше свічок, тим точніший RSI за методом Вайлдера.
        # 200 достатньо для ідеальної стабілізації RSI(14).
        candles_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={symbol}&granularity={bitget_granularity}&limit=200"
        
        async with session.get(candles_url, timeout=10) as response:
            if response.status != 200:
                logger.error(f"Помилка Candles API ({symbol}): статус {response.status}")
                return None, None
            
            candles_data = await response.json()
            if 'data' not in candles_data or not candles_data['data']:
                logger.warning(f"Candles API повернув порожні дані для {symbol}")
                return None, None
            
            candles = candles_data['data']
            
            # У Bitget API v2: candles[0] — це найсвіжіша свічка (поточна ціна).
            # Формат: [ts, open, high, low, close, vol, quoteVol]
            current_price = float(candles[0][4])
            
            # Формуємо список цін закриття для розрахунку RSI
            close_prices = [float(c[4]) for c in candles]
            
            # Свічки йдуть від нових до старих (0 — зараз, 199 — минуле).
            # Для розрахунку RSI нам потрібен хронологічний порядок (від минулого до теперішнього).
            close_prices.reverse()
            
            # Розраховуємо RSI
            rsi_val = calculate_rsi(close_prices, period=14)
            
            return current_price, rsi_val
        
    except Exception as e:
        logger.error(f"Критична помилка в get_bitget_data ({symbol}): {e}")
        return None, None
