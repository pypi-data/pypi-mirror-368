# Daily Lead Distribution Algorithm Requirements

## Overview

This document specifies the requirements for implementing a comprehensive daily lead distribution system within the Odoo Lead Manager package. The system will automate the process of distributing leads to salespeople based on configurable criteria, current workload, and distribution strategies.

## Important Terminology Clarification

**Campaigns vs. Lead Status Fields**

This specification uses two distinct concepts that must not be confused:

1. **Salesperson Campaigns** (e.g., "Voice", "Apple"): These are user-defined business entities that represent different sales initiatives or market segments. Salespeople are assigned to specific campaigns, and the distribution system distributes leads within these campaign contexts.

2. **Lead Status Fields** (e.g., "new", "in_progress", "utr", "call_back"): These are Odoo lead status values that indicate the current state of a lead in the sales process. The system filters leads based on these status values for distribution.

**Key Distinction:**
- **Campaigns** determine **which salespeople** are eligible for lead distribution
- **Lead Status** determines **which leads** are eligible for distribution

For example, when distributing leads for the "Voice" campaign, the system:
- Selects salespeople assigned to the "Voice" campaign
- Filters leads by status (e.g., "new", "in_progress") regardless of any lead campaign field
- Distributes eligible leads to eligible salespeople

## 1. System Architecture & Data Flow

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DAILY LEAD DISTRIBUTION PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CONFIGURATION │    │   ODOO DATABASE │    │  TRACKING DB    │
│   FILES         │    │                 │    │                 │
│                 │    │                 │    │                 │
│ • YAML Config   │    │ • Salespeople   │    │ • Distribution  │
│ • CSV Files     │    │ • Lead Data     │    │   History       │
│ • Text Files    │    │ • Campaign Data │    │ • Performance   │
│                 │    │                 │    │   Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CORE DISTRIBUTION ENGINE                               │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ SALESPERSON     │  │   LEAD FINDER   │  │ DISTRIBUTION    │              │
│  │ SELECTOR        │  │                 │  │ ENGINE          │              │
│  │                 │  │                 │  │                 │              │
│  │ • Campaign      │  │ • Date Range    │  │ • Level-Based   │              │
│  │   Filtering     │  │ • Status Filter │  │ • Round Robin   │              │
│  │ • User          │  │ • Web Sources   │  │ • Proportional  │              │
│  │   Exclusion     │  │ • DNC Filtering │  │ • Workload      │              │
│  │ • Active Status │  │ • Tag Matching  │  │   Balancing     │              │
│  │ • Team Filter   │  │ • Field         │  │                 │              │
│  │                 │  │   Validation    │  │                 │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ASSIGNMENT & TRACKING                                  │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ LEAD ASSIGNMENT │  │ PERFORMANCE     │  │ REPORTING       │              │
│  │                 │  │ TRACKING        │  │                 │              │
│  │ • Update Odoo   │  │ • Pre/Post      │  │ • Distribution  │              │
│  │   Records       │  │   Counts        │  │   Summary       │              │
│  │ • Status Reset  │  │ • Assignment    │  │ • Analytics     │              │
│  │ • Team          │  │   History       │  │ • Performance   │              │
│  │   Assignment    │  │ • Efficiency    │  │   Metrics       │              │
│  │ • User          │  │   Metrics       │  │ • Trend         │              │
│  │   Assignment    │  │ • Utilization   │  │   Analysis      │              │
│  │                 │  │   Tracking      │  │                 │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW OVERVIEW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

INPUT PHASE
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │ Salespeople     │    │ Lead Data       │
│ Loading         │    │ Selection       │    │ Retrieval       │
│                 │    │                 │    │                 │
│ • YAML Config   │    │ • Campaign      │    │ • Date Range    │
│ • CSV Files     │    │   Filtering     │    │   Filtering     │
│ • Environment   │    │ • User          │    │ • Status        │
│   Variables     │    │   Exclusion     │    │   Filtering     │
│ • Validation    │    │ • Active Status │    │ • Web Source    │
│                 │    │ • Team Filter   │    │   Filtering     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            PROCESSING PHASE                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Salesperson     │    │ Lead Filtering  │    │ Distribution    │
│ Workload        │    │ & Validation    │    │ Strategy        │
│ Calculation     │    │                 │    │ Application     │
│                 │    │                 │    │                 │
│ • Current Lead  │    │ • DNC Filtering │    │ • Level-Based   │
│   Counts        │    │ • Tag Matching  │    │ • Round Robin   │
│ • Target Levels │    │ • Field         │    │ • Proportional  │
│ • Utilization   │    │   Validation    │    │ • Workload      │
│   Percentage    │    │ • Priority      │    │   Balancing     │
│ • Deficit       │    │   Filtering     │    │ • Assignment    │
│   Calculation   │    │ • Assignment    │    │   Logic         │
│                 │    │   Filtering     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT PHASE                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Lead Assignment │    │ Performance     │    │ Reporting &     │
│ Application     │    │ Tracking        │    │ Analytics       │
│                 │    │                 │    │                 │
│ • Odoo Record   │    │ • Pre/Post      │    │ • Distribution  │
│   Updates       │    │   Counts        │    │   Summary       │
│ • Status Reset  │    │ • Assignment    │    │ • Performance   │
│ • Team          │    │   History       │    │   Metrics       │
│   Assignment    │    │ • Efficiency    │    │ • Trend         │
│ • User          │    │   Metrics       │    │   Analysis      │
│   Assignment    │    │ • Utilization   │    │ • Email         │
│ • Audit Trail   │    │   Tracking      │    │   Notifications │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.3 Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        COMPONENT INTERACTION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────┐
│ Load Config     │ ◄── YAML/JSON Configuration Files
│ Files           │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Initialize      │ ◄── Odoo Connection
│ Connections     │ ◄── Database Connection
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Select          │ ◄── Campaign Table/File
│ Salespeople     │ ◄── User Exclusions
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Calculate       │ ◄── Current Lead Counts
│ Workload        │ ◄── Target Levels
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Find            │ ◄── Date Range Filtering
│ Distributable   │ ◄── Status Filtering
│ Leads           │ ◄── Web Source Filtering
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Apply           │ ◄── Distribution Strategy
│ Distribution    │ ◄── Workload Balancing
│ Strategy        │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Update Odoo     │ ◄── Lead Assignments
│ Records         │ ◄── Status Reset
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Track           │ ◄── Performance Metrics
│ Performance     │ ◄── Assignment History
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Generate        │ ◄── Distribution Report
│ Reports         │ ◄── Analytics
└─────────────────┘
  │
  ▼
END
```

### 1.4 Data Sources and Destinations

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES & DESTINATIONS                           │
└─────────────────────────────────────────────────────────────────────────────────┘

INPUT SOURCES
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │ Salespeople     │    │ Lead Data       │
│ Sources         │    │ Sources         │    │ Sources         │
│                 │    │                 │    │                 │
│ • YAML Config   │    │ • Campaign CSV  │    │ • Odoo CRM      │
│ • JSON Config   │    │ • Text Files    │    │   Module        │
│ • Environment   │    │ • Database      │    │ • Lead Tables   │
│   Variables     │    │   Tables        │    │ • Status        │
│ • CLI Args      │    │ • Direct Lists  │    │   Fields        │
│ • Templates     │    │ • API Queries   │    │ • Campaign      │
│                 │    │                 │    │   Fields        │
└─────────────────┘    └─────────────────┘    └─────────────────┘

OUTPUT DESTINATIONS
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Odoo Database   │    │ Tracking        │    │ Reports &       │
│ Updates         │    │ Database        │    │ Analytics       │
│                 │    │                 │    │                 │
│ • Lead          │    │ • Distribution  │    │ • CSV Reports   │
│   Assignments   │    │   History       │    │ • JSON Reports  │
│ • Status        │    │ • Performance   │    │ • HTML Reports  │
│   Updates       │    │   Metrics       │    │ • Email         │
│ • Team          │    │ • Assignment    │    │   Notifications │
│   Assignments   │    │   History       │    │ • Dashboard     │
│ • User          │    │ • Efficiency    │    │   Data          │
│   Assignments   │    │   Tracking      │    │ • Log Files     │
│ • Audit Trail   │    │ • Utilization   │    │                 │
│                 │    │   Metrics       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.5 Error Handling and Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING & RECOVERY FLOW                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │ Connection      │    │ Distribution    │
│ Errors          │    │ Errors          │    │ Errors          │
│                 │    │                 │    │                 │
│ • Invalid YAML  │    │ • Odoo          │    │ • No Eligible   │
│ • Missing       │    │   Connection    │    │   Salespeople   │
│   Files         │    │ • Database      │    │ • No Eligible   │
│ • Validation    │    │   Connection    │    │   Leads         │
│   Failures      │    │ • Timeout       │    │ • Assignment    │
│ • Environment   │    │   Errors        │    │   Failures      │
│   Variables     │    │ • Authentication│    │ • Strategy      │
│                 │    │   Errors        │    │   Failures      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Recovery        │    │ Recovery        │    │ Recovery        │
│ Actions         │    │ Actions         │    │ Actions         │
│                 │    │                 │    │                 │
│ • Use Default   │    │ • Retry         │    │ • Fallback to   │
│   Config        │    │   Connection    │    │   Round Robin   │
│ • Generate      │    │ • Use Cached    │    │ • Skip Failed   │
│   Template      │    │   Data          │    │   Assignments   │
│ • Validate      │    │ • Use Offline   │    │ • Partial       │
│   Files         │    │   Mode          │    │   Distribution  │
│ • Log Errors    │    │ • Alert Admin   │    │ • Alert Admin   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 2. System Architecture

### 1.1 Core Components

The daily lead distribution system will consist of the following components:

1. **Configuration Manager**: Handles JSON/YAML configuration files
2. **Salesperson Selector**: Identifies eligible salespeople based on criteria
3. **Lead Finder**: Identifies leads for distribution based on filters
4. **Distribution Engine**: Calculates and executes lead assignments
5. **Reporting System**: Generates distribution reports and analytics

### 1.2 Configuration-Driven Design

The entire pipeline will be driven by configuration files (JSON/YAML) that control:
- Salesperson selection criteria
- Lead filtering parameters
- Distribution strategies and rules
- Reporting preferences
- Override mechanisms

## 2. Salesperson Selection Algorithm

### 2.1 Input Sources

The system will read salesperson lists from multiple sources:

1. **Campaign Table**: CSV file or database table with salesperson-campaign relationships
2. **Text File Input**: Simple text file with salesperson names or IDs (legacy)
3. **Database Query**: Direct Odoo queries for salespeople
4. **List Configuration**: Direct list in configuration file
5. **Category/Campaign Matching**: Filter by specific categories or campaigns
6. **Team-Based Selection**: Select entire sales teams

### 2.2 Campaign-Based Salesperson Selection

**Primary Method**: Campaign table with salesperson-campaign relationships

```yaml
salesperson_selection:
  source_type: "campaign_table"
  source_config:
    campaign_table:
      file_path: "config/salesperson_campaigns.csv"
      campaign_column: "campaign_name"
      salesperson_column: "salesperson_name"
      active_column: "active"
  
  campaign_filtering:
    enabled: true
    target_campaign: "Voice"  # Voice, Apple, or other user-defined campaigns
    include_inactive_salespeople: false
    exclude_specific_users: ["Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"]
```

**Selection Process:**
1. Load salesperson-campaign relationships from CSV or database
2. Filter by target campaign (e.g., "Voice", "Apple")
3. Filter by active status (if enabled)
4. Exclude specific users
5. Apply additional criteria (team, level, etc.)

### 2.3 Alternative Selection Methods

**File-Based Selection (Legacy):**
```yaml
salesperson_selection:
  source_type: "file"
  source_config:
    file_path: "salespeople.txt"
  filters:
    active_only: true
    has_permissions: true
    min_experience_level: 1
    max_workload_percentage: 90
```

**List-Based Selection:**
```yaml
salesperson_selection:
  source_type: "list"
  source_config:
    salespeople_list:
      - "alice_smith"
      - "bob_johnson"
      - "carol_williams"
```

**Database Query Selection:**
```yaml
salesperson_selection:
  source_type: "database"
  source_config:
    database_query:
      table: "res_users"
      where_clause: "active = true AND sales_team_id = 1"
      fields: ["name", "id", "sales_team_id"]
```

### 2.4 Selection Criteria

```yaml
salesperson_selection:
  source_type: "campaign_table" | "file" | "database" | "list"
  source_config:
    file_path: "salespeople.txt"  # For file-based selection
    category: "senior_sales"       # For category-based selection
    campaign: "summer_2024"        # For campaign-based selection
    team: "sales_team_a"           # For team-based selection
  filters:
    active_only: true
    has_permissions: true
    min_experience_level: 1
    max_workload_percentage: 90
    team_filter: "Voice"  # Optional team filter
```

### 2.5 Current Lead Count Calculation

For each selected salesperson, calculate:
- **Total lead count** across all statuses
- **Lead count by status** (new, in_progress, won, lost, etc.)
- **Lead count by source** (web sources, campaigns, etc.)
- **Lead count by date range** (last 30 days, this month, etc.)

## 3. Lead Finding Algorithm

### 3.1 Date Range Filtering

**Current Implementation Analysis:**
Based on the current pipeline workflow, the system uses a **30-day window** for lead distribution with specific filtering logic:

```r
# From current_pipeline.R - m_leadsActivesalesguys function
m_leadsActivesalesguys<-function(status.counts1, all_leads, x, stts,lowerlimit,upperlimit)
{
  firstresults <- status.counts1 %>% filter(!open_user_id %in%
                                              c("Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel")) %>%
    filter(active %in% c(x))
  same.day2 <- all_leads %>% filter(open_user_id %in% firstresults$open_user_id)
  same.day2 <- same.day2 %>% filter(source_date < Sys.Date() -
                                      lowerlimit &
                                      source_date >= Sys.Date() - upperlimit)
  same.day2 <- same.day2 %>% filter(status %in% stts)
  same.day2$activity_date_deadline <- as.Date(same.day2$activity_date_deadline)
  same.day2 <- same.day2 %>% filter(activity_date_deadline <
                                      Sys.Date() - 4 | is.na(activity_date_deadline))
  same.day2 <- same.day2 %>% filter(!is.na(source_date))
  return(same.day2)
}
```

**Current Date Range Logic:**
- **Date Range**: `source_date < Sys.Date() - lowerlimit & source_date >= Sys.Date() - upperlimit`
- **Current Settings**: `lowerlimit=0, upperlimit=30` (last 30 days)
- **Date Field**: Uses `source_date` field for date filtering
- **Activity Deadline**: Excludes leads with activity deadline within 4 days of today
- **Excluded Users**: "Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"

**Status-Based Filtering:**
```r
# Active salespeople
stts<-c("Utr","Call Back")

