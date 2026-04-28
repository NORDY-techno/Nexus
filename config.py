# Налаштування списку активів
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"
]

# Таймфрейм для RSI та аналізу
GRANULARITY = "5m"

# Пороги для сповіщень та кольорового виводу
COLOR_THRESHOLD = 0.1    # Поріг для зміни кольору в терміналі (у відсотках)
TG_THRESHOLD = 0.01      # Поріг для відправки в Telegram (у відсотках)

# Затримка перед оновленням після закриття свічки (у секундах)
UPDATE_DELAY = 2
