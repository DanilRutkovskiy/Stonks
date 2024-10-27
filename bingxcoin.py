import json
import websocket
import gzip
import io
import coin

class BingXCoinImpl(coin.Coin):
    def __init__(self, url, channel, indicator):
        self.url = url
        self.ws = None
        self.channel = channel
        self.indicator = indicator
        self.current_cost = 0

    def on_open(self, ws):
        #print('WebSocket connected')
        ws.send(json.dumps(self.channel))
        #print("Subscribed to :", subStr)

    def on_data(self, ws, string, type, continue_flag):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(string), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        #print(utf8_data)

    def on_message(self, ws, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')

        json_data = json.loads(utf8_data)
        cost_string = json_data.get("data", {}).get("c")
        if cost_string:
            self.current_cost = float(cost_string.replace(",", "."))
        #print(self.indicator + ": " + self.currentCost)  # this is the message you need
        if "ping" in utf8_data:  # this is very important , if you receive 'Ping' you need to send 'pong'
            ws.send("Pong")

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            #on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def getCurrentCost(self):
        return self.current_cost