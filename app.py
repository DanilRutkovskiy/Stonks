import threading
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from stockmarket import StockMarket
import time

import bybitstockmarket, bingxstockmarket
import database
from general_settings import BINGX_API_KEY, BINGX_API_SECRET, BYBIT_API_KEY, BYBIT_API_SECRET

TRADE_COMMISSION = 0.001
MAX_WAIT_TIME = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('logger')

class Application:

    def __init__(self):
        self.bing_x_api_key: str = BINGX_API_KEY
        self.bing_x_secret_key: str = BINGX_API_SECRET
        self.bybit_api_key: str = BYBIT_API_KEY
        self.bybit_secret_key: str = BYBIT_API_SECRET

        self.bybit_ex: Optional[bybitstockmarket.ByBitStockMarketImpl] = None
        self.bingx_ex: Optional[bingxstockmarket.BingXStockMarketImpl] = None
        self.stock_ex_pool: list = []
        self.thread_pool: dict = {}

    def init_bybit(self):
        self.bybit_ex = bybitstockmarket.ByBitStockMarketImpl(self.bybit_api_key, self.bybit_secret_key)
        self.stock_ex_pool.append(self.bybit_ex)

    def init_bingx(self):
        self.bingx_ex = bingxstockmarket.BingXStockMarketImpl(self.bing_x_api_key, self.bing_x_secret_key)
        self.stock_ex_pool.append(self.bingx_ex)

    def track_coin(self, coin: str):
        for stock in self.stock_ex_pool:
            stock_thread = threading.Thread(target=self._start_stock_tracking, args=(stock, coin,), name=stock.name + " Thread", daemon=True)
            stock_thread.start()

            #sleep(1) - пока убрал, хз зачем делали. Может надо будет вернуть
        time.sleep(10)
        self.show_spot_dif()

    @staticmethod
    def _start_stock_tracking(stock: StockMarket, coin: str):
        stock.add_coin(coin)
        stock.start()
        logger.info(f"Started tracking {coin} on {stock.name}")

        # while True:
        #     max_price = max([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
        #     min_price = min([stock.get_coin_cost('BTC') for stock in self.stock_ex_pool])
        #     if max_price * 0.1 + min_price * 0.1 < max_price - min_price:
        #         print(max_price, min_price)
        #         print('SIGNAL')
        #     else:
        #         print(max_price, min_price)
        #         print(max_price / 100 * 0.1 + min_price / 100 * 0.1 - (max_price - min_price))
        #
        #     sleep(1)

    def show_spot_dif(self):
        while True:
            for coin in self.stock_ex_pool[0].coin_list:
                min_stock: StockMarket = self._get_extreme_stock(coin, "min")
                max_stock: StockMarket = self._get_extreme_stock(coin, "max")
                if min_stock.get_coin_cost(coin) != 0 and max_stock.get_coin_cost(coin) != 0:
                    self.generate_arbtr_stats(min_stock, max_stock, coin)
            time.sleep(1)

    def _get_extreme_stock(self, coin: str, extreme: str):
        extreme_price = float("inf") if extreme == "min" else float("-inf")
        result_stock = None

        for stock in self.stock_ex_pool:
            coin_cost = stock.get_coin_cost(coin)
            if (extreme == "min" and coin_cost < extreme_price) or (extreme == "max" and coin_cost > extreme_price):
                extreme_price = coin_cost
                result_stock = stock

        return result_stock


    def generate_arbtr_stats(self, min_stock: StockMarket, max_stock: StockMarket, coin: str):
        max_price = max_stock.get_coin_cost(coin)
        min_price = min_stock.get_coin_cost(coin)
        min_coin_network = min_stock.get_coin_network(coin)

        sell_buy_prc: float = abs(1 - max_price / min_price) * 100
        sell_buy: float = max_price - min_price
        trade_cost: float = 5
        trade_profit: float = 0
        if sell_buy != 0:
            sbp_fee_corr: float = min_price * float(min_coin_network.withdraw_fee)
            close_fee: float = sbp_fee_corr / sell_buy

            msg = f"""
                    Покупаем с: {min_stock.name}, Цена: {min_price}, Продаем на {max_stock.name}, Цена: {max_price}
                    Абсолютная разница: {sell_buy}, Процентная разница: {sell_buy_prc}, 
                    Кол-во монет для перекрытия Network Fee и комиссию за покупку/продажу: {close_fee}
                    Входная стоимость (Цена монет для перекрытия Network Fee и комиссию за покупку/продажу): {close_fee * min_price}
                    Test Case 1 - 100 USDT
                    Абсолютная разница: {sell_buy * int(100 / min_price)}, Затраты на комиссию при покупке/продаже: {100 * 2 * TRADE_COMMISSION},
                    Итоговая прибыль: {sell_buy * int(100 / min_price) - 100 * 2 * TRADE_COMMISSION - sbp_fee_corr}
                    Test Case 2 - 500 USDT
                    Абсолютная разница: {sell_buy * int(500 / min_price)}, Затраты на комиссию при покупке/продаже: {500 * 2 * TRADE_COMMISSION},
                    Итоговая прибыль: {sell_buy * int(500 / min_price) - 500 * 2 * TRADE_COMMISSION - sbp_fee_corr}
                    Test Case 3 - 1000 USDT
                    Абсолютная разница: {sell_buy * int(1000 / min_price)}, Затраты на комиссию при покупке/продаже: {1000 * 2 * TRADE_COMMISSION},
                    Итоговая прибыль: {sell_buy * int(1000 / min_price) - 1000 * 2 * TRADE_COMMISSION - sbp_fee_corr}
                    """

            logger.info(msg)

            if sell_buy * int(trade_cost / min_price) - trade_cost * 2 * TRADE_COMMISSION - sbp_fee_corr > trade_profit:
                logger.info('МОЖНО БРАТЬ')
                self.make_deal(min_stock, max_stock, trade_cost / min_price, min_price, max_price, coin)

    #TODO реализовать функции place_order, check_order, withdraw
    def make_deal(self, min_stock: StockMarket, max_stock: StockMarket, amount: float, min_price: float, max_price: float, coin: str):

        order_done = False
        order_id_buy = min_stock.place_order(min_price, amount, min_stock.coin_map[coin].symbol, 'BUY')

        start_time = time.time()
        while not order_done:
            order_done = min_stock.check_order(min_stock.coin_map[coin].symbol, order_id_buy)
            if time.time() - start_time > 10 and not order_done:
                if min_stock.cancel_order(min_stock.coin_map[coin].symbol, order_id_buy):
                    return
        print('Ордер на покупку выполнен')
        network = min_stock.get_coin_network(coin)
        address = max_stock.get_deposit_address(coin, network.name)
        amount = min_stock.get_coin_balance(coin)
        min_stock.withdraw(address, amount, coin, network.name)

        while float(max_stock.get_coin_balance(coin)) < float(amount):
            time.sleep(5)
        #TODO - TEST FROM HERE :)
        order_id_sell = max_stock.place_order(max_price, amount, max_stock.coin_map[coin].symbol, 'SELL')

        order_done = False
        while not order_done:
            order_done = max_stock.check_order(max_stock.coin_map[coin].symbol, order_id_sell)

        db = database.StockMarketDb()
        db._write_sucseeded_transation(self.get_all_acc_balance(),
                                       min_stock.name,
                                       max_stock.name,
                                       min_stock.get_coin_network(coin),
                                       coin)

        print('Ордер на продажу выполнен')

        pass

    def get_all_acc_balance(self):

        sum_balance = 0

        for stock in self.stock_ex_pool:

            sum_balance += float(stock.get_acc_balance())

        return sum_balance