"""service installation utilities for ups-pi"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional


class ServiceInstallError(Exception):
    """service installation error"""
    pass


def _check_root():
    """check if running as root (linux only)"""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows or other non-Unix systems
        return True


def install_systemd_service(
    service_name: str = "ups-pi",
    user: str = "root",
    config_path: str = "/etc/ups-pi/config.ini"
) -> bool:
    """install systemd service for ups-pi"""
    
    if not _check_root():
        raise ServiceInstallError("Service installation requires root privileges")
    
    service_content = f"""[Unit]
Description=UPS-Pi Power Management System
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
Group=dialout
ExecStart=/usr/local/bin/ups-pi --config {config_path}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path(f"/etc/systemd/system/{service_name}.service")
    
    try:
        # Write service file
        service_file.write_text(service_content)
        service_file.chmod(0o644)
        
        # Reload systemd
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print(f"Service {service_name} installed successfully")
        
        return True
        
    except Exception as e:
        raise ServiceInstallError(f"Failed to install service: {e}")


def enable_service(service_name: str = "ups-pi") -> bool:
    """enable and start ups-pi service"""
    
    if not _check_root():
        raise ServiceInstallError("Service management requires root privileges")
    
    try:
        # Enable service
        subprocess.run(["systemctl", "enable", service_name], check=True)
        print(f"Service {service_name} enabled")
        
        # Start service
        subprocess.run(["systemctl", "start", service_name], check=True)
        print(f"Service {service_name} started")
        
        return True
        
    except Exception as e:
        raise ServiceInstallError(f"Failed to enable service: {e}")


def create_config_dir(config_dir: str = "/etc/ups-pi") -> bool:
    """create configuration directory"""
    
    if not _check_root():
        raise ServiceInstallError("Config directory creation requires root privileges")
    
    try:
        config_path = Path(config_dir)
        config_path.mkdir(parents=True, exist_ok=True)
        config_path.chmod(0o755)
        
        # Create default config if it doesn't exist
        config_file = config_path / "config.ini"
        if not config_file.exists():
            default_config = """[uart]
port = /dev/ttyAMA0
baudrate = 9600
timeout = 2.0

[monitoring]
interval = 5.0
retries = 3
max_failures = 5

[shutdown]
delay = 30
critical_threshold = 5
low_threshold = 20
enable = true

[gpio]
enable = false
shutdown_pin = 18
status_led_pin = 

[logging]
level = INFO
file = /var/log/ups-pi/power_events.log
max_size = 10485760
backup_count = 5
"""
            config_file.write_text(default_config)
            config_file.chmod(0o644)
            print(f"Default config created at {config_file}")
        
        return True
        
    except Exception as e:
        raise ServiceInstallError(f"Failed to create config directory: {e}")


def create_log_dir(log_dir: str = "/var/log/ups-pi") -> bool:
    """create log directory"""
    
    if not _check_root():
        raise ServiceInstallError("Log directory creation requires root privileges")
    
    try:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_path.chmod(0o755)
        print(f"Log directory created at {log_path}")
        
        return True
        
    except Exception as e:
        raise ServiceInstallError(f"Failed to create log directory: {e}")


def uninstall_service(service_name: str = "ups-pi") -> bool:
    """uninstall ups-pi service"""
    
    if not _check_root():
        raise ServiceInstallError("Service removal requires root privileges")
    
    try:
        # Stop service
        subprocess.run(["systemctl", "stop", service_name], check=False)
        
        # Disable service
        subprocess.run(["systemctl", "disable", service_name], check=False)
        
        # Remove service file
        service_file = Path(f"/etc/systemd/system/{service_name}.service")
        if service_file.exists():
            service_file.unlink()
        
        # Reload systemd
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        
        print(f"Service {service_name} uninstalled successfully")
        return True
        
    except Exception as e:
        raise ServiceInstallError(f"Failed to uninstall service: {e}")


def main():
    """command line interface for service management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UPS-Pi Service Management")
    parser.add_argument("action", choices=["install", "enable", "uninstall", "setup-dirs"],
                       help="Action to perform")
    parser.add_argument("--service-name", default="ups-pi", help="Service name")
    parser.add_argument("--user", default="root", help="Service user")
    parser.add_argument("--config-path", default="/etc/ups-pi/config.ini", 
                       help="Config file path")
    
    args = parser.parse_args()
    
    try:
        if args.action == "install":
            install_systemd_service(args.service_name, args.user, args.config_path)
        elif args.action == "enable":
            enable_service(args.service_name)
        elif args.action == "uninstall":
            uninstall_service(args.service_name)
        elif args.action == "setup-dirs":
            create_config_dir()
            create_log_dir()
        
        print("Operation completed successfully")
        
    except ServiceInstallError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
