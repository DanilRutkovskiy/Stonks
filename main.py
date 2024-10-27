import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time

coins = {1:"BTC", 2:"ETH"}

def testStock(stock):
    while True:
        print("BTC: " + str(stock.getCoinCost("BTC")))
        print("ETH: " + str(stock.getCoinCost("ETH")))
        time.sleep(1)

if __name__ == "__main__":
    bingX = bingxstockmarket.BingXStockMarketImpl()
    bingX.addCoin("BTC")
    bingX.addCoin("ETH")

    thredd = threading.Thread(target=testStock, args=(bingX,), name="MainApplication")
    thredd.start()
    bingX.start()