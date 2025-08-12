#!/usr/bin/env python3
"""Test script to directly test config generation without full module dependencies."""

import sys
import os
sys.path.append('.')

# Import only the config generator class
from src.odoo_lead_manager.daily_distribution import DailyDistributionConfigGenerator

def test_config_generation():
    """Test the config generation functionality."""
    print("Testing config generation...")
    
    generator = DailyDistributionConfigGenerator()
    
    # Test basic template
    print("\n1. Testing basic template:")
    basic_config = generator.generate_config(template='basic')
    print("Basic config generated successfully")
    
    # Test with campaign
    print("\n2. Testing with Voice campaign:")
    voice_config = generator.generate_config(campaign='Voice', template='basic')
    print("Voice campaign config generated successfully")
    
    # Test with output file
    print("\n3. Testing with output file:")
    output_file = "test_generated_config.yaml"
    generator.generate_config(campaign='Voice', template='basic', output_path=output_file)
    print(f"Config written to {output_file}")
    
    # Verify the generated file
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            content = f.read()
            print(f"\nGenerated config preview (first 500 chars):")
            print(content[:500])
            print("...")
        
        # Test YAML parsing
        import yaml
        parsed = yaml.safe_load(content)
        print(f"\n✅ YAML parsed successfully")
        print(f"Version: {parsed.get('version')}")
        print(f"Name: {parsed.get('name')}")
        print(f"Campaign: {parsed.get('campaign', {}).get('name')}")
        
        # Check for proper quoting
        print(f"\n🔍 Checking string quoting:")
        lines = content.split('\n')
        quoted_strings = [line for line in lines if ':' in line and '"' in line]
        print(f"Found {len(quoted_strings)} properly quoted strings")
        
        # Show some examples
        for i, line in enumerate(quoted_strings[:5]):
            print(f"  {i+1}. {line.strip()}")
        
        return True
    else:
        print("❌ Output file not created")
        return False

if __name__ == "__main__":
    success = test_config_generation()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 