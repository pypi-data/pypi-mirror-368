# UPS-Pi

UART-based UPS power management for Raspberry Pi4+ using UPSPack v3 devices.

## Features

- **UART Communication**: Direct serial via `/dev/ttyAMA0` (GPIO 14/15)
- **Automated Shutdown**: Configurable battery thresholds and delays
- **Real-time Monitoring**: Continuous UPS status monitoring
- **Systemd Integration**: Optional service installation for production
- **GPIO Support**: Optional status LEDs and hardware signals
- **Comprehensive Logging**: Event logging with rotation

## Installation

### Basic Installation
```bash
pip install ups-pi
```

### With GPIO Support
```bash
pip install ups-pi[gpio]
```

## Quick Start

### Basic Usage
```python
from ups_pi import UPSDevice, PowerManager, PowerManagerConfig

# Monitor UPS status
with UPSDevice() as ups:
    status = ups.read_status()
    print(f"Power: {status.power_status}")
    print(f"Battery: {status.battery_percentage}%")
    print(f"Voltage: {status.voltage_mv}mV")

# Full power management
config = PowerManagerConfig(
    shutdown_delay=60,
    critical_battery_threshold=10
)

with PowerManager(config) as pm:
    pm.start_monitoring()
```

### Command Line
```bash
# Start monitoring (foreground)
ups-pi

# Test UPS communication
ups-pi --test-communication

# Verbose logging
ups-pi --verbose

# Custom config file
ups-pi --config /path/to/config.ini
```

## Hardware Setup

### Connections
Connect UPSPack v3 to Raspberry Pi:
- **UPS TX** → **Pi GPIO 15** (RX)
- **UPS RX** → **Pi GPIO 14** (TX)  
- **UPS GND** → **Pi GND**
- **UPS SHUTDOWN** → **Pi GPIO 18** (optional, for GPIO support)

### Enable UART
Add to `/boot/firmware/config.txt`:
```ini
enable_uart=1
dtoverlay=disable-bt
```

### Shutdown Permissions (Important!)
For automatic shutdown to work, configure passwordless sudo:

```bash
# Add to /etc/sudoers.d/ups-pi (run: sudo visudo -f /etc/sudoers.d/ups-pi)
your-username ALL=(ALL) NOPASSWD: /sbin/shutdown, /sbin/halt, /bin/systemctl poweroff

# Or run as systemd service (recommended)
sudo ups-pi-service install
```

Reboot after changes.

## Service Installation (Optional)

### Install Service
```bash
# Install service files (requires root)
sudo ups-pi-service install

# Create config and log directories
sudo ups-pi-service setup-dirs

# Enable and start service
sudo ups-pi-service enable
```

### Service Management
```bash
# Check status
sudo systemctl status ups-pi

# View logs
sudo journalctl -u ups-pi -f

# Stop service
sudo systemctl stop ups-pi

# Uninstall service
sudo ups-pi-service uninstall
```

## Configuration

### Default Locations
- `/etc/ups-pi/config.ini` (system-wide)
- `~/.config/ups-pi/config.ini` (user-specific)
- `config.ini` (current directory)

### Example Configuration
```ini
[uart]
port = /dev/ttyAMA0
baudrate = 9600
timeout = 2.0

[monitoring]
interval = 5.0
retries = 3

[shutdown]
delay = 30
critical_threshold = 5
enable = true

[gpio]
enable = false
status_led_pin = 18

[logging]
level = INFO
file = /var/log/ups-pi/power_events.log
```

## API Reference

### UPSDevice
```python
from ups_pi import UPSDevice

with UPSDevice(port="/dev/ttyAMA0") as ups:
    status = ups.read_status()
    # status.firmware_version
    # status.power_status ("External", "Battery", "Charging")
    # status.battery_percentage (0-100)
    # status.voltage_mv (millivolts)
```

