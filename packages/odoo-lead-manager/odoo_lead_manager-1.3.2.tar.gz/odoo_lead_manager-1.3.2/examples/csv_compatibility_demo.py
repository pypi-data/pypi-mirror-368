#!/usr/bin/env python3
"""
CSV/TSV Input Compatibility Demo

This script demonstrates how to use the new CSV/TSV input features
with the odlm update command, showing the complete workflow from
lead retrieval to bulk updates.

Usage examples:
    # Export leads to CSV
    odlm leads --format csv --output leads.csv --status new
    
    # Update leads from CSV file
    odlm update --from-csv leads.csv --user-name "Alice Smith"
    
    # Update leads from TSV file  
    odlm update --from-tsv leads.tsv --status assigned
    
    # Update leads from simple text file
    odlm update --from-file lead_ids.txt --user-id 123
"""

import subprocess
import sys
import os

def print_usage_examples():
    """Print usage examples for CSV/TSV compatibility."""
    
    examples = """
📋 CSV/TSV Input Compatibility - Usage Examples
==============================================

1. Export leads to CSV format:
   odlm leads --format csv --output leads.csv --status new --limit 100

2. Export specific fields:
   odlm leads --fields "id,name,email,status,user_id" --format csv --output leads.csv

3. Update leads from CSV file:
   odlm update --from-csv leads.csv --user-name "Alice Smith"

4. Update leads from TSV file:
   odlm update --from-tsv leads.tsv --status assigned

5. Update leads from simple text file:
   echo "12345\\n67890\\n11111" > lead_ids.txt
   odlm update --from-file lead_ids.txt --user-id 42

6. Chain operations (export then update):
   odlm leads --format csv --output new_leads.csv --status new
   odlm update --from-csv new_leads.csv --user-name "Bob Johnson"

7. Handle Odoo export format:
   # CSV file can contain Odoo's __export__ format
   # __export__.crm_lead_12345_abcdef123 -> extracts 12345

8. Filter and update:
   odlm leads --format csv --output filtered.csv --date-from 2024-01-01 --date-to 2024-01-31
   odlm update --from-csv filtered.csv --status "in_progress"

9. Combine with user assignment:
   odlm leads --format csv --output unassigned.csv --user ""
   odlm update --from-csv unassigned.csv --user-name "Charlie Brown"

10. Dry run with count:
    odlm leads --format csv --output leads.csv --status new
    wc -l leads.csv  # Check how many leads
    odlm update --from-csv leads.csv --user-name "Alice Smith" --status assigned
"""
    
    print(examples)

def create_sample_csv():
    """Create a sample CSV file for demonstration."""
    
    sample_data = """id,name,email,status,user_id,phone
10001,John Doe,john@example.com,new,Unassigned,555-0101
10002,Jane Smith,jane@example.com,new,Unassigned,555-0102
10003,Bob Johnson,bob@example.com,new,Unassigned,555-0103
10004,Alice Brown,alice@example.com,new,Unassigned,555-0104
__export__.crm_lead_10005_abcdef123,Charlie Wilson,charlie@example.com,new,Unassigned,555-0105"""
    
    with open('sample_leads.csv', 'w') as f:
        f.write(sample_data)
    
    print("✅ Created sample_leads.csv with 5 test leads")

def create_sample_tsv():
    """Create a sample TSV file for demonstration."""
    
    sample_data = """id\tname\temail\tstatus
20001\tDavid Lee\tdavid@example.com\tnew
20002\tEmma Davis\temma@example.com\tnew
20003\tFrank Miller\tfrank@example.com\tnew"""
    
    with open('sample_leads.tsv', 'w') as f:
        f.write(sample_data)
    
    print("✅ Created sample_leads.tsv with 3 test leads")

def create_sample_text_file():
    """Create a simple text file with IDs."""
    
    sample_ids = ["30001", "30002", "30003", "30004", "30005"]
    
    with open('sample_ids.txt', 'w') as f:
        for id_val in sample_ids:
            f.write(f"{id_val}\n")
    
    print("✅ Created sample_ids.txt with 5 test IDs")

def demonstrate_workflows():
    """Demonstrate complete workflows."""
    
    print("\n🔧 Complete Workflow Examples")
    print("=" * 50)
    
    # Create sample files
    create_sample_csv()
    create_sample_tsv()
    create_sample_text_file()
    
    print("\n📊 Files created:")
    print("- sample_leads.csv (CSV format with full lead data)")
    print("- sample_leads.tsv (TSV format)")
    print("- sample_ids.txt (Simple ID list)")
    
    print("\n🚀 Usage commands:")
    print("\n# 1. Update from CSV (full workflow)")
    print("odlm leads --format csv --output my_leads.csv --status new")
    print("odlm update --from-csv my_leads.csv --user-name 'Sales Team Lead'")
    
    print("\n# 2. Update from TSV")
    print("odlm update --from-tsv sample_leads.tsv --status 'assigned'")
    
    print("\n# 3. Update from text file")
    print("odlm update --from-file sample_ids.txt --user-id 42")
    
    print("\n# 4. Filter and update")
    print("odlm leads --format csv --output recent.csv --date-from 2024-01-01")
    print("odlm update --from-csv recent.csv --closer-name 'Senior Sales'")
    
    print("\n# 5. Check what would be updated")
    print("head -5 sample_leads.csv  # Preview data")
    print("odlm update --from-csv sample_leads.csv --user-name 'Test User' --dry-run")

def cleanup():
    """Clean up sample files."""
    sample_files = ['sample_leads.csv', 'sample_leads.tsv', 'sample_ids.txt']
    for file in sample_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
    print("\n🧹 Sample files cleaned up")

def main():
    """Main demo function."""
    
    print("🎯 CSV/TSV Input Compatibility Demo")
    print("=" * 50)
    
    try:
        print_usage_examples()
        demonstrate_workflows()
        
        print("\n💡 Tips:")
        print("- CSV files can contain any columns; 'id' column will be used automatically")
        print("- TSV files work the same as CSV but use tab separators")
        print("- Text files should have one ID per line")
        print("- Odoo's __export__ format is automatically handled")
        print("- You can combine filters: --from-csv with --status, --user-name, etc.")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())