"""
Tests for LeadFilter class.
"""

import pytest
from datetime import datetime, date
from odoo_lead_manager.filters import LeadFilter, LeadStatus


class TestLeadFilter:
    """Test cases for LeadFilter."""
    
    def test_initialization(self):
        """Test LeadFilter initialization."""
        filter_obj = LeadFilter()
        
        assert filter_obj._domain == []
        assert filter_obj._model_name == "res.partner"
        assert filter_obj._fields == []
        assert filter_obj._limit is None
        assert filter_obj._offset == 0
        assert filter_obj._order is None
    
    def test_model_method(self):
        """Test setting model name."""
        filter_obj = LeadFilter()
        result = filter_obj.model("crm.lead")
        
        assert result is filter_obj  # Method chaining
        assert filter_obj._model_name == "crm.lead"
    
    def test_fields_method(self):
        """Test setting fields."""
        filter_obj = LeadFilter()
        fields = ["id", "name", "email"]
        result = filter_obj.fields(fields)
        
        assert result is filter_obj
        assert filter_obj._fields == fields
    
    def test_limit_method(self):
        """Test setting limit."""
        filter_obj = LeadFilter()
        result = filter_obj.limit(100)
        
        assert result is filter_obj
        assert filter_obj._limit == 100
    
    def test_offset_method(self):
        """Test setting offset."""
        filter_obj = LeadFilter()
        result = filter_obj.offset(50)
        
        assert result is filter_obj
        assert filter_obj._offset == 50
    
    def test_order_method(self):
        """Test setting order."""
        filter_obj = LeadFilter()
        result = filter_obj.order("create_date desc")
        
        assert result is filter_obj
        assert filter_obj._order == "create_date desc"
    
    def test_by_date_range_both_dates(self):
        """Test date range filtering with both start and end dates."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        filter_obj = LeadFilter().by_date_range(start_date, end_date)
        
        expected_domain = [
            ["source_date", ">=", "2024-01-01"],
            ["source_date", "<=", "2024-01-31"]
        ]
        
        assert filter_obj._domain == expected_domain
    
    def test_by_date_range_only_start(self):
        """Test date range filtering with only start date."""
        start_date = date(2024, 1, 1)
        
        filter_obj = LeadFilter().by_date_range(start_date=start_date)
        
        expected_domain = [["source_date", ">=", "2024-01-01"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_date_range_only_end(self):
        """Test date range filtering with only end date."""
        end_date = "2024-01-31"
        
        filter_obj = LeadFilter().by_date_range(end_date=end_date)
        
        expected_domain = [["source_date", "<=", "2024-01-31"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_date_range_custom_field(self):
        """Test date range filtering with custom field name."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        filter_obj = LeadFilter().by_date_range(
            start_date=start_date,
            end_date=end_date,
            field_name="create_date"
        )
        
        expected_domain = [
            ["create_date", ">=", "2024-01-01"],
            ["create_date", "<=", "2024-01-31"]
        ]
        
        assert filter_obj._domain == expected_domain
    
    def test_by_web_source_ids_single(self):
        """Test filtering by single web source ID."""
        filter_obj = LeadFilter().by_web_source_ids("web")
        
        expected_domain = [["web_source_id", "in", ["web"]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_web_source_ids_list(self):
        """Test filtering by multiple web source IDs."""
        source_ids = ["web", "email", "social"]
        filter_obj = LeadFilter().by_web_source_ids(source_ids)
        
        expected_domain = [["web_source_id", "in", source_ids]]
        assert filter_obj._domain == expected_domain
    
    def test_by_web_source_ids_int(self):
        """Test filtering by integer web source ID."""
        filter_obj = LeadFilter().by_web_source_ids(123)
        
        expected_domain = [["web_source_id", "in", [123]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_status_single_string(self):
        """Test filtering by single status string."""
        filter_obj = LeadFilter().by_status("new")
        
        expected_domain = [["status", "in", ["new"]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_status_multiple_strings(self):
        """Test filtering by multiple status strings."""
        statuses = ["new", "in_progress", "won"]
        filter_obj = LeadFilter().by_status(statuses)
        
        expected_domain = [["status", "in", statuses]]
        assert filter_obj._domain == expected_domain
    
    def test_by_status_enum(self):
        """Test filtering by LeadStatus enum."""
        filter_obj = LeadFilter().by_status(LeadStatus.NEW)
        
        expected_domain = [["status", "in", ["new"]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_status_multiple_enums(self):
        """Test filtering by multiple LeadStatus enums."""
        statuses = [LeadStatus.NEW, LeadStatus.WON]
        filter_obj = LeadFilter().by_status(statuses)
        
        expected_domain = [["status", "in", ["new", "won"]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_user_assignments_user_ids(self):
        """Test filtering by user IDs."""
        filter_obj = LeadFilter().by_user_assignments(user_ids=[1, 2, 3])
        
        expected_domain = [["user_id", "in", [1, 2, 3]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_user_assignments_single_user_id(self):
        """Test filtering by single user ID."""
        filter_obj = LeadFilter().by_user_assignments(user_ids=1)
        
        expected_domain = [["user_id", "in", [1]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_user_assignments_closer_ids(self):
        """Test filtering by closer IDs."""
        filter_obj = LeadFilter().by_user_assignments(closer_ids=[1, 2])
        
        expected_domain = [["closer_id", "in", [1, 2]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_user_assignments_open_user_ids(self):
        """Test filtering by open user IDs."""
        filter_obj = LeadFilter().by_user_assignments(open_user_ids=[1, 2])
        
        expected_domain = [["open_user_id", "in", [1, 2]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_user_assignments_user_names(self):
        """Test filtering by user names."""
        filter_obj = LeadFilter().by_user_assignments(user_names="Alice Smith")
        
        # Should contain name-based filtering
        assert any("user_id.name" in str(condition) for condition in filter_obj._domain)
    
    def test_by_user_assignments_multiple_names(self):
        """Test filtering by multiple user names."""
        names = ["Alice Smith", "Bob Johnson"]
        filter_obj = LeadFilter().by_user_assignments(user_names=names)
        
        # Should contain multiple name-based conditions
        domain_str = str(filter_obj._domain)
        assert "Alice Smith" in domain_str
        assert "Bob Johnson" in domain_str
    
    def test_by_customer_name_exact(self):
        """Test filtering by exact customer name."""
        filter_obj = LeadFilter().by_customer_name("John Doe", exact=True)
        
        expected_domain = [["name", "=", "John Doe"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_customer_name_partial(self):
        """Test filtering by partial customer name."""
        filter_obj = LeadFilter().by_customer_name("John")
        
        expected_domain = [["name", "ilike", "%John%"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_email_exact(self):
        """Test filtering by exact email."""
        filter_obj = LeadFilter().by_email("test@example.com", exact=True)
        
        expected_domain = [["email", "=", "test@example.com"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_email_partial(self):
        """Test filtering by partial email."""
        filter_obj = LeadFilter().by_email("@example.com")
        
        expected_domain = [["email", "ilike", "%@example.com%"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_phone_exact(self):
        """Test filtering by exact phone."""
        filter_obj = LeadFilter().by_phone("+1234567890", exact=True)
        
        expected_domain = [["phone", "=", "+1234567890"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_phone_partial(self):
        """Test filtering by partial phone."""
        filter_obj = LeadFilter().by_phone("123456")
        
        expected_domain = [["phone", "ilike", "%123456%"]]
        assert filter_obj._domain == expected_domain
    
    def test_by_tags_single(self):
        """Test filtering by single tag."""
        filter_obj = LeadFilter().by_tags("VIP")
        
        expected_domain = [["category_id.name", "in", ["VIP"]]]
        assert filter_obj._domain == expected_domain
    
    def test_by_tags_multiple(self):
        """Test filtering by multiple tags."""
        tags = ["VIP", "Hot Lead", "Enterprise"]
        filter_obj = LeadFilter().by_tags(tags)
        
        expected_domain = [["category_id.name", "in", tags]]
        assert filter_obj._domain == expected_domain
    
    def test_custom_filter(self):
        """Test adding custom domain filter."""
        custom_domain = [["email", "!=", False], ["phone", "!=", False]]
        filter_obj = LeadFilter().custom_filter(custom_domain)
        
        assert custom_domain[0] in filter_obj._domain
        assert custom_domain[1] in filter_obj._domain
    
    def test_chained_filters(self):
        """Test chaining multiple filters."""
        filter_obj = LeadFilter() \
            .by_date_range(datetime(2024, 1, 1), datetime(2024, 1, 31)) \
            .by_status("new") \
            .by_web_source_ids("web") \
            .limit(50)
        
        expected_domain = [
            ["source_date", ">=", "2024-01-01"],
            ["source_date", "<=", "2024-01-31"],
            ["status", "in", ["new"]],
            ["web_source_id", "in", ["web"]]
        ]
        
        assert filter_obj._domain == expected_domain
        assert filter_obj._limit == 50
    
    def test_build(self):
        """Test building final filter configuration."""
        filter_obj = LeadFilter() \
            .model("crm.lead") \
            .fields(["id", "name"]) \
            .by_status("new") \
            .limit(100) \
            .offset(50) \
            .order("create_date desc")
        
        config = filter_obj.build()
        
        expected_config = {
            "model_name": "crm.lead",
            "domain": [["status", "in", ["new"]]],
            "fields": ["id", "name"],
            "limit": 100,
            "offset": 50,
            "order": "create_date desc"
        }
        
        assert config == expected_config
    
    def test_clear(self):
        """Test clearing all filters."""
        filter_obj = LeadFilter() \
            .by_status("new") \
            .by_date_range(datetime(2024, 1, 1)) \
            .clear()
        
        assert filter_obj._domain == []
    
    def test_copy(self):
        """Test creating a copy of the filter."""
        original = LeadFilter() \
            .by_status("new") \
            .limit(50) \
            .fields(["id", "name"])
        
        copy = original.copy()
        
        # Should have same values
        assert copy._model_name == original._model_name
        assert copy._domain == original._domain
        assert copy._fields == original._fields
        assert copy._limit == original._limit
        
        # But should be independent
        copy.by_status("won")
        assert len(original._domain) != len(copy._domain)
    
    def test_empty_filter(self):
        """Test empty filter configuration."""
        filter_obj = LeadFilter()
        config = filter_obj.build()
        
        expected_config = {
            "model_name": "res.partner",
            "domain": [],
            "fields": [],
            "limit": None,
            "offset": 0,
            "order": None
        }
        
        assert config == expected_config
    
    def test_repr(self):
        """Test string representation."""
        filter_obj = LeadFilter().by_status("new")
        
        repr_str = repr(filter_obj)
        assert "LeadFilter" in repr_str
        assert "domain" in repr_str
    
    def test_str(self):
        """Test human-readable string representation."""
        filter_obj = LeadFilter().by_status("new").by_date_range(date(2024, 1, 1))
        
        str_repr = str(filter_obj)
        assert "LeadFilter:" in str_repr
        assert "new" in str_repr