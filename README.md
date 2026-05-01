# Nexus: Multi-Asset Guardian

Nexus is a high-performance, asynchronous monitoring tool for cryptocurrency assets. It tracks real-time prices via Bitget API and technical indicators (RSI) via TradingView, providing instant updates through a Telegram bot and a clean terminal interface.

## Key Features

- **Asynchronous Execution**: Powered by `asyncio` and `aiohttp` for simultaneous multi-asset monitoring without delays.
- **Accurate Indicators**: Integrated with `tradingview-ta` to fetch 100% accurate RSI values directly from TradingView servers.
- **Bulk Data Fetching**: Optimized API requests (bulk fetching) to avoid rate limiting (HTTP 429).
- **Telegram Integration**: Instant notifications for significant price changes and RSI levels.
- **Modular Architecture**: Clean separation between API logic, configuration, and utilities.
- **Advanced Logging**: Centralized logging with automatic file rotation (max 5MB).

## Visual Indicators

### Price Change
- 📈 **Price Up**: Significant upward movement (default threshold: 0.1%).
- 📉 **Price Down**: Significant downward movement.
- � **Flat**: Minor price fluctuations.

### RSI Levels
- 🟢 **Overbought**: RSI > 70.
- � **Oversold**: RSI < 30.
- ⚪ **Neutral**: RSI between 30 and 70.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NORDY-techno/Nexus.git
   cd Nexus
   ```

2. **Install dependencies**:
   ```bash
   pip install aiohttp python-dotenv tradingview-ta
   ```

3. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   TELEGRAM_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## Configuration

Modify `config.py` to customize:
- `SYMBOLS`: List of assets to monitor (e.g., `BTCUSDT`, `ETHUSDT`).
- `GRANULARITY`: Timeframe for analysis (`1m`, `5m`, `15m`, `1h`).
- `COLOR_THRESHOLD`: Threshold for terminal color highlights.
- `TG_THRESHOLD`: Threshold for Telegram push notifications.

## Usage

Start the guardian:
```bash
python main.py
```

## Security

- Sensitive data is stored in `.env`.
- Project rules for AI assistants are managed via `.traerules`.
- Both `.env` and `.traerules` are ignored by Git via `.gitignore`.

## License

MIT License. See `LICENSE` for details.
