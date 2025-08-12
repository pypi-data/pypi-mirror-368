"""
Tests for LeadManager class.
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock
from odoo_lead_manager.lead_manager import LeadManager
from odoo_lead_manager.filters import LeadFilter


class TestLeadManager:
    """Test cases for LeadManager."""
    
    def test_initialization(self, mock_odoo_client):
        """Test LeadManager initialization."""
        manager = LeadManager(mock_odoo_client)
        
        assert manager.client == mock_odoo_client
        assert manager._default_fields is not None
        assert "id" in manager._default_fields
        assert "name" in manager._default_fields
    
    def test_get_leads_basic(self, lead_manager, sample_leads):
        """Test basic lead retrieval."""
        leads = lead_manager.get_leads()
        
        assert len(leads) == 5
        assert leads[0]["id"] == 1
        assert leads[0]["name"] == "John Doe"
    
    def test_get_leads_with_filter(self, lead_manager):
        """Test getting leads with LeadFilter."""
        filter_obj = LeadFilter().by_status("new")
        leads = lead_manager.get_leads(filter_obj)
        
        assert len(leads) == 3  # John, Sarah, and Mike have status 'new' or 'lost'
    
    def test_get_leads_with_fields(self, lead_manager):
        """Test getting leads with specific fields."""
        fields = ["id", "name", "email"]
        leads = lead_manager.get_leads(fields=fields)
        
        assert len(leads) == 5
        for lead in leads:
            assert set(lead.keys()).issubset(set(fields + ["id"]))  # ID is always included
    
    def test_get_leads_with_limit(self, lead_manager):
        """Test getting leads with limit."""
        leads = lead_manager.get_leads(limit=3)
        
        assert len(leads) == 3
    
    def test_get_leads_with_offset(self, lead_manager):
        """Test getting leads with offset."""
        leads = lead_manager.get_leads(offset=2)
        
        assert len(leads) == 3  # 5 total - 2 offset = 3
    
    def test_get_leads_by_date_range(self, lead_manager):
        """Test getting leads by date range."""
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 17)
        
        leads = lead_manager.get_leads_by_date_range(start_date, end_date)
        
        assert len(leads) == 3  # John, Jane, Tech Solutions
    
    def test_get_leads_by_source(self, lead_manager):
        """Test getting leads by web source ID."""
        leads = lead_manager.get_leads_by_source("Website")
        
        assert len(leads) == 2  # John and Mike from Website
    
    def test_get_leads_by_status(self, lead_manager):
        """Test getting leads by status."""
        leads = lead_manager.get_leads_by_status("new")
        
        assert len(leads) == 2  # John and Sarah
    
    def test_get_leads_by_users_ids(self, lead_manager):
        """Test getting leads by user IDs."""
        leads = lead_manager.get_leads_by_users(user_ids=[1, 2])
        
        assert len(leads) == 4  # All except Mike (unassigned)
    
    def test_get_leads_by_users_names(self, lead_manager):
        """Test getting leads by user names."""
        leads = lead_manager.get_leads_by_users(user_names=["Alice Smith"])
        
        assert len(leads) == 2  # John and Sarah assigned to Alice
    
    def test_count_leads(self, lead_manager):
        """Test counting leads."""
        count = lead_manager.count_leads()
        
        assert count == 5
    
    def test_count_leads_with_filter(self, lead_manager):
        """Test counting leads with filter."""
        filter_obj = LeadFilter().by_status("new")
        count = lead_manager.count_leads(filter_obj)
        
        assert count == 2  # John and Sarah
    
    def test_get_lead_summary(self, lead_manager, sample_leads):
        """Test getting comprehensive lead summary."""
        summary = lead_manager.get_lead_summary()
        
        assert summary["total_leads"] == 5
        assert len(summary["leads"]) == 5
        assert "statistics" in summary
        assert "user_assignments" in summary
        assert "source_distribution" in summary
        assert "status_distribution" in summary
        assert "date_range" in summary
        assert "geographic_distribution" in summary
    
    def test_get_lead_summary_empty(self, lead_manager):
        """Test getting lead summary with no leads."""
        # Mock empty result
        lead_manager.client.search_read.return_value = []
        
        summary = lead_manager.get_lead_summary()
        
        assert summary["total_leads"] == 0
        assert summary["leads"] == []
        assert summary["statistics"]["total_leads"] == 0
    
    def test_update_lead_assignments_single(self, lead_manager):
        """Test updating assignments for single lead."""
        result = lead_manager.update_lead_assignments(1, user_id=2)
        
        assert result is True
        lead_manager.client.write.assert_called_once_with(
            "res.partner", [1], {"user_id": 2}
        )
    
    def test_update_lead_assignments_multiple(self, lead_manager):
        """Test updating assignments for multiple leads."""
        lead_ids = [1, 2, 3]
        result = lead_manager.update_lead_assignments(
            lead_ids, user_id=2, closer_id=3
        )
        
        assert result is True
        lead_manager.client.write.assert_called_once_with(
            "res.partner", lead_ids, {"user_id": 2, "closer_id": 3}
        )
    
    def test_update_lead_assignments_no_updates(self, lead_manager):
        """Test updating assignments with no updates provided."""
        result = lead_manager.update_lead_assignments(1)
        
        assert result is False
        lead_manager.client.write.assert_not_called()
    
    def test_get_user_lead_counts(self, lead_manager):
        """Test getting user lead counts."""
        lead_manager.client.search_read.return_value = [
            {"id": 1, "user_id": [1, "Alice Smith"]},
            {"id": 2, "user_id": [2, "Bob Johnson"]},
            {"id": 3, "user_id": [1, "Alice Smith"]},
            {"id": 4, "user_id": False},
            {"id": 5, "user_id": [3, "Carol Williams"]},
        ]
        
        counts = lead_manager.get_user_lead_counts()
        
        assert counts == {1: 2, 2: 1, 3: 1}
    
    def test_get_user_lead_counts_specific_users(self, lead_manager):
        """Test getting lead counts for specific users."""
        lead_manager.client.search_read.return_value = [
            {"id": 1, "user_id": [1, "Alice Smith"]},
            {"id": 2, "user_id": [2, "Bob Johnson"]},
            {"id": 3, "user_id": [1, "Alice Smith"]},
        ]
        
        counts = lead_manager.get_user_lead_counts(user_ids=[1, 2])
        
        assert counts == {1: 2, 2: 1}
    
    def test_export_to_dataframe(self, lead_manager):
        """Test exporting leads to DataFrame."""
        df = lead_manager.export_to_dataframe()
        
        assert len(df) == 5
        assert "id" in df.columns
        assert "name" in df.columns
        assert df.iloc[0]["name"] == "John Doe"
    
    def test_export_to_dataframe_with_filter(self, lead_manager):
        """Test exporting filtered leads to DataFrame."""
        filter_obj = LeadFilter().by_status("new")
        df = lead_manager.export_to_dataframe(filter_obj)
        
        assert len(df) > 0
        assert all(df["status"] == "new")
    
    def test_get_leads_complex_filtering(self, lead_manager):
        """Test complex filtering scenarios."""
        # Test multiple criteria combined
        filter_obj = LeadFilter() \
            .by_date_range(date(2024, 1, 15), date(2024, 1, 18)) \
            .by_status(["new", "in_progress"]) \
            .by_web_source_ids(["Website", "Email Campaign"]) \
            .by_user_assignments(user_names=["Alice Smith", "Bob Johnson"]) \
            .limit(10) \
            .order("create_date desc")
        
        leads = lead_manager.get_leads(filter_obj)
        
        assert len(leads) > 0
        assert len(leads) <= 10
    
    def test_get_leads_error_handling(self, lead_manager):
        """Test error handling during lead retrieval."""
        lead_manager.client.search_read.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            lead_manager.get_leads()
    
    def test_count_leads_error_handling(self, lead_manager):
        """Test error handling during lead counting."""
        lead_manager.client.search_count.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            lead_manager.count_leads()
    
    def test_quick_filter_parameters(self, lead_manager):
        """Test quick filter parameters."""
        leads = lead_manager.get_leads(
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17),
            statuses="new",
            source_ids="Website",
            user_ids=[1, 2],
            limit=5
        )
        
        assert len(leads) <= 5
    
    def test_statistics_calculation(self, lead_manager):
        """Test statistics calculation in lead summary."""
        summary = lead_manager.get_lead_summary()
        
        stats = summary["statistics"]
        
        assert stats["total_leads"] == 5
        assert stats["leads_with_email"] >= 0
        assert stats["assigned_leads"] >= 0
        assert stats["unassigned_leads"] >= 0
        assert "unique_emails" in stats
        assert "unique_phones" in stats