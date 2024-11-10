class StockMarket(object):
    def __init__(self, api_key, api_secret_key):
        pass

    def add_coin(self, name):
        pass

    def get_coin_cost(self, name):
        pass

    def start(self):
        pass

    def buy(self, name, quantity):
        pass

    def sell(self, name, quantity):
        pass

    def get_address(self):
        pass

    def get_config(self):
        pass

    def withdraw(self, adress, amount, coin, chain):
        pass

    def get_withdraw_record(self):
        pass

    def get_comission(self):
        pass

    def get_coin_list(self):
        pass

    def get_coin_networks(self, coin):
        pass

    def get_server_timestamp(self):
        pass

#Проверяет, готова ли биржа к работе - прошла ли инициализация.
    def ready(self):
        return False