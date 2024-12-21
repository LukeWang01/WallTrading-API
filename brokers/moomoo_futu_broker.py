# Dev
# 03/29/2024
# LukeLab for LookAtWallStreet
# Version 1.0
# Programming Trading based on MooMoo API/OpenD

"""
# updated: 11/17/2024, final version for open source only
# Version 2.0
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
"""

# MooMoo API Documentation, English:
# https://openapi.moomoo.com/moomoo-api-doc/en/intro/intro.html
# 官方文档，中文:
# https://openapi.moomoo.com/moomoo-api-doc/intro/intro.html

from moomoo import *

from brokers.base_broker import BaseBroker
from env._secrete import MooMoo_PWD
from utils.dataIO import logging_info

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
TRADING_PWD = MooMoo_PWD  # set up the trading password in the env/_secrete.py file
SECURITY_FIRM = SecurityFirm.FUTUINC  # set up the security firm based on your broker account registration
# for U.S. account, use FUTUINC, (default)
# for HongKong account, use FUTUSECURITIES
# for Singapore account, use FUTUSG
# for Australia account, use FUTUAU

'''
Step 3: Set up the trading information
'''
FILL_OUTSIDE_MARKET_HOURS = True  # enable if order fills on extended hours
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

    def init_context(self):
        self.trade_context = OpenSecTradeContext(filter_trdmarket=TRADING_MARKET, host=MOOMOOOPEND_ADDRESS,
                                                 port=MOOMOOOPEND_PORT, security_firm=SECURITY_FIRM)

    def close_context(self):
        self.trade_context.close()

    def _unlock_trade(self):
        if TRADING_ENVIRONMENT == TrdEnv.REAL:
            ret, data = self.trade_context.unlock_trade(TRADING_PWD)
            if ret != RET_OK:
                print('Unlock trade failed: ', data)
                return False
            print('Unlock Trade success!')
        return True

    def market_sell(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.SELL,
                                                       order_type=OrderType.MARKET, trd_env=TRADING_ENVIRONMENT)
            if ret != RET_OK:
                print('Trader: Market Sell failed: ', data)
                self.close_context()
                return ret, data
            print('Trader: Market Sell success!', data)
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Market Sell failed: unlock trade failed'
            print(data)
            self.close_context()
            return self.ret_error_code, data

    def market_buy(self, stock, quantity, price):
        self.init_context()
        if self._unlock_trade():
            code = f'US.{stock}'
            ret, data = self.trade_context.place_order(price=price, qty=quantity, code=code, trd_side=TrdSide.BUY,
                                                       order_type=OrderType.MARKET, trd_env=TRADING_ENVIRONMENT)
            if ret != RET_OK:
                print('Trader: Market Buy failed: ', data)
                self.close_context()
                return self.ret_error_code, data
            print('Trader: Market Buy success!', data)
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Market Buy failed: unlock trade failed'
            print(data)
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
                print('Trader: Limit Sell failed: ', data)
                self.close_context()
                return self.ret_error_code, data
            print('Trader: Limit Sell success!', data)
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Limit Sell failed: unlock trade failed'
            print(data)
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
                print('Trader: Limit Buy failed: ', data)
                self.close_context()
                return self.ret_error_code, data
            print('Trader: Limit Buy success!', data)
            self.close_context()
            return self.ret_ok_code, data
        else:
            data = 'Trader: Limit Buy failed: unlock trade failed'
            print(data)
            self.close_context()
            return self.ret_error_code, data

    def get_account_info(self):
        self.init_context()
        if self._unlock_trade():
            ret, data = self.trade_context.accinfo_query()
            if ret != RET_OK:
                print('Trader: Get Account Info failed: ', data)
                self.close_context()
                return self.ret_error_code, data

            acct_info = {
                'cash': round(data["cash"][0], 2),
                'total_assets': round(data["total_assets"][0], 2),
                'market_value': round(data["market_val"][0], 2),
            }
            self.close_context()
            logging_info('Trader: Get Account Info success!')
            return self.ret_ok_code, acct_info
        else:
            data = 'Trader: Get Account Info failed: unlock trade failed'
            print(data)
            self.close_context()
            return self.ret_error_code, data

    def get_positions(self):
        self.init_context()
        if self._unlock_trade():
            ret, data = self.trade_context.position_list_query()
            if ret != RET_OK:
                print('Trader: Get Positions failed: ', data)
                self.close_context()
                return self.ret_error_code, data
            # refactor the data
            data['code'] = data['code'].str[3:]
            data_dict = data.set_index('code').to_dict(orient='index')
            self.close_context()
            logging_info('Trader: Get Positions success!')
            return self.ret_ok_code, data_dict
        else:
            data = 'Trader: Get Positions failed: unlock trade failed'
            print(data)
            self.close_context()
            return self.ret_error_code, data

    def get_positions_by_ticker(self, ticker):
        position_ret, position_data = self.get_positions()
        if position_ret != self.ret_ok_code:
            # get current position quantity
            print('MooMoo, Get Positions by Ticker failed: ', position_data)
            return self.ret_error_code, position_data
        return self.ret_ok_code, position_data[ticker]["qty"]

    def get_cash_balance(self):
        acct_ret, acct_info = self.get_account_info()
        if acct_ret == self.ret_ok_code:
            return self.ret_ok_code, acct_info['cash']
        else:
            print('MooMooFutuBroker: Get Account Info and cash failed: ', acct_info)
            return self.ret_error_code, acct_info

    def get_cash_balance_number_only(self):
        acct_ret, acct_info = self.get_cash_balance()
        if acct_ret == self.ret_ok_code:
            return self.ret_ok_code, acct_info
        else:
            print('MooMooFutuBroker: Get cash balance number only failed: ', acct_info)
            return self.ret_error_code, acct_info
