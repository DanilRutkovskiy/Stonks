import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time

coins = {1:"BTC", 2:"ETH"}

def bing_x_thread_function(bing_x):

    bing_x.add_coin("BTC")
    bing_x.add_coin("ETH")
    bing_x.start()

if __name__ == "__main__":
    bing_x = bingxstockmarket.BingXStockMarketImpl()
    bing_x_thread = threading.Thread(target=bing_x_thread_function, args=(bing_x,), name="MainApplication")
    bing_x_thread.daemon = True
    bing_x_thread.start()

    while True:
        if bing_x.ready():
            print("BTC: " + str(bing_x.get_coin_cost("BTC")))
            print("ETH: " + str(bing_x.get_coin_cost("ETH")))

        time.sleep(1)