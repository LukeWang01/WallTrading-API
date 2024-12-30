import websockets
from websockets.exceptions import ConnectionClosed
# noinspection PyUnresolvedReferences
from websockets.exceptions import InvalidMessage, InvalidStatusCode
import asyncio
import json
import requests
from typing import Callable, Optional, Tuple
import os
from requests.exceptions import RequestException, ConnectionError, Timeout
import time

from utils.logger_config import setup_logger

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
        self.max_retry_delay = 300  # Maximum delay (5 minutes)
        self.retry_count = 0  # Track retry attempts
        self.max_retries = 10  # Maximum number of retries before giving up
        self.max_auth_retries = 3
        self.auth_retry_count = 0
        self.auth_required = False  # New flag to track if re-auth is needed
        self.max_server_check_retries = 5  # New attribute for server check retries
        self.server_check_count = 0  # New counter for server checks
        self.ping_interval = 30  # Increase ping interval (seconds)
        self.ping_timeout = 10   # Ping timeout (seconds)
        self.heartbeat_failed_count = 0
        self.max_heartbeat_failures = 3
        self.last_ping_time = 0  # Track last successful ping time
        # Time to wait before starting health checks
        self.connection_stabilization_time = 5
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

    def get_retry_delay(self) -> int:
        """Calculate exponential backoff delay"""
        # Exponential backoff: base_delay * 2^retry_count
        delay = min(
            self.base_retry_delay * (2 ** self.retry_count),
            self.max_retry_delay
        )
        logger.info(f"Retry attempt {self.retry_count + 1}, delay: {delay}s")
        print_status("Connection",
                     f"Retry attempt {self.retry_count + 1} of {self.max_retries}, waiting {delay}s",
                     "INFO")
        return delay

    async def connect(self) -> bool:
        """Connect to WebSocket server with authentication"""
        try:
            if self.retry_count >= self.max_retries:
                msg = "Maximum reconnection attempts reached. Requiring re-authentication."
                logger.error(msg)
                print_status("Connection", msg, "ERROR")
                self.token = None
                self.auth_required = True
                self.retry_count = 0
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
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=10,
                max_size=2**23,
                user_agent_header="DataClient/1.0"
            )

            # Send authentication token
            auth_message = json.dumps({"token": self.token})
            await self.ws.send(auth_message)
            logger.debug("Authentication token sent")

            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=5)
                response_data = json.loads(response)

                # Check if server indicates token expiry
                if isinstance(response_data, dict) and response_data.get('error') == 'token_expired':
                    logger.warning(
                        "Token expired, requiring re-authentication")
                    self.token = None
                    self.auth_required = True
                    return False

                logger.info(
                    f"Server response after authentication: {response}")
                self.heartbeat_failed_count = 0
                self.last_ping_time = time.time()
            except asyncio.TimeoutError:
                logger.warning(
                    "No response after authentication (this might be normal)")
            except json.JSONDecodeError:
                logger.warning("Invalid response format from server")

            await asyncio.sleep(self.connection_stabilization_time)
            self.retry_count = 0
            self.auth_required = False
            logger.info("Successfully connected to server")
            print_status(
                "Connection", "Successfully connected to server", "SUCCESS")
            return True

        except Exception as e:
            error_msg = str(e)
            if "4000" in error_msg or "private use" in error_msg:
                logger.warning(
                    "Server indicated authentication issue, will re-authenticate")
                self.token = None
                self.auth_required = True
                return False

            logger.error(f"Connection failed: {error_msg}")
            print_status("Connection", f"Failed: {error_msg}", "ERROR")
            self.retry_count += 1
            return False

    async def check_connection_health(self) -> bool:
        """Check if the connection is healthy using ping"""
        current_time = time.time()

        # Skip health check if we haven't waited long enough since connection
        if current_time - self.last_ping_time < self.connection_stabilization_time:
            return True

        try:
            if self.ws:  # Simply check if ws exists
                try:
                    pong_waiter = await self.ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=self.ping_timeout)
                    self.heartbeat_failed_count = 0
                    self.last_ping_time = current_time
                    return True
                except Exception as e:
                    self.heartbeat_failed_count += 1
                    if self.heartbeat_failed_count >= self.max_heartbeat_failures:
                        logger.warning(
                            f"Multiple heartbeat failures detected ({self.heartbeat_failed_count} failures)")
                        return False
                    # Log intermediate failures but don't disconnect yet
                    logger.debug(
                        f"Heartbeat check failed ({self.heartbeat_failed_count}/{self.max_heartbeat_failures})")
            return True
        except Exception as e:
            logger.error(f"Connection check error: {str(e)}")
            return False

    def should_log_error(self, error_msg: str) -> bool:
        """Rate limit error logging"""
        current_time = time.time()
        if (current_time - self.last_error_time) >= self.error_log_interval:
            self.last_error_time = current_time
            return True
        return False

    async def listen(self, callback: Callable[[dict], None]):
        """Listen for data from server"""
        self.running = True
        self.server_check_count = 0

        while self.running:
            try:
                # Check if authentication is needed
                if self.auth_required or not self.token:
                    logger.info("Re-authentication required")
                    is_online, status_msg = await self.check_server_status()
                    if not is_online:
                        self.server_check_count += 1
                        if self.server_check_count >= self.max_server_check_retries:
                            logger.error(
                                "Maximum server check attempts reached. Stopping client.")
                            print_status("Client",
                                         "Maximum server check attempts reached. Stopping client.",
                                         "ERROR")
                            self.running = False
                            return

                        logger.error(f"Server is not available: {status_msg}")
                        print_status("Server Check",
                                     f"Server not available: {status_msg}",
                                     "ERROR")
                        await asyncio.sleep(self.get_retry_delay())
                        continue

                    # Reset counters when server is available
                    self.server_check_count = 0
                    self.retry_count = 0  # Reset retry count for fresh authentication

                    if not await self.authenticate():
                        if self.auth_retry_count >= self.max_auth_retries:
                            logger.error(
                                "Maximum authentication attempts reached. Stopping client.")
                            print_status("Authentication",
                                         "Maximum attempts reached. Stopping client.",
                                         "ERROR")
                            self.running = False
                            return
                        await asyncio.sleep(self.get_retry_delay())
                        continue

                if not self.ws:
                    if not await self.connect():
                        if self.auth_required:
                            continue
                        await asyncio.sleep(self.get_retry_delay())
                        continue

                while self.running and self.ws:
                    try:
                        # Periodically check connection health
                        if not await self.check_connection_health():
                            logger.warning(
                                "Connection health check failed, reconnecting...")
                            try:
                                await self.ws.close(code=1001)  # Going away
                            except Exception:
                                pass  # Ignore errors during close
                            self.ws = None
                            self.heartbeat_failed_count = 0  # Reset counter
                            break

                        try:
                            message = await asyncio.wait_for(
                                self.ws.recv(),
                                timeout=self.ping_interval
                            )

                            # Reset heartbeat counter on successful message receipt
                            self.heartbeat_failed_count = 0
                            self.last_ping_time = time.time()

                            data = json.loads(message)
                            await self.handle_message(callback, data)

                        except asyncio.TimeoutError:
                            continue
                        except json.JSONDecodeError:
                            logger.error("Invalid message format")
                            continue
                        except Exception as e:
                            if "ping timeout" in str(e).lower() or "keepalive" in str(e).lower():
                                self.ws = None
                                break
                            logger.error(f"Error processing message: {e}")
                            continue

                    except Exception as e:
                        logger.error(f"Connection loop error: {str(e)}")
                        self.ws = None
                        break

            except ConnectionClosed as e:
                if not self.running:
                    return
                if self.should_log_error(f"Connection closed ({e.code})"):
                    logger.warning(f"Connection closed ({e.code}): {e.reason}")
                await self.handle_connection_closed(e)

            except Exception as e:
                if not self.running:
                    return
                if self.should_log_error(str(e)):
                    logger.error(f"Unexpected error: {e}")
                self.ws = None
                await asyncio.sleep(self.get_retry_delay())

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
        if e.code == 4000:  # Private use (usually auth issues)
            logger.warning("Server indicated authentication issue")
            self.token = None
            self.auth_required = True
            self.retry_count = 0  # Reset retry count for re-auth
            return
        elif e.code == 1001:  # Going away
            logger.info("Connection closing due to health check failure")
            self.retry_count += 1
        elif e.code == 1011:  # Internal error (usually ping timeout)
            logger.warning(
                "Connection ping timeout, will attempt to reconnect")
            self.retry_count += 1
            self.ws = None
            await asyncio.sleep(self.get_retry_delay())
            return
        elif e.code == 1000:  # Normal closure
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

        await asyncio.sleep(self.get_retry_delay())

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
