import requests  # Імпортуємо бібліотеку для роботи з інтернет-запитами
import time      # Для коротких пауз при помилках
from utils import animate_wait  # Імпортуємо нашу функцію анімації
from logger import setup_logger # Імпортуємо налаштування логера

# Ініціалізуємо логер
logger = setup_logger()

# Коди кольорів для консолі (ANSI escape codes)
GREEN = "\033[92m"   # Зелений колір
RED = "\033[91m"     # Червоний колір
RESET = "\033[0m"    # Скидання кольору до звичайного

# Змінна для збереження попередньої ціни
last_price = None

logger.info("Nexus запущено. Починаємо відстеження ціни ETH/USDT.")

# Створюємо нескінченний цикл
while True:
    try:
        # Запит до Binance
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=10)
        
        # Перевіряємо, чи успішний запит (код 200)
        if response.status_code == 200:
            current_price = float(response.json()['price'])
            
            if last_price is not None:
                # Розрахунок зміни
                change = ((current_price - last_price) / last_price) * 100
                
                # Визначаємо колір для консолі
                if change >= 0.1:
                    color, sign = GREEN, "+"
                elif change <= -0.1:
                    color, sign = RED, ""
                else:
                    color, sign = RESET, ""
                
                # Формуємо повідомлення
                msg = f"Ціна: {current_price} USDT | Зміна: {sign}{change:.2f}%"
                
                # Записуємо в лог
                logger.info(msg)
            
            # Оновлюємо попередню ціну
            last_price = current_price
            
            # Якщо все пройшло успішно, чекаємо 30 секунд до наступного планового запиту
            animate_wait(30)
            
        else:
            logger.error(f"Біржа відповіла помилкою {response.status_code}. Спробуємо знову через 5 секунд...")
            time.sleep(5)
            continue
            
    except Exception as e:
        logger.error(f"Помилка зв'язку: {e}. Повторна спроба через 5 секунд...")
        time.sleep(5)
        continue
