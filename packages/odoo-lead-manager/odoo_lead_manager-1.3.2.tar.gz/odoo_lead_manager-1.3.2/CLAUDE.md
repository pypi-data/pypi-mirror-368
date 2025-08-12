# CLAUDE.md - Odoo Lead Manager

This file contains comprehensive documentation for the Odoo Lead Manager package, designed to help Claude Code understand and work with this codebase efficiently.

## 📦 Package Overview

**Name**: odoo-lead-manager  
**Purpose**: Comprehensive Python package for managing Odoo leads with intelligent distribution  
**Target**: res.partner model in Odoo  
**Architecture**: Modular design with clear separation of concerns

## 🏗️ Architecture & Design

### Core Components

1. **OdooClient** (`src/odoo_lead_manager/client.py`)
   - **Purpose**: Robust Odoo RPC connection management
   - **Key Features**:
     - Connection pooling and authentication
     - CRUD operations wrapper
     - Context manager support
     - Environment variable configuration
   - **Model**: Singleton pattern for connection management

2. **LeadFilter** (`src/odoo_lead_manager/filters.py`)
   - **Purpose**: Fluent interface for complex lead filtering
   - **Key Features**:
     - Date range filtering (source_date, create_date, etc.)
     - Web source ID filtering
     - Status filtering (new, in_progress, won, lost, etc.)
     - User assignment filtering (user_id, closer_id, open_user_id)
     - Name-based user filtering
     - Method chaining for complex queries
   - **Pattern**: Builder pattern with fluent interface

3. **LeadManager** (`src/odoo_lead_manager/lead_manager.py`)
   - **Purpose**: High-level lead management operations
   - **Key Features**:
     - Lead retrieval with various criteria
     - Lead counting and analysis
     - Lead assignment updates (configurable model support)
     - Comprehensive lead summaries
     - DataFrame export
   - **Pattern**: Service layer pattern

4. **SmartDistributor** (`src/odoo_lead_manager/distribution.py`)
   - **Purpose**: Intelligent lead distribution algorithms
   - **Key Features**:
     - Proportional distribution based on expected percentages
     - Round-robin distribution
     - Least-loaded distribution
     - Weighted random distribution
     - Capacity-based distribution
     - User profile management
     - Distribution history tracking
   - **Pattern**: Strategy pattern for distribution algorithms

5. **CLI** (`src/odoo_lead_manager/cli.py`)
   - **Purpose**: Command-line interface for all operations
   - **Key Features**:
     - Interactive configuration management
     - Flexible lead selection (IDs, CSV, TSV, query filters)
     - Configurable model updates (crm.lead, res.partner, etc.)
     - User-friendly error handling and validation
     - Multiple output formats (table, CSV, JSON)
   - **Commands**: query, update, count, distribute, users, leads, check, configure, leadreport

## 🔍 Filtering Capabilities

### Date Range Filtering
```python
# Single date field
LeadFilter().by_date_range(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    field_name="source_date"
)

# Custom date field
LeadFilter().by_date_range(
    start_date=date(2024, 1, 1),
    field_name="create_date"
)
```

### Web Source ID Filtering
```python
# Single source
LeadFilter().by_web_source_ids("Website")

# Multiple sources
LeadFilter().by_web_source_ids(["Website", "Email Campaign", "Social Media"])
```

### Status Filtering
```python
# Using strings
LeadFilter().by_status(["new", "in_progress", "won"])

# Using enum
LeadFilter().by_status([LeadStatus.NEW, LeadStatus.WON])
```

### User Assignment Filtering
```python
# By IDs
LeadFilter().by_user_assignments(user_ids=[1, 2, 3])

# By names
LeadFilter().by_user_assignments(user_names=["Alice Smith", "Bob Johnson"])

# Mixed approach
LeadFilter().by_user_assignments(
    user_ids=[1, 2],
    closer_names=["Alice Smith"],
    open_user_ids=[3]
)
```

## 🧠 Smart Distribution Features

### Distribution Strategies
- **PROPORTIONAL**: Based on expected percentages
- **ROUND_ROBIN**: Equal rotation
- **LEAST_LOADED**: To users with fewest leads
- **WEIGHTED_RANDOM**: Random with percentage weights
- **CAPACITY_BASED**: Based on remaining capacity

### User Profile Management
```python
UserProfile(
    user_id=1,
    name="Alice Smith",
    current_leads=10,
    expected_percentage=40.0,
    max_capacity=50,
    priority=1,
    is_active=True
)
```

## 📊 Analytics & Reporting