# Inactive salespeople  
stts<-c("Utr","Call Back","Full Pitch Follow Up","Full Pitch Follow Up ","New")
```

**Updated Configuration:**
```yaml
lead_finding:
  date_range:
    # Current implementation uses 30-day window
    older_than_days: 0      # Changed from 60 to match current logic
    younger_than_days: 30   # Changed from 180 to match current logic
    custom_start_date: null  # Override with specific date
    custom_end_date: null    # Override with specific date
    exclude_weekends: false
    exclude_holidays: false
  
  # Status-based filtering (from current implementation)
  status_filters:
    active_salespeople:
      statuses: ["Utr", "Call Back"]
      date_range_days: 30
    inactive_salespeople:
      statuses: ["Utr", "Call Back", "Full Pitch Follow Up", "Full Pitch Follow Up ", "New"]
      date_range_days: 30
    exclude_closed_leads: true
    exclude_assigned_leads: false  # Current implementation redistributes assigned leads
  
  # Activity deadline filtering
  activity_deadline:
    exclude_within_days: 4  # Exclude leads with activity deadline within 4 days
    exclude_missing_deadline: false  # Include leads with no deadline
  
  # User exclusions
  excluded_users:
    - "Drew Cox"
    - "Patrick Adler" 
    - "Administrator"
    - "Marc Spiegel"
```

**Enhanced Date Range Options:**
```yaml
lead_finding:
  date_range_strategies:
    current_30_day:  # Current implementation
      older_than_days: 0
      younger_than_days: 30
      description: "Leads from last 30 days (current default)"
    
    extended_60_day:  # Alternative for larger datasets
      older_than_days: 0
      younger_than_days: 60
      description: "Leads from last 60 days"
    
    stale_lead_recovery:  # For recovering old leads
      older_than_days: 60
      younger_than_days: 180
      description: "Leads older than 2 months but newer than 6 months"
    
    custom_range:
      older_than_days: null  # Configurable
      younger_than_days: null  # Configurable
      description: "User-defined date range"
```

### 3.2 Web Source Filtering

**Input Sources:**
1. **Text File**: List of web source IDs/names
2. **Database Table**: Odoo table with source configurations
3. **Configuration Array**: Direct list in config file

**Configuration:**
```yaml
lead_finding:
  web_sources:
    source_type: "file" | "database" | "config"
    source_config:
      file_path: "web_sources.txt"
      table_name: "lead_web_sources"
      sources: ["facebook_form", "google_ads", "website_contact"]
    include_inactive: false
    case_sensitive: false  # Configurable case sensitivity
    exact_match: false     # Whether to require exact match or partial match
    match_mode: "exact" | "partial" | "regex"  # Match mode for web sources
```

**Enhanced Web Source Matching:**
```yaml
lead_finding:
  web_sources:
    # Basic configuration
    source_type: "file"
    source_config:
      file_path: "web_sources.txt"
    
    # Matching options
    case_sensitive: false
    exact_match: false
    match_mode: "exact"  # exact, partial, regex
    
    # Advanced matching
    match_patterns:
      - "facebook*"      # Wildcard patterns
      - "google_ads*"
      - "website_contact"
    
    # Regex patterns (when match_mode is "regex")
    regex_patterns:
      - "^facebook.*"
      - "^google.*ads"
      - ".*contact.*"
    
    # Validation
    validate_sources: true  # Verify sources exist in Odoo
    exclude_invalid: true   # Skip invalid sources
```

### 3.3 Campaign Filtering

**Important Note**: This section refers to **lead campaign fields** in Odoo, which are separate from the **salesperson campaigns** (Voice, Apple) used for distribution. Lead campaigns are typically marketing campaign identifiers that may be attached to leads.

**Configurable Lead Campaign Types:**
- **Marketing campaigns**: Lead-specific campaign identifiers
- **Source campaigns**: Campaigns attached to leads from marketing sources
- **Custom campaigns**: User-defined lead campaign types

**Configuration:**
```yaml
lead_finding:
  campaigns:
    types: ["voice_campaign_2024", "apple_campaign_2024", "summer_promo"]
    match_patterns:
      - "voice_campaign_*"
      - "apple_campaign_*"
      - "summer_promo"
    case_sensitive: false
    exact_match: false
    match_mode: "exact" | "partial" | "regex"
```

**Enhanced Campaign Matching:**
```yaml
lead_finding:
  campaigns:
    # Basic configuration
    types: ["voice_campaign_2024", "apple_campaign_2024", "summer_promo"]
    
    # Matching options
    case_sensitive: false
    exact_match: false
    match_mode: "exact"  # exact, partial, regex
    
    # Pattern matching
    match_patterns:
      - "voice_campaign_*"
      - "apple_campaign_*"
      - "summer_promo"
    
    # Regex patterns (when match_mode is "regex")
    regex_patterns:
      - "^voice_campaign_.*"
      - "^apple_campaign_.*"
      - "^summer_promo.*"
    
    # Campaign-specific settings
    campaign_settings:
      voice_campaign_2024:
        case_sensitive: false
        match_mode: "partial"
      apple_campaign_2024:
        case_sensitive: true
        match_mode: "exact"
      summer_promo:
        case_sensitive: false
        match_mode: "regex"
```

### 3.4 Lead Status Filtering

**Lead Status Types:**
- **new**: New leads that haven't been processed
- **in_progress**: Leads currently being worked on
- **call_back**: Leads requiring follow-up calls
- **utr**: Universal Tracking Reference status
- **full_pitch_follow_up**: Leads in full pitch follow-up phase
- **won**: Successfully converted leads
- **lost**: Failed conversion leads
- **cancelled**: Cancelled leads

**DNC (Do Not Call) Statuses:**
- **dnc**: Do not call
- **do_not_call**: Do not call
- **dont_call**: Don't call
- **no_call**: No call
- **blocked**: Blocked from calling
- **opt_out**: Opted out of calls

**Configuration:**
```yaml
lead_finding:
  additional_filters:
    status: ["new", "in_progress"]  # Only distribute unassigned or in-progress leads
    exclude_assigned: true           # Exclude leads already assigned to users
    exclude_closed: true             # Exclude won/lost leads
    min_priority: 1                 # Minimum lead priority
    max_priority: 5                 # Maximum lead priority
    required_fields: ["name", "email"]  # Leads must have these fields
    exclude_tags: ["do_not_distribute", "test"]
    include_tags: ["hot_lead", "vip"]
    
    # DNC filtering
    exclude_dnc: true               # Exclude Do Not Call leads
    dnc_statuses: ["dnc", "do_not_call", "dont_call", "no_call", "blocked", "opt_out"]
    dnc_case_sensitive: false       # Case sensitivity for DNC status matching
    dnc_match_mode: "exact"         # exact, partial, regex
    
    # Status matching configuration
    status_matching:
      case_sensitive: false
      exact_match: false
      match_mode: "exact"  # exact, partial, regex
      include_partial_matches: true
```

**Enhanced Status and Tag Matching:**
```yaml
lead_finding:
  additional_filters:
    # Status filtering with case sensitivity
    status:
      values: ["new", "in_progress", "call_back", "utr"]
      case_sensitive: false
      exact_match: false
      match_mode: "exact"
      include_partial_matches: true
    
    # DNC filtering configuration
    dnc_filtering:
      enabled: true
      statuses: ["dnc", "do_not_call", "dont_call", "no_call", "blocked", "opt_out"]
      case_sensitive: false
      match_mode: "exact"  # exact, partial, regex
      include_partial_matches: false  # Usually want exact match for DNC
      
      # Additional DNC patterns
      regex_patterns:
        - "^dnc.*"
        - "^do_not_call.*"
        - "^dont_call.*"
        - ".*no_call.*"
        - ".*blocked.*"
        - ".*opt_out.*"
      
      # DNC tag filtering
      exclude_dnc_tags: true
      dnc_tags: ["do_not_call", "dnc", "blocked", "opt_out"]
    
    # Tag filtering with case sensitivity
    exclude_tags:
      values: ["do_not_distribute", "test", "archived"]
      case_sensitive: false
      exact_match: false
      match_mode: "exact"
    
    include_tags:
      values: ["hot_lead", "vip", "priority"]
      case_sensitive: false
      exact_match: false
      match_mode: "exact"
    
    # Field validation
    required_fields:
      - "name"
      - "email"
      - "phone"
    
    # Priority filtering
    priority_range:
      min: 1
      max: 5
    
    # Assignment filtering
    assignment_filters:
      exclude_assigned: true
      exclude_closed: true
      exclude_inactive_users: true
```

### 3.5 Sales Filter (Opportunity Matching)

**Purpose:**
The sales filter prevents redistribution of leads that already have corresponding sales/opportunities in the system. This filter checks if a lead (crm.lead) has a matching opportunity (crm.opp) based on the partner_id, indicating the lead has likely been converted to a sale or is actively being pursued as an opportunity.

**Business Logic:**
1. For each lead found in the distribution process, check if there's a matching opportunity in crm.opp
2. Match leads to opportunities using the partner_id field (both tables should have the same partner_id)
3. If a match is found, exclude the lead from distribution as it's already converted or being actively worked
4. Only distribute leads that have no corresponding opportunities

**Database Relationship:**
```
crm.lead (Lead Table)           crm.opp (Opportunity Table)
├── id                          ├── id
├── partner_id  ◄──────────────┤ partner_id
├── name                        ├── name
├── status                      ├── stage_id
└── source_date                 └── date_open

Filter Logic: Exclude leads where crm.lead.partner_id = crm.opp.partner_id
```

**Configuration:**
```yaml
lead_finding:
  sales_filter:
    # Enable/disable sales filter
    enabled: true
    
    # Opportunity table configuration
    opportunity_table: "crm.opp"  # Default opportunity table name
    opportunity_partner_field: "partner_id"  # Field to match in opportunity table
    lead_partner_field: "partner_id"  # Field to match in lead table
    
    # Additional opportunity filters (optional)
    exclude_opportunity_stages:
      - "cancelled"
      - "lost"
      - "closed_lost"
    
    # Include only opportunities in specific stages (optional)
    include_opportunity_stages: []  # Empty means all stages
    
    # Date range for opportunity matching (optional)
    opportunity_date_range:
      enabled: false
      field_name: "date_open"  # Date field to check in opportunities
      days_back: 365  # Only check opportunities from last 365 days
    
    # Logging and debugging
    log_excluded_leads: true  # Log leads excluded due to sales filter
    log_level: "info"  # debug, info, warning, error
```

**Enhanced Configuration with Multiple Match Criteria:**
```yaml
lead_finding:
  sales_filter:
    enabled: true
    
    # Primary matching criteria
    primary_match:
      opportunity_table: "crm.opp"
      lead_field: "partner_id"
      opportunity_field: "partner_id"
      require_both_non_null: true  # Both fields must have values to match
    
    # Secondary matching criteria (optional)
    secondary_matches:
      email_match:
        enabled: false
        lead_field: "email_from"
        opportunity_field: "email_from"
      
      phone_match:
        enabled: false
        lead_field: "phone"
        opportunity_field: "phone"
    
    # Opportunity filtering
    opportunity_criteria:
      exclude_stages: ["cancelled", "lost", "closed_lost"]
      include_stages: []  # Empty = all stages
      active_only: true  # Only check active opportunities
      
      # Date filtering for opportunities
      date_filter:
        enabled: false
        field_name: "date_open"
        newer_than_days: 365  # Only opportunities from last year
    
    # Performance optimization
    performance:
      batch_size: 1000  # Process leads in batches
      use_database_join: true  # Use SQL JOIN instead of Python filtering
      cache_opportunities: true  # Cache opportunity data for session
      cache_duration_minutes: 30
    
    # Reporting
    reporting:
      log_excluded_leads: true
      log_match_details: false  # Detailed matching information
      count_excluded_by_stage: true  # Count exclusions by opportunity stage
      export_excluded_leads: false  # Export excluded leads to file
      export_path: "logs/excluded_leads.csv"
```

**Implementation Requirements:**

1. **Database Query Optimization:**
   - Use SQL JOIN operations when possible for better performance
   - Implement batch processing for large lead datasets
   - Add database indexes on partner_id fields if not present

2. **Error Handling:**
   - Handle missing partner_id values gracefully
   - Log warnings for leads/opportunities with null partner_id
   - Continue processing if opportunity table is inaccessible

3. **Performance Considerations:**
   - Cache opportunity data during distribution session
   - Use efficient database queries with proper indexing
   - Implement timeout protection for slow queries

4. **Logging and Debugging:**
   - Log number of leads excluded due to sales filter
   - Provide detailed match information in debug mode
   - Track performance metrics for filter operation

**Example Implementation Flow:**
```python
def _matches_sales_criteria(self, lead: Dict[str, Any]) -> bool:
    """Check if lead should be excluded due to existing sales/opportunities."""
    sales_config = self.config.get('lead_finding', {}).get('sales_filter', {})
    
    if not sales_config.get('enabled', False):
        return True  # Sales filter disabled, include lead
    
    lead_partner_id = lead.get('partner_id')
    if not lead_partner_id:
        return True  # No partner_id, cannot match to opportunities
    
    # Check for matching opportunities
    has_matching_opportunity = self._check_opportunity_match(lead_partner_id, sales_config)
    
    # Return False if matching opportunity found (exclude lead)
    return not has_matching_opportunity

