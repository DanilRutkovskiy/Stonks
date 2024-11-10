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

def bing_x_thread_function(_bing_x):
    _bing_x.add_coin(coins_dict.get_btc_name())
    # _bing_x.add_coin(coins_dict.get_eth_name())
    _bing_x.start()#Эта функция блокирует дальнейшее выполнение потока, поэтому каждая биржа должна быть создана в отдельном

def bybit_thread_function(_bybit):
    _bybit.add_coin({'BTC': 'BTCUSDT'}, _all=False)
    _bybit.start()

if __name__ == "__main__":
    #BING_X
    bing_x_api_key = "kwdUd7o2o6Ka1DjjA1sbX4CDLZvtvXbVyIWQaY2QwnKvF7YLCm5LuQp2ej4vz8ZXFasmuavxjkemVmRy1Rw"
    bing_x_secret_key = "z0SB45M2fud5Tkx8u55dsJDzVjHEEqVp4qJKAAHjYGg0nWLPpq1sqXuKtN1EAQogVmtYMhZkDSqNSAvKw"
    bing_x = bingxstockmarket.BingXStockMarketImpl(bing_x_api_key, bing_x_secret_key)
    # bing_x_thread = threading.Thread(target=bing_x_thread_function, args=(bing_x,), name="BING X Thread")
    # bing_x_thread.daemon = True
    # bing_x_thread.start()
    #BY_BIT
    # bybit_thread = threading.Thread(target=bybit_thread_function, args=(bybit,), name="Bybit X Thread")
    # bybit_thread.daemon = True
    # bybit_thread.start()
    bybit_api_key = "Xir3foco4eJ3LjctHz"
    bybit_secret_key = "2LqxhKE6RoYzwb4rIUOOcVeURRIQ5FWIGTDd"
    bybit = bybitstockmarket.ByBitStockMarketImpl(bybit_api_key, bybit_secret_key)
    bybit.create_session()
    bybit.get_coin_list()

    #Пока в качестве основной функции программы будем использовать этот цикл while
    db = database.StockMarketDb()
    db.init_local_db(True)
    #while True:
        #if bing_x.ready() and bybit.ready():
    data = bing_x.get_config()
    json_data = json.loads(data)
    for obj in json_data["data"]:
        db.import_coin(bing_x.convert_coin_to_db_import(obj), bing_x.get_name())
    for coin in bybit.coin_full_list['name'].unique():
         db.import_coin({coin: bybit.get_coin_networks(coin)}, bybit.get_name())



            #BTC
            # bing_x_btc_cost = bing_x.get_coin_cost(coins_dict.get_btc_name())
            # bing_x_btc_comission = bing_x_btc_cost * bing_x.get_comission()
            # bybit_btc_cost = bybit.get_coin_cost(coins_dict.get_btc_name())
            # bybit_btc_comission = bybit_btc_cost * bybit.get_comission()
            # diff = bing_x_btc_cost - bybit_btc_cost
            # if abs(diff) > abs(bing_x_btc_comission + bybit_btc_comission):
            #     if diff > 0: #Значит на bing_x цена выше, покупаем на bybit
            #         if bybit.buy(coins_dict.get_btc_name(), 10000):
            #             #Здесь идет логика перевода монет
            #             pass
            #         if bing_x.sell(coins_dict.get_btc_name(), 10000):
            #             #Здесь идет логика об удачном завершении сделки и фиксация результата в БД
            #             pass
            #     else:
            #         if bing_x.buy(coins_dict.get_btc_name(), 10000):
            #             # Здесь идет логика перевода монет
            #             pass
            #         if bybit.sell(coins_dict.get_btc_name(), 10000):
            #             # Здесь идет логика об удачном завершении сделки и фиксация результата в БД
            #             pass
            #print("BINGX:" + coins_dict.get_btc_name() + ": " + str(bing_x.get_coin_cost(coins_dict.get_btc_name())))
            #print("Bybit:" + coins_dict.get_btc_name() + ": " + str(bybit.get_coin_cost(coins_dict.get_btc_name())))
        #time.sleep(1)
