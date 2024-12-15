import time
from ib_insync import IB, Stock, MarketOrder, LimitOrder, Trade
from typing import Dict

from brokers.base_broker import BaseBroker


class IBKRBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.ib = IB()
        self.connection_attempts = 0
        self.max_attempts = 3
        self.retry_delay = 5  # seconds

    def connect(self, credentials: Dict) -> bool:
        while self.connection_attempts < self.max_attempts:
            try:
                self.ib.connect(
                    host=credentials.get('host', 'localhost'),
                    port=credentials.get('port', 7497),
                    clientId=credentials.get('client_id', 1),
                    readonly=credentials.get('readonly', False)
                )
                self.connected = True
                self.connection_attempts = 0
                self.logger.info("Successfully connected to IBKR")
                return True

            except Exception as e:
                self.connection_attempts += 1
                self.logger.error(
                    f"Connection attempt {self.connection_attempts} failed: {e}")
                if self.connection_attempts < self.max_attempts:
                    time.sleep(self.retry_delay)

        self.logger.error("Failed to connect to IBKR after maximum attempts")
        return False

    def get_positions(self):
        try:
            positions = self.ib.positions()
            self.logger.info(f"Retrieved positions: {positions}")
            return positions
        except Exception as e:
            self.logger.error(f"Error retrieving positions: {e}")
            return None

    def get_cash_balance(self):
        try:
            account_values = self.ib.accountValues()
            cash_balance = next((v.value for v in account_values if v.tag == 'CashBalance'), None)
            self.logger.info(f"Retrieved cash balance: {cash_balance}")
            return cash_balance
        except Exception as e:
            self.logger.error(f"Error retrieving cash balance: {e}")
            return None

    def get_account_info(self):
        try:
            account_summary = self.ib.accountSummary()
            self.logger.info(f"Retrieved account info: {account_summary}")
            return account_summary
        except Exception as e:
            self.logger.error(f"Error retrieving account info: {e}")
            return None

    def market_sell(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = MarketOrder('sell', quantity)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)
        except Exception as e:
            self.logger.error(f"Error placing market sell order: {e}")
            return None

    def market_buy(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = MarketOrder('buy', quantity)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)
        except Exception as e:
            self.logger.error(f"Error placing market buy order: {e}")
            return None

    def limit_sell(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = LimitOrder('sell', quantity, price)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)
        except Exception as e:
            self.logger.error(f"Error placing limit sell order: {e}")
            return None

    def limit_buy(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = LimitOrder('buy', quantity, price)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)
        except Exception as e:
            self.logger.error(f"Error placing limit buy order: {e}")
            return None

    def _handle_trade_timeout(self, trade: Trade, timeout: int = 30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.ib.sleep(1)  # Sleep for 1 second to avoid busy-waiting
            if trade.isDone():
                self.logger.info(f"Trade completed: {trade}")
                return trade
        self.logger.error(f"Trade timed out after {timeout} seconds: {trade}")
        return None
