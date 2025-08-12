# Odoo Lead Manager CLI Usage

## New `leads` Command

The new `leads` command provides comprehensive filtering for CRM leads using the exact field structure from your CSV.

### Basic Usage

```bash
# Count all leads
odlm leads --count

# Get first 5 leads
odlm leads --limit 5

# Get leads in CSV format
odlm leads --limit 100 --format csv --output leads.csv
```

### Filtering Options

```bash
# Filter by status
odlm leads --status new --count
odlm leads --status new --limit 50

# Filter by date range
odlm leads --date-from 2024-01-01 --date-to 2024-12-31 --count
odlm leads --date-from 2024-01-01 --limit 100

# Filter by user
odlm leads --user "Jason" --count
odlm leads --user "Jason" --limit 25

# Filter by sales team
odlm leads --team "Sales" --count

# Filter by source
odlm leads --source "facebook_form" --count
odlm leads --source "google" --limit 50

# Filter by campaign
odlm leads --campaign "Summer2024" --count

# Combine filters
odlm leads --status new --source facebook_form --date-from 2024-01-01 --count
```

### Output Formats

```bash
# Table format (default)
odlm leads --limit 10

# CSV format
odlm leads --format csv --limit 100 --output leads.csv

# JSON format
odlm leads --format json --limit 50 --output leads.json
```

### Field Selection

```bash
# Get specific fields
odlm leads --fields "id,name,email,phone,status" --limit 10
```

### Count Preview

Always use `--count` first to see how many records will be returned:

```bash
odlm leads --count --status new --source facebook_form --date-from 2024-01-01
# Output: Total leads: 82352
```

## Available Fields

Based on actual crm.lead model discovery, these are the available fields:

- `id`, `web_source_id`, `create_date`, `source_date`, `campaign_id`
- `source_id`, `medium_id`, `term_id`, `content_id`, `team_id`
- `partner_name`, `contact_name`, `partner_id`, `stage_id`, `closer_id`
- `open_user_id`, `user_id`, `status`, `is_mobile1`, `phone`, `mobile`
- `email_from`, `is_mobile2`, `activity_date_deadline`, `tag_ids`, `is_email_valid`
- `street`, `street2`, `city`, `state_id`, `zip`, `country_id`, `status_date`, `company_id`

## Examples

```bash
# Get all new Facebook leads from 2024
odlm leads --status new --source facebook_form --date-from 2024-01-01 --limit 100 --format csv --output 2024_facebook_leads.csv

# Count leads assigned to specific user
odlm leads --user "Jason Buffone" --count

# Get recent leads with email validation
odlm leads --date-from 2024-10-01 --fields "id,partner_name,email_from,is_email_valid" --limit 50
```