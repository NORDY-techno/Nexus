import requests  # Імпортуємо бібліотеку для роботи з інтернет-запитами
import time      # Для коротких пауз при помилках
from utils import animate_wait, calculate_rsi  # Імпортуємо допоміжні функції
from logger import setup_logger # Імпортуємо налаштування логера

# Ініціалізуємо логер
logger = setup_logger()

# Коди кольорів для консолі (ANSI escape codes)
GREEN = "\033[92m"   # Зелений колір
RED = "\033[91m"     # Червоний колір
RESET = "\033[0m"    # Скидання кольору до звичайного

# Налаштування моніторингу
SYMBOL = "ETHUSDT"
GRANULARITY = "5m" # Таймфрейм M5 для RSI

# Змінна для збереження попередньої ціни
last_price = None

logger.info(f"Nexus переключено на Bitget API. Моніторинг {SYMBOL} та RSI(14) на M5.")

# Створюємо нескінченний цикл
while True:
    try:
        # 1. Отримуємо поточну ціну через Bitget Ticker API
        ticker_url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={SYMBOL}"
        ticker_resp = requests.get(ticker_url, timeout=10)
        
        if ticker_resp.status_code == 200:
            ticker_data = ticker_resp.json()
            current_price = float(ticker_data['data'][0]['lastPr'])
            
            # 2. Отримуємо історичні дані для RSI (таймфрейм M5)
            candles_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={SYMBOL}&granularity={GRANULARITY}&limit=100"
            candles_resp = requests.get(candles_url, timeout=10)
            
            rsi_text = ""
            if candles_resp.status_code == 200:
                # Bitget повертає свічки від нових до старих
                candles = candles_resp.json()['data']
                # Беремо ціни закриття (індекс 4) і розвертаємо список для правильного розрахунку
                close_prices = [float(c[4]) for c in candles]
                close_prices.reverse()
                
                # Додаємо поточну ціну як останню "незакриту" свічку для актуальності RSI
                close_prices.append(current_price)
                
                rsi_val = calculate_rsi(close_prices, period=14)
                if rsi_val is not None:
                    rsi_text = f" | RSI(14): {rsi_val:.2f}"
            
            # 3. Розрахунок зміни ціни та вивід
            if last_price is not None:
                change = ((current_price - last_price) / last_price) * 100
                
                if change >= 0.1:
                    color, sign = GREEN, "+"
                elif change <= -0.1:
                    color, sign = RED, ""
                else:
                    color, sign = RESET, ""
                
                msg = f"Ціна: {current_price} USDT | Зміна: {sign}{change:.2f}%{rsi_text}"
                logger.info(msg)
            
            last_price = current_price
            animate_wait(30)
            
        else:
            logger.error(f"Bitget повернув помилку {ticker_resp.status_code}. Спробуємо знову через 5 секунд...")
            time.sleep(5)
            continue
            
    except Exception as e:
        logger.error(f"Помилка зв'язку з Bitget: {e}. Повторна спроба через 5 секунд...")
        time.sleep(5)
        continue
