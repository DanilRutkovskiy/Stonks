import threading
from time import sleep

import bybitstockmarket, bingxstockmarket


class Application:

    def __init__(self):
        self.bing_x_api_key = "kwdUd7o2o6Ka1DjjA1sbX4CDLZvtvXbVyIWQaY2QwnKvF7YLCm5LuQp2ej4vz8ZXFasmuavxjkemVmRy1Rw"
        self.bing_x_secret_key = "z0SB45M2fud5Tkx8u55dsJDzVjHEEqVp4qJKAAHjYGg0nWLPpq1sqXuKtN1EAQogVmtYMhZkDSqNSAvKw"
        self.bybit_api_key = "Xir3foco4eJ3LjctHz"
        self.bybit_secret_key = "2LqxhKE6RoYzwb4rIUOOcVeURRIQ5FWIGTDd"

        self.bybit_ex = []
        self.bingx_ex = []
        self.stock_ex_pool = []
        self.thread_pool = {}

    def init_bybit(self):
        # self.bybit_ex.append(bybitstockmarket.ByBitStockMarketImpl(self.bybit_api_key, self.bybit_secret_key))
        self.bybit_ex = bybitstockmarket.ByBitStockMarketImpl(self.bybit_api_key, self.bybit_secret_key)
        self.stock_ex_pool.append(self.bybit_ex)

    def init_bingx(self):
        # self.bingx_ex.append(bingxstockmarket.BingXStockMarketImpl(self.bing_x_api_key, self.bing_x_secret_key))
        self.bingx_ex = bingxstockmarket.BingXStockMarketImpl(self.bing_x_api_key, self.bing_x_secret_key)
        self.stock_ex_pool.append(self.bingx_ex)

    def track_coin(self, coin):

        for stock in self.stock_ex_pool:
            def target_func(stock):
                stock.add_coin(coin)
                stock.start()

            stock_thread = threading.Thread(target=target_func, args=(stock,), name=stock.name + " Thread")
            stock_thread.daemon = True
            stock_thread.start()

            sleep(1)

        # while True:
        #     max_price = max([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
        #     min_price = min([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
        #     if max_price * 0.1 + min_price * 0.1 < max_price - min_price:
        #         print(max_price, min_price)
        #         print('SIGNAL')
        #     else:
        #         print(max_price, min_price)
        #         print(max_price / 100 * 0.1 + min_price / 100 * 0.1 - (max_price - min_price))
        #
        #     sleep(1)

    def show_spot_dif(self):
        def get_min_stock(coin):
            min_price = 100000000
            to_ret = None
            for st in self.stock_ex_pool:
                if min_price > st.get_coin_cost(coin):
                    min_price = st.get_coin_cost(coin)
                    to_ret = st
            return to_ret

        def get_max_stock(coin):
            max_price = -1
            to_ret = None
            for st in self.stock_ex_pool:
                if max_price < st.get_coin_cost(coin):
                    max_price = st.get_coin_cost(coin)
                    to_ret = st
            return to_ret

        while True:

            for coin in self.stock_ex_pool[0].coin_list:
                min_stock = get_min_stock(coin)
                max_stock = get_max_stock(coin)
                max_price = max_stock.get_coin_cost(coin)
                min_price = min_stock.get_coin_cost(coin)
                max_name = max_stock.name
                min_name = min_stock.name
                if max_price / 100 * 0.1 + min_price / 100 * 0.1 < max_price - min_price:
                    print(max_name,':', max_price, ' | ', min_name, ':', min_price)
                    print(coin, ": ", max_price, min_price)
                    print('SIGNAL')
                else:
                    print(coin, ": ", max_price, min_price)
                    print(max_price / 100 * 0.1 + min_price / 100 * 0.1 - (max_price - min_price))

            sleep(1)

    def create_thread(self, stock, target, name):
        threading.Thread(target=target, args=(stock,), name=name)


