from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional


class PulsarActuator:
    """
    Main class for controlling Pulsar actuators via PCP (Pulsar Control Protocol).
    
    This class provides high-level methods to control actuator modes, setpoints,
    feedback configuration, and parameter management.
    """

    class Mode(Enum):
        """Control modes available for the Pulsar actuator."""
        TORQUE = 0x05
        SPEED = 0x06
        POSITION = 0x07
        IMPEDANCE = 0x08
        # These modes are only for testing purposes
        FVI = 0x02
        OPEN_LOOP = 0x03
        DVI = 0x04         # Field oriented voltage injection

    class Rates(Enum):
        """Feedback update rates for high/low frequency data streams."""
        DISABLED = 0       # Feedback disabled
        RATE_1KHZ = 10     # 1kHz update rate (1000 Hz)
        RATE_100HZ = 100
        RATE_50HZ = 200
        RATE_10HZ = 1_000
        RATE_5HZ = 2_000
        RATE_2HZ = 5_000
        RATE_1HZ = 10_000

    class TorquePerformance(Enum):
        """Performance settings for torque control mode."""
        AGGRESSIVE = 1     # Fast, responsive torque control
        BALANCED = 2       # Balanced torque control
        SOFT = 3          # Smooth, gentle torque control

    class SpeedPerformance(Enum):
        """Performance settings for speed control mode."""
        AGGRESSIVE = 1     # Fast, responsive speed control
        BALANCED = 2       # Balanced speed control
        SOFT = 3          # Smooth, gentle speed control
        CUSTOM = 4        # Custom speed control parameters

    class PCP_Parameters(Enum):
        """Available parameters that can be read/written on the actuator."""
        K_DAMPING = 0x01              # Damping coefficient (Nm·s/rad) for the virtual damper behavior (Impedance Control)
        K_STIFFNESS = 0x02            # Stiffness coefficient (Nm/rad) for the virtual spring behavior (Impedance Control)
        TORQUE_FF = 0x03              # Feedforward Torque Value (Nm)
        LIM_TORQUE = 0x04             # Upper and lower bounds for how much torque can be applied in the positive and negative directions. (Nm)
        LIM_POSITION_MAX = 0x05       # Max. Position Limit (rad)
        LIM_POSITION_MIN = 0x06       # Min. Position Limit (rad)
        LIM_SPEED_MAX = 0x07          # Max. Speed Limit (rad/s)
        LIM_SPEED_MIN = 0x08          # Min. Speed Limit (rad/s)
        PROFILE_POSITION_MAX = 0x09   # Max. Positive Speed (rad/s) in Position control configuration
        PROFILE_POSITION_MIN = 0x0A   # Min. Negative Speed (rad/s) in Position control configuration
        PROFILE_SPEED_MAX = 0x0B      # Max. Acceleration (rad/s^2) in Speed control configuration
        PROFILE_SPEED_MIN = 0x0C      # Max. Deceleration (rad/s^2) in Speed control configuration
        KP_SPEED = 0x0D               # Kp speed control constant P value
        KI_SPEED = 0x0E               # Ki speed control constant I value
        KP_POSITION = 0x0F            # Kp position control constant P value
        MODE = 0x30                   # Operation Mode (read-only, must be set via CHANGE_MODE)
        SETPOINT = 0x31               # Setpoint, Position (rad), Speed (rad/s), Torque (Nm)
        TORQUE_PERFORMANCE = 0x40     # Torque performance setting
        SPEED_PERFORMANCE = 0x41      # Speed performance setting
        PROFILE_SPEED_MAX_RAD_S = 0x42    # Maximum profile speed in rad/s
        PROFILE_TORQUE_MAX_NM = 0x43      # Maximum profile torque in Nm
        FIRMWARE_VERSION = 0x80       # Firmware version (read-only)
        PCP_ADDRESS = 0x81            # device PCP address
        SERIAL_NUMBER = 0x82          # Device serial number (read-only)
        DEVICE_MODEL = 0x83           # Device model identifier (read-only)
        CONTROL_VERSION = 0x84        # Control software version (read-only)

    class PCP_Items(Enum):
        """Feedback items available for monitoring actuator state."""
        ENCODER_INT = 0x41            # Internal encoder position
        ENCODER_INT_RAW = 0x42        # Raw internal encoder counts
        ENCODER_EXT = 0x43            # External encoder position
        ENCODER_EXT_RAW = 0x44        # Raw external encoder counts
        SPEED_FB = 0x45               # Speed feedback
        IA = 0x46                     # Phase A current
        IB = 0x47                     # Phase B current
        IC = 0x48                     # Phase C current
        TORQUE_SENS = 0x49            # Torque sensor reading
        TORQUE_SENS_RAW = 0x4A        # Raw torque sensor reading
        POSITION_REF = 0x4B           # Position reference/command
        POSITION_FB = 0x4C            # Position feedback
        SPEED_REF = 0x4D              # Speed reference/command
        ID_REF = 0x4F                 # D-axis current reference
        ID_FB = 0x50                  # D-axis current feedback
        IQ_REF = 0x51                 # Q-axis current reference
        IQ_FB = 0x52                  # Q-axis current feedback
        VD_REF = 0x53                 # D-axis voltage reference
        VQ_REF = 0x54                 # Q-axis voltage reference
        TORQUE_REF = 0x55             # Torque reference/command
        TORQUE_FB = 0x56              # Torque feedback
        ERRORS_ENCODER_INT = 0x60     # Internal encoder error flags
        ERRORS_ENCODER_EXT = 0x61     # External encoder error flags
        ERRORS_OVERRUN = 0x62         # Control loop overrun errors
        VBUS = 0x70                   # Bus voltage
        TEMP_PCB = 0x71               # PCB temperature
        TEMP_MOTOR = 0x72             # Motor temperature

    def __init__(self, adapter_handler: Any, address: int, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize a PulsarActuator instance.
        
        Args:
            adapter_handler: Communication adapter for PCP protocol
            address: PCP network address of the actuator (0x0001-0x3FFE)
            logger: Optional logger for debugging messages
        """
        ...

    def connect(self, timeout: float = 1.0) -> bool:
        """
        Establish connection to the actuator.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        ...

    def set_feedback_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Set callback function to receive feedback data.
        
        Args:
            callback: Function to call when feedback data is received
        """
        ...

    def disconnect(self) -> None:
        """Disconnect from the actuator and clean up resources."""
        ...

    def get_feedback(self) -> Dict[Any, Any]:
        """
        Get the latest feedback data.
        
        Returns:
            Dictionary containing latest feedback values
        """
        ...

    def send_ping(self, timeout: float = 1.0) -> bool:
        """
        Send ping to verify actuator connectivity.
        
        Args:
            timeout: Response timeout in seconds
            
        Returns:
            True if ping successful, False otherwise
        """
        ...

    def changeAddress(self, new_address: int) -> None:
        """
        Change the PCP address of the actuator.
        
        Args:
            new_address: New PCP address (0x10 - 0x3FFE)
        """
        ...

    def start(self) -> None:
        """Enable the actuator control system."""
        ...

    def stop(self) -> None:
        """Disable the actuator control system."""
        ...

    def change_mode(self, mode: 'PulsarActuator.Mode') -> None:
        """
        Change the actuator control mode.
        
        Args:
            mode (PulsarActuator.Mode): The mode to be set.  (TORQUE, SPEED, POSITION, ...)
        """
        ...

    def change_setpoint(self, setpoint: float) -> None:
        """
        Set the control setpoint for the current mode.
        
        Args:
            setpoint: Target value (units depend on current mode)
                     - Torque mode: Nm
                     - Speed mode: rad/s
                     - Position mode: rad
                     - Impedance mode: rad
        """
        ...

    def save_config(self) -> None:
        """Save current configuration to non-volatile memory."""
        ...

    def setHighFreqFeedbackItems(self, items: List['PulsarActuator.PCP_Items']) -> None:
        """
        Configure which items to include in high frequency feedback stream.
        
        Args:
            items: List of PCP_Items to monitor at high frequency
        """
        ...

    def setHighFreqFeedbackRate(self, rate: 'PulsarActuator.Rates') -> None:
        """
        Set the update rate for high frequency feedback.
        
        Args:
            rate: Desired update rate from Rates enum
        """
        ...

    def setLowFreqFeedbackItems(self, items: List['PulsarActuator.PCP_Items']) -> None:
        """
        Configure which items to include in low frequency feedback stream.
        
        Args:
            items: List of PCP_Items to monitor at low frequency
        """
        ...

    def setLowFreqFeedbackRate(self, rate: 'PulsarActuator.Rates') -> None:
        """
        Set the update rate for low frequency feedback.
        
        Args:
            rate: Desired update rate from Rates enum
        """
        ...

    def set_home_position(self) -> None:
        """Sets the current position as the home position (zero reference)."""
        ...

    def set_parameters(self, parameters: Dict['PulsarActuator.PCP_Parameters', float]) -> None:
        """
        Set multiple actuator parameters.
        
        Args:
            parameters: Dictionary mapping PCP_Parameters to their values
        """
        ...

    def get_parameters(self, parameters: List['PulsarActuator.PCP_Parameters'], timeout: float = 1.0) -> Dict['PulsarActuator.PCP_Parameters', float]:
        """
        Read multiple actuator parameters.
        
        Args:
            parameters: List of parameters to read
            timeout: Response timeout in seconds
            
        Returns:
            Dictionary mapping parameters to their current values
        """
        ...

    def get_parameters_all(self) -> Dict['PulsarActuator.PCP_Parameters', float]:
        """
        Read all available actuator parameters.
        
        Returns:
            Dictionary containing all parameter values
        """
        ...

    def set_torque_performance(self, performance: 'PulsarActuator.TorquePerformance') -> None:
        """
        Set torque control performance level.
        
        Args:
            performance: Desired performance setting (AGGRESSIVE, BALANCED, or SOFT)
        """
        ...

    def set_speed_performance(self, performance: 'PulsarActuator.SpeedPerformance') -> None:
        """
        Set speed control performance level.
        
        Args:
            performance: Desired performance setting (AGGRESSIVE, BALANCED, SOFT, or CUSTOM)
        """
        ...


class PulsarActuatorScanner(PulsarActuator):
    """
    Scanner class for discovering Pulsar actuators on the PCP network.
    
    Inherits from PulsarActuator but uses broadcast address for scanning operations.
    """

    def __init__(self, adapter_handler: Any, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize a PulsarActuatorScanner instance.
        
        Args:
            adapter_handler: Communication adapter for PCP protocol
            logger: Optional logger for debugging messages
        """
        ...

    def scan(self, begin: int = 0x10, end: int = 0x3FFE) -> List[int]:
        """
        Scan for actuators within the specified address range.
        
        Args:
            begin: Starting address for scan (default: 0x10)
            end: Ending address for scan (default: 0x3FFE)

        Returns:
            List of discovered actuator addresses
        """
        ...
