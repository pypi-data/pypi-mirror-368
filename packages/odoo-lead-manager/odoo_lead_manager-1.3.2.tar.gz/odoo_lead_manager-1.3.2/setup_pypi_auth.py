#!/usr/bin/env python3
"""
Interactive PyPI Authentication Setup

This script helps you set up your PyPI authentication by creating the ~/.pypirc file
with your API tokens.
"""

import os
import sys
from pathlib import Path
import getpass

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

def get_user_input(prompt, secret=False):
    """Get user input with optional secret mode."""
    if secret:
        return getpass.getpass(prompt)
    else:
        return input(prompt)

def create_pypirc_file():
    """Create the ~/.pypirc file with user input."""
    print_status("Setting up PyPI authentication...")
    print("\nThis script will help you create a ~/.pypirc file with your PyPI API tokens.")
    print("You'll need to generate API tokens from your PyPI account first.")
    print("\nTo generate API tokens:")
    print("1. Go to https://pypi.org/account/settings/")
    print("2. Click 'API tokens' in the left sidebar")
    print("3. Click 'Add API token'")
    print("4. Give it a name (e.g., 'odoo-lead-manager-upload')")
    print("5. Copy the token (it starts with 'pypi-')")
    print("\n" + "="*60)
    
    # Get PyPI token
    print("\n🔑 PyPI API Token Setup")
    print("-" * 30)
    pypi_token = get_user_input("Enter your PyPI API token (starts with 'pypi-'): ", secret=True)
    
    if not pypi_token.startswith("pypi-"):
        print_status("Warning: PyPI tokens should start with 'pypi-'", "WARNING")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            print_status("Setup cancelled", "INFO")
            return False
    
    # Ask about TestPyPI
    print("\n🧪 TestPyPI Setup (Optional)")
    print("-" * 30)
    use_testpypi = input("Do you want to set up TestPyPI as well? (y/n): ").lower() == 'y'
    
    testpypi_token = None
    if use_testpypi:
        print("\nTo generate TestPyPI API tokens:")
        print("1. Go to https://test.pypi.org/account/settings/")
        print("2. Follow the same steps as PyPI")
        print("3. Copy the token (it starts with 'pypi-')")
        print("\n" + "="*60)
        
        testpypi_token = get_user_input("Enter your TestPyPI API token (starts with 'pypi-'): ", secret=True)
        
        if not testpypi_token.startswith("pypi-"):
            print_status("Warning: TestPyPI tokens should start with 'pypi-'", "WARNING")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                use_testpypi = False
                testpypi_token = None
    
    # Create the configuration content
    config_content = """[distutils]
index-servers =
    pypi
"""
    
    if use_testpypi:
        config_content += "    testpypi\n"
    
    config_content += f"""
[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = {pypi_token}
"""
    
    if use_testpypi and testpypi_token:
        config_content += f"""
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = {testpypi_token}
"""
    
    # Write the file
    pypirc_path = Path.home() / ".pypirc"
    
    try:
        with open(pypirc_path, 'w') as f:
            f.write(config_content)
        
        # Set proper permissions
        os.chmod(pypirc_path, 0o600)
        
        print_status(f"~/.pypirc file created successfully at {pypirc_path}", "SUCCESS")
        print_status("File permissions set to 600 (owner read/write only)", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Error creating ~/.pypirc file: {e}", "ERROR")
        return False

def verify_setup():
    """Verify the setup by testing the configuration."""
    print("\n🔍 Verifying setup...")
    
    pypirc_path = Path.home() / ".pypirc"
    
    if not pypirc_path.exists():
        print_status("~/.pypirc file not found", "ERROR")
        return False
    
    try:
        # Check file permissions
        stat = pypirc_path.stat()
        mode = stat.st_mode & 0o777
        
        if mode != 0o600:
            print_status(f"File permissions should be 600, but are {oct(mode)}", "WARNING")
            fix_perms = input("Fix permissions? (y/n): ").lower()
            if fix_perms == 'y':
                os.chmod(pypirc_path, 0o600)
                print_status("Permissions fixed", "SUCCESS")
        
        # Read and validate the file
        with open(pypirc_path, 'r') as f:
            content = f.read()
        
        if "pypi" in content and "__token__" in content:
            print_status("~/.pypirc file appears to be properly configured", "SUCCESS")
            return True
        else:
            print_status("~/.pypirc file seems to be missing required content", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Error verifying setup: {e}", "ERROR")
        return False

def main():
    """Main function."""
    print("🚀 PyPI Authentication Setup")
    print("=" * 50)
    
    # Check if ~/.pypirc already exists
    pypirc_path = Path.home() / ".pypirc"
    
    if pypirc_path.exists():
        print_status("~/.pypirc file already exists", "WARNING")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print_status("Setup cancelled", "INFO")
            return
    
    # Create the file
    if create_pypirc_file():
        # Verify the setup
        if verify_setup():
            print_status("PyPI authentication setup completed successfully!", "SUCCESS")
            print("\n🎉 You can now test your setup:")
            print("  python test_pypi_connection.py")
            print("\n🚀 And publish your package:")
            print("  ./publish_to_pypi.sh")
        else:
            print_status("Setup verification failed", "ERROR")
    else:
        print_status("Setup failed", "ERROR")

if __name__ == "__main__":
    main() 