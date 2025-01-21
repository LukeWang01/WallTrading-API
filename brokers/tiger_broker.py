"""
# created: 01/18/2024, final version for open source only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus
"""

from typing import Optional, Tuple

from brokers.base_broker import BaseBroker
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.consts import Market, SecurityType, Currency
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.trade.domain.order import Order

from env._secrete import Tiger_account_number

import time

import nest_asyncio

from utils.wall_api_client import print_status

nest_asyncio.apply()

""" ⬇️ Broker Setup ⬇️ """
# Tiger API Docs: https://quant.itigerup.com/openapi/zh/python/overview/introduction.html
'''
Step 1: Set up the environment information
'''
# Environment Variables
TIGER_CONFIG_PATH = './env/'

'''
Step 2: Set up the account information
'''
TIGER_ACCOUNT_NUMBER = Tiger_account_number  # set up the account number in the env/_secrete.py file

'''
Step 3: Set up the trading information
'''
FILL_OUTSIDE_MARKET_HOURS = True  # enable if order fills on extended hours

""" ⏫ Broker Setup ⏫ """


class TigerBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        self.connection_attempts = 0
        self.max_attempts = 3
        self.retry_delay = 5  # seconds
        # init the trade_client, account_hash, and connected status
        self.trade_client = None
        self.connected = False

    def connect(self) -> bool:
        while self.connection_attempts < self.max_attempts:
            try:
                self.trade_client = TradeClient(self._get_client_config())
                self.trade_client.get_managed_accounts(
                    account=TIGER_ACCOUNT_NUMBER)  # if the execution fails, the Tiger SDK will raise an exception
                self.connected = True
                self.connection_attempts = 0
                # self.logger.info("Successfully connected to Tiger")
                return True

            except Exception as e:
                self.connection_attempts += 1
                self.logger.error(
                    f"Connection attempt {self.connection_attempts} failed: {e}")
                if self.connection_attempts < self.max_attempts:
                    time.sleep(self.retry_delay * self.connection_attempts ** 2)  # exponential backoff

        self.connected = False
        self.logger.error("Failed to connect to Tiger after maximum attempts")
        return False

    def _get_client_config(self) -> TigerOpenClientConfig:
        client_config = TigerOpenClientConfig(props_path=TIGER_CONFIG_PATH)
        return client_config

    def get_account_info(self) -> Tuple[int, Optional[dict]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Account Info failed: not connected")
            # print("Trader: Get Account Info failed: not connected")
            print_status("Trader", "Get Account Info failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            account_info = self.trade_client.get_managed_accounts(account=TIGER_ACCOUNT_NUMBER)
            self.logger.info(f"Retrieved account info: {account_info}")
            return self.ret_ok_code, account_info
        except Exception as e:
            self.logger.error(f"Error retrieving account info: {e}")
            return self.ret_ok_code, None

    def get_cash_balance(self) -> Tuple[int, Optional[float]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Cash Balance failed: not connected")
            # print("Trader: Get Cash Balance failed: not connected")
            print_status("Trader", "Get Cash Balance failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            portfolio_account = self.trade_client.get_prime_assets(account=TIGER_ACCOUNT_NUMBER, base_currency='USD')
            cash_available_for_trade = portfolio_account.segments['S'].currency_assets['USD'].cash_available_for_trade
            self.logger.info(f"Retrieved cash balance: {cash_available_for_trade}")
            return self.ret_ok_code, float(cash_available_for_trade)
        except Exception as e:
            self.logger.error(f"Error retrieving cash balance: {e}")
            return self.ret_error_code, None

    def get_cash_balance_number_only(self) -> Tuple[int, Optional[float]]:
        return self.get_cash_balance()

    def get_positions(self) -> Tuple[int, Optional[list]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Positions failed: not connected")
            # print("Trader: Get Positions failed: not connected")
            print_status("Trader", "Get Positions failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            positions = self.trade_client.get_positions(account=TIGER_ACCOUNT_NUMBER, sec_type=SecurityType.STK,
                                                        currency=Currency.USD, market=Market.US, symbol=None)
            self.logger.info(f"Retrieved positions: {positions}")
            return self.ret_ok_code, positions
        except Exception as e:
            self.logger.error(f"Error retrieving positions: {e}")
            return self.ret_error_code, None

    def get_positions_by_ticker(self, ticker) -> Tuple[int, Optional[int]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Positions by Ticker failed: not connected")
            # print("Trader: Get Positions by Ticker failed: not connected")
            print_status("Trader", "Get Positions by Ticker failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            position = self.trade_client.get_positions(account=TIGER_ACCOUNT_NUMBER, sec_type=SecurityType.STK,
                                                       currency=Currency.USD, market=Market.US, symbol=ticker)
            if not position:
                return self.ret_error_code, 0
            return self.ret_ok_code, position[0].salable_qty
        except Exception as e:
            self.logger.error(f"Error retrieving positions: {e}")
            return self.ret_error_code, None

    def market_sell(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Market Sell failed: not connected")
            # print("Trader: Market Sell failed: not connected")
            print_status("Trader", "Market Sell failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            contract = stock_contract(symbol=stock, currency='USD')
            order = Order(account=TIGER_ACCOUNT_NUMBER, contract=contract, action='SELL', order_type='MKT',
                          quantity=quantity)
            oid = self.trade_client.place_order(order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing market sell order: {e}")
            return self.ret_error_code, None

    def market_buy(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Market Buy failed: not connected")
            # print("Trader: Market Buy failed: not connected")
            print_status("Trader", "Market Buy failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            contract = stock_contract(symbol=stock, currency='USD')
            order = Order(account=TIGER_ACCOUNT_NUMBER, contract=contract, action='BUY', order_type='MKT',
                          quantity=quantity)
            oid = self.trade_client.place_order(order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing market buy order: {e}")
            return self.ret_error_code, None

    def limit_sell(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Limit Sell failed: not connected")
            # print("Trader: Limit Sell failed: not connected")
            print_status("Trader", "Limit Sell failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            contract = stock_contract(symbol=stock, currency='USD')
            order = Order(account=TIGER_ACCOUNT_NUMBER, contract=contract, action='SELL', order_type='LMT',
                          quantity=quantity, limit_price=price, outside_rth=FILL_OUTSIDE_MARKET_HOURS,
                          time_in_force='GTC')
            oid = self.trade_client.place_order(order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing limit sell order: {e}")
            return self.ret_error_code, None

    def limit_buy(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Limit Buy failed: not connected")
            # print("Trader: Limit Buy failed: not connected")
            print_status("Trader", "Limit Buy failed: not connected", "ERROR")
            return self.ret_error_code, None

        try:
            contract = stock_contract(symbol=stock, currency='USD')
            order = Order(account=TIGER_ACCOUNT_NUMBER, contract=contract, action='BUY', order_type='LMT',
                          quantity=quantity, limit_price=price, outside_rth=FILL_OUTSIDE_MARKET_HOURS,
                          time_in_force='GTC')
            oid = self.trade_client.place_order(order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing limit buy order: {e}")
            return self.ret_error_code, None
