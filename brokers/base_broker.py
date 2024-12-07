from abc import ABC, abstractmethod
import logging


class BaseBroker(ABC):
    def __init__(self):
        self.broker_name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def get_cash_balance(self):
        pass

    @abstractmethod
    def get_account_info(self):
        pass

    @abstractmethod
    def market_sell(self, stock: str, quantity: int, price: float):
        pass

    @abstractmethod
    def market_buy(self, stock: str, quantity: int, price: float):
        pass

    @abstractmethod
    def limit_sell(self, stock: str, quantity: int, price: float):
        pass

    @abstractmethod
    def limit_buy(self, stock: str, quantity: int, price: float):
        pass
