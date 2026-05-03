import asyncio, logging
from tradingview_ta import Interval, get_multiple_analysis

logger = logging.getLogger("Nexus")

def get_tv_interval(gran):
    m = {"1m": Interval.INTERVAL_1_MINUTE, "5m": Interval.INTERVAL_5_MINUTES, "15m": Interval.INTERVAL_15_MINUTES, "1h": Interval.INTERVAL_1_HOUR}
    return m.get(gran, Interval.INTERVAL_5_MINUTES)

async def get_all_rsi_data(symbols, gran="5m"):
    try:
        analysis = await asyncio.to_thread(get_multiple_analysis, screener="crypto", interval=get_tv_interval(gran), symbols=[f"BITGET:{s}" for s in symbols])
        return {k.split(":")[1]: v.indicators.get("RSI") for k, v in analysis.items() if v and hasattr(v, 'indicators')}
    except Exception as e:
        logger.error(f"RSI fetch error: {e}")
        return {s: None for s in symbols}
