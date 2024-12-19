from abc import ABC, abstractmethod
import logging

from trading_settings import TRADING_LIST, TRADING_CONFIRMATION, TRADING_CASH_CONTROL, TRADING_CASH_THRESHOLD
from utils.time_tool import is_market_hours, get_current_time


class BaseBroker(ABC):
    def __init__(self):
        self.broker_name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.broker_name}")

    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def get_positions_by_ticker(self, ticker: str):
        pass

    @abstractmethod
    def get_cash_balance(self):
        pass

    @abstractmethod
    def get_cash_balance_number_only(self):
        pass

    @abstractmethod
    def get_account_info(self):
        pass

    @abstractmethod
    def market_sell(self, stock: str, quantity: int, price: float):
        # ignore price for market orders if needed for the broker class implementation
        pass

    @abstractmethod
    def market_buy(self, stock: str, quantity: int, price: float):
        # ignore price for market orders if needed for the broker class implementation
        pass

    @abstractmethod
    def limit_sell(self, stock: str, quantity: int, price: float):
        pass

    @abstractmethod
    def limit_buy(self, stock: str, quantity: int, price: float):
        pass

    def strategy_make_trade(self, direction: str, called_by: str, stock: str, quantity: int, price: float):
        if stock in TRADING_LIST and TRADING_CONFIRMATION:
            if direction == "Bull":
                # check the current buying power first
                current_cash = self.get_cash_balance_number_only()

                if current_cash >= TRADING_CASH_THRESHOLD and current_cash > quantity * price or not TRADING_CASH_CONTROL:
                    if is_market_hours():
                        # market order
                        self.market_buy(stock, quantity, price)
                        print(f"{get_current_time()}: Market Buy: {stock}, {quantity}, {price}, order placed, please check account.")
                    else:
                        # limit order extended hours
                        self.limit_buy(stock, quantity, price)
                        print(f"{get_current_time()}: Limit Buy: {stock}, {quantity}, {price}, order placed, please check account.")

                else:
                    # order failed
                    data = f"⚠️⚠️⚠️\n{get_current_time()}: {stock}, Buy Failed. \nThe market value is higher than the limit or trading not confirmed, skipped.\n⚠️⚠️⚠️"
                    print(data)

            if direction == "Bear":
                ok_to_sell = True
                position_by_ticker = self.get_positions_by_ticker(stock)

                if quantity >= position_by_ticker - 2:
                    # set the sell quantity at least less than the current position - 1
                    data = f"{stock}, Sell Order failed, The current position is less than the order quantity, skipped."
                    print(data)
                    ok_to_sell = False

                if ok_to_sell:
                    if is_market_hours():
                        # market order
                        self.market_sell(stock, quantity, price)
                        print(f"{get_current_time()}: Market Sell: {stock}, {quantity}, {price}, order placed, please check account.")
                    else:
                        # limit order extended hours
                        self.limit_sell(stock, quantity, price)
                        print(f"{get_current_time()}: Limit Sell: {stock}, {quantity}, {price}, order placed, please check account.")

        # if stock not in the trading list, skip the order
        else:
            # print(f"{get_current_time()}: Stock({stock}) not in the trading list, skip the order.")
            print(f'Stock({stock}) not in the trading list, skip the order.')
