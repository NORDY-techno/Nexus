# Nexus v2: Real-Time Multi-Asset Guardian

Nexus v2 is a high-performance, real-time cryptocurrency monitoring system powered by WebSocket technology. It tracks live prices via Bitget WebSocket API, analyzes technical indicators (RSI), volume changes, and Open Interest anomalies, providing instant alerts through Telegram and a color-coded terminal interface.

## Key Features

- **Real-Time WebSocket Streaming**: Instant price updates via Bitget WebSocket API with automatic reconnection and heartbeat management.
- **Advanced Market Analysis**: 
  - **RSI Indicators**: Accurate RSI values from TradingView servers
  - **Volume Analysis**: Real-time volume change detection with spike alerts (>100%)
  - **Open Interest Monitoring**: Detects OI anomalies and market sentiment shifts
- **Smart Alert System**: Multi-condition Telegram notifications triggered by:
  - Significant price movements (configurable threshold)
  - Volume spikes (≥100% increase)
  - Open Interest anomalies with market interpretation
- **Asynchronous Architecture**: Powered by `asyncio` and `aiohttp` for efficient multi-asset monitoring.
- **Optimized Performance**: 
  - WebSocket for real-time price updates
  - Background indicator updates synchronized with candle closures
  - Bulk data fetching to avoid rate limiting
- **Modular Design**: Clean separation between WebSocket client, API logic, analyzers, and utilities.
- **Advanced Logging**: Centralized logging with automatic file rotation (max 5MB).

## Visual Indicators

### Price Change
- 📈 **Price Up**: Significant upward movement (default threshold: 0.1%).
- 📉 **Price Down**: Significant downward movement.
- 📊 **Flat**: Minor price fluctuations.

### RSI Levels
- 🟢 **Overbought**: RSI > 70.
- 🔵 **Oversold**: RSI < 30.
- ⚪ **Neutral**: RSI between 30 and 70.

### Volume Changes
- 🔥 **Volume Spike**: Volume increase ≥100%.
- ⬆️ **Volume Up**: Positive volume change.
- ⬇️ **Volume Down**: Negative volume change.
- ⚪ **Neutral**: No significant volume change.

### Open Interest Status
- **Bullish**: Price ↑ + OI ↑ (New longs entering)
- **Bearish**: Price ↓ + OI ↑ (New shorts entering)
- **Weakening**: Price ↑ + OI ↓ (Long liquidation/exit)
- **Short Squeeze Risk**: Price ↓ + OI ↓ (Shorts covering)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NORDY-techno/Nexus.git
   cd Nexus
   ```

2. **Install dependencies**:
   ```bash
   pip install aiohttp python-dotenv tradingview-ta ccxt websockets
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
- `COLOR_THRESHOLD`: Threshold for terminal color highlights (default: 0.1%).
- `TG_THRESHOLD`: Threshold for Telegram push notifications (default: 0.1%).
- `UPDATE_DELAY`: Delay after candle closure before updating indicators (default: 2 seconds).

## Usage

Start the guardian:
```bash
python main.py
```

The system will:
1. Connect to Bitget WebSocket for real-time price streaming
2. Initialize background tasks for RSI, Volume, and OI analysis
3. Send a startup notification to Telegram
4. Display color-coded updates in the terminal
5. Send Telegram alerts when thresholds are met

## Architecture

### Core Components

- **main.py**: Main orchestrator with WebSocket integration and background indicator updates
- **ws_client.py**: Bitget WebSocket client with automatic reconnection and heartbeat
- **bitget_api.py**: REST API integration for bulk price fetching
- **indicators.py**: TradingView RSI data fetching
- **volume_analyzer.py**: Real-time volume change analysis
- **oi_analyzer.py**: Open Interest anomaly detection with market sentiment interpretation
- **telegram_bot.py**: Telegram notification system
- **utils.py**: Helper functions for emojis and formatting
- **logger.py**: Centralized logging system
- **config.py**: Configuration management

### Data Flow

1. **Real-Time Updates**: WebSocket streams live prices → `process_ticker()` → Terminal/Telegram
2. **Background Analysis**: Periodic updates (synchronized with candle closures):
   - RSI from TradingView
   - Volume changes from CCXT
   - Open Interest from Bitget Futures
3. **Smart Alerts**: Multi-condition logic triggers Telegram notifications

## Alert Conditions

Telegram notifications are sent when ANY of these conditions are met:
- Price change ≥ `TG_THRESHOLD` (default: 0.1%)
- Volume spike ≥ 100%
- Open Interest anomaly detected (OI change ≥ 0.1% with market interpretation)

## Security

- Sensitive data is stored in `.env`.
- Project rules for AI assistants are managed via `.traerules`.
- Both `.env` and `.traerules` are ignored by Git via `.gitignore`.

## License

MIT License. See `LICENSE` for details.

## What's New in v2

- ✨ **WebSocket Integration**: Real-time price streaming instead of polling
- 📊 **Open Interest Analysis**: New OI anomaly detection with market sentiment
- 🔥 **Volume Spike Detection**: Automatic alerts for volume surges ≥100%
- ⚡ **Optimized Performance**: Background indicator updates synchronized with candle closures
- 🎯 **Smart Alert System**: Multi-condition Telegram notifications
- 🔄 **Auto-Reconnection**: Robust WebSocket connection management with heartbeat
