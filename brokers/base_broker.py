"""
# created: 12/20/2024, final version for open source only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus
"""

from abc import ABC, abstractmethod

from utils.logger_config import setup_logger
from trading_settings import TRADING_LIST, TRADING_CONFIRMATION, TRADING_CASH_MARGIN_CONTROL, TRADING_CASH_THRESHOLD
from utils.time_tool import is_market_hours, get_current_time
from utils.wall_api_client import print_status


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
        """
        Get the current positions
        :return: status code, positions
        """
        pass

    @abstractmethod
    def get_positions_by_ticker(self, ticker: str):
        """
        Get the current positions by ticker
        :param ticker:
        :return: status code, positions
        """
        pass

    @abstractmethod
    def get_cash_balance(self):
        """
        Get the cash balance
        :return: status code, cash balance
        """
        pass

    @abstractmethod
    def get_cash_balance_number_only(self) -> tuple[int, float]:
        """
        Get the cash balance number only
        :return: status code, cash balance
        """
        pass

    @abstractmethod
    def get_account_info(self):
        """
        Get the account information
        :return: status code, account information
        """
        pass

    @abstractmethod
    def market_sell(self, stock: str, quantity: int, price: float):
        # ignore price for market orders if needed for the broker class implementation
        """
        Market sell
        :param stock:
        :param quantity:
        :param price:
        :return: status code, order data
        """
        pass

    @abstractmethod
    def market_buy(self, stock: str, quantity: int, price: float):
        # ignore price for market orders if needed for the broker class implementation
        """
        Market buy
        :param stock:
        :param quantity:
        :param price:
        :return: status code, order data
        """
        pass

    @abstractmethod
    def limit_sell(self, stock: str, quantity: int, price: float):
        """
        Limit sell
        :param stock:
        :param quantity:
        :param price:
        :return: status code, order data
        """
        pass

    @abstractmethod
    def limit_buy(self, stock: str, quantity: int, price: float):
        """
        Limit buy
        :param stock:
        :param quantity:
        :param price:
        :return: status code, order data
        """
        pass

    def broker_make_trade(self, direction: str, called_by: str, stock: str, quantity: int, price: float):
        if stock in TRADING_LIST and TRADING_CONFIRMATION:
            # Bull, buy order
            if direction == "Bull":
                # check the current buying power first
                ret_status_code, current_cash = self.get_cash_balance_number_only()
                if ret_status_code != self.ret_ok_code:
                    data = f"{get_current_time()}: {stock}, Buy Failed. \nFailed to get the current cash balance, skipped, by: {called_by}"
                    # print(data)
                    print_status("BaseBroker", data, "ERROR")
                    self.logger.error(data)
                    return

                if current_cash >= TRADING_CASH_THRESHOLD and current_cash > quantity * price or not TRADING_CASH_MARGIN_CONTROL:
                    if is_market_hours():
                        # market order
                        ret_status_code, order_data = self.market_buy(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Market Buy: {stock}, {quantity}, {price}, order placed successfully, please check account. by: {called_by}"
                            # print(data)
                            print_status("BaseBroker", data, "INFO")
                            # print(order_data)
                            self.logger.info(data)
                            # self.logger.info(order_data)  # for privacy, not logging the order data, updated 01-13-2025
                        else:
                            data = f"{get_current_time()}: Market Buy: {stock}, {quantity}, {price} Failed, please check broker side or app, by: {called_by}"
                            # print(data)
                            # print(order_data)
                            print_status("BaseBroker", data, "ERROR")
                            print_status("BaseBroker", order_data, "ERROR")
                            # self.logger.error(data)
                            self.logger.error(order_data)   # only log error msg, updated 03-09-2025
                    else:
                        # limit order extended hours
                        ret_status_code, order_data = self.limit_buy(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Limit Buy: {stock}, {quantity}, {price}, order placed successfully, please check account, by: {called_by}"
                            # print(data)
                            # print(order_data)
                            print_status("BaseBroker", data, "INFO")
                            # self.logger.info(data)
                            # self.logger.info(order_data)  # for privacy, not logging the order data, updated 01-13-2025
                        else:
                            data = f"{get_current_time()}: Limit Buy: {stock}, {quantity}, {price} Failed, please check broker side or app, by: {called_by}"
                            # print(data)
                            # print(order_data)
                            print_status("BaseBroker", data, "ERROR")
                            print_status("BaseBroker", order_data, "ERROR")
                            self.logger.error(data)
                            self.logger.error(order_data)   # only log error msg, updated 03-09-2025
                else:
                    # order failed
                    data = f"{get_current_time()}: Buy: {stock}, {quantity}, {price} Failed: no enough cash, below the threshold, or wrong margin settings, {current_cash} - {TRADING_CASH_THRESHOLD} - {quantity * price} - {TRADING_CASH_MARGIN_CONTROL}, by: {called_by}"
                    # print(data)
                    print_status("BaseBroker", data, "ERROR")
                    self.logger.error(data)

            # Bear, sell order
            if direction == "Bear":
                ok_to_sell = True
                ret_status_code, position_by_ticker = self.get_positions_by_ticker(stock)
                if ret_status_code != self.ret_ok_code:
                    data = f"{get_current_time()}: Sell: {stock}, {quantity}, {price} failed, Failed to get the current position, skipped, by: {called_by}"
                    # print(data)
                    print_status("BaseBroker", data, "ERROR")
                    self.logger.error(data)
                    return

                if quantity >= position_by_ticker - 2:
                    # set the sell quantity at least less than the current position - 1
                    data = f"{get_current_time()}: Sell: {stock}, {quantity}, {price} failed, no enough position to sell, skipped, {quantity} - {position_by_ticker}, by: {called_by}"
                    # print(data)
                    print_status("BaseBroker", data, "WARNING")
                    self.logger.warning(data)
                    ok_to_sell = False

                if ok_to_sell:
                    if is_market_hours():
                        # market order
                        ret_status_code, order_data = self.market_sell(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Market Sell: {stock}, {quantity}, {price}, order placed successfully, please check account., by: {called_by}"
                            # print(data)
                            print_status("BaseBroker", data, "INFO")
                            # print(order_data)
                            # self.logger.info(data)
                            # self.logger.info(order_data)  # for privacy, not logging the order data, updated 01-13-2025
                        else:
                            # order failed
                            data = f"{get_current_time()}: Market Sell: {stock}, {quantity}, {price}, order failed, please check broker side or app, by: {called_by}"
                            # print(data)
                            print_status("BaseBroker", data, "ERROR")
                            self.logger.warning(data)   # only log warning msg, updated 03-09-2025
                    else:
                        # limit order extended hours
                        ret_status_code, order_data = self.limit_sell(stock, quantity, price)
                        if ret_status_code == self.ret_ok_code:
                            data = f"{get_current_time()}: Limit Sell: {stock}, {quantity}, {price}, order placed successfully, please check account., by: {called_by}"
                            # print(data)
                            print_status("BaseBroker", data, "INFO")
                            # print(order_data)
                            # self.logger.info(data)
                            # self.logger.info(order_data)  # for privacy, not logging the order data, updated 01-13-2025
                        else:
                            # order failed
                            data = f"{get_current_time()}: Limit Sell: {stock}, {quantity}, {price}, order failed, please check broker side or app, by: {called_by}"
                            # print(data)
                            # print(order_data)
                            print_status("BaseBroker", data, "ERROR")
                            print_status("BaseBroker", order_data, "ERROR")
                            self.logger.warning(data)
                            self.logger.warning(order_data)  # only log warning msg, updated 03-09-2025

        # if stock not in the trading list, skip the order
        else:
            data = f"{get_current_time()}: Stock({stock}) is not in the trading list:{TRADING_LIST}, or the trading is disable:{TRADING_CONFIRMATION}, skip the order, by: {called_by}"
            # print(data)
            print_status("BaseBroker", data, "WARNING")
            self.logger.warning(data)
