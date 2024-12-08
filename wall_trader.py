from utils.logger import setup_logger
from brokers.broker_factory import BrokerFactory


if __name__ == '__main__':
    # Setup logging
    logger = setup_logger('trading_app', 'logs/trading.log')

    # try:
    #     # Get broker instance
    #     ibkr = BrokerFactory.get_broker('IBKR')
    #
    #     # Get account information
    #     positions = ibkr.get_positions()
    #     cash = ibkr.get_cash_balance()
    #
    #     logger.info(f"Current cash balance: ${cash:,.2f}")
    #     for position in positions:
    #         logger.info(f"Position: {position.symbol}, Quantity: {position.quantity}, "
    #                     f"P/L: ${position.unrealized_pl:,.2f}")
    #
    #     # Place orders
    #     response = ibkr.market_buy(
    #         stock='AAPL',
    #         quantity=100,
    #         price=0.0)
    #
    #     logger.info(
    #         f"Order status: {response.status}, Order ID: {response.order_id}")
    #
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")

    try:
        # Get Schwab broker instance
        schwab = BrokerFactory.get_broker('SCHWAB')

        # Get account information
        positions = schwab.get_positions()
        cash = schwab.get_cash_balance()

        print(f"Current cash balance: ${cash:,.2f}")
        for position in positions:
            print(f"Position: {position.symbol}, Quantity: {position.quantity}, "
                  f"P/L: ${position.unrealized_pl:,.2f}")

        # Place a market order
        market_order = schwab.market_buy(stock='AAPL', quantity=100, price=0.0)

        # Place a limit order in extended hours
        limit_order = schwab.limit_buy(stock='MSFT', quantity=50, price=300.00)

        # Check order status
        market_order_status = schwab.get_order_status(market_order.order_id)
        print(f"Market order status: {market_order_status.status}")

    except Exception as e:
        print(f"An error occurred: {e}")
