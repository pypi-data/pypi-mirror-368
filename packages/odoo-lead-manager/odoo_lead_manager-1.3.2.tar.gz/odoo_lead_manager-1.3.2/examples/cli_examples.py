#!/usr/bin/env python3
"""
CLI usage examples for Odoo Lead Manager.

This script demonstrates common CLI usage patterns.
"""

import subprocess
import os

def run_command(cmd):
    """Run CLI command and show example."""
    print(f"$ {cmd}")
    print("-" * 50)
    # In real usage, you would run: subprocess.run(cmd.split())
    print(f"Example output for: {cmd}")
    print()

def main():
    """Show CLI usage examples."""
    print("🚀 Odoo Lead Manager CLI Examples")
    print("=" * 50)
    
    print("\n## Basic Query Examples")
    
    examples = [
        # Basic queries
        "odlm query --limit 5",
        "odlm query --status new --format table",
        "odlm query --date-filter older_than_2_months --user \"Naidene\"",
        
        # Date filtering
        "odlm query --date-filter last_30_days --format csv --output recent_leads.csv",
        "odlm query --date-from 2024-01-01 --date-to 2024-01-31 --status won",
        
        # User-based filtering
        "odlm query --user \"Alice Smith\" --source Website",
        "odlm query --closer \"Bob Johnson\" --format json",
        
        # Combined filtering
        "odlm query --date-filter older_than_1_month --status new --user \"Naidene\" --format table",
        
        # Counting
        "odlm count --status new",
        "odlm count --date-filter older_than_2_months --user \"Naidene\"",
        
        # Updating
        "odlm update --ids 1,2,3 --user-name \"Administrator\" --status assigned",
        "odlm update --date-filter older_than_2_months --user \"Naidene\" --user-name \"Administrator\"",
        
        # Chained operations
        "odlm query --date-filter older_than_2_months --user \"Naidene\" --format table",
        "odlm count --date-filter older_than_2_months --user \"Naidene\"",
        "odlm update --date-filter older_than_2_months --user \"Naidene\" --user-name \"Administrator\" --status reassigned",
        
        # Distribution
        "odlm distribute --status new --strategy proportional",
        "odlm distribute --date-filter last_7_days --strategy round_robin --dry-run",
        
        # User management
        "odlm users --list",
        "odlm users --counts",
    ]
    
    for example in examples:
        run_command(example)
    
    print("\n## Real-World Usage Script")
    print("""
#!/bin/bash
# daily_lead_management.sh

echo "=== Daily Lead Management ==="
date

echo "1. Counting leads older than 2 months assigned to Naidene..."
OLD_COUNT=$(odlm count --date-filter older_than_2_months --user "Naidene")
echo "Found: $OLD_COUNT old leads"

if [ "$OLD_COUNT" -gt 0 ]; then
    echo "2. Showing details..."
    odlm query --date-filter older_than_2_months --user "Naidene" --format table
    
    echo "3. Reassigning to Administrator..."
    odlm update --date-filter older_than_2_months --user "Naidene" --user-name "Administrator" --status reassigned
    
    echo "4. Verification..."
    odlm query --user "Administrator" --date-filter older_than_2_months --format table
fi

echo "5. Exporting daily report..."
odlm query --date-filter today --format csv --output "daily_$(date +%Y%m%d).csv"

echo "=== Complete ==="
    """)
    
    print("\n## Environment Configuration")
    print("""
# .env file example
ODOO_HOST=your-odoo-server.com
ODOO_PORT=8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Usage with environment variables
echo "Using production server..."
ODOO_HOST=prod.example.com ODOO_DB=production odlm query --status new
    """)

if __name__ == "__main__":
    main()