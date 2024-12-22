import coin
from pybit.unified_trading import WebSocket
import database
from Structs.network import network

class ByBitCoinImpl(coin.Coin):
    def __init__(self, coin_name):
        super().__init__()
        self.ws = None
        self.current_cost = 0
        self.coin_name = coin_name
        self.channel_type = "spot"
        self.commission = self.current_cost * 0.1
        self.coin_network: network
        self.symbol = self.coin_name + 'USDT'

        self._load_network_data()

    def handle_message(self, message):
        self.update_cost(message)

    def update_cost(self, new_cost):
        cost = new_cost['data']['usdIndexPrice']
        if cost != '':
            self.current_cost = float(new_cost['data']['usdIndexPrice'])

    def _load_network_data(self):
        db = database.StockMarketDb()
        self.coin_network = db.get_best_network_for_coin(self.coin_name, 'BYBIT')

    def start(self):
        ws = WebSocket(
            testnet=False,
            channel_type=self.channel_type,
        )
        ws.ticker_stream(
            symbol=self.coin_name+'USDT',
            callback=self.handle_message
        )
        self.ws.run_forever()

    def get_current_cost(self):
        return self.current_cost

    def get_commission(self):
        return float(self.commission)

    def get_coin_network(self):
        return self.coin_network