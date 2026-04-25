import requests
from utils import calculate_rsi

def get_bitget_data(symbol, granularity="5m"):
    """
    Отримує поточну ціну та розраховує RSI через API Bitget.
    Повертає кортеж (price, rsi_val).
    """
    try:
        # 1. Отримуємо поточну ціну
        ticker_url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
        ticker_resp = requests.get(ticker_url, timeout=10)
        
        if ticker_resp.status_code != 200:
            return None, None
            
        ticker_data = ticker_resp.json()
        current_price = float(ticker_data['data'][0]['lastPr'])
        
        # 2. Отримуємо дані для RSI
        candles_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={symbol}&granularity={granularity}&limit=100"
        candles_resp = requests.get(candles_url, timeout=10)
        
        rsi_val = None
        if candles_resp.status_code == 200:
            candles = candles_resp.json()['data']
            close_prices = [float(c[4]) for c in candles]
            close_prices.reverse()
            close_prices.append(current_price)
            rsi_val = calculate_rsi(close_prices, period=14)
            
        return current_price, rsi_val
        
    except Exception:
        return None, None
