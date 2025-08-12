# Daily Lead Distribution System

This document describes the implementation of the daily lead distribution system for ODLM (Odoo Lead Manager) based on the detailed specification in `DAILY_LEAD_DISTRIBUTION_REQUIREMENTS.md`.

## Overview

The daily distribution system provides automated lead distribution based on configurable criteria, current workload, and distribution strategies. It supports multiple salesperson selection methods, enhanced lead filtering, and various distribution algorithms.

## Key Features

### 1. Configuration-Driven Design
- YAML/JSON configuration files control all aspects of distribution
- Environment variable support for secure credential management
- Multiple configuration templates (basic, advanced, minimal)

### 2. Salesperson Selection
- **Campaign Table**: CSV file with salesperson-campaign relationships
- **File-based**: Legacy text file support
- **List-based**: Direct configuration lists
- **Database**: Direct Odoo queries
- Campaign filtering (Voice, Apple, etc.)
- User exclusions and workload balancing

### 3. Enhanced Lead Filtering
- Date range filtering (30-day window by default)
- Web source filtering with case-sensitive matching
- Campaign filtering for lead campaigns
- Status filtering with configurable matching modes
- DNC (Do Not Call) filtering
- Tag-based filtering
- Field validation and priority filtering

### 4. Distribution Strategies
- **Level-based**: Distribute based on seniority levels and target leads
- **Round-robin**: Simple round-robin distribution
- **Proportional**: Distribute based on current workload ratios
- **Capacity-based**: Advanced capacity management

### 5. Performance Tracking
- Pre/post distribution lead counts
- Assignment history tracking
- Distribution efficiency metrics
- Database integration for analytics

## Installation

The daily distribution system is included in the main ODLM package. No additional installation is required beyond the standard dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Configuration File

```bash
# Generate basic configuration
odlm dailydist --generate-config --output daily_distribution_config.yaml

# Generate configuration for specific campaign
odlm dailydist --generate-config --campaign Voice --template advanced --output voice_config.yaml

# Generate minimal configuration
odlm dailydist --generate-config --template minimal --output minimal_config.yaml
```

### 2. Configure Environment Variables

Set up your environment variables in a `.env` file:

```bash
# Odoo Connection
ODOO_HOST=your-odoo-server.com
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional: MySQL Tracking Database
TRACKING_DB_HOST=localhost
TRACKING_DB_NAME=lead_distribution_tracking
TRACKING_DB_USER=tracking_user
TRACKING_DB_PASSWORD=tracking_password
```

### 3. Create Supporting Files

Create the required supporting files:

**config/salesperson_campaigns.csv:**
```csv
salesperson_name,salesperson_id,campaign_name,active,team,level,target_leads
alice_smith,1,Voice,true,Voice,senior,200
bob_johnson,2,Voice,true,Voice,senior,200
carol_williams,3,Voice,true,Voice,mid_level,150
```

**config/web_sources.txt:**
```
facebook_form
google_ads
website_contact
linkedin_ads
```

### 4. Run Daily Distribution

```bash
# Basic distribution
odlm dailydist --config daily_distribution_config.yaml

# Dry run to see what would be distributed
odlm dailydist --config config.yaml --dry-run

# Override settings
odlm dailydist --config config.yaml --max-leads 100 --override-date-range "2024-01-01,2024-06-30"

# Generate report
odlm dailydist --config config.yaml --generate-report --report-format html
```

## Configuration File Structure

### Main Configuration Sections

```yaml
# Connection settings
odoo_connection:
  host: "${ODOO_HOST}"
  port: 8069
  database: "${ODOO_DB}"
  username: "${ODOO_USERNAME}"
  password: "${ODOO_PASSWORD}"

# Campaign configuration
campaign:
  name: "Voice"
  target_campaign: "Voice"
  active: true

# Salesperson selection
salesperson_selection:
  source_type: "campaign_table"  # campaign_table, file, list, database
  source_config:
    campaign_table:
      file_path: "config/salesperson_campaigns.csv"
  campaign_filtering:
    enabled: true
    target_campaign: "Voice"
    exclude_specific_users: ["Drew Cox", "Patrick Adler"]

# Lead finding criteria
lead_finding:
  date_range:
    older_than_days: 0
    younger_than_days: 30
  web_sources:
    source_type: "file"
    source_config:
      file_path: "config/web_sources.txt"
  additional_filters:
    status: ["new", "in_progress", "call_back", "utr"]
    exclude_dnc: true
    dnc_statuses: ["dnc", "do_not_call"]

# Distribution strategy
distribution:
  strategy: "level_based"  # level_based, round_robin, proportional
  level_based:
    levels:
      senior:
        target_leads: 200
        priority: 1
      mid_level:
        target_leads: 150
        priority: 2
```

