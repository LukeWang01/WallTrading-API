"""
# created: 12/20/2024, final version for open source only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus
"""

from typing import Optional, Tuple

from brokers.base_broker import BaseBroker
from schwab.auth import easy_client, client_from_login_flow, client_from_manual_flow
from schwab.orders.equities import equity_buy_limit, equity_sell_limit, equity_buy_market, equity_sell_market
from schwab.orders.common import Duration, Session

from env._secrete import Schwab_account_number, Schwab_app_key, Schwab_secret

import httpx
import time

from trading_settings import TRADING_ALLOW_PRE_POST_MARKET_ORDER
from utils.wall_api_client import print_status

""" ⬇️ Broker Setup ⬇️ """
# Schwab API Docs: https://schwab-py.readthedocs.io/en/latest/getting-started.html
'''
Step 1: Set up the environment information
'''
# Environment Variables
SCHWAB_CALLBACK_URL = 'https://127.0.0.1:8182'  # should be same as the Callback URL of the App in Schwab Developer Portal, just keep as default
SCHWAB_TOKEN_PATH = './env/_schwab_token.json'

'''
Step 2: Set up the account information
'''
SCHWAB_ACCOUNT_NUMBER = Schwab_account_number  # set up the account number in the env/_secrete.py file
SCHWAB_APP_KEY = Schwab_app_key  # set up the App Key in the env/_secrete.py file
SCHWAB_SECRET = Schwab_secret  # set up the Secret in the env/_secrete.py file

'''
Step 3: Set up the trading information
'''
FILL_OUTSIDE_MARKET_HOURS = TRADING_ALLOW_PRE_POST_MARKET_ORDER  # enable if order fills on extended hours

""" ⏫ Broker Setup ⏫ """


class SchwabBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        self.connection_attempts = 0
        self.max_attempts = 3
        self.retry_delay = 5  # seconds
        # self.connect()    #don't connect when init here, connect when needed

        # init the client, account_hash, and connected status
        self.client = None
        self.account_hash = None
        self.connected = False

    def connect(self) -> bool:
        while self.connection_attempts < self.max_attempts:
            try:
                self.client = easy_client(api_key=SCHWAB_APP_KEY, app_secret=SCHWAB_SECRET,
                                          callback_url=SCHWAB_CALLBACK_URL, token_path=SCHWAB_TOKEN_PATH,
                                          max_token_age=60 * 60 * 24 * 6.5)

                ret_status_code, self.account_hash = self._get_account_hash()
                if ret_status_code != self.ret_ok_code:
                    raise Exception

                self.connected = True
                self.connection_attempts = 0
                # self.logger.info("Successfully connected to Schwab")
                return True

            except Exception as e:
                self.connection_attempts += 1
                self.logger.error(
                    f"Connection attempt {self.connection_attempts} failed: {e}")
                if self.connection_attempts < self.max_attempts:
                    time.sleep(self.retry_delay * self.connection_attempts ** 2)  # exponential backoff

        self.connected = False
        self.logger.error("Failed to connect to Schwab after maximum attempts")
        return False

    def _get_account_hash(self) -> Tuple[int, Optional[str]]:
        resp = self.client.get_account_numbers()
        if resp.status_code != httpx.codes.OK:
            self.logger.error(f"Trader: Get Account Hash failed: {resp.json()['message']}")
            # print(f"Trader: Get Account Hash failed: {resp.json()['message']}")
            print_status("Trader", f"Get Account Hash failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        account_hash = next(
            (item['hashValue'] for item in resp.json() if item['accountNumber'] == SCHWAB_ACCOUNT_NUMBER),
            None
        )

        if account_hash:
            return self.ret_ok_code, account_hash
        else:
            self.logger.error('Trader: Get Account Hash failed: wrong account number')
            # print("Trader: Get Account Hash failed: wrong account number")
            print_status("Trader", "Get Account Hash failed: wrong account number", "ERROR")
            return self.ret_error_code, None

    def get_account_info(self) -> Tuple[int, Optional[dict]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Account Info failed: not connected")
            # print("Trader: Get Account Info failed: not connected")
            print_status("Trader", "Get Account Info failed: not connected", "ERROR")
            return self.ret_error_code, None

        resp = self.client.get_account(self.account_hash)

        if resp.status_code != httpx.codes.OK:
            self.logger.error(f"Trader: Get Account Info failed: {resp.json()['message']}")
            # print(f"Trader: Get Account Info failed: {resp.json()['message']}")
            print_status("Trader", f"Get Account Info failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        account_info = resp.json()

        cash = 0

        if account_info['securitiesAccount']['type'] == 'CASH':
            cash = account_info['securitiesAccount']['currentBalances']['totalCash'] - \
                   account_info['securitiesAccount']['currentBalances']['unsettledCash']
        elif account_info['securitiesAccount']['type'] == 'MARGIN':
            cash = account_info['securitiesAccount']['currentBalances']['cashBalance']
        total_assets = account_info['securitiesAccount']['currentBalances']['liquidationValue']
        market_value = account_info['securitiesAccount']['currentBalances']['longMarketValue']

        acct_info = {
            'cash': round(cash, 2),
            'total_assets': round(total_assets, 2),
            'market_value': round(market_value, 2),
        }

        self.logger.info(f"Retrieved account info: {acct_info}")

        return self.ret_ok_code, acct_info

    def get_cash_balance(self) -> Tuple[int, Optional[float]]:
        acct_ret, acct_info = self.get_account_info()
        if acct_ret == self.ret_ok_code:
            self.logger.info(f"Retrieved cash balance: {acct_info['cash']}")
            return self.ret_ok_code, acct_info['cash']
        else:
            return self.ret_error_code, None

    def get_cash_balance_number_only(self) -> Tuple[int, Optional[float]]:
        return self.get_cash_balance()

    def get_positions(self) -> Tuple[int, Optional[dict]]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Get Positions failed: not connected")
            # print("Trader: Get Positions failed: not connected")
            print_status("Trader", "Get Positions failed: not connected", "ERROR")
            return self.ret_error_code, None

        resp = self.client.get_account(self.account_hash, fields=[self.client.Account.Fields.POSITIONS])

        if resp.status_code != httpx.codes.OK:
            self.logger.error(f"Trader: Get Positions failed: {resp.json()['message']}")
            # print(f"Trader: Get Positions failed: {resp.json()['message']}")
            print_status("Trader", f"Get Positions failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None
        else:
            account_info = resp.json()
            positions = account_info.get('securitiesAccount', {}).get('positions', [])
            data_dict = {}
            for position in positions:
                code = position['instrument']['symbol']
                position_data = {key: value for key, value in position.items() if key != 'instrument'}
                position_data.update(position['instrument'])
                data_dict[code] = position_data
            self.logger.info(f"Retrieved positions: {data_dict}")
            return self.ret_ok_code, data_dict

    def get_positions_by_ticker(self, ticker: str) -> Tuple[int, Optional[float]]:
        ret_status_code, positions = self.get_positions()
        if ret_status_code == self.ret_ok_code:
            position = positions.get(ticker, {})
            return self.ret_ok_code, position.get('longQuantity', 0.0)
        else:
            return self.ret_error_code, None

    def market_sell(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Market Sell failed: not connected")
            # print("Trader: Market Sell failed: not connected")
            print_status("Trader", "Market Sell failed: not connected", "ERROR")
            return self.ret_error_code, None

        order = equity_sell_market(stock, quantity).build()
        resp = self.client.place_order(self.account_hash, order)

        if resp.status_code != httpx.codes.CREATED:
            self.logger.error(f"Trader: Market Sell failed: {resp.json()['message']}")
            # print(f"Trader: Market Sell failed: {resp.json()['message']}")
            print_status("Trader", f"Market Sell failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        return self.ret_ok_code, None

    def market_buy(self, stock: str, quantity: int, price: float) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Market Buy failed: not connected")
            # print("Trader: Market Buy failed: not connected")
            print_status("Trader", "Market Buy failed: not connected", "ERROR")
            return self.ret_error_code, None

        order = equity_buy_market(stock, quantity).build()
        resp = self.client.place_order(self.account_hash, order)

        if resp.status_code != httpx.codes.CREATED:
            self.logger.error(f"Trader: Market Buy failed: {resp.json()['message']}")
            # print(f"Trader: Market Buy failed: {resp.json()['message']}")
            print_status("Trader", f"Market Buy failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        return self.ret_ok_code, None

    def limit_sell(self, stock: str, quantity: int, price: str) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Limit Sell failed: not connected")
            # print("Trader: Limit Sell failed: not connected")
            print_status("Trader", "Limit Sell failed: not connected", "ERROR")
            return self.ret_error_code, None

        if not isinstance(price, str):
            price = str(price)

        if FILL_OUTSIDE_MARKET_HOURS:
            order = equity_sell_limit(stock, quantity, price).set_duration(Duration.GOOD_TILL_CANCEL).set_session(
                Session.SEAMLESS).build()
        else:
            order = equity_sell_limit(stock, quantity, price).set_duration(Duration.GOOD_TILL_CANCEL).set_session(
                Session.NORMAL).build()
        resp = self.client.place_order(self.account_hash, order)

        if resp.status_code != httpx.codes.CREATED:
            self.logger.error(f"Trader: Limit Sell failed: {resp.json()['message']}")
            # print(f"Trader: Limit Sell failed: {resp.json()['message']}")
            print_status("Trader", f"Limit Sell failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        return self.ret_ok_code, None

    def limit_buy(self, stock: str, quantity: int, price: str) -> Tuple[int, None]:
        self.connect()
        if not self.connected:
            self.logger.error(f"Trader: Limit Buy failed: not connected")
            # print("Trader: Limit Buy failed: not connected")
            print_status("Trader", "Limit Buy failed: not connected", "ERROR")
            return self.ret_error_code, None

        if not isinstance(price, str):
            price = str(price)

        if FILL_OUTSIDE_MARKET_HOURS:
            order = equity_buy_limit(stock, quantity, price).set_duration(Duration.GOOD_TILL_CANCEL).set_session(
                Session.SEAMLESS).build()
        else:
            order = equity_buy_limit(stock, quantity, price).set_duration(Duration.GOOD_TILL_CANCEL).set_session(
                Session.NORMAL).build()
        resp = self.client.place_order(self.account_hash, order)

        if resp.status_code != httpx.codes.CREATED:
            self.logger.error(f"Trader: Limit Buy failed: {resp.json()['message']}")
            # print(f"Trader: Limit Buy failed: {resp.json()['message']}")
            print_status("Trader", f"Limit Buy failed: {resp.json()['message']}", "ERROR")
            return self.ret_error_code, None

        return self.ret_ok_code, None
