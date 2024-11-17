import coin
from pybit.unified_trading import WebSocket

class ByBitCoinImpl(coin.Coin):
    def __init__(self, coin_name):
        super().__init__()
        self.ws = None
        self.current_cost = 0
        self.coin_name = coin_name
        self.channel_type = "linear"
        self.commission = 0.1

    def handle_message(self, message):
        self.update_cost(message)

    def update_cost(self, new_cost):
        cost = new_cost['data']['markPrice']
        if cost == '':
            self.current_cost = 10000000
        else:
            self.current_cost = float(new_cost['data']['markPrice'])

    def start(self):
        ws = WebSocket(
            testnet=True,
            channel_type=self.channel_type,
        )
        ws.ticker_stream(
            symbol=self.coin_name+'USDT',
            callback=self.handle_message
        )
        self.ws.run_forever()

    def get_current_cost(self):
        return self.current_cost