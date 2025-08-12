    def _add_leadreport_args(self, parser: argparse.ArgumentParser):
        """Add lead report command arguments."""
        parser.add_argument("--format", choices=["table", "csv"], default="table", help="Output format")
        parser.add_argument("--output", help="Output file (default: stdout)")
        parser.add_argument("--date-field", default="create_date", help="Date field to filter on (default: create_date)")
        
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
        
        parser.epilog = """LEAD REPORT EXAMPLES:

DAILY STATUS REPORT:
  odlm leadreport --date-from 2024-01-01 --date-to 2024-01-31  # January report
  odlm leadreport --date-filter "today"                      # Today's report
  odlm leadreport --user "Alice" --date-filter "last_7_days"  # Alice's weekly report

CAMPAIGN ANALYSIS:
  odlm leadreport --source "facebook,google" --date-from 2024-01-01  # Campaign comparison
  odlm leadreport --status "new,in_progress,won" --format csv --output status_report.csv

TEAM PERFORMANCE:
  odlm leadreport --date-filter "this_month" --format table  # Current month team report
  odlm leadreport --user "Sales Team" --date-from 2024-01-01  # Team performance
"""

    def handle_leadreport(self, args) -> int:
        """Handle leadreport command."""
        if not self.setup_client():
            return 1
        
        try:
            # Build filter from arguments
            filter_obj = self.build_filter_from_args(args)
            
            # Get leads with basic fields
            fields = ["id", "name", "status", "user_id", "open_user_id", "closer_id", "source_id", "create_date"]
            leads = self.lead_manager.get_leads(filter_obj, fields=fields)
            
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
            
            # Convert to list and sort by user name
            report_data = sorted(user_reports.values(), key=lambda x: x['user_name'])
            
            # Prepare output
            headers = ['Date', 'User', 'Total', 'New', 'In Progress', 'Won', 'Lost', 'Call Back', 'Do Not Call']
            rows = []
            
            for report in report_data:
                row = [
                    report['date'],
                    report['user_name'],
                    report['total_leads'],
                    report['status_counts'].get('new', 0),
                    report['status_counts'].get('in_progress', 0),
                    report['status_counts'].get('won', 0),
                    report['status_counts'].get('lost', 0),
                    report['status_counts'].get('call_back', 0),
                    report['status_counts'].get('do_not_call', 0)
                ]
                rows.append(row)
            
            # Format output
            if args.format == "csv":
                import csv
                output = "Date,User,Total,New,In Progress,Won,Lost,Call Back,Do Not Call\n"
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