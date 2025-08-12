#!/usr/bin/env python3
"""Test script to verify YAML generation with proper string quoting."""

import yaml
from typing import Dict, Any

def dump_yaml_with_quotes(data: Dict[str, Any]) -> str:
    """Dump YAML with proper string quoting."""
    class QuotedStringDumper(yaml.SafeDumper):
        def represent_str(self, data):
            # Always quote strings that contain special characters or environment variables
            if any(char in data for char in ['$', '{', '}', ':', ' ', '-', '|', '>', '<', '&', '*', '?', '!', '%', '@', '`']) or data.startswith('${'):
                return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    
    # Register the custom dumper
    QuotedStringDumper.add_representer(str, QuotedStringDumper.represent_str)
    
    return yaml.dump(data, Dumper=QuotedStringDumper, default_flow_style=False, 
                    sort_keys=False, allow_unicode=True, width=float("inf"))

# Test data similar to the config template
test_config = {
    "version": "1.0",
    "name": "Daily Lead Distribution - Voice",
    "description": "Automated daily lead distribution system for Voice campaigns",
    "tags": ["lead-distribution", "automation", "sales", "odoo"],
    "author": "Sales Operations Team",
    "created_date": "2024-01-15",
    "last_modified": "2024-01-15",
    
    "odoo_connection": {
        "host": "${ODOO_HOST}",
        "port": 8069,
        "database": "${ODOO_DB}",
        "username": "${ODOO_USERNAME}",
        "password": "${ODOO_PASSWORD}"
    },
    
    "database_connection": {
        "host": "${TRACKING_DB_HOST}",
        "port": 3306,
        "database": "${TRACKING_DB_NAME}",
        "username": "${TRACKING_DB_USER}",
        "password": "${TRACKING_DB_PASSWORD}"
    },
    
    "campaign": {
        "name": "Voice",
        "description": "Voice/telephony sales campaign distribution",
        "target_campaign": "Voice",
        "distribution_frequency": "daily",
        "active": True
    },
    
    "salesperson_selection": {
        "source_type": "campaign_table",
        "source_config": {
            "campaign_table": {
                "file_path": "config/salesperson_campaigns.csv"
            }
        },
        "campaign_filtering": {
            "enabled": True,
            "target_campaign": "Voice",
            "include_inactive_salespeople": False,
            "exclude_specific_users": ["Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"]
        },
        "filters": {
            "active_only": True,
            "has_permissions": True,
            "min_experience_level": 1,
            "max_workload_percentage": 90,
            "team_filter": "Voice"
        }
    }
}

print("Testing YAML generation with proper string quoting:")
print("=" * 60)
result = dump_yaml_with_quotes(test_config)
print(result)

# Test that the generated YAML can be parsed back
print("\nTesting YAML parsing:")
print("=" * 60)
parsed = yaml.safe_load(result)
print("✅ YAML parsed successfully")
print(f"Version: {parsed.get('version')}")
print(f"Name: {parsed.get('name')}")
print(f"Host: {parsed.get('odoo_connection', {}).get('host')}") 