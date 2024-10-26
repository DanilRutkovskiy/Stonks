import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time

coins = {1:"BTC", 2:"ETH"}

def testStock(stock):
    stock.start()
    while True:
        print(stock.getCoinCost("BTC"))
        print(stock.getCoinCost("ETH"))
        time.sleep(1)

if __name__ == "__main__":
    bingX = bingxstockmarket.BingXStockMarketImpl()

    bingX.addCoin("BTC")
    bingX.addCoin("ETH")

    testStock(bingX)