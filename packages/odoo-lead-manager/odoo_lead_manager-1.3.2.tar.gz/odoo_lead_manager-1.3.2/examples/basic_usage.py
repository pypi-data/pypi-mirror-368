#!/usr/bin/env python3
"""
Basic usage examples for Odoo Lead Manager.

This script demonstrates common use cases and provides practical examples
for getting started with the package.
"""

import os
from datetime import datetime, date
from odoo_lead_manager import OdooClient, LeadManager, SmartDistributor
from odoo_lead_manager.filters import LeadFilter, LeadStatus
from odoo_lead_manager.distribution import UserProfile, Lead


def main():
    """Run basic usage examples."""
    print("🚀 Odoo Lead Manager - Basic Usage Examples")
    print("=" * 50)
    
    # Example 1: Basic Connection
    print("\n1. Basic Connection Setup")
    print("-" * 25)
    
    # Option A: Direct configuration
    client = OdooClient(
        host="localhost",
        port=8069,
        database="odoo",
        username="admin",
        password="admin"
    )
    
    # Option B: Environment variables (recommended)
    # client = OdooClient()
    
    # Option C: Context manager (auto-cleanup)
    # with OdooClient() as client:
    #     # Use client here
    #     pass
    
    print("✓ Client initialized")
    
    # Example 2: Lead Manager Setup
    print("\n2. Lead Manager Setup")
    print("-" * 25)
    
    lead_manager = LeadManager(client)
    print("✓ Lead manager initialized")
    
    # Example 3: Basic Filtering
    print("\n3. Basic Lead Filtering")
    print("-" * 25)
    
    # Method A: Quick filtering
    print("Quick filtering examples:")
    
    # These would work with real Odoo connection:
    # leads = lead_manager.get_leads_by_date_range(
    #     start_date=date(2024, 1, 1),
    #     end_date=date(2024, 1, 31)
    # )
    
    # leads = lead_manager.get_leads_by_status(["new", "in_progress"])
    # leads = lead_manager.get_leads_by_source(["Website", "Email Campaign"])
    # leads = lead_manager.get_leads_by_users(user_names=["Alice Smith", "Bob Johnson"])
    
    print("   • Date range filtering")
    print("   • Status filtering") 
    print("   • Source filtering")
    print("   • User assignment filtering")
    
    # Method B: Advanced filtering with LeadFilter
    print("\nAdvanced filtering with LeadFilter:")
    
    filter_obj = LeadFilter() \
        .by_date_range(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        ) \
        .by_status(["new", "in_progress"]) \
        .by_web_source_ids(["Website", "Email Campaign"]) \
        .by_user_assignments(user_names=["Alice Smith", "Bob Johnson"]) \
        .fields(["id", "name", "email", "phone", "status", "user_id"]) \
        .limit(100) \
        .order("create_date desc")
    
    print("✓ Complex filter built")
    print(f"   Filter configuration: {filter_obj.build()}")
    
    # Example 4: Lead Analysis
    print("\n4. Lead Analysis")
    print("-" * 25)
    
    # This would work with real data:
    # summary = lead_manager.get_lead_summary()
    # 
    # print(f"   Total leads: {summary['total_leads']}")
    # print(f"   User assignments: {summary['user_assignments']}")
    # print(f"   Source distribution: {summary['source_distribution']}")
    # print(f"   Status distribution: {summary['status_distribution']}")
    
    print("✓ Analysis framework ready")
    
    # Example 5: Smart Distribution Setup
    print("\n5. Smart Distribution Setup")
    print("-" * 25)
    
    distributor = SmartDistributor()
    
    # Add user profiles
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
    
    print("✓ Users configured for distribution")
    
    # Example 6: Lead Distribution
    print("\n6. Lead Distribution")
    print("-" * 25)
    
    # Prepare leads for distribution
    leads_to_distribute = [
        Lead(lead_id=101, name="Hot Lead A", source_id="web", priority=3),
        Lead(lead_id=102, name="Warm Lead B", source_id="email", priority=2),
        Lead(lead_id=103, name="Cold Lead C", source_id="referral", priority=1),
        Lead(lead_id=104, name="Hot Lead D", source_id="social", priority=3),
        Lead(lead_id=105, name="Warm Lead E", source_id="web", priority=2),
    ]
    
    print(f"   Leads to distribute: {len(leads_to_distribute)}")
    
    # Different distribution strategies
    from odoo_lead_manager.distribution import DistributionStrategy
    
    strategies = [
        DistributionStrategy.PROPORTIONAL,
        DistributionStrategy.ROUND_ROBIN,
        DistributionStrategy.LEAST_LOADED,
        DistributionStrategy.WEIGHTED_RANDOM,
        DistributionStrategy.CAPACITY_BASED
    ]
    
    for strategy in strategies:
        distributor.set_distribution_strategy(strategy)
        assignments = distributor.distribute_leads(leads_to_distribute)
        
        print(f"   {strategy.value}: {assignments}")
    
    # Example 7: Distribution Report
    print("\n7. Distribution Report")
    print("-" * 25)
    
    distributor.set_distribution_strategy(DistributionStrategy.PROPORTIONAL)
    assignments = distributor.distribute_leads(leads_to_distribute)
    
    report = distributor.get_distribution_report()
    
    print(f"   Total users: {report['total_users']}")
    print(f"   Active users: {report['active_users']}")
    
    for user_id, details in report['user_details'].items():
        print(f"   {details['name']}: {details['current_leads']} leads "
              f"(expected: {details['expected_leads']:.1f})")
    
    # Example 8: Real-world Workflow
    print("\n8. Real-world Workflow")
    print("-" * 25)
    
    print("Complete workflow example:")
    print("1. Connect to Odoo")
    print("2. Load user profiles and proportions")
    print("3. Fetch new leads")
    print("4. Distribute leads intelligently")
    print("5. Update lead assignments")
    print("6. Generate reports")
    
    # Workflow code (commented for demo)
    # with OdooClient() as client:
    #     lead_manager = LeadManager(client)
    #     distributor = SmartDistributor()
    #     
    #     # Load users and proportions
    #     distributor.load_user_profiles_from_odoo(lead_manager)
    #     distributor.load_proportions_from_odoo(lead_manager)
    #     
    #     # Fetch new leads
    #     new_leads = lead_manager.get_leads_by_status("new")
    #     
    #     # Convert to Lead objects
    #     lead_objects = [
    #         Lead(lead_id=l['id'], name=l['name']) 
    #         for l in new_leads
    #     ]
    #     
    #     # Distribute leads
    #     assignments = distributor.distribute_leads(lead_objects)
    #     
    #     # Apply assignments
    #     for user_id, lead_ids in assignments.items():
    #         lead_manager.update_lead_assignments(lead_ids, user_id=user_id)
    
    print("✓ Workflow template ready")
    
    # Example 9: Environment Configuration
    print("\n9. Environment Configuration")
    print("-" * 25)
    
    env_example = """
    # .env file example
    ODOO_HOST=your-odoo-server.com
    ODOO_PORT=8069
    ODOO_DB=your_database
    ODOO_USERNAME=your_username
    ODOO_PASSWORD=your_password
    """
    
    print(env_example)
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed! Ready to use Odoo Lead Manager")
    print("\nNext steps:")
    print("1. Set up your Odoo connection in .env file")
    print("2. Run: pip install -e .")
    print("3. Run tests: python run_tests.py")
    print("4. Start using the package!")


if __name__ == "__main__":
    main()