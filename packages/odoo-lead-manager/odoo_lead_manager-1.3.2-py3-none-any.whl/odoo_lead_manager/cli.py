"""
Command Line Interface for Odoo Lead Manager.

Provides a comprehensive CLI for querying, filtering, and modifying leads
from Odoo's res.partner model with advanced features like:
- Date-based filtering (e.g., "older than 2 months")
- User-based filtering and assignment
- Status management
- CSV and table output
- Chained operations
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import json
from io import StringIO

from tabulate import tabulate
from loguru import logger

from .client import OdooClient
from .filters import LeadFilter, LeadStatus
from .lead_manager import LeadManager
from .distribution import SmartDistributor, UserProfile


class DateFilterHelper:
    """Helper class for parsing date filters in CLI."""
    
    @staticmethod
    def parse_date_filter(date_str: str) -> Dict[str, Any]:
        """
        Parse CLI date filters like 'older_than_2_months', 'last_30_days', etc.
        
        Args:
            date_str: Date filter string
            
        Returns:
            Dictionary with start_date and end_date
        """
        today = date.today()
        
        if date_str == "today":
            return {"start_date": today, "end_date": today}
        
        elif date_str == "yesterday":
            yesterday = today - timedelta(days=1)
            return {"start_date": yesterday, "end_date": yesterday}
        
        elif date_str.startswith("older_than_"):
            # Format: older_than_2_months, older_than_1_week, etc.
            parts = date_str.replace("older_than_", "").split("_")
            if len(parts) == 2:
                amount, unit = parts
                amount = int(amount)
                
                if unit == "days":
                    cutoff_date = today - timedelta(days=amount)
                    return {"end_date": cutoff_date}
                elif unit == "weeks":
                    cutoff_date = today - timedelta(weeks=amount)
                    return {"end_date": cutoff_date}
                elif unit == "months":
                    cutoff_date = today - timedelta(days=amount * 30)
                    return {"end_date": cutoff_date}
                elif unit == "years":
                    cutoff_date = today - timedelta(days=amount * 365)
                    return {"end_date": cutoff_date}
        
        elif date_str.startswith("last_"):
            # Format: last_30_days, last_2_months, etc.
            parts = date_str.replace("last_", "").split("_")
            if len(parts) == 2:
                amount, unit = parts
                amount = int(amount)
                
                if unit == "days":
                    start_date = today - timedelta(days=amount)
                    return {"start_date": start_date, "end_date": today}
                elif unit == "weeks":
                    start_date = today - timedelta(weeks=amount)
                    return {"start_date": start_date, "end_date": today}
                elif unit == "months":
                    start_date = today - timedelta(days=amount * 30)
                    return {"start_date": start_date, "end_date": today}
                elif unit == "years":
                    start_date = today - timedelta(days=amount * 365)
                    return {"start_date": start_date, "end_date": today}
        
        elif date_str.startswith("this_"):
            # Format: this_month, this_week, this_year
            unit = date_str.replace("this_", "")
            
            if unit == "week":
                start_date = today - timedelta(days=today.weekday())
                return {"start_date": start_date, "end_date": today}
            elif unit == "month":
                start_date = date(today.year, today.month, 1)
                return {"start_date": start_date, "end_date": today}
            elif unit == "year":
                start_date = date(today.year, 1, 1)
                return {"start_date": start_date, "end_date": today}
        
        # Try parsing as exact date
        try:
            exact_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return {"start_date": exact_date, "end_date": exact_date}
        except ValueError:
            pass
        
        return {}


class CLI:
    """Main CLI class for Odoo Lead Manager."""
    
    def __init__(self):
        """Initialize CLI."""
        self.client = None
        self.lead_manager = None
    
    def setup_client(self) -> bool:
        """Set up Odoo client."""
        try:
            self.client = OdooClient()
            self.lead_manager = LeadManager(self.client)
            return True
        except Exception as e:
            print(f"Error setting up client: {e}")
            return False
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="""Odoo Lead Manager CLI - Comprehensive lead management for Odoo

EXAMPLES:
  # Basic usage:
  odlm check                                    # Test connection to Odoo
  odlm configure                                # Interactive setup of credentials

  # Querying leads:
  odlm leads --format table                     # Show all leads in table format
  odlm leads --status "new" --limit 50          # Show 50 new leads
  odlm leads --date-from 2024-01-01 --date-to 2024-01-31  # Leads from January
  odlm leads --user "Alice Smith"               # Leads assigned to Alice
  odlm leads --web-source-ids "facebook,google"  # Leads from specific sources
  odlm leads --group-by "user_id,status"        # Group leads by user and status
  odlm leads --pivot-rows "user_id" --pivot-cols "status"  # Pivot table

  # Counting leads:
  odlm count --status "won"                     # Count won leads
  odlm count --date-filter "last_30_days"       # Count leads from last 30 days
  odlm count --exclude-users                    # Count leads excluding default users

  # Updating leads:
  odlm update --ids "1,2,3" --user-id 5         # Assign leads 1,2,3 to user 5
  odlm update --from-file leads.txt --user-name "Bob"  # Update leads from file
  odlm update --status "in_progress" --closer-id 7     # Update status and closer

  # Distributing leads:
  odlm distribute --strategy proportional       # Distribute using proportions
  odlm distribute --strategy round_robin --dry-run  # Show plan without applying

  # Daily distribution:
  odlm dailydist --config config.yaml          # Run daily distribution
  odlm dailydist --config config.yaml --dry-run # Show comprehensive analysis without changes
  odlm dailydist --config config.yaml --step-mode # Interactive step-by-step mode
  odlm dailydist --generate-config --output config.yaml # Generate config file

  # User management:
  odlm users --list                             # List all users
  odlm users --counts                           # Show lead counts per user

DATE FILTERS:
  --date-filter "today"
  --date-filter "yesterday"
  --date-filter "last_7_days"
  --date-filter "last_30_days"
  --date-filter "older_than_2_months"
  --date-filter "this_month"
  --date-filter "2024-01-01"

WEB SOURCE ID FORMAT:
  Use source names (strings) like: facebook_form, google_ads, website, etc.
  NOT numeric IDs.