def _check_opportunity_match(self, partner_id: int, config: Dict[str, Any]) -> bool:
    """Check if partner_id has matching opportunities in crm.opp."""
    # Implementation details...
    pass
```

### 3.6 Dropback Filter (Old Lead Handling)

**Purpose:**
The dropback filter identifies leads that are older than a specified threshold (default 30 days) and automatically assigns them back to designated campaign managers instead of proceeding through the normal distribution process. This ensures that stale leads receive specialized attention from experienced team members.

**Business Logic:**
1. Before normal distribution, check if leads exceed the configured age threshold
2. Leads meeting dropback criteria are immediately assigned to campaign-specific users
3. These leads bypass the normal distribution algorithm entirely
4. The system logs dropback assignments for tracking and reporting
5. Only leads that don't meet dropback criteria proceed to normal distribution

**Web Source-Based Dropback Assignment:**
```
Lead Age > Threshold → Check Web Source ID → Map to Campaign → Assign to Designated User

Web Source ID → Campaign Mapping:
- Voice Web Sources → Voice Campaign → Pat Adler  
- Apple Web Sources → Apple Campaign → Kevin Levonas
- Other/Unknown Sources → Default → Configurable fallback user
```

**Important:** Campaign identification is based on the web source ID provided in the lead data, not a separate campaign field. The system maps web source IDs to campaigns using configurable mappings.

**Configuration:**
```yaml
lead_finding:
  dropback_filter:
    # Enable/disable dropback functionality
    enabled: true
    
    # Age threshold configuration
    age_threshold:
      days: 30  # Leads older than this many days trigger dropback
      field_name: "source_date"  # Date field to check against
      use_business_days: false  # Count only business days vs calendar days
    
    # Web source to campaign mapping
    web_source_campaign_mapping:
      # Voice campaign web sources
      voice_sources:
        - "facebook_voice"
        - "google_ads_voice" 
        - "voice_landing_page"
        - "voice_campaign_2024"
      
      # Apple campaign web sources  
      apple_sources:
        - "facebook_apple"
        - "google_ads_apple"
        - "apple_landing_page"
        - "apple_campaign_2024"
      
      # Default mapping for unmatched sources
      default_campaign: "default"
    
    # Campaign-specific dropback assignments
    campaign_assignments:
      "Voice": "Pat Adler"        # Voice campaign leads go to Pat Adler
      "Apple": "Kevin Levonas"    # Apple campaign leads go to Kevin Levonas
      "default": "Administrator"  # Fallback for unmatched campaigns
    
    # Assignment configuration
    assignment_config:
      # Field to use for web source identification
      web_source_field: "source_id"  # Field containing web source ID
      web_source_field_type: "many2one"  # "many2one", "char", "selection"
      
      # User assignment settings
      assign_immediately: true  # Apply assignment during dropback
      update_status: true       # Update lead status when dropping back
      dropback_status: "dropback"  # Status to set for dropback leads
      
      # Override existing assignments
      override_existing_assignments: true
      preserve_team_assignment: false
    
    # Logging and tracking
    logging:
      log_dropback_assignments: true
      log_level: "info"  # debug, info, warning, error
      include_lead_details: false  # Include lead info in logs
    
    # Reporting
    reporting:
      count_dropback_leads: true
      export_dropback_report: false
      report_path: "reports/dropback_assignments.csv"
```

**Enhanced Configuration with Multiple Criteria:**
```yaml
lead_finding:
  dropback_filter:
    enabled: true
    
    # Multiple age thresholds
    age_thresholds:
      primary:
        days: 30
        field_name: "source_date"
        description: "Standard dropback threshold"
      
      secondary:
        days: 60
        field_name: "create_date"
        description: "Extended threshold for special cases"
        conditions:
          - "priority >= 3"  # Only high priority leads
          - "tag_ids contains 'vip'"
    
    # Advanced web source to campaign matching
    web_source_matching:
      # Primary web source field
      primary_field: "source_id"
      primary_field_type: "many2one"
      
      # Fallback web source fields
      fallback_fields:
        - field: "utm_source"
          type: "char"
        - field: "x_web_source"
          type: "char"
      
      # Web source name patterns for campaign mapping
      campaign_patterns:
        "Voice":
          exact_matches:
            - "facebook_voice"
            - "google_ads_voice"
            - "voice_landing_page"
          pattern_matches:
            - ".*voice.*"
            - ".*telephone.*"
            - ".*phone.*"
        
        "Apple":
          exact_matches:
            - "facebook_apple"
            - "google_ads_apple" 
            - "apple_landing_page"
          pattern_matches:
            - ".*apple.*"
            - ".*iphone.*"
            - ".*ios.*"
    
    # Assignment rules
    assignment_rules:
      "Voice":
        user: "Pat Adler"
        user_id: 15  # Optional: direct user ID
        team: "Voice Team"
        status: "dropback_voice"
        priority: 2
        
      "Apple":
        user: "Kevin Levonas"
        user_id: 23
        team: "Apple Team"
        status: "dropback_apple"
        priority: 1
        
      "default":
        user: "Administrator"
        user_id: 1
        team: null  # Keep existing team
        status: "dropback_general"
        priority: 3
    
    # Advanced filtering
    additional_criteria:
      # Only dropback leads that meet these criteria
      lead_criteria:
        min_priority: 1
        max_priority: 5
        required_fields: ["email", "phone"]
        exclude_statuses: ["won", "lost", "cancelled"]
        exclude_tags: ["do_not_dropback", "manual_assignment"]
      
      # Exclude leads already assigned to dropback users
      exclude_existing_assignments:
        enabled: true
        dropback_users: ["Pat Adler", "Kevin Levonas"]
    
    # Performance settings
    performance:
      batch_size: 500
      async_assignment: false
      timeout_seconds: 30
