"""configuration management for ups-pi system"""

import os
import configparser
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field

from .power_manager import PowerManagerConfig


class ConfigError(Exception):
    """configuration error"""
    pass


@dataclass
class UPSConfig:
    """main configuration for ups-pi system"""
    
    # Default configuration file locations
    DEFAULT_CONFIG_PATHS = [
        "/etc/ups-pi/config.ini",
        "/usr/local/etc/ups-pi/config.ini",
        "config/config.ini",
        "config.ini"
    ]
    
    # Configuration data
    power_manager: PowerManagerConfig = field(default_factory=PowerManagerConfig)
    
    @classmethod
    def load(
        cls, 
        config_file: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ) -> 'UPSConfig':
        """
        Load configuration from file and environment variables.
        
        Args:
            config_file: Specific config file path (optional)
            logger: Logger instance for messages
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigError: If configuration is invalid
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        
        config = cls()
        
        # Load from config file
        config_path = config._find_config_file(config_file, logger)
        if config_path:
            config._load_from_file(config_path, logger)
        else:
            logger.info("No config file found, using defaults")
        
        # Override with environment variables
        config._load_from_environment(logger)
        
        # Validate configuration
        config._validate(logger)
        
        logger.info("Configuration loaded successfully")
        return config
    
    def _find_config_file(
        self, 
        config_file: Optional[str],
        logger: logging.Logger
    ) -> Optional[Path]:
        """Find the configuration file to use."""
        
        # Use specified file if provided
        if config_file:
            path = Path(config_file)
            if path.exists():
                logger.info(f"Using specified config file: {path}")
                return path
            else:
                raise ConfigError(f"Specified config file not found: {config_file}")
        
        # Search default locations
        for config_path in self.DEFAULT_CONFIG_PATHS:
            path = Path(config_path)
            if path.exists():
                logger.info(f"Found config file: {path}")
                return path
        
        return None
    
    def _load_from_file(self, config_path: Path, logger: logging.Logger) -> None:
        """Load configuration from INI file."""
        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)
            
            # UART settings
            if parser.has_section('uart'):
                uart_section = parser['uart']
                self.power_manager.uart_port = uart_section.get(
                    'port', self.power_manager.uart_port
                )
                self.power_manager.uart_baudrate = uart_section.getint(
                    'baudrate', self.power_manager.uart_baudrate
                )
                self.power_manager.uart_timeout = uart_section.getfloat(
                    'timeout', self.power_manager.uart_timeout
                )
            
            # Monitoring settings
            if parser.has_section('monitoring'):
                monitor_section = parser['monitoring']
                self.power_manager.monitor_interval = monitor_section.getfloat(
                    'interval', self.power_manager.monitor_interval
                )
                self.power_manager.communication_retries = monitor_section.getint(
                    'retries', self.power_manager.communication_retries
                )
                self.power_manager.max_consecutive_failures = monitor_section.getint(
                    'max_failures', self.power_manager.max_consecutive_failures
                )
            
            # Shutdown settings
            if parser.has_section('shutdown'):
                shutdown_section = parser['shutdown']
                self.power_manager.shutdown_delay = shutdown_section.getint(
                    'delay', self.power_manager.shutdown_delay
                )
                self.power_manager.critical_battery_threshold = shutdown_section.getint(
                    'critical_threshold', self.power_manager.critical_battery_threshold
                )
                self.power_manager.low_battery_threshold = shutdown_section.getint(
                    'low_threshold', self.power_manager.low_battery_threshold
                )
                self.power_manager.enable_shutdown = shutdown_section.getboolean(
                    'enable', self.power_manager.enable_shutdown
                )
                self.power_manager.require_confirmation = shutdown_section.getboolean(
                    'require_confirmation', self.power_manager.require_confirmation
                )
            
            # GPIO settings
            if parser.has_section('gpio'):
                gpio_section = parser['gpio']
                self.power_manager.enable_gpio = gpio_section.getboolean(
                    'enable', self.power_manager.enable_gpio
                )
                self.power_manager.shutdown_pin = gpio_section.getint(
                    'shutdown_pin', self.power_manager.shutdown_pin
                )
                
                led_pin = gpio_section.get('status_led_pin', '').strip()
                if led_pin and led_pin.isdigit():
                    self.power_manager.status_led_pin = int(led_pin)
                else:
                    self.power_manager.status_led_pin = None
            
            # Logging settings
            if parser.has_section('logging'):
                log_section = parser['logging']
                self.power_manager.log_level = log_section.get(
                    'level', self.power_manager.log_level
                ).upper()
                
                log_file = log_section.get('file', '').strip()
                if log_file:
                    self.power_manager.log_file = log_file
                else:
                    self.power_manager.log_file = None
                
                self.power_manager.log_max_size = log_section.getint(
                    'max_size', self.power_manager.log_max_size
                )
                self.power_manager.log_backup_count = log_section.getint(
                    'backup_count', self.power_manager.log_backup_count
                )
            
            logger.debug(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to load config from {config_path}: {e}")
    
    def _load_from_environment(self, logger: logging.Logger) -> None:
        """Load configuration from environment variables."""
        env_vars_found = []
        
        # UART settings
        if 'UPS_UART_PORT' in os.environ:
            self.power_manager.uart_port = os.environ['UPS_UART_PORT']
            env_vars_found.append('UPS_UART_PORT')
        
        if 'UPS_UART_BAUDRATE' in os.environ:
            try:
                self.power_manager.uart_baudrate = int(os.environ['UPS_UART_BAUDRATE'])
                env_vars_found.append('UPS_UART_BAUDRATE')
            except ValueError:
                logger.warning(f"Invalid UPS_UART_BAUDRATE: {os.environ['UPS_UART_BAUDRATE']}")
        
        if 'UPS_UART_TIMEOUT' in os.environ:
            try:
                self.power_manager.uart_timeout = float(os.environ['UPS_UART_TIMEOUT'])
                env_vars_found.append('UPS_UART_TIMEOUT')
            except ValueError:
                logger.warning(f"Invalid UPS_UART_TIMEOUT: {os.environ['UPS_UART_TIMEOUT']}")
        
        # Monitoring settings
        if 'UPS_MONITOR_INTERVAL' in os.environ:
            try:
                self.power_manager.monitor_interval = float(os.environ['UPS_MONITOR_INTERVAL'])
                env_vars_found.append('UPS_MONITOR_INTERVAL')
            except ValueError:
                logger.warning(f"Invalid UPS_MONITOR_INTERVAL: {os.environ['UPS_MONITOR_INTERVAL']}")
        
        if 'UPS_COMMUNICATION_RETRIES' in os.environ:
            try:
                self.power_manager.communication_retries = int(os.environ['UPS_COMMUNICATION_RETRIES'])
                env_vars_found.append('UPS_COMMUNICATION_RETRIES')
            except ValueError:
                logger.warning(f"Invalid UPS_COMMUNICATION_RETRIES: {os.environ['UPS_COMMUNICATION_RETRIES']}")
        
        # Shutdown settings
        if 'UPS_SHUTDOWN_DELAY' in os.environ:
            try:
                self.power_manager.shutdown_delay = int(os.environ['UPS_SHUTDOWN_DELAY'])
                env_vars_found.append('UPS_SHUTDOWN_DELAY')
            except ValueError:
                logger.warning(f"Invalid UPS_SHUTDOWN_DELAY: {os.environ['UPS_SHUTDOWN_DELAY']}")
        
        if 'UPS_CRITICAL_BATTERY' in os.environ:
            try:
                self.power_manager.critical_battery_threshold = int(os.environ['UPS_CRITICAL_BATTERY'])
                env_vars_found.append('UPS_CRITICAL_BATTERY')
            except ValueError:
                logger.warning(f"Invalid UPS_CRITICAL_BATTERY: {os.environ['UPS_CRITICAL_BATTERY']}")
        
        if 'UPS_LOW_BATTERY' in os.environ:
            try:
                self.power_manager.low_battery_threshold = int(os.environ['UPS_LOW_BATTERY'])
                env_vars_found.append('UPS_LOW_BATTERY')
            except ValueError:
                logger.warning(f"Invalid UPS_LOW_BATTERY: {os.environ['UPS_LOW_BATTERY']}")
        
        if 'UPS_ENABLE_SHUTDOWN' in os.environ:
            self.power_manager.enable_shutdown = os.environ['UPS_ENABLE_SHUTDOWN'].lower() in ['true', '1', 'yes', 'on']
            env_vars_found.append('UPS_ENABLE_SHUTDOWN')
        
        # GPIO settings
        if 'UPS_ENABLE_GPIO' in os.environ:
            self.power_manager.enable_gpio = os.environ['UPS_ENABLE_GPIO'].lower() in ['true', '1', 'yes', 'on']
            env_vars_found.append('UPS_ENABLE_GPIO')
        
        if 'UPS_SHUTDOWN_PIN' in os.environ:
            try:
                self.power_manager.shutdown_pin = int(os.environ['UPS_SHUTDOWN_PIN'])
                env_vars_found.append('UPS_SHUTDOWN_PIN')
            except ValueError:
                logger.warning(f"Invalid UPS_SHUTDOWN_PIN: {os.environ['UPS_SHUTDOWN_PIN']}")
        
        if 'UPS_STATUS_LED_PIN' in os.environ:
            try:
                pin_value = os.environ['UPS_STATUS_LED_PIN'].strip()
                if pin_value and pin_value.isdigit():
                    self.power_manager.status_led_pin = int(pin_value)
                else:
                    self.power_manager.status_led_pin = None
                env_vars_found.append('UPS_STATUS_LED_PIN')
            except ValueError:
                logger.warning(f"Invalid UPS_STATUS_LED_PIN: {os.environ['UPS_STATUS_LED_PIN']}")
        
        # Logging settings
        if 'UPS_LOG_LEVEL' in os.environ:
            self.power_manager.log_level = os.environ['UPS_LOG_LEVEL'].upper()
            env_vars_found.append('UPS_LOG_LEVEL')
        
        if 'UPS_LOG_FILE' in os.environ:
            log_file = os.environ['UPS_LOG_FILE'].strip()
            if log_file:
                self.power_manager.log_file = log_file
            else:
                self.power_manager.log_file = None
            env_vars_found.append('UPS_LOG_FILE')
        
        if env_vars_found:
            logger.debug(f"Environment variables loaded: {', '.join(env_vars_found)}")
    
    def _validate(self, logger: logging.Logger) -> None:
        """Validate configuration values."""
        errors = []
        
        # Validate UART settings
        if not self.power_manager.uart_port:
            errors.append("UART port cannot be empty")
        
        if self.power_manager.uart_baudrate <= 0:
            errors.append(f"Invalid UART baudrate: {self.power_manager.uart_baudrate}")
        
        if self.power_manager.uart_timeout <= 0:
            errors.append(f"Invalid UART timeout: {self.power_manager.uart_timeout}")
        
        # Validate monitoring settings
        if self.power_manager.monitor_interval <= 0:
            errors.append(f"Invalid monitor interval: {self.power_manager.monitor_interval}")
        
        if self.power_manager.communication_retries < 0:
            errors.append(f"Invalid communication retries: {self.power_manager.communication_retries}")
        
        if self.power_manager.max_consecutive_failures <= 0:
            errors.append(f"Invalid max consecutive failures: {self.power_manager.max_consecutive_failures}")
        
        # Validate shutdown settings
        if self.power_manager.shutdown_delay < 0:
            errors.append(f"Invalid shutdown delay: {self.power_manager.shutdown_delay}")
        
        if not 0 <= self.power_manager.critical_battery_threshold <= 100:
            errors.append(f"Invalid critical battery threshold: {self.power_manager.critical_battery_threshold}")
        
        if not 0 <= self.power_manager.low_battery_threshold <= 100:
            errors.append(f"Invalid low battery threshold: {self.power_manager.low_battery_threshold}")
        
        if self.power_manager.critical_battery_threshold > self.power_manager.low_battery_threshold:
            errors.append("Critical battery threshold cannot be higher than low battery threshold")
        
        # Validate GPIO settings
        if self.power_manager.enable_gpio:
            if not 0 <= self.power_manager.shutdown_pin <= 40:
                errors.append(f"Invalid shutdown pin: {self.power_manager.shutdown_pin}")
            
            if (self.power_manager.status_led_pin is not None and 
                not 0 <= self.power_manager.status_led_pin <= 40):
                errors.append(f"Invalid status LED pin: {self.power_manager.status_led_pin}")
        
        # Validate logging settings
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.power_manager.log_level not in valid_log_levels:
            errors.append(f"Invalid log level: {self.power_manager.log_level}")
        
        if self.power_manager.log_max_size <= 0:
            errors.append(f"Invalid log max size: {self.power_manager.log_max_size}")
        
        if self.power_manager.log_backup_count < 0:
            errors.append(f"Invalid log backup count: {self.power_manager.log_backup_count}")
        
        # Report validation errors
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ConfigError(error_msg)
        
        logger.debug("Configuration validation passed")
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save configuration file
        """
        parser = configparser.ConfigParser()
        
        # UART section
        parser.add_section('uart')
        parser.set('uart', 'port', self.power_manager.uart_port)
        parser.set('uart', 'baudrate', str(self.power_manager.uart_baudrate))
        parser.set('uart', 'timeout', str(self.power_manager.uart_timeout))
        
        # Monitoring section
        parser.add_section('monitoring')
        parser.set('monitoring', 'interval', str(self.power_manager.monitor_interval))
        parser.set('monitoring', 'retries', str(self.power_manager.communication_retries))
        parser.set('monitoring', 'max_failures', str(self.power_manager.max_consecutive_failures))
        
        # Shutdown section
        parser.add_section('shutdown')
        parser.set('shutdown', 'delay', str(self.power_manager.shutdown_delay))
        parser.set('shutdown', 'critical_threshold', str(self.power_manager.critical_battery_threshold))
        parser.set('shutdown', 'low_threshold', str(self.power_manager.low_battery_threshold))
        parser.set('shutdown', 'enable', str(self.power_manager.enable_shutdown))
        parser.set('shutdown', 'require_confirmation', str(self.power_manager.require_confirmation))
        
        # GPIO section
        parser.add_section('gpio')
        parser.set('gpio', 'enable', str(self.power_manager.enable_gpio))
        parser.set('gpio', 'shutdown_pin', str(self.power_manager.shutdown_pin))
        parser.set('gpio', 'status_led_pin', str(self.power_manager.status_led_pin or ''))
        
        # Logging section
        parser.add_section('logging')
        parser.set('logging', 'level', self.power_manager.log_level)
        parser.set('logging', 'file', self.power_manager.log_file or '')
        parser.set('logging', 'max_size', str(self.power_manager.log_max_size))
        parser.set('logging', 'backup_count', str(self.power_manager.log_backup_count))
        
        # Create directory if needed
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write configuration
        with open(config_path, 'w') as f:
            parser.write(f)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'uart': {
                'port': self.power_manager.uart_port,
                'baudrate': self.power_manager.uart_baudrate,
                'timeout': self.power_manager.uart_timeout,
            },
            'monitoring': {
                'interval': self.power_manager.monitor_interval,
                'retries': self.power_manager.communication_retries,
                'max_failures': self.power_manager.max_consecutive_failures,
            },
            'shutdown': {
                'delay': self.power_manager.shutdown_delay,
                'critical_threshold': self.power_manager.critical_battery_threshold,
                'low_threshold': self.power_manager.low_battery_threshold,
                'enable': self.power_manager.enable_shutdown,
                'require_confirmation': self.power_manager.require_confirmation,
            },
            'gpio': {
                'enable': self.power_manager.enable_gpio,
                'shutdown_pin': self.power_manager.shutdown_pin,
                'status_led_pin': self.power_manager.status_led_pin,
            },
            'logging': {
                'level': self.power_manager.log_level,
                'file': self.power_manager.log_file,
                'max_size': self.power_manager.log_max_size,
                'backup_count': self.power_manager.log_backup_count,
            }
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        lines = []
        for section, settings in config_dict.items():
            lines.append(f"[{section}]")
            for key, value in settings.items():
                lines.append(f"  {key} = {value}")
            lines.append("")
        return "\n".join(lines)
