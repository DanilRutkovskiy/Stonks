import asyncio
import json
from typing import Optional, Dict, Any
import threading
import websocket
import gzip
import io
import coin
import database
from Structs.network import network

import logging
logging.basicConfig(level=logging.INFO)

class BingXCoinImpl(coin.Coin):
    def __init__(self, url: str, channel: dict, name: str):
        super().__init__()
        self.url: str = url
        self.ws: Optional[websocket.WebSocketApp] = None
        self.channel: dict = channel
        self.current_cost: float = 0
        self.commission: float = self.current_cost * 0.1
        self.name: str = name
        self.symbol: str = self.name + '-USDT'
        self.coin_network: network
        self.lock = threading.Lock()
        self.logger = logging.getLogger('logger')

        self._load_network_data()

    def _on_open(self, ws):
        ws.send(json.dumps(self.channel))

    def _on_message(self, ws, message):
        try:
            compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
            decompressed_data = compressed_data.read()
            utf8_data = decompressed_data.decode('utf-8')

            if "ping" in utf8_data:  # this is very important , if you receive 'Ping' you need to send 'pong'
                ws.send("Pong")

            json_data = json.loads(utf8_data)
            cost_string = json_data.get("data", {}).get("c")
            if cost_string:
                with self.lock:
                    self.current_cost = float(cost_string.replace(",", "."))
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
        except Exception as e:
            print(f"Unknown error:{e}")

    def _on_error(self, ws, error):
        self.logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")

    def _load_network_data(self):
        db = database.StockMarketDb()
        self.coin_network = db.get_best_network_for_coin(self.name, 'BINGX')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws.run_forever()
        self.logger.info("WebSocket disconnected. Reconnecting...")
        asyncio.sleep(5)

    def get_current_cost(self):
        with self.lock:
            return float(self.current_cost)

    def get_commission(self):
        return float(self.commission)

    def get_coin_network(self):
        return self.coin_network
