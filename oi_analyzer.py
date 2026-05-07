import logging
import asyncio

logger = logging.getLogger("Nexus")

# Словник для збереження попередніх значень OI та ціни {symbol: {"oi": val, "price": val}}
oi_cache = {}

async def check_oi_anomaly(exchange, symbol, curr_price):
    global oi_cache
    try:
        swap_symbol = f"{symbol[:-4]}/USDT:USDT"
        data = await exchange.fetch_open_interest(swap_symbol)
        curr_oi = float(data.get('openInterestAmount') or data.get('baseSelfValue') or 0)

        if curr_oi == 0: return None

        if symbol not in oi_cache:
            oi_cache[symbol] = {"oi": curr_oi, "price": curr_price}
            return None

        prev = oi_cache[symbol]
        oi_change = ((curr_oi - prev['oi']) / prev['oi']) * 100
        price_change = ((curr_price - prev['price']) / prev['price']) * 100
        oi_cache[symbol] = {"oi": curr_oi, "price": curr_price}
        
        logger.info(f"OI Debug [{symbol}]: OI {curr_oi}, Change {oi_change:+.2f}%")

        if abs(oi_change) >= 0.1:
            status = ""
            if price_change >= 0 and oi_change > 0: status = "Bullish: New Longs entering"
            elif price_change < 0 and oi_change > 0: status = "Bearish: New Shorts entering"
            elif price_change >= 0 and oi_change < 0: status = "Weakening: Long Liquidation/Exit"
            elif price_change < 0 and oi_change < 0: status = "Short Squeeze Risk: Shorts covering"

            if status:
                logger.info(f"OI ALERT [{symbol}]: {status} | OI: {oi_change:+.2f}%")
                return {"status": status, "oi_change": oi_change, "price_change": price_change}
        return None
    except Exception as e:
        logger.error(f"OI Error {symbol}: {e}")
        return None
