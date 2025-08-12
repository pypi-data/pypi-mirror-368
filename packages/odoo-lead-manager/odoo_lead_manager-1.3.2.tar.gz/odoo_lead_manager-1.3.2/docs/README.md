# Odoo Lead Manager

A comprehensive Python package for managing Odoo leads with advanced filtering capabilities and smart distribution algorithms.

## Features

- **Robust Odoo API Client**: Secure connection and authentication with Odoo instances
- **Advanced Lead Filtering**: Multiple criteria including date ranges, web source IDs, status, and user assignments
- **Smart Lead Distribution**: Intelligent algorithms for fair lead distribution based on user capacity and expected proportions
- **Comprehensive Analytics**: Lead characteristics, user statistics, and distribution reports
- **Export Capabilities**: DataFrame export for further analysis
- **Well-Tested**: Extensive unit test coverage with mocking support

## Installation

### From Source
```bash
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Command Line Interface (CLI)

The Odoo Lead Manager provides a comprehensive CLI for easy lead management:

```bash
# Install the package
pip install -e .

# Check connection to Odoo
odlm check

# Configure credentials interactively
odlm configure

# Get leads with various filters
odlm leads --status "new" --limit 50
odlm leads --user "Alice Smith" --format csv --output alice_leads.csv
odlm leads --date-from 2024-01-01 --date-to 2024-01-31 --count

# Update lead assignments
odlm update --ids "1,2,3" --user-name "Bob Johnson"
odlm update --from-csv leads.csv --status "in_progress"

# Count leads
odlm count --status "won" --date-filter "this_month"

# Query invoices
odlm invoices --date-from 2024-01-01 --format csv --output invoices.csv

# Join leads with invoice data
odlm join --lead-status "won" --invoice-state "paid"
```

### 2. Python API Setup

```python
from odoo_lead_manager import OdooClient, LeadManager, SmartDistributor

# Configure Odoo connection
client = OdooClient(
    host="your-odoo-server.com",
    port=8069,
    database="your_database",
    username="your_username",
    password="your_password"
)

# Initialize lead manager
lead_manager = LeadManager(client)
```

### 2. Environment Variables

You can also use environment variables:

```bash
export ODOO_HOST=your-odoo-server.com
export ODOO_PORT=8069
export ODOO_DB=your_database
export ODOO_USERNAME=your_username
export ODOO_PASSWORD=your_password
```

Then just use:
```python
client = OdooClient()
```

## CLI Usage Examples

### Basic Commands

#### Connection and Configuration
```bash
# Test connection to Odoo
odlm check

# Interactive configuration setup
odlm configure

# Check with verbose output
odlm check --verbose
```

#### Lead Management
```bash
# Get all leads in table format
odlm leads --format table

# Get new leads with limit
odlm leads --status "new" --limit 50

# Export leads to CSV
odlm leads --format csv --output leads.csv

# Get leads for specific user
odlm leads --user "Alice Smith"

# Get leads from date range
odlm leads --date-from 2024-01-01 --date-to 2024-01-31

# Count leads by status
odlm count --status "won"
```

#### Lead Updates
```bash
# Assign specific leads to user
odlm update --ids "1,2,3" --user-name "Bob Johnson"

# Update leads from CSV file
odlm update --from-csv leads.csv --user-name "Alice Smith"

# Update status and assign closer
odlm update --ids "100,101,102" --status "in_progress" --closer-name "Senior Manager"

# Update leads from text file
odlm update --from-file lead_ids.txt --status "assigned"
```

#### Advanced Filtering
```bash
# Date-based filtering
odlm leads --date-filter "last_30_days"
odlm leads --date-filter "this_month"
odlm leads --date-filter "older_than_2_months"

# Source-based filtering
odlm leads --web-source-ids "facebook_form,google_ads,website"

# Team and user filtering
odlm leads --team "Sales Team" --user "Alice"

# Campaign filtering
odlm leads --campaign "Summer Sale 2024"
```

#### Analytics and Reporting
```bash
# Group leads by user and status
odlm leads --group-by "user_id,status"

# Pivot table analysis
odlm leads --pivot-rows "user_id" --pivot-cols "status"

# Export for analysis
odlm leads --fields "id,name,email,phone,user_id,status" --format json --output analysis.json
```

#### Invoice Management
```bash
# Query invoices
odlm invoices --date-from 2024-01-01 --limit 100

# Export invoices to CSV
odlm invoices --format csv --output invoices.csv

