import stockmarket
import coin
import bingxcoin
import threading
coinExp = coin.Coin
class BingXStockMarketImpl(stockmarket.StockMarket):
    def __init__(self):
        self.url = "wss://open-api-ws.bingx.com/market"
        self.coin_list = {}
        self.thread_coin_list = {}

    def create_btc_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.url, channel, "BING-X-BTC")
        self.coin_list["BTC"] = new_coin
        new_coin.start()

    def create_eth_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "ETH-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.url, channel, "BING-X-ETX")
        self.coin_list["ETH"] = new_coin
        new_coin.start()

    def add_coin(self, name):
        thread_coin = 0
        if name == "BTC":
            thread_coin = threading.Thread(target=self.create_btc_coin, args=(), name="BTC")
        elif name == "ETH":
            thread_coin = threading.Thread(target=self.create_eth_coin, args=(), name="ETH")
        self.thread_coin_list[name] = thread_coin
        thread_coin.start()

    def start(self):
        for coin_thread in self.thread_coin_list.values():
            coin_thread.join()

    def get_coin_cost(self, name):
        return self.coin_list[name].getCurrentCost()
