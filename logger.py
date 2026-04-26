import logging

def setup_logger():
    """
    Налаштовує логування: чистий текст у файл та мінімалістичний вивід у консоль.
    """
    # Створюємо логер
    logger = logging.getLogger("Nexus")
    logger.setLevel(logging.INFO)
    
    # Видаляємо старі обробники, якщо вони є
    if logger.hasHandlers():
        logger.handlers.clear()

    # 1. Налаштування запису у файл (без кольорів, тільки текст)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler("nexus.log", encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    
    # 2. Налаштування виводу в консоль (максимально коротко)
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Додаємо обробники до логера
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Вимикаємо дублювання логів від бібліотеки requests
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger
