#!/usr/bin/env python3
"""
Test PyPI Connection Script

This script helps verify that your PyPI authentication is set up correctly
before attempting to publish your package.
"""

import os
import sys
import configparser
from pathlib import Path
import subprocess

def print_status(message, status="INFO"):
    """Print a formatted status message."""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
    }
    color = colors.get(status, "\033[0m")
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def check_pypirc_file():
    """Check if ~/.pypirc file exists and is properly configured."""
    print_status("Checking ~/.pypirc configuration...")
    
    pypirc_path = Path.home() / ".pypirc"
    
    if not pypirc_path.exists():
        print_status("~/.pypirc file not found", "WARNING")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(pypirc_path)
        
        # Check for required sections
        required_sections = ["pypi"]
        optional_sections = ["testpypi"]
        
        for section in required_sections:
            if section not in config.sections():
                print_status(f"Missing required section: {section}", "ERROR")
                return False
        
        # Check for required keys in each section
        for section in config.sections():
            if section in ["pypi", "testpypi"]:
                required_keys = ["username", "password"]
                for key in required_keys:
                    if key not in config[section]:
                        print_status(f"Missing {key} in [{section}] section", "ERROR")
                        return False
                
                # Check if username is __token__
                if config[section]["username"] != "__token__":
                    print_status(f"Username in [{section}] should be '__token__'", "WARNING")
                
                # Check if password starts with pypi-
                password = config[section]["password"]
                if not password.startswith("pypi-"):
                    print_status(f"Password in [{section}] should start with 'pypi-'", "WARNING")
        
        print_status("~/.pypirc file is properly configured", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Error reading ~/.pypirc: {e}", "ERROR")
        return False

def check_file_permissions():
    """Check if ~/.pypirc has proper permissions."""
    print_status("Checking file permissions...")
    
    pypirc_path = Path.home() / ".pypirc"
    
    if not pypirc_path.exists():
        return False
    
    try:
        stat = pypirc_path.stat()
        mode = stat.st_mode & 0o777
        
        if mode == 0o600:
            print_status("File permissions are correct (600)", "SUCCESS")
            return True
        else:
            print_status(f"File permissions should be 600, but are {oct(mode)}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Error checking permissions: {e}", "ERROR")
        return False

def check_twine_installation():
    """Check if twine is installed."""
    print_status("Checking twine installation...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "twine", "--version"], 
                              capture_output=True, text=True, check=True)
        print_status("Twine is installed", "SUCCESS")
        return True
    except subprocess.CalledProcessError:
        print_status("Twine is not installed", "ERROR")
        return False
    except FileNotFoundError:
        print_status("Twine is not installed", "ERROR")
        return False

def test_pypi_connection():
    """Test connection to PyPI."""
    print_status("Testing PyPI connection...")
    
    try:
        # Test with a simple check command (without --repository flag)
        result = subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_status("PyPI connection successful", "SUCCESS")
            return True
        else:
            print_status(f"PyPI connection failed: {result.stderr}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("PyPI connection timed out", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error testing PyPI connection: {e}", "ERROR")
        return False

def test_testpypi_connection():
    """Test connection to TestPyPI."""
    print_status("Testing TestPyPI connection...")
    
    try:
        # Test with a simple check command (without --repository flag)
        result = subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_status("TestPyPI connection successful", "SUCCESS")
            return True
        else:
            print_status(f"TestPyPI connection failed: {result.stderr}", "WARNING")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("TestPyPI connection timed out", "WARNING")
        return False
    except Exception as e:
        print_status(f"Error testing TestPyPI connection: {e}", "WARNING")
        return False

def check_built_packages():
    """Check if packages are built and ready for upload."""
    print_status("Checking for built packages...")
    
    dist_path = Path("dist")
    
    if not dist_path.exists():
        print_status("dist/ directory not found", "WARNING")
        return False
    
    packages = list(dist_path.glob("*.whl")) + list(dist_path.glob("*.tar.gz"))
    
    if not packages:
        print_status("No built packages found in dist/", "WARNING")
        return False
    
    print_status(f"Found {len(packages)} built package(s):", "SUCCESS")
    for package in packages:
        print(f"  - {package.name}")
    
    return True

def main():
    """Main test function."""
    print("🔍 PyPI Connection Test")
    print("=" * 50)
    
    # Check if we're in the project directory
    if not Path("setup.py").exists():
        print_status("setup.py not found. Please run this script from the project root directory.", "ERROR")
        sys.exit(1)
    
    tests = [
        ("Twine Installation", check_twine_installation),
        ("Built Packages", check_built_packages),
        ("PyPI Configuration", check_pypirc_file),
        ("File Permissions", check_file_permissions),
        ("PyPI Connection", test_pypi_connection),
        ("TestPyPI Connection", test_testpypi_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("All tests passed! Your PyPI setup is ready.", "SUCCESS")
        print("\n🚀 You can now publish your package:")
        print("  ./publish_to_pypi.sh")
    else:
        print_status("Some tests failed. Please fix the issues above before publishing.", "WARNING")
        print("\n📖 See docs/PYPI_AUTHENTICATION_SETUP.md for detailed setup instructions.")

if __name__ == "__main__":
    main() 