### PowerManager
```python
from ups_pi import PowerManager, PowerManagerConfig

config = PowerManagerConfig(
    shutdown_delay=60,           # seconds before shutdown
    critical_battery_threshold=5, # immediate shutdown %
    enable_shutdown=True         # allow actual shutdown
)

with PowerManager(config) as pm:
    pm.start_monitoring()
    # Monitoring runs in background thread
```

## Troubleshooting

### UART Issues
```bash
# Check UART status
ls -la /dev/ttyAMA*

# Test UART loopback (connect GPIO 14 to 15)
ups-pi --test-communication
```

### Permissions
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again
```

### Service Issues
```bash
# Check service logs
sudo journalctl -u ups-pi --no-pager

# Test manual run
sudo ups-pi --verbose
```

### Shutdown Issues
```bash
# Test shutdown permissions
sudo shutdown -c  # Cancel any pending shutdown
sudo systemctl poweroff --dry-run

# Configure passwordless shutdown
sudo visudo -f /etc/sudoers.d/ups-pi
# Add: your-username ALL=(ALL) NOPASSWD: /sbin/shutdown, /sbin/halt, /bin/systemctl

# Use systemd service (recommended)
sudo ups-pi-service install
sudo systemctl start ups-pi
```
## License

MIT License - see LICENSE file for details.

## Hardware Compatibility

- **Tested**: UPSPack v3
- **Compatible**: Any UART-based UPS with CSV output format
- **Requirements**: Raspberry Pi with GPIO UART support
   sudo systemctl start ups-pi
   
   # Check status
   sudo systemctl status ups-pi
   ```

## Manual Installation

### 1. Enable UART

Add to `/boot/firmware/config.txt`:
```
enable_uart=1
```

