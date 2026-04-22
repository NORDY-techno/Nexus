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
