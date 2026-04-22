import requests  # Імпортуємо бібліотеку для роботи з інтернет-запитами
from utils import animate_wait  # Імпортуємо нашу функцію анімації

# Коди кольорів для консолі (ANSI escape codes)
GREEN = "\033[92m"   # Зелений колір
RED = "\033[91m"     # Червоний колір
RESET = "\033[0m"    # Скидання кольору до звичайного

# Змінна для збереження попередньої ціни
last_price = None

# Створюємо нескінченний цикл
while True:
    try:
        # Запит до Binance
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
        current_price = float(response.json()['price'])
        
        if last_price is not None:
            # Розрахунок зміни
            change = ((current_price - last_price) / last_price) * 100
            
            # Визначаємо колір
            if change >= 0.1:
                color, sign = GREEN, "+"
            elif change <= -0.1:
                color, sign = RED, ""
            else:
                color, sign = RESET, ""
            
            # Виводимо результат
            print(f"{color}Ціна: {current_price} USDT | Зміна: {sign}{change:.2f}%{RESET}")
        
        # Оновлюємо попередню ціну
        last_price = current_price
        
    except Exception as e:
        print(f"Виникла помилка: {e}")
    
    # Викликаємо анімоване очікування на 30 секунд з utils.py
    animate_wait(30)