### 2. Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-serial
pip3 install -r requirements.txt
```

### 3. Install UPS-Pi

```bash
# Copy files
sudo mkdir -p /usr/local/bin/ups-pi
sudo cp src/* /usr/local/bin/ups-pi/
sudo chmod +x /usr/local/bin/ups-pi/ups_manager.py

# Install configuration
sudo mkdir -p /etc/ups-pi
sudo cp config/config.ini /etc/ups-pi/

# Install service
sudo cp config/ups-pi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ups-pi
```

### 4. Create Log Directory

```bash
sudo mkdir -p /var/log/ups-pi
sudo chmod 755 /var/log/ups-pi
```

## Configuration

### Configuration File: `/etc/ups-pi/config.ini`

```ini
[uart]
port = /dev/ttyAMA0
baudrate = 9600
timeout = 2.0

[monitoring]
interval = 5.0          # seconds between status checks
retries = 3             # communication retry attempts
max_failures = 5        # max consecutive failures before stopping

[shutdown]
delay = 30              # seconds to wait on battery before shutdown
critical_threshold = 5  # battery % for immediate shutdown
low_threshold = 20      # battery % for low battery warnings
enable = true           # allow automatic shutdown
require_confirmation = false

[gpio]
enable = false          # enable GPIO features
shutdown_pin = 18       # GPIO pin for shutdown signal
status_led_pin =        # GPIO pin for status LED (empty = disabled)

[logging]
level = INFO                               # DEBUG, INFO, WARNING, ERROR, CRITICAL
file = /var/log/ups-pi/power_events.log    # log file path
max_size = 10485760                        # 10MB max log file size
backup_count = 5                           # number of backup log files
```

### Environment Variables

Override configuration with environment variables:

```bash
export UPS_UART_PORT=/dev/ttyAMA0
export UPS_SHUTDOWN_DELAY=60
export UPS_CRITICAL_BATTERY=10
export UPS_ENABLE_GPIO=false
export UPS_LOG_LEVEL=DEBUG
```

## Usage

### Service Management

```bash
# Start/stop service
sudo systemctl start ups-pi
sudo systemctl stop ups-pi

# Enable/disable automatic startup
sudo systemctl enable ups-pi
sudo systemctl disable ups-pi

# Check status and logs
sudo systemctl status ups-pi
sudo journalctl -u ups-pi -f
```

### Interactive Mode

```bash
# Test mode (no actual shutdown)
/usr/local/bin/ups-pi/ups_manager.py --test-mode

# Verbose logging
/usr/local/bin/ups-pi/ups_manager.py --verbose

# Custom configuration
/usr/local/bin/ups-pi/ups_manager.py --config /path/to/config.ini
```

### Testing

```bash
# Test UPS communication
python3 tests/test_device.py

# Test with different device
python3 tests/test_device.py --port /dev/ttyS0

# Performance testing
python3 tests/test_device.py --performance 60

# Multiple test cycles
python3 tests/test_device.py --loop 10
```

## Monitoring and Logs

### Log Files

- **Service logs**: `sudo journalctl -u ups-pi`
- **Application logs**: `/var/log/ups-pi/power_events.log`
- **System logs**: `/var/log/syslog`

### Status Monitoring

```bash
# View real-time logs
sudo tail -f /var/log/ups-pi/power_events.log

# Check current UPS status
/usr/local/bin/ups-pi/ups_manager.py --test-communication

# Monitor systemd service
sudo systemctl status ups-pi
```

## Troubleshooting

### Common Issues

1. **UART device not found**:
   ```bash
   # Check if UART is enabled
   grep uart /boot/firmware/config.txt
   
   # Check device exists
   ls -la /dev/ttyAMA*
   
   # May need reboot after enabling UART
   sudo reboot
   ```

2. **Permission errors**:
   ```bash
   # Check user groups
   groups
   
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

3. **Communication errors**:
   ```bash
   # Test different baud rates
   python3 tests/test_device.py --baudrate 2400
   python3 tests/test_device.py --baudrate 4800
   
   # Check physical connections
   # Verify UPS is powered and operational
   ```

4. **Service won't start**:
   ```bash
   # Check service status
   sudo systemctl status ups-pi
   
   # Check configuration
   /usr/local/bin/ups-pi/ups_manager.py --test-communication
   
   # Reload systemd
   sudo systemctl daemon-reload
   ```

### Hardware Verification

```bash
# Check GPIO status
python3 -c "
import subprocess
result = subprocess.run(['gpio', 'readall'], capture_output=True, text=True)
print(result.stdout)
"

# Manual UART test
sudo minicom -D /dev/ttyAMA0 -b 9600

# Loopback test (connect GPIO 14 to GPIO 15)
echo "Testing UART loopback..."
```

## Architecture

### Components

- **`ups_communication.py`**: UART communication and data parsing
- **`power_manager.py`**: Main power management logic and monitoring
- **`config.py`**: Configuration loading and validation
- **`ups_manager.py`**: Main application entry point

### Data Flow

1. **UART Communication**: Read status from UPS device
2. **Data Parsing**: Parse and validate UPS data
3. **State Management**: Track power state changes
4. **Action Execution**: Execute shutdown procedures when needed
5. **Logging**: Record all events and status changes

### Power States

- **EXTERNAL_POWER**: Normal operation on external power
- **BATTERY_POWER**: Running on battery (power outage)
- **CRITICAL_BATTERY**: Critical battery level (immediate shutdown)
- **UNKNOWN**: Initial state or communication error

## Development

### Project Structure

```
ups-pi-clean/
├── src/                    # Source code
│   ├── ups_manager.py      # Main application
│   ├── power_manager.py    # Power management logic
│   ├── ups_communication.py # UART communication
│   ├── config.py           # Configuration management
│   └── __init__.py         # Package initialization
├── config/                 # Configuration files
│   ├── config.ini          # Default configuration
│   └── ups-pi.service      # Systemd service file
├── scripts/                # Installation and utility scripts
│   └── install.py          # Automated installer
├── tests/                  # Test scripts
│   └── test_device.py      # Device communication tests
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Testing

```bash
# Install development dependencies
pip3 install -r requirements.txt

# Run device tests
python3 tests/test_device.py --verbose

# Test installation (dry run)
python3 scripts/install.py --help
```

## License

MIT License - see LICENSE file for details.

## Support

For support and bug reports, please open an issue on GitHub.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

---

