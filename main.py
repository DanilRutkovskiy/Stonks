from psycopg2 import OperationalError
import json
import bingxstockmarket
import coin
import threading
import bingxcoin
import stockmarket
import time
import coins_dict
import bybitstockmarket
import database
from app import Application


def bing_x_thread_function(_bing_x):
    _bing_x.add_coin(coins_dict.get_btc_name())
    # _bing_x.add_coin(coins_dict.get_eth_name())
    _bing_x.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

def bybit_thread_function(_bybit):
    _bybit.add_coin({'BTC': 'BTCUSDT'}, _all=False)
    _bybit.start()


if __name__ == "__main__":

    # coin_list = db.get_common_coin_list()
    app = Application()
    app.init_bingx()
    app.init_bybit()

    app.bybit_ex.place_order(0.5925, 2, 'ZRXUSDT', 'Buy')


