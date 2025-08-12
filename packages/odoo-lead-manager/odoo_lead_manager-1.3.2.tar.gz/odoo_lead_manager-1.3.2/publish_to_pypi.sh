#!/bin/bash

# PyPI Publication Script for Odoo Lead Manager
# This script helps you publish your package to PyPI

set -e  # Exit on any error

echo "🚀 PyPI Publication Script for Odoo Lead Manager"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    if ! python -c "import build" &> /dev/null; then
        print_warning "build package not found. Installing..."
        pip install build
    fi
    
    if ! python -c "import twine" &> /dev/null; then
        print_warning "twine package not found. Installing..."
        pip install twine
    fi
    
    print_success "Dependencies check completed"
}

# Clean and build the package
build_package() {
    print_status "Building package..."
    
    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/ src/*.egg-info/
    
    # Build the package
    python -m build
    
    if [ $? -eq 0 ]; then
        print_success "Package built successfully"
    else
        print_error "Package build failed"
        exit 1
    fi
}

# Check the built package
check_package() {
    print_status "Checking built package..."
    
    twine check dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Package validation passed"
    else
        print_error "Package validation failed"
        exit 1
    fi
}

# Test installation locally
test_installation() {
    print_status "Testing local installation..."
    
    # Install the package locally
    pip install dist/*.whl --force-reinstall
    
    if [ $? -eq 0 ]; then
        print_success "Local installation test passed"
        
        # Test CLI command
        if command -v odlm &> /dev/null; then
            print_success "CLI command 'odlm' is available"
        else
            print_warning "CLI command 'odlm' not found"
        fi
    else
        print_error "Local installation test failed"
        exit 1
    fi
}

# Upload to TestPyPI
upload_to_testpypi() {
    print_status "Uploading to TestPyPI..."
    
    read -p "Do you want to upload to TestPyPI first? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload --repository testpypi dist/*
        
        if [ $? -eq 0 ]; then
            print_success "Upload to TestPyPI completed"
            print_status "You can test the installation with:"
            echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ odoo-lead-manager"
        else
            print_error "Upload to TestPyPI failed"
            exit 1
        fi
    else
        print_status "Skipping TestPyPI upload"
    fi
}

# Upload to PyPI
upload_to_pypi() {
    print_status "Uploading to PyPI..."
    
    read -p "Are you ready to upload to PyPI? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload dist/*
        
        if [ $? -eq 0 ]; then
            print_success "Upload to PyPI completed successfully!"
            print_status "Your package is now available at:"
            echo "https://pypi.org/project/odoo-lead-manager/"
        else
            print_error "Upload to PyPI failed"
            exit 1
        fi
    else
        print_status "Upload to PyPI cancelled"
    fi
}

# Main execution
main() {
    echo
    print_status "Starting PyPI publication process..."
    
    # Check if we're in the right directory
    if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
        print_error "setup.py or pyproject.toml not found. Please run this script from the project root directory."
        exit 1
    fi
    
    check_dependencies
    build_package
    check_package
    test_installation
    upload_to_testpypi
    upload_to_pypi
    
    echo
    print_success "PyPI publication process completed!"
    echo
    print_status "Next steps:"
    echo "1. Verify your package on PyPI: https://pypi.org/project/odoo-lead-manager/"
    echo "2. Test installation: pip install odoo-lead-manager"
    echo "3. Update your documentation with installation instructions"
    echo "4. Consider setting up automated publishing with GitHub Actions"
}

# Run main function
main "$@" 