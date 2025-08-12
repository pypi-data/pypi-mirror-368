# CLI Usage Guide - Odoo Lead Manager

This guide provides comprehensive examples for using the Odoo Lead Manager CLI to query, filter, and modify leads with powerful command-line tools.

## 🚀 Installation & Setup

### 1. Install Package
```bash
pip install -e .
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Odoo credentials
```

### 3. Verify Installation
```bash
odlm --help
# or
odoo-lead-manager --help
```

## 📋 Available Commands

- `check` - Check connection to Odoo server
- `configure` - Configure Odoo credentials interactively
- `query` - Query leads with advanced filtering
- `count` - Count leads matching criteria
- `update` - Update leads and their properties
- `distribute` - Distribute leads among users
- `users` - User management utilities

## 🔍 Query Command Examples

### Basic Query
```bash
# Get all leads
odlm query

# Get leads with table output
odlm query --format table

# Get leads with CSV output
odlm query --format csv --output leads.csv
```

### Date Filtering
```bash
# Get leads older than 2 months
odlm query --date-filter older_than_2_months

# Get leads from last 30 days
odlm query --date-filter last_30_days

# Get leads from this month
odlm query --date-filter this_month

# Get leads from specific date range
odlm query --date-from 2024-01-01 --date-to 2024-01-31

# Get leads older than 1 week
odlm query --date-filter older_than_1_week
```

### User-Based Filtering
```bash
# Get leads assigned to specific user
odlm query --user "Naidene"

# Get leads assigned to multiple users
odlm query --user "Alice Smith,Bob Johnson"

# Get leads by closer
odlm query --closer "Alice Smith"

# Get leads by open user
odlm query --open-user "Bob Johnson"
```

### Status Filtering
```bash
# Get new leads
odlm query --status new

# Get leads with multiple statuses
odlm query --status new,in_progress

# Get won leads
odlm query --status won
```

### Combined Filtering
```bash
# Get leads older than 2 months assigned to Naidene
odlm query --date-filter older_than_2_months --user "Naidene"

# Get new leads from website source
odlm query --status new --source Website

# Get leads with specific tags
odlm query --tags "VIP,Hot Lead"
```

### Advanced Filtering
```bash
# Get leads with specific name pattern
odlm query --name "John"

# Get leads with specific email domain
odlm query --email "@company.com"

# Get leads with specific phone pattern
odlm query --phone "555"
```

### Output Customization
```bash
# Get specific fields
odlm query --fields id,name,email,status,user_id

# Limit results
odlm query --limit 50

# Paginate results
odlm query --offset 100 --limit 25

# Sort results
odlm query --order "create_date desc"

# Save to file
odlm query --format csv --output leads_report.csv
```

## 📝 Update Command Examples

### Update by IDs
```bash
# Update specific leads
odlm update --ids 1,2,3 --user-id 5

# Update leads and change status
odlm update --ids 1,2,3 --status in_progress

# Update multiple fields
odlm update --ids 1,2,3 --user-id 5 --closer-id 6 --status won
```

### Update by Query (Chained Operations)
```bash
# Find leads older than 2 months assigned to Naidene and reassign to Administrator
odlm update --user "Naidene" --date-filter older_than_2_months --user-name "Administrator"

# Find new leads and change status
odlm update --status new --date-filter last_7_days --status in_progress

# Complex chained operation
odlm update --query '{"status": "new", "user_id": {"ilike": "Naidene"}}' --user-name "Administrator" --status assigned
```

### Update by Name
```bash
# Update leads and assign to user by name
odlm update --ids 1,2,3 --user-name "Alice Smith"

# Update closer by name
odlm update --ids 1,2,3 --closer-name "Bob Johnson"

# Update open user by name
odlm update --ids 1,2,3 --open-user-name "Carol Williams"
```

### JSON Fields Update
```bash
# Update multiple custom fields
odlm update --ids 1,2,3 --fields '{"priority": "high", "notes": "Updated via CLI"}'
```

## 📊 Count Command Examples

### Basic Counting
```bash
# Count all leads
odlm count

# Count new leads
odlm count --status new

# Count leads older than 1 month
odlm count --date-filter older_than_1_month
```

