import requests
import logging
from utils import calculate_rsi

# Отримуємо існуючий логер
logger = logging.getLogger("Nexus")

def get_bitget_data(symbol, granularity="5m"):
    """
    Отримує поточну ціну та розраховує RSI через API Bitget.
    Повертає кортеж (price, rsi_val).
    """
    try:
        # 1. Отримуємо поточну ціну
        # Важливо: Bitget API v2 вимагає символ у форматі ETHUSDT (Spot)
        ticker_url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
        ticker_resp = requests.get(ticker_url, timeout=10)
        
        if ticker_resp.status_code != 200:
            logger.error(f"Помилка Ticker API: статус {ticker_resp.status_code}")
            return None, None
            
        ticker_data = ticker_resp.json()
        if 'data' not in ticker_data or not ticker_data['data']:
            logger.error("Ticker API повернув порожні дані")
            return None, None
            
        current_price = float(ticker_data['data'][0]['lastPr'])
        
        # 2. Отримуємо дані для RSI
        # Granularity для Bitget API v2: 1min, 5min, 15min, 30min, 1h, 4h, 1day тощо.
        # Виправимо granularity, якщо передано "5m" замість "5min"
        bitget_granularity = "5min" if granularity == "5m" else granularity
        
        candles_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={symbol}&granularity={bitget_granularity}&limit=100"
        candles_resp = requests.get(candles_url, timeout=10)
        
        rsi_val = None
        if candles_resp.status_code == 200:
            candles_data = candles_resp.json()
            if 'data' in candles_data and candles_data['data']:
                candles = candles_data['data']
                # У Bitget API v2 свічки повертаються як масив масивів:
                # [ts, open, high, low, close, vol, quoteVol]
                # Закриття — це індекс 4
                close_prices = [float(c[4]) for c in candles]
                # Свічки зазвичай йдуть від нових до старих, тому розвертаємо для RSI
                close_prices.reverse()
                
                # Додаємо поточну ціну для "живого" RSI
                close_prices.append(current_price)
                
                rsi_val = calculate_rsi(close_prices, period=14)
            else:
                logger.warning("Candles API повернув порожні дані для RSI")
        else:
            logger.error(f"Помилка Candles API: статус {candles_resp.status_code}")
            
        return current_price, rsi_val
        
    except Exception as e:
        logger.error(f"Критична помилка в get_bitget_data: {e}")
        return None, None
