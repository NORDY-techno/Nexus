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
    Розрахунок індикатора RSI за методом Вайлдера (RMA), як у TradingView.
    """
    if len(prices) < period + 1:
        return None
    
    # 1. Рахуємо різниці (зміни ціни)
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i-1])
        
    # 2. Початкові середні (SMA за перший період)
    avg_gain = 0.0
    avg_loss = 0.0
    
    for i in range(period):
        d = deltas[i]
        if d > 0:
            avg_gain += d
        else:
            avg_loss -= d
            
    avg_gain /= period
    avg_loss /= period
    
    # 3. Згладжування за методом Вайлдера (RMA)
    # Формула: Alpha = 1 / period
    # NewAvg = (PrevAvg * (period - 1) + CurrentValue) / period
    for i in range(period, len(deltas)):
        d = deltas[i]
        gain = d if d > 0 else 0.0
        loss = -d if d < 0 else 0.0
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