# Filter by amount
odlm invoices --amount-min 1000 --amount-max 5000

# Filter by state
odlm invoices --state "paid" --date-from 2024-01-01
```

#### Lead-Invoice Analysis
```bash
# Join leads with invoice data
odlm join --lead-status "won" --invoice-state "paid"

# Export conversion analysis
odlm join --lead-date-from 2024-01-01 --format csv --output conversion_analysis.csv

# Filter by user performance
odlm join --lead-user "Alice Smith" --invoice-date-from 2024-01-01
```

### Comprehensive CLI Examples

#### Lead Management Workflows

**Daily Operations:**
```bash
# Morning lead review
odlm leads --status "new" --limit 50 --format table

# Assign new leads to sales team
odlm update --from-csv morning_leads.csv --user-name "Alice Smith"

# Check team performance
odlm leads --user "Alice Smith" --date-filter "this_month" --group-by "status"
```

**Weekly Reporting:**
```bash
# Weekly lead summary
odlm leads --date-filter "last_7_days" --group-by "user_id,status" --format csv --output weekly_report.csv

# Source performance analysis
odlm leads --date-filter "last_7_days" --pivot-rows "web_source_id" --pivot-cols "status"

# Export for analysis
odlm leads --date-filter "last_7_days" --fields "id,name,email,phone,user_id,status,web_source_id" --format json --output weekly_data.json
```

**Campaign Management:**
```bash
# Campaign lead assignment
odlm update --query '{"campaign_id.name": "Summer Sale 2024", "status": "new"}' --user-name "Campaign Team"

# Campaign performance
odlm leads --campaign "Summer Sale 2024" --date-filter "this_month" --group-by "status"

# Export campaign data
odlm leads --campaign "Summer Sale 2024" --format csv --output summer_sale_leads.csv
```

#### Advanced Analytics

**Sales Performance:**
```bash
# Individual salesperson performance
odlm leads --user "Alice Smith" --date-filter "this_month" --pivot-rows "status" --pivot-cols "web_source_id"

# Team comparison
odlm leads --team "Sales Team" --date-filter "this_month" --group-by "user_id,status"

# Conversion analysis
odlm join --lead-status "won" --lead-date-from 2024-01-01 --format csv --output conversions.csv
```

**Revenue Analysis:**
```bash
# Invoice analysis
odlm invoices --date-from 2024-01-01 --state "paid" --format csv --output revenue.csv

# Lead-to-revenue mapping
odlm join --lead-status "won" --invoice-state "paid" --lead-date-from 2024-01-01

# Source ROI
odlm join --lead-source "Facebook" --invoice-state "paid" --format csv --output facebook_roi.csv
```

#### Data Export and Integration

**Automated Reports:**
```bash
# Daily CSV export
odlm leads --date-filter "today" --format csv --output daily_leads_$(date +%Y%m%d).csv

# Monthly JSON export for API integration
odlm leads --date-filter "this_month" --format json --output monthly_data.json

# User-specific exports
odlm leads --user "Alice Smith" --date-filter "this_month" --format csv --output alice_monthly.csv
```

**Batch Processing:**
```bash
# Large dataset processing
odlm leads --date-from 2024-01-01 --date-to 2024-12-31 --format csv --output yearly_data.csv

# Incremental updates
odlm update --from-csv batch_1.csv --user-name "Team A"
odlm update --from-csv batch_2.csv --user-name "Team B"
```

#### Quality Assurance

**Data Validation:**
```bash
# Check for unassigned leads
odlm leads --status "new" --user "" --count

# Validate lead quality
odlm leads --status "new" --fields "id,name,email,phone,web_source_id" --limit 100

# Review old leads
odlm leads --date-filter "older_than_2_months" --status "new" --format table
```

**Error Handling:**
```bash
# Debug mode for troubleshooting
odlm update --ids "1,2,3" --user-name "Alice" --debug

# Quiet mode for automation
odlm update --from-csv large_batch.csv --user-name "Bob" --quiet

# Validation before update
odlm leads --ids "1,2,3" --format table  # Check leads exist first
```

## Python API Usage Examples

### Fetching Leads

#### Basic Lead Retrieval
```python
# Get all leads
leads = lead_manager.get_leads()

# Get leads with specific fields
leads = lead_manager.get_leads(fields=["id", "name", "email", "status"])

