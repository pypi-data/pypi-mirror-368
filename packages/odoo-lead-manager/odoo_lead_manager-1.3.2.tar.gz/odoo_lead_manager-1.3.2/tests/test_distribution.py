"""
Tests for SmartDistributor class.
"""

import pytest
from unittest.mock import Mock
from odoo_lead_manager.distribution import (
    SmartDistributor, UserProfile, Lead, DistributionStrategy
)


class TestSmartDistributor:
    """Test cases for SmartDistributor."""

    def test_initialization(self):
        """Test SmartDistributor initialization."""
        distributor = SmartDistributor()
        
        assert isinstance(distributor.user_profiles, dict)
        assert isinstance(distributor.distribution_history, list)
        assert distributor.strategy == DistributionStrategy.PROPORTIONAL

    def test_add_user_profile(self):
        """Test adding user profiles."""
        distributor = SmartDistributor()
        profile = UserProfile(user_id=1, name="Test User", current_leads=5)
        
        distributor.add_user_profile(profile)
        
        assert 1 in distributor.user_profiles
        assert distributor.user_profiles[1] == profile

    def test_remove_user_profile(self):
        """Test removing user profiles."""
        distributor = SmartDistributor()
        profile = UserProfile(user_id=1, name="Test User")
        distributor.add_user_profile(profile)
        
        result = distributor.remove_user_profile(1)
        assert result is True
        assert 1 not in distributor.user_profiles
        
        # Test removing non-existent user
        result = distributor.remove_user_profile(999)
        assert result is False

    def test_update_user_current_leads(self):
        """Test updating user lead counts."""
        distributor = SmartDistributor()
        profile = UserProfile(user_id=1, name="Test User", current_leads=5)
        distributor.add_user_profile(profile)
        
        distributor.update_user_current_leads(1, 10)
        
        assert distributor.user_profiles[1].current_leads == 10

    def test_set_distribution_strategy(self):
        """Test setting distribution strategy."""
        distributor = SmartDistributor()
        
        distributor.set_distribution_strategy(DistributionStrategy.ROUND_ROBIN)
        assert distributor.strategy == DistributionStrategy.ROUND_ROBIN

    def test_distribute_leads_empty(self, smart_distributor):
        """Test distributing empty lead list."""
        assignments = smart_distributor.distribute_leads([])
        assert assignments == {}

    def test_distribute_leads_no_active_users(self):
        """Test distributing with no active users."""
        distributor = SmartDistributor()
        leads = [Lead(lead_id=1, name="Test Lead")]
        
        assignments = distributor.distribute_leads(leads)
        assert assignments == {}

    def test_distribute_proportional(self, smart_distributor, sample_lead_objects):
        """Test proportional distribution."""
        assignments = smart_distributor.distribute_leads(
            sample_lead_objects, DistributionStrategy.PROPORTIONAL
        )
        
        assert len(assignments) == 3  # 3 users
        total_assigned = sum(len(leads) for leads in assignments.values())
        assert total_assigned == 5  # 5 leads

    def test_distribute_round_robin(self, smart_distributor, sample_lead_objects):
        """Test round-robin distribution."""
        assignments = smart_distributor.distribute_leads(
            sample_lead_objects, DistributionStrategy.ROUND_ROBIN
        )
        
        assert len(assignments) == 3
        total_assigned = sum(len(leads) for leads in assignments.values())
        assert total_assigned == 5

    def test_distribute_least_loaded(self, smart_distributor, sample_lead_objects):
        """Test least-loaded distribution."""
        assignments = smart_distributor.distribute_leads(
            sample_lead_objects, DistributionStrategy.LEAST_LOADED
        )
        
        assert len(assignments) == 3
        total_assigned = sum(len(leads) for leads in assignments.values())
        assert total_assigned == 5

    def test_distribute_weighted_random(self, smart_distributor, sample_lead_objects):
        """Test weighted random distribution."""
        assignments = smart_distributor.distribute_leads(
            sample_lead_objects, DistributionStrategy.WEIGHTED_RANDOM
        )
        
        assert len(assignments) == 3
        total_assigned = sum(len(leads) for leads in assignments.values())
        assert total_assigned == 5

    def test_distribute_capacity_based(self, smart_distributor, sample_lead_objects):
        """Test capacity-based distribution."""
        assignments = smart_distributor.distribute_leads(
            sample_lead_objects, DistributionStrategy.CAPACITY_BASED
        )
        
        assert len(assignments) == 3
        total_assigned = sum(len(leads) for leads in assignments.values())
        assert total_assigned == 5

    def test_distribute_leads_obeys_capacity_limits(self):
        """Test that distribution respects capacity limits."""
        distributor = SmartDistributor()
        
        # Add user with low capacity
        user = UserProfile(
            user_id=1, name="Limited User",
            current_leads=8, max_capacity=10, expected_percentage=100.0
        )
        distributor.add_user_profile(user)
        
        # Try to assign more leads than capacity allows
        leads = [Lead(lead_id=i, name=f"Lead {i}") for i in range(1, 6)]
        assignments = distributor.distribute_leads(leads)
        
        # Should only assign 2 leads (10 - 8 = 2 remaining capacity)
        assert len(assignments[1]) == 2

    def test_get_distribution_report(self, smart_distributor):
        """Test getting distribution report."""
        report = smart_distributor.get_distribution_report()
        
        assert "total_users" in report
        assert "active_users" in report
        assert "user_details" in report
        assert "expected_vs_actual" in report
        assert "distribution_history" in report
        
        assert report["total_users"] == 3
        assert report["active_users"] == 3

    def test_load_user_profiles_from_odoo(self, smart_distributor, mock_odoo_client):
        """Test loading user profiles from Odoo."""
        mock_odoo_client.search_read.return_value = [
            {"id": 1, "name": "Alice Smith", "email": "alice@test.com", "login": "alice"},
            {"id": 2, "name": "Bob Johnson", "email": "bob@test.com", "login": "bob"},
        ]
        
        # Mock get_user_lead_counts
        def mock_get_user_lead_counts(user_ids=None):
            return {1: 5, 2: 10}
        
        # Create a mock lead manager
        mock_lead_manager = Mock()
        mock_lead_manager.client = mock_odoo_client
        mock_lead_manager.get_user_lead_counts = mock_get_user_lead_counts
        
        smart_distributor.load_user_profiles_from_odoo(mock_lead_manager)
        
        assert len(smart_distributor.user_profiles) == 2
        assert 1 in smart_distributor.user_profiles
        assert 2 in smart_distributor.user_profiles
        assert smart_distributor.user_profiles[1].name == "Alice Smith"
        assert smart_distributor.user_profiles[1].current_leads == 5

    def test_save_proportions_to_odoo(self, smart_distributor, mock_odoo_client):
        """Test saving proportions to Odoo."""
        # Create a mock lead manager
        mock_lead_manager = Mock()
        mock_lead_manager.client = mock_odoo_client
        
        # Mock search_read to return empty (no existing records)
        mock_odoo_client.search_read.return_value = []
        
        result = smart_distributor.save_proportions_to_odoo(mock_lead_manager)
        
        assert result is True
        # Should create new records for each user
        assert mock_odoo_client.create.call_count == 3

    def test_save_proportions_to_odoo_with_existing(self, smart_distributor, mock_odoo_client):
        """Test saving proportions when records already exist."""
        # Create a mock lead manager
        mock_lead_manager = Mock()
        mock_lead_manager.client = mock_odoo_client
        
        # Mock search_read to return existing records
        mock_odoo_client.search_read.side_effect = [
            [{"id": 1, "user_id": [1, "Alice Smith"]}],  # Alice has existing record
            [],  # Bob doesn't
            []   # Carol doesn't
        ]
        
        result = smart_distributor.save_proportions_to_odoo(mock_lead_manager)
        
        assert result is True
        # Should update one and create two
        assert mock_odoo_client.write.call_count == 1
        assert mock_odoo_client.create.call_count == 2

    def test_load_proportions_from_odoo(self, smart_distributor, mock_odoo_client):
        """Test loading proportions from Odoo."""
        mock_odoo_client.search_read.return_value = [
            {"user_id": [1, "Alice Smith"], "expected_percentage": 50.0, "max_capacity": 60},
            {"user_id": [2, "Bob Johnson"], "expected_percentage": 30.0, "max_capacity": 40},
        ]
        
        # Create a mock lead manager
        mock_lead_manager = Mock()
        mock_lead_manager.client = mock_odoo_client
        
        # Add users to distributor
        smart_distributor.add_user_profile(UserProfile(user_id=1, name="Alice Smith"))
        smart_distributor.add_user_profile(UserProfile(user_id=2, name="Bob Johnson"))
        
        result = smart_distributor.load_proportions_from_odoo(mock_lead_manager)
        
        assert result is True
        assert smart_distributor.user_profiles[1].expected_percentage == 50.0
        assert smart_distributor.user_profiles[1].max_capacity == 60
        assert smart_distributor.user_profiles[2].expected_percentage == 30.0
        assert smart_distributor.user_profiles[2].max_capacity == 40

    def test_distribution_history_tracking(self, smart_distributor, sample_lead_objects):
        """Test that distribution history is tracked."""
        initial_history_length = len(smart_distributor.distribution_history)
        
        smart_distributor.distribute_leads(sample_lead_objects)
        
        assert len(smart_distributor.distribution_history) == initial_history_length + 1
        
        history_record = smart_distributor.distribution_history[-1]
        assert "timestamp" in history_record
        assert "strategy" in history_record
        assert "total_leads" in history_record
        assert "assignments" in history_record
        assert "user_states" in history_record

    def test_user_profile_skills_initialization(self):
        """Test UserProfile skills initialization."""
        profile = UserProfile(user_id=1, name="Test User")
        assert profile.skills == []
        
        profile_with_skills = UserProfile(
            user_id=1, name="Test User", skills=["python", "sales"]
        )
        assert profile_with_skills.skills == ["python", "sales"]

    def test_lead_tags_initialization(self):
        """Test Lead tags initialization."""
        lead = Lead(lead_id=1, name="Test Lead")
        assert lead.tags == []
        assert lead.required_skills == []
        
        lead_with_tags = Lead(
            lead_id=1, name="Test Lead", tags=["hot", "vip"], required_skills=["sales"]
        )
        assert lead_with_tags.tags == ["hot", "vip"]
        assert lead_with_tags.required_skills == ["sales"]

    def test_distribution_with_priority_users(self):
        """Test distribution with priority-based assignment."""
        distributor = SmartDistributor()
        
        # Add users with different priorities
        users = [
            UserProfile(user_id=1, name="High Priority", current_leads=0, priority=3),
            UserProfile(user_id=2, name="Low Priority", current_leads=0, priority=1),
        ]
        
        for user in users:
            distributor.add_user_profile(user)
        
        leads = [Lead(lead_id=i, name=f"Lead {i}") for i in range(1, 5)]
        assignments = distributor.distribute_leads(leads, DistributionStrategy.ROUND_ROBIN)
        
        # High priority user should get more leads
        assert len(assignments[1]) >= len(assignments[2])

    def test_unsupported_strategy_error(self, smart_distributor, sample_lead_objects):
        """Test error with unsupported strategy."""
        with pytest.raises(ValueError):
            smart_distributor.distribute_leads(
                sample_lead_objects, "unsupported_strategy"
            )

    def test_active_users_filtering(self):
        """Test filtering of active users."""
        distributor = SmartDistributor()
        
        # Add active and inactive users
        distributor.add_user_profile(UserProfile(user_id=1, name="Active User", is_active=True))
        distributor.add_user_profile(UserProfile(user_id=2, name="Inactive User", is_active=False))
        distributor.add_user_profile(UserProfile(user_id=3, name="At Capacity", current_leads=100, max_capacity=100))
        
        active_users = distributor._get_active_users()
        
        assert len(active_users) == 1
        assert active_users[0].user_id == 1