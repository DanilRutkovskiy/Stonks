import stockmarket
import bybitcoin
import threading
import coins_dict

class ByBitStockMarketImpl(stockmarket.StockMarket):
    def __init__(self):
        super().__init__()
        self.coin_list = {}
        self.thread_coin_list = {}
        self.is_ready = False

    def _create_coin(self, coin_name, coin_index):
        new_coin = bybitcoin.ByBitCoinImpl(coin_index)
        self.coin_list[coin_name] = new_coin
        new_coin.start()

    def add_coin(self, name_list={}, _all=True):

        if _all == True:
            for v, k in self.coin_list.items():
                thread_coin = threading.Thread(target=self._create_coin, args=(v, k,), name=k)
                self.thread_coin_list[k] = thread_coin
                thread_coin.start()
        else:
            for v, k in name_list.items():
                thread_coin = threading.Thread(target=self._create_coin, args=(v, k,), name=k)
                self.thread_coin_list[k] = thread_coin
                thread_coin.start()

    def start(self):
        self.is_ready = True
        for coin_thread in self.thread_coin_list.values():
            coin_thread.join()

    def get_coin_cost(self, name):
        return self.coin_list[name].get_current_cost()

    def ready(self):
        return self.is_ready
