import threading
from time import sleep

from Stonks import bybitstockmarket, bingxstockmarket


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

    def track_coin(self, stocks, coin):

        self.thread_pool['BTC'] = []

        for stock in stocks:

            def target_func(stock):
                stock.add_coin({'BTC': 'BTCUSDT'}, _all=False)
                stock.start()

            stock_thread = threading.Thread(target=target_func, args=(stock,), name=stock.name + " Thread")
            stock_thread.daemon = True
            stock_thread.start()
            self.thread_pool['BTC'].append({stock.name: stock, 'thread': stock_thread})

            sleep(1)

        while True:
            max_price = max([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
            min_price = min([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
            if max_price * 0.1 + min_price * 0.1 < max_price - min_price:
                print(max_price, min_price)
                print('SIGNAL')
            else:
                print(max_price, min_price)
                print(max_price / 100 * 0.1 + min_price / 100 * 0.1 - (max_price - min_price))

            sleep(1)

    def show_spot_dif(self):

        # for thread in self.thread_pool['BTC']:
        #     thread['thread'].daemon = True
        #     thread['thread'].start()

        while True:
            max_price = max([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
            min_price = min([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
            if max_price * 0.1 + min_price * 0.1 < max_price - min_price:
                print(max_price, min_price)
                print('SIGNAL')
            else:
                print(max_price, min_price)
                print(max_price * 0.1 + min_price * 0.1 - (max_price - min_price))

    def create_thread(self, stock, target, name):
        threading.Thread(target=target, args=(stock,), name=name)


