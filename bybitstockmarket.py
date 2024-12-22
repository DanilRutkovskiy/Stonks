import hashlib
import hmac
import json
import uuid

from pybit.unified_trading import HTTP

import stockmarket
import bybitcoin
import threading
import requests
import pandas as pd
import time


class ByBitStockMarketImpl(stockmarket.StockMarket):
    def __init__(self, api_key, api_secret_key):
        super().__init__()
        self.name = 'ByBit'
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.coin_list = []
        self.thread_coin_list = {}
        self.session = None
        self.is_ready = False
        # URL для публичного API Bybit по торговым парам на споте
        self.coin_list_url = "https://api.bybit.com/v5/market/instruments-info"
        self.coin_full_list = []
        self.coin_map = {}

    def _create_coin(self, coin_name):
        new_coin = bybitcoin.ByBitCoinImpl(coin_name)
        new_coin.get_min_network()
        self.coin_map[coin_name] = new_coin
        new_coin.start()

    def add_coin(self, coin_list):

        self.coin_list = coin_list

        for k in coin_list:
            thread_coin = threading.Thread(target=self._create_coin, args=(k,), name=k)
            self.thread_coin_list[k] = thread_coin
            thread_coin.start()


    def start(self):
        self.is_ready = True
        for coin_thread in self.thread_coin_list.values():
            coin_thread.join()

    def get_coin_list(self):
        params = {
            "category": "spot"  # Для спотового рынка
        }
        try:
            response = requests.get(self.coin_list_url, params=params)
            response.raise_for_status()  # Проверить успешность запроса
            data = response.json()

            if data['retCode'] == 0:  # Успешный ответ
                self.coin_full_list = pd.DataFrame([{'alias': info['baseCoin'], 'name': info['symbol']} for info in data['result']['list']])

            else:
                print("Error:", data['retMsg'])

        except requests.RequestException as e:
            print(f"Request failed: {e}")

    def get_coin_networks(self, coin):
        data = self.session.get_coin_info(coin=coin)
        if len(data['result']['rows']) > 0:
            network_list = [{'chain': info['chain'], 'withdrawFee': info['withdrawFee'],
                    'depositMin': info['depositMin'], 'withdrawMin': info['withdrawMin']} for info in data['result']['rows'][0]['chains']]
            return network_list

    def get_name(self):
        return "BYBIT"

    def get_server_timestamp(self):
        return self.session.get_server_time()['time']

    def create_session(self):
        if self.session is None:
            self.session = HTTP(testnet=False,api_key=self.api_key,api_secret=self.api_secret_key)

    def get_coin_cost(self, name):
        return self.coin_map[name].get_current_cost()

    def get_commission(self, name):
        return self.coin_map[name].get_commission()

    def get_coin_network(self, name):
        return self.coin_map[name].get_coin_network()

    def withdraw(self, address, amount, coin, chain):
        self.create_session()
        self.transfer_from_unif_to_fund(coin, amount)
        self.session.withdraw(
            coin=coin,
            chain=chain,
            address=address,
            amount=amount,
            timestamp=self.session.get_server_time()['time'],
            forceChain=0,
            accountType="SPOT",
        )

    def ready(self):
        return self.is_ready
    
    def import_stock_data_to_db(self, db):
        self.create_session()
        self.get_coin_list()
        for coin in self.coin_full_list['alias']:
            coin_data = self.get_coin_networks(coin)
            if coin_data != None:
                db.import_coin({coin: coin_data}, self.get_name())

    def place_order(self, price, qty, symbol, side):

        self.create_session()
        response = self.session.place_order(
            category='spot',
            symbol=symbol,#BTSUSDT
            side=side,
            orderType='Limit',
            qty=round(qty, 2),
            price=round(price, 2),
            timeInForce="PostOnly",
            isLeverage=0,
            orderFilter="Order"
        )

        print(f'{side}-сделка по монете {symbol} выполнена')

        return response['result']['orderId']

    def check_order(self, order_id):
        self.create_session()
        response = self.session.get_order_history(
            category="spot",
            order_id=order_id
        )

        return response['result']['list'][0]['orderStatus'] == 'Filled'

    def get_order_list(self):
        self.create_session()
        response = self.session.get_open_orders(
            category="spot",
            symbol='ETHUSDT'
        )
        return response

    def get_acc_balance(self):
        self.create_session()
        response = self.session.get_coins_balance(
            accountType="UNIFIED",
            coin="USDT",
        )

        return response['result']['balance'][0]['walletBalance']


    def get_deposit_addres(self, coin, chain):
        self.create_session()
        response = self.session.get_master_deposit_address(
            coin=coin,
            chainType=chain,
        )

        return response['result']['chains'][0]['addressDeposit']

    def cancel_order(self, symbol, order_id):
        self.create_session()
        response = self.session.cancel_order(
            category="spot",
            symbol=symbol,
            orderId=order_id,
        )

        return response

    def transfer_from_unif_to_fund(self, coin, amount):
        self.create_session()
        response = self.session.create_internal_transfer(
            transferId=str(uuid.uuid4()),
            coin=coin,
            amount=amount,
            fromAccountType="UNIFIED",
            toAccountType="FUND",
        )

        return response