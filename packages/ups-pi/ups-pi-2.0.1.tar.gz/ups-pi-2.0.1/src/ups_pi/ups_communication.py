"""uart communication with upspack v3 devices"""

import time
import logging
import re
from typing import Tuple, Optional, Any, Union, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass

try:
    import serial
    from serial import Serial
    SERIAL_AVAILABLE = True
except ImportError:
    serial = None  # type: ignore
    Serial = None  # type: ignore
    SERIAL_AVAILABLE = False


class UPSCommunicationError(Exception):
    """ups communication failure"""
    pass


class UPSDataError(Exception):
    """invalid ups data"""
    pass


@dataclass
class UPSStatus:
    """ups status data"""
    firmware_version: str
    power_status: str
    battery_percentage: int
    voltage_mv: int
    raw_data: str
    timestamp: float


class UPSDevice:
    """uart communication with ups device"""
    
    # UART communication constants
    DEFAULT_PORT = "/dev/ttyAMA0"
    DEFAULT_BAUDRATE = 9600
    DEFAULT_TIMEOUT = 2.0
    
    # Data validation patterns
    FIRMWARE_PATTERN = re.compile(r'^[A-Za-z0-9._\-\s\$]+$')  # Allow spaces, $ symbol
    STATUS_PATTERN = re.compile(r'^(External|Battery|Charging|Unknown)$')
    
    def __init__(
        self,
        port: str = DEFAULT_PORT,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        logger: Optional[logging.Logger] = None
    ):
        """initialize ups communication"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        
        self._serial_connection = None
        self._is_open = False
        
        if not SERIAL_AVAILABLE:
            raise UPSCommunicationError(
                "pyserial library not available. Install with: pip install pyserial"
            )
    
    def __enter__(self) -> 'UPSDevice':
        """context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """context manager exit"""
        self.close()
    
    def open(self) -> None:
        """open serial connection"""
        if self._is_open:
            self.logger.warning("UPS connection already open")
            return
        
        try:
            self.logger.info(f"Opening UPS connection: {self.port} @ {self.baudrate} baud")
            
            self._serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            if not self._serial_connection.is_open:
                raise UPSCommunicationError("Failed to open serial connection")
            
            self._is_open = True
            self.logger.info("UPS connection established successfully")
            
            self._serial_connection.reset_input_buffer()
            self._serial_connection.reset_output_buffer()
            
        except serial.SerialException as e:
            raise UPSCommunicationError(f"Serial connection failed: {e}")
        except Exception as e:
            raise UPSCommunicationError(f"Unexpected error opening connection: {e}")
    
    def close(self) -> None:
        """close serial connection"""
        if not self._is_open:
            return
        
        try:
            if self._serial_connection and self._serial_connection.is_open:
                self._serial_connection.close()
                self.logger.info("UPS connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
        finally:
            self._serial_connection = None
            self._is_open = False
    
    def is_connected(self) -> bool:
        """check if device is connected"""
        return (
            self._is_open and 
            self._serial_connection is not None and 
            self._serial_connection.is_open
        )
    
    def read_status(self, retries: int = 3) -> UPSStatus:
        """read current ups status"""
        if not self.is_connected():
            raise UPSCommunicationError("UPS device not connected")
        
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                self.logger.debug(f"Reading UPS status (attempt {attempt + 1})")
                
                self._serial_connection.reset_input_buffer()
                raw_data = self._serial_connection.readline()
                
                if not raw_data:
                    self.logger.debug("No data received from UPS - retrying")
                    if attempt < retries:
                        time.sleep(0.1)
                        continue
                    raise UPSCommunicationError("No data received from UPS after retries")
                
                data_str = raw_data.decode('utf-8', errors='ignore').strip()
                
                if not data_str:
                    self.logger.debug("Empty data received - retrying")
                    if attempt < retries:
                        time.sleep(0.1)
                        continue
                    raise UPSDataError("Empty data received after retries")
                
                # Skip if data is too short to be valid UPS data
                if len(data_str) < 10:
                    self.logger.debug(f"Data too short: '{data_str}' - retrying")
                    if attempt < retries:
                        time.sleep(0.1)
                        continue
                    raise UPSDataError(f"Data too short: '{data_str}' after retries")
                
                status = self._parse_status_data(data_str)
                self.logger.debug(f"UPS status read successfully: {status}")
                return status
                
            except (UPSCommunicationError, UPSDataError) as e:
                last_error = e
                if attempt < retries:
                    # Log partial data as debug, communication errors as warning
                    if "Invalid data format" in str(e) or "Empty firmware field" in str(e) or "Data too short" in str(e):
                        self.logger.debug(f"UPS read attempt {attempt + 1} - partial data: {e}")
                    else:
                        self.logger.warning(f"UPS read attempt {attempt + 1} failed: {e}")
                    time.sleep(0.1)
                    continue
                break
            except Exception as e:
                last_error = UPSCommunicationError(f"Unexpected error: {e}")
                break
        
        error_msg = f"Failed to read UPS status after {retries + 1} attempts"
        if last_error:
            error_msg += f": {last_error}"
        
        self.logger.error(error_msg)
        raise UPSCommunicationError(error_msg)
    
    def _parse_status_data(self, data: str) -> UPSStatus:
        """parse raw ups data string"""
        try:
            self.logger.debug(f"Parsing UPS data: '{data}' (length: {len(data)})")
            
            # Handle original UPSPack format: $ SmartUPS V3.2P, Vin GOOD, BATCAP 100, Vout 5000 $
            # Extract content between $ markers
            pattern = r'\$ (.*?) \$'
            matches = re.findall(pattern, data, re.S)
            
            if not matches:
                # Fallback to comma-separated format
                return self._parse_csv_format(data)
            
            content = matches[0]
            
            # Extract firmware version: SmartUPS V3.2P
            firmware_pattern = r'SmartUPS (.*?),'
            firmware_matches = re.findall(firmware_pattern, content)
            firmware = f"SmartUPS {firmware_matches[0]}" if firmware_matches else "Unknown"
            
            # Extract input voltage status: Vin GOOD/NG
            vin_pattern = r',Vin (.*?),'
            vin_matches = re.findall(vin_pattern, content)
            vin_status = vin_matches[0] if vin_matches else "Unknown"
            
            # Map input status to power status
            if vin_status == "GOOD":
                status = "External"
            elif vin_status == "NG":
                status = "Battery" 
            else:
                status = "Unknown"
            
            # Extract battery capacity: BATCAP 100
            batcap_pattern = r'BATCAP (.*?),'
            batcap_matches = re.findall(batcap_pattern, content)
            if batcap_matches:
                battery_percentage = int(batcap_matches[0])
            else:
                raise UPSDataError("Battery capacity not found")
            
            # Extract output voltage: Vout 5000
            vout_pattern = r',Vout (.*)'
            vout_matches = re.findall(vout_pattern, content)
            if vout_matches:
                voltage_mv = int(vout_matches[0])
            else:
                raise UPSDataError("Output voltage not found")
            
            return UPSStatus(
                firmware_version=firmware,
                power_status=status,
                battery_percentage=battery_percentage,
                voltage_mv=voltage_mv,
                raw_data=data,
                timestamp=time.time()
            )
            
        except UPSDataError:
            raise
        except Exception as e:
            raise UPSDataError(f"Failed to parse UPS data '{data}': {e}")
    
    def _parse_csv_format(self, data: str) -> UPSStatus:
        """fallback parser for comma-separated format"""
        try:
            parts = data.split(',')
            
            # Handle incomplete data gracefully
            if len(parts) < 2:
                raise UPSDataError(f"Insufficient data: '{data}' (got {len(parts)} parts)")
            
            if len(parts) != 4:
                raise UPSDataError(f"Invalid data format: expected 4 parts, got {len(parts)}")
            
            firmware, status, battery_str, voltage_str = parts
            
            firmware = firmware.strip()
            if not firmware:
                raise UPSDataError("Empty firmware field")
            if not self.FIRMWARE_PATTERN.match(firmware):
                raise UPSDataError(f"Invalid firmware format: '{firmware}'")
            
            status = status.strip()
            if not self.STATUS_PATTERN.match(status):
                status_lower = status.lower()
                if 'ext' in status_lower or 'ac' in status_lower:
                    status = "External"
                elif 'bat' in status_lower:
                    status = "Battery"
                elif 'charg' in status_lower:
                    status = "Charging"
                else:
                    status = "Unknown"
            
            try:
                battery_str_clean = battery_str.strip().rstrip('%')
                # Handle formats like "BATCAP 100" or "100"
                if ' ' in battery_str_clean:
                    # Extract number from "BATCAP 100" format
                    parts = battery_str_clean.split()
                    battery_str_clean = parts[-1]  # Take the last part (the number)
                
                battery_percentage = int(battery_str_clean)
                if not 0 <= battery_percentage <= 100:
                    raise ValueError("Battery percentage out of range")
            except ValueError as e:
                raise UPSDataError(f"Invalid battery percentage: {battery_str}")
            
            # Parse voltage
            try:
                voltage_mv = int(voltage_str.strip())
                if voltage_mv < 0:
                    raise ValueError("Negative voltage")
            except ValueError as e:
                raise UPSDataError(f"Invalid voltage: {voltage_str}")
            
            return UPSStatus(
                firmware_version=firmware,
                power_status=status,
                battery_percentage=battery_percentage,
                voltage_mv=voltage_mv,
                raw_data=data,
                timestamp=time.time()
            )
            
        except UPSDataError:
            raise
        except Exception as e:
            raise UPSDataError(f"Failed to parse UPS data '{data}': {e}")


# Legacy compatibility - maintain interface from original ups2.py
class UPS2(UPSDevice):
    """Legacy compatibility class - use UPSDevice instead."""
    
    def __init__(self, port: str = "/dev/ttyAMA0", **kwargs):
        super().__init__(port=port, **kwargs)
        self.logger.warning("UPS2 class is deprecated, use UPSDevice instead")
    
    def decode_uart(self) -> Tuple[str, str, int, int]:
        """Legacy method - returns tuple format."""
        if not self.is_connected():
            self.open()
        
        status = self.read_status()
        return (
            status.firmware_version,
            status.power_status,
            status.battery_percentage,
            status.voltage_mv
        )
