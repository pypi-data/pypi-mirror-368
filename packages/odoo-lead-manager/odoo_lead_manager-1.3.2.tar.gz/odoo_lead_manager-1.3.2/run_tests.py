#!/usr/bin/env python3
"""
Test runner script for Odoo Lead Manager package.

This script provides convenient ways to run the test suite with various options.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Odoo Lead Manager tests")
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--pattern", 
        "-k", 
        help="Test pattern (pytest -k option)"
    )
    parser.add_argument(
        "--markers", 
        "-m", 
        help="Test markers (pytest -m option)"
    )
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Run only fast unit tests"
    )
    parser.add_argument(
        "--specific", 
        help="Run specific test file or test"
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=src/odoo_lead_manager", "--cov-report=html", "--cov-report=term-missing"])
    
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.specific:
        cmd.append(args.specific)
    else:
        cmd.append("tests/")
    
    print("Running tests with command:", " ".join(cmd))
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()