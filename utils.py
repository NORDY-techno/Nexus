import time
import sys
import asyncio

def animate_wait(seconds):
    """
    Функція для анімованого очікування (синхронна).
    """
    symbols = ["|", "/", "-", "\\"]
    iterations = int(seconds / 0.1)
    
    for i in range(iterations):
        symbol = symbols[i % 4]
        sys.stdout.write(f"\rОчікування... [{symbol}]")
        sys.stdout.flush()
        time.sleep(0.1)
    
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()

async def async_animate_wait(seconds):
    """
    Асинхронна функція для анімованого очікування.
    """
    symbols = ["|", "/", "-", "\\"]
    iterations = int(seconds / 0.1)
    
    for i in range(iterations):
        symbol = symbols[i % 4]
        sys.stdout.write(f"\rОчікування... [{symbol}]")
        sys.stdout.flush()
        await asyncio.sleep(0.1)
    
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()

def calculate_rsi(prices, period=14):
    """
    Розрахунок індикатора RSI за методом Вайлдера (як у TradingView).
    """
    if len(prices) < period + 1:
        return None
    
    # 1. Рахуємо різницю (зміни)
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i-1])
        
    # 2. Поділяємо на прибутки та збитки
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    
    # 3. Перше середнє значення — це просте середнє (SMA) за перший період
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # 4. Всі наступні значення рахуємо за методом згладжування Вайлдера (Wilder's Smoothing)
    # Формула: Alpha = 1 / period
    # NewAvg = PrevAvg * (1 - Alpha) + CurrentValue * Alpha
    # Що еквівалентно: NewAvg = (PrevAvg * (period - 1) + CurrentValue) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
