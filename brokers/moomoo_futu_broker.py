# Dev
# 03/29/2024
# LukeLab for LookAtWallStreet
# Version 1.0
# Programming Trading based on MooMoo API/OpenD

"""
# created: 11/17/2024, final version for open source only
# Version 2.0
# for more info, please visit: https://www.patreon.com/LookAtWallStreet

# created: 12/20/2024, final version for WallTrading API only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus

"""

# MooMoo API Documentation, English:
# https://openapi.moomoo.com/moomoo-api-doc/en/intro/intro.html
# 官方文档，中文:
# https://openapi.moomoo.com/moomoo-api-doc/intro/intro.html

from moomoo import *

from brokers.base_broker import BaseBroker
from env._secrete import MooMoo_Futu_PWD, MooMoo_Futu_SecurityFirm
from trading_settings import TRADING_BROKER, TRADING_ALLOW_PRE_POST_MARKET_ORDER
from utils.wall_api_client import print_status

import nest_asyncio

nest_asyncio.apply()

""" ⬇️ Broker Setup ⬇️ """
'''
Step 1: Set up the environment information
'''
# Environment Variables
MOOMOOOPEND_ADDRESS = "127.0.0.1"  # should be same as the OpenD host IP, just keep as default
MOOMOOOPEND_PORT = 11112  # should be same as the OpenD port number, make sure keep both the same
TRADING_ENVIRONMENT = TrdEnv.REAL  # set up trading environment, real, or simulate/paper trading
# REAL = "REAL"
# SIMULATE = "SIMULATE"

'''
Step 2: Set up the account information
'''
TRADING_PWD = MooMoo_Futu_PWD  # set up the trading password in the env/_secrete.py file

'''
Step 3: Set up the trading information
'''
FILL_OUTSIDE_MARKET_HOURS = TRADING_ALLOW_PRE_POST_MARKET_ORDER  # enable if order fills on extended hours
TRADING_MARKET = TrdMarket.US  # set up the trading market, US market, HK for HongKong, etc.
# NONE = "N/A"
# HK = "HK"
# US = "US"
# CN = "CN"
# HKCC = "HKCC"
# FUTURES = "FUTURES"

""" ⏫ project setup ⏫ """


