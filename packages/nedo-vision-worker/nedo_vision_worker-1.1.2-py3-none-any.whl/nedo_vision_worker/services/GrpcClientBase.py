import grpc
import logging
import time
from grpc import StatusCode

logger = logging.getLogger(__name__)

# Global callback for authentication failures
_auth_failure_callback = None

def set_auth_failure_callback(callback):
    """Set a global callback to be called when authentication failures occur."""
    global _auth_failure_callback
    _auth_failure_callback = callback

def _notify_auth_failure():
    """Notify the registered callback about authentication failure."""
    global _auth_failure_callback
    if _auth_failure_callback:
        _auth_failure_callback()

class GrpcClientBase:
    def __init__(self, server_host: str, server_port: int = 50051, max_retries: int = 3):
        """
        Initialize the gRPC client base.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
            max_retries (int): Maximum number of reconnection attempts.
        """
        self.server_address = f"{server_host}:{server_port}"
        self.channel = None
        self.stub = None
        self.connected = False
        self.max_retries = max_retries

    def connect(self, stub_class, retry_interval: int = 2):
        """
        Create a gRPC channel and stub, with retry logic if the server is unavailable.

        Args:
            stub_class: The gRPC stub class for the service.
            retry_interval (int): Initial time in seconds between reconnection attempts.
        """
        attempts = 0
        while attempts < self.max_retries and not self.connected:
            try:
                self.channel = grpc.insecure_channel(self.server_address)
                future = grpc.channel_ready_future(self.channel)
                try:
                    future.result(timeout=30)
                except grpc.FutureTimeoutError:
                    raise grpc.RpcError("gRPC connection timed out.")

                self.stub = stub_class(self.channel)
                self.connected = True
                logger.info("🚀 [APP] Successfully connected to gRPC server at %s", self.server_address)
                return  # Exit if successful

            except grpc.RpcError as e:
                attempts += 1
                self.connected = False

                error_message = getattr(e, "details", lambda: str(e))()
                logger.error("⚠️ [APP] Failed to connect (%d/%d): %s", attempts, self.max_retries, error_message)

                if attempts < self.max_retries:
                    sleep_time = retry_interval * (2 ** (attempts - 1))  # Exponential backoff
                    logger.info("⏳ [APP] Retrying in %d seconds...", sleep_time)
                    time.sleep(sleep_time)
                else:
                    logger.critical("❌ [APP] Maximum retries reached. Could not connect to gRPC server.")

            except Exception as e:
                logger.critical("🚨 [APP] Unexpected error during gRPC initialization: %s", str(e))
                break  # Stop retrying if an unexpected error occurs

    def close(self):
        """
        Close the gRPC channel.
        """
        if self.channel:
            self.channel.close()
            self.connected = False
            logger.info("🔌 [APP] gRPC channel closed.")

    def handle_rpc(self, rpc_call, *args, **kwargs):
        """
        Handle an RPC call with error handling.

        Args:
            rpc_call: The RPC method to call.
            *args: Positional arguments for the RPC call.
            **kwargs: Keyword arguments for the RPC call.

        Returns:
            The RPC response or None if an error occurs.
        """
        try:
            response = rpc_call(*args, **kwargs)
            return response

        except grpc.RpcError as e:
            status_code = e.code()

            # ✅ Extract only the meaningful part of the error message
            error_message = getattr(e, "details", lambda: str(e))()
            error_clean = error_message.split("debug_error_string")[0].strip()

            self.connected = False  # Mark as disconnected for reconnection

            if status_code == StatusCode.UNAVAILABLE:
                logger.warning("⚠️ [APP] Server unavailable. Attempting to reconnect... (Error: %s)", error_clean)
                self.connect(type(self.stub))  # Attempt to reconnect
            elif status_code == StatusCode.DEADLINE_EXCEEDED:
                logger.error("⏳ [APP] RPC timeout error. (Error: %s)", error_clean)
            elif status_code == StatusCode.PERMISSION_DENIED:
                logger.error("🚫 [APP] RPC call failed: Permission denied. (Error: %s)", error_clean)
            elif status_code == StatusCode.UNAUTHENTICATED:
                logger.error("🔑 [APP] Authentication failed. (Error: %s)", error_clean)
                _notify_auth_failure()  # Notify about authentication failure
            elif status_code == StatusCode.INVALID_ARGUMENT:
                logger.error("⚠️ [APP] Invalid argument in RPC call. (Error: %s)", error_clean)
            elif status_code == StatusCode.NOT_FOUND:
                logger.error("🔍 [APP] Requested resource not found. (Error: %s)", error_clean)
            elif status_code == StatusCode.INTERNAL:
                logger.error("💥 [APP] Internal server error encountered. (Error: %s)", error_clean)
            else:
                logger.error("❌ [APP] Unhandled gRPC error: %s (Code: %s)", error_clean, status_code)

            return None  # Ensure the caller handles the failure

    @staticmethod
    def get_error_message(response):
        """
        Extract only the meaningful part of the error message.

        Args:
            response: The RPC response.

        Returns:
            str: The error message.
        """
        if response and response.get("success"):
            return None
        
        message = response.get("message", "Unknown error") if response else "Unknown error"
        
        # Check for authentication failure in the message
        if message and ("Invalid authentication token" in message or "authentication" in message.lower()):
            logger.error("🔑 [APP] Authentication failure detected in response: %s", message)
            _notify_auth_failure()
        
        return message