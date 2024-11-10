class StockMarket(object):
    def __init__(self):
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

    def withdraw(self):
        pass

    def get_withdraw_record(self):
        pass

    def get_comission(self):
        pass

    def convert_coin_to_db_import(self, data):
        pass

    def get_name(self):
        pass


#Проверяет, готова ли биржа к работе - прошла ли инициализация.
    def ready(self):
        return False