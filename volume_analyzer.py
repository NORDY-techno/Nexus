import logging
logger = logging.getLogger("Nexus")

async def get_bitget_volume_data(ex, sym, tf='5m'):
    try:
        h = await ex.fetch_ohlcv(sym, timeframe=tf, limit=3)
        if len(h) < 2: return None
        p, c = (h[-3][5], h[-2][5]) if len(h) == 3 else (h[0][5], h[1][5])
        return ((c - p) / p * 100) if p != 0 else 0.0
    except Exception as e:
        logger.error(f"Vol error {sym}: {e}")
        return None
