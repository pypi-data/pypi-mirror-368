"""production uart-based ups power management for raspberry pi"""

from .ups_communication import UPSDevice, UPSStatus, UPSCommunicationError, UPSDataError
from .power_manager import PowerManager, PowerState, PowerManagerConfig
from .config import UPSConfig, ConfigError

__version__ = "2.0.1"
__all__ = [
    "UPSDevice",
    "UPSStatus", 
    "UPSCommunicationError",
    "UPSDataError",
    "PowerManager",
    "PowerState",
    "PowerManagerConfig", 
    "UPSConfig",
    "ConfigError",
]
__author__ = "UPS-Pi Development Team"
__license__ = "MIT"

# Core module imports
try:
    from .ups_communication import UPSDevice
    from .power_manager import PowerManager, PowerState  
    from .config import UPSConfig
    
    __all__ = [
        "UPSDevice",
        "PowerManager", 
        "PowerState",
        "UPSConfig",
    ]
except ImportError:
    # Allow imports to fail during development
    __all__ = []
