from typing import List, Optional, Callable
import logging


class PCP_over_USB:
    """
    PCP (Pulsar Communication Protocol) adapter for USB connections.

    This class provides USB serial communication for the PCP protocol, sending messages,
    receiving incoming messages in a thread for asynchronous communication
    """

    def __init__(self, port: Optional[str] = None, connect_on_init: bool = True, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize PCP over USB communication adapter.
        
        Args:
            port: Serial port name (e.g., 'COM3', '/dev/ttyACM0'). If None, auto-discovery is attempted.
            connect_on_init: Whether to automatically connect during initialization
            logger: Optional logger for debugging messages
        """
        ...

    def connect(self, port: Optional[str] = None) -> bool:
        """
        Establish a connection to the device.

        Args:
            port (str, optional): Serial port name. If None, uses previously set port or auto-discovery.
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        ...

    def disconnect(self) -> None:
        """
        Disconnect from the USB serial port and stop background threads.
        
        Cleanly shuts down the polling thread and closes the serial connection.
        """
        ...

    def close(self) -> None:
        """
        Alias for disconnect() method.
        
        Provided for compatibility and explicit resource cleanup.
        """
        ...

    def setCallback(self, address: int, callback: Callable[[int, List[int]], None]) -> None:
        """
        Register a callback function for messages from a specific PCP address.
        
        Args:
            address: PCP address to listen for (0x0001-0x3FFE)
            callback: Function to call when messages are received from this address.
                     Callback signature: callback(address: int, data: List[int])
        """
        ...

    def removeCallback(self, address: int) -> None:
        """
        Unregister the callback function for a specific PCP address.

        Args:
            address: PCP address to stop listening for (0x0001-0x3FFE)
        """
        ...

    def send_PCP(self, address: int, data: List[int]) -> bool:
        """
        Send a PCP message to the specified address.
        
        Args:
            address: Target PCP address (0x0001-0x3FFE)
            data: List of bytes to send as message payload
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        ...

    @staticmethod
    def get_ports() -> List[str]:
        """
        Get list of available USB serial ports from Pulsar HRI devices.

        Automatically filters serial ports to only include those manufactured
        by Pulsar HRI, which are compatible with PCP over USB.
        
        Returns:
            List of serial port names/paths (e.g., ['COM3', 'COM5'] on Windows
            or ['/dev/ttyACM0', '/dev/ttyACM1'] on Linux)
        """
        ...

    @staticmethod
    def get_port() -> str:
        """
        Auto-discover a single USB serial port for PCP communication.
        
        Attempts to automatically find a suitable serial port. If exactly one
        Pulsar HRI port is found, returns it. Otherwise, returns empty string.
        
        Returns:
            Serial port name if exactly one suitable port is found, empty string otherwise
        """
        ...

    @property
    def is_connected(self) -> bool:
        """
        Check if the USB connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        ...
