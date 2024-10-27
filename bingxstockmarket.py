import stockmarket
import coin
import bingxcoin
import threading
import coins_dict

class BingXStockMarketImpl(stockmarket.StockMarket):
    def __init__(self):
        super().__init__()
        self.url = "wss://open-api-ws.bingx.com/market"
        self.coin_list = {}
        self.thread_coin_list = {}
        self.is_ready = False

    def create_btc_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.url, channel)
        self.coin_list[coins_dict.get_btc_name()] = new_coin
        new_coin.start()

    def create_eth_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "ETH-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.url, channel)
        self.coin_list[coins_dict.get_eth_name()] = new_coin
        new_coin.start()

    def add_coin(self, name):
        thread_coin = 0
        if name == coins_dict.get_btc_name():
            thread_coin = threading.Thread(target=self.create_btc_coin, args=(), name=coins_dict.get_btc_name())
        elif name == coins_dict.get_eth_name():
            thread_coin = threading.Thread(target=self.create_eth_coin, args=(), name=coins_dict.get_eth_name())
        self.thread_coin_list[name] = thread_coin
        thread_coin.start()

    def start(self):
        self.is_ready = True
        for coin_thread in self.thread_coin_list.values():
            coin_thread.join()

    def get_coin_cost(self, name):
        return self.coin_list[name].get_current_cost()

    def ready(self):
        return self.is_ready