```

**Implementation Requirements:**

1. **Campaign Detection:**
   - Support multiple campaign field types (many2one, char, selection)
   - Implement fallback mechanisms for campaign identification
   - Handle campaign name variations and aliases

2. **Age Calculation:**
   - Use configurable date fields for age calculation
   - Support business days vs calendar days
   - Handle missing or invalid dates gracefully

3. **User Assignment:**
   - Validate dropback users exist in the system
   - Support both user names and user IDs
   - Update lead assignments immediately or queue for batch processing

4. **Integration with Distribution:**
   - Remove dropback leads from normal distribution pool
   - Ensure dropback happens before other filtering steps
   - Maintain accurate counts for reporting

5. **Error Handling:**
   - Handle missing campaign information
   - Fallback to default user for unmatched campaigns
   - Continue processing if dropback assignment fails

**Process Flow:**
```python
def process_leads_with_dropback(self, all_leads: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Separate leads into dropback and distribution pools."""
    dropback_config = self.config.get('lead_finding', {}).get('dropback_filter', {})
    
    if not dropback_config.get('enabled', False):
        return all_leads, []  # No dropback, all leads go to distribution
    
    dropback_leads = []
    distribution_leads = []
    
    for lead in all_leads:
        if self._is_dropback_lead(lead, dropback_config):
            # Assign to appropriate dropback user
            assigned_lead = self._assign_dropback_lead(lead, dropback_config)
            dropback_leads.append(assigned_lead)
        else:
            distribution_leads.append(lead)
    
    return distribution_leads, dropback_leads

def _is_dropback_lead(self, lead: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """Check if lead meets dropback criteria."""
    # Age check, campaign check, additional criteria
    pass

def _assign_dropback_lead(self, lead: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Assign lead to appropriate dropback user based on campaign."""
    # Determine campaign, find assigned user, update lead
    pass
```

**Integration Points:**

1. **Lead Finding Pipeline:**
   ```
   All Leads → Date Filter → Sales Filter → Dropback Filter → Distribution Filter → Distribution
                                                ↓
                                        Dropback Leads → Campaign Assignment → Immediate Assignment
   ```

2. **Reporting Integration:**
   - Include dropback counts in distribution summary
   - Track dropback assignments separately from distribution
   - Generate dropback-specific reports

3. **Performance Monitoring:**
   - Track dropback processing time
   - Monitor dropback assignment success rates
   - Alert on dropback assignment failures

## 4. Distribution Algorithm

### 4.1 Level-Based Distribution

**Core Logic:**
1. Calculate each salesperson's current lead count
2. Determine their target level (e.g., 200 leads for senior, 150 for mid-level)
3. Calculate deficit: `target_level - current_count`
4. Distribute leads to fill deficits, starting with highest priority salespeople

**Configuration:**
```yaml
distribution:
  strategy: "level_based" | "round_robin" | "proportional" | "capacity_based"
  level_based:
    levels:
      senior:
        target_leads: 200
        priority: 1
        salespeople: ["alice_smith", "bob_johnson"]
      mid_level:
        target_leads: 150
        priority: 2
        salespeople: ["carol_williams", "dave_brown"]
      junior:
        target_leads: 100
        priority: 3
        salespeople: ["eve_davis", "frank_miller"]
    fill_strategy: "highest_priority_first" | "round_robin_within_level"
    allow_overflow: false  # Allow exceeding target levels
    overflow_limit: 10     # Maximum overflow percentage
```

### 4.2 Round Robin Override

**Configuration:**
```yaml
distribution:
  round_robin_override:
    enabled: false
    trigger_conditions:
      - "when_lead_count < 10"
      - "when_salespeople_count < 3"
      - "when_manual_override = true"
    distribution_order: "random" | "alphabetical" | "seniority"
    cycle_reset: "daily" | "weekly" | "monthly"
```

### 4.3 Advanced Distribution Rules

```yaml
distribution:
  advanced_rules:
    skill_matching:
      enabled: true
      required_skills: ["enterprise_sales", "technical_knowledge"]
      skill_weights: [0.7, 0.3]
    
    workload_balancing:
      enabled: true
      max_daily_distribution: 20
      min_daily_distribution: 5
      consider_weekend_workload: false
    
    priority_handling:
      high_priority_leads: "senior_only"
      medium_priority_leads: "all_levels"
      low_priority_leads: "junior_first"
    
    geographic_distribution:
      enabled: false
      region_matching: true
      timezone_consideration: true
```

## 5. Configuration File Structure

### 5.1 Main Configuration File

```yaml
# daily_lead_distribution_config.yaml
version: "1.0"
name: "Daily Lead Distribution"
description: "Automated daily lead distribution system for UTR campaigns"
tags: ["lead-distribution", "automation", "sales", "odoo"]
author: "Sales Operations Team"
created_date: "2024-01-15"
last_modified: "2024-01-15"

# Connection settings
odoo_connection:
  host: "${ODOO_HOST}"
  port: 8069
  database: "${ODOO_DB}"
  username: "${ODOO_USERNAME}"
  password: "${ODOO_PASSWORD}"

# Database connection for tracking and analytics
database_connection:
  host: "${TRACKING_DB_HOST}" | "localhost"
  port: 3306
  database: "${TRACKING_DB_NAME}" | "lead_distribution_tracking"
  username: "${TRACKING_DB_USER}" | "tracking_user"
  password: "${TRACKING_DB_PASSWORD}"

# Campaign configuration
campaign:
  name: "Voice"
  description: "Voice/telephony sales campaign distribution"
  target_campaign: "Voice"  # Voice, Apple, or other user-defined campaigns
  distribution_frequency: "daily"
  active: true

# Salesperson selection
salesperson_selection:
  source_type: "campaign_table" | "file" | "list" | "database"
  source_config:
    # For campaign-based selection
    campaign_table:
      file_path: "config/salesperson_campaigns.csv"  # CSV with salesperson,campaign_name
      table_name: "salesperson_campaigns"  # Database table name
      campaign_column: "campaign_name"
      salesperson_column: "salesperson_name"
      active_column: "active"  # Optional: filter by active status
    
    # For file-based selection (legacy)
    file_path: "config/salespeople.txt"
    
    # For list-based selection
    salespeople_list:
      - "alice_smith"
      - "bob_johnson"
      - "carol_williams"
    
    # For database query selection
    database_query:
      table: "res_users"
      where_clause: "active = true AND sales_team_id = 1"
      fields: ["name", "id", "sales_team_id"]
  
  # Campaign-specific salesperson filtering
  campaign_filtering:
    enabled: true
    target_campaign: "Voice"  # Voice, Apple, or other user-defined campaigns
    include_inactive_salespeople: false
    exclude_specific_users: ["Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"]
  
  # Salesperson criteria
  filters:
    active_only: true
    has_permissions: true
    min_experience_level: 1
    max_workload_percentage: 90
    team_filter: "Voice"  # Optional team filter

# Lead finding criteria
lead_finding:
  date_range:
    older_than_days: 60
    younger_than_days: 180
  web_sources:
    source_type: "file"
    source_config:
      file_path: "config/web_sources.txt"
  campaigns:
    types: ["voice_campaign_2024", "apple_campaign_2024"]
    match_patterns:
      - "voice_campaign_*"
      - "apple_campaign_*"
  additional_filters:
    status: ["new", "in_progress"]
    exclude_assigned: true

# Distribution strategy
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
  round_robin_override:
    enabled: false

# Reporting
reporting:
  generate_report: true
  report_format: "csv" | "json" | "html"
  report_location: "reports/"
  include_analytics: true
  email_notification: false

# Execution settings
execution:
  dry_run: false
  max_leads_per_run: 1000
  batch_size: 50
  retry_failed: true
  max_retries: 3
  log_level: "INFO"
```

### 5.2 Campaign-Salesperson Relationship

**Important Distinction: Campaigns vs. Lead Status**

Campaigns are **user-defined business entities** that represent different sales initiatives or market segments. They are **NOT** the same as lead status fields. 

**Current Campaigns:**
- **Voice**: Voice/telephony sales campaigns
- **Apple**: Apple product sales campaigns
- **Future campaigns**: Additional campaigns may be added as business needs evolve

**Lead Status Fields** (separate from campaigns):
- **new**: New leads that haven't been processed
- **in_progress**: Leads currently being worked on  
- **call_back**: Leads requiring follow-up calls
- **utr**: Universal Tracking Reference status
- **full_pitch_follow_up**: Leads in full pitch follow-up phase
- **won**: Successfully converted leads
- **lost**: Failed conversion leads
- **cancelled**: Cancelled leads

**CSV File Format (salesperson_campaigns.csv):**
```csv
salesperson_name,campaign_name,active,team,level,target_leads
alice_smith,Voice,true,Voice,senior,200
bob_johnson,Voice,true,Voice,senior,200
carol_williams,Voice,true,Voice,mid_level,150
dave_brown,Voice,true,Voice,mid_level,150
eve_davis,Voice,true,Voice,junior,100
frank_miller,Voice,true,Voice,junior,100
gina_wilson,Apple,true,Apple,senior,200
henry_jones,Apple,true,Apple,mid_level,150
```

**Database Table Structure:**
```sql
CREATE TABLE salesperson_campaigns (
    id SERIAL PRIMARY KEY,
    salesperson_name VARCHAR(255) NOT NULL,
    salesperson_id INTEGER,
    campaign_name VARCHAR(255) NOT NULL,  -- Voice, Apple, etc.
    active BOOLEAN DEFAULT true,
    team VARCHAR(100),                    -- Usually matches campaign_name
    level VARCHAR(50),                    -- senior, mid_level, junior
    target_leads INTEGER DEFAULT 150,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_campaign_name (campaign_name),
    INDEX idx_salesperson_name (salesperson_name),
    INDEX idx_active (active),
    UNIQUE KEY unique_salesperson_campaign (salesperson_name, campaign_name)
);
```

### 5.3 Supporting Configuration Files

**salespeople.txt (Legacy Format):**
```
# Salesperson list - one per line
# Format: name|id|level|target_leads
alice_smith|1|senior|200
bob_johnson|2|senior|200
carol_williams|3|mid_level|150
dave_brown|4|mid_level|150
eve_davis|5|junior|100
frank_miller|6|junior|100
```

**web_sources.txt:**
```
# Web source IDs - one per line
facebook_form
google_ads
website_contact
linkedin_ads
twitter_ads
```

## 6. CLI Implementation

### 6.1 New CLI Command

```bash
# Basic daily distribution
odlm dailydist --config daily_lead_distribution_config.yaml

# Comprehensive dry run analysis with detailed reporting
odlm dailydist --config config.yaml --dry-run

# Override configuration
odlm dailydist --config config.yaml --override-date-range "2024-01-01,2024-06-30"

# Force round robin distribution
odlm dailydist --config config.yaml --force-round-robin

# Limit distribution
odlm dailydist --config config.yaml --max-leads 100

# Generate detailed report
odlm dailydist --config config.yaml --generate-report --report-format html

# Generate boilerplate config file
odlm dailydist --generate-config --output daily_distribution_config.yaml

# Generate config with specific campaign
odlm dailydist --generate-config --campaign Voice --output voice_distribution_config.yaml
```

### 6.2 CLI Arguments

```python
# New CLI arguments for dailydist command
parser.add_argument("--config", help="Configuration file path")
parser.add_argument("--dry-run", action="store_true", help="Show plan without applying")
parser.add_argument("--override-date-range", help="Override date range (start,end)")
parser.add_argument("--force-round-robin", action="store_true", help="Force round robin distribution")
parser.add_argument("--max-leads", type=int, help="Maximum leads to distribute")
parser.add_argument("--generate-report", action="store_true", help="Generate distribution report")
parser.add_argument("--report-format", choices=["csv", "json", "html"], default="csv")
parser.add_argument("--report-location", help="Report output directory")
parser.add_argument("--email-notification", action="store_true", help="Send email notification")
parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")

# Config generation arguments
parser.add_argument("--generate-config", action="store_true", help="Generate boilerplate config file")
parser.add_argument("--output", help="Output file path for generated config")
parser.add_argument("--campaign", help="Campaign name for config generation")
parser.add_argument("--template", choices=["basic", "advanced", "minimal"], default="basic", help="Config template type")
```

### 6.3 Enhanced Dry-Run Functionality

The `--dry-run` flag provides comprehensive analysis without making changes to Odoo:

**Dry-Run Report Sections:**

1. **Distribution Overview**
   - Date range and total leads found
   - Dropback lead counts and assignments  
   - Filter impact analysis
   - Final distributable lead count

2. **Workload Analysis**
   - Current lead counts per salesperson
   - Target utilization percentages
   - Capacity deficits and surpluses

3. **Distribution Preview**
   - Proposed lead assignments per salesperson
   - Before/after workload projections
   - Final utilization percentages

4. **Strategy Details**
   - Distribution strategy configuration
   - Level priorities and targets
   - Campaign-specific rules

5. **Recommendations**
   - Workload imbalance warnings
   - Capacity optimization suggestions
   - Configuration improvements

**Example Output:**
```
🔍 DRY RUN REPORT - DAILY LEAD DISTRIBUTION ANALYSIS
================================================================================

📊 DISTRIBUTION OVERVIEW
--------------------------------------------------
📅 Date Range: 2024-01-01 to 2024-01-31 (30 days)
🔢 Total leads in date range: 1,250
↩️  Dropback leads (old): 85
📋 Leads after dropback: 1,165
✅ Final distributable leads: 892
👥 Eligible salespeople: 8

📤 DROPBACK ANALYSIS
--------------------------------------------------
   Voice: 45 leads → Pat Adler
   Apple: 32 leads → Kevin Levonas
   default: 8 leads → Administrator

🔍 FILTER IMPACT ANALYSIS
--------------------------------------------------
🚫 Leads filtered out: 273
   • Sales filter (has opportunities): 82 leads
   • DNC (Do Not Call) status: 55 leads
   • Missing required fields: 27 leads
   • Web source not matched: 55 leads
   • Other criteria: 54 leads

👥 CURRENT WORKLOAD ANALYSIS
--------------------------------------------------
┌──────────────┬──────┬───────────┬─────────┬────────┬─────────────┬─────────┐
│ Salesperson  │ Team │ Level     │ Current │ Target │ Utilization │ Deficit │
├──────────────┼──────┼───────────┼─────────┼────────┼─────────────┼─────────┤
│ Alice Smith  │ Voice│ senior    │    145  │    200 │      72.5%  │      55 │
│ Bob Johnson  │ Voice│ mid_level │    98   │    150 │      65.3%  │      52 │
└──────────────┴──────┴───────────┴─────────┴────────┴─────────────┴─────────┘

📋 DISTRIBUTION PREVIEW
--------------------------------------------------
📊 Total leads to distribute: 892

┌──────────────┬───────────┬─────────┬────────────┬────────┬─────────────┐
│ Salesperson  │ New Leads │ Current │ After Dist │ Target │ Final Util% │
├──────────────┼───────────┼─────────┼────────────┼────────┼─────────────┤
│ Alice Smith  │        55 │     145 │        200 │    200 │      100.0% │
│ Bob Johnson  │        52 │      98 │        150 │    150 │      100.0% │
└──────────────┴───────────┴─────────┴────────────┴────────┴─────────────┘

💡 RECOMMENDATIONS
--------------------------------------------------
   • Low overall utilization - consider increasing lead volume or reducing targets
   • High dropback volume - consider adjusting age thresholds or lead sources

📋 EXECUTION SUMMARY
--------------------------------------------------
🔍 This was a DRY RUN - no changes were made to Odoo
💡 To execute this distribution, run without --dry-run flag
```

### 6.4 Config File Generation

```python
class DailyDistributionConfigGenerator:
    """Generate boilerplate configuration files for daily distribution."""
    
    def __init__(self):
        """Initialize the config generator."""
        self.templates = {
            'basic': self._get_basic_template(),
            'advanced': self._get_advanced_template(),
            'minimal': self._get_minimal_template()
        }
    
    def generate_config(self, campaign: str = None, template: str = 'basic', output_path: str = None) -> str:
        """Generate a configuration file based on template and campaign."""
        if template not in self.templates:
            raise ValueError(f"Unknown template: {template}")
        
        config = self.templates[template].copy()
        
        # Customize for specific campaign
        if campaign:
            config = self._customize_for_campaign(config, campaign)
        
        # Convert to YAML
        import yaml
        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
        
        # Add header comments
        header = self._generate_header_comments(campaign, template)
        full_content = header + yaml_content
        
        # Write to file if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(full_content)
        
        return full_content
    
    def _get_basic_template(self) -> Dict[str, Any]:
        """Get basic configuration template."""
        return {
            "version": "1.0",
            "name": "Daily Lead Distribution",
            "description": "Automated daily lead distribution system",
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
            },
            
            "lead_finding": {
                "date_range": {
                    "older_than_days": 0,
                    "younger_than_days": 30,
                    "exclude_weekends": False,
                    "exclude_holidays": False
                },
                "web_sources": {
                    "source_type": "file",
                    "source_config": {
                        "file_path": "config/web_sources.txt"
                    },
                    "case_sensitive": False,
                    "exact_match": False,
                    "match_mode": "exact"
                },
                "campaigns": {
                    "types": ["voice_campaign_2024"],
                    "case_sensitive": False,
                    "exact_match": False,
                    "match_mode": "exact"
                },
                "additional_filters": {
                    "status": {
                        "values": ["new", "in_progress", "call_back", "utr"],
                        "case_sensitive": False,
                        "exact_match": False,
                        "match_mode": "exact"
                    },
                    "exclude_dnc": True,
                    "dnc_statuses": ["dnc", "do_not_call", "dont_call", "no_call", "blocked", "opt_out"],
                    "exclude_tags": {
                        "values": ["do_not_distribute", "test", "archived"],
                        "case_sensitive": False,
                        "match_mode": "exact"
                    },
                    "include_tags": {
                        "values": ["hot_lead", "vip", "priority"],
                        "case_sensitive": False,
                        "match_mode": "exact"
                    },
                    "required_fields": ["name", "email"],
                    "priority_range": {
                        "min": 1,
                        "max": 5
                    },
                    "assignment_filters": {
                        "exclude_assigned": True,
                        "exclude_closed": True,
                        "exclude_inactive_users": True
                    }
                }
            },
            
            "distribution": {
                "strategy": "level_based",
                "level_based": {
                    "levels": {
                        "senior": {
                            "target_leads": 200,
                            "priority": 1
                        },
                        "mid_level": {
                            "target_leads": 150,
                            "priority": 2
                        },
                        "junior": {
                            "target_leads": 100,
                            "priority": 3
                        }
                    },
                    "fill_strategy": "highest_priority_first",
                    "allow_overflow": False,
                    "overflow_limit": 10
                },
                "round_robin_override": {
                    "enabled": False
                }
            },
            
            "tracking": {
                "enabled": True,
                "track_individual_assignments": True,
                "track_pre_post_counts": True,
                "track_distribution_summary": True,
                "retention_days": 365,
                "archive_old_data": True,
                "batch_size": 1000,
                "async_tracking": False
            },
            
            "reporting": {
                "generate_report": True,
                "report_format": "csv",
                "report_location": "reports/",
                "include_analytics": True,
                "email_notification": False
            },
            
            "execution": {
                "dry_run": False,
                "max_leads_per_run": 1000,
                "batch_size": 50,
                "retry_failed": True,
                "max_retries": 3,
                "log_level": "INFO"
            }
        }
    
    def _get_advanced_template(self) -> Dict[str, Any]:
        """Get advanced configuration template with all features enabled."""
        basic = self._get_basic_template()
        
        # Add advanced features
        basic["lead_finding"]["web_sources"]["validate_sources"] = True
        basic["lead_finding"]["web_sources"]["exclude_invalid"] = True
        basic["lead_finding"]["web_sources"]["match_patterns"] = ["facebook*", "google_ads*", "website_contact"]
        
        basic["distribution"]["advanced_rules"] = {
            "skill_matching": {
                "enabled": True,
                "required_skills": ["enterprise_sales", "technical_knowledge"],
                "skill_weights": [0.7, 0.3]
            },
            "workload_balancing": {
                "enabled": True,
                "max_daily_distribution": 20,
                "min_daily_distribution": 5,
                "consider_weekend_workload": False
            },
            "priority_handling": {
                "high_priority_leads": "senior_only",
                "medium_priority_leads": "all_levels",
                "low_priority_leads": "junior_first"
            }
        }
        
        basic["tracking"]["async_tracking"] = True
        basic["tracking"]["batch_size"] = 1000
        
        return basic
    
    def _get_minimal_template(self) -> Dict[str, Any]:
        """Get minimal configuration template for basic usage."""
        return {
            "version": "1.0",
            "name": "Daily Lead Distribution - Minimal",
            "description": "Minimal configuration for daily lead distribution",
            "tags": ["lead-distribution", "minimal"],
            "author": "Sales Operations Team",
            "created_date": "2024-01-15",
            
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
                "target_campaign": "Voice",
                "active": True
            },
            
            "salesperson_selection": {
                "source_type": "file",
                "source_config": {
                    "file_path": "config/salespeople.txt"
                },
                "filters": {
                    "active_only": True
                }
            },
            
            "lead_finding": {
                "date_range": {
                    "older_than_days": 0,
                    "younger_than_days": 30
                },
                "additional_filters": {
                    "status": ["new", "in_progress"],
                    "exclude_dnc": True,
                    "dnc_statuses": ["dnc", "do_not_call"]
                }
            },
            
            "distribution": {
                "strategy": "round_robin"
            },
            
            "tracking": {
                "enabled": True,
                "track_individual_assignments": True,
                "track_pre_post_counts": True,
                "track_distribution_summary": True
            },
            
            "execution": {
                "dry_run": False,
                "log_level": "INFO"
            }
        }
    
    def _customize_for_campaign(self, config: Dict[str, Any], campaign: str) -> Dict[str, Any]:
        """Customize configuration for specific campaign."""
        config["campaign"]["name"] = campaign
        config["campaign"]["target_campaign"] = campaign
        config["salesperson_selection"]["campaign_filtering"]["target_campaign"] = campaign
        config["lead_finding"]["campaigns"]["types"] = [campaign]
        
        # Update description
        config["description"] = f"Automated daily lead distribution system for {campaign} campaigns"
        config["name"] = f"Daily Lead Distribution - {campaign}"
        
        return config
    
    def _generate_header_comments(self, campaign: str = None, template: str = 'basic') -> str:
        """Generate header comments for the config file."""
        header = f"""# Daily Lead Distribution Configuration
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Template: {template}
"""
        
        if campaign:
            header += f"# Campaign: {campaign}\n"
        
        header += """# 
# This configuration file controls the daily lead distribution system.
# Please review and modify the settings below before running the distribution.
#
# Key sections:
# - odoo_connection: Odoo database connection settings
# - database_connection: MySQL database connection for tracking and analytics
# - campaign: Campaign-specific settings
# - salesperson_selection: How to select eligible salespeople
# - lead_finding: Criteria for finding distributable leads
# - distribution: Strategy for distributing leads
# - tracking: Performance monitoring settings
# - reporting: Report generation settings
# - execution: Runtime behavior settings
#
# Environment Variables:
# ODOO_HOST, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD - Odoo connection
# TRACKING_DB_HOST, TRACKING_DB_NAME, TRACKING_DB_USER, TRACKING_DB_PASSWORD - MySQL tracking database
#

"""
        return header
