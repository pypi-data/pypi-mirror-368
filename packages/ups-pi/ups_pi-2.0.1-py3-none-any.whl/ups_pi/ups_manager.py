"""main ups-pi application"""

import sys
import argparse
import logging
import signal
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from .config import UPSConfig, ConfigError
from .power_manager import PowerManager, PowerState
from .ups_communication import UPSDevice, UPSCommunicationError


def setup_signal_handlers(power_manager: PowerManager) -> None:
    """setup signal handlers for graceful shutdown"""
    def signal_handler(signum: int, frame) -> None:
        signal_name = signal.Signals(signum).name
        print(f"\nReceived signal {signal_name}, shutting down gracefully...")
        power_manager.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def test_ups_communication(config: UPSConfig) -> bool:
    """test ups communication before starting monitoring"""
    logger = logging.getLogger("ups-pi.test")
    
    try:
        logger.info("Testing UPS communication...")
        
        with UPSDevice(
            port=config.power_manager.uart_port,
            baudrate=config.power_manager.uart_baudrate,
            timeout=config.power_manager.uart_timeout,
            logger=logger
        ) as ups:
            status = ups.read_status(retries=3)
            
            logger.info(
                f"UPS Communication Test PASSED:\n"
                f"  Firmware: {status.firmware_version}\n"
                f"  Power Status: {status.power_status}\n"
                f"  Battery: {status.battery_percentage}%\n"
                f"  Voltage: {status.voltage_mv}mV"
            )
            return True
            
    except UPSCommunicationError as e:
        logger.error(f"UPS Communication Test FAILED: {e}")
        return False
    except Exception as e:
        logger.error(f"UPS Communication Test ERROR: {e}")
        return False


def create_status_callback(logger: logging.Logger):
    """create callback function for power state changes"""
    def on_state_change(status):
        logger.info(
            f"Power state changed - Status: {status.power_status}, "
            f"Battery: {status.battery_percentage}%, "
            f"Voltage: {status.voltage_mv}mV"
        )
    return on_state_change


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="UPS-Pi Power Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default configuration
  %(prog)s --config custom.ini      # Use custom config file
  %(prog)s --test-mode              # Test mode (no shutdown)
  %(prog)s --verbose                # Enable debug logging
  %(prog)s --test-communication     # Test UPS communication only

For systemd service configuration, see:
  /etc/systemd/system/ups-pi.service
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Configuration file path (default: search standard locations)'
    )
    
    parser.add_argument(
        '--test-mode', '-t',
        action='store_true',
        help='Test mode - disable actual system shutdown'
    )
    
    parser.add_argument(
        '--test-communication',
        action='store_true',
        help='Test UPS communication and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose (debug) logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='UPS-Pi 2.0.1'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = UPSConfig.load(config_file=args.config)
        
        # Override log level if verbose requested
        if args.verbose:
            config.power_manager.log_level = "DEBUG"
        
        # Disable shutdown in test mode
        if args.test_mode:
            config.power_manager.enable_shutdown = False
            print("TEST MODE: System shutdown disabled")
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to load configuration: {e}", file=sys.stderr)
        return 1
    
    # Test communication only
    if args.test_communication:
        return 0 if test_ups_communication(config) else 1
    
    # Create power manager
    try:
        power_manager = PowerManager(config.power_manager)
        logger = logging.getLogger("ups-pi.main")
        
    except Exception as e:
        print(f"Failed to initialize power manager: {e}", file=sys.stderr)
        return 1
    
    # Setup signal handlers
    setup_signal_handlers(power_manager)
    
    # Test UPS communication before starting
    if not test_ups_communication(config):
        logger.error("UPS communication test failed - check hardware connections")
        return 1
    
    # Register state change callbacks
    state_callback = create_status_callback(logger)
    for state in PowerState:
        power_manager.register_state_callback(state, state_callback)
    
    # Display startup information
    logger.info("UPS-Pi Power Management System starting...")
    logger.info(f"UART Device: {config.power_manager.uart_port}")
    logger.info(f"Monitor Interval: {config.power_manager.monitor_interval}s")
    logger.info(f"Shutdown Delay: {config.power_manager.shutdown_delay}s")
    logger.info(f"Critical Battery: {config.power_manager.critical_battery_threshold}%")
    logger.info(f"GPIO Enabled: {config.power_manager.enable_gpio}")
    logger.info(f"Shutdown Enabled: {config.power_manager.enable_shutdown}")
    
    if args.test_mode:
        logger.warning("RUNNING IN TEST MODE - System shutdown disabled")
    
    # Run power management
    try:
        with power_manager:
            logger.info("Power monitoring started - Press Ctrl+C to stop")
            
            # Run monitoring loop
            power_manager.run()
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Power management error: {e}")
        return 1
    finally:
        logger.info("Power management stopped")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)  # Standard exit code for Ctrl+C
