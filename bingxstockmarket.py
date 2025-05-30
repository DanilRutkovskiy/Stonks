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
        self.name = 'BINGX'
        self.socket_url = "wss://open-api-ws.bingx.com/market"
        self.api_url = "https://open-api.bingx.com"
        self.coin_list: list = []
        self.thread_coin_list = {}
        self.is_ready = False
        self.api_key = _api_key
        self.secret_key = _secret_key
        self.commission = 0.1
        self.coin_map: dict = {}

    def _convert_coin_to_db_import(self, data):
        coin_name = data["coin"]
        network_list = data["networkList"]
        network_list_new = []
        for network in network_list:
            network_list_new.append({"chain": network["network"],
                                     "withdrawFee": network["withdrawFee"],
                                     "depositMin": network["depositMin"],
                                     "withdrawMin": network["withdrawMin"]})

        return {coin_name: network_list_new}

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

    def get_coin_cost(self, name):
        return self.coin_map[name].get_current_cost()

    def get_commission(self, name):
        return self.coin_map[name].get_commission()

    def get_coin_network(self, name):
        return self.coin_map[name].get_coin_network()

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
            "timestamp": self.get_server_timestamp()
        }
        params_str = self._parse_param(params_map)
        return self._send_request(method, path, params_str, payload)

    def sell(self, name, quantity):
        pass

    def _create_coin(self, coin):
        channel = {"id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", "reqType": "sub", "dataType": f"{coin}-USDT@lastPrice"}
        new_coin = bingxcoin.BingXCoinImpl(self.socket_url, channel, coin)
        self.coin_map[coin] = new_coin
        new_coin.get_min_network()
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

    def get_server_timestamp(self):
        path = '/openApi/swap/v2/server/time'
        method = "GET"
        payload = {}
        data = self._send_request(method, path,"", payload)
        json_data = json.loads(data)
        server_time = json_data.get("data", {}).get("serverTime")
        if server_time:
            return server_time

    def _get_config(self):
        path = '/openApi/wallets/v1/capital/config/getall'
        method = "GET"
        payload = {}
        params_map = {
            "timestamp": self.get_server_timestamp()
        }
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        return data

    def withdraw(self, address: str, amount: float, coin_name: str, network_name: str):
        payload = {}
        path = '/openApi/wallets/v1/capital/withdraw/apply'
        method = "POST"
        params_map = {
            "address": address,
            "amount": str(amount),
            "coin": coin_name,
            "network": network_name,
            "timestamp": self.get_server_timestamp(),
            "walletType": "1"
        }
        #TODO Возможные ошибки - не удалось выполнить запрос к бирже(приходит JSON без data)
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        json_data = json.loads(data)
        id = json_data.get("data", {}).get("id")
        return id

    def place_order(self, price: float, qty: float, symbol: str, side: str):
        payload = {}
        path = "/openApi/spot/v1/trade/order"
        method = "POST"
        params_map = {
            "type": "LIMIT",
            "symbol": symbol,#format BTC-USDT
            "side": side,
            "quantity": round(float(qty), 2),
            "newClientOrderId": "",
            "price": round(float(price), 4),
            "recvWindow": 1000,
            "timeInForce": "GTC",
            "timestamp": self.get_server_timestamp()
        }
        #TODO Возможные ошибки - не удалось выполнить запрос к бирже(приходит JSON без data)
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        json_data = json.loads(data)
        order_id = json_data.get("data", {}).get("orderId")
        return order_id

    def cancel_order(self, symbol: str, order_id: int):
        payload = {}
        path = '/openApi/spot/v1/trade/cancel'
        method = "POST"
        params_map = {
            "orderId": str(order_id),
            "symbol": symbol,
            "timestamp": self.get_server_timestamp()
        }
        params_str = self._parse_param(params_map)
        try:
            data = self._send_request(method, path, params_str, payload)
            json_data = json.loads(data)
            status = json_data.get("data", {}).get("status")
            return status == "CANCELED"
        except:
            return True

    def get_coin_balance(self, coin: str):
        payload = {}
        path = '/openApi/spot/v1/account/balance'
        method = "GET"
        params_map = {
            "recvWindow": "60000",
            "timestamp": self.get_server_timestamp()
        }
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        json_data = json.loads(data)
        for obj in json_data['data']['balances']:
            if obj.get('asset') == coin:
                return obj.get('free')

        return -1

    def get_deposit_address(self, coin: str, network: str):
        payload = {}
        path = '/openApi/wallets/v1/capital/deposit/address'
        method = "GET"
        params_map = {
            "coin": coin,
            "limit": "1000",
            "offset": "0",
            "recvWindow": "0",
            "timestamp": self.get_server_timestamp()
        }
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        json_data = json.loads(data)
        for obj in json_data['data']['data']:
            if obj.get('network') == network:
                return obj.get('address')

        return -1

    def check_order(self, symbol: str, order_id: int):
        payload = {}
        path = '/openApi/spot/v1/trade/query'
        method = "GET"
        params_map = {
            "symbol": symbol,
            "orderId": str(order_id),
            "timestamp": self.get_server_timestamp()
        }
        #TODO Возможные ошибки - не удалось выполнить запрос к бирже(приходит JSON без data)
        params_str = self._parse_param(params_map)
        data = self._send_request(method, path, params_str, payload)
        json_data = json.loads(data)
        status = json_data.get("data", {}).get("status")
        return status == "FILLED"

    def import_stock_data_to_db(self, db):
        data = self._get_config()
        #TODO Проверить, что data пришла корректная
        json_data = json.loads(data)
        for obj in json_data["data"]:
            db.import_coin(self._convert_coin_to_db_import(obj), self.name)

    def get_order_list(self):
        payload = {}
        path = '/openApi/spot/v1/trade/openOrders'
        method = "GET"
        paramsMap = {
            "symbol": "ETH-USDT",
            "timestamp": self.get_server_timestamp()
        }
        paramsStr = self._parse_param(paramsMap)
        return json.loads(self._send_request(method, path, paramsStr, payload))


    def get_acc_balance(self):
        payload = {}
        path = '/openApi/account/v1/allAccountBalance'
        method = "GET"
        paramsMap = {
            "accountType": "sopt",
            "recvWindow": "6000",
            "timestamp": self.get_server_timestamp()
        }
        paramsStr = self._parse_param(paramsMap)
        data = self._send_request(method, path, paramsStr, payload)
        json_data = json.loads(data)
        return json_data['data'][0]['usdtBalance']
