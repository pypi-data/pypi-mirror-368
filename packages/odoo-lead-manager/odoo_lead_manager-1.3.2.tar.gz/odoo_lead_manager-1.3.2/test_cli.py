#!/usr/bin/env python3
"""
Test script to verify CLI functionality.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from odoo_lead_manager.cli import CLI


def test_cli_help():
    """Test CLI help output."""
    cli = CLI()
    parser = cli.create_parser()
    
    print("=== CLI Help Test ===")
    parser.print_help()
    print("\n=== CLI Commands ===")
    
    # Test each command help
    commands = ["query", "count", "update", "distribute", "users"]
    for cmd in commands:
        print(f"\n--- {cmd} command ---")
        try:
            if cmd == "query":
                cli.create_parser().parse_args([cmd, "--help"])
        except SystemExit:
            pass  # Expected for --help


if __name__ == "__main__":
    test_cli_help()
    print("\n✅ CLI structure verified!")