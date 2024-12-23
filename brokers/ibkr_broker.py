"""
# updated: 12/20/2024, final version for open source only
# Version 0.1.1
# for more info, please visit: https://www.patreon.com/LookAtWallStreet
Dev. Team:
Luke
Angus
"""

from brokers.base_broker import BaseBroker
from ib_insync import IB, Stock, MarketOrder, LimitOrder, Trade
import time

from env._secrete import IBKR_account_number

""" ⬇️ Broker Setup ⬇️ """
# IBKR API Docs: https://ib-insync.readthedocs.io/readme.html
'''
Step 1: Set up the environment information
'''
# Environment Variables
CREDENTIAL = {
    'host': 'localhost',
    'port': 4001,  # IB Gateway or TWS port number, should be 4001 or 7497 in default
    'client_id': 1,
    'readonly': False
}

'''
Step 2: Set up the account information
'''
IBKR_ACCOUNT_NUMBER = IBKR_account_number  # set up the account number in the env/_secrete.py file

'''
Step 3: Set up the trading information
'''
# TODO: Set up the trading information for pre post market trading
FILL_OUTSIDE_MARKET_HOURS = True  # enable if order fills on extended hours

""" ⏫ Broker Setup ⏫ """


class IBKRBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.ib = IB()
        self.connection_attempts = 0
        self.max_attempts = 3
        self.retry_delay = 5  # seconds

    def connect(self) -> bool:
        while self.connection_attempts < self.max_attempts:
            try:
                self.ib.connect(
                    host=CREDENTIAL.get('host', 'localhost'),
                    port=CREDENTIAL.get('port', 4001),
                    clientId=CREDENTIAL.get('client_id', 1),
                    readonly=CREDENTIAL.get('readonly', False)
                )
                self.connected = True
                self.connection_attempts = 0
                # self.logger.info("Successfully connected to IBKR")
                return True

            except Exception as e:
                self.connection_attempts += 1
                self.logger.error(
                    f"Connection attempt {self.connection_attempts} failed: {e}")
                if self.connection_attempts < self.max_attempts:
                    time.sleep(self.retry_delay * self.connection_attempts ** 2)  # exponential backoff

        self.connected = False
        self.logger.error("Failed to connect to IBKR after maximum attempts")
        return False

    def get_account_info(self):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Get Account Info failed: not connected")
            print("Trader: Get Account Info failed: not connected")
            return self.ret_error_code, None
        
        try:
            account_summary = self.ib.accountSummary(IBKR_ACCOUNT_NUMBER)
            self.logger.info(f"Retrieved account info: {account_summary}")
            return self.ret_ok_code, account_summary
        except Exception as e:
            self.logger.error(f"Error retrieving account info: {e}")
            return self.ret_ok_code, None
        finally:
            self.ib.disconnect()

    def get_cash_balance(self):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Get Cash Balance failed: not connected")
            print("Trader: Get Cash Balance failed: not connected")
            return self.ret_error_code, None
        
        try:
            account_values = self.ib.accountValues(IBKR_ACCOUNT_NUMBER)
            cash_balance = next((v.value for v in account_values if v.tag == 'CashBalance'), None)
            self.logger.info(f"Retrieved cash balance: {cash_balance}")
            return self.ret_ok_code, float(cash_balance)
        except Exception as e:
            self.logger.error(f"Error retrieving cash balance: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def get_cash_balance_number_only(self):
        return self.get_cash_balance()
    
    def get_positions(self):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Get Positions failed: not connected")
            print("Trader: Get Positions failed: not connected")
            return self.ret_error_code, None
        
        try:
            positions = self.ib.positions(IBKR_ACCOUNT_NUMBER)
            self.logger.info(f"Retrieved positions: {positions}")
            return self.ret_ok_code, positions
        except Exception as e:
            self.logger.error(f"Error retrieving positions: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def get_positions_by_ticker(self, ticker):
        try:
            positions = self.get_positions()
            return self.ret_ok_code, next((p.position for p in positions[1] if p.contract.symbol == ticker), 0.0)
        except Exception as e:
            self.logger.error(f"Error retrieving positions by ticker: {e}")
            return self.ret_error_code, None

    def market_sell(self, stock: str, quantity: int, price: float):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Market Sell failed: not connected")
            print("Trader: Market Sell failed: not connected")
            return self.ret_error_code, None
        
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = MarketOrder('sell', quantity, account=IBKR_ACCOUNT_NUMBER)
            trade = self.ib.placeOrder(contract, order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing market sell order: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def market_buy(self, stock: str, quantity: int, price: float):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Market Buy failed: not connected")
            print("Trader: Market Buy failed: not connected")
            return self.ret_error_code, None
        
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = MarketOrder('buy', quantity, account=IBKR_ACCOUNT_NUMBER)
            trade = self.ib.placeOrder(contract, order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing market buy order: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def limit_sell(self, stock: str, quantity: int, price: float):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Limit Sell failed: not connected")
            print("Trader: Limit Sell failed: not connected")
            return self.ret_error_code, None
        
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = LimitOrder('sell', quantity, price, account=IBKR_ACCOUNT_NUMBER)
            trade = self.ib.placeOrder(contract, order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing limit sell order: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def limit_buy(self, stock: str, quantity: int, price: float):
        self.connect()
        if not self.ib.isConnected():
            self.logger.error(f"Trader: Limit Buy failed: not connected")
            print("Trader: Limit Buy failed: not connected")
            return self.ret_error_code, None
        
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = LimitOrder('buy', quantity, price, account=IBKR_ACCOUNT_NUMBER)
            trade = self.ib.placeOrder(contract, order)
            return self.ret_ok_code, None
        except Exception as e:
            self.logger.error(f"Error placing limit buy order: {e}")
            return self.ret_error_code, None
        finally:
            self.ib.disconnect()

    def _handle_trade_timeout_market(self, trade: Trade, timeout: int = 30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.ib.sleep(1)  # Sleep for 1 second to avoid busy-waiting
            if trade.isDone():
                self.logger.info(f"Trade completed: {trade}")
                return trade
        self.logger.error(f"Trade timed out after {timeout} seconds: {trade}")
        return None
    
    def _handle_trade_timeout_limit(self, trade: Trade, timeout: int = 30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.ib.sleep(1)  # Sleep for 1 second to avoid busy-waiting
            if trade.isActive():
                self.logger.info(f"Trade submitted: {trade}")
                return trade
        self.logger.error(f"Trade timed out after {timeout} seconds: {trade}")
        return None
