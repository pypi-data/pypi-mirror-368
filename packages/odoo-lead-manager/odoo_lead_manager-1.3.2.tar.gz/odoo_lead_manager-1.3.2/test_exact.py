#!/usr/bin/env python3
"""Test script for the new --exact functionality."""

import subprocess
import sys

def test_exact_functionality():
    """Test the new --exact parameter functionality."""
    
    # Test help text includes the new parameter
    try:
        result = subprocess.run(['python', '-m', 'odoo_lead_manager.cli', 'leads', '--help'], 
                              capture_output=True, text=True)
        if '--exact' in result.stdout:
            print("✅ --exact parameter found in help text")
        else:
            print("❌ --exact parameter not found in help text")
    except Exception as e:
        print(f"❌ Error testing help: {e}")
    
    # Test exact filtering (would need actual Odoo connection)
    print("\n🧪 Exact filtering is implemented with:")
    print("  odlm leads --exact 'Paul Park'  # Exact open_user_id match")
    print("  odlm leads --exact-user 'Harry Cho'  # Exact user_id match")
    print("  odlm leads --user 'Harry'  # Partial user match (existing)")

if __name__ == "__main__":
    test_exact_functionality()