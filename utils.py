import time
import sys

def animate_wait(seconds):
    """
    Функція для анімованого очікування.
    Вона показує символ, що обертається, поки програма чекає.
    """
    symbols = ["|", "/", "-", "\\"]
    
    # Робимо кроки по 0.1 секунди, щоб анімація була плавною
    iterations = int(seconds / 0.1)
    
    for i in range(iterations):
        symbol = symbols[i % 4]
        # \r повертає курсор на початок рядка
        # end="" дозволяє не переходити на новий рядок
        sys.stdout.write(f"\rОчікування... [{symbol}]")
        sys.stdout.flush()
        time.sleep(0.1)
    
    # Очищаємо рядок після завершення очікування
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()

def calculate_rsi(prices, period=14):
    """
    Розрахунок індикатора RSI (Relative Strength Index).
    Приймає список цін закриття.
    """
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    # Рахуємо різницю між сусідніми цінами
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
            
    # Перше середнє значення (просте середнє)
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Наступні значення за методом згладжування Уайлдера
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
