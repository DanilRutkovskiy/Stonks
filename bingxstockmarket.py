import stockmarket
import coin
import bingxcoin
import threading
coinExp = coin.Coin
class BingXStockMarketImpl(stockmarket.StockMarket):
    def __init__(self):
        self.url = "wss://open-api-ws.bingx.com/market"
        self.coinList = {}
        self.threadCoinList = {}

    def createBtcCoin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}
        newCoin = bingxcoin.BingXCoinImpl(self.url, channel, "BING-X-BTC")
        self.coinList["BTC"] = newCoin
        newCoin.start()

    def createEthCoin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "ETH-USDT@lastPrice"}
        newCoin = bingxcoin.BingXCoinImpl(self.url, channel, "BING-X-ETX")
        self.coinList["ETH"] = newCoin
        newCoin.start()

    def addCoin(self, name):
        thread_coin = 0
        if name == "BTC":
            thread_coin = threading.Thread(target=self.createBtcCoin, args=(), name="BTC")
        elif name == "ETH":
            thread_coin = threading.Thread(target=self.createEthCoin, args=(), name="ETH")
        self.threadCoinList[name] = thread_coin
        thread_coin.start()

    def start(self):
        for coin_thread in self.threadCoinList.values():
            coin_thread.join()

    def getCoinCost(self, name):
        return self.coinList[name].getCurrentCost()
