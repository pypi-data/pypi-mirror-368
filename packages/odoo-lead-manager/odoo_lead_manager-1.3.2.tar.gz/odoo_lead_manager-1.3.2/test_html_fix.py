#!/usr/bin/env python3
"""Test that the HTML report generation fix works correctly."""

import sys
import os
from src.odoo_lead_manager.daily_distribution import DailyLeadDistributor

def test_html_report_generation():
    """Test that HTML report generation works without undefined 'leads' error."""
    
    # Create minimal report data structure
    report_data = {
        'report_metadata': {
            'generated_at': '2025-08-10 07:30:00',
            'date_range': 'Last 30 days'
        },
        'distribution_overview': {
            'total_leads_in_range': 500,
            'dropback_leads': 50,
            'final_distributable_leads': 200,
            'eligible_salespeople_count': 10
        },
        'lead_analysis': {
            'total_starting_leads': 500,
            'status_distribution': {
                'new': 250,
                'in_progress': 150,
                'call_back': 50,
                'utr': 50
            },
            'web_source_distribution': {
                'Facebook': 200,
                'Google Ads': 150,
                'Website': 100,
                'Email Campaign': 50
            },
            'sales_match_analysis': {
                'total_leads': 500,
                'with_opportunities': 100,
                'opportunity_rate': 20.0,
                'with_email': 400,
                'email_rate': 80.0,
                'with_phone': 350,
                'phone_rate': 70.0,
                'with_mobile': 300,
                'mobile_rate': 60.0,
                'assigned': 250,
                'assignment_rate': 50.0
            }
        },
        'filter_impact': {
            'web_source_filter': 100,
            'status_filter': 50,
            'dnc_filter': 30,
            'sales_filter': 120
        },
        'salesperson_workload': [
            {
                'name': 'Alice Smith',
                'team': 'Voice',
                'level': 'senior',
                'current_leads': 150,
                'target_leads': 200,
                'utilization_percent': 75.0,
                'deficit': 50,
                'is_eligible': True,
                'filter_reason': None
            },
            {
                'name': 'Bob Johnson',
                'team': 'Voice',
                'level': 'mid_level',
                'current_leads': 120,
                'target_leads': 150,
                'utilization_percent': 80.0,
                'deficit': 30,
                'is_eligible': True,
                'filter_reason': None
            }
        ],
        'distribution_preview': {
            'total_to_distribute': 200,
            'users_receiving_leads': 8,
            'assignments': [
                {
                    'salesperson_name': 'Alice Smith',
                    'new_leads': 50,
                    'current_leads': 150,
                    'total_after_distribution': 200,
                    'target_leads': 200,
                    'utilization_after_percent': 100.0
                },
                {
                    'salesperson_name': 'Bob Johnson',
                    'new_leads': 30,
                    'current_leads': 120,
                    'total_after_distribution': 150,
                    'target_leads': 150,
                    'utilization_after_percent': 100.0
                }
            ]
        },
        'strategy_details': {
            'strategy': 'level_based'
        },
        'recommendations': [
            'Consider increasing salesperson capacity',
            'Review lead quality filters'
        ]
    }
    
    try:
        # Create a minimal config file
        import tempfile
        import yaml
        
        config = {
            'odoo_connection': {
                'host': 'test',
                'database': 'test',
                'username': 'test',
                'password': 'test'
            },
            'salesperson_selection': {
                'source_type': 'list',
                'source_config': {
                    'salespeople_list': ['Test User']
                }
            },
            'lead_finding': {
                'date_range': {
                    'older_than_days': 0,
                    'younger_than_days': 30
                }
            },
            'distribution': {
                'strategy': 'round_robin'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_file = f.name
        
        # Create distributor instance
        distributor = DailyLeadDistributor(config_file)
        
        # Test HTML report generation (this was failing with "name 'leads' is not defined")
        html_content = distributor._generate_html_report(report_data)
        
        # Basic validation that HTML was generated
        assert html_content is not None
        assert len(html_content) > 1000  # Should be a substantial HTML document
        assert '<html' in html_content
        assert 'Daily Lead Distribution Report' in html_content
        
        # Check that key data points are included
        assert '500' in html_content  # total_starting_leads
        assert '200' in html_content  # final_distributable_leads
        assert 'Alice Smith' in html_content
        assert 'Bob Johnson' in html_content
        
        print("✅ SUCCESS: HTML report generation works correctly!")
        print(f"✅ Generated HTML report of {len(html_content):,} characters")
        
        # Clean up
        os.unlink(config_file)
        
        return True
        
    except NameError as e:
        if 'leads' in str(e):
            print(f"❌ FAILED: Still has undefined 'leads' reference")
            print(f"   Error: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"❌ FAILED: Unexpected error")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_html_report_generation()
    sys.exit(0 if success else 1)