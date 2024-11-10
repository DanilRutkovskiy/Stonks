import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time
import pandas as pd
import coins_dict
import bybitstockmarket

def bing_x_thread_function(_bing_x):
    _bing_x.add_coin(coins_dict.get_btc_name())
    # _bing_x.add_coin(coins_dict.get_eth_name())
    _bing_x.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

def bybit_thread_function(_bybit):
    _bybit.add_coin({'BTC': 'BTCUSDT'}, _all=False)
    _bybit.start()

if __name__ == "__main__":

    #BY_BIT
    bybit_api_key = "Xir3foco4eJ3LjctHz"
    bybit_secret_key = "2LqxhKE6RoYzwb4rIUOOcVeURRIQ5FWIGTDd"
    bybit = bybitstockmarket.ByBitStockMarketImpl(bybit_api_key, bybit_secret_key)
    bybit.create_session()
    bybit.get_coin_list()

    for coin in bybit.coin_full_list['name'].unique():
        test = bybit.get_coin_networks(coin)
        print(test)