```

### 6.4 CLI Integration with Existing ODLM

```python
# Integration with existing CLI class
class CLI:
    """Existing CLI class with dailydist command integration."""
    
    def _add_dailydist_args(self, parser: argparse.ArgumentParser):
        """Add dailydist command arguments."""
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--dry-run", action="store_true", help="Show plan without applying")
        parser.add_argument("--override-date-range", help="Override date range (start,end)")
        parser.add_argument("--force-round-robin", action="store_true", help="Force round robin distribution")
        parser.add_argument("--max-leads", type=int, help="Maximum leads to distribute")
        parser.add_argument("--generate-report", action="store_true", help="Generate distribution report")
        parser.add_argument("--report-format", choices=["csv", "json", "html"], default="csv")
        parser.add_argument("--report-location", help="Report output directory")
        parser.add_argument("--email-notification", action="store_true", help="Send email notification")
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
        
        # Config generation arguments
        parser.add_argument("--generate-config", action="store_true", help="Generate boilerplate config file")
        parser.add_argument("--output", help="Output file path for generated config")
        parser.add_argument("--campaign", help="Campaign name for config generation")
        parser.add_argument("--template", choices=["basic", "advanced", "minimal"], default="basic", help="Config template type")
        
        parser.epilog = """DAILY DISTRIBUTION EXAMPLES:

BASIC USAGE:
  odlm dailydist --config daily_distribution_config.yaml
  odlm dailydist --config config.yaml --dry-run

OVERRIDE SETTINGS:
  odlm dailydist --config config.yaml --max-leads 100
  odlm dailydist --config config.yaml --override-date-range "2024-01-01,2024-06-30"

REPORTING:
  odlm dailydist --config config.yaml --generate-report --report-format html
  odlm dailydist --config config.yaml --generate-report --report-location reports/

CONFIG GENERATION:
  odlm dailydist --generate-config --output daily_distribution_config.yaml
  odlm dailydist --generate-config --campaign UTR --template advanced --output utr_config.yaml
  odlm dailydist --generate-config --template minimal --output minimal_config.yaml
"""

    def handle_dailydist(self, args) -> int:
        """Handle dailydist command."""
        try:
            # Check if generating config
            if args.generate_config:
                return self._handle_config_generation(args)
            
            # Check if config file provided
            if not args.config:
                print("Error: --config file is required for daily distribution")
                print("Use --generate-config to create a boilerplate config file")
                return 1
            
            # Initialize daily distributor
            distributor = DailyLeadDistributor(args.config)
            
            # Run distribution
            result = distributor.run_daily_distribution(dry_run=args.dry_run)
            
            if result['success']:
                print(f"✓ Distribution completed successfully")
                print(f"  Leads found: {result['leads_found']}")
                print(f"  Leads distributed: {result['leads_distributed']}")
                print(f"  Execution time: {result['execution_time_seconds']:.2f} seconds")
                
                if args.generate_report:
                    self._generate_distribution_report(result, args)
                
                return 0
            else:
                print(f"✗ Distribution failed: {result.get('error', 'Unknown error')}")
                return 1
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    
    def _handle_config_generation(self, args) -> int:
        """Handle config file generation."""
        try:
            generator = DailyDistributionConfigGenerator()
            
            output_path = args.output or "daily_distribution_config.yaml"
            campaign = args.campaign
            template = args.template
            
            config_content = generator.generate_config(
                campaign=campaign,
                template=template,
                output_path=output_path
            )
            
            print(f"✓ Configuration file generated: {output_path}")
            print(f"  Template: {template}")
            if campaign:
                print(f"  Campaign: {campaign}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Error generating config: {e}")
            return 1
    
    def _generate_distribution_report(self, result: Dict[str, Any], args):
        """Generate distribution report."""
        # Implementation for report generation
        pass
```

### 6.5 Usage Examples

```bash
# Generate basic config file
odlm dailydist --generate-config --output daily_distribution_config.yaml

# Generate config for specific campaign
odlm dailydist --generate-config --campaign Voice --output voice_config.yaml

# Generate advanced config
odlm dailydist --generate-config --template advanced --output advanced_config.yaml

# Run daily distribution
odlm dailydist --config daily_distribution_config.yaml

# Dry run to see what would be distributed
odlm dailydist --config config.yaml --dry-run

# Run with custom settings
odlm dailydist --config config.yaml --max-leads 100 --override-date-range "2024-01-01,2024-06-30"