## CLI Commands

### Basic Usage

```bash
# Run daily distribution
odlm dailydist --config daily_distribution_config.yaml

# Dry run
odlm dailydist --config config.yaml --dry-run

# Generate configuration
odlm dailydist --generate-config --output config.yaml

# Generate configuration for specific campaign
odlm dailydist --generate-config --campaign Voice --template advanced
```

### Advanced Options

```bash
# Override date range
odlm dailydist --config config.yaml --override-date-range "2024-01-01,2024-06-30"

# Limit distribution
odlm dailydist --config config.yaml --max-leads 100

# Generate detailed report
odlm dailydist --config config.yaml --generate-report --report-format html

# Force round robin
odlm dailydist --config config.yaml --force-round-robin

# Interactive step-through mode
odlm dailydist --config config.yaml --step-mode
odlm dailydist --config config.yaml --step-mode --auto-accept
odlm dailydist --config config.yaml --step-mode --dry-run
```

## Distribution Strategies

### Level-Based Distribution

Distributes leads based on salesperson levels (senior, mid_level, junior) and target lead counts:

```yaml
distribution:
  strategy: "level_based"
  level_based:
    levels:
      senior:
        target_leads: 200
        priority: 1
      mid_level:
        target_leads: 150
        priority: 2
      junior:
        target_leads: 100
        priority: 3
```

### Round-Robin Distribution

Simple round-robin distribution among eligible salespeople:

```yaml
distribution:
  strategy: "round_robin"
```

### Proportional Distribution

Distributes leads based on current workload ratios:

```yaml
distribution:
  strategy: "proportional"
```

## Lead Filtering

### Date Range Filtering

```yaml
lead_finding:
  date_range:
    older_than_days: 0      # Leads newer than X days
    younger_than_days: 30   # Leads older than X days
    exclude_weekends: false
    exclude_holidays: false
```

### Web Source Filtering

```yaml
lead_finding:
  web_sources:
    source_type: "file"
    source_config:
      file_path: "config/web_sources.txt"
    case_sensitive: false
    match_mode: "exact"  # exact, partial, regex
```

### Status and DNC Filtering

```yaml
lead_finding:
  additional_filters:
    status: ["new", "in_progress", "call_back", "utr"]
    exclude_dnc: true
    dnc_statuses: ["dnc", "do_not_call", "dont_call", "no_call"]
    exclude_tags: ["do_not_distribute", "test"]
    include_tags: ["hot_lead", "vip"]
```

## Salesperson Selection

### Campaign Table Method

```yaml
salesperson_selection:
  source_type: "campaign_table"
  source_config:
    campaign_table:
      file_path: "config/salesperson_campaigns.csv"
  campaign_filtering:
    enabled: true
    target_campaign: "Voice"
    exclude_specific_users: ["Drew Cox", "Patrick Adler"]
```

### File-Based Method (Legacy)

```yaml
salesperson_selection:
  source_type: "file"
  source_config:
    file_path: "config/salespeople.txt"
```

### List-Based Method

```yaml
salesperson_selection:
  source_type: "list"
  source_config:
    salespeople_list:
      - "alice_smith"
      - "bob_johnson"
      - "carol_williams"
```

## Performance Tracking

The system can track distribution performance when a MySQL database is configured:

```yaml
database_connection:
  host: "${TRACKING_DB_HOST}"
  port: 3306
  database: "${TRACKING_DB_NAME}"
  username: "${TRACKING_DB_USER}"
  password: "${TRACKING_DB_PASSWORD}"

tracking:
  enabled: true
  track_individual_assignments: true
  track_pre_post_counts: true
  track_distribution_summary: true
```

