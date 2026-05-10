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

    async def heartbeat(self, ws):
        """Відправка текстового 'ping' кожні 20 секунд для підтримки з'єднання"""
        try:
            while True:
                await asyncio.sleep(20)
                if ws.open:
                    await ws.send("ping")
        except Exception:
            pass

    async def connect(self):
        while True:
            try:
                # Вимикаємо вбудовані протокольні пінги, бо Bitget очікує текстові
                async with websockets.connect(
                    WS_URL, 
                    ping_interval=None, 
                    close_timeout=5
                ) as ws:
                    self.ws = ws
                    logger.info("WebSocket connected to Bitget")
                    
                    # Запускаємо фонову задачу Heartbeat (текстовий ping)
                    heartbeat_task = asyncio.create_task(self.heartbeat(ws))
                    
                    # Підписка на тікери
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": [{"instType": "SPOT", "channel": "ticker", "instId": s} for s in self.symbols]
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    
                    try:
                        async for message in ws:
                            if message == "pong":
                                continue
                                
                            data = json.loads(message)
                            # Перевірка на помилки від сервера
                            if data.get("event") == "error":
                                logger.error(f"Bitget WS Error: {data.get('msg')}")
                                break
                                
                            if data.get("action") in ["snapshot", "update"]:
                                for item in data.get("data", []):
                                    symbol = item.get("instId")
                                    price = float(item.get("lastPr", 0))
                                    if symbol and price:
                                        await self.callback(symbol, price)
                    finally:
                        heartbeat_task.cancel()
                        
            except Exception as e:
                # Приглушуємо лог про відсутність close frame, бо це наслідок розриву
                if "no close frame" not in str(e):
                    logger.warning(f"WebSocket Connection Lost: {e}. Reconnecting...")
                await asyncio.sleep(5)

    async def stop(self):
        if self.ws:
            await self.ws.close()
