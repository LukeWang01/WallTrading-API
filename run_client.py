import asyncio
import signal
import sys

from brokers.broker_factory import BrokerFactory
from env._secrete import SERVER_IP, API_CLIENT_ID, API_PASSWORD
from trading_settings import decision_qty, TRADING_BROKER, TRADING_CONFIRMATION
from utils.wall_api_client import DataClient, print_status
from utils.logger_config import setup_logger

# Setup logger for the client runner
logger = setup_logger('client_runner')

# Global variable to track the client instance
client = None
shutdown_event = asyncio.Event()

# Initialize the client trader
client_trader = BrokerFactory.get_broker(TRADING_BROKER)
print_status("Client Runner", "Client Trader Initialized", "INFO")


def trader_broker_setup_check():
    try:
        ret_code, data = client_trader.get_cash_balance_number_only()
        if ret_code == client_trader.ret_ok_code:
            print_status("Client Runner", "Broker setup successful", "SUCCESS")
            return True
        else:
            print_status("Client Runner", "Broker setup failed, please check password or connection", "ERROR")
            return False
    except Exception as error:
        print_status("Client Runner", f"Broker setup failed: {error}", "ERROR")
        return False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    print_status("Client Runner", "Shutdown signal received", "WARNING")
    if client:
        client.running = False
    if not shutdown_event.is_set():
        shutdown_event.set()


def check_if_test_data(json_data):
    for k, v in json_data.items():
        if "test" in str(k):
            return True
        if "test" in str(v):
            return True
    return False


def handle_data(json_data):
    """Handle incoming data"""
    logger.debug(f"Received data: {json_data}")
    print_status("Data Handler",
                 f"Received data: {json_data}, type: {type(json_data)}",
                 "INFO")
    print_status("Data Handler", "Starting to process data", "INFO")

    """
    json_data = {
            "time": time_now,
            "ticker": stock,
            "price": price,
            "level": level,
            "direction": direction, # Bull or Bear
            "depth": depth,
            "codeNum": codeNum,
            "qty": qty, (Optional)
        }
    """
    if check_if_test_data(json_data):
        # test data received, no trade made
        print_status("Data Handler", "Test data received, no trade made", "INFO")
    else:
        # trading data received, make trade
        qty_num, qty_pct = decision_qty(json_data)
        print_status("Data Handler", f"Decision qty: {qty_num}, Decision original qty percent: {qty_pct}", "INFO")
        called_by = "run_client.py - handle_data"
        if qty_num > 0:
            if TRADING_CONFIRMATION:
                try:
                    print_status("Data Handler", "Making trade...", "INFO")
                    client_trader.broker_make_trade(json_data["direction"], called_by, json_data["ticker"], qty_num,
                                                    json_data["price"])
                except Exception as error:
                    print_status("Data Handler", f"Error making trade: {error}", "ERROR")
            else:
                print_status("Data Handler", "No trade made, trading not confirmed", "INFO")
        else:
            print_status("Data Handler", "No trade made, qty decision is 0", "WARNING")


async def main():
    global client

    logger.info("Starting client process")
    print_status("Client Runner", "Starting client process", "INFO")

    # Initialize client
    client = DataClient(
        server_url=f"http://{SERVER_IP}:8000",
        client_id=API_CLIENT_ID,
        password=API_PASSWORD
    )

    # Setup signal handlers in a cross-platform way
    if sys.platform != 'win32':
        logger.debug("Setting up Unix-style signal handlers")
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: signal_handler(sig, None))
    else:
        logger.debug("Setting up Windows-style signal handlers")
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal_handler)

    try:
        logger.info("Starting client listener")
        print_status("Client Runner", "Starting connection to server", "INFO")

        listen_task = asyncio.create_task(client.listen(handle_data))
        wait_task = asyncio.create_task(shutdown_event.wait())

        # Wait for either the shutdown event or the listen task to complete
        done, pending = await asyncio.wait(
            {listen_task, wait_task},
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.debug("Task cancelled successfully")

        if listen_task in done:
            # If listen_task completed, check if it raised any exceptions
            try:
                await listen_task
            except Exception as e:
                logger.error(f"Error in listen task: {e}")
                print_status("Client Runner",
                             f"Error in connection: {str(e)}",
                             "ERROR")

        logger.info("Initiating shutdown sequence")
        print_status("Client Runner", "Initiating shutdown sequence", "INFO")
        await client.close()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print_status("Client Runner", f"Unexpected error: {str(e)}", "ERROR")
    finally:
        logger.info("Cleanup complete")
        print_status("Client Runner", "Cleanup complete", "SUCCESS")


if __name__ == "__main__":
    if trader_broker_setup_check():
        try:
            logger.info("Initializing client application")
            print_status("Client Runner",
                         "Initializing client application", "INFO")

            # start the client runner, listening for data
            asyncio.run(main())

        except KeyboardInterrupt:
            logger.warning("Program interrupted by user")
            print_status("Client Runner", "Program interrupted by user", "WARNING")
        except Exception as e:
            logger.error(f"Fatal error in main: {e}")
            print_status("Client Runner", f"Fatal error: {str(e)}", "ERROR")
    else:
        logger.error("Broker setup failed, exiting... Please check required settings")
        print_status("Client Runner", "Broker setup failed, exiting... Please check required settings", "ERROR")
        sys.exit(1)
