"""
# created: 03/05/2025, final version for open source only
# Version 0.1.7
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus


long_port_broker.py
https://github.com/longportapp/openapi-sdk/tree/main-v2
"""
from brokers.base_broker import BaseBroker
from decimal import Decimal
from longport.openapi import TradeContext, Config, OrderType, OrderSide, TimeInForceType, OutsideRTH

from env._secrete import LongPort_app_key, LongPort_app_secret, LongPort_access_token
from utils.wall_api_client import print_status

import nest_asyncio

nest_asyncio.apply()


class LongPortBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        self.config = Config(app_key=LongPort_app_key,
                             app_secret=LongPort_app_secret,
                             access_token=LongPort_access_token)
        self.ctx = None

        self.currency = "USD"
        # self.is_connected = False

    def connect(self):
        try:
            self.ctx = TradeContext(self.config)
            if self.ctx:
                self.logger.info("Connected to LongPort")
                print_status("LongPort Trader", "Connected to LongPort", "INFO")
                return True
            else:
                self.logger.error("Failed to connect to LongPort")
                print_status("LongPort Trader", "Connect to LongPort failed, ctx empty, error", "ERROR")
                return False
        except Exception as e:
            self.logger.error(f"Failed to connect to LongPort: {e}")
            print_status("LongPort Trader", f"Connect to LongPort failed, {e}", "ERROR")
            return False

    def disconnect(self):
        self.ctx = None

    def get_cash_balance(self):
        if self.connect():
            resp = self.ctx.account_balance()
            if resp and resp.get("code", -1) == 0:
                cash_list = resp.get("data", {}).get("list", [])
                if cash_list:
                    for cash_info in cash_list[0].get("cash_infos", []):
                        if cash_info.get("currency") == self.currency:
                            available_cash = cash_info.get("available_cash")
                            # other cash info, for future use
                            # withdraw_cash = cash_info.get("withdraw_cash")
                            # frozen_cash = cash_info.get("frozen_cash")
                            # settling_cash = cash_info.get("settling_cash")
                            self.disconnect()
                            return self.ret_ok_code, available_cash
                    msg = f"Failed to get cash balance, NO USD FOUND: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_error_code, 0.0
                meg = f"Failed to get cash balance, cash list is empty: {resp}"
                self.logger.error(meg)
                print_status("LongPort Trader", meg, "ERROR")
                self.disconnect()
                return self.ret_error_code, 0.0
            else:
                msg = f"Failed to get cash balance: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, 0.0

    def get_cash_balance_number_only(self):
        return self.get_cash_balance()

    def get_account_info(self):
        if self.connect():
            resp = self.ctx.account_balance()
            if resp and resp.get("code") == 0:
                self.disconnect()
                return self.ret_ok_code, resp["data"]
            else:
                msg = f"Failed to get account info: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, None

    def get_positions(self):
        if self.connect():
            resp = self.ctx.stock_positions()
            if resp and resp.get("code") == 0:
                stock_list = resp.get("data", {}).get("list", [])
                stock_info_list = stock_list[0].get("stock_info", [])
                self.disconnect()
                return self.ret_ok_code, stock_info_list
            else:
                msg = f"Failed to get positions: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

    def get_positions_by_ticker(self, ticker: str):
        if self.connect():
            resp = self.ctx.stock_positions()
            if resp and resp.get("code") == 0:
                stock_list = resp.get("data", {}).get("list", [])
                stock_info_list = stock_list[0].get("stock_info", [])
                if not stock_list:
                    msg = f"Failed to get positions by ticker, stock list is empty: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_ok_code, 0.0

                for stock in stock_info_list:
                    if stock.get("symbol") == ticker:
                        self.disconnect()
                        return self.ret_ok_code, stock.get("quantity")

                msg = f"Failed to get positions by ticker, ticker not found: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "WARNING")
                self.disconnect()
                return self.ret_ok_code, 0.0
            else:
                msg = f"Failed to get positions by ticker: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

    def market_sell(self, stock: str, quantity: int, price: float):
        if self.connect():
            stock_symbol = f'{stock.upper()}.US'
            resp = self.ctx.submit_order(stock_symbol,
                                         OrderType.MO,
                                         OrderSide.Sell,
                                         Decimal(quantity),
                                         TimeInForceType.Day,
                                         )

            if resp and resp.get("code") == 0:
                if resp["message"] == "success":
                    self.disconnect()
                    return self.ret_ok_code, resp["data"]
                else:
                    msg = f"Failed to market sell: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_error_code, msg
            else:
                msg = f"Failed to market sell: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

    def market_buy(self, stock: str, quantity: int, price: float):
        if self.connect():
            stock_symbol = f'{stock.upper()}.US'
            resp = self.ctx.submit_order(stock_symbol,
                                         OrderType.MO,
                                         OrderSide.Buy,
                                         Decimal(quantity),
                                         TimeInForceType.Day,
                                         )

            if resp and resp.get("code") == 0:
                if resp["message"] == "success":
                    self.disconnect()
                    return self.ret_ok_code, resp["data"]
                else:
                    msg = f"Failed to market buy: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_error_code, msg
            else:
                msg = f"Failed to market buy: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

    def limit_sell(self, stock: str, quantity: int, price: float):
        if self.connect():
            stock_symbol = f'{stock.upper()}.US'
            resp = self.ctx.submit_order(stock_symbol,
                                         OrderType.LO,
                                         OrderSide.Sell,
                                         Decimal(quantity),
                                         TimeInForceType.GoodTilCanceled,
                                         submitted_price=Decimal(price),
                                         outside_rth=OutsideRTH.AnyTime
                                         )

            if resp and resp.get("code") == 0:
                if resp["message"] == "success":
                    self.disconnect()
                    return self.ret_ok_code, resp["data"]
                else:
                    msg = f"Failed to limit sell: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_error_code, msg
            else:
                msg = f"Failed to limit sell: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

    def limit_buy(self, stock: str, quantity: int, price: float):
        if self.connect():
            stock_symbol = f'{stock.upper()}.US'
            resp = self.ctx.submit_order(stock_symbol,
                                         OrderType.LO,
                                         OrderSide.Buy,
                                         Decimal(quantity),
                                         TimeInForceType.GoodTilCanceled,
                                         submitted_price=Decimal(price),
                                         outside_rth=OutsideRTH.AnyTime
                                         )

            if resp and resp.get("code") == 0:
                if resp["message"] == "success":
                    self.disconnect()
                    return self.ret_ok_code, resp["data"]
                else:
                    msg = f"Failed to limit buy: {resp}"
                    self.logger.error(msg)
                    print_status("LongPort Trader", msg, "ERROR")
                    self.disconnect()
                    return self.ret_error_code, msg
            else:
                msg = f"Failed to limit buy: {resp}"
                self.logger.error(msg)
                print_status("LongPort Trader", msg, "ERROR")
                self.disconnect()
                return self.ret_error_code, msg