## Error Handling

The system includes comprehensive error handling:

- Configuration validation
- Connection error recovery
- Distribution failure handling
- Detailed error reporting

## Logging

Configure logging levels in the configuration:

```yaml
execution:
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Examples

### Basic Voice Campaign Distribution

```bash
# Generate configuration
odlm dailydist --generate-config --campaign Voice --output voice_config.yaml

# Run distribution
odlm dailydist --config voice_config.yaml

# Dry run to verify
odlm dailydist --config voice_config.yaml --dry-run
```

### Advanced Apple Campaign Distribution

```bash
# Generate advanced configuration
odlm dailydist --generate-config --campaign Apple --template advanced --output apple_config.yaml

# Run with custom settings
odlm dailydist --config apple_config.yaml --max-leads 50 --generate-report
```

### Minimal Configuration

```bash
# Generate minimal configuration
odlm dailydist --generate-config --template minimal --output minimal_config.yaml

# Run minimal distribution
odlm dailydist --config minimal_config.yaml
```

## Step-Through Mode

The daily distribution system includes an interactive step-through mode for testing and understanding the distribution process. This mode shows detailed information at each step and asks for user confirmation before proceeding.

### Features

- **Interactive Confirmation**: Each major step requires user confirmation (Y/n)
- **Detailed Tables**: Pretty-formatted tables showing salespeople, leads, and workload
- **Before/After Analysis**: Shows current state and expected outcomes
- **Auto-Accept Option**: Use `--auto-accept` to skip confirmations
- **Dry Run Support**: Combine with `--dry-run` for safe testing

### Step Breakdown

1. **Salesperson Selection**: Shows eligible salespeople with their details
2. **Lead Discovery**: Displays found leads with characteristics breakdown
3. **Workload Analysis**: Current lead counts and utilization percentages
4. **Distribution Planning**: Shows the distribution plan with before/after analysis
5. **Application**: Confirms the actual assignment to Odoo

### Example Usage

```bash
# Interactive step-through mode
odlm dailydist --config config.yaml --step-mode

# Auto-accept all steps
odlm dailydist --config config.yaml --step-mode --auto-accept

# Step-through with dry run (safe for testing)
odlm dailydist --config config.yaml --step-mode --dry-run
```

### Sample Output

```
================================================================================
🔄 Step 1: Salesperson Selection
📝 Selecting eligible salespeople based on configuration
================================================================================

✅ Found 3 eligible salespeople:

+---------------+----+----------+--------+--------+------+--------+
| Name          | ID | Campaign | Level  | Target | Team | Active |
+---------------+----+----------+--------+--------+------+--------+
| alice_smith   | 1  | Voice    | senior | 200    | Voice| ✅     |
| bob_johnson   | 2  | Voice    | senior | 200    | Voice| ✅     |
| carol_williams| 3  | Voice    | mid    | 150    | Voice| ✅     |
+---------------+----+----------+--------+--------+------+--------+

📊 Configuration Summary:
   • Campaign: Voice
   • Distribution Strategy: level_based
   • Date Range: 30 days

❓ Proceed to next step? (Y/n): 
```

## Troubleshooting

### Common Issues

1. **Configuration file not found**
   - Use `--generate-config` to create a boilerplate file
   - Check file path and permissions

2. **No eligible salespeople found**
   - Verify salesperson source file exists
   - Check campaign filtering settings
   - Ensure salespeople are active

3. **No distributable leads found**
   - Check date range settings
   - Verify lead status filters
   - Review web source configuration

4. **Database connection errors**
   - Verify MySQL credentials
   - Check database exists
   - Ensure mysql-connector-python is installed

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
odlm dailydist --config config.yaml --log-level DEBUG
```

## Future Enhancements

Planned enhancements include:

- Email notification system
- Advanced analytics dashboard
- Machine learning-based distribution
- Integration with external CRM systems
- Real-time monitoring and alerts

## Support

For issues and questions:

1. Check the configuration file syntax
2. Verify all required files exist
3. Review the logs for detailed error messages
4. Test with `--dry-run` to verify settings
5. Use `--log-level DEBUG` for detailed troubleshooting 