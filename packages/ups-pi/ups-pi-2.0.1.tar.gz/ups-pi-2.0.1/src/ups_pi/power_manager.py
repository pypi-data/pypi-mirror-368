"""power management for raspberry pi using upspack v3"""

import logging
import os
import sys
import time
import threading
import signal
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from contextlib import contextmanager

try:
    import RPi.GPIO as GPIO  # type: ignore
    GPIO_AVAILABLE = True
except ImportError:
    GPIO = None
    GPIO_AVAILABLE = False

from .ups_communication import UPSDevice, UPSStatus, UPSCommunicationError


class PowerState(Enum):
    """power states for ups system"""
    EXTERNAL_POWER = "external"
    BATTERY_POWER = "battery"
    CRITICAL_BATTERY = "critical"
    UNKNOWN = "unknown"


@dataclass
class PowerManagerConfig:
    """power management configuration"""
    
    # UART Communication Settings
    uart_port: str = "/dev/ttyAMA0"
    uart_baudrate: int = 9600
    uart_timeout: float = 2.0
    
    # Monitoring Settings
    monitor_interval: float = 5.0  # seconds between status checks
    communication_retries: int = 3
    max_consecutive_failures: int = 5
    
    # Shutdown Settings
    shutdown_delay: int = 30  # seconds delay before shutdown on battery
    critical_battery_threshold: int = 5  # percentage for immediate shutdown
    low_battery_threshold: int = 20  # percentage for warnings
    
    # GPIO Settings (optional)
    enable_gpio: bool = False
    shutdown_pin: int = 18  # GPIO pin for shutdown signal
    status_led_pin: Optional[int] = None  # GPIO pin for status LED
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = None  # will use fallback logic
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # Safety Settings
    enable_shutdown: bool = True  # Allow automatic shutdown
    require_confirmation: bool = False  # Require user confirmation for shutdown


