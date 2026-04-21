import requests  # Імпортуємо бібліотеку для роботи з інтернет-запитами
import time      # Імпортуємо бібліотеку для роботи з часом (паузами)

# Коди кольорів для консолі (ANSI escape codes)
GREEN = "\033[92m"   # Зелений колір
RED = "\033[91m"     # Червоний колір
RESET = "\033[0m"    # Скидання кольору до звичайного

# Створюємо змінну для зберігання попередньої ціни (спочатку вона порожня)
last_price = None

# Створюємо нескінченний цикл, щоб програма працювала постійно
while True:
    try:
        # Робимо запит до публічного API Binance для отримання ціни ETH/USDT
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
        
        # Перетворюємо відповідь у формат JSON та беремо ціну як число
        current_price = float(response.json()['price'])
        
        # Якщо у нас вже була збережена попередня ціна, рахуємо зміну
        if last_price is not None:
            # Рахуємо зміну у відсотках
            change = ((current_price - last_price) / last_price) * 100
            
            # Визначаємо колір та знак залежно від зміни ціни
            if change > 0:
                color = GREEN
                sign = "+"
            elif change < 0:
                color = RED
                sign = ""
            else:
                color = RESET
                sign = ""
            
            # Виводимо кольорове повідомлення (2 знаки після коми)
            print(f"{color}Ціна: {current_price} USDT | Зміна: {sign}{change:.2f}%{RESET}")
        # Оновлюємо попередню ціну поточною для наступного кроку циклу
        last_price = current_price
    except Exception as e:
        # Вивід повідомлення про помилку
        print(f"Виникла помилка під час запиту: {e}")
    
    # Робимо паузу на 30 секунд
    time.sleep(30)
