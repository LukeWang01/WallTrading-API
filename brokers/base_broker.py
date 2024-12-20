from abc import ABC, abstractmethod

from utils.logger_config import setup_logger
from trading_settings import TRADING_LIST, TRADING_CONFIRMATION, TRADING_CASH_CONTROL, TRADING_CASH_THRESHOLD
from utils.time_tool import is_market_hours, get_current_time


class BaseBroker(ABC):
    def __init__(self):
        self.broker_name = self.__class__.__name__

        # setup logger, child classes should keep align with these codes
        self.logger = setup_logger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.broker_name}")

        # return codes setup, child classes should keep align with these codes
        self.ret_ok_code = 1
        self.ret_error_code = -1

    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def get_positions_by_ticker(self, ticker: str):
        # return the current position quantity of the ticker,
        # int (or float if fractional shares are supported)
        pass

    @abstractmethod
    def get_cash_balance(self):
        pass

    @abstractmethod
    def get_cash_balance_number_only(self):
        # return the current cash balance, float
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

    def broker_make_trade(self, direction: str, called_by: str, stock: str, quantity: int, price: float):
        if stock in TRADING_LIST and TRADING_CONFIRMATION:
            # Bull, buy order
            if direction == "Bull":
                # check the current buying power first
                ret_status_code, current_cash = self.get_cash_balance_number_only()
                if ret_status_code != self.ret_ok_code:
                    data = f"⚠️⚠️⚠️\n{get_current_time()}: {stock}, Buy Failed. \nFailed to get the current cash balance, skipped., {called_by}\n⚠️⚠️⚠️"
                    print(data)
                    self.logger.warning(data)
                    return

                if current_cash >= TRADING_CASH_THRESHOLD and current_cash > quantity * price or not TRADING_CASH_CONTROL:
                    if is_market_hours():
                        # market order
                        ret_status_code, order_data = self.market_buy(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Market Buy: {stock}, {quantity}, {price}, order placed, please check account., {called_by}"
                            print(data)
                            print(order_data)
                            self.logger.info(data)
                            self.logger.info(order_data)
                        else:
                            data = f"⚠️⚠️⚠️\n{get_current_time()}: {stock}, Buy Failed. \nThe market value is higher than the limit or trading not confirmed, skipped., {called_by}\n⚠️⚠️⚠️"
                            print(data)
                            print(order_data)
                            self.logger.warning(data)
                            self.logger.warning(order_data)
                    else:
                        # limit order extended hours
                        ret_status_code, order_data = self.limit_buy(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Limit Buy: {stock}, {quantity}, {price}, order placed, please check account., {called_by}"
                            print(data)
                            print(order_data)
                            self.logger.info(data)
                            self.logger.info(order_data)
                        else:
                            data = f"⚠️⚠️⚠️\n{get_current_time()}: {stock}, Buy Failed. \nThe market value is higher than the limit or trading not confirmed, skipped., {called_by}\n⚠️⚠️⚠️"
                            print(data)
                            print(order_data)
                            self.logger.warning(data)
                            self.logger.warning(order_data)

                else:
                    # order failed
                    data = f"⚠️⚠️⚠️\n{get_current_time()}: {stock}, Buy Failed. \nThe market value is higher than the limit or trading not confirmed, skipped., {called_by}\n⚠️⚠️⚠️"
                    print(data)
                    self.logger.warning(data)

            # Bear, sell order
            if direction == "Bear":
                ok_to_sell = True
                ret_status_code, position_by_ticker = self.get_positions_by_ticker(stock)
                if ret_status_code != self.ret_ok_code:
                    data = f"{stock}, Sell Order failed, Failed to get the current position, skipped., {called_by}"
                    print(data)
                    self.logger.warning(data)
                    return

                if quantity >= position_by_ticker - 2:
                    # set the sell quantity at least less than the current position - 1
                    data = f"{stock}, Sell Order failed, The current position is less than the order quantity, skipped., {called_by}"
                    print(data)
                    self.logger.warning(data)
                    ok_to_sell = False

                if ok_to_sell:
                    if is_market_hours():
                        # market order
                        ret_status_code, order_data = self.market_sell(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Market Sell: {stock}, {quantity}, {price}, order placed, please check account., {called_by}"
                            print(data)
                            print(order_data)
                            self.logger.info(data)
                            self.logger.info(order_data)
                        else:
                            # order failed
                            data = f"{get_current_time()}: Market Sell: {stock}, {quantity}, {price}, order failed, please check account., {called_by}"
                            print(data)
                            self.logger.warning(data)
                    else:
                        # limit order extended hours
                        ret_status_code, order_data = self.limit_sell(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Limit Sell: {stock}, {quantity}, {price}, order placed, please check account., {called_by}"
                            print(data)
                            print(order_data)
                            self.logger.info(data)
                            self.logger.info(order_data)
                        else:
                            # order failed
                            data = f"{get_current_time()}: Limit Sell: {stock}, {quantity}, {price}, order failed, please check account., {called_by}"
                            print(data)
                            print(order_data)
                            self.logger.warning(data)
                            self.logger.warning(order_data)

        # if stock not in the trading list, skip the order
        else:
            # print(f"{get_current_time()}: Stock({stock}) not in the trading list, skip the order.")
            print(f'Stock({stock}) not in the trading list, skip the order., {called_by}')
            self.logger.warning(f"Stock({stock}) not in the trading list, skip the order., {called_by}")