# Get leads with limit and offset
leads = lead_manager.get_leads(limit=50, offset=100)
```

#### Date Range Filtering
```python
from datetime import date

# Get leads from January 2024
leads = lead_manager.get_leads_by_date_range(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31)
)

# Get leads after specific date
leads = lead_manager.get_leads_by_date_range(
    start_date=date(2024, 1, 1)
)
```

#### Web Source Filtering
```python
# Single source
leads = lead_manager.get_leads_by_source("Website")

# Multiple sources
leads = lead_manager.get_leads_by_source(["Website", "Email Campaign", "Social Media"])
```

#### Status Filtering
```python
from odoo_lead_manager.filters import LeadStatus

# Single status
leads = lead_manager.get_leads_by_status("new")

# Multiple statuses
leads = lead_manager.get_leads_by_status(["new", "in_progress", "won"])

# Using enum
leads = lead_manager.get_leads_by_status([LeadStatus.NEW, LeadStatus.WON])
```

#### User Assignment Filtering
```python
# By user IDs
leads = lead_manager.get_leads_by_users(user_ids=[1, 2, 3])

# By user names
leads = lead_manager.get_leads_by_users(user_names=["Alice Smith", "Bob Johnson"])

# By closer IDs
leads = lead_manager.get_leads_by_users(closer_ids=[1, 2])

# By open user IDs
leads = lead_manager.get_leads_by_users(open_user_ids=[1, 2])

# Combined filtering
leads = lead_manager.get_leads_by_users(
    user_ids=[1, 2],
    closer_names=["Alice Smith"],
    open_user_names=["Bob Johnson"]
)
```

### Advanced Filtering with LeadFilter

```python
from odoo_lead_manager.filters import LeadFilter

# Complex filtering with chaining
filter_obj = LeadFilter() \
    .by_date_range(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        field_name="create_date"
    ) \
    .by_status(["new", "in_progress"]) \
    .by_web_source_ids(["Website", "Email Campaign"]) \
    .by_user_assignments(user_ids=[1, 2, 3]) \
    .by_customer_name("John", exact=False) \
    .by_email("@company.com") \
    .by_tags(["VIP", "Hot Lead"]) \
    .limit(100) \
    .offset(50) \
    .order("create_date desc")

leads = lead_manager.get_leads(filter_obj)
```

### Lead Analysis and Summary

```python
# Get comprehensive lead summary
summary = lead_manager.get_lead_summary()

print(f"Total leads: {summary['total_leads']}")
print(f"Statistics: {summary['statistics']}")
print(f"User assignments: {summary['user_assignments']}")
print(f"Source distribution: {summary['source_distribution']}")
print(f"Status distribution: {summary['status_distribution']}")
print(f"Geographic distribution: {summary['geographic_distribution']}")

# Export to DataFrame for analysis
import pandas as pd
df = lead_manager.export_to_dataframe(filter_obj)
print(df.head())
```

### Smart Lead Distribution

#### Basic Setup
```python
# Initialize distributor
distributor = SmartDistributor()

# Add users with their profiles
users = [
    UserProfile(
        user_id=1, 
        name="Alice Smith", 
        current_leads=10, 
        expected_percentage=40.0, 
        max_capacity=50
    ),
    UserProfile(
        user_id=2, 
        name="Bob Johnson", 
        current_leads=15, 
        expected_percentage=35.0, 
        max_capacity=40
    ),
    UserProfile(
        user_id=3, 
        name="Carol Williams", 
        current_leads=5, 
        expected_percentage=25.0, 
        max_capacity=30
    )
]

for user in users:
    distributor.add_user_profile(user)
```

#### Load Users from Odoo
```python
# Load existing users and their current lead counts
distributor.load_user_profiles_from_odoo(lead_manager)

# Load expected proportions from Odoo table
distributor.load_proportions_from_odoo(lead_manager)
```

#### Distribute Leads
```python
from odoo_lead_manager.distribution import Lead

# Prepare leads for distribution
leads = [
    Lead(lead_id=101, name="Hot Lead A", source_id="web", priority=3),
    Lead(lead_id=102, name="Warm Lead B", source_id="email", priority=2),
    Lead(lead_id=103, name="Cold Lead C", source_id="referral", priority=1),
]

# Choose distribution strategy
distributor.set_distribution_strategy(DistributionStrategy.PROPORTIONAL)

# Distribute leads
assignments = distributor.distribute_leads(leads)

