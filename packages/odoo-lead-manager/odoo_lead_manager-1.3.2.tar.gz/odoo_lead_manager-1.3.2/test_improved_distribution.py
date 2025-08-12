#!/usr/bin/env python3
"""
Test script for the improved daily distribution algorithm.
Tests the new functionality that prevents leads from being reassigned to their current owner.
"""

import sys
import os
from datetime import datetime, date
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from odoo_lead_manager.daily_distribution import (
    DailyLeadDistributor, 
    SalespersonConfig,
    LeadDistributionResult
)

class MockOdooClient:
    """Mock Odoo client for testing purposes."""
    
    def __init__(self):
        self._uid = 1
        self.users = [
            {'id': 1, 'name': 'Alice Smith'},
            {'id': 2, 'name': 'Bob Johnson'},  
            {'id': 3, 'name': 'Carol Davis'},
            {'id': 4, 'name': 'Dave Wilson'}
        ]
        
        # Mock lead data with some assigned to participants
        self.leads = [
            {'id': 101, 'user_id': 1, 'name': 'Lead 1', 'type': 'lead', 'status': 'new'},  # Assigned to Alice
            {'id': 102, 'user_id': 2, 'name': 'Lead 2', 'type': 'lead', 'status': 'new'},  # Assigned to Bob
            {'id': 103, 'user_id': None, 'name': 'Lead 3', 'type': 'lead', 'status': 'new'},  # Unassigned
            {'id': 104, 'user_id': 5, 'name': 'Lead 4', 'type': 'lead', 'status': 'new'},  # Assigned to non-participant
            {'id': 105, 'user_id': 1, 'name': 'Lead 5', 'type': 'lead', 'status': 'new'},  # Assigned to Alice
            {'id': 106, 'user_id': 3, 'name': 'Lead 6', 'type': 'lead', 'status': 'new'},  # Assigned to Carol
        ]
    
    def connect(self):
        return True
    
    def authenticate(self):
        return True
    
    def search_read(self, model, domain=None, fields=None, limit=None):
        if model == 'res.users':
            return self.users
        elif model in ['crm.lead', 'res.partner']:
            # Filter leads based on domain if provided
            results = self.leads.copy()
            
            # Simple domain filtering for testing
            if domain:
                filtered_results = []
                for lead in results:
                    matches = True
                    for condition in domain:
                        if len(condition) == 3:
                            field, operator, value = condition
                            if field == 'type' and operator == '=' and lead.get('type') != value:
                                matches = False
                                break
                            elif field == 'user_id' and operator == '=' and lead.get('user_id') != value:
                                matches = False
                                break
                    if matches:
                        filtered_results.append(lead)
                results = filtered_results
            
            # Apply limit
            if limit and len(results) > limit:
                results = results[:limit]
            
            # Filter fields if specified
            if fields:
                filtered_results = []
                for result in results:
                    filtered_result = {}
                    for field in fields:
                        filtered_result[field] = result.get(field)
                    filtered_results.append(filtered_result)
                results = filtered_results
            
            return results
        
        return []
    
    def search_count(self, model, domain=None):
        results = self.search_read(model, domain)
        return len(results)


