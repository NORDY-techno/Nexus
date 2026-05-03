import logging

logger = logging.getLogger("Nexus")
BASE_URL = "https://api.bitget.com/api/v2/spot/market"

async def get_all_bitget_prices(session, symbols):
    try:
        async with session.get(f"{BASE_URL}/tickers", timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {t['symbol']: float(t['lastPr']) for t in data.get('data', []) if t['symbol'] in symbols}
            logger.error(f"Ticker API error: {resp.status}")
    except Exception as e:
        logger.error(f"Price fetch error: {e}")
    return {}
