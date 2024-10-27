import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time
import coins_dict

def bing_x_thread_function(_bing_x):
    _bing_x.add_coin(coins_dict.get_btc_name())
    _bing_x.add_coin(coins_dict.get_eth_name())
    _bing_x.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

if __name__ == "__main__":
#Создаем первую биржу.
    bing_x = bingxstockmarket.BingXStockMarketImpl()
    bing_x_thread = threading.Thread(target=bing_x_thread_function, args=(bing_x,), name="BING X Thread")
    bing_x_thread.daemon = True
    bing_x_thread.start()
#Здесь можно будет создать вторую и т.д.

#Пока в качестве основной функции программы будем использовать этот цикл while
    while True:
        if bing_x.ready():
            print("BINGX:" + coins_dict.get_btc_name() + ": " + str(bing_x.get_coin_cost(coins_dict.get_btc_name())))
            print("BINGX:" + coins_dict.get_eth_name() + ": " + str(bing_x.get_coin_cost(coins_dict.get_eth_name())))

        time.sleep(1)