class TestImprovedDistribution:
    """Test suite for improved distribution algorithm."""
    
    def __init__(self):
        self.test_config = {
            'odoo_connection': {
                'host': 'localhost',
                'port': 8069,
                'database': 'test_db',
                'username': 'test',
                'password': 'test'
            },
            'campaign': {
                'name': 'Test Campaign',
                'target_campaign': 'Test'
            },
            'salesperson_selection': {
                'source_type': 'list',
                'source_config': {
                    'salespeople_list': ['Alice Smith', 'Bob Johnson', 'Carol Davis']
                },
                'filters': {
                    'active_only': True
                }
            },
            'lead_finding': {
                'date_range': {
                    'older_than_days': 0,
                    'younger_than_days': 30
                },
                'sales_filter': {'enabled': False},
                'dropback_filter': {'enabled': False},
                'additional_filters': {
                    'status': {
                        'values': ['new'],
                        'case_sensitive': False,
                        'match_mode': 'exact'
                    },
                    'exclude_dnc': False
                }
            },
            'distribution': {
                'strategy': 'level_based',
                'level_based': {
                    'levels': {
                        'senior': {'target_leads': 200, 'priority': 1},
                        'mid_level': {'target_leads': 150, 'priority': 2},
                        'junior': {'target_leads': 100, 'priority': 3}
                    }
                }
            },
            'execution': {
                'dry_run': True,
                'max_leads_per_run': 1000
            }
        }
    
    def create_mock_distributor(self):
        """Create a distributor with mock client."""
        # Create temporary config file
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name
        
        try:
            distributor = DailyLeadDistributor(config_path)
            # Replace the client with our mock
            distributor.client = MockOdooClient()
            distributor.lead_manager.client = distributor.client
            return distributor
        finally:
            os.unlink(config_path)
    
    def test_lead_separation(self):
        """Test that leads are correctly separated by ownership."""
        print("🧪 Test 1: Lead Separation")
        
        distributor = self.create_mock_distributor()
        
        # Create test leads
        leads = [
            {'id': 101, 'user_id': 1, 'name': 'Lead 1'},  # Owned by participant
            {'id': 102, 'user_id': 2, 'name': 'Lead 2'},  # Owned by participant
            {'id': 103, 'user_id': None, 'name': 'Lead 3'},  # Unassigned
            {'id': 104, 'user_id': 5, 'name': 'Lead 4'},  # Owned by non-participant
        ]
        
        participant_ids = {1, 2, 3}  # Alice, Bob, Carol
        
        leads_to_redistribute, leads_from_outside = distributor._separate_leads_by_ownership(leads, participant_ids)
        
        print(f"   Leads to redistribute: {len(leads_to_redistribute)} (expected: 2)")
        print(f"   Leads from outside: {len(leads_from_outside)} (expected: 2)")
        
        assert len(leads_to_redistribute) == 2, f"Expected 2 leads to redistribute, got {len(leads_to_redistribute)}"
        assert len(leads_from_outside) == 2, f"Expected 2 leads from outside, got {len(leads_from_outside)}"
        
        # Check that the right leads are in each category
        redistribute_ids = {lead['id'] for lead in leads_to_redistribute}
        outside_ids = {lead['id'] for lead in leads_from_outside}
        
        assert redistribute_ids == {101, 102}, f"Expected {{101, 102}}, got {redistribute_ids}"
        assert outside_ids == {103, 104}, f"Expected {{103, 104}}, got {outside_ids}"
        
        print("   ✅ Lead separation test passed!")
        return True
    
    def test_level_based_distribution(self):
        """Test level-based distribution with exclusion."""
        print("\n🧪 Test 2: Level-Based Distribution")
        
        distributor = self.create_mock_distributor()
        
        # Create test salespeople
        salespeople = [
            SalespersonConfig('Alice Smith', 1, 'Test', level='senior', target_leads=200),
            SalespersonConfig('Bob Johnson', 2, 'Test', level='mid_level', target_leads=150),
            SalespersonConfig('Carol Davis', 3, 'Test', level='junior', target_leads=100),
        ]
        
        # Create test leads - some owned by participants
        leads = [
            {'id': 101, 'user_id': 1, 'name': 'Lead 1'},  # Alice's lead
            {'id': 102, 'user_id': 2, 'name': 'Lead 2'},  # Bob's lead  
            {'id': 103, 'user_id': None, 'name': 'Lead 3'},  # Unassigned
            {'id': 104, 'user_id': 5, 'name': 'Lead 4'},  # Non-participant
            {'id': 105, 'user_id': 1, 'name': 'Lead 5'},  # Alice's lead
            {'id': 106, 'user_id': 3, 'name': 'Lead 6'},  # Carol's lead
        ]
        
        assignments = distributor._distribute_level_based(leads, salespeople)
        
        print(f"   Assignments: {assignments}")
        
        # Verify no one gets their own leads back
        for user_id, lead_ids in assignments.items():
            for lead_id in lead_ids:
                original_lead = next(lead for lead in leads if lead['id'] == lead_id)
                original_owner = original_lead.get('user_id')
                
                if original_owner == user_id:
                    print(f"   ❌ ERROR: User {user_id} got their own lead {lead_id} back!")
                    return False
        
        total_assigned = sum(len(lead_ids) for lead_ids in assignments.values())
        print(f"   Total leads assigned: {total_assigned} out of {len(leads)}")
        
        print("   ✅ Level-based distribution test passed!")
        return True
    
    def test_round_robin_distribution(self):
        """Test round-robin distribution with exclusion."""
        print("\n🧪 Test 3: Round-Robin Distribution")
        
        distributor = self.create_mock_distributor()
        
        # Update config for round-robin
        distributor.config['distribution']['strategy'] = 'round_robin'
        
        salespeople = [
            SalespersonConfig('Alice Smith', 1, 'Test', level='mid_level', target_leads=150),
            SalespersonConfig('Bob Johnson', 2, 'Test', level='mid_level', target_leads=150),
            SalespersonConfig('Carol Davis', 3, 'Test', level='mid_level', target_leads=150),
        ]
        
        leads = [
            {'id': 101, 'user_id': 1, 'name': 'Lead 1'},  # Alice's lead
            {'id': 102, 'user_id': 2, 'name': 'Lead 2'},  # Bob's lead  
            {'id': 103, 'user_id': None, 'name': 'Lead 3'},  # Unassigned
            {'id': 104, 'user_id': None, 'name': 'Lead 4'},  # Unassigned
        ]
        
        assignments = distributor._distribute_round_robin(leads, salespeople)
        
        print(f"   Assignments: {assignments}")
        
        # Verify no one gets their own leads back
        for user_id, lead_ids in assignments.items():
            for lead_id in lead_ids:
                original_lead = next(lead for lead in leads if lead['id'] == lead_id)
                original_owner = original_lead.get('user_id')
                
                if original_owner == user_id:
                    print(f"   ❌ ERROR: User {user_id} got their own lead {lead_id} back!")
                    return False
        
        total_assigned = sum(len(lead_ids) for lead_ids in assignments.values())
        print(f"   Total leads assigned: {total_assigned} out of {len(leads)}")
        
        print("   ✅ Round-robin distribution test passed!")
        return True
    
    def test_proportional_distribution(self):
        """Test proportional distribution with exclusion."""
        print("\n🧪 Test 4: Proportional Distribution")
        
        distributor = self.create_mock_distributor()
        
        # Update config for proportional
        distributor.config['distribution']['strategy'] = 'proportional'
        
        salespeople = [
            SalespersonConfig('Alice Smith', 1, 'Test', level='senior', target_leads=200),
            SalespersonConfig('Bob Johnson', 2, 'Test', level='mid_level', target_leads=150),
            SalespersonConfig('Carol Davis', 3, 'Test', level='junior', target_leads=100),
        ]
        
        leads = [
            {'id': 101, 'user_id': 1, 'name': 'Lead 1'},  # Alice's lead
            {'id': 102, 'user_id': 2, 'name': 'Lead 2'},  # Bob's lead  
            {'id': 103, 'user_id': None, 'name': 'Lead 3'},  # Unassigned
            {'id': 104, 'user_id': None, 'name': 'Lead 4'},  # Unassigned
        ]
        
        assignments = distributor._distribute_proportional(leads, salespeople)
        
        print(f"   Assignments: {assignments}")
        
        # Verify no one gets their own leads back
        for user_id, lead_ids in assignments.items():
            for lead_id in lead_ids:
                original_lead = next(lead for lead in leads if lead['id'] == lead_id)
                original_owner = original_lead.get('user_id')
                
                if original_owner == user_id:
                    print(f"   ❌ ERROR: User {user_id} got their own lead {lead_id} back!")
                    return False
        
        total_assigned = sum(len(lead_ids) for lead_ids in assignments.values())
        print(f"   Total leads assigned: {total_assigned} out of {len(leads)}")
        
        print("   ✅ Proportional distribution test passed!")
        return True
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Improved Distribution Algorithm Tests")
        print("=" * 60)
        
        tests = [
            self.test_lead_separation,
            self.test_level_based_distribution,
            self.test_round_robin_distribution,
            self.test_proportional_distribution,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"   ❌ Test failed with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! The improved distribution algorithm works correctly.")
        else:
            print("⚠️  Some tests failed. Please review the implementation.")
        
        return failed == 0


if __name__ == "__main__":
    tester = TestImprovedDistribution()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)