#!/usr/bin/env python3
"""
Build script for odoo-lead-manager package.
This script helps build and test the package before publishing to PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def clean_build_artifacts():
    """Clean up build artifacts."""
    print("\n🧹 Cleaning build artifacts...")
    
    dirs_to_clean = [
        "build",
        "dist", 
        "*.egg-info",
        "src/*.egg-info",
        "__pycache__",
        "src/__pycache__",
        "src/odoo_lead_manager/__pycache__",
        "tests/__pycache__",
        ".pytest_cache",
        ".coverage",
        "htmlcov"
    ]
    
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed file: {path}")

def check_package_structure():
    """Check if the package structure is correct."""
    print("\n📁 Checking package structure...")
    
    required_files = [
        "setup.py",
        "pyproject.toml", 
        "MANIFEST.in",
        "LICENSE",
        "README.md",
        "requirements.txt",
        "src/odoo_lead_manager/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Package structure looks good")
    return True

def main():
    """Main build process."""
    print("🚀 Starting odoo-lead-manager package build process...")
    
    # Step 1: Clean build artifacts
    clean_build_artifacts()
    
    # Step 2: Check package structure
    if not check_package_structure():
        print("❌ Package structure check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Step 3: Install build dependencies
    if not run_command("pip install --upgrade build twine", "Installing build dependencies"):
        sys.exit(1)
    
    # Step 4: Build the package
    if not run_command("python -m build", "Building package"):
        sys.exit(1)
    
    # Step 5: Check the built package
    if not run_command("twine check dist/*", "Checking built package"):
        sys.exit(1)
    
    # Step 6: Run tests (if available)
    if Path("tests").exists():
        if not run_command("python -m pytest tests/ -v", "Running tests"):
            print("⚠️  Tests failed, but continuing with build...")
    
    print("\n🎉 Package build completed successfully!")
    print("\n📦 Built packages are in the 'dist' directory:")
    
    dist_files = list(Path("dist").glob("*"))
    for file_path in dist_files:
        print(f"  - {file_path}")
    
    print("\n📋 Next steps:")
    print("1. Review the built packages in the 'dist' directory")
    print("2. Test the package locally: pip install dist/odoo_lead_manager-*.whl")
    print("3. Upload to PyPI: twine upload dist/*")
    print("4. Or upload to TestPyPI first: twine upload --repository testpypi dist/*")

if __name__ == "__main__":
    main() 