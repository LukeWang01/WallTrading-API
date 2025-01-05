"""
# created: 12/20/2024, final version for open source only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus
"""

import requests
from webull import webull

from brokers.base_broker import BaseBroker
from utils.time_tool import get_current_time

""" ⬇️ Broker Setup ⬇️ """
# refill the setup like MooMooFutuBroker Class
""" ⏫ Broker Setup ⏫ """


class WebullBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        # Log in authentication:
        self.username = ''
        self.password = ''
        self.device_name = ''

        # Trading token authentication:
        self.PID = ''
        self.PID_timeout = 15  # should be int

        # init webull api
        self._webull = webull()

        # Authentication additional:
        self.did = ''
        self.access_token = ''
        self.uuid = ''
        self.account_id = ''
        self.account_type = ''

        # Trader current trading status:
        self.order_placed = 0
        self.order_filled = 0
        self.order_pending = 0
        self.openPL_pct = 0
        self.openPL = 0
        self.dayPL_pct = 0
        self.dayPL = 0
        self.market_value = 0
        self.cash_balance = 0
        self.net_account_value = 0
        self.my_positions = ''
        self.dayBuyingPower = 0
        self.overnightBuyingPower = 0
        self.cryptoBuyingPower = 0
        self.optionBuyingPower = 0
        self.open_orders = ''

        # Historical trading status:
        self.filled_orders_history = ''
        self.cancelled_orders_history = ''
        self.pending_orders_history = ''

        self.has_trader_info = False

        print(f"Webull created")

    def set_PID_expiry(self, expiry):
        self._webull.timeout = expiry

    def set_trader_info(self, username, password, pid):
        self.username = username
        self.password = password
        self.PID = pid
        print(f"Webull: Trader info set")

    def set_user_name(self, email):
        self.username = email

    def set_device_name(self, device_name):
        self.device_name = device_name

    def set_auth_did(self, did):
        self._webull._set_did(did)
        self.did = did

    def set_auth_access_token(self, access_token):
        self.access_token = access_token
        self._webull._access_token = access_token

    def set_auth_uuid(self, uuid):
        self._webull.uuid = uuid
        self.uuid = uuid

    def get_account_id(self):
        return self.account_id

    def is_trader_logged_in(self):
        return self._webull.is_logged_in()

    def set_time_out(self, timeout):
        self._webull.timeout = int(timeout)

    def login_preparation(self):
        return self.uuid != '' and self.did != '' and self.access_token != ''

    def log_in(self):
        try:
            self._webull._access_token = self.access_token
            login_result = self._webull.login(self.username, self.password, device_name=self.device_name,
                                              save_token=True)
            response = self._webull.is_logged_in()
            if response:
                self.account_id = self._webull.get_account_id()
                self.account_type = self._webull.get_account_type(self.username)
                # print('-----------------------------------')
                # print('>>>>>>   Log in successful   <<<<<<')
                # print(f'>>>   Your login ID: {self.account_id}   <<<')
                print('Log in successful')
                return True
            else:
                # print('-----------------------------------')
                # print('>>> Log in failed, authentication failed, check info below: ')
                # print(login_result)
                print(f'Log in failed, authentication failed, check info below: {login_result}')
                return False
        except ValueError:
            # print('>>>>>>    Log in failed, please check username or password')
            print('Log in failed, please check username or password')
            return False

    def log_out(self):
        response = self._webull.logout()
        print('Logout requested')
        print(response)

    def enable_trading(self):
        response = self._webull.get_trade_token(self.PID)
        # print('-----------------------------------')
        # print('>>> Enable trading requested <<<')
        if response:
            # print('Trading enabled, authentication passed')
            print('Trading enabled, authentication passed')
            return True
        else:
            if self._webull.is_logged_in():
                # print('Authentication failed, check PID again')
                print('Authentication failed, check PID again')
                return False
            else:
                # print('Authentication failed, please log in again')
                print('Authentication failed, please login again')
                return False

    def get_stock_quote(self, stock):
        res = {}
        try:
            quote_response = self._webull.get_quote(stock)
            ask_price_1 = quote_response['askList'][0]['price']
            bid_price_1 = quote_response['bidList'][0]['price']
            res['bid_price'] = bid_price_1
            res['ask_price'] = ask_price_1
            # print('-----------------------------------')
            # print('>>> Stock ticker: ', stock)
            # print('>>> First bid price/ buy one price:  ', bid_price_1)
            # print('>>> First ask price/ sell one price:  ', ask_price_1)
            return res
        except ValueError or KeyError:
            # print('>>> Please pass a valid stock ticker <<<')
            print('Please pass a valid stock ticker')
            return False

    def get_bid_price(self, stock):
        # get first bid price
        res = self.get_stock_quote(stock)
        if res:
            # print('-----------------------------------')
            # print('>>> Stock: ', stock, 'First bid price/ buy one price:', res['bid_price'])
            return res['bid_price']
        else:
            print('Please pass a valid stock ticker')
            return False

    def get_ask_price(self, stock):
        # get first ask price
        res = self.get_stock_quote(stock)
        if res:
            # print('-----------------------------------')
            # print('>>> Stock: ', stock, 'First ask price/ sell one price: ', res['ask_price'])
            return res['ask_price']
        else:
            print('Please pass a valid stock ticker')
            return False

    def get_account_info(self):
        account_info = self._webull.get_account()
        self.account_id = account_info['secAccountId']
        self.order_placed = '-'
        self.order_filled = '-'
        self.order_pending = account_info['openOrderSize']
        self.openPL_pct = str(round(float(account_info['unrealizedProfitLossRate']) * 100, 2)) + ' %'
        self.openPL = account_info['unrealizedProfitLoss']
        self.dayPL_pct = '-'
        self.dayPL = '-'
        self.market_value = account_info['accountMembers'][0]['value']
        self.cash_balance = account_info['accountMembers'][1]['value']
        self.dayBuyingPower = account_info['accountMembers'][2]['value']
        self.overnightBuyingPower = account_info['accountMembers'][3]['value']
        self.cryptoBuyingPower = account_info['accountMembers'][4]['value']
        self.optionBuyingPower = account_info['accountMembers'][5]['value']
        self.net_account_value = account_info['netLiquidation']

    def market_sell(self, stock: str, quantity: int, price: float):
        self.enable_trading()
        # Sell, market order, sell 1 price, daily:
        response = self._webull.place_order(stock=stock, action='SELL', enforce='DAY', orderType='MKT', quant=quantity)
        price = self.get_bid_price(stock)
        order_details = self.print_order_details(response, stock, price, quantity, 'SELL', 'MKT')
        return order_details

    def market_buy(self, stock: str, quantity: int, price: float):
        self.enable_trading()
        # Buy, market order, buy 1 price, daily:
        response = self._webull.place_order(stock=stock, action='BUY', enforce='DAY', orderType='MKT', quant=quantity)
        price = self.get_ask_price(stock)
        order_details = self.print_order_details(response, stock, price, quantity, 'BUY', 'MKT')
        return order_details

    def limit_sell(self, stock: str, quantity: int, price: float):
        self.enable_trading()
        # Sell, limit price order, ask price, sell 1 price, daily:
        response = self._webull.place_order(stock=stock, action='SELL', price=price, enforce='DAY', orderType='LMT',
                                            quant=quantity)
        order_details = self.print_order_details(response, stock, price, quantity, 'SELL', 'DAY')
        return order_details

    def limit_buy(self, stock: str, quantity: int, price: float):
        self.enable_trading()
        # Buy, limit price order, bid price, buy 1 price, daily:
        response = self._webull.place_order(stock=stock, action='BUY', price=price, enforce='DAY', orderType='LMT',
                                            quant=quantity)
        order_details = self.print_order_details(response, stock, price, quantity, 'BUY', 'DAY')
        return order_details

    def order_limit_buy_gtc(self, stock, price, quantity=1):
        self.enable_trading()
        # Buy, limit price order, ask price, buy 1 price, GTC order:
        response = self._webull.place_order(stock=stock, action='BUY', price=price, enforce='GTC', orderType='LMT',
                                            quant=quantity)
        order_details = self.print_order_details(response, stock, price, quantity, 'BUY', 'GTC')
        return order_details

    def order_limit_sell_gtc(self, stock, price, quantity=1):
        self.enable_trading()
        # Sell, limit price order, bid price, sell 1 price, GTC order:
        response = self._webull.place_order(stock=stock, action='SELL', price=price, enforce='GTC', orderType='LMT',
                                            quant=quantity)
        order_details = self.print_order_details(response, stock, price, quantity, 'SELL', 'GTC')
        return order_details

    def get_positions(self):
        account_info = self._webull.get_account()
        position = account_info['positions']
        ticker = position['ticker']['symbol']
        qty = position['position']
        marketValue = position['marketValue']
        lastPrice = position['lastPrice']
        costPrice = position['costPrice']
        unrealizedProfitLoss = position['unrealizedProfitLoss']
        unrealizedProfitLossRate = round(float(position['unrealizedProfitLossRate']) * 100, 2)
        return position

    def get_positions_by_ticker(self, ticker: str):
        # TODO: get positions by ticker
        pass

    def get_cash_balance(self) -> float:
        account_info = self._webull.get_account()
        self.cash_balance = float(account_info['accountMembers'][1]['value'])
        return self.cash_balance

    def get_cash_balance_number_only(self):
        return self.get_cash_balance()

    def print_order_details(self, response, stock, price, qty, direction, order_type):
        if response['success']:
            res = {'result': 'success',
                   'status': '>>>>>> Order placed successfully! <<<<<<',
                   'account_id': self.account_id,
                   'order_id': response['data']['orderId'],
                   'order_time': get_current_time(),
                   'stock_info': stock,
                   'order_direction': direction,
                   'order_type': order_type,
                   'order_price': price,
                   'order_qty': qty,
                   'order_cost': round(float(price) * int(qty), 3)
                   }
            return res
        else:
            res = {
                'result': 'failed',
                'status': '>>>>>> Order placed Failed! <<<<<<',
                'msg': response['msg'],
            }
            return res

    def get_history_orders_v2(self, status='All', count=20):
        # rewrite the get_history_orders function in the webull library
        headers = self._webull.build_req_headers(include_trade_token=True, include_time=True)
        base_ustradebroker_url = 'https://ustrade.webullbroker.com/api'
        response = requests.get(f'{base_ustradebroker_url}/trade/v2/option/list?secAccountId={self._webull._account_id}'
                                f'&dateType=ORDER&pageSize={count}&status=' + str(status), headers=headers,
                                timeout=self._webull.timeout)
        return response.json()

    def get_filled_orders_history(self, status='Filled', count=200):
        # get filled orders
        res = self.get_history_orders_v2(status, count)
        return res

    def get_cancelled_orders_history(self, status='Cancelled', count=200):
        # get cancelled orders
        res = self.get_history_orders_v2(status, count)
        return res

    def get_pending_orders_history(self, status='Working', count=200):
        # get pending orders
        res = self.get_history_orders_v2(status, count)
        return res
