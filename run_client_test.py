import asyncio
import signal
import sys

from brokers.broker_factory import BrokerFactory
from env._secrete import SERVER_IP, API_CLIENT_ID, API_PASSWORD
from trading_settings import TRADING_BROKER
from utils.wall_api_client import DataClient, print_status
from utils.logger_config import setup_logger


"""
For test only, not for production use.

Please run this script to test before running the `run_client.py`.

This test can:

1. Check the required libraries are installed
2. Check the settings are correct
3. Check the client can connect to the server

"""


# Setup logger for the client runner
logger = setup_logger('client_runner')

# Global variable to track the client instance
client = None
shutdown_event = asyncio.Event()

# Initialize the client trader
client_trader = BrokerFactory.get_broker(TRADING_BROKER)
print_status("Client Runner", "Client Trader Initialized, testing", "INFO")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    print_status("Client Runner", "Shutdown signal received", "WARNING")
    if client:
        client.running = False
    if not shutdown_event.is_set():
        shutdown_event.set()


async def main():
    global client

    logger.info("Starting client process")
    print_status("Client Runner", "Starting client test process", "INFO")

    def handle_data(json_data):
        """Handle incoming data"""
        logger.debug(f"Received data: {json_data}")
        print_status("Data Handler",
                     f"Received data: {json_data}, type: {type(json_data)}",
                     "INFO")
        print_status("Data Handler", "Starting to process data", "INFO")
        # some code here
        print_status("Data Handler", "Data processed", "SUCCESS")
        print_status("Client Runner", "Client test done", "SUCCESS")


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
    print(">>> Starting client test")
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