# Apply assignments to Odoo
for user_id, lead_ids in assignments.items():
    lead_manager.update_lead_assignments(lead_ids, user_id=user_id)
```

#### Distribution Strategies
```python
# Available strategies:
from odoo_lead_manager.distribution import DistributionStrategy

strategies = [
    DistributionStrategy.PROPORTIONAL,      # Based on expected percentages
    DistributionStrategy.ROUND_ROBIN,       # Equal rotation
    DistributionStrategy.LEAST_LOADED,      # To users with fewest leads
    DistributionStrategy.WEIGHTED_RANDOM,   # Random with percentage weights
    DistributionStrategy.CAPACITY_BASED,    # Based on remaining capacity
]

# Change strategy
distributor.set_distribution_strategy(DistributionStrategy.LEAST_LOADED)
```

#### Distribution Reports
```python
# Get detailed distribution report
report = distributor.get_distribution_report()

print(f"Total users: {report['total_users']}")
print(f"Active users: {report['active_users']}")

for user_id, details in report['user_details'].items():
    print(f"User {details['name']}: {details['current_leads']} leads")
    print(f"  Expected: {details['expected_leads']}")
    print(f"  Deviation: {details['deviation']}")
    print(f"  Utilization: {details['utilization_rate']}%")
```

### Save and Load Proportions

```python
# Save current proportions to Odoo table
distributor.save_proportions_to_odoo(lead_manager, "lead_distribution_proportions")

# Load proportions from Odoo table
distributor.load_proportions_from_odoo(lead_manager, "lead_distribution_proportions")
```

## Configuration File

Create a `.env` file in your project root:

```bash
# Odoo Connection
ODOO_HOST=your-odoo-server.com
ODOO_PORT=8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional Settings
ODOO_PROTOCOL=jsonrpc
ODOO_TIMEOUT=120
```

## Testing

### Run All Tests
```bash
python run_tests.py
```

### Run with Coverage
```bash
python run_tests.py --coverage
```

### Run Specific Tests
```bash
python run_tests.py --pattern "test_lead*"
python run_tests.py --specific tests/test_filters.py::TestLeadFilter::test_by_date_range_both_dates
```

### Using pytest directly
```bash
pytest tests/
pytest tests/ -v --cov=src/odoo_lead_manager
```

## CLI Reference

### Available Commands

#### `odlm check`
Test connection to Odoo server and validate credentials.
```bash
odlm check [--verbose]
```

#### `odlm configure`
Interactive setup of Odoo credentials.
```bash
odlm configure [--file .env] [--overwrite]
```

#### `odlm leads`
Get leads with advanced filtering, grouping, and pivot capabilities.
```bash
odlm leads [OPTIONS]
```

**Key Options:**
- `--status`: Filter by lead status (new, in_progress, won, lost, etc.)
- `--date-from/--date-to`: Date range filtering
- `--user`: Filter by assigned user name
- `--team`: Filter by sales team name
- `--source`: Filter by source name
- `--web-source-ids`: Comma-separated web source names
- `--format`: Output format (table, csv, json)
- `--output`: Output file
- `--group-by`: Group by columns
- `--pivot-rows/--pivot-cols`: Pivot table analysis
- `--count`: Count results only

#### `odlm update`
Update lead assignments, status, or other fields.
```bash
odlm update [OPTIONS]
```

**Key Options:**
- `--ids`: Comma-separated list of lead IDs
- `--from-csv/--from-tsv/--from-file`: Read IDs from files
- `--user-name/--user-id`: Assign to user
- `--closer-name/--closer-id`: Set closer
- `--status`: Update lead status
- `--model`: Odoo model to update (default: crm.lead)

#### `odlm count`
Count leads matching filter criteria.
```bash
odlm count [OPTIONS]
```

#### `odlm invoices`
Query invoice data from account.invoice model.
```bash
odlm invoices [OPTIONS]
```

**Key Options:**
- `--date-from/--date-to`: Date range filtering
- `--partner-id`: Filter by customer ID
- `--state`: Filter by invoice state (draft, open, paid, cancel)
- `--amount-min/--amount-max`: Amount range filtering
- `--format`: Output format (table, csv, json)

#### `odlm join`
Join leads with invoice data based on partner relationships.
```bash
odlm join [OPTIONS]
```

**Key Options:**
- `--lead-date-from/--lead-date-to`: Lead date filtering
- `--lead-status`: Filter leads by status
- `--lead-user`: Filter leads by user
- `--invoice-state`: Filter invoices by state
- `--exclude-unmatched`: Exclude leads without invoices

### Date Filter Examples

```bash
# Relative date filters
odlm leads --date-filter "today"
odlm leads --date-filter "yesterday"
odlm leads --date-filter "last_7_days"
odlm leads --date-filter "last_30_days"
odlm leads --date-filter "this_month"
odlm leads --date-filter "older_than_2_months"