### Lead Summary Structure
```python
summary = {
    "total_leads": 150,
    "leads": [...],  # List of lead dictionaries
    "statistics": {
        "total_leads": 150,
        "leads_with_email": 120,
        "leads_with_phone": 100,
        "assigned_leads": 130,
        "unassigned_leads": 20,
        "unique_emails": 110,
        "unique_phones": 95,
        "earliest_lead": "2024-01-01T00:00:00",
        "latest_lead": "2024-01-31T23:59:59"
    },
    "user_assignments": {
        "user_id": {"Alice Smith": 45, "Bob Johnson": 38},
        "closer_id": {...},
        "open_user_id": {...}
    },
    "source_distribution": {"Website": 60, "Email Campaign": 40, "Social": 50},
    "status_distribution": {"new": 50, "in_progress": 30, "won": 20},
    "date_range": {...},
    "geographic_distribution": {...}
}
```

## 🧪 Testing Framework

### Test Structure
- **Unit Tests**: All core components
- **Mocking**: Odoo API calls mocked for testing
- **Fixtures**: Reusable test data in `conftest.py`
- **Coverage**: 80%+ coverage target

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run specific tests
python run_tests.py --pattern "test_lead*"

# Using pytest directly
pytest tests/ -v --cov=src/odoo_lead_manager
```

### Test Categories
- `test_client.py`: OdooClient tests
- `test_filters.py`: LeadFilter tests
- `test_lead_manager.py`: LeadManager tests
- `test_distribution.py`: SmartDistributor tests

## 🚀 Usage Patterns

### Pattern 1: Basic Lead Retrieval
```python
from odoo_lead_manager import OdooClient, LeadManager

client = OdooClient()
lead_manager = LeadManager(client)

