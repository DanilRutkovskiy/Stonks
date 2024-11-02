import bingxstockmarket
import bybitstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time
import coins_dict

def bybit_thread_function(bybit):
    bybit.add_coin({'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT'}, _all=False)
    bybit.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

def bing_x_thread_function(_bing_x):
    _bing_x.add_coin(coins_dict.get_btc_name())
    _bing_x.add_coin(coins_dict.get_eth_name())
    _bing_x.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

if __name__ == "__main__":
#Создаем первую биржу.
    bybit = bybitstockmarket.ByBitStockMarketImpl()
    bybit_thread = threading.Thread(target=bybit_thread_function, args=(bybit,), name="BING X Thread")
    bybit_thread.daemon = True
    bybit_thread.start()
#Здесь можно будет создать вторую и т.д.

#Пока в качестве основной функции программы будем использовать этот цикл while
    while True:
        if bybit.ready():
            print("ByBit:" + coins_dict.get_btc_name() + ": " + str(bybit.get_coin_cost(coins_dict.get_btc_name())))
            print("ByBit:" + coins_dict.get_eth_name() + ": " + str(bybit.get_coin_cost(coins_dict.get_eth_name())))

        time.sleep(1)