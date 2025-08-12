#!/usr/bin/env python3
"""
CLI script to run dry-run test with sale status exclusion.

Usage:
    python run_dry_run_test.py [--config CONFIG_FILE] [--step-mode] [--auto-accept]
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run dry-run test with sale status exclusion."""
    parser = argparse.ArgumentParser(
        description="Run dry-run test for daily lead distribution with sale status exclusion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_dry_run_test.py
    python run_dry_run_test.py --config config/test_dry_run_config.yaml
    python run_dry_run_test.py --step-mode --auto-accept
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/test_dry_run_config.yaml',
        help='Configuration file path (default: config/test_dry_run_config.yaml)'
    )
    
    parser.add_argument(
        '--step-mode',
        action='store_true',
        help='Enable step-through mode for detailed analysis'
    )
    
    parser.add_argument(
        '--auto-accept',
        action='store_true',
        help='Auto-accept all steps in step mode'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        print("💡 Available configuration files:")
        config_dir = Path("config")
        if config_dir.exists():
            for config_file in config_dir.glob("*.yaml"):
                print(f"   • {config_file}")
        else:
            print("   • No config directory found")
        return 1
    
    try:
        from odoo_lead_manager.daily_distribution import DailyLeadDistributor
        
        print("🚀 Starting Daily Lead Distribution Dry-Run Test")
        print("=" * 60)
        print(f"📁 Configuration: {args.config}")
        print(f"🔧 Step Mode: {'✅ Enabled' if args.step_mode else '❌ Disabled'}")
        print(f"🤖 Auto Accept: {'✅ Enabled' if args.auto_accept else '❌ Disabled'}")
        print(f"📝 Verbose: {'✅ Enabled' if args.verbose else '❌ Disabled'}")
        print("=" * 60)
        
        # Initialize distributor
        print("\n🔧 Initializing Daily Lead Distributor...")
        distributor = DailyLeadDistributor(args.config)
        
        # Run dry-run
        print("\n🔄 Running dry-run test...")
        result = distributor.run_daily_distribution(
            dry_run=True,
            step_mode=args.step_mode,
            auto_accept=args.auto_accept
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 DRY-RUN TEST RESULTS")
        print("=" * 60)
        
        if result.success:
            print("✅ Test completed successfully!")
        else:
            print("❌ Test failed!")
            if result.error_message:
                print(f"   Error: {result.error_message}")
        
        print(f"\n📈 Performance Metrics:")
        print(f"   • Execution Time: {result.execution_time_seconds:.2f} seconds")
        print(f"   • Leads Found: {result.leads_found:,}")
        print(f"   • Leads Distributed: {result.leads_distributed:,}")
        print(f"   • Leads Not Distributed: {result.leads_not_distributed:,}")
        print(f"   • Eligible Salespeople: {result.salespeople_eligible:,}")
        print(f"   • Salespeople Receiving Leads: {result.salespeople_received_leads:,}")
        
        if result.distribution_summary:
            print(f"\n📋 Distribution Summary:")
            summary = result.distribution_summary
            print(f"   • Total Leads in Date Range: {summary.get('total_leads_in_date_range', 0):,}")
            print(f"   • Dropback Leads: {summary.get('dropback_leads', 0):,}")
            print(f"   • Leads After Filters: {summary.get('leads_after_filters', 0):,}")
            print(f"   • Strategy Used: {summary.get('strategy_used', 'unknown')}")
            
            # Show distribution by salesperson
            assignments = summary.get('distribution_assignments', {})
            if assignments:
                print(f"\n👥 Distribution by Salesperson:")
                for user_id, count in assignments.items():
                    print(f"   • User {user_id}: {count} leads")
        
        # Sale status exclusion summary
        print(f"\n🔍 Sale Status Exclusion Summary:")
        config = distributor.config
        sale_status_config = config.get('lead_finding', {}).get('additional_filters', {}).get('exclude_sale_statuses', {})
        
        if sale_status_config.get('enabled', False):
            sale_statuses = sale_status_config.get('values', [])
            print(f"   ✅ Sale status exclusion is ENABLED")
            print(f"   📝 Excluded statuses ({len(sale_statuses)}):")
            for status in sale_statuses:
                print(f"      • {status}")
            print(f"   ⚙️  Match mode: {sale_status_config.get('match_mode', 'exact')}")
            print(f"   🔤 Case sensitive: {sale_status_config.get('case_sensitive', False)}")
        else:
            print(f"   ❌ Sale status exclusion is DISABLED")
        
        print("\n" + "=" * 60)
        print("🎉 Dry-run test completed!")
        print("💡 This was a test run - no changes were made to Odoo")
        print("📝 To run the actual distribution, set dry_run: false in the configuration")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Test cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 