### Complex Counting
```bash
# Count leads assigned to specific user
odlm count --user "Naidene"

# Count leads with multiple criteria
odlm count --status new --source Website --user "Alice Smith"
```

## 🔄 Distribute Command Examples

### Basic Distribution
```bash
# Distribute new leads proportionally
odlm distribute --status new

# Distribute leads from last week round-robin style
odlm distribute --date-filter last_7_days --strategy round_robin
```

### Strategy Selection
```bash
# Use least-loaded strategy
odlm distribute --status new --strategy least_loaded

# Use weighted random strategy
odlm distribute --status new --strategy weighted_random
```

### Dry Run Mode
```bash
# Preview distribution without applying
odlm distribute --status new --strategy proportional --dry-run
```

## 👥 User Management

### List Users
```bash
# List all users
odlm users --list

# Show user lead counts
odlm users --counts
```

## 🔧 Configuration Examples

### Interactive Configuration
```bash
# Configure credentials interactively
odlm configure

# Configure to a specific file
odlm configure --file production.env

# Overwrite existing configuration
odlm configure --overwrite
```

### Configuration Process
```bash
$ odlm configure
🛠️  Odoo Lead Manager Configuration
==================================================
📁 Configuration will be saved to: .env
💡 Press Enter to use default values shown in [brackets]

Odoo Server Host [localhost]: my-odoo-server.com
Odoo Server Port [8069]: 8069
Database Name [odoo]: my_database
Username [admin]: my_user
Password: ********

✅ Configuration saved successfully!
📄 File: .env
🔒 Permissions: Set to owner-only access

🧪 Testing new configuration...
✅ Configuration test successful!
   Connected to: my-odoo-server.com:8069
   Database: my_database
   Odoo Version: 16.0
```

## 🔍 Connection Check Examples

### Basic Connection Check
```bash
# Check if Odoo server is accessible
odlm check

# Detailed connection information
odlm check --verbose
```

### Connection Troubleshooting
```bash
# Test connection and show configuration
odlm check

# Example output:
🔍 Odoo Connection Check
========================================
Server: localhost:8069
Database: odoo
Username: admin

🌐 Testing connection...
✅ Connection successful!
Odoo Version: 16.0
Server Name: Odoo Server
Connected as: Administrator (admin)
✅ res.partner model accessible
```

### Failed Connection Example
```bash
odlm check
🔍 Odoo Connection Check
========================================
Server: localhost:8069
Database: odoo
Username: admin

🌐 Testing connection...
❌ Connection failed: [Errno 61] Connection refused

💡 Troubleshooting:
  1. Check if Odoo server is running
  2. Verify host and port in .env file
  3. Check database name and credentials
  4. Ensure Odoo RPC is enabled
  5. Run 'odlm configure' to set up credentials
```

## 🎯 Practical Examples

### Example 1: Find and Reassign Old Leads
```bash
# Find leads older than 2 months assigned to Naidene
odlm query --date-filter older_than_2_months --user "Naidene" --format table

# Count them
odlm count --date-filter older_than_2_months --user "Naidene"

# Reassign all to Administrator
odlm update --user "Naidene" --date-filter older_than_2_months --user-name "Administrator"
```

### Example 2: Weekly Lead Management
```bash
#!/bin/bash
# Weekly script to process new leads

# Get new leads from last week
echo "=== New Leads This Week ==="
odlm query --date-filter last_7_days --status new --format table

# Count them
echo "Count: $(odlm count --date-filter last_7_days --status new)"

# Distribute new leads
echo "=== Distributing New Leads ==="
odlm distribute --date-filter last_7_days --status new --strategy proportional
```

### Example 3: Export to CSV
```bash
# Export all new leads to CSV
odlm query --status new --format csv --output new_leads.csv

# Export specific date range
odlm query --date-from 2024-01-01 --date-to 2024-01-31 --format csv --output january_leads.csv

# Export with specific fields
odlm query --fields id,name,email,phone,status,user_id --format csv --output leads_with_contact.csv
```

### Example 4: Batch Operations
```bash
# Find leads from specific source and reassign
odlm query --source "Website" --format table
odlm update --source "Website" --user-name "Alice Smith"

# Find high-priority leads and change status
odlm query --tags "VIP" --status new --format table
odlm update --tags "VIP" --status new --status in_progress
```

