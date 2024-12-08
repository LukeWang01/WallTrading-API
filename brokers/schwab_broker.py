from typing import Dict
from schwab import auth, client

from brokers.base_broker import BaseBroker

""" ⬇️ Broker Setup ⬇️ """
# refill the setup like MooMooFutuBroker Class
""" ⏫ Broker Setup ⏫ """


class SchwabBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        self.client = None
        self.max_attempts = 3
        self.retry_delay = 5  # seconds

    def connect(self, credentials: Dict) -> bool:
        # test example code, need to be modified
        # try:
        #     self.client = Schwab()
        #     # Login using credentials
        #     login_successful = self.client.login(
        #         username=credentials.get('username'),
        #         password=credentials.get('password'),
        #         # Optional MFA callback function
        #         mfa_callback=credentials.get('mfa_callback')
        #     )
        #
        #     if login_successful:
        #         self.connected = True
        #         self.logger.info("Successfully connected to Schwab")
        #         return True
        #     else:
        #         self.logger.error("Failed to connect to Schwab")
        #         return False
        #
        # except Exception as e:
        #     self.logger.error(f"Failed to connect to Schwab: {e}")
        #     return False
        pass

    def get_account_info(self):
        pass

    def market_sell(self, stock: str, quantity: int, price: float):
        try:
            order = self.client.place_order(
                stock=stock,
                quantity=quantity,
                order_type='market',
                side='sell'
            )
            print('Trader: Market Sell success!')

            return order

        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            print('Trader: Market Sell failed: ', e)

    def market_buy(self, stock: str, quantity: int, price: float):
        try:
            order = self.client.place_order(
                stock=stock,
                quantity=quantity,
                order_type='market',
                side='buy'
            )
            print('Trader: Market Buy success!')

            return order

        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            print('Trader: Market Buy failed: ', e)

    def limit_sell(self, stock: str, quantity: int, price: float):
        try:
            order = self.client.place_order(
                stock=stock,
                quantity=quantity,
                order_type='limit',
                side='sell',
                price=price,
                extended_hours=True  # add this to setting on top like MooMoo
            )
            print('Trader: Limit Sell success!')
            return order

        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            print('Trader: Limit Sell failed: ', e)

    def limit_buy(self, stock: str, quantity: int, price: float):
        try:
            order = self.client.place_order(
                stock=stock,
                quantity=quantity,
                order_type='limit',
                side='buy',
                price=price,
                extended_hours=True  # add this to setting on top like MooMoo
            )
            print('Trader: Limit Buy success!')
            return order

        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            print('Trader: Limit Buy failed: ', e)

    def get_positions(self):
        try:
            positions_data = self.client.get_positions()
            positions = []

            for pos in positions_data:
                positions.append(pos)  # rewrite pos to access the data

            return positions

        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")

    def get_cash_balance(self) -> float:
        try:
            account_data = self.client.get_account_info()
            return float(account_data['cash_balance'])

        except Exception as e:
            self.logger.error(f"Error fetching cash balance: {e}")

    def get_order_status(self, order_id: str):
        # try:
        #     order_status = self.client.get_order_status(order_id)
        #     print('Trader: Order status: ', order_status)
        #     return order_status
        #
        # except Exception as e:
        #     self.logger.error(f"Error fetching order status: {e}")
        #     print('Trader: Error fetching order status: ', e)
        pass