# Exact dates
odlm leads --date-from 2024-01-01 --date-to 2024-01-31
```

### File Input Formats

#### CSV/TSV Files
- Must have 'id' column (or first column will be used)
- Supports Odoo export format: `__export__.crm_lead_12345_abcdef123`

#### Text Files
- One ID per line
- Supports comments with `#` prefix
- Supports Odoo export format

### Output Formats

#### Table Format (Default)
Pretty-printed tables with grid formatting

#### CSV Format
Standard CSV output for spreadsheet applications

#### JSON Format
Structured JSON for API integration and data processing

## Python API Reference

### OdooClient
- `connect()`: Establish connection to Odoo
- `authenticate()`: Authenticate with credentials
- `search_read()`: Search and read records
- `search_count()`: Count matching records
- `write()`: Update records
- `create()`: Create new records
- `unlink()`: Delete records

### LeadFilter
- `by_date_range()`: Filter by date range
- `by_web_source_ids()`: Filter by web source IDs
- `by_status()`: Filter by lead status
- `by_user_assignments()`: Filter by user assignments
- `by_customer_name()`: Filter by customer name
- `by_email()`: Filter by email
- `by_phone()`: Filter by phone
- `by_tags()`: Filter by tags
- `build()`: Build final filter configuration

### LeadManager
- `get_leads()`: Get leads with filters
- `get_leads_by_date_range()`: Get leads by date range
- `get_leads_by_source()`: Get leads by source
- `get_leads_by_status()`: Get leads by status
- `get_leads_by_users()`: Get leads by user assignments
- `count_leads()`: Count matching leads
- `get_lead_summary()`: Get comprehensive summary
- `update_lead_assignments()`: Update lead assignments
- `get_user_lead_counts()`: Get user lead counts
- `export_to_dataframe()`: Export to pandas DataFrame

### SmartDistributor
- `add_user_profile()`: Add user profile
- `remove_user_profile()`: Remove user profile
- `update_user_current_leads()`: Update user lead count
- `distribute_leads()`: Distribute leads among users
- `get_distribution_report()`: Get distribution statistics
- `load_user_profiles_from_odoo()`: Load users from Odoo
- `save_proportions_to_odoo()`: Save proportions to Odoo
- `load_proportions_from_odoo()`: Load proportions from Odoo

## Troubleshooting

### CLI Issues

#### Connection Problems
```bash
# Test connection
odlm check

# Check with verbose output
odlm check --verbose

# Reconfigure credentials
odlm configure
```

**Common Issues:**
- Verify Odoo server is accessible
- Check credentials and permissions
- Ensure correct port and protocol
- Check firewall settings

#### Command Not Found
```bash
# Install in development mode
pip install -e .

# Check installation
pip list | grep odoo-lead-manager
```

#### File Input Issues
- **CSV Format**: Ensure file has 'id' column or first column contains IDs
- **Text Files**: One ID per line, supports comments with `#`
- **Odoo Export Format**: Supports `__export__.crm_lead_12345_abcdef123` format

#### Update Command Issues
- **Non-existent Lead IDs**: System validates all IDs against crm.lead model
- **ID Validation**: Comprehensive search across all crm.lead records
- **Model Flexibility**: Use `--model` parameter for different Odoo models
- **User Resolution**: Automatic name-to-ID resolution with error reporting

### Python API Issues

#### Import Issues
- Install package in development mode: `pip install -e .`
- Check Python path includes src directory

#### Test Failures
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check for environment variable conflicts
- Verify mock setup in test configuration

### Common Error Messages

#### "Failed to connect to Odoo"
- Check server is running
- Verify host and port
- Test network connectivity

#### "User not found"
- Use exact user names
- Check user exists in Odoo
- Use `odlm users --list` to see available users

#### "No leads found"
- Verify filter criteria
- Check date formats (YYYY-MM-DD)
- Ensure status values are correct

#### "Permission denied"
- Check user permissions in Odoo
- Verify database access rights
- Ensure proper authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the test examples
- Open an issue on GitHub