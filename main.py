import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time

coins = {1:"BTC", 2:"ETH"}

def main_thread_function(stock):
    while True:
        print("BTC: " + str(stock.get_coin_cost("BTC")))
        print("ETH: " + str(stock.get_coin_cost("ETH")))
        time.sleep(1)

if __name__ == "__main__":
    bingX = bingxstockmarket.BingXStockMarketImpl()
    bingX.add_coin("BTC")
    bingX.add_coin("ETH")

    main_thread = threading.Thread(target=main_thread_function, args=(bingX,), name="MainApplication")
    main_thread.daemon = True
    main_thread.start()
    bingX.start()