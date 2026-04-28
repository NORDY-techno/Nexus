import sys
import asyncio

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
