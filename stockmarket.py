from abc import ABC, abstractmethod

class StockMarket(ABC):
    def __init__(self):
        self.name: str = ""
        self.coin_map: dict = {}
        pass
    @abstractmethod
    def add_coin(self, name: str):
        pass

    @abstractmethod
    def get_coin_cost(self, name: str):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def buy(self, name: str, quantity):
        pass

    @abstractmethod
    def sell(self, name: str, quantity):
        pass

    @abstractmethod
    def get_address(self):
        pass

    @abstractmethod
    def get_config(self):
        pass

    @abstractmethod
    def withdraw(self, adress: str, amount: float, coin: str, network: str):
        pass

    @abstractmethod
    def get_withdraw_record(self):
        pass

    @abstractmethod
    def get_comission(self):
        pass

    @abstractmethod
    def convert_coin_to_db_import(self, data):
        pass

    @abstractmethod
    def get_coin_list(self):
        pass

    @abstractmethod
    def get_coin_networks(self, coin: str):
        pass

    @abstractmethod
    def get_server_timestamp(self):
        pass

    @abstractmethod
    def get_coin_network(self, name: str):
        pass

    @abstractmethod
    def place_order(self, price: float, qty: float, symbol: str, side: str):
        pass

    @abstractmethod
    def check_order(self, symbol: str, order_id: int):
        pass

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: int):
        pass

    @abstractmethod
    def get_deposit_address(self, coin: str, network: str):
        pass

    @abstractmethod
    def get_coin_balance(self, coin: str):
        pass

#Проверяет, готова ли биржа к работе - прошла ли инициализация.
    def ready(self):
        return False