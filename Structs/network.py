class network(object):
    def __init__(self, withdraw_fee, deposit_min, withdraw_min, name):
        self.withdraw_fee = withdraw_fee
        self.deposit_min = deposit_min
        self.withdraw_min = withdraw_min
        self.name = name