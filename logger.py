import logging

def setup_logger():
    """
    Налаштовує логування: запис у файл nexus.log та вивід у консоль.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("nexus.log", encoding="utf-8"),  # Запис у файл
            logging.StreamHandler()  # Вивід у консоль
        ]
    )
    return logging.getLogger("Nexus")
