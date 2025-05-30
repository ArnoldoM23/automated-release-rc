#!/usr/bin/env python3
# main.py - Main entry point for RC Release Agent

"""
Main entry point for the RC Release Agent CLI.
Follows proper Python module execution standards.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def main():
    """Main entry point for the RC Release Agent."""
    try:
        from src.cli.run_release_agent import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 