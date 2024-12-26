import websockets
from websockets.exceptions import ConnectionClosed
# noinspection PyUnresolvedReferences
from websockets.exceptions import InvalidMessage, InvalidStatusCode
import asyncio
import json
import requests
from typing import Callable, Optional, Tuple
from utils.logger_config import setup_logger
import os
from requests.exceptions import ConnectionError, Timeout

# Create logs directory if it doesn't exist
os.makedirs('./logs', exist_ok=True)

# Setup logger
logger = setup_logger('wall_api_client')

# Terminal output formatting


class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(source: str, message: str, status: str = "INFO"):
    """Format and print status messages to terminal"""
    color = {
        "INFO": TerminalColors.OKBLUE,
        "SUCCESS": TerminalColors.OKGREEN,
        "WARNING": TerminalColors.WARNING,
        "ERROR": TerminalColors.FAIL
    }.get(status, TerminalColors.OKBLUE)

    print(
        f"{color}[{status}] {TerminalColors.BOLD}{source}: {TerminalColors.ENDC}{message}")


class DataClient:
    def __init__(self, server_url: str, client_id: str, password: str):
        self.server_url = server_url.rstrip('/')
        self.ws_url = server_url.replace('http', 'ws') + '/ws'
        self.client_id = client_id
        self.password = password
        self.token: Optional[str] = None
        self.running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.base_retry_delay = 5  # Base delay in seconds
        self.max_auth_retries = 3
        self.auth_retry_count = 0
        self.auth_required = False  # New flag to track if re-auth is needed
        self.max_server_check_retries = 5  # New attribute for server check retries
        self.server_check_count = 0  # New counter for server checks
        print_status(
            "DataClient", f"Initialized for client {client_id}", "INFO")
        logger.info(
            f"DataClient initialized for {client_id} with server URL: {server_url}")

    async def check_server_status(self) -> Tuple[bool, str]:
        """Check if the server is online and responding"""
        try:
            logger.debug(f"Checking server status at {self.server_url}")
            response = requests.get(
                f"{self.server_url}/",
                timeout=5
            )
            if response.status_code == 200:
                self.server_check_count = 0
                logger.info(
                    "Server status check: Server is online and responding")
                return True, "Server is online"
            logger.warning(
                f"Server returned unexpected status code: {response.status_code}")
            return False, f"Server returned status code: {response.status_code}"
        except ConnectionError:
            logger.error(
                "Server connection failed: Server is offline or unreachable")
            return False, "Server is offline or unreachable"
        except Timeout:
            logger.error("Server request timed out: Server is not responding")
            return False, "Server is not responding (timeout)"
        except Exception as e:
            logger.error(f"Unexpected error during server check: {str(e)}")
            return False, f"Error checking server status: {str(e)}"

    async def authenticate(self) -> bool:
        """Authenticate with server and get token"""
        if self.auth_retry_count >= self.max_auth_retries:
            msg = "Maximum authentication attempts reached. Stopping client."
            logger.error(msg)
            print_status("Authentication", msg, "ERROR")
            self.running = False
            return False

        try:
            logger.info(
                f"Attempting authentication for client {self.client_id}")
            print_status("Authentication",
                         "Attempting to authenticate with server", "INFO")

            # Check server status first
            is_online, status_msg = await self.check_server_status()
            if not is_online:
                logger.error(f"Authentication failed: {status_msg}")
                print_status("Authentication",
                             f"Failed: {status_msg}", "ERROR")
                self.auth_retry_count += 1
                return False

            response = requests.post(
                f"{self.server_url}/auth",
                json={
                    "client_id": self.client_id,
                    "password": self.password
                },
                timeout=10
            )

            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.reconnect_attempts = 0
                self.auth_retry_count = 0
                logger.info("Authentication successful")
                print_status(
                    "Authentication", "Successfully authenticated with server", "SUCCESS")
                return True
            elif response.status_code == 401:
                msg = "Authentication failed: Invalid credentials"
                logger.error(msg)
                print_status("Authentication", msg, "ERROR")
                self.running = False
                return False
            else:
                logger.error(
                    f"Authentication failed with status {response.status_code}: {response.text}")
                print_status("Authentication",
                             f"Failed: {response.text}", "ERROR")
                self.auth_retry_count += 1
                return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            print_status("Authentication", f"Error: {str(e)}", "ERROR")
            self.auth_retry_count += 1
            return False

    def get_retry_delay(self, attempt: int) -> int:
        """Implement exponential backoff for retry delays"""
        return min(self.base_retry_delay * (2 ** attempt), 60)  # Max delay of 60 seconds

    async def connect(self) -> bool:
        """Connect to WebSocket server with authentication"""
        try:
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                msg = "Maximum reconnection attempts reached. Requiring re-authentication."
                logger.error(msg)
                print_status("Connection", msg, "ERROR")
                self.token = None
                self.auth_required = True
                self.reconnect_attempts = 0
                return False

            if not self.token:
                msg = "No valid token available. Authentication required."
                logger.error(msg)
                print_status("Connection", msg, "ERROR")
                self.auth_required = True
                return False

            logger.info(f"Attempting WebSocket connection to {self.ws_url}")
            print_status(
                "Connection", "Attempting to connect to server", "INFO")

            self.ws = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )

            # Send authentication token
            auth_message = json.dumps({"token": self.token})
            await self.ws.send(auth_message)
            logger.debug("Authentication token sent")

            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=5)
                logger.info(
                    f"Server response after authentication: {response}")
            except asyncio.TimeoutError:
                logger.warning(
                    "No response after authentication (this might be normal)")

            self.reconnect_attempts = 0
            self.auth_required = False
            logger.info("Successfully connected to server")
            print_status(
                "Connection", "Successfully connected to server", "SUCCESS")
            return True

        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            print_status("Connection", f"Failed: {str(e)}", "ERROR")
            self.reconnect_attempts += 1
            return False

    async def listen(self, callback: Callable[[dict], None]):
        """Listen for data from server"""
        self.running = True
        self.server_check_count = 0  # Reset counter at start

        while self.running:
            try:
                # Check if authentication is needed
                if self.auth_required or not self.token:
                    is_online, status_msg = await self.check_server_status()
                    if not is_online:
                        self.server_check_count += 1
                        if self.server_check_count >= self.max_server_check_retries:
                            logger.error(
                                "Maximum server check attempts reached. Stopping client.")
                            print(
                                "ERROR: Maximum server check attempts reached. Stopping client.")
                            self.running = False
                            return

                        logger.error(f"Server is not available: {status_msg}")
                        print(f"ERROR: Server is not available - {status_msg}")
                        print(
                            f"Retry attempt {self.server_check_count} of {self.max_server_check_retries}")
                        await asyncio.sleep(10)  # Wait before retry
                        continue

                    # Reset server check counter when server is available
                    self.server_check_count = 0

                    if not await self.authenticate():
                        if self.auth_retry_count >= self.max_auth_retries:
                            logger.error(
                                "Maximum authentication attempts reached. Stopping client.")
                            print(
                                "ERROR: Maximum authentication attempts reached. Stopping client.")
                            self.running = False
                            return
                        delay = self.get_retry_delay(self.auth_retry_count)
                        logger.error(
                            f"Authentication failed, retrying in {delay} seconds...")
                        print(
                            f"Authentication failed, retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue

                if not self.ws:
                    if not await self.connect():
                        if self.auth_required:
                            continue
                        delay = self.get_retry_delay(self.reconnect_attempts)
                        logger.info(
                            f"Retrying connection in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue

                while self.running and self.ws:
                    try:
                        message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                        data = json.loads(message)
                        logger.debug(
                            f"Received data: {data}, data type: {type(data)}")
                        print(
                            f"Print - from wall_api_client, Received data: {data}, data type: {type(data)}")
                        await self.handle_message(callback, data)
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        logger.error("Invalid message format")
                        continue
                    except Exception as e:
                        if "service restart" in str(e) or "4001" in str(e):
                            self.auth_required = True
                            self.ws = None
                            logger.warning(
                                "Authentication required. Reconnecting...")
                            break
                        else:
                            logger.error(f"Error processing message: {e}")
                            break

            except ConnectionClosed as e:
                if not self.running:
                    return
                if e.code in [1012, 4001]:  # Service Restart or Auth Error
                    self.auth_required = True
                    self.ws = None
                    logger.warning("Server requires re-authentication")
                    await asyncio.sleep(5)
                else:
                    logger.warning(f"Connection closed ({e.code}): {e.reason}")
                    self.ws = None
                    await self.handle_connection_closed(e)

            except Exception as e:
                if not self.running:
                    return
                logger.error(f"Unexpected error: {e}")
                self.ws = None
                await asyncio.sleep(self.get_retry_delay(self.reconnect_attempts))

    async def handle_message(self, callback: Callable[[dict], None], data: dict):
        """Handle incoming messages with error handling"""
        try:
            logger.debug(f"Processing received message: {data}")
            callback(data)
            logger.debug("Message processed successfully")
        except Exception as e:
            logger.error(f"Error in message handler: {str(e)}")
            print_status("Message Handler",
                         f"Error processing message: {str(e)}", "ERROR")

    async def handle_connection_closed(self, e: ConnectionClosed):
        """Handle different connection closed scenarios"""
        if e.code == 1000:  # Normal closure
            logger.info("Connection closed normally")
        elif e.code == 4001:  # Authentication error
            logger.error("Authentication failed, clearing token")
            self.token = None
        elif e.code == 4000:  # Server error
            logger.error("Server error, will retry connection")
        elif e.code == 1012:  # Service restart
            logger.warning("Server is restarting")
            print("Server is restarting. Will attempt to reconnect...")
        else:
            logger.warning(f"Connection closed with code {e.code}")

        delay = self.get_retry_delay(self.reconnect_attempts)
        await asyncio.sleep(delay)

    async def close(self):
        """Gracefully close the connection"""
        logger.info("Initiating graceful shutdown")
        print_status("Shutdown", "Initiating graceful shutdown", "INFO")
        self.running = False

        if self.ws:
            try:
                await self.ws.close()
                logger.info("WebSocket connection closed gracefully")
                print_status(
                    "Shutdown", "Connection closed gracefully", "SUCCESS")
            except Exception as e:
                logger.error(f"Error during connection closure: {str(e)}")
                print_status(
                    "Shutdown", f"Error closing connection: {str(e)}", "ERROR")

        logger.info("Shutdown complete")
        print_status("Shutdown", "Complete", "SUCCESS")

    def stop(self):
        """Stop listening and close connection"""
        self.running = False
        if self.ws:
            logger.info("Closing connection...")
            asyncio.create_task(self.close())
