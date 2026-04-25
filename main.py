import time
from utils import animate_wait
from logger import setup_logger
from bitget_api import get_bitget_data

# Ініціалізуємо логер
logger = setup_logger()

# Коди кольорів для консолі
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Налаштування
SYMBOL = "ETHUSDT"
GRANULARITY = "5m"

# Змінна для збереження попередньої ціни
last_price = None

logger.info(f"Nexus запущено. Моніторинг {SYMBOL} (Bitget) + RSI(14) M5.")

while True:
    # Отримуємо дані через окремий модуль API
    current_price, rsi_val = get_bitget_data(SYMBOL, GRANULARITY)
    
    if current_price is not None:
        rsi_text = f" | RSI(14): {rsi_val:.2f}" if rsi_val is not None else ""
        
        if last_price is not None:
            change = ((current_price - last_price) / last_price) * 100
            
            if change >= 0.1:
                color, sign = GREEN, "+"
            elif change <= -0.1:
                color, sign = RED, ""
            else:
                color, sign = RESET, ""
            
            logger.info(f"{color}Ціна: {current_price} USDT | Зміна: {sign}{change:.2f}%{rsi_text}{RESET}")
        
        last_price = current_price
        animate_wait(30)
    else:
        logger.error("Не вдалося отримати дані з Bitget. Повтор через 5 секунд...")
        time.sleep(5)
