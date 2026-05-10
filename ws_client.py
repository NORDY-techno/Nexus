import asyncio
import json
import logging
import websockets

logger = logging.getLogger("Nexus")
WS_URL = "wss://ws.bitget.com/v2/ws/public"

class BitgetWS:
    def __init__(self, symbols, callback):
        self.symbols = symbols
        self.callback = callback
        self.ws = None

    async def connect(self):
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    self.ws = ws
                    logger.info("WebSocket connected to Bitget")
                    
                    # Підписка на тікери для всіх символів
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": [{"instType": "SPOT", "channel": "ticker", "instId": s} for s in self.symbols]
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    
                    async for message in ws:
                        data = json.loads(message)
                        if data.get("action") == "snapshot" or data.get("action") == "update":
                            for item in data.get("data", []):
                                symbol = item.get("instId")
                                price = float(item.get("lastPr", 0))
                                if symbol and price:
                                    await self.callback(symbol, price)
                                    
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    async def stop(self):
        if self.ws:
            await self.ws.close()
