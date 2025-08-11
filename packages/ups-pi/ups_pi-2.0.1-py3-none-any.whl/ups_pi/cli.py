"""command line interface for ups-pi"""

import sys
import argparse
import logging
from pathlib import Path

from .ups_manager import main as ups_main


def main():
    """main entry point for ups-pi cli"""
    try:
        ups_main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