# Get all new leads from January 2024
leads = lead_manager.get_leads_by_date_range(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Pattern 2: Complex Filtering
```python
from odoo_lead_manager.filters import LeadFilter

filter_obj = LeadFilter() \
    .by_date_range("2024-01-01", "2024-01-31") \
    .by_status(["new", "in_progress"]) \
    .by_web_source_ids(["Website", "Email Campaign"]) \
    .by_user_assignments(user_names=["Alice Smith", "Bob Johnson"]) \
    .fields(["id", "name", "email", "status", "user_id"]) \
    .limit(100)

leads = lead_manager.get_leads(filter_obj)
```

### Pattern 3: Smart Distribution
```python
from odoo_lead_manager.distribution import SmartDistributor, UserProfile

distributor = SmartDistributor()

# Configure users
distributor.add_user_profile(UserProfile(
    user_id=1, name="Alice Smith", 
    current_leads=10, expected_percentage=40.0, max_capacity=50
))

# Load from Odoo
distributor.load_user_profiles_from_odoo(lead_manager)

# Distribute leads
leads = [...]  # List of Lead objects
assignments = distributor.distribute_leads(leads)
```

### Pattern 4: Complete Workflow
```python
# End-to-end workflow
with OdooClient() as client:
    lead_manager = LeadManager(client)
    distributor = SmartDistributor()
    
    # Load configuration
    distributor.load_user_profiles_from_odoo(lead_manager)
    distributor.load_proportions_from_odoo(lead_manager)
    
    # Fetch new leads
    new_leads = lead_manager.get_leads_by_status("new")
    
    # Convert to Lead objects
    lead_objects = [Lead(lead_id=l['id'], name=l['name']) for l in new_leads]
    
    # Distribute
    assignments = distributor.distribute_leads(lead_objects)
    
    # Apply assignments
    for user_id, lead_ids in assignments.items():
        lead_manager.update_lead_assignments(lead_ids, user_id=user_id, model="crm.lead")
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
ODOO_HOST=your-odoo-server.com
ODOO_PORT=8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional
ODOO_PROTOCOL=jsonrpc
ODOO_TIMEOUT=120
```

### CLI Usage Examples
```bash
# Lead retrieval and analysis
odlm leads --status new --limit 50                    # Get 50 new leads
odlm leads --format csv --output leads.csv           # Export all leads to CSV
odlm leads --date-filter last_7_days --format json   # Recent leads as JSON
odlm leads --user "Alice" --status won               # Alice's closed deals
odlm query --status in_progress --limit 100          # Query active leads

# Lead updates and management
odlm update --ids 123,456 --user-id 1 --closer-id 2  # Assign specific leads
odlm update --from-csv leads.csv --user-name "Alice" # Bulk update from CSV
odlm update --query '{"status":"new"}' --user-id 1  # Query-based updates

# Lead distribution
odlm distribute --leads 100 --strategy proportional  # Distribute 100 leads proportionally
odlm distribute --date-filter today --strategy least_loaded  # Distribute today's leads

# Lead reporting and analytics
odlm leadreport --date-filter yesterday               # Daily status report
odlm leadreport --user "Alice" --date-filter this_week # User performance report
odlm count --status new --date-filter this_month      # Monthly new lead count
odlm leads --group-by "user_id,status" --count        # Grouped statistics

# Advanced filtering
odlm leads --source "Facebook" --date-from 2024-01-01  # Facebook leads from date
odlm leads --exact-user "Alice Smith" --format table    # Exact user match
odlm leads --team "Inside Sales" --status new          # Team-specific new leads

# File-based operations
odlm update --from-file lead_ids.txt --status in_progress  # Update from ID list
odlm leads --fields "id,name,email,status" --output leads.csv  # Custom field export
odlm leads --web-source-file sources.txt --format json   # Multi-source filtering

# Connection and configuration
odlm check --verbose                                   # Test connection
odlm configure                                         # Interactive setup
odlm configure --file .env.production                  # Custom config file
```

### Dependencies
- `odoorpc>=0.8.0`: Odoo RPC client
- `python-dateutil>=2.8.0`: Date handling
- `pandas>=1.3.0`: Data analysis
- `numpy>=1.21.0`: Numerical operations
- `pydantic>=1.8.0`: Data validation
- `loguru>=0.6.0`: Logging
- `python-dotenv>=0.19.0`: Environment configuration

## 📁 File Structure

```
odo_lead_distribution/
├── src/odoo_lead_manager/          # Main package
│   ├── __init__.py                 # Package exports
│   ├── client.py                   # Odoo API client
│   ├── filters.py                  # Lead filtering
│   ├── lead_manager.py             # Lead management
│   ├── distribution.py             # Smart distribution
│   ├── cli.py                      # Command-line interface
│   └── add_leadreport.py           # Lead reporting module
├── tests/                          # Test suite
│   ├── conftest.py                 # Test fixtures
│   ├── test_*.py                   # Unit tests
├── examples/                       # Usage examples
├── setup.py                        # Package setup
├── requirements.txt               # Dependencies
├── pytest.ini                     # Test configuration
├── run_tests.py                   # Test runner
├── README.md                      # Documentation
└── CLAUDE.md                      # This file
```

## 🎯 Key Design Decisions

1. **Separation of Concerns**: Each module has a single responsibility
2. **Fluent Interface**: LeadFilter supports method chaining
3. **Strategy Pattern**: Multiple distribution algorithms
4. **Environment Configuration**: Support for .env files
5. **Mocking**: Full test coverage without live Odoo
6. **Data Classes**: Clean user and lead representations
7. **Context Managers**: Proper resource cleanup
8. **Type Hints**: Full type safety

## 🔄 Integration Points

### Odoo Models Used
- **crm.lead**: Primary lead model (default for CLI updates)
- **res.partner**: Customer/partner model (configurable via --model parameter)
- **res.users**: User management
- Custom proportions table: `lead_distribution_proportions`

### Non-Existent ID Validation Algorithm
When updating leads via CLI, the system validates provided IDs against the target model using:
1. **Comprehensive check**: Uses Odoo's native `search_read` with `("id", "in", lead_ids)` domain
2. **Complete scope**: Checks against **all** records in the specified model (e.g., crm.lead)
3. **Accurate reporting**: Compares provided IDs against found IDs to identify non-existent records
4. **Model-specific**: Validates against the model specified via `--model` parameter (defaults to crm.lead)

Example validation flow:
```python
# Checks entire crm.lead table for provided IDs
existing_leads = client.search_read(
    "crm.lead", 
    domain=[("id", "in", [123, 456, 789])], 
    fields=["id"]
)
# Reports which IDs don't exist in crm.lead model
```

### Extension Points
- Custom filtering criteria in LeadFilter
- New distribution strategies
- Additional analytics
- Custom Odoo models
- Integration with other Odoo modules

## 🚨 Common Issues & Solutions

### Connection Issues
- **Problem**: Cannot connect to Odoo
- **Solution**: Check host, port, credentials in .env file

### Non-existent Records
- **Problem**: "Lead IDs do not exist" error
- **Solution**: Use valid IDs from `odlm query` or `odlm leads` commands

### Import Issues
- **Problem**: Module not found
- **Solution**: Install in development mode: `pip install -e .`

### Test Failures
- **Problem**: Tests failing
- **Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`

### Performance Issues
- **Problem**: Slow lead retrieval
- **Solution**: Use specific fields and limits in filters

- **Version**: add v

This CLAUDE.md serves as a complete reference for understanding and working with the Odoo Lead Manager package.