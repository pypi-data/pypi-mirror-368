#!/usr/bin/env python3
"""
🏴‍☠️ uzdabrawza CLI Entry Point 🏴‍☠️

Command-line interface for the anal-queen of browser automation.
This module provides the entry point for the CLI command and imports
the main functionality from the core module.
"""

import asyncio
import sys
from .core import main as core_main


def main():
    """
    Main CLI entry point for uzdabrawza.
    
    This function serves as the entry point when uzdabrawza is installed
    as a package and called via the command line using 'uzdabrawza' command.
    """
    try:
        # Run the main async function
        asyncio.run(core_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user - chaos aborted gracefully!")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"💥 CLUSTERFUCK ALERT: CLI execution failed: {e}")
        print("   Check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()