# CLI Installation & Quick Start Guide

## 🚀 Installation Steps

### 1. Install Package with CLI Support
```bash
# Install in development mode with CLI dependencies
pip install -e ".[dev]"

# Or install manually
pip install -e .
pip install tabulate
```

### 2. Verify Installation
```bash
# Test CLI installation
odlm --help
# or
odoo-lead-manager --help
```

### 3. Configure Environment
```bash
# Copy and configure .env file
cp .env.example .env
# Edit .env with your Odoo credentials:
# ODOO_HOST=your-odoo-server.com
# ODOO_PORT=8069
# ODOO_DB=your_database
# ODOO_USERNAME=your_username
# ODOO_PASSWORD=your_password
```

## ✅ Quick Start Examples

### Basic Querying
```bash
# Test basic functionality
echo "=== Testing CLI ==="
python test_cli.py

# Show all commands
odlm --help

# Show specific command help
odlm query --help
odlm update --help
odlm count --help
```

### Your Requested Example
```bash
# Find leads older than 2 months assigned to Naidene
odlm query --date-filter older_than_2_months --user "Naidene" --format table

# Count them
odlm count --date-filter older_than_2_months --user "Naidene"

# Reassign them to Administrator
odlm update --date-filter older_than_2_months --user "Naidene" --user-name "Administrator" --status reassigned
```

### Test Environment Setup
```bash
# Test with mock data (if you have test environment)
ODOO_HOST=localhost ODOO_PORT=8069 ODOO_DB=test_db ODOO_USERNAME=admin ODOO_PASSWORD=admin odlm query --limit 5
```

## 🎯 Common Usage Patterns

### Pattern 1: Find and Reassign Old Leads
```bash
# Complete workflow for finding old leads and reassigning
odlm query --date-filter older_than_2_months --user "Naidene" --format table
odlm count --date-filter older_than_2_months --user "Naidene"
odlm update --date-filter older_than_2_months --user "Naidene" --user-name "Administrator" --status reassigned
```

### Pattern 2: Daily Lead Processing
```bash
# Daily script example
odlm query --date-filter last_24_hours --status new --format csv --output daily_new_leads.csv
odlm count --date-filter last_7_days --status new
odlm distribute --date-filter last_7_days --status new --strategy proportional
```

### Pattern 3: Export Reports
```bash
# Export comprehensive reports
odlm query --format csv --output all_leads.csv
odlm query --status new --format table --fields id,name,email,status,user_id
```

## 🔧 Troubleshooting

### Import Errors
```bash
# If you get import errors, reinstall:
pip install -e .
pip install tabulate
```

### Environment Issues
```bash
# Test environment variables
echo $ODOO_HOST
echo $ODOO_PORT

# Test with explicit credentials
odlm query --host localhost --port 8069 --db test_db --user admin --password admin --limit 1
```

### CLI Not Found
```bash
# Ensure package is properly installed
which odlm
which odoo-lead-manager

# Alternative: Run directly
python -m odoo_lead_manager.cli --help
```

## 📋 CLI Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `query` | Query leads with filters | `odlm query --status new --limit 10` |
| `count` | Count matching leads | `odlm count --date-filter older_than_2_months` |
| `update` | Update lead properties | `odlm update --ids 1,2,3 --user-name "Admin"` |
| `distribute` | Distribute leads among users | `odlm distribute --status new --strategy proportional` |
| `users` | User management | `odlm users --list` |

## 🎯 Quick Test

Run this to verify everything works:
```bash
echo "Testing CLI installation..."
odlm --help | head -20
echo "✅ CLI installed successfully!"
```

## 🚀 Ready to Use!

Your CLI is now ready with all requested features:
- ✅ .env file credential support
- ✅ Advanced date filtering ("older_than_2_months")
- ✅ User-based filtering ("Naidene")
- ✅ CSV and table output
- ✅ Chained operations (query → update)
- ✅ Comprehensive filtering capabilities

Start using: `odlm query --date-filter older_than_2_months --user 