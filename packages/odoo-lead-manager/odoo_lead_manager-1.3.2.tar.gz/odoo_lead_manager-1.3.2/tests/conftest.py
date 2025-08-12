"""
Pytest configuration and fixtures for Odoo Lead Manager tests.

This module provides test fixtures and configuration for the test suite.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, date
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from odoo_lead_manager.client import OdooClient
from odoo_lead_manager.filters import LeadFilter, LeadStatus
from odoo_lead_manager.lead_manager import LeadManager
from odoo_lead_manager.distribution import SmartDistributor, UserProfile, Lead, DistributionStrategy


@pytest.fixture
def mock_odoo_client():
    """Mock Odoo client for testing."""
    client = Mock(spec=OdooClient)
    
    # Mock successful connection
    client.is_connected.return_value = True
    client.uid = 1
    
    # Mock search_read with sample data
    def mock_search_read(model_name, domain=None, fields=None, limit=None, offset=0, order=None):
        if model_name == "res.partner":
            return get_sample_leads()
        elif model_name == "res.users":
            return get_sample_users()
        return []
    
    client.search_read = mock_search_read
    
    # Mock search_count
    def mock_search_count(model_name, domain=None):
        if model_name == "res.partner":
            return len(get_sample_leads())
        return 0
    
    client.search_count = mock_search_count
    
    # Mock write
    def mock_write(model_name, record_ids, values):
        return True
    
    client.write = mock_write
    
    return client


@pytest.fixture
def sample_leads():
    """Sample leads data for testing."""
    return get_sample_leads()


@pytest.fixture
def sample_users():
    """Sample users data for testing."""
    return get_sample_users()


@pytest.fixture
def lead_manager(mock_odoo_client):
    """LeadManager instance with mocked client."""
    return LeadManager(mock_odoo_client)


@pytest.fixture
def smart_distributor():
    """SmartDistributor instance with sample users."""
    distributor = SmartDistributor()
    
    # Add sample users
    users = [
        UserProfile(user_id=1, name="Alice Smith", current_leads=10, expected_percentage=40.0, max_capacity=50),
        UserProfile(user_id=2, name="Bob Johnson", current_leads=15, expected_percentage=30.0, max_capacity=40),
        UserProfile(user_id=3, name="Carol Williams", current_leads=5, expected_percentage=30.0, max_capacity=30),
    ]
    
    for user in users:
        distributor.add_user_profile(user)
    
    return distributor


@pytest.fixture
def sample_lead_objects():
    """Sample Lead objects for distribution testing."""
    return [
        Lead(lead_id=1, name="Lead A", source_id="web", tags=["hot"], priority=3),
        Lead(lead_id=2, name="Lead B", source_id="email", tags=["warm"], priority=2),
        Lead(lead_id=3, name="Lead C", source_id="referral", tags=["cold"], priority=1),
        Lead(lead_id=4, name="Lead D", source_id="web", tags=["hot"], priority=3),
        Lead(lead_id=5, name="Lead E", source_id="social", tags=["warm"], priority=2),
    ]


def get_sample_leads():
    """Generate sample leads data."""
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "create_date": "2024-01-15 10:30:00",
            "write_date": "2024-01-15 10:30:00",
            "source_date": "2024-01-15",
            "status": "new",
            "web_source_id": [1, "Website"],
            "user_id": [1, "Alice Smith"],
            "closer_id": False,
            "open_user_id": [1, "Alice Smith"],
            "company_id": False,
            "street": "123 Main St",
            "city": "New York",
            "zip": "10001",
            "country_id": [1, "United States"],
            "state_id": [1, "New York"],
            "category_id": [],
            "comment": "Interested in product A",
            "opt_out": False,
            "is_company": False,
            "parent_id": False,
            "child_ids": []
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1234567891",
            "create_date": "2024-01-16 09:15:00",
            "write_date": "2024-01-16 14:20:00",
            "source_date": "2024-01-16",
            "status": "in_progress",
            "web_source_id": [2, "Email Campaign"],
            "user_id": [2, "Bob Johnson"],
            "closer_id": [2, "Bob Johnson"],
            "open_user_id": [2, "Bob Johnson"],
            "company_id": [1, "Acme Corp"],
            "street": "456 Oak Ave",
            "city": "Los Angeles",
            "zip": "90001",
            "country_id": [1, "United States"],
            "state_id": [2, "California"],
            "category_id": [[1, "VIP"]],
            "comment": "High value prospect",
            "opt_out": False,
            "is_company": False,
            "parent_id": False,
            "child_ids": []
        },
        {
            "id": 3,
            "name": "Tech Solutions Inc",
            "email": "info@techsolutions.com",
            "phone": "+1234567892",
            "create_date": "2024-01-17 11:00:00",
            "write_date": "2024-01-17 11:00:00",
            "source_date": "2024-01-17",
            "status": "won",
            "web_source_id": [3, "Referral"],
            "user_id": [3, "Carol Williams"],
            "closer_id": [3, "Carol Williams"],
            "open_user_id": [3, "Carol Williams"],
            "company_id": False,
            "street": "789 Business Blvd",
            "city": "Chicago",
            "zip": "60601",
            "country_id": [1, "United States"],
            "state_id": [3, "Illinois"],
            "category_id": [[2, "Enterprise"]],
            "comment": "B2B client",
            "opt_out": False,
            "is_company": True,
            "parent_id": False,
            "child_ids": []
        },
        {
            "id": 4,
            "name": "Mike Johnson",
            "email": "mike.j@example.com",
            "phone": "+1234567893",
            "create_date": "2024-01-18 08:45:00",
            "write_date": "2024-01-18 08:45:00",
            "source_date": "2024-01-18",
            "status": "lost",
            "web_source_id": [1, "Website"],
            "user_id": False,
            "closer_id": False,
            "open_user_id": False,
            "company_id": False,
            "street": "321 Pine St",
            "city": "Houston",
            "zip": "77001",
            "country_id": [1, "United States"],
            "state_id": [4, "Texas"],
            "category_id": [],
            "comment": "Not interested",
            "opt_out": True,
            "is_company": False,
            "parent_id": False,
            "child_ids": []
        },
        {
            "id": 5,
            "name": "Sarah Davis",
            "email": "sarah.d@example.com",
            "phone": "+1234567894",
            "create_date": "2024-01-19 14:30:00",
            "write_date": "2024-01-19 14:30:00",
            "source_date": "2024-01-19",
            "status": "new",
            "web_source_id": [4, "Social Media"],
            "user_id": [1, "Alice Smith"],
            "closer_id": False,
            "open_user_id": [1, "Alice Smith"],
            "company_id": False,
            "street": "555 Elm St",
            "city": "Miami",
            "zip": "33101",
            "country_id": [1, "United States"],
            "state_id": [5, "Florida"],
            "category_id": [[3, "Hot Lead"]],
            "comment": "Follow up needed",
            "opt_out": False,
            "is_company": False,
            "parent_id": False,
            "child_ids": []
        }
    ]


def get_sample_users():
    """Generate sample users data."""
    return [
        {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "login": "alice"},
        {"id": 2, "name": "Bob Johnson", "email": "bob@example.com", "login": "bob"},
        {"id": 3, "name": "Carol Williams", "email": "carol@example.com", "login": "carol"}
    ]