# Trader class:
class MooMooFutuBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.trade_context = None

        # set up the security firm based on your broker account registration
        if MooMoo_Futu_SecurityFirm == 'FUTUINC':
            self.Broker_SecurityFirm = SecurityFirm.FUTUINC  # for U.S. account, use FUTUINC, (default)
        elif MooMoo_Futu_SecurityFirm == 'FUTUSECURITIES' or TRADING_BROKER == 'Futu':
            self.Broker_SecurityFirm = SecurityFirm.FUTUSECURITIES  # for HongKong account, use 'FUTUSECURITIES'
        elif MooMoo_Futu_SecurityFirm == 'FUTUSG':
            self.Broker_SecurityFirm = SecurityFirm.FUTUSG  # for Singapore account, use 'FUTUSG'
        else:
            self.Broker_SecurityFirm = SecurityFirm.FUTUAU  # for Australia account, use 'FUTUAU'

    def init_context(self):
        try:
            # if OpenD not running, it will loop to connect until OpenD is running.
            self.trade_context = OpenSecTradeContext(filter_trdmarket=TRADING_MARKET, host=MOOMOOOPEND_ADDRESS,
                                                     port=MOOMOOOPEND_PORT, security_firm=self.Broker_SecurityFirm)
            self.logger.info('MooMoo/Futu Trader: Init Context success!')
            return True
        except Exception as e:
            self.logger.error(f'MooMoo/Futu Trader: Init Context failed: {e}')
            self.logger.error('MooMoo/Futu Trader: Please check the OpenD host IP and port number!')
            print_status("MooMoo/Futu Trader", "Init Context failed, please check the OpenD host IP and port number!",
                         "ERROR")
            return False

    def close_context(self):
        self.trade_context.close()
        self.logger.info('MooMoo/Futu Trader: Close Context success!')

    def _unlock_trade(self):
        if TRADING_ENVIRONMENT == TrdEnv.REAL:
            ret, data = self.trade_context.unlock_trade(TRADING_PWD)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", f"Unlock Trade failed, {data}", "ERROR")
                return False
            print_status("MooMoo/Futu Trader", "Unlock Trade success", "SUCCESS")
        return True

    def market_sell(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.SELL,
                                                       order_type=OrderType.MARKET, trd_env=TRADING_ENVIRONMENT)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Market Sell failed", "ERROR")
                self.logger.warning(f'Trader: Market Sell failed: {data}')
                self.close_context()
                return ret, data
            print_status("MooMoo/Futu Trader", "Market Sell success", "SUCCESS")
            self.logger.info('Trader: Market Sell success!')
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Market Sell failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Market Sell failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def market_buy(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.BUY,
                                                       order_type=OrderType.MARKET, trd_env=TRADING_ENVIRONMENT)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Market Buy failed", "ERROR")
                self.logger.warning(f'Trader: Market Buy failed: {data}')
                self.close_context()
                return self.ret_error_code, data
            print_status("MooMoo/Futu Trader", "Market Buy success", "SUCCESS")
            self.logger.info('Trader: Market Buy success!')
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Market Buy failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Market Buy failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def limit_sell(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.SELL,
                                                       order_type=OrderType.NORMAL, trd_env=TRADING_ENVIRONMENT,
                                                       fill_outside_rth=FILL_OUTSIDE_MARKET_HOURS)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Limit Sell failed", "ERROR")
                self.logger.warning(f'Trader: Limit Sell failed: {data}')
                self.close_context()
                return self.ret_error_code, data
            print_status("MooMoo/Futu Trader", "Limit Sell success", "SUCCESS")
            self.logger.info('Trader: Limit Sell success!')
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Limit Sell failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Limit Sell failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def limit_buy(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.BUY,
                                                       order_type=OrderType.NORMAL, trd_env=TRADING_ENVIRONMENT,
                                                       fill_outside_rth=FILL_OUTSIDE_MARKET_HOURS)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Limit Buy failed", "ERROR")
                self.logger.warning(f'Trader: Limit Buy failed: {data}')
                self.close_context()
                return self.ret_error_code, data
            print_status("MooMoo/Futu Trader", "Limit Buy success", "SUCCESS")
            self.logger.info('Trader: Limit Buy success!')
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Limit Buy failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Limit Buy failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def get_account_info(self):
        self.init_context()
        if self._unlock_trade():
            # https://openapi.moomoo.com/moomoo-api-doc/en/trade/get-funds.html
            # Default, currency=Currency.HKD, change to USD
            # updated 01-07-2025
            ret, data = self.trade_context.accinfo_query(currency=Currency.USD)
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Get Account Info failed", "ERROR")
                self.logger.warning(f'Trader: Get Account Info failed: {data}')
                self.close_context()
                return self.ret_error_code, data

            acct_info = {
                # https://openapi.moomoo.com/moomoo-api-doc/en/trade/get-funds.html
                # Obsolete. Please use 'us_cash' or other fields to get the cash of each currency.
                # updated 01-07-2025
                'cash': round(data["us_cash"][0], 2),
                'total_assets': round(data["total_assets"][0], 2),
                'market_value': round(data["market_val"][0], 2),
            }
            self.close_context()
            self.logger.info('Trader: Get Account Info success!')
            return self.ret_ok_code, acct_info
        else:
            data = 'Trader: Get Account Info failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Get Account Info failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def get_positions(self):
        self.init_context()
        if self._unlock_trade():
            ret, data = self.trade_context.position_list_query()
            if ret != RET_OK:
                print_status("MooMoo/Futu Trader", "Get Positions failed", "ERROR")
                self.logger.warning(f'Trader: Get Positions failed: {data}')
                self.close_context()
                return self.ret_error_code, data
            # refactor the data
            data['code'] = data['code'].str[3:]
            data_dict = data.set_index('code').to_dict(orient='index')
            self.close_context()
            self.logger.info('Trader: Get Positions success!')
            return self.ret_ok_code, data_dict
        else:
            data = 'Trader: Get Positions failed: unlock trade failed'
            print_status("MooMoo/Futu Trader", "Get Positions failed: unlock trade failed", "ERROR")
            self.logger.warning(data)
            self.close_context()
            return self.ret_error_code, data

    def get_positions_by_ticker(self, ticker):
        position_ret, position_data = self.get_positions()
        if position_ret != self.ret_ok_code:
            # get current position quantity
            print_status("MooMoo/Futu Trader", "Get Positions by Ticker failed", "ERROR")
            return self.ret_error_code, position_data
        try:
            qty = position_data[ticker]["qty"]
            return self.ret_ok_code, qty
        except KeyError as e:
            print_status("MooMoo/Futu Trader", "Get Positions by Ticker failed", "ERROR")
            self.logger.warning(f"Trader: Get Positions by Ticker failed: {e}")
            return self.ret_error_code, 0

    def get_cash_balance(self):
        acct_ret, acct_info = self.get_account_info()
        if acct_ret == self.ret_ok_code:
            return self.ret_ok_code, acct_info['cash']
        else:
            print_status("MooMoo/Futu Trader", "Get Cash Balance failed", "ERROR")
            self.logger.warning("Trader: Get Cash Balance failed")
            return self.ret_error_code, acct_info

    def get_cash_balance_number_only(self):
        acct_ret, acct_info = self.get_cash_balance()
        if acct_ret == self.ret_ok_code:
            return self.ret_ok_code, acct_info
        else:
            print_status("MooMoo/Futu Trader", "Get Cash Balance number only failed", "ERROR")
            self.logger.warning("Trader: Get Cash Balance number only failed")
            return self.ret_error_code, acct_info
