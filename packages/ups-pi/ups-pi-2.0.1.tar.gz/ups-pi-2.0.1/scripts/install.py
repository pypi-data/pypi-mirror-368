#!/usr/bin/env python3
"""
UPS-Pi Installation Script

Automated installation script for production deployment of UPS-Pi system.
Handles UART configuration, file installation, service setup, and validation.

Features:
- UART configuration validation and setup
- System file installation with proper permissions
- Systemd service configuration
- Log directory creation
- Hardware validation
- Automatic startup configuration

Usage:
    sudo python3 install.py [options]

Requirements:
- Run as root (sudo)
- Raspberry Pi with GPIO UART capability
- UPSPack v3 (or compatible) device
- Python 3.8+ with pyserial
"""

import os
import sys
import subprocess
import shutil
import argparse
import logging
from pathlib import Path
from typing import List, Tuple


class InstallationError(Exception):
    """Exception raised during installation."""
    pass


class UPSPiInstaller:
    """UPS-Pi system installer."""
    
    # Installation paths
    INSTALL_DIR = Path("/usr/local/bin/ups-pi")
    CONFIG_DIR = Path("/etc/ups-pi")
    LOG_DIR = Path("/var/log/ups-pi")
    SERVICE_FILE = Path("/etc/systemd/system/ups-pi.service")
    
    # Source paths (relative to script location)
    SCRIPT_DIR = Path(__file__).parent.parent
    SRC_DIR = SCRIPT_DIR / "src"
    CONFIG_SRC = SCRIPT_DIR / "config"
    
    def __init__(self, args):
        """Initialize installer with command line arguments."""
        self.args = args
        self.logger = self._setup_logging()
        
        # Note: Installation should be run as root (sudo) on target system
        pass
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for installation."""
        logger = logging.getLogger("ups-pi-installer")
        
        # Set log level
        level = logging.DEBUG if self.args.verbose else logging.INFO
        logger.setLevel(level)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def run_command(self, command: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run a system command and return results."""
        self.logger.debug(f"Running command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def check_prerequisites(self) -> None:
        """Check system prerequisites."""
        self.logger.info("Checking system prerequisites...")
        
        # Check if running on Raspberry Pi
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
            if "Raspberry Pi" not in cpuinfo and "BCM" not in cpuinfo:
                self.logger.warning("System does not appear to be a Raspberry Pi")
        except Exception:
            self.logger.warning("Could not verify Raspberry Pi hardware")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise InstallationError(f"Python 3.8+ required, found {sys.version}")
        
        self.logger.info(f"Python version: {sys.version}")
        
        # Check for pyserial
        try:
            import serial
            self.logger.info(f"pyserial version: {serial.VERSION}")
        except ImportError:
            self.logger.info("Installing pyserial...")
            returncode, stdout, stderr = self.run_command([
                sys.executable, "-m", "pip", "install", "pyserial"
            ])
            if returncode != 0:
                raise InstallationError(f"Failed to install pyserial: {stderr}")
        
        # Check source files exist
        required_files = [
            self.SRC_DIR / "ups_manager.py",
            self.SRC_DIR / "ups_communication.py",
            self.SRC_DIR / "power_manager.py",
            self.SRC_DIR / "config.py",
            self.CONFIG_SRC / "config.ini",
            self.CONFIG_SRC / "ups-pi.service"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise InstallationError(f"Required file not found: {file_path}")
        
        self.logger.info("Prerequisites check passed")
    
    def configure_uart(self) -> None:
        """Configure UART for UPS communication."""
        self.logger.info("Configuring UART...")
        
        # Check current UART configuration
        config_files = ["/boot/firmware/config.txt", "/boot/config.txt"]
        config_file = None
        
        for path in config_files:
            if Path(path).exists():
                config_file = Path(path)
                break
        
        if not config_file:
            raise InstallationError("Could not find boot config file")
        
        self.logger.info(f"Using boot config: {config_file}")
        
        # Read current configuration
        try:
            with open(config_file, 'r') as f:
                config_content = f.read()
        except Exception as e:
            raise InstallationError(f"Failed to read {config_file}: {e}")
        
        # Check if UART is already enabled
        uart_enabled = False
        for line in config_content.split('\n'):
            line = line.strip()
            if line == "enable_uart=1":
                uart_enabled = True
                break
            elif line.startswith("enable_uart="):
                # UART setting exists but may be disabled
                break
        
        if not uart_enabled:
            self.logger.info("Adding UART configuration to boot config")
            
            # Backup original config
            backup_path = f"{config_file}.backup.ups-pi"
            shutil.copy2(config_file, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            
            # Add UART configuration
            uart_config = [
                "",
                "# UPS-Pi UART Configuration",
                "enable_uart=1",
                ""
            ]
            
            try:
                with open(config_file, 'a') as f:
                    f.write('\n'.join(uart_config))
                self.logger.info("UART configuration added")
            except Exception as e:
                raise InstallationError(f"Failed to update {config_file}: {e}")
        else:
            self.logger.info("UART already enabled in boot config")
        
        # Check UART device exists
        uart_device = Path("/dev/ttyAMA0")
        if uart_device.exists():
            self.logger.info(f"UART device available: {uart_device}")
        else:
            self.logger.warning(f"UART device not found: {uart_device}")
            self.logger.warning("Reboot may be required for UART changes to take effect")
    
    def install_files(self) -> None:
        """Install UPS-Pi files to system locations."""
        self.logger.info("Installing UPS-Pi files...")
        
        # Create directories
        directories = [self.INSTALL_DIR, self.CONFIG_DIR, self.LOG_DIR]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
        
        # Install source files
        src_files = [
            "ups_manager.py",
            "ups_communication.py", 
            "power_manager.py",
            "config.py",
            "__init__.py"
        ]
        
        for filename in src_files:
            src_path = self.SRC_DIR / filename
            dst_path = self.INSTALL_DIR / filename
            
            shutil.copy2(src_path, dst_path)
            os.chmod(dst_path, 0o755 if filename.endswith('.py') else 0o644)
            self.logger.debug(f"Installed: {src_path} → {dst_path}")
        
        # Install configuration
        config_src = self.CONFIG_SRC / "config.ini"
        config_dst = self.CONFIG_DIR / "config.ini"
        
        if not config_dst.exists() or self.args.force:
            shutil.copy2(config_src, config_dst)
            os.chmod(config_dst, 0o644)
            self.logger.info(f"Installed config: {config_dst}")
        else:
            self.logger.info(f"Config file exists, skipping: {config_dst}")
        
        # Set log directory permissions
        os.chmod(self.LOG_DIR, 0o755)
        
        self.logger.info("Files installed successfully")
    
    def install_service(self) -> None:
        """Install and configure systemd service."""
        self.logger.info("Installing systemd service...")
        
        # Copy service file
        service_src = self.CONFIG_SRC / "ups-pi.service"
        shutil.copy2(service_src, self.SERVICE_FILE)
        os.chmod(self.SERVICE_FILE, 0o644)
        
        # Reload systemd
        returncode, stdout, stderr = self.run_command([
            "systemctl", "daemon-reload"
        ])
        if returncode != 0:
            raise InstallationError(f"Failed to reload systemd: {stderr}")
        
        # Enable service if requested
        if self.args.enable_service:
            returncode, stdout, stderr = self.run_command([
                "systemctl", "enable", "ups-pi"
            ])
            if returncode != 0:
                raise InstallationError(f"Failed to enable service: {stderr}")
            
            self.logger.info("Service enabled for automatic startup")
        
        self.logger.info(f"Service installed: {self.SERVICE_FILE}")
    
    def test_installation(self) -> None:
        """Test the installation."""
        self.logger.info("Testing installation...")
        
        # Test UPS communication
        test_cmd = [
            sys.executable,
            str(self.INSTALL_DIR / "ups_manager.py"),
            "--test-communication"
        ]
        
        returncode, stdout, stderr = self.run_command(test_cmd, check=False)
        
        if returncode == 0:
            self.logger.info("✅ UPS communication test PASSED")
        else:
            self.logger.warning("⚠️  UPS communication test FAILED")
            self.logger.warning("This may be normal if UPS is not connected")
            if stderr:
                self.logger.debug(f"Test output: {stderr}")
    
    def install(self) -> None:
        """Run complete installation process."""
        try:
            self.logger.info("Starting UPS-Pi installation...")
            
            self.check_prerequisites()
            self.configure_uart()
            self.install_files()
            self.install_service()
            
            if not self.args.skip_test:
                self.test_installation()
            
            self.logger.info("✅ UPS-Pi installation completed successfully!")
            
            # Display post-installation instructions
            self._show_post_install_info()
            
        except InstallationError as e:
            self.logger.error(f"❌ Installation failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Unexpected installation error: {e}")
            raise InstallationError(f"Unexpected error: {e}")
    
    def _show_post_install_info(self) -> None:
        """Show post-installation information."""
        print("\n" + "="*60)
        print("UPS-Pi Installation Complete!")
        print("="*60)
        
        print(f"\n📁 Installation locations:")
        print(f"   Program files: {self.INSTALL_DIR}")
        print(f"   Configuration: {self.CONFIG_DIR}/config.ini")
        print(f"   Log files: {self.LOG_DIR}")
        print(f"   Service file: {self.SERVICE_FILE}")
        
        print(f"\n🔧 Hardware setup:")
        print(f"   Connect UPS TX → Raspberry Pi GPIO 15 (RX)")
        print(f"   Connect UPS RX → Raspberry Pi GPIO 14 (TX)")
        print(f"   Connect UPS GND → Raspberry Pi GND")
        
        print(f"\n🚀 Getting started:")
        
        if self.args.enable_service:
            print(f"   Service enabled - UPS monitoring will start on boot")
            print(f"   Start now: sudo systemctl start ups-pi")
            print(f"   Check status: sudo systemctl status ups-pi")
        else:
            print(f"   Enable service: sudo systemctl enable ups-pi")
            print(f"   Start service: sudo systemctl start ups-pi")
        
        print(f"\n🔍 Testing:")
        print(f"   Test communication: {self.INSTALL_DIR}/ups_manager.py --test-communication")
        print(f"   Run interactively: {self.INSTALL_DIR}/ups_manager.py --test-mode")
        print(f"   View logs: sudo journalctl -u ups-pi -f")
        
        print(f"\n⚙️  Configuration:")
        print(f"   Edit: {self.CONFIG_DIR}/config.ini")
        print(f"   Restart service after changes: sudo systemctl restart ups-pi")
        
        if "/dev/ttyAMA0" not in str(subprocess.run(["ls", "/dev/tty*"], capture_output=True, text=True).stdout):
            print(f"\n⚠️  NOTICE: UART device not detected")
            print(f"   Reboot may be required: sudo reboot")
            print(f"   Check UART config: grep uart /boot/firmware/config.txt")
        
        print("\n" + "="*60)


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(
        description="UPS-Pi Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force overwrite existing files'
    )
    
    parser.add_argument(
        '--enable-service',
        action='store_true',
        help='Enable systemd service for automatic startup'
    )
    
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='Skip installation testing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        installer = UPSPiInstaller(args)
        installer.install()
        return 0
        
    except InstallationError as e:
        print(f"\nInstallation failed: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