# Generate HTML report
odlm dailydist --config config.yaml --generate-report --report-format html --report-location reports/
```

## 7. Python API Implementation

### 7.1 Main Distribution Class

```python
class DailyLeadDistributor:
    """
    Main class for daily lead distribution operations.
    """
    
    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self.load_config(config_path)
        self.client = OdooClient.from_config(self.config)
        self.lead_manager = LeadManager(self.client)
        self.distributor = SmartDistributor()
        
        # Initialize database connection for tracking
        self.db_connection = self._initialize_database_connection()
        self.tracker = LeadDistributionTracker(self.db_connection)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML/JSON file."""
        pass
    
    def _initialize_database_connection(self):
        """Initialize MySQL database connection for tracking."""
        db_config = self.config.get('database_connection', {})
        
        if not db_config:
            return None
        
        try:
            import mysql.connector
            from mysql.connector import pooling
            
            # Parse connection parameters
            host = self._resolve_env_var(db_config.get('host', 'localhost'))
            port = db_config.get('port', 3306)
            database = self._resolve_env_var(db_config.get('database', 'lead_distribution_tracking'))
            username = self._resolve_env_var(db_config.get('username', 'tracking_user'))
            password = self._resolve_env_var(db_config.get('password', ''))
            
            # Create connection pool with simplified settings
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                pool_name='lead_distribution_pool',
                pool_size=5,
                autocommit=True,
                charset='utf8mb4'
            )
            
            return connection_pool
            
        except ImportError:
            print("Warning: mysql-connector-python not installed. Database tracking will be disabled.")
            return None
        except Exception as e:
            print(f"Warning: Failed to initialize database connection: {e}")
            print("Database tracking will be disabled.")
            return None
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variable references in configuration values."""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]  # Remove ${ and }
            return os.getenv(env_var, '')
        return value
    
    def _get_database_connection(self):
        """Get a database connection from the pool."""
        if not self.db_connection:
            return None
        
        try:
            return self.db_connection.get_connection()
        except Exception as e:
            print(f"Warning: Failed to get database connection: {e}")
            return None
    
    def _return_database_connection(self, connection):
        """Return a database connection to the pool."""
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"Warning: Failed to close database connection: {e}")
    
    def select_salespeople(self) -> List[Dict[str, Any]]:
        """Select eligible salespeople based on configuration."""
        selection_config = self.config.get('salesperson_selection', {})
        source_type = selection_config.get('source_type', 'campaign_table')
        
        if source_type == 'campaign_table':
            return self._select_salespeople_from_campaign_table()
        elif source_type == 'file':
            return self._select_salespeople_from_file()
        elif source_type == 'list':
            return self._select_salespeople_from_list()
        elif source_type == 'database':
            return self._select_salespeople_from_database()
        else:
            raise ValueError(f"Unknown salesperson selection source type: {source_type}")
    
    def _select_salespeople_from_campaign_table(self) -> List[Dict[str, Any]]:
        """Select salespeople from campaign table."""
        selection_config = self.config.get('salesperson_selection', {})
        campaign_config = selection_config.get('source_config', {}).get('campaign_table', {})
        campaign_filtering = selection_config.get('campaign_filtering', {})
        
        # Load campaign-salesperson relationships
        if 'file_path' in campaign_config:
            salespeople = self._load_campaign_table_from_file(campaign_config['file_path'])
        elif 'table_name' in campaign_config:
            salespeople = self._load_campaign_table_from_database(campaign_config['table_name'])
        else:
            raise ValueError("Campaign table source not specified")
        
        # Filter by target campaign
        target_campaign = campaign_filtering.get('target_campaign', 'UTR')
        salespeople = [sp for sp in salespeople if sp.get('campaign_name') == target_campaign]
        
        # Filter by active status
        if not campaign_filtering.get('include_inactive_salespeople', False):
            salespeople = [sp for sp in salespeople if sp.get('active', True)]
        
        # Exclude specific users
        excluded_users = campaign_filtering.get('exclude_specific_users', [])
        salespeople = [sp for sp in salespeople if sp.get('salesperson_name') not in excluded_users]
        
        # Apply additional filters
        salespeople = self._apply_salesperson_filters(salespeople)
        
        return salespeople
    
    def _load_campaign_table_from_database(self, table_name: str) -> List[Dict[str, Any]]:
        """Load campaign-salesperson relationships from database."""
        connection = self._get_database_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = f"""
                SELECT salesperson_name, salesperson_id, campaign_name, active, 
                       team, level, target_leads
                FROM {table_name}
                WHERE active = 1
                ORDER BY salesperson_name
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            salespeople = []
            for row in results:
                salespeople.append({
                    'salesperson_name': row['salesperson_name'],
                    'salesperson_id': row['salesperson_id'],
                    'campaign_name': row['campaign_name'],
                    'active': bool(row['active']),
                    'team': row.get('team', 'Voice'),
                    'level': row.get('level', 'mid_level'),
                    'target_leads': row.get('target_leads', 150)
                })
            
            return salespeople
            
        except Exception as e:
            print(f"Error loading campaign table from database: {e}")
            return []
        finally:
            cursor.close()
            self._return_database_connection(connection)
    
    def _load_campaign_table_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load campaign-salesperson relationships from CSV file."""
        import csv
        
        salespeople = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    salespeople.append({
                        'salesperson_name': row.get('salesperson_name'),
                        'salesperson_id': int(row.get('salesperson_id', 0)),
                        'campaign_name': row.get('campaign_name'),
                        'active': row.get('active', 'true').lower() == 'true',
                        'team': row.get('team', 'Voice'),
                        'level': row.get('level', 'mid_level'),
                        'target_leads': int(row.get('target_leads', 150))
                    })
        except FileNotFoundError:
            raise FileNotFoundError(f"Campaign table file not found: {file_path}")
        
        return salespeople
    
    def _select_salespeople_from_file(self) -> List[Dict[str, Any]]:
        """Select salespeople from legacy text file."""
        selection_config = self.config.get('salesperson_selection', {})
        file_path = selection_config.get('source_config', {}).get('file_path')
        
        salespeople = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 4:
                            salespeople.append({
                                'salesperson_name': parts[0],
                                'salesperson_id': int(parts[1]),
                                'level': parts[2],
                                'target_leads': int(parts[3])
                            })
        except FileNotFoundError:
            raise FileNotFoundError(f"Salespeople file not found: {file_path}")
        
        return self._apply_salesperson_filters(salespeople)
    
    def _select_salespeople_from_list(self) -> List[Dict[str, Any]]:
        """Select salespeople from configuration list."""
        selection_config = self.config.get('salesperson_selection', {})
        salespeople_list = selection_config.get('source_config', {}).get('salespeople_list', [])
        
        salespeople = []
        for name in salespeople_list:
            salespeople.append({
                'salesperson_name': name,
                'salesperson_id': 0,  # Will be resolved from Odoo
                'level': 'mid_level',
                'target_leads': 150
            })
        
        return self._apply_salesperson_filters(salespeople)
    
    def _select_salespeople_from_database(self) -> List[Dict[str, Any]]:
        """Select salespeople from database query."""
        selection_config = self.config.get('salesperson_selection', {})
        query_config = selection_config.get('source_config', {}).get('database_query', {})
        
        # Implementation to query Odoo database
        # This would execute the specified query against the Odoo database
        pass
    
    def _apply_salesperson_filters(self, salespeople: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply additional filters to salespeople list."""
        filters = self.config.get('salesperson_selection', {}).get('filters', {})
        
        filtered_salespeople = []
        for salesperson in salespeople:
            # Check active status
            if filters.get('active_only', True) and not salesperson.get('active', True):
                continue
            
            # Check team filter
            team_filter = filters.get('team_filter')
            if team_filter and salesperson.get('team') != team_filter:
                continue
            
            # Check experience level
            min_level = filters.get('min_experience_level', 1)
            if salesperson.get('level') == 'junior' and min_level > 1:
                continue
            
            # Check workload percentage
            max_workload = filters.get('max_workload_percentage', 90)
            current_workload = self._calculate_salesperson_workload(salesperson)
            if current_workload > max_workload:
                continue
            
            filtered_salespeople.append(salesperson)
        
        return filtered_salespeople
    
    def _calculate_salesperson_workload(self, salesperson: Dict[str, Any]) -> float:
        """Calculate current workload percentage for salesperson."""
        # Implementation to calculate workload based on current lead count vs target
        current_leads = self._get_salesperson_lead_count(salesperson)
        target_leads = salesperson.get('target_leads', 150)
        
        if target_leads == 0:
            return 0
        
        return (current_leads / target_leads) * 100
    
    def _get_salesperson_lead_count(self, salesperson: Dict[str, Any]) -> int:
        """Get current lead count for salesperson."""
        # Implementation to query Odoo for salesperson's current lead count
        pass
    
    def calculate_current_workload(self, salespeople: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Calculate current lead counts for each salesperson."""
        pass
    
    def find_distributable_leads(self) -> List[Dict[str, Any]]:
        """Find leads that match distribution criteria."""
        pass
    
    def distribute_leads(self, leads: List[Dict[str, Any]], salespeople: List[Dict[str, Any]]) -> Dict[int, List[int]]:
        """Distribute leads according to strategy."""
        pass
    
    def apply_distribution(self, assignments: Dict[int, List[int]]) -> bool:
        """Apply lead assignments to Odoo."""
        pass
    
    def generate_report(self, assignments: Dict[int, List[int]]) -> Dict[str, Any]:
        """Generate distribution report."""
        pass
    
    def run_daily_distribution(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute complete daily distribution process."""
        pass
```

### 7.2 Enhanced Filtering Implementation

```python
class EnhancedLeadFilter:
    """Enhanced lead filter with case-sensitive matching capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        self.web_source_config = config.get('lead_finding', {}).get('web_sources', {})
        self.campaign_config = config.get('lead_finding', {}).get('campaigns', {})
        self.status_config = config.get('lead_finding', {}).get('additional_filters', {}).get('status_matching', {})
        self.tag_config = config.get('lead_finding', {}).get('additional_filters', {}).get('tag_matching', {})
        self.dnc_config = config.get('lead_finding', {}).get('additional_filters', {}).get('dnc_filtering', {})
    
    def match_web_sources(self, lead_source: str, configured_sources: List[str]) -> bool:
        """Match web sources with configurable case sensitivity."""
        case_sensitive = self.web_source_config.get('case_sensitive', False)
        exact_match = self.web_source_config.get('exact_match', False)
        match_mode = self.web_source_config.get('match_mode', 'exact')
        
        if not case_sensitive:
            lead_source = lead_source.lower()
            configured_sources = [src.lower() for src in configured_sources]
        
        if match_mode == 'exact':
            return lead_source in configured_sources
        elif match_mode == 'partial':
            return any(src in lead_source or lead_source in src for src in configured_sources)
        elif match_mode == 'regex':
            import re
            patterns = self.web_source_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_source, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def match_campaigns(self, lead_campaign: str, configured_campaigns: List[str]) -> bool:
        """Match campaigns with configurable case sensitivity."""
        case_sensitive = self.campaign_config.get('case_sensitive', False)
        exact_match = self.campaign_config.get('exact_match', False)
        match_mode = self.campaign_config.get('match_mode', 'exact')
        
        if not case_sensitive:
            lead_campaign = lead_campaign.lower()
            configured_campaigns = [camp.lower() for camp in configured_campaigns]
        
        if match_mode == 'exact':
            return lead_campaign in configured_campaigns
        elif match_mode == 'partial':
            return any(camp in lead_campaign or lead_campaign in camp for camp in configured_campaigns)
        elif match_mode == 'regex':
            import re
            patterns = self.campaign_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_campaign, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def match_lead_status(self, lead_status: str, configured_statuses: List[str]) -> bool:
        """Match lead statuses with configurable case sensitivity."""
        case_sensitive = self.status_config.get('case_sensitive', False)
        exact_match = self.status_config.get('exact_match', False)
        match_mode = self.status_config.get('match_mode', 'exact')
        include_partial = self.status_config.get('include_partial_matches', True)
        
        if not case_sensitive:
            lead_status = lead_status.lower()
            configured_statuses = [status.lower() for status in configured_statuses]
        
        if match_mode == 'exact':
            return lead_status in configured_statuses
        elif match_mode == 'partial' and include_partial:
            return any(status in lead_status or lead_status in status for status in configured_statuses)
        elif match_mode == 'regex':
            import re
            patterns = self.status_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_status, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def is_dnc_lead(self, lead_status: str, lead_tags: List[str] = None) -> bool:
        """Check if lead has DNC (Do Not Call) status or tags."""
        if not self.dnc_config.get('enabled', True):
            return False
        
        # Check DNC status
        dnc_statuses = self.dnc_config.get('statuses', [])
        case_sensitive = self.dnc_config.get('case_sensitive', False)
        match_mode = self.dnc_config.get('match_mode', 'exact')
        
        if not case_sensitive:
            lead_status = lead_status.lower()
            dnc_statuses = [status.lower() for status in dnc_statuses]
        
        # Status matching
        if match_mode == 'exact':
            if lead_status in dnc_statuses:
                return True
        elif match_mode == 'partial':
            if any(status in lead_status or lead_status in status for status in dnc_statuses):
                return True
        elif match_mode == 'regex':
            import re
            patterns = self.dnc_config.get('regex_patterns', [])
            if any(re.match(pattern, lead_status, re.IGNORECASE if not case_sensitive else 0) 
                   for pattern in patterns):
                return True
        
        # Check DNC tags
        if lead_tags and self.dnc_config.get('exclude_dnc_tags', True):
            dnc_tags = self.dnc_config.get('dnc_tags', [])
            if not case_sensitive:
                lead_tags = [tag.lower() for tag in lead_tags]
                dnc_tags = [tag.lower() for tag in dnc_tags]
            
            if any(tag in dnc_tags for tag in lead_tags):
                return True
        
        return False
    
    def match_tags(self, lead_tags: List[str], configured_tags: List[str], exclude_mode: bool = False) -> bool:
        """Match tags with configurable case sensitivity."""
        case_sensitive = self.tag_config.get('case_sensitive', False)
        exact_match = self.tag_config.get('exact_match', False)
        match_mode = self.tag_config.get('match_mode', 'exact')
        
        if not case_sensitive:
            lead_tags = [tag.lower() for tag in lead_tags]
            configured_tags = [tag.lower() for tag in configured_tags]
        
        if match_mode == 'exact':
            if exclude_mode:
                return not any(tag in configured_tags for tag in lead_tags)
            else:
                return any(tag in configured_tags for tag in lead_tags)
        elif match_mode == 'partial':
            if exclude_mode:
                return not any(any(tag in lead_tag or lead_tag in tag for tag in configured_tags) 
                             for lead_tag in lead_tags)
            else:
                return any(any(tag in lead_tag or lead_tag in tag for tag in configured_tags) 
                         for lead_tag in lead_tags)
        elif match_mode == 'regex':
            import re
            patterns = self.tag_config.get('regex_patterns', [])
            for lead_tag in lead_tags:
                for pattern in patterns:
                    if re.match(pattern, lead_tag, re.IGNORECASE if not case_sensitive else 0):
                        return not exclude_mode
            return exclude_mode
        else:
            return False
    
    def validate_web_sources(self, sources: List[str]) -> List[str]:
        """Validate web sources against Odoo database."""
        if not self.web_source_config.get('validate_sources', False):
            return sources
        
        # Query Odoo to validate sources exist
        valid_sources = []
        for source in sources:
            # Implementation to check if source exists in Odoo
            if self._source_exists_in_odoo(source):
                valid_sources.append(source)
        
        return valid_sources
    
    def _source_exists_in_odoo(self, source: str) -> bool:
        """Check if web source exists in Odoo database."""
        # Implementation to query Odoo for source validation
        pass
```

### 7.3 Updated Lead Finding Implementation

```python
class EnhancedLeadFinder:
    """Enhanced lead finder with case-sensitive matching."""
    
    def __init__(self, config: Dict[str, Any], lead_manager: LeadManager):
        """Initialize with configuration and lead manager."""
        self.config = config
        self.lead_manager = lead_manager
        self.filter = EnhancedLeadFilter(config)
    
    def find_distributable_leads(self) -> List[Dict[str, Any]]:
        """Find leads that match all distribution criteria."""
        # Build base filter
        filter_obj = LeadFilter().model("crm.lead")
        
        # Apply date range filtering
        date_config = self.config.get('lead_finding', {}).get('date_range', {})
        filter_obj.by_date_range(
            start_date=date_config.get('custom_start_date'),
            end_date=date_config.get('custom_end_date'),
            field_name="source_date"
        )
        
        # Get all leads in date range
        leads = self.lead_manager.get_leads(filter_obj)
        
        # Apply enhanced filtering
        filtered_leads = []
        for lead in leads:
            if self._matches_all_criteria(lead):
                filtered_leads.append(lead)
        
        return filtered_leads
    
    def _matches_all_criteria(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches all filtering criteria."""
        # DNC filtering (check first to exclude early)
        if self._is_dnc_lead(lead):
            return False
        
        # Web source matching
        if not self._matches_web_sources(lead):
            return False
        
        # Campaign matching
        if not self._matches_campaigns(lead):
            return False
        
        # Lead status matching
        if not self._matches_lead_status(lead):
            return False
        
        # Tag matching
        if not self._matches_tags(lead):
            return False
        
        # Additional criteria
        if not self._matches_additional_criteria(lead):
            return False
        
        return True
    
    def _is_dnc_lead(self, lead: Dict[str, Any]) -> bool:
        """Check if lead has DNC status or tags."""
        lead_status = lead.get('status', '')
        lead_tags = lead.get('tag_ids', [])
        
        return self.filter.is_dnc_lead(lead_status, lead_tags)
    
    def _matches_web_sources(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches web source criteria."""
        web_source_config = self.config.get('lead_finding', {}).get('web_sources', {})
        
        if not web_source_config:
            return True
        
        lead_source = lead.get('source_id', [None])[0] if isinstance(lead.get('source_id'), list) else lead.get('source_id')
        if not lead_source:
            return False
        
        # Get configured sources
        sources = self._get_configured_web_sources(web_source_config)
        
        return self.filter.match_web_sources(str(lead_source), sources)
    
    def _matches_campaigns(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches campaign criteria."""
        campaign_config = self.config.get('lead_finding', {}).get('campaigns', {})
        
        if not campaign_config:
            return True
        
        lead_campaign = lead.get('campaign_id', [None])[0] if isinstance(lead.get('campaign_id'), list) else lead.get('campaign_id')
        if not lead_campaign:
            return False
        
        # Get configured campaigns
        campaigns = campaign_config.get('types', [])
        
        return self.filter.match_campaigns(str(lead_campaign), campaigns)
    
    def _matches_lead_status(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches status criteria."""
        status_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('status', {})
        
        if isinstance(status_config, dict):
            statuses = status_config.get('values', [])
        else:
            statuses = status_config if isinstance(status_config, list) else []
        
        if not statuses:
            return True
        
        lead_status = lead.get('status', '')
        if not lead_status:
            return False
        
        return self.filter.match_lead_status(lead_status, statuses)
    
    def _matches_tags(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches tag criteria."""
        additional_filters = self.config.get('lead_finding', {}).get('additional_filters', {})
        
        # Check exclude tags
        exclude_tags = additional_filters.get('exclude_tags', {})
        if isinstance(exclude_tags, dict):
            exclude_values = exclude_tags.get('values', [])
        else:
            exclude_values = exclude_tags if isinstance(exclude_tags, list) else []
        
        if exclude_values:
            lead_tags = lead.get('tag_ids', [])
            if self.filter.match_tags(lead_tags, exclude_values, exclude_mode=True):
                return False
        
        # Check include tags
        include_tags = additional_filters.get('include_tags', {})
        if isinstance(include_tags, dict):
            include_values = include_tags.get('values', [])
        else:
            include_values = include_tags if isinstance(include_tags, list) else []
        
        if include_values:
            lead_tags = lead.get('tag_ids', [])
            if not self.filter.match_tags(lead_tags, include_values, exclude_mode=False):
                return False
        
        return True
    
    def _matches_additional_criteria(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches additional criteria."""
        additional_filters = self.config.get('lead_finding', {}).get('additional_filters', {})
        
        # Check required fields
        required_fields = additional_filters.get('required_fields', [])
        for field in required_fields:
            if not lead.get(field):
                return False
        
        # Check priority range
        priority_range = additional_filters.get('priority_range', {})
        if priority_range:
            min_priority = priority_range.get('min', 1)
            max_priority = priority_range.get('max', 5)
            lead_priority = lead.get('priority', 1)
            if not (min_priority <= lead_priority <= max_priority):
                return False
        
        # Check assignment filters
        assignment_filters = additional_filters.get('assignment_filters', {})
        if assignment_filters.get('exclude_assigned', False):
            if lead.get('user_id'):
                return False
        
        if assignment_filters.get('exclude_closed', False):
            closed_statuses = ['won', 'lost', 'cancelled']
            if lead.get('status') in closed_statuses:
                return False
        
        return True
    
    def _get_configured_web_sources(self, web_source_config: Dict[str, Any]) -> List[str]:
        """Get configured web sources from various sources."""
        source_type = web_source_config.get('source_type', 'config')
        
        if source_type == 'file':
            file_path = web_source_config.get('source_config', {}).get('file_path')
            return self._read_sources_from_file(file_path)
        elif source_type == 'database':
            table_name = web_source_config.get('source_config', {}).get('table_name')
            return self._read_sources_from_database(table_name)
        else:  # config
            return web_source_config.get('source_config', {}).get('sources', [])
    
    def _read_sources_from_file(self, file_path: str) -> List[str]:
        """Read web sources from file."""
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []
    
    def _read_sources_from_database(self, table_name: str) -> List[str]:
        """Read web sources from database table."""
        # Implementation to query database table
        pass
```

### 7.4 Usage Examples

```python
# Basic usage
from odoo_lead_manager.daily_distribution import DailyLeadDistributor

distributor = DailyLeadDistributor("config/daily_distribution.yaml")
result = distributor.run_daily_distribution()

# Dry run
result = distributor.run_daily_distribution(dry_run=True)

# Custom configuration
distributor = DailyLeadDistributor("config/custom_distribution.yaml")
distributor.config["distribution"]["strategy"] = "round_robin"
result = distributor.run_daily_distribution()
```

## 8. Reporting and Analytics

### 8.1 Distribution Report

```yaml
reporting:
  distribution_summary:
    total_leads_found: 150
    total_leads_distributed: 120
    leads_not_distributed: 30
    reason_not_distributed: "No eligible salespeople"
  
  salesperson_summary:
    - name: "Alice Smith"
      id: 1
      level: "senior"
      target_leads: 200
      current_leads: 180
      leads_received: 20
      new_total: 200
      utilization: 100%
    
    - name: "Bob Johnson"
      id: 2
      level: "senior"
      target_leads: 200
      current_leads: 190
      leads_received: 10
      new_total: 200
      utilization: 100%
  
  lead_characteristics:
    by_source:
      facebook_form: 45
      google_ads: 35
      website_contact: 40
    
    by_campaign:
      UTR: 60
      FPFC: 60
    
    by_date_range:
      older_than_2_months: 120
      younger_than_6_months: 120
```

### 8.2 Analytics Dashboard

```python
class DistributionAnalytics:
    """Analytics for distribution performance."""
    
    def calculate_distribution_efficiency(self) -> float:
        """Calculate how efficiently leads were distributed."""
        pass
    
    def analyze_salesperson_utilization(self) -> Dict[str, float]:
        """Analyze how well salespeople are utilized."""
        pass
    
    def track_distribution_trends(self, days: int = 30) -> Dict[str, Any]:
        """Track distribution trends over time."""
        pass
    
    def generate_performance_metrics(self) -> Dict[str, Any]:
        """Generate comprehensive performance metrics."""
        pass
```

## 9. Lead Tracking and Monitoring System

### 9.1 Overview

The lead tracking and monitoring system will record daily lead distribution metrics to enable historical analysis, performance monitoring, and distribution optimization. This system will track lead counts before and after distribution for each salesperson on a daily basis.

### 9.2 Data Model

#### 9.2.1 Lead Distribution Tracking Table

```sql
-- Daily lead distribution tracking
CREATE TABLE lead_distribution_tracking (
    id SERIAL PRIMARY KEY,
    distribution_date DATE NOT NULL,
    salesperson_id INTEGER NOT NULL,
    salesperson_name VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(255),
    
    -- Lead counts before distribution
    leads_before_total INTEGER DEFAULT 0,
    leads_before_new INTEGER DEFAULT 0,
    leads_before_in_progress INTEGER DEFAULT 0,
    leads_before_call_back INTEGER DEFAULT 0,
    leads_before_utr INTEGER DEFAULT 0,
    leads_before_full_pitch INTEGER DEFAULT 0,
    leads_before_won INTEGER DEFAULT 0,
    leads_before_lost INTEGER DEFAULT 0,
    
    -- Lead counts after distribution
    leads_after_total INTEGER DEFAULT 0,
    leads_after_new INTEGER DEFAULT 0,
    leads_after_in_progress INTEGER DEFAULT 0,
    leads_after_call_back INTEGER DEFAULT 0,
    leads_after_utr INTEGER DEFAULT 0,
    leads_after_full_pitch INTEGER DEFAULT 0,
    leads_after_won INTEGER DEFAULT 0,
    leads_after_lost INTEGER DEFAULT 0,
    
    -- Distribution metrics
    leads_received INTEGER DEFAULT 0,
    leads_distributed_from INTEGER DEFAULT 0,
    target_leads INTEGER DEFAULT 0,
    utilization_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Metadata
    distribution_strategy VARCHAR(50) DEFAULT 'round_robin',
    active_status BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_distribution_date (distribution_date),
    INDEX idx_salesperson_date (salesperson_id, distribution_date),
    INDEX idx_campaign_date (campaign_name, distribution_date),
    UNIQUE KEY unique_salesperson_date (salesperson_id, distribution_date, campaign_name)
);
```

#### 9.2.2 Lead Distribution Summary Table

```sql
-- Daily distribution summary
CREATE TABLE lead_distribution_summary (
    id SERIAL PRIMARY KEY,
    distribution_date DATE NOT NULL,
    campaign_name VARCHAR(255),
    
    -- Overall metrics
    total_leads_found INTEGER DEFAULT 0,
    total_leads_distributed INTEGER DEFAULT 0,
    total_leads_not_distributed INTEGER DEFAULT 0,
    total_salespeople_eligible INTEGER DEFAULT 0,
    total_salespeople_received_leads INTEGER DEFAULT 0,
    
    -- Distribution efficiency
    distribution_efficiency_percentage DECIMAL(5,2) DEFAULT 0.0,
    average_leads_per_salesperson DECIMAL(5,2) DEFAULT 0.0,
    max_leads_to_single_salesperson INTEGER DEFAULT 0,
    min_leads_to_single_salesperson INTEGER DEFAULT 0,
    
    -- Lead characteristics
    leads_by_source JSON,  -- {"facebook": 45, "google": 35}
    leads_by_status JSON,  -- {"new": 60, "in_progress": 40}
    leads_by_campaign JSON, -- {"UTR": 60, "FPFC": 60}
    
    -- Configuration used
    date_range_start DATE,
    date_range_end DATE,
    distribution_strategy VARCHAR(50),
    excluded_users JSON,
    
    -- Metadata
    execution_time_seconds DECIMAL(10,2),
    dry_run BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_summary_date (distribution_date),
    INDEX idx_campaign_summary (campaign_name, distribution_date),
    UNIQUE KEY unique_date_campaign (distribution_date, campaign_name)
);
```

#### 9.2.3 Lead Assignment History Table

```sql
-- Individual lead assignment tracking
CREATE TABLE lead_assignment_history (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL,
    distribution_date DATE NOT NULL,
    
    -- Assignment details
    previous_user_id INTEGER,
    previous_user_name VARCHAR(255),
    new_user_id INTEGER NOT NULL,
    new_user_name VARCHAR(255) NOT NULL,
    
    -- Lead details
    lead_status VARCHAR(50),
    lead_source VARCHAR(100),
    lead_campaign VARCHAR(100),
    lead_priority INTEGER,
    
    -- Distribution context
    campaign_name VARCHAR(255),
    distribution_strategy VARCHAR(50),
    distribution_reason VARCHAR(255), -- "round_robin", "workload_balance", etc.
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_lead_id (lead_id),
    INDEX idx_distribution_date (distribution_date),
    INDEX idx_new_user (new_user_id, distribution_date),
    INDEX idx_previous_user (previous_user_id, distribution_date)
);
```

### 9.3 Python Implementation

#### 9.3.1 Lead Tracking Class

```python
class LeadDistributionTracker:
    """Track and record lead distribution metrics."""
    
    def __init__(self, db_connection=None):
        """Initialize tracker with optional database connection."""
        self.db_connection = db_connection
        self.tracking_enabled = db_connection is not None
    
    def record_pre_distribution_counts(self, salespeople: List[Dict], campaign_name: str) -> Dict[int, Dict]:
        """Record lead counts before distribution for each salesperson."""
        if not self.tracking_enabled:
            return {}
        
        pre_counts = {}
        for salesperson in salespeople:
            user_id = salesperson['id']
            counts = self._get_salesperson_lead_counts(user_id)
            pre_counts[user_id] = counts
            
            # Store in database
            self._store_pre_distribution_counts(
                user_id, salesperson['name'], campaign_name, counts
            )
        
        return pre_counts
    
    def record_post_distribution_counts(self, salespeople: List[Dict], 
                                      assignments: Dict[int, List[int]], 
                                      campaign_name: str) -> Dict[int, Dict]:
        """Record lead counts after distribution for each salesperson."""
        if not self.tracking_enabled:
            return {}
        
        post_counts = {}
        for salesperson in salespeople:
            user_id = salesperson['id']
            counts = self._get_salesperson_lead_counts(user_id)
            post_counts[user_id] = counts
            
            # Calculate distribution metrics
            leads_received = len(assignments.get(user_id, []))
            pre_counts = self._get_stored_pre_counts(user_id, campaign_name)
            
            # Store in database
            self._store_post_distribution_counts(
                user_id, salesperson['name'], campaign_name, 
                counts, leads_received, pre_counts
            )
        
        return post_counts
    
    def record_lead_assignments(self, assignments: Dict[int, List[int]], 
                               campaign_name: str, strategy: str):
        """Record individual lead assignments."""
        if not self.tracking_enabled:
            return
        
        for user_id, lead_ids in assignments.items():
            for lead_id in lead_ids:
                self._store_lead_assignment(
                    lead_id, user_id, campaign_name, strategy
                )
    
    def generate_distribution_summary(self, campaign_name: str, 
                                   total_leads_found: int,
                                   total_leads_distributed: int,
                                   execution_time: float,
                                   config: Dict) -> Dict:
        """Generate and store distribution summary."""
        if not self.tracking_enabled:
            return {}
        
        summary = {
            'total_leads_found': total_leads_found,
            'total_leads_distributed': total_leads_distributed,
            'total_leads_not_distributed': total_leads_found - total_leads_distributed,
            'distribution_efficiency_percentage': (
                (total_leads_distributed / total_leads_found * 100) 
                if total_leads_found > 0 else 0
            ),
            'execution_time_seconds': execution_time,
            'campaign_name': campaign_name,
            'distribution_strategy': config.get('distribution', {}).get('strategy', 'round_robin'),
            'date_range_start': config.get('lead_finding', {}).get('date_range', {}).get('older_than_days'),
            'date_range_end': config.get('lead_finding', {}).get('date_range', {}).get('younger_than_days')
        }
        
        self._store_distribution_summary(summary)
        return summary
    
    def _get_salesperson_lead_counts(self, user_id: int) -> Dict[str, int]:
        """Get current lead counts for a salesperson by status."""
        # Implementation to query Odoo for lead counts
        pass
    
    def _store_pre_distribution_counts(self, user_id: int, user_name: str, 
                                     campaign_name: str, counts: Dict[str, int]):
        """Store pre-distribution counts in database."""
        # Database insertion logic
        pass
    
    def _store_post_distribution_counts(self, user_id: int, user_name: str,
                                      campaign_name: str, counts: Dict[str, int],
                                      leads_received: int, pre_counts: Dict[str, int]):
        """Store post-distribution counts and calculate metrics."""
        # Database update logic
        pass
    
    def _store_lead_assignment(self, lead_id: int, user_id: int, 
                              campaign_name: str, strategy: str):
        """Store individual lead assignment."""
        # Database insertion logic
        pass
    
    def _store_distribution_summary(self, summary: Dict):
        """Store distribution summary."""
        # Database insertion logic
        pass
```

#### 9.3.2 Integration with Daily Distributor

```python
class DailyLeadDistributor:
    """Main class for daily lead distribution operations."""
    
    def __init__(self, config_path: str, db_connection=None):
        """Initialize with configuration file and optional database connection."""
        self.config = self.load_config(config_path)
        self.client = OdooClient.from_config(self.config)
        self.lead_manager = LeadManager(self.client)
        self.distributor = SmartDistributor()
        self.tracker = LeadDistributionTracker(db_connection)
    
    def run_daily_distribution(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute complete daily distribution process with tracking."""
        start_time = time.time()
        
        try:
            # Get campaign name from config
            campaign_name = self.config.get('campaign_name', 'default')
            
            # Select salespeople
            salespeople = self.select_salespeople()
            
            # Record pre-distribution counts
            pre_counts = self.tracker.record_pre_distribution_counts(salespeople, campaign_name)
            
            # Find distributable leads
            leads = self.find_distributable_leads()
            
            if not leads:
                return {
                    'success': False,
                    'message': 'No leads found for distribution',
                    'leads_found': 0,
                    'leads_distributed': 0
                }
            
            # Distribute leads
            if dry_run:
                assignments = self.distributor.plan_distribution(leads, salespeople)
                applied = False
            else:
                assignments = self.distributor.distribute_leads(leads, salespeople)
                applied = self.apply_distribution(assignments)
            
            # Record post-distribution counts
            post_counts = self.tracker.record_post_distribution_counts(
                salespeople, assignments, campaign_name
            )
            
            # Record individual assignments
            if not dry_run and applied:
                self.tracker.record_lead_assignments(assignments, campaign_name, 
                                                   self.config.get('distribution', {}).get('strategy', 'round_robin'))
            
            # Generate summary
            execution_time = time.time() - start_time
            summary = self.tracker.generate_distribution_summary(
                campaign_name, len(leads), sum(len(leads) for leads in assignments.values()),
                execution_time, self.config
            )
            
            return {
                'success': True,
                'leads_found': len(leads),
                'leads_distributed': sum(len(leads) for leads in assignments.values()),
                'salespeople_count': len(salespeople),
                'execution_time_seconds': execution_time,
                'dry_run': dry_run,
                'pre_counts': pre_counts,
                'post_counts': post_counts,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time_seconds': time.time() - start_time
            }
```

### 9.4 Configuration for Tracking

```yaml
# Add to main configuration file
tracking:
  enabled: true
  
  # Use the main database_connection section
  # database_connection is defined at the root level
  
  # What to track
  track_individual_assignments: true
  track_pre_post_counts: true
  track_distribution_summary: true
  
  # Retention policy
  retention_days: 365  # Keep data for 1 year
  archive_old_data: true
  
  # Performance settings
  batch_size: 1000
  async_tracking: false  # Set to true for better performance
```

**Database Connection Usage:**
```yaml
# The tracking system will use the database_connection section
# defined at the root level of the configuration

# Example environment variables for database connection:
# TRACKING_DB_HOST=localhost
# TRACKING_DB_NAME=lead_distribution_tracking
# TRACKING_DB_USER=tracking_user
# TRACKING_DB_PASSWORD=secure_password
# DB_CA_CERT=/path/to/ca-cert.pem (optional)
# DB_CLIENT_CERT=/path/to/client-cert.pem (optional)
# DB_CLIENT_KEY=/path/to/client-key.pem (optional)
```

### 9.5 Reporting and Analytics

#### 9.5.1 Daily Distribution Report

```python
class DistributionReporter:
    """Generate reports from tracking data."""
    
    def generate_daily_report(self, date: date, campaign_name: str = None) -> Dict:
        """Generate daily distribution report."""
        # Query tracking tables for the specified date
        pass
    
    def generate_salesperson_report(self, user_id: int, date_range: Tuple[date, date]) -> Dict:
        """Generate report for specific salesperson over date range."""
        # Query tracking data for specific user
        pass
    
    def generate_campaign_report(self, campaign_name: str, date_range: Tuple[date, date]) -> Dict:
        """Generate report for specific campaign over date range."""
        # Query tracking data for specific campaign
        pass
    
    def generate_trend_analysis(self, days: int = 30) -> Dict:
        """Generate trend analysis over specified days."""
        # Analyze trends in distribution patterns
        pass
```

#### 9.5.2 Sample Reports

**Daily Distribution Summary:**
```json
{
  "date": "2024-01-15",
  "campaign": "UTR",
  "total_leads_found": 150,
  "total_leads_distributed": 120,
  "distribution_efficiency": 80.0,
  "salespeople_participated": 8,
  "average_leads_per_salesperson": 15.0,
  "execution_time_seconds": 45.2,
  "top_recipients": [
    {"user_id": 1, "name": "Alice Smith", "leads_received": 20},
    {"user_id": 2, "name": "Bob Johnson", "leads_received": 18}
  ]
}
```

**Salesperson Performance Report:**
```json
{
  "user_id": 1,
  "name": "Alice Smith",
  "date_range": ["2024-01-01", "2024-01-31"],
  "total_leads_received": 450,
  "average_leads_per_day": 14.5,
  "utilization_trend": [85, 90, 95, 88, 92],
  "distribution_efficiency": 92.5,
  "lead_status_distribution": {
    "new": 200,
    "in_progress": 150,
    "won": 80,
    "lost": 20
  }
}
```

This comprehensive tracking system provides detailed insights into lead distribution patterns, enabling data-driven optimization of the distribution algorithm and monitoring of salesperson workload and performance.

## 9. Error Handling and Validation

### 9.1 Configuration Validation

```python
class ConfigurationValidator:
    """Validate configuration files and settings."""
    
    def validate_config_structure(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration structure and required fields."""
        pass
    
    def validate_salespeople_file(self, file_path: str) -> List[str]:
        """Validate salespeople file format and content."""
        pass
    
    def validate_web_sources_file(self, file_path: str) -> List[str]:
        """Validate web sources file format and content."""
        pass
    
    def validate_odoo_connection(self, config: Dict[str, Any]) -> bool:
        """Validate Odoo connection settings."""
        pass
```

### 9.2 Error Handling

```yaml
error_handling:
  retry_failed_assignments: true
  max_retries: 3
  retry_delay_seconds: 5
  
  error_thresholds:
    max_failed_assignments: 10
    max_connection_errors: 3
    max_validation_errors: 5
  
  fallback_strategies:
    when_no_salespeople_found: "skip_distribution"
    when_no_leads_found: "generate_warning"
    when_distribution_fails: "use_round_robin"
```

## 10. Testing Requirements

### 10.1 Unit Tests

```python
class TestDailyLeadDistributor:
    """Test cases for daily lead distribution."""
    
    def test_config_loading(self):
        """Test configuration file loading."""
        pass
    
    def test_salesperson_selection(self):
        """Test salesperson selection logic."""
        pass
    
    def test_lead_finding(self):
        """Test lead finding with various filters."""
        pass
    
    def test_distribution_strategies(self):
        """Test different distribution strategies."""
        pass
    
    def test_error_handling(self):
        """Test error handling and recovery."""
        pass
```

### 10.2 Integration Tests

```python
class TestDailyDistributionIntegration:
    """Integration tests for complete workflow."""
    
    def test_complete_daily_workflow(self):
        """Test complete daily distribution workflow."""
        pass
    
    def test_dry_run_functionality(self):
        """Test dry run without making changes."""
        pass
    
    def test_report_generation(self):
        """Test report generation and formatting."""
        pass
```

## 11. Deployment and Automation

### 11.1 Cron Job Setup

```bash
# Daily distribution at 9 AM
0 9 * * * /usr/bin/python3 -m odoo_lead_manager.daily_distribution --config /path/to/config.yaml

# Weekly distribution on Monday at 8 AM
0 8 * * 1 /usr/bin/python3 -m odoo_lead_manager.daily_distribution --config /path/to/config.yaml --generate-report
```

### 11.2 Docker Support

```dockerfile
# Dockerfile for daily distribution
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "-m", "odoo_lead_manager.daily_distribution", "--config", "/app/config/daily_distribution.yaml"]
```

## 12. Performance Considerations

### 12.1 Optimization Strategies

1. **Batch Processing**: Process leads in batches to avoid memory issues
2. **Caching**: Cache salesperson data and lead counts
3. **Parallel Processing**: Distribute leads in parallel when possible
4. **Database Optimization**: Use efficient queries for large datasets

### 12.2 Monitoring

```yaml
monitoring:
  enable_performance_tracking: true
  log_execution_time: true
  track_memory_usage: true
  alert_on_slow_execution: true
  slow_execution_threshold_seconds: 300
```

## 13. Security Considerations

### 13.1 Configuration Security

1. **Environment Variables**: Use environment variables for sensitive data
2. **File Permissions**: Secure configuration files with appropriate permissions
3. **Audit Logging**: Log all distribution activities for audit purposes

### 13.2 Data Protection

```yaml
security:
  encrypt_sensitive_data: true
  log_audit_trail: true
  mask_personal_data: true
  retention_policy_days: 90
```

## 14. Future Enhancements

### 14.1 Machine Learning Integration

- **Predictive Distribution**: Use ML to predict optimal lead assignments
- **Performance Prediction**: Predict lead conversion likelihood
- **Dynamic Workload Balancing**: Automatically adjust based on performance

### 14.2 Advanced Features

- **Multi-tenant Support**: Support for multiple Odoo instances
- **Real-time Distribution**: Real-time lead distribution as they come in
- **Mobile Notifications**: Push notifications for new assignments
- **Advanced Analytics**: Deep learning-based performance analytics

## 15. Implementation Timeline

### Phase 1 (Week 1-2): Core Infrastructure
- Configuration file structure
- Basic CLI command
- Salesperson selection logic
- Lead finding algorithms

### Phase 2 (Week 3-4): Distribution Engine
- Level-based distribution
- Round robin override
- Assignment application
- Basic reporting

### Phase 3 (Week 5-6): Advanced Features
- Advanced filtering
- Error handling
- Performance optimization
- Comprehensive testing

### Phase 4 (Week 7-8): Production Readiness
- Documentation
- Deployment automation
- Monitoring and alerting
- Security hardening

## 16. Success Metrics

### 16.1 Performance Metrics
- **Distribution Efficiency**: >95% of eligible leads distributed
- **Execution Time**: <5 minutes for 1000 leads
- **Error Rate**: <1% failed assignments
- **User Satisfaction**: >90% salesperson satisfaction

### 16.2 Business Metrics
- **Lead Response Time**: Reduced by 50%
- **Sales Conversion**: Improved by 15%
- **Workload Balance**: Standard deviation <10% across salespeople
- **Manual Intervention**: Reduced by 80%

This comprehensive specification provides a complete roadmap for implementing the daily lead distribution system within the Odoo Lead Manager package, ensuring it meets all the requirements while maintaining flexibility and extensibility for future enhancements. 

## 17. Current Implementation Summary

### 17.1 Overview of Existing Pipeline

The current lead distribution system is implemented in R and follows a specific workflow for UTR (Universal Tracking Reference) campaign distribution. The system is designed to redistribute leads from both active and inactive salespeople based on specific criteria.

### 17.2 Current Workflow Analysis

**Main Distribution Function:**
```r
main_utr_distribution_workflow(all_leads, campaign_name, round_robin=T, return_input=F, person_filter=NULL)
```

**Key Components:**

1. **Salesperson Selection:**
   - Filters salespeople by campaign (`category_campaign %in% campaign_name`) - where campaign_name refers to salesperson campaigns like "Voice" or "Apple"
   - Excludes specific users: "Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"
   - Distinguishes between active (`active = 'True'`) and inactive (`active = 'False'`) salespeople

2. **Lead Finding Logic:**
   - **Date Range**: Last 30 days (`lowerlimit=0, upperlimit=30`)
   - **Date Field**: `source_date`
   - **Activity Deadline**: Excludes leads with deadline within 4 days of today
   - **Status Filtering**: Different statuses for active vs inactive salespeople

3. **Distribution Strategy:**
   - **Round-Robin**: Random sampling of salespeople, then sequential distribution
   - **Lead Assignment**: Updates `closer_id`, `open_user_id`, `user_id` to assigned salesperson
   - **Status Reset**: Sets all distributed leads to "New" status
   - **Team Assignment**: Sets `team_id` to "Voice"

### 17.3 Current Implementation Details

**Lead Filtering Criteria:**
```r
# Active Salespeople Leads
- Date Range: source_date within last 30 days
- Lead Status: "Utr", "Call Back"  # Note: These are lead status fields, not campaigns
- Activity Deadline: > 4 days from today OR missing deadline
- Excluded Users: Drew Cox, Patrick Adler, Administrator, Marc Spiegel

# Inactive Salespeople Leads  
- Date Range: source_date within last 30 days
- Lead Status: "Utr", "Call Back", "Full Pitch Follow Up", "Full Pitch Follow Up ", "New"  # Note: These are lead status fields, not campaigns
- Activity Deadline: > 4 days from today OR missing deadline
- Excluded Users: Drew Cox, Patrick Adler, Administrator, Marc Spiegel
```

**Distribution Process:**
```r
dist_round_robin(dat, sales.name):
1. Randomize salespeople order
2. While leads remain:
   - For each salesperson:
     - Sample 1 lead randomly
     - Filter out leads already assigned to this salesperson
     - Update lead assignment fields
     - Set status to "New", team_id to "Voice"
     - Remove assigned lead from pool
3. Return distributed leads
```

**Data Flow:**
1. **Input**: `all_leads` (complete lead dataset), `campaign_name` (target salesperson campaign like "Voice" or "Apple")
2. **Processing**: 
   - Get salespeople counts by campaign (salesperson campaigns like "Voice", "Apple")
   - Filter leads by active/inactive status and criteria (lead status fields like "Utr", "Call Back")
   - Combine active and inactive leads
3. **Distribution**: Round-robin assignment to eligible salespeople
4. **Output**: Updated leads with new assignments
5. **Backup**: Save distribution results to RDS file

### 17.4 Current Implementation Strengths

1. **Simple and Effective**: Straightforward round-robin distribution
2. **Status-Aware**: Different criteria for active vs inactive salespeople
3. **Activity Deadline Protection**: Prevents redistribution of recently scheduled leads
4. **User Exclusion**: Protects specific users from redistribution
5. **Audit Trail**: Saves backup files for tracking

### 17.5 Current Implementation Limitations

1. **Fixed Date Range**: Hard-coded 30-day window
2. **Limited Distribution Strategy**: Only round-robin, no workload balancing
3. **No Performance Metrics**: No tracking of distribution effectiveness
4. **Manual Configuration**: Hard-coded user exclusions and status lists
5. **No Error Handling**: Limited validation and error recovery
6. **R-Specific**: Not easily portable to other environments

### 17.6 Migration Strategy

**Phase 1: Direct Port**
- Port current R logic to Python
- Maintain exact same filtering criteria
- Implement round-robin distribution
- Preserve user exclusions and status logic

**Phase 2: Enhanced Features**
- Add configurable date ranges
- Implement multiple distribution strategies
- Add performance monitoring
- Include error handling and validation

**Phase 3: Advanced Capabilities**
- Workload balancing algorithms
- Machine learning-based distribution
- Real-time performance analytics
- Multi-tenant support

### 17.7 Configuration Mapping

**Current R Logic → YAML Configuration:**
```yaml
# Current hard-coded values
current_implementation:
  date_range:
    lowerlimit: 0
    upperlimit: 30
  
  excluded_users:
    - "Drew Cox"
    - "Patrick Adler"
    - "Administrator" 
    - "Marc Spiegel"
  
  # Lead status filtering (not campaign)
  status_filters:
    active_salespeople:
      statuses: ["Utr", "Call Back"]
    inactive_salespeople:
      statuses: ["Utr", "Call Back", "Full Pitch Follow Up", "Full Pitch Follow Up ", "New"]
  
  # Salesperson campaign filtering (separate from lead status)
  campaign_filters:
    campaign_name: "Voice"  # The salesperson campaign being distributed (Voice, Apple, etc.)
  
  # DNC filtering (new addition)
  dnc_filtering:
    enabled: true
    statuses: ["dnc", "do_not_call", "dont_call", "no_call", "blocked", "opt_out"]
    case_sensitive: false
    match_mode: "exact"
    exclude_dnc_tags: true
    dnc_tags: ["do_not_call", "dnc", "blocked", "opt_out"]
  
  activity_deadline:
    exclude_within_days: 4
  
  distribution:
    strategy: "round_robin"
    randomize_order: true
    team_assignment: "Voice"
    status_reset: "New"
```

This summary provides a complete understanding of the current implementation, enabling accurate migration to the new Python-based system while preserving all existing functionality and business logic. 