## 🔧 Advanced Usage

### Chaining Operations
```bash
# One-liner: Find leads older than 1 month and reassign
odlm query --date-filter older_than_1_month --user "Naidene" --format table && \
odlm update --user "Naidene" --date-filter older_than_1_month --user-name "Administrator"

# Using xargs for bulk operations
odlm query --status new --fields id --format json | jq -r '.[].id' | \
xargs -I {} odlm update --ids {} --status assigned --user-id 5
```

### JSON Query Filters
```bash
# Complex query using JSON
odlm update --query '{"status": "new", "create_date": {"<": "2024-01-01"}}' \
            --user-name "Administrator" --status assigned
```

### Environment-Specific Usage
```bash
# Use with different environment files
ODOO_HOST=prod-server.com ODOO_DB=production odlm query --status new

# Use with development database
ODOO_HOST=localhost ODOO_DB=dev odlm query --limit 10
```

## 📝 Date Filter Reference

| Filter | Description | Example |
|--------|-------------|---------|
| `today` | Today's leads | `--date-filter today` |
| `yesterday` | Yesterday's leads | `--date-filter yesterday` |
| `older_than_X_days` | Leads older than X days | `--date-filter older_than_30_days` |
| `older_than_X_weeks` | Leads older than X weeks | `--date-filter older_than_2_weeks` |
| `older_than_X_months` | Leads older than X months | `--date-filter older_than_3_months` |
| `older_than_X_years` | Leads older than X years | `--date-filter older_than_1_year` |
| `last_X_days` | Leads from last X days | `--date-filter last_7_days` |
| `last_X_weeks` | Leads from last X weeks | `--date-filter last_2_weeks` |
| `last_X_months` | Leads from last X months | `--date-filter last_3_months` |
| `this_week` | This week's leads | `--date-filter this_week` |
| `this_month` | This month's leads | `--date-filter this_month` |
| `YYYY-MM-DD` | Specific date | `--date-filter 2024-01-15` |

## 🎨 Output Formats

### Table Format (Default)
```
+----+------------+---------------------+--------+-------------+
| ID | Name       | Email               | Status | User        |
+====+============+=====================+========+=============+
| 1  | John Doe   | john@example.com    | new    | Alice Smith |
| 2  | Jane Smith | jane@example.com    | won    | Bob Johnson |
+----+------------+---------------------+--------+-------------+
```

### CSV Format
```csv
id,name,email,status,user_id
1,John Doe,john@example.com,new,Alice Smith
2,Jane Smith,jane@example.com,won,Bob Johnson
```

### JSON Format
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "status": "new",
    "user_id": [1, "Alice Smith"]
  }
]
```

## 🔍 Troubleshooting

### Connection Issues
```bash
# Check .env file
odlm query --help  # Should show help without connection errors

# Test with explicit credentials
odlm query --host localhost --port 8069 --db test_db --user admin --password admin
```

### Permission Issues
```bash
# Check user permissions
odlm users --list

# Verify user exists
odlm users --counts
```

### Complex Queries
```bash
# Debug query with verbose output
odlm query --status new --user "Naidene" --format table

# Check field availability
odlm query --limit 1 --format json | jq '.[0] | keys'
```

## 📚 Script Examples

### Daily Lead Processing Script
```bash
#!/bin/bash
# daily_leads.sh

echo "=== Daily Lead Processing ==="
date

echo "1. Counting new leads..."
NEW_COUNT=$(odlm count --status new)
echo "New leads: $NEW_COUNT"

echo "2. Processing old leads..."
OLD_LEADS=$(odlm count --date-filter older_than_2_months)
echo "Old leads: $OLD_LEADS"

if [ "$OLD_LEADS" -gt 0 ]; then
    echo "3. Reassigning old leads..."
    odlm update --date-filter older_than_2_months --status new --user-name "Follow-up Team"
fi

echo "4. Exporting daily report..."
odlm query --date-filter today --format csv --output "daily_report_$(date +%Y%m%d).csv"

echo "=== Processing Complete ==="
```

This CLI provides a comprehensive interface for all lead management operations with intuitive commands and powerful filtering capabilities!