class PowerManager:
    """main power management system"""
    
    def __init__(self, config: PowerManagerConfig):
        """initialize power manager"""
        self.config = config
        self.current_state = PowerState.UNKNOWN
        self.previous_state = PowerState.UNKNOWN
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize UPS device
        self.ups_device = UPSDevice(
            port=config.uart_port,
            baudrate=config.uart_baudrate,
            timeout=config.uart_timeout,
            logger=self.logger
        )
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread = None
        self._gpio_monitor_thread = None
        self._shutdown_timer = None
        self._consecutive_failures = 0
        self._last_status = None
        
        # Event callbacks
        self._state_change_callbacks: Dict[PowerState, Callable] = {}
        
        # GPIO setup
        if config.enable_gpio and GPIO_AVAILABLE:
            self._setup_gpio()
        elif config.enable_gpio and not GPIO_AVAILABLE:
            self.logger.warning("GPIO requested but RPi.GPIO not available")
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.logger.info("Power Manager initialized")
    
    def __enter__(self) -> 'PowerManager':
        """context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """context manager exit"""
        self.stop()
    
    def _setup_logging(self) -> logging.Logger:
        """setup logging configuration"""
        logger = logging.getLogger("ups-pi")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with fallback locations
        log_file = self.config.log_file
        if not log_file:
            # Try multiple fallback locations
            fallback_paths = [
                "/var/log/ups-pi/power_events.log",
                f"{Path.home()}/.local/share/ups-pi/power_events.log",
                f"{Path.home()}/ups-pi.log",
                "./ups-pi.log"
            ]
            
            for path_str in fallback_paths:
                try:
                    path = Path(path_str)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # Test write permission
                    test_file = path.parent / "test_write"
                    test_file.touch()
                    test_file.unlink()
                    log_file = str(path)
                    break
                except (PermissionError, OSError):
                    continue
        
        if log_file:
            try:
                # Create log directory if needed
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=self.config.log_max_size,
                    backupCount=self.config.log_backup_count
                )
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                logger.info(f"File logging enabled: {log_file}")
                
            except Exception as e:
                # Fall back to console only
                logger.warning(f"Failed to setup file logging: {e}")
        
        return logger
    
    def _setup_gpio(self) -> None:
        """setup gpio pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Shutdown pin (input with pull-down to match original script behavior)
            GPIO.setup(self.config.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Status LED pin (output)
            if self.config.status_led_pin:
                GPIO.setup(self.config.status_led_pin, GPIO.OUT)
                GPIO.output(self.config.status_led_pin, GPIO.LOW)
            
            self.logger.info("GPIO initialized successfully")
            
        except Exception as e:
            self.logger.error(f"GPIO setup failed: {e}")
            self.config.enable_gpio = False
    
    def _signal_handler(self, signum: int, frame) -> None:
        """handle system signals for graceful shutdown"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received signal {signal_name}, shutting down gracefully")
        self.stop()
    
    def start(self) -> None:
        """start power monitoring"""
        if self._monitoring:
            self.logger.warning("Power monitoring already running")
            return
        
        try:
            self.logger.info("Starting power monitoring")
            
            # Connect to UPS device
            self.ups_device.open()
            
            # Start monitoring thread
            self._monitoring = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                name="ups-monitor",
                daemon=True
            )
            self._monitor_thread.start()
            
            # Start GPIO monitoring thread if enabled
            if self.config.enable_gpio and GPIO_AVAILABLE:
                self._gpio_monitor_thread = threading.Thread(
                    target=self._gpio_shutdown_monitor,
                    name="gpio-monitor", 
                    daemon=True
                )
                self._gpio_monitor_thread.start()
                self.logger.info("GPIO monitoring started")
            
            self.logger.info("Power monitoring started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start power monitoring: {e}")
            self._monitoring = False
            raise
    
    def stop(self) -> None:
        """stop power monitoring"""
        if not self._monitoring:
            return
        
        self.logger.info("Stopping power monitoring")
        self._monitoring = False
        
        # Cancel shutdown timer if running
        if self._shutdown_timer:
            self._shutdown_timer.cancel()
            self._shutdown_timer = None
        
        # Wait for monitor threads to finish
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
            
        if self._gpio_monitor_thread and self._gpio_monitor_thread.is_alive():
            self._gpio_monitor_thread.join(timeout=5.0)
        
        # Close UPS connection
        self.ups_device.close()
        
        # Cleanup GPIO
        if self.config.enable_gpio and GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception as e:
                self.logger.warning(f"GPIO cleanup error: {e}")
        
        self.logger.info("Power monitoring stopped")
    
    def run(self) -> None:
        """run power monitoring (blocking)"""
        try:
            self.start()
            
            # Keep main thread alive
            while self._monitoring:
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Power monitoring error: {e}")
        finally:
            self.stop()
    
    def _monitor_loop(self) -> None:
        """main monitoring loop"""
        self.logger.info("Power monitoring loop started")
        
        while self._monitoring:
            try:
                # Read UPS status
                status = self.ups_device.read_status(
                    retries=self.config.communication_retries
                )
                
                # Reset failure counter on successful read
                self._consecutive_failures = 0
                self._last_status = status
                
                # Process status update
                self._process_status_update(status)
                
                # Update GPIO status LED
                if self.config.enable_gpio and self.config.status_led_pin:
                    self._update_status_led(status)
                
            except UPSCommunicationError as e:
                self._handle_communication_error(e)
            except Exception as e:
                self.logger.error(f"Unexpected error in monitoring loop: {e}")
                self._consecutive_failures += 1
            
            # Check for excessive failures
            if self._consecutive_failures >= self.config.max_consecutive_failures:
                self.logger.critical(
                    f"Too many consecutive failures ({self._consecutive_failures}), "
                    "stopping monitoring"
                )
                break
            
            # Sleep until next check
            time.sleep(self.config.monitor_interval)
        
        self.logger.info("Power monitoring loop ended")
    
    def _process_status_update(self, status: UPSStatus) -> None:
        """process ups status update"""
        # Determine current power state
        new_state = self._determine_power_state(status)
        
        # Check for state change
        if new_state != self.current_state:
            self._handle_state_change(self.current_state, new_state, status)
        
        # Log status periodically
        self.logger.debug(
            f"UPS Status - Power: {status.power_status}, "
            f"Battery: {status.battery_percentage}%, "
            f"Voltage: {status.voltage_mv}mV"
        )
    
    def _determine_power_state(self, status: UPSStatus) -> PowerState:
        """determine power state from ups status"""
        if status.power_status.lower() in ['external', 'charging']:
            return PowerState.EXTERNAL_POWER
        elif status.battery_percentage <= self.config.critical_battery_threshold:
            return PowerState.CRITICAL_BATTERY
        elif status.power_status.lower() == 'battery':
            return PowerState.BATTERY_POWER
        else:
            return PowerState.UNKNOWN
    
    def _handle_state_change(
        self, 
        old_state: PowerState, 
        new_state: PowerState, 
        status: UPSStatus
    ) -> None:
        """handle power state transitions"""
        self.previous_state = old_state
        self.current_state = new_state
        
        self.logger.info(
            f"Power state changed: {old_state.value} → {new_state.value} "
            f"(Battery: {status.battery_percentage}%)"
        )
        
        # Execute state-specific actions
        if new_state == PowerState.BATTERY_POWER:
            self._handle_battery_power(status)
        elif new_state == PowerState.CRITICAL_BATTERY:
            self._handle_critical_battery(status)
        elif new_state == PowerState.EXTERNAL_POWER:
            self._handle_external_power(status)
        
        # Call registered callbacks
        if new_state in self._state_change_callbacks:
            try:
                self._state_change_callbacks[new_state](status)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")
    
    def _handle_battery_power(self, status: UPSStatus) -> None:
        """handle transition to battery power"""
        self.logger.warning(
            f"System running on battery power (Battery: {status.battery_percentage}%)"
        )
        
        # Cancel any existing shutdown timer
        if self._shutdown_timer:
            self._shutdown_timer.cancel()
        
        # Schedule shutdown if enabled
        if self.config.enable_shutdown and self.config.shutdown_delay > 0:
            self.logger.info(f"Scheduling shutdown in {self.config.shutdown_delay} seconds")
            self._shutdown_timer = threading.Timer(
                self.config.shutdown_delay,
                self._initiate_shutdown
            )
            self._shutdown_timer.start()
    
    def _handle_critical_battery(self, status: UPSStatus) -> None:
        """handle critical battery level"""
        self.logger.critical(
            f"CRITICAL BATTERY LEVEL: {status.battery_percentage}% - "
            "Initiating immediate shutdown"
        )
        
        # Cancel any existing timer and shutdown immediately
        if self._shutdown_timer:
            self._shutdown_timer.cancel()
        
        if self.config.enable_shutdown:
            self._initiate_shutdown()
    
    def _handle_external_power(self, status: UPSStatus) -> None:
        """handle return to external power"""
        self.logger.info(
            f"External power restored (Battery: {status.battery_percentage}%)"
        )
        
        # Cancel any pending shutdown
        if self._shutdown_timer:
            self.logger.info("Cancelling scheduled shutdown - power restored")
            self._shutdown_timer.cancel()
            self._shutdown_timer = None
    
    def _handle_communication_error(self, error: UPSCommunicationError) -> None:
        """handle ups communication errors"""
        self._consecutive_failures += 1
        
        if self._consecutive_failures == 1:
            self.logger.warning(f"UPS communication error: {error}")
        else:
            self.logger.error(
                f"UPS communication error ({self._consecutive_failures} consecutive): {error}"
            )
        
        # Set unknown state on communication failure
        if self.current_state != PowerState.UNKNOWN:
            self.current_state = PowerState.UNKNOWN
    
    def _update_status_led(self, status: UPSStatus) -> None:
        """update status led based on power state"""
        if not GPIO_AVAILABLE or not self.config.status_led_pin:
            return
        
        try:
            # LED patterns based on state
            if self.current_state == PowerState.EXTERNAL_POWER:
                GPIO.output(self.config.status_led_pin, GPIO.HIGH)  # Solid on
            elif self.current_state == PowerState.BATTERY_POWER:
                # Blink slowly
                current_time = time.time()
                led_state = int(current_time) % 2
                GPIO.output(self.config.status_led_pin, led_state)
            elif self.current_state == PowerState.CRITICAL_BATTERY:
                # Blink rapidly
                current_time = time.time()
                led_state = int(current_time * 4) % 2
                GPIO.output(self.config.status_led_pin, led_state)
            else:  # UNKNOWN
                GPIO.output(self.config.status_led_pin, GPIO.LOW)  # Off
                
        except Exception as e:
            self.logger.warning(f"Status LED update error: {e}")
    
    def _gpio_shutdown_monitor(self) -> None:
        """GPIO shutdown monitoring thread - based on original script logic"""
        if not GPIO_AVAILABLE or not self.config.enable_gpio:
            return
            
        self.logger.info("GPIO shutdown monitoring started")
        
        # Log startup time
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.logger.info(f"GPIO monitor start time: {cur_time}")
        
        try:
            while self._monitoring:
                try:
                    # Wait for rising edge on shutdown pin
                    GPIO.wait_for_edge(self.config.shutdown_pin, GPIO.RISING, timeout=1000)
                    
                    if not self._monitoring:
                        break
                    
                    # Small delay to debounce
                    time.sleep(0.01)
                    
                    # Count how long the pin stays high (pulse duration)
                    pulse_time = 1
                    while GPIO.input(self.config.shutdown_pin) == GPIO.HIGH and self._monitoring:
                        time.sleep(0.01)
                        pulse_time += 1
                        
                        # Safety timeout to prevent infinite loop
                        if pulse_time > 1000:  # 10 seconds max
                            break
                    
                    # Check if we got the expected pulse duration (2-3 * 10ms = 20-30ms)
                    if 2 <= pulse_time <= 3:
                        self.logger.critical("GPIO shutdown signal detected - initiating shutdown")
                        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        self.logger.critical(f"GPIO shutdown time: {cur_time}")
                        
                        # Initiate shutdown
                        self._initiate_shutdown()
                        break
                    else:
                        self.logger.debug(f"GPIO pulse detected but wrong duration: {pulse_time} (expected 2-3)")
                        
                except Exception as e:
                    if self._monitoring:
                        self.logger.error(f"GPIO monitoring error: {e}")
                        time.sleep(1)  # Brief pause before retrying
                    
        except Exception as e:
            self.logger.error(f"GPIO shutdown monitor failed: {e}")
        finally:
            self.logger.info("GPIO shutdown monitoring stopped")
    
    def _initiate_shutdown(self) -> None:
        """initiate system shutdown"""
        if not self.config.enable_shutdown:
            self.logger.warning("Shutdown requested but disabled in configuration")
            return
        
        self.logger.critical("Initiating system shutdown due to UPS battery power")
        
        try:
            # Stop monitoring
            self._monitoring = False
            
            # Execute shutdown command - use single reliable method
            shutdown_methods = [
                # Use systemctl poweroff with -i flag to ignore dependencies
                ["sudo", "systemctl", "poweroff", "-i"]
            ]
            
            shutdown_success = False
            for shutdown_cmd in shutdown_methods:
                try:
                    if self.config.require_confirmation:
                        self.logger.info("Shutdown confirmation required")
                        # In a real implementation, this might check for user input
                        # For now, we'll proceed with shutdown
                    
                    self.logger.info(f"Attempting shutdown: {' '.join(shutdown_cmd)}")
                    result = subprocess.run(shutdown_cmd, check=True, timeout=10)
                    self.logger.info("Shutdown command executed successfully")
                    shutdown_success = True
                    break
                    
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Shutdown method failed: {' '.join(shutdown_cmd)} - {e}")
                    continue
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Shutdown command timed out: {' '.join(shutdown_cmd)}")
                    continue
                except FileNotFoundError:
                    self.logger.warning(f"Shutdown command not found: {' '.join(shutdown_cmd)}")
                    continue
            
            if not shutdown_success:
                self.logger.error("All shutdown methods failed - manual intervention required")
                # As a last resort, try to signal the system
                try:
                    os.system("sync")  # Sync filesystem
                    self.logger.error("Filesystem synced - system may need manual shutdown")
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
    
    # Public API methods
    
    def get_current_status(self) -> Optional[UPSStatus]:
        """get the most recent ups status"""
        return self._last_status
    
    def get_current_state(self) -> PowerState:
        """get current power management state"""
        return self.current_state
    
    def register_state_callback(
        self, 
        state: PowerState, 
        callback: Callable[[UPSStatus], None]
    ) -> None:
        """register callback for power state changes"""
        self._state_change_callbacks[state] = callback
    
    def force_shutdown(self) -> None:
        """force immediate system shutdown"""
        self.logger.warning("Forced shutdown requested")
        self._initiate_shutdown()
    
    def cancel_shutdown(self) -> None:
        """cancel any pending shutdown"""
        if self._shutdown_timer:
            self.logger.info("Shutdown cancelled by user request")
            self._shutdown_timer.cancel()
            self._shutdown_timer = None
        else:
            self.logger.info("No pending shutdown to cancel")
