import stockmarket
import bingxcoin
import threading
import coins_dict
import time
import requests
import hmac
import json
from datetime import timedelta, datetime
from hashlib import sha256

class BingXStockMarketImpl(stockmarket.StockMarket):
    def __init__(self, _api_key, _secret_key):
        super().__init__()
        self.socket_url = "wss://open-api-ws.bingx.com/market"
        self.api_url = "https://open-api.bingx.com"
        self.coin_list = {}
        self.thread_coin_list = {}
        self.is_ready = False
        self.api_key = _api_key
        self.secret_key = _secret_key
        self.timestapm = self._get_server_time()
        self.comission = 0.1

    def get_comission(self):
        return self.comission

    def add_coin(self, name):
        thread_coin = 0
        if name == coins_dict.get_btc_name():
            thread_coin = threading.Thread(target=self._create_btc_coin, args=(), name=coins_dict.get_btc_name())
        elif name == coins_dict.get_eth_name():
            thread_coin = threading.Thread(target=self._create_eth_coin, args=(), name=coins_dict.get_eth_name())
        self.thread_coin_list[name] = thread_coin
        thread_coin.start()

    def start(self):
        self.is_ready = True
        for coin_thread in self.thread_coin_list.values():
            coin_thread.join()

    def get_coin_cost(self, name):
        return self.coin_list[name].get_current_cost()

    def ready(self):
        return self.is_ready

    def buy(self, name, quantity):
        payload = {}
        path = '/openApi/spot/v1/trade/order'
        method = "POST"
        params_map = {
            "type": "MARKET",
            "symbol": name + "-USDT",
            "side": "BUY",
            "quantity": quantity,
            "newClientOrderId": "",
            "recvWindow": 1000,
            "timeInForce": "GTC",
            "timestamp": self.timestapm
        }
        params_str = self._parse_param(params_map)
        return self._send_request(method, path, params_str, payload)

    def sell(self, name, quantity):
        pass

    def _create_btc_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.socket_url, channel)
        self.coin_list[coins_dict.get_btc_name()] = new_coin
        new_coin.start()

    def _create_eth_coin(self):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": "ETH-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.socket_url, channel)
        self.coin_list[coins_dict.get_eth_name()] = new_coin
        new_coin.start()

    def _get_sign(self, api_secret, payload):
        signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature

    def _send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (self.api_url, path, urlpa, self._get_sign(self.secret_key, urlpa))
        headers = {
            'X-BX-APIKEY': self.api_key,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response.text

    def _parse_param(self, params_map):
        sorted_keys = sorted(params_map)
        params_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sorted_keys])
        if params_str != "":
            return params_str + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return params_str + "timestamp=" + str(int(time.time() * 1000))

    def _get_server_time(self):
        path = '/openApi/swap/v2/server/time'
        method = "GET"
        payload = {}
        data = self._send_request(method, path,"", payload)
        json_data = json.loads(data)
        server_time = json_data.get("data", {}).get("serverTime")
        if server_time:
            return server_time

    def get_address(self):
        path = '/openApi/wallets/v1/capital/deposit/address'
        method = "GET"
        payload = {}
        params_map = {
            "coin": "USDT",
            "limit": "1000",
            "offset": "0",
            "recvWindow": "0",
            "timestamp": self.timestapm
        }
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        print(data)

    def get_config(self):
        path = '/openApi/wallets/v1/capital/config/getall'
        method = "GET"
        payload = {}
        params_map = {
            "timestamp": self.timestapm
        }
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        print(data)

    def get_withdraw_record(self):

        payload = {}
        path = '/openApi/api/v3/capital/withdraw/history'
        method = "GET"
        params_map = {
            "coin": "BNB",
            "endTime": self.timestapm,
            "recvWindow": "60",
            "startTime": int((datetime.fromtimestamp(self.timestapm / 1000) - timedelta(days=1)).timestamp() * 1000),
            "timestamp": self.timestapm
        }
        params_str = self._parse_param(params_map)
        data =  self._send_request(method, path, params_str, payload)
        print(data)

    def withdraw(self):
        payload = {}
        path = '/openApi/wallets/v1/capital/withdraw/apply'
        method = "POST"
        params_map = {
            "address": "0x8****11",
            "addressTag": "None",
            "amount": "4998.0",
            "coin": "USDT",
            "network": "BEP20",
            "timestamp": self.timestapm,
            "walletType": "1"
        }
        params_str = self._parse_param(params_map)
        return self._send_request(method, path, params_str, payload)