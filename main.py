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

    db = database.StockMarketDb()
    db.init_local_db()

    # coin_list = db.get_common_coin_list()
    app = Application()
    app.init_bingx()
    app.init_bybit()

    # # app.bingx_ex.coin_list = coin_list[:100]
    # # app.bybit_ex.coin_list = coin_list[:100]
    # #
    # app.track_coin(['ZRX'])
    # app.show_spot_dif()


    # bing_x_api_key = "kwdUd7o2o6Ka1DjjA1sbX4CDLZvtvXbVyIWQaY2QwnKvF7YLCm5LuQp2ej4vz8ZXFasmuavxjkemVmRy1Rw"
    # bing_x_secret_key = "z0SB45M2fud5Tkx8u55dsJDzVjHEEqVp4qJKAAHjYGg0nWLPpq1sqXuKtN1EAQogVmtYMhZkDSqNSAvKw"
    # bing_x = bingxstockmarket.BingXStockMarketImpl(bing_x_api_key, bing_x_secret_key)
    # bing_x_thread = threading.Thread(target=bing_x_thread_function, args=(bing_x,), name="BING X Thread")
    # bing_x_thread.daemon = True
    # bing_x_thread.start()
    #
    # bybit_api_key = "Xir3foco4eJ3LjctHz"
    # bybit_secret_key = "2LqxhKE6RoYzwb4rIUOOcVeURRIQ5FWIGTDd"
    # bybit = bybitstockmarket.ByBitStockMarketImpl(bybit_api_key, bybit_secret_key)
    # bybit_thread = threading.Thread(target=bybit_thread_function, args=(bybit,), name="Bybit X Thread")
    # bybit_thread.daemon = True
    # bybit_thread.start()
    #
    # while True:
    #     print(bybit.get_coin_cost('BTC'))

    # bybit.create_session()
    # bybit.get_coin_list()

