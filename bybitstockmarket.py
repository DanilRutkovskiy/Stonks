from pybit.unified_trading import HTTP

import stockmarket
import bybitcoin
import threading
import requests
import pandas as pd

class ByBitStockMarketImpl(stockmarket.StockMarket):
    def __init__(self, api_key, api_secret_key):
        super().__init__(api_key, api_secret_key)
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.coin_list = {}
        self.thread_coin_list = {}
        self.session = None
        self.is_ready = False
        # URL для публичного API Bybit по торговым парам на споте
        self.coin_list_url = "https://api.bybit.com/spot/v3/public/symbols"
        self.coin_full_list = []

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

    def get_coin_list(self):
        resp_json = requests.get(self.coin_list_url).json()
        self.coin_full_list = pd.DataFrame([{'alias': info['alias'], 'name': info['baseCoin']} for info in resp_json['result']['list']])

    def get_coin_networks(self, coin):
        data = self.session.get_coin_info(coin=coin)
        if len(data['result']['rows']) > 0:
            network_list = [{'chain': info['chain'], 'withdrawFee': info['withdrawFee'],
                    'depositMin': info['depositMin'], 'withdrawMin': info['withdrawMin']} for info in data['result']['rows'][0]['chains']]
            return network_list

    def get_server_timestamp(self):
        return self.session.get_server_time()['time']

    def create_session(self):
        self.session = HTTP(testnet=False,api_key=self.api_key,api_secret=self.api_secret_key)

    def get_coin_cost(self, name):
        return self.coin_list[name].get_current_cost()

    def withdraw(self, address, amount, coin, chain):
        self.session.withdraw(
            coin=coin,
            chain=chain,
            address=address,
            amount=amount,
            timestamp=self.session.get_server_time()['time'],
            forceChain=0,
            accountType="FUND",
        )


    def ready(self):
        return self.is_ready