ENVIRONMENT:
  Set credentials in .env file or run 'odlm configure'
  Required: ODOO_HOST, ODOO_PORT, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Query command
        query_parser = subparsers.add_parser("query", help="Query leads with filters", description="Query leads with advanced filtering")
        self._add_query_args(query_parser)
        
        # Count command
        count_parser = subparsers.add_parser("count", help="Count leads", description="Count leads matching criteria")
        self._add_query_args(count_parser, for_count=True)
        
        # Update command
        update_parser = subparsers.add_parser("update", help="Update leads", description="Update lead assignments and status")
        self._add_update_args(update_parser)
        
        # Distribute command
        distribute_parser = subparsers.add_parser("distribute", help="Distribute leads", description="Distribute leads among users using various strategies")
        self._add_distribute_args(distribute_parser)
        
        # User management commands
        user_parser = subparsers.add_parser("users", help="User management", description="List users and show lead assignment statistics")
        self._add_user_args(user_parser)
        
        # Leads command - uses your exact CSV fields and crm.lead model
        leads_parser = subparsers.add_parser("leads", help="Get all leads using CRM lead structure", description="Get leads with advanced filtering, grouping, and pivot capabilities")
        self._add_leads_args(leads_parser)
        
        # Invoices command - for querying invoice data
        invoices_parser = subparsers.add_parser("invoices", help="Query invoice data from account.invoice model", description="Get invoices with filtering and export capabilities")
        self._add_invoices_args(invoices_parser)
        
        # Join command - for joining leads with invoice data
        join_parser = subparsers.add_parser("join", help="Join leads with invoice data", description="Match leads to their invoice data based on partner relationships")
        self._add_join_args(join_parser)
        
        # Lead Report command - for generating daily lead status reports
        leadreport_parser = subparsers.add_parser("leadreport", help="Generate lead status reports by user", description="Generate daily lead status reports grouped by user with status counts")
        self._add_leadreport_args(leadreport_parser)
        
        # Daily Distribution command - for automated daily lead distribution
        dailydist_parser = subparsers.add_parser("dailydist", help="Daily lead distribution (leads only)", description="Automated daily lead distribution based on configuration. Only processes leads (type='lead'), not opportunities.")
        self._add_dailydist_args(dailydist_parser)
        
        # Check command - for testing connection
        check_parser = subparsers.add_parser("check", help="Test connection to Odoo", description="Verify connection to Odoo server and credentials")
        
        # Configure command - for interactive setup
        configure_parser = subparsers.add_parser("configure", help="Interactive configuration", description="Set up Odoo connection credentials interactively")
        
        return parser
    
    def _add_leads_args(self, parser: argparse.ArgumentParser):
        """Add leads command arguments using CSV field structure."""
        parser.add_argument("--fields", help="Fields to display (comma-separated)")
        parser.add_argument("--limit", type=int, default=1000, help="Limit number of results")
        parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        
        # Lead-specific filters
        parser.add_argument("--status", help="Filter by lead status (new, in_progress, won, lost, etc.)")
        parser.add_argument("--type", choices=["lead", "opportunity"], help="Filter by lead type (lead or opportunity)")
        parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
        parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
        parser.add_argument("--user", help="Filter by assigned user name (partial match, default)")
        parser.add_argument("--exact-user", help="Filter by assigned user name (exact match)")
        parser.add_argument("--exact", help="Filter by exact open_user_id name (exact match)")
        parser.add_argument("--team", help="Filter by sales team name (partial match)")
        parser.add_argument("--source", help="Filter by source name (text search, partial match)")
        parser.add_argument("--campaign", help="Filter by campaign name (partial match)")
        parser.add_argument("--count", action="store_true", help="Count results only")
        
        # Web source ID filtering (mutually exclusive)
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--web-source-ids", 
            help="Comma-separated web source names (e.g., 'facebook_form,google_ads,website')"
        )
        source_group.add_argument(
            "--web-source-file", 
            help="File with web source names (one per line, e.g., facebook_form, google_ads)"
        )
        
        # Grouping and pivoting
        parser.add_argument("--group-by", help="Group by columns (comma-separated, e.g., 'user_id,status')")
        parser.add_argument("--pivot-rows", help="Pivot table row columns (comma-separated)")
        parser.add_argument("--pivot-cols", help="Pivot table column columns (comma-separated)")
        
        # User exclusion filters
        parser.add_argument("--exclude-users", action="store_true", help="Enable user exclusion filter")
        parser.add_argument("--excluded-users", default="Administrator,Patrick Adler", 
                           help="Comma-separated list of users to exclude (default: 'Administrator,Patrick Adler')")
        
        # Add epilog with comprehensive examples
        parser.epilog = """COMPREHENSIVE EXAMPLES:

BASIC LEAD RETRIEVAL:
  odlm leads --format table                     # Show all leads in table format
  odlm leads --limit 100                        # Show first 100 leads
  odlm leads --fields "id,name,email,status"    # Custom field selection
  odlm leads --format csv --output leads.csv    # Export to CSV

FILTERING BY STATUS:
  odlm leads --status "new"                     # Only new leads
  odlm leads --status "won,lost"                # Won or lost leads
  odlm leads --status "in_progress" --limit 50  # 50 in-progress leads

DATE-BASED FILTERING:
  odlm leads --date-from 2024-01-01 --date-to 2024-01-31  # January 2024 leads
  odlm leads --date-filter "last_7_days"        # Last 7 days
  odlm leads --date-filter "this_month"         # Current month

USER-BASED FILTERING:
  odlm leads --user "Alice"                     # Leads assigned to Alice (partial match)
  odlm leads --exact-user "Alice Smith"         # Exact name match
  odlm leads --team "Inside Sales"              # Leads in Inside Sales team

SOURCE FILTERING:
  odlm leads --source "Facebook"                # Facebook leads
  odlm leads --web-source-ids "facebook,google" # Multiple sources
  odlm leads --web-source-file sources.txt      # Sources from file

ADVANCED USAGE:
  odlm leads --status "new" --date-filter "last_30_days" --format json  # New leads last 30 days as JSON
  odlm leads --group-by "user_id,status"        # Group by user and status
  odlm leads --pivot-rows "user_id" --pivot-cols "status"  # Pivot table

USER EXCLUSION:
  odlm leads --exclude-users                    # Exclude default users (Administrator,Patrick Adler)
  odlm leads --exclude-users --excluded-users "Admin,Bob,Carol"  # Exclude custom user list
  odlm leads --status "new" --exclude-users     # New leads excluding default users

PERFORMANCE TIPS:
  • For large datasets, specify essential fields only: --fields "id,name,status,user_id"
  • Use --limit to control dataset size (e.g., --limit 5000)
  • Apply specific filters to reduce data: --date-filter, --status, --user

QUICK TIPS:
  • Use --count to get quick statistics
  • Use --output to save results to file
  • Use --limit to prevent overwhelming results
  • Partial matching works for user, team, source, and campaign names
  • Use --exclude-users to filter out system/admin users from results"""
    
    def _add_query_args(self, parser: argparse.ArgumentParser, for_count: bool = False):
        """Add query command arguments."""
        if not for_count:
            parser.add_argument("--fields", help="Fields to display (comma-separated)")
        parser.add_argument("--limit", type=int, default=1000, help="Limit number of results")
        parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        
        # Date filters
        parser.add_argument("--date-filter", help="Date filter (today, yesterday, last_7_days, etc.)")
        parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
        parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
        parser.add_argument("--date-field", default="create_date", help="Date field to filter on")
        
        # Status filters
        parser.add_argument("--status", help="Filter by lead status (e.g., new, in_progress, won, lost)")
        
        # User filters
        parser.add_argument("--user", help="Filter by assigned user name (partial match)")
        parser.add_argument("--exact-user", help="Filter by assigned user name (exact match)")
        parser.add_argument("--closer", help="Filter by closer name (comma-separated)")
        parser.add_argument("--open-user", help="Filter by open user name (comma-separated)")
        
        # Text filters
        parser.add_argument("--name", help="Filter by customer name (partial match)")
        parser.add_argument("--email", help="Filter by email address")
        parser.add_argument("--phone", help="Filter by phone number")
        parser.add_argument("--source", help="Filter by web source IDs (comma-separated)")
        parser.add_argument("--tags", help="Filter by tags (comma-separated)")
        
        # Pagination
        parser.add_argument("--offset", type=int, help="Skip first N results")
        parser.add_argument("--order", help="Order results (e.g., 'create_date desc')")
        
        # User exclusion filters
        parser.add_argument("--exclude-users", action="store_true", help="Enable user exclusion filter")
        parser.add_argument("--excluded-users", default="Administrator,Patrick Adler", 
                           help="Comma-separated list of users to exclude (default: 'Administrator,Patrick Adler')")
    
    def _add_update_args(self, parser: argparse.ArgumentParser):
        """Add update command arguments."""
        parser.add_argument("--ids", help="Comma-separated lead IDs to update")
        parser.add_argument("--from-file", help="File with lead IDs (one per line)")
        parser.add_argument("--from-csv", help="CSV file with 'id' column")
        parser.add_argument("--from-tsv", help="TSV file with 'id' column")
        parser.add_argument("--model", default="crm.lead", help="Model to update (default: crm.lead)")
        
        # Assignment options
        parser.add_argument("--user-id", type=int, help="Assign to user by ID")
        parser.add_argument("--user-name", help="Assign to user by name")
        parser.add_argument("--closer-id", type=int, help="Set closer by ID")
        parser.add_argument("--closer-name", help="Set closer by name")
        parser.add_argument("--open-user-id", type=int, help="Set open user by ID")
        parser.add_argument("--open-user-name", help="Set open user by name")
        parser.add_argument("--status", help="Update lead status")
        
        parser.epilog = """UPDATE EXAMPLES:

SINGLE LEAD UPDATE:
  odlm update --ids 123 --user-id 5                    # Assign lead 123 to user 5
  odlm update --ids 456 --status "in_progress"         # Update status to in_progress
  odlm update --ids 789 --closer-name "Alice"          # Set closer to Alice

MULTIPLE LEAD UPDATES:
  odlm update --ids 1,2,3 --user-id 5                  # Assign multiple leads
  odlm update --from-file leads.txt --user-name "Bob"  # Update from file
  odlm update --from-csv leads.csv --status "won"      # Update from CSV

USER ASSIGNMENT OPTIONS:
  --user-id 5              # Assign to user with ID 5
  --user-name "Alice"      # Assign to user named "Alice"
  --closer-id 3            # Set closer to user with ID 3
  --closer-name "Bob"      # Set closer to user named "Bob"
  --open-user-id 7         # Set open user to user with ID 7
  --open-user-name "Carol" # Set open user to user named "Carol"

STATUS UPDATES:
  --status new             # Set to new
  --status in_progress     # Set to in_progress
  --status won             # Set to won
  --status lost            # Set to lost

MODEL OVERRIDE:
  --model res.partner      # Update res.partner instead of crm.lead"""
    
    def _add_distribute_args(self, parser: argparse.ArgumentParser):
        """Add distribute command arguments."""
        parser.add_argument("--status", help="Filter leads by status (e.g., new)")
        parser.add_argument("--strategy", choices=["proportional", "round_robin", "least_loaded", "weighted_random", "capacity_based"], help="Distribution strategy")
        parser.add_argument("--dry-run", action="store_true", help="Show distribution plan without applying")
        parser.add_argument("--limit", type=int, help="Limit number of leads to distribute")
    
    def _add_user_args(self, parser: argparse.ArgumentParser):
        """Add user management arguments."""
        parser.add_argument("--list", action="store_true", help="List all users")
        parser.add_argument("--counts", action="store_true", help="Show lead counts per user")
    
    def _add_invoices_args(self, parser: argparse.ArgumentParser):
        """Add invoices command arguments."""
        parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        parser.add_argument("--limit", type=int, default=100, help="Limit number of results")
        
        # Date filters
        parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
        parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
        
        # Invoice filters
        parser.add_argument("--state", choices=["draft", "open", "paid", "cancel"], help="Filter by invoice state")
        parser.add_argument("--type", choices=["out_invoice", "in_invoice", "out_refund", "in_refund"], help="Filter by invoice type")
        parser.add_argument("--partner", help="Filter by partner name (partial match)")
        parser.add_argument("--min-amount", type=float, help="Minimum invoice amount")
        parser.add_argument("--max-amount", type=float, help="Maximum invoice amount")
    
    def _add_join_args(self, parser: argparse.ArgumentParser):
        """Add lead-invoice join arguments."""
        parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        parser.add_argument("--limit", type=int, default=100, help="Limit number of results")
        
        # Lead filters
        parser.add_argument("--lead-date-from", help="Start date for leads (YYYY-MM-DD)")
        parser.add_argument("--lead-date-to", help="End date for leads (YYYY-MM-DD)")
        parser.add_argument("--lead-status", help="Filter leads by status")
        parser.add_argument("--lead-user", help="Filter leads by assigned user")
        parser.add_argument("--lead-source", help="Filter leads by source")
        
        # Invoice filters
        parser.add_argument("--invoice-date-from", help="Start date for invoices (YYYY-MM-DD)")
        parser.add_argument("--invoice-date-to", help="End date for invoices (YYYY-MM-DD)")
        parser.add_argument("--invoice-state", choices=["draft", "open", "paid", "cancel"], help="Filter invoices by state")
        
        # Join options
        parser.add_argument("--exclude-unmatched", action="store_true", help="Exclude leads without invoices")
        parser.add_argument("--include-all", action="store_true", default=True, help="Include leads without invoices (default)")
        parser.add_argument("--fields", help="Fields to display (comma-separated)")
        
        parser.epilog = """LEAD-INVOICE JOIN EXAMPLES:

SALES PERFORMANCE ANALYSIS:
  odlm join --lead-date-from 2024-01-01 --lead-date-to 2024-01-31  # January leads with invoices
  odlm join --lead-status "won" --invoice-state paid               # Won leads with paid invoices
  odlm join --lead-user "Alice" --format csv --output alice_sales.csv  # Alice's sales data

REVENUE ANALYSIS:
  odlm join --lead-date-from 2024-01-01 --exclude-unmatched        # Only converted leads
  odlm join --lead-source "Facebook" --invoice-state paid          # Facebook ROI analysis
  odlm join --invoice-date-from 2024-01-01 --limit 50              # Recent invoice matches

CONVERSION ANALYSIS:
  odlm join --lead-date-from 2024-01-01 --format json              # Full conversion data
  odlm join --lead-status "new" --exclude-unmatched --count        # New leads converted
  odlm join --lead-user "Bob" --invoice-date-from 2024-01-01       # Bob's conversion rates
"""

    def _add_leadreport_args(self, parser: argparse.ArgumentParser):
        """Add lead report command arguments."""
        parser.add_argument("--format", choices=["table", "csv"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        parser.add_argument("--date-field", default="create_date", help="Date field to filter on (default: create_date)")
        parser.add_argument("--limit", type=int, help="Limit number of results (default: no limit)")
        parser.add_argument("--no-limit", action="store_true", help="Remove any result limits")
        
        # Sorting options
        parser.add_argument("--sort", choices=["asc", "desc"], default="asc", help="Sort order (default: asc)")
        parser.add_argument("--sort-col", choices=["user", "total", "new", "call_back", "dont_call", "sale_made", "fpfu", "utr", "other"], 
                           default="user", help="Column to sort by (default: user)")
        
        # Standard filtering options
        parser.add_argument("--status", help="Filter by lead status (comma-separated)")
        parser.add_argument("--source", help="Filter by web source IDs (comma-separated)")
        parser.add_argument("--user", help="Filter by assigned user name (partial match)")
        parser.add_argument("--exact-user", help="Filter by assigned user name (exact match)")
        parser.add_argument("--closer", help="Filter by closer name (comma-separated)")
        parser.add_argument("--open-user", help="Filter by open user name (comma-separated)")
        
        # Date filtering options
        parser.add_argument("--date-filter", help="Date filter (today, yesterday, last_7_days, last_30_days, older_than_2_months)")
        parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
        parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
        
        # User exclusion filters
        parser.add_argument("--exclude-users", action="store_true", help="Enable user exclusion filter")
        parser.add_argument("--excluded-users", default="Administrator,Patrick Adler", 
                           help="Comma-separated list of users to exclude (default: 'Administrator,Patrick Adler')")
        
        parser.epilog = """LEAD REPORT EXAMPLES:

DAILY STATUS REPORT:
  odlm leadreport --date-from 2024-01-01 --date-to 2024-01-31  # January report
  odlm leadreport --date-filter "today"                      # Today's report
  odlm leadreport --user "Alice" --date-filter "last_7_days"  # Alice's weekly report

SORTING AND ORDERING:
  odlm leadreport --sort-col total --sort desc               # Sort by total leads (descending)
  odlm leadreport --sort-col won --sort asc                  # Sort by won leads (ascending)
  odlm leadreport --sort-col new --sort desc --format csv    # Sort by new leads (descending)
  odlm leadreport --sort-col user --sort asc                 # Sort by user name (ascending, default)

CAMPAIGN ANALYSIS:
  odlm leadreport --source "facebook,google" --date-from 2024-01-01  # Campaign comparison
  odlm leadreport --status "new,in_progress,won" --format csv --output status_report.csv

TEAM PERFORMANCE:
  odlm leadreport --date-filter "this_month" --format table  # Current month team report
  odlm leadreport --user "Sales Team" --date-from 2024-01-01  # Team performance

USER EXCLUSION:
  odlm leadreport --exclude-users                # Exclude default users (Administrator,Patrick Adler)
  odlm leadreport --exclude-users --excluded-users "Admin,System"  # Exclude custom users
  odlm leadreport --date-filter "last_7_days" --exclude-users      # Weekly report excluding system users

PERFORMANCE NOTES:
  • Default limit: 10,000 records (use --limit or --no-limit to override)
  • Large datasets are automatically optimized with minimal field selection
  • Use specific date filters to reduce data size for better performance

SORTING COLUMNS:
  --sort-col user        # Sort by user name
  --sort-col total       # Sort by total lead count
  --sort-col new         # Sort by new leads count
  --sort-col call_back   # Sort by call back leads count
  --sort-col dont_call   # Sort by dont call leads count
  --sort-col sale_made   # Sort by sale made leads count
  --sort-col fpfu        # Sort by FPFU (Follow-up) leads count
  --sort-col utr         # Sort by UTR leads count
  --sort-col other       # Sort by other status leads count

NOTE: Status columns reflect the actual status values in your Odoo system:
  • New, Call Back, Dont Call, Sale Made, FPFU, UTR, Other
  • Legacy options (won, lost, in_progress, do_not_call) are supported for compatibility
"""

    def _add_dailydist_args(self, parser: argparse.ArgumentParser):
        """Add daily distribution command arguments."""
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--dry-run", action="store_true", help="Show comprehensive analysis and distribution plan without making changes")
        parser.add_argument("--override-date-range", help="Override date range (start,end)")
        parser.add_argument("--force-round-robin", action="store_true", help="Force round robin distribution")
        parser.add_argument("--max-leads", type=int, help="Maximum leads to distribute")
        parser.add_argument("--generate-report", action="store_true", help="Generate distribution report")
        parser.add_argument("--report-format", choices=["csv", "json", "html"], default="csv")
        parser.add_argument("--report-location", help="Report output directory")
        parser.add_argument("--email-notification", action="store_true", help="Send email notification")
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
        
        # Lead export options
        parser.add_argument("--export-leads", action="store_true", help="Export final distributable leads to CSV file")
        parser.add_argument("--leads-output", help="CSV file path for distributable leads export (default: distributable_leads.csv)")
        parser.add_argument("--leads-fields", help="Comma-separated list of fields to export (default: id,name,email,phone,status,web_source_id,partner_id)")
        
        # Lead filtering analysis options
        parser.add_argument("--export-all-stages", action="store_true", help="Export leads at all filtering stages (before and after each filter)")
        parser.add_argument("--export-before-filter", action="store_true", help="Export leads before any filtering (raw date range results)")
        parser.add_argument("--export-after-filter", action="store_true", help="Export leads after all filtering (same as --export-leads)")
        parser.add_argument("--stages-output-dir", help="Directory for stage export files (default: lead_stages/)")
        parser.add_argument("--show-filter-delta", action="store_true", help="Show detailed delta analysis between filtering stages")
        
        # Interactive step-through mode
        parser.add_argument("--step-mode", action="store_true", help="Interactive step-through mode for testing")
        parser.add_argument("--auto-accept", action="store_true", help="Auto-accept all steps in step mode")
        
        # Config generation arguments
        parser.add_argument("--generate-config", action="store_true", help="Generate boilerplate config file")
        parser.add_argument("--output", help="Output file path for generated config")
        parser.add_argument("--campaign", help="Campaign name for config generation")
        parser.add_argument("--template", choices=["basic", "advanced", "minimal"], default="basic", help="Config template type")
        
        parser.epilog = """DAILY DISTRIBUTION EXAMPLES:

BASIC USAGE:
  odlm dailydist --config daily_lead_distribution_config.yaml
  odlm dailydist --config config.yaml --dry-run

OVERRIDE SETTINGS:
  odlm dailydist --config config.yaml --max-leads 100
  odlm dailydist --config config.yaml --override-date-range "2024-01-01,2024-06-30"

REPORTING:
  odlm dailydist --config config.yaml --generate-report --report-format html
  odlm dailydist --config config.yaml --generate-report --report-location reports/

LEAD EXPORT:
  odlm dailydist --config config.yaml --dry-run --export-leads
  odlm dailydist --config config.yaml --export-leads --leads-output my_leads.csv
  odlm dailydist --config config.yaml --export-leads --leads-fields "id,name,email,phone,status"

FILTERING ANALYSIS:
  odlm dailydist --config config.yaml --dry-run --export-before-filter    # Export raw leads before filtering
  odlm dailydist --config config.yaml --dry-run --export-after-filter     # Export final leads after filtering
  odlm dailydist --config config.yaml --dry-run --export-all-stages       # Export at all filtering stages
  odlm dailydist --config config.yaml --dry-run --show-filter-delta       # Show detailed filter analysis
  odlm dailydist --config config.yaml --dry-run --export-all-stages --stages-output-dir analysis/

STEP-THROUGH MODE:
  odlm dailydist --config config.yaml --step-mode                    # Interactive step-by-step
  odlm dailydist --config config.yaml --step-mode --auto-accept      # Auto-accept all steps
  odlm dailydist --config config.yaml --step-mode --dry-run          # Step-through with dry run

CONFIG GENERATION:
  odlm dailydist --generate-config --output daily_distribution_config.yaml
  odlm dailydist --generate-config --campaign Voice --template advanced --output voice_config.yaml
  odlm dailydist --generate-config --template minimal --output minimal_config.yaml

NOTE: Daily distribution only processes leads (type='lead'), not opportunities (type='opportunity').
This ensures proper lead distribution workflow and prevents confusion between new leads and existing opportunities.
"""

    def build_filter_from_args(self, args) -> LeadFilter:
        """Build LeadFilter from command line arguments."""
        filter_obj = LeadFilter()
        
        # Status filter
        if getattr(args, 'status', None):
            filter_obj.by_status(args.status.split(','))
        
        # Source filter
        if getattr(args, 'source', None):
            filter_obj.by_web_source_ids(args.source.split(','))
        
        # User filters
        if getattr(args, 'exact_user', None):
            filter_obj.by_user_assignments(user_names=[args.exact_user], exact=True)
        elif getattr(args, 'user', None):
            filter_obj.by_user_assignments(user_names=[args.user], exact=False)
        if getattr(args, 'closer', None):
            filter_obj.by_user_assignments(closer_names=args.closer.split(','))
        if getattr(args, 'open_user', None):
            filter_obj.by_user_assignments(open_user_names=args.open_user.split(','))
        
        # Text filters
        if getattr(args, 'name', None):
            filter_obj.by_customer_name(args.name)
        if getattr(args, 'email', None):
            filter_obj.by_email(args.email)
        if getattr(args, 'phone', None):
            filter_obj.by_phone(args.phone)
        if getattr(args, 'tags', None):
            filter_obj.by_tags(args.tags.split(','))
        
        # Date filters - use source_date for consistency with CSV output
        if getattr(args, 'date_filter', None):
            date_params = DateFilterHelper.parse_date_filter(args.date_filter)
            filter_obj.by_date_range(
                start_date=date_params.get("start_date"),
                end_date=date_params.get("end_date"),
                field_name=getattr(args, 'date_field', 'source_date')
            )
        elif getattr(args, 'date_from', None) or getattr(args, 'date_to', None):
            filter_obj.by_date_range(
                start_date=getattr(args, 'date_from', None),
                end_date=getattr(args, 'date_to', None),
                field_name=getattr(args, 'date_field', 'source_date')
            )
        
        # Pagination
        if hasattr(args, 'limit') and args.limit:
            filter_obj.limit(args.limit)
        if hasattr(args, 'offset') and args.offset:
            filter_obj.offset(args.offset)
        if hasattr(args, 'order') and args.order:
            filter_obj.order(args.order)
        
        # User exclusion filters
        if getattr(args, 'exclude_users', None):
            excluded_users = getattr(args, 'excluded_users', "Administrator,Patrick Adler")
            if excluded_users:
                user_list = [user.strip() for user in excluded_users.split(',') if user.strip()]
                filter_obj.exclude_users(user_list, exact=True)
        
        return filter_obj

    def handle_leadreport(self, args) -> int:
        """Handle leadreport command."""
        if not self.setup_client():
            return 1
        
        try:
            # Build filter from arguments and set model to crm.lead
            filter_obj = self.build_filter_from_args(args)
            filter_obj.model("crm.lead")
            
            # Set default type to "lead" for leadreport
            filter_obj.by_type("lead")
            
            # Set reasonable limits to prevent memory issues with large datasets
            if args.no_limit:
                # Don't apply any limit - but warn user about potential issues
                print("Warning: No limit specified. Large datasets may cause memory or parsing issues.")
            elif args.limit:
                # Use explicit limit
                filter_obj.limit(args.limit)
            else:
                # Apply a reasonable default limit for leadreport to prevent issues
                default_limit = 10000
                filter_obj.limit(default_limit)
                print(f"Info: Applied default limit of {default_limit} records. Use --limit or --no-limit to override.")
            
            # Get leads with minimal fields needed for report generation
            # Only fetch essential fields to handle large datasets efficiently
            fields = ["id", "status", "user_id", getattr(args, 'date_field', 'create_date')]
            
            try:
                leads = self.lead_manager.get_leads(filter_obj, fields=fields)
            except Exception as e:
                error_msg = str(e)
                if "unclosed token" in error_msg or "parsing" in error_msg.lower():
                    print("Error: Dataset too large to process. Try one of these solutions:")
                    print("  1. Add a smaller --limit (e.g., --limit 5000)")
                    print("  2. Use more specific date filters (e.g., --date-filter last_7_days)")
                    print("  3. Filter by specific users or status")
                    print(f"  Original error: {error_msg}")
                    return 1
                else:
                    # Re-raise other errors
                    raise
            
            if not leads:
                print("No leads found for the specified criteria.")
                return 0
            
            # Group leads by user and count by status
            user_reports = {}
            
            for lead in leads:
                # Get user name from user_id field (which is [id, name] format)
                user_info = lead.get('user_id', [None, 'Unassigned'])
                if user_info is False or user_info is None:
                    user_name = 'Unassigned'
                elif isinstance(user_info, list) and len(user_info) >= 2:
                    user_name = user_info[1]
                else:
                    user_name = str(user_info)
                
                # Initialize user report if not exists
                if user_name not in user_reports:
                    user_reports[user_name] = {
                        'user_name': user_name,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'total_leads': 0,
                        'status_counts': {}
                    }
                
                # Count by status
                status = lead.get('status', 'Unknown')
                user_reports[user_name]['status_counts'][status] = user_reports[user_name]['status_counts'].get(status, 0) + 1
                user_reports[user_name]['total_leads'] += 1
            
            # Convert to list and sort based on arguments
            def get_sort_value(report):
                col_mapping = {
                    'user': 'user_name',
                    'total': 'total_leads',
                    'new': lambda x: x['status_counts'].get('new', 0),
                    'call_back': lambda x: x['status_counts'].get('call_back', 0),
                    'dont_call': lambda x: x['status_counts'].get('dont_call', 0),
                    'sale_made': lambda x: x['status_counts'].get('sale_made', 0),
                    'fpfu': lambda x: x['status_counts'].get('fpfu', 0),
                    'utr': lambda x: x['status_counts'].get('utr', 0),
                    'other': lambda x: sum(count for status, count in x['status_counts'].items() 
                                         if status not in ['new', 'call_back', 'dont_call', 'sale_made', 'fpfu', 'utr']),
                    # Legacy support for old status names
                    'in_progress': lambda x: x['status_counts'].get('in_progress', 0),
                    'won': lambda x: x['status_counts'].get('won', 0) + x['status_counts'].get('sale_made', 0),
                    'lost': lambda x: x['status_counts'].get('lost', 0),
                    'do_not_call': lambda x: x['status_counts'].get('do_not_call', 0) + x['status_counts'].get('dont_call', 0)
                }
                
                sort_key = col_mapping.get(args.sort_col, 'user_name')
                if callable(sort_key):
                    return sort_key(report)
                else:
                    return report[sort_key]
            
            reverse_order = args.sort == 'desc'
            report_data = sorted(user_reports.values(), key=get_sort_value, reverse=reverse_order)
            
            # Prepare output with actual status values found in the system
            headers = ['Date', 'User', 'Total', 'New', 'Call Back', 'Dont Call', 'Sale Made', 'FPFU', 'UTR', 'Other']
            rows = []
            
            for report in report_data:
                # Calculate "Other" for any status not explicitly handled
                all_status_counts = report['status_counts']
                handled_statuses = ['new', 'call_back', 'dont_call', 'sale_made', 'fpfu', 'utr']
                other_count = sum(count for status, count in all_status_counts.items() 
                                if status not in handled_statuses)
                
                row = [
                    report['date'],
                    report['user_name'],
                    report['total_leads'],
                    report['status_counts'].get('new', 0),
                    report['status_counts'].get('call_back', 0),
                    report['status_counts'].get('dont_call', 0),
                    report['status_counts'].get('sale_made', 0),
                    report['status_counts'].get('fpfu', 0),
                    report['status_counts'].get('utr', 0),
                    other_count
                ]
                rows.append(row)
            
            # Format output
            if args.format == "csv":
                output = "Date,User,Total,New,Call Back,Dont Call,Sale Made,FPFU,UTR,Other\n"
                for row in rows:
                    output += ",".join(map(str, row)) + "\n"
            else:  # table
                output = tabulate(rows, headers=headers, tablefmt="grid")
            
            # Output to file or stdout
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Lead report written to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"Error generating lead report: {e}")
            return 1

    def handle_query(self, args) -> int:
        """Handle query command."""
        if not self.setup_client():
            return 1
        
        filter_obj = self.build_filter_from_args(args)
        filter_obj.model("crm.lead")
        
        # Build fields list
        fields = None
        if args.fields:
            fields = args.fields.split(',')
        
        # Get leads
        leads = self.lead_manager.get_leads(filter_obj, fields=fields)
        
        if not leads:
            print("No leads found.")
            return 0
        
        # Format output
        if args.format == "csv":
            output = self.format_csv(leads, fields)
        elif args.format == "json":
            output = json.dumps(leads, indent=2, default=str)
        else:  # table
            output = self.format_table(leads, fields)
        
        # Output to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
        
        return 0

    def handle_count(self, args) -> int:
        """Handle count command."""
        if not self.setup_client():
            return 1
        
        filter_obj = self.build_filter_from_args(args)
        filter_obj.model("crm.lead")
        
        try:
            count = self.lead_manager.count_leads(filter_obj)
            print(f"Total leads: {count}")
            return 0
        except Exception as e:
            error_msg = str(e)
            if "unclosed token" in error_msg or "parsing" in error_msg.lower():
                print("Error: Query too complex to process. Try using more specific filters:")
                print("  1. Use more specific date filters (e.g., --date-filter last_7_days)")
                print("  2. Filter by specific users, status, or sources")
                print(f"  Original error: {error_msg}")
                return 1
            else:
                print(f"Error counting leads: {e}")
                return 1

    def handle_update(self, args) -> int:
        """Handle update command."""
        if not self.setup_client():
            return 1
        
        try:
            # Resolve lead IDs
            lead_ids = []
            if args.ids:
                lead_ids = [int(x.strip()) for x in args.ids.split(',')]
            elif args.from_file:
                with open(args.from_file, 'r') as f:
                    if args.from_file.endswith('.csv'):
                        reader = csv.DictReader(f)
                        lead_ids = [int(row['id']) for row in reader if row.get('id')]
                    else:
                        lead_ids = [int(line.strip()) for line in f if line.strip().isdigit()]
            elif args.from_csv:
                with open(args.from_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    lead_ids = [int(row['id']) for row in reader if row.get('id')]
            elif args.from_tsv:
                with open(args.from_tsv, 'r') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    lead_ids = [int(row['id']) for row in reader if row.get('id')]
            
            if not lead_ids:
                print("No lead IDs provided. Use --ids, --from-file, --from-csv, or --from-tsv.")
                return 1
            
            # Validate lead IDs exist
            model = getattr(args, 'model', 'crm.lead')
            existing_leads = self.client.search_read(model, [('id', 'in', lead_ids)], ['id'])
            existing_ids = [lead['id'] for lead in existing_leads]
            
            missing_ids = set(lead_ids) - set(existing_ids)
            if missing_ids:
                print(f"Error: Lead IDs do not exist: {', '.join(map(str, missing_ids))}")
                return 1
            
            # Build updates
            updates = {}
            if args.user_id is not None:
                updates['user_id'] = args.user_id
            if args.user_name:
                user_id = self.resolve_user_name(args.user_name)
                if user_id is None:
                    return 1
                updates['user_id'] = user_id
            if args.closer_id is not None:
                updates['closer_id'] = args.closer_id
            if args.closer_name:
                closer_id = self.resolve_user_name(args.closer_name)
                if closer_id is None:
                    return 1
                updates['closer_id'] = closer_id
            if args.open_user_id is not None:
                updates['open_user_id'] = args.open_user_id
            if args.open_user_name:
                open_user_id = self.resolve_user_name(args.open_user_name)
                if open_user_id is None:
                    return 1
                updates['open_user_id'] = open_user_id
            if args.status:
                updates['status'] = args.status
            
            if not updates:
                print("No updates specified. Use --user-id, --closer-id, --open-user-id, or --status.")
                return 1
            
            # Apply updates
            success = self.lead_manager.update_lead_assignments(
                lead_ids, 
                user_id=updates.get('user_id'),
                closer_id=updates.get('closer_id'),
                open_user_id=updates.get('open_user_id'),
                status=updates.get('status'),
                model=model
            )
            
            if success:
                print(f"Successfully updated {len(lead_ids)} leads with: {updates}")
                return 0
            else:
                print("Failed to update leads")
                return 1
                
        except Exception as e:
            print(f"Error updating leads: {e}")
            return 1

    def resolve_user_name(self, user_name: str) -> Optional[int]:
        """Resolve user name to user ID."""
        try:
            users = self.client.search_read('res.users', [('name', 'ilike', user_name)], ['id', 'name'])
            if not users:
                print(f"User '{user_name}' not found")
                return None
            elif len(users) == 1:
                return users[0]['id']
            else:
                print(f"Multiple users found for '{user_name}':")
                for user in users:
                    print(f"   ID: {user['id']}, Name: {user['name']}")
                print("   Use exact name or user ID instead")
                return None
                
        except Exception as e:
            print(f"Error resolving user name '{user_name}': {e}")
            return None

    def format_table(self, data: List[Dict[str, Any]], fields: List[str] = None) -> str:
        """Format data as a table."""
        if not data:
            return "No data found."
        
        if fields is None:
            fields = list(data[0].keys()) if data else []
        
        # Prepare rows
        rows = []
        for item in data:
            row = []
            for field in fields:
                value = item.get(field, '')
                if isinstance(value, list) and len(value) == 2:
                    value = value[1]  # Take the name from [id, name] format
                row.append(str(value))
            rows.append(row)
        
        return tabulate(rows, headers=fields, tablefmt="grid")

    def format_csv(self, data: List[Dict[str, Any]], fields: List[str] = None) -> str:
        """Format data as CSV."""
        if not data:
            return ""
        
        if fields is None:
            fields = list(data[0].keys()) if data else []
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        
        for item in data:
            row = {}
            for field in fields:
                value = item.get(field, '')
                if isinstance(value, list) and len(value) == 2:
                    value = value[1]  # Take the name from [id, name] format
                row[field] = str(value)
            writer.writerow(row)
        
        return output.getvalue()

    def handle_distribute(self, args) -> int:
        """Handle distribute command."""
        if not self.setup_client():
            return 1
        
        try:
            # Get leads to distribute
            filter_obj = LeadFilter()
            filter_obj.model("crm.lead")
            if args.status:
                filter_obj.by_status(args.status.split(','))
            if args.limit:
                filter_obj.limit(args.limit)
            
            leads = self.lead_manager.get_leads(filter_obj, fields=['id', 'name', 'user_id'])
            
            if not leads:
                print("No leads found to distribute.")
                return 0
            
            # Initialize distributor
            distributor = SmartDistributor()
            distributor.load_user_profiles_from_odoo(self.lead_manager)
            
            # Convert to Lead objects
            from .distribution import Lead
            lead_objects = [Lead(lead_id=l['id'], name=l['name']) for l in leads]
            
            # Distribute leads
            strategy = args.strategy or "proportional"
            assignments = distributor.distribute_leads(lead_objects, strategy=strategy)
            
            if not assignments:
                print("No assignments generated.")
                return 0
            
            # Display results
            print(f"Distribution Strategy: {strategy}")
            print(f"Total leads to distribute: {len(leads)}")
            print()
            
            for user_id, lead_ids in assignments.items():
                user_name = "Unknown"
                try:
                    user = self.client.search_read('res.users', [('id', '=', user_id)], ['name'])
                    if user:
                        user_name = user[0]['name']
                except:
                    pass
                
                print(f"{user_name} (ID: {user_id}): {len(lead_ids)} leads")
                for lead_id in lead_ids:
                    lead = next(l for l in leads if l['id'] == lead_id)
                    print(f"  - {lead['name']} (ID: {lead_id})")
                print()
            
            # Apply changes if not dry run
            if not args.dry_run:
                confirm = input("Apply these assignments? (y/N): ")
                if confirm.lower() == 'y':
                    for user_id, lead_ids in assignments.items():
                        success = self.lead_manager.update_lead_assignments(
                            lead_ids, 
                            user_id=user_id,
                            model="crm.lead"
                        )
                        if success:
                            print(f"Successfully assigned {len(lead_ids)} leads to user {user_id}")
                        else:
                            print(f"Failed to assign leads to user {user_id}")
                else:
                    print("Distribution cancelled.")
            else:
                print("Dry run completed. No changes applied.")
            
            return 0
            
        except Exception as e:
            print(f"Error distributing leads: {e}")
            return 1

    def handle_users(self, args) -> int:
        """Handle users command."""
        if not self.setup_client():
            return 1
        
        try:
            if args.list:
                users = self.client.search_read('res.users', [], ['id', 'name', 'login'])
                for user in users:
                    print(f"{user['id']}: {user['name']} ({user['login']})")
                return 0
            
            elif args.counts:
                users = self.client.search_read('res.users', [], ['id', 'name'])
                for user in users:
                    count = self.client.search_count('crm.lead', [('user_id', '=', user['id'])])
                    print(f"{user['name']}: {count} leads")
                return 0
            
            else:
                print("Use --list or --counts")
                return 1
                
        except Exception as e:
            print(f"Error handling users command: {e}")
            return 1

    def handle_invoices(self, args) -> int:
        """Handle invoices command."""
        if not self.setup_client():
            return 1
        
        try:
            domain = []
            if args.date_from:
                domain.append(('date_invoice', '>=', args.date_from))
            if args.date_to:
                domain.append(('date_invoice', '<=', args.date_to))
            if args.state:
                domain.append(('state', '=', args.state))
            if args.type:
                domain.append(('type', '=', args.type))
            if args.partner:
                domain.append(('partner_id.name', 'ilike', args.partner))
            if args.min_amount:
                domain.append(('amount_total', '>=', args.min_amount))
            if args.max_amount:
                domain.append(('amount_total', '<=', args.max_amount))
            
            fields = ['number', 'partner_id', 'amount_total', 'state', 'date_invoice', 'type']
            invoices = self.client.search_read('account.invoice', domain, fields, limit=args.limit)
            
            if not invoices:
                print("No invoices found.")
                return 0
            
            # Format output
            if args.format == "csv":
                output = self.format_csv(invoices)
            elif args.format == "json":
                import json
                output = json.dumps(invoices, indent=2, default=str)
            else:  # table
                output = self.format_table(invoices)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Results written to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"Error querying invoices: {e}")
            return 1

    def handle_check(self, args) -> int:
        """Handle check command."""
        try:
            if self.setup_client():
                print("✓ Successfully connected to Odoo")
                return 0
            else:
                print("✗ Failed to connect to Odoo")
                return 1
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return 1

    def handle_leads(self, args) -> int:
        """Handle leads command."""
        if not self.setup_client():
            return 1
        
        try:
            # Build filter from arguments - always use crm.lead for leads
            filter_obj = LeadFilter()
            filter_obj.model("crm.lead")
            
            # Status filter
            if args.status:
                filter_obj.by_status(args.status.split(','))
            
            # Type filter
            if args.type:
                filter_obj.by_type(args.type)
            
            # User filters
            if args.exact_user:
                filter_obj.by_user_assignments(user_names=[args.exact_user], exact=True)
            elif args.user:
                filter_obj.by_user_assignments(user_names=[args.user], exact=False)
            elif args.exact:
                filter_obj.by_user_assignments(user_names=[args.exact], exact=True)
            
            # Date filters - use source_date as it matches the CSV output format
            if args.date_from or args.date_to:
                filter_obj.by_date_range(args.date_from, args.date_to, field_name="source_date")
            
            # Source/campaign filters
            if args.source:
                filter_obj.by_web_source_ids([args.source])
            if args.campaign:
                filter_obj.by_campaign([args.campaign])
            if args.web_source_ids:
                filter_obj.by_web_source_ids(args.web_source_ids.split(','))
            
            # Text filters
            if args.team:
                filter_obj.by_team(args.team)
            
            if args.limit:
                filter_obj.limit(args.limit)
            
            # Fields to display
            fields = None
            if args.fields:
                fields = args.fields.split(',')
            
            # Get leads with error handling for large datasets
            try:
                leads = self.lead_manager.get_leads(filter_obj, fields=fields)
            except Exception as e:
                error_msg = str(e)
                if "unclosed token" in error_msg or "parsing" in error_msg.lower():
                    print("Error: Dataset too large to process. Try one of these solutions:")
                    print("  1. Add a smaller --limit (e.g., --limit 5000)")
                    print("  2. Use more specific date filters (e.g., --date-filter last_7_days)")
                    print("  3. Specify only essential --fields (e.g., --fields 'id,name,status,user_id')")
                    print("  4. Filter by specific users, status, or sources")
                    print(f"  Original error: {error_msg}")
                    return 1
                else:
                    # Re-raise other errors
                    raise
            
            if not leads:
                print("No leads found.")
                return 0
            
            # Handle count only
            if args.count:
                print(f"Total leads: {len(leads)}")
                return 0
            
            # Handle grouping
            if args.group_by:
                from collections import defaultdict
                groups = defaultdict(list)
                group_fields = args.group_by.split(',')
                
                for lead in leads:
                    key = tuple(str(lead.get(field, '')) for field in group_fields)
                    groups[key].append(lead)
                
                for key, group_leads in groups.items():
                    print(f"\n{' - '.join(key)}: {len(group_leads)} leads")
                    for lead in group_leads[:5]:  # Show first 5 of each group
                        print(f"  {lead.get('name', 'N/A')}")
                return 0
            
            # Handle pivot
            if args.pivot_rows and args.pivot_cols:
                from collections import defaultdict
                pivot_data = defaultdict(lambda: defaultdict(int))
                row_fields = args.pivot_rows.split(',')
                col_fields = args.pivot_cols.split(',')
                
                for lead in leads:
                    row_key = tuple(str(lead.get(field, '')) for field in row_fields)
                    col_key = tuple(str(lead.get(field, '')) for field in col_fields)
                    pivot_data[row_key][col_key] += 1
                
                # Print pivot table
                col_headers = sorted(set(k for row in pivot_data.values() for k in row.keys()))
                print(f"{' | '.join(row_fields):<30}", end="")
                for col in col_headers:
                    print(f" | {' | '.join(col):<15}", end="")
                print()
                print("-" * 80)
                
                for row_key, cols in pivot_data.items():
                    print(f"{' | '.join(row_key):<30}", end="")
                    for col in col_headers:
                        print(f" | {cols.get(col, 0):<15}", end="")
                    print()
                return 0
            
            # Format output
            if args.format == "csv":
                output = self.format_csv(leads, fields)
            elif args.format == "json":
                import json
                output = json.dumps(leads, indent=2, default=str)
            else:  # table
                output = self.format_table(leads, fields)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Results written to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"Error querying leads: {e}")
            return 1

    def handle_join(self, args) -> int:
        """Handle join command."""
        if not self.setup_client():
            return 1
        
        try:
            # Get leads
            lead_filter = LeadFilter()
            if args.lead_date_from or args.lead_date_to:
                lead_filter.by_date_range(args.lead_date_from, args.lead_date_to)
            if args.lead_status:
                lead_filter.by_status(args.lead_status.split(','))
            if args.lead_user:
                lead_filter.by_user_assignments(user_names=[args.lead_user])
            if args.lead_source:
                lead_filter.by_web_source_ids([args.lead_source])
            
            leads = self.lead_manager.get_leads(lead_filter, fields=['id', 'name', 'partner_id', 'user_id', 'create_date', 'status'])
            
            # Get invoices
            invoice_filter = []
            if args.invoice_date_from or args.invoice_date_to:
                invoice_filter.append(('date_invoice', '>=', args.invoice_date_from or '2000-01-01'))
                invoice_filter.append(('date_invoice', '<=', args.invoice_date_to or '2100-12-31'))
            if args.invoice_state:
                invoice_filter.append(('state', '=', args.invoice_state))
            
            invoices = self.client.search_read('account.invoice', invoice_filter, 
                                             ['id', 'number', 'partner_id', 'amount_total', 'state', 'date_invoice'])
            
            # Join data
            joined_data = []
            partner_invoice_map = {inv['partner_id'][0]: inv for inv in invoices if inv.get('partner_id')}
            
            for lead in leads:
                partner_id = lead.get('partner_id', [None])[0] if lead.get('partner_id') else None
                invoice = partner_invoice_map.get(partner_id)
                
                if invoice or not args.exclude_unmatched:
                    row = {
                        'lead_id': lead['id'],
                        'lead_name': lead['name'],
                        'lead_user': lead['user_id'][1] if lead.get('user_id') else '',
                        'lead_date': lead['create_date'],
                        'lead_status': lead['status'],
                        'invoice_number': invoice['number'] if invoice else '',
                        'invoice_amount': invoice['amount_total'] if invoice else 0,
                        'invoice_state': invoice['state'] if invoice else '',
                        'invoice_date': invoice['date_invoice'] if invoice else ''
                    }
                    joined_data.append(row)
            
            # Limit results
            if args.limit:
                joined_data = joined_data[:args.limit]
            
            # Format output
            if args.fields:
                fields = args.fields.split(',')
            else:
                fields = ['lead_id', 'lead_name', 'lead_user', 'lead_date', 'lead_status', 
                         'invoice_number', 'invoice_amount', 'invoice_state', 'invoice_date']
            
            if args.format == "csv":
                output = self.format_csv(joined_data, fields)
            elif args.format == "json":
                import json
                output = json.dumps(joined_data, indent=2, default=str)
            else:  # table
                output = self.format_table(joined_data, fields)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Results written to {args.output}")
            else:
                print(output)
            
            return 0
            
        except Exception as e:
            print(f"Error joining leads and invoices: {e}")
            return 1

    def handle_configure(self, args) -> int:
        """Handle configure command."""
        print("Interactive configuration not implemented. Please set environment variables:")
        print("ODOO_HOST, ODOO_PORT, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD")
        return 0

    def handle_dailydist(self, args) -> int:
        """Handle daily distribution command.
        
        Note: Daily distribution automatically filters for type='lead' only,
        ensuring that opportunities (type='opportunity') are not processed.
        """
        try:
            # Import the daily distribution module
            from .daily_distribution import DailyLeadDistributor, DailyDistributionConfigGenerator
            
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
            
            # Override max_leads in config if provided via CLI
            if args.max_leads:
                if 'execution' not in distributor.config:
                    distributor.config['execution'] = {}
                distributor.config['execution']['max_leads_per_run'] = args.max_leads
                print(f"Overriding max_leads_per_run to {args.max_leads}")
            
            # Set export options
            export_options = {
                'export_all_stages': args.export_all_stages,
                'export_before_filter': args.export_before_filter,
                'export_after_filter': args.export_after_filter or args.export_leads,
                'stages_output_dir': args.stages_output_dir or 'lead_stages',
                'show_filter_delta': args.show_filter_delta,
                'leads_fields': args.leads_fields.split(',') if args.leads_fields else None
            }
            
            # Run distribution
            result = distributor.run_daily_distribution(
                dry_run=args.dry_run,
                step_mode=args.step_mode,
                auto_accept=args.auto_accept,
                generate_report=args.generate_report,
                report_format=args.report_format,
                report_location=args.report_location,
                export_options=export_options
            )
            
            # Export distributable leads to CSV if requested
            if args.export_leads and result.success:
                self._export_distributable_leads(distributor, args)
            
            if result.success:
                if args.dry_run:
                    print(f"\n✓ Dry run analysis completed successfully")
                    print(f"  📊 Analysis time: {result.execution_time_seconds:.2f} seconds")
                    
                    # Show summary statistics from distribution_summary
                    if result.distribution_summary:
                        summary = result.distribution_summary
                        print(f"\n📋 QUICK SUMMARY:")
                        print(f"  • Total leads in range: {summary.get('total_leads_in_date_range', 0):,}")
                        print(f"  • Dropback leads: {summary.get('dropback_leads', 0):,}")
                        print(f"  • Distributable leads: {result.leads_found:,}")
                        print(f"  • Would distribute: {result.leads_distributed:,}")
                        print(f"  • Eligible salespeople: {result.salespeople_eligible:,}")
                        print(f"  • Strategy: {summary.get('strategy_used', 'N/A').title()}")
                        
                        if result.leads_distributed > 0:
                            print(f"\n💡 Run without --dry-run to execute this distribution")
                        else:
                            print(f"\n⚠️  No leads would be distributed - check configuration")
                else:
                    print(f"✓ Distribution completed successfully")
                    print(f"  Leads found: {result.leads_found}")
                    print(f"  Leads distributed: {result.leads_distributed}")
                    print(f"  Salespeople involved: {result.salespeople_received_leads}")
                    print(f"  Execution time: {result.execution_time_seconds:.2f} seconds")
                    
                    # Show dropback info if available
                    if result.distribution_summary and result.distribution_summary.get('dropback_leads', 0) > 0:
                        dropback_count = result.distribution_summary['dropback_leads']
                        print(f"  Dropback leads processed: {dropback_count}")
                
                return 0
            else:
                print(f"✗ Distribution failed: {result.error_message}")
                return 1
                
        except KeyboardInterrupt:
            print("\n✗ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    
    def _handle_config_generation(self, args) -> int:
        """Handle config file generation."""
        try:
            from .daily_distribution import DailyDistributionConfigGenerator
            
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
    
    def _generate_distribution_report(self, result, args):
        """Generate distribution report."""
        # Implementation for report generation
        print(f"Report generation requested but not yet implemented")
        pass

    def _export_distributable_leads(self, distributor, args):
        """Export distributable leads to CSV file."""
        try:
            import csv
            from pathlib import Path
            
            # Get the distributable leads from the distributor
            leads = getattr(distributor, 'distributable_leads', None)
            if not leads:
                print("⚠️  No distributable leads found to export")
                return
            
            # Set default output path
            output_path = args.leads_output or "distributable_leads.csv"
            
            # Set default fields to export
            default_fields = ["id", "name", "email", "phone", "status", "web_source_id", "partner_id", "create_date", "source_date"]
            if args.leads_fields:
                fields = [f.strip() for f in args.leads_fields.split(',')]
            else:
                fields = default_fields
            
            # Filter fields to only include those that exist in the lead data
            if leads:
                available_fields = list(leads[0].keys())
                fields = [f for f in fields if f in available_fields]
                missing_fields = [f for f in (args.leads_fields.split(',') if args.leads_fields else default_fields) if f not in available_fields]
                
                if missing_fields:
                    print(f"⚠️  Warning: These requested fields are not available: {', '.join(missing_fields)}")
                    print(f"Available fields: {', '.join(sorted(available_fields))}")
            
            # Create output directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                
                for lead in leads:
                    # Only write fields that exist in this lead
                    row = {field: lead.get(field, '') for field in fields}
                    writer.writerow(row)
            
            print(f"✓ Exported {len(leads):,} distributable leads to {output_path}")
            print(f"  Fields exported: {', '.join(fields)}")
            
        except Exception as e:
            print(f"✗ Error exporting leads: {e}")

    def run(self, argv=None) -> int:
        """Main CLI entry point."""
        parser = self.create_parser()
        args = parser.parse_args(argv)
        
        if not args.command:
            parser.print_help()
            return 1
        
        command_map = {
            "query": self.handle_query,
            "count": self.handle_count,
            "update": self.handle_update,
            "distribute": self.handle_distribute,
            "users": self.handle_users,
            "leads": self.handle_leads,
            "invoices": self.handle_invoices,
            "join": self.handle_join,
            "check": self.handle_check,
            "configure": self.handle_configure,
            "leadreport": self.handle_leadreport,
            "dailydist": self.handle_dailydist,
        }
        
        if args.command in command_map:
            return command_map[args.command](args)
        else:
            print(f"Unknown command: {args.command}")
            return 1


def main():
    """CLI entry point."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    import sys
    sys.exit(main())