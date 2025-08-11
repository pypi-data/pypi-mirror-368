#!/usr/bin/env python3
"""
UPS-Pi Project Cleanup Script

Archives old files and directories outside of the ups-pi-clean directory.
Creates a timestamped archive of the legacy files for reference.

Usage:
    python3 cleanup_project.py [options]

This script will:
1. Create an archive of old files
2. Remove or move legacy directories
3. Clean up test and development files
4. Preserve the new ups-pi-clean structure
"""

import os
import sys
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path


def setup_logging(verbose: bool) -> logging.Logger:
    """Setup logging for cleanup operations."""
    logger = logging.getLogger("ups-pi-cleanup")
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def create_archive(source_dir: Path, archive_path: Path, logger: logging.Logger) -> bool:
    """Create archive of legacy files."""
    try:
        logger.info(f"Creating archive: {archive_path}")
        
        # Files and directories to archive (exclude ups-pi-clean)
        items_to_archive = []
        
        for item in source_dir.iterdir():
            if item.name not in ['ups-pi-clean', '.git', '__pycache__', '.venv', '.pytest_cache', '.mypy_cache']:
                items_to_archive.append(item)
        
        if not items_to_archive:
            logger.info("No items to archive")
            return True
        
        # Create temporary directory for archive contents
        temp_dir = source_dir / "temp_archive"
        temp_dir.mkdir(exist_ok=True)
        
        # Copy items to temp directory
        for item in items_to_archive:
            dest_path = temp_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest_path, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '.pytest_cache', 'node_modules'
                ))
            else:
                shutil.copy2(item, dest_path)
            logger.debug(f"Added to archive: {item.name}")
        
        # Create archive
        archive_base = archive_path.with_suffix('')
        shutil.make_archive(str(archive_base), 'zip', temp_dir)
        
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        
        logger.info(f"Archive created successfully: {archive_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create archive: {e}")
        return False


def cleanup_legacy_files(source_dir: Path, logger: logging.Logger, dry_run: bool = False) -> bool:
    """Remove or move legacy files."""
    try:
        # Files and directories to remove
        items_to_remove = [
            'ups-pi',  # old ups-pi directory
            'check_gpio.py',
            'uart_config.py', 
            'device_test.py',
            'device_test_pi.py',
            'power_management_system.py',
            'upspackv2.py',
            'ups_manager.py',  # old version
            'install_production.sh',
            'install_usb_ups.sh',
            'cleanup_production.sh',
            'cleanup_project.sh',
            'usb_diagnostics.sh',
            'usb_test_comprehensive.py',
            'usb_ups_test.py',
            'find_devices.py',
            'manual_serial_test.py',
            'test_uart.py',
            'upspack-power-management.service',
            'README_USB.md',
            'DEVICE_SETUP_GUIDE.md',
            'TROUBLESHOOTING.md',
            'VARIABLES_GUIDE.md',
            'CONFIGURATION_REFERENCE.md',
            '__pycache__',
            'tests',  # old tests directory
            'docs',   # old docs directory
            '.pytest_cache',
            '.mypy_cache',
            'htmlcov',
            'site'
        ]
        
        removed_count = 0
        
        for item_name in items_to_remove:
            item_path = source_dir / item_name
            
            if item_path.exists():
                if dry_run:
                    logger.info(f"Would remove: {item_name}")
                else:
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                        logger.info(f"Removed directory: {item_name}")
                    else:
                        item_path.unlink()
                        logger.info(f"Removed file: {item_name}")
                
                removed_count += 1
        
        if removed_count == 0:
            logger.info("No legacy files found to remove")
        else:
            action = "Would remove" if dry_run else "Removed"
            logger.info(f"{action} {removed_count} legacy items")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to cleanup legacy files: {e}")
        return False


def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description="UPS-Pi Project Cleanup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Skip creating archive of legacy files'
    )
    
    parser.add_argument(
        '--archive-path',
        type=str,
        help='Custom path for archive file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Get source directory (script location parent)
    source_dir = Path(__file__).parent
    
    logger.info("UPS-Pi Project Cleanup")
    logger.info("=" * 40)
    logger.info(f"Source directory: {source_dir}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    # Determine archive path
    archive_path = None
    if not args.no_archive:
        if args.archive_path:
            archive_path = Path(args.archive_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = source_dir / f"ups-pi-legacy_{timestamp}.zip"
        
        # Create archive
        if not args.dry_run:
            if not create_archive(source_dir, archive_path, logger):
                logger.error("Archive creation failed, aborting cleanup")
                return 1
        else:
            logger.info(f"Would create archive: {archive_path}")
    
    # Cleanup legacy files
    if not cleanup_legacy_files(source_dir, logger, args.dry_run):
        logger.error("Cleanup failed")
        return 1
    
    # Final status
    logger.info("=" * 40)
    if args.dry_run:
        logger.info("Dry run completed - no changes made")
        logger.info("Run without --dry-run to perform actual cleanup")
    else:
        logger.info("Project cleanup completed successfully!")
        logger.info(f"Clean project structure is in: {source_dir / 'ups-pi-clean'}")
        
        if not args.no_archive and archive_path:
            logger.info(f"Legacy files archived to: {archive_path}")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCleanup cancelled by user")
        sys.exit(130)
