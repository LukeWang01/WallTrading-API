from ib_insync import IB, Stock, MarketOrder, LimitOrder, Trade
from typing import Dict
import time

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
        pass

    def get_cash_balance(self):
        pass

    def get_account_info(self):
        pass

    def market_sell(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = MarketOrder('sell', quantity)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)

        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            print(f"Error placing market order: {e}")

    def market_buy(self, stock: str, quantity: int, price: float):
        pass

    def limit_sell(self, stock: str, quantity: int, price: float):
        try:
            contract = Stock(stock, 'SMART', 'USD')
            order = LimitOrder('sell', quantity, price)
            trade = self.ib.placeOrder(contract, order)
            return self._handle_trade_timeout(trade)

        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            print(f"Error placing limit order: {e}")

    def limit_buy(self, stock: str, quantity: int, price: float):
        pass

    def _handle_trade_timeout(self, trade: Trade, timeout: int = 30):
        # end_time = time.time() + timeout
        # while time.time() < end_time:
        #     if trade.orderStatus.status == 'Filled':
        #         return OrderResponse(
        #             order_id=str(trade.order.orderId),
        #             status='FILLED',
        #             filled_quantity=trade.orderStatus.filled,
        #             filled_price=trade.orderStatus.avgFillPrice
        #         )
        #     elif trade.orderStatus.status in ['Cancelled', 'Error']:
        #         return OrderResponse(
        #             order_id=str(trade.order.orderId),
        #             status='FAILED',
        #             message=trade.orderStatus.whyHeld
        #         )
        #     self.ib.sleep(0.1)
        #
        # return OrderResponse(
        #     order_id=str(trade.order.orderId),
        #     status='PENDING',
        #     message='Order placement timeout'
        # )
        #
        pass


