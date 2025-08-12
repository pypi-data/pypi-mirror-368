"""
Lead filtering module for applying various criteria to Odoo leads.

This module provides comprehensive filtering capabilities for leads including:
- Date range filtering based on source_date
- Web source ID tag filtering
- Status filtering
- User assignment filtering (user_id, closer_id, open_user_id)
- Name-based filtering for users
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum
import re
from loguru import logger


class LeadStatus(Enum):
    """Enumeration of common lead statuses."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class LeadFilter:
    """
    Comprehensive lead filtering class for applying multiple criteria.
    
    This class provides a fluent interface for building complex lead queries
    with support for date ranges, source IDs, statuses, and user assignments.
    """
    
    def __init__(self):
        """Initialize a new LeadFilter instance."""
        self._domain = []
        self._model_name = "res.partner"
        self._fields = []
        self._limit = 1000
        self._offset = 0
        self._order = None
    
    def model(self, model_name: str) -> "LeadFilter":
        """
        Set the model name for filtering (default: res.partner).
        
        Args:
            model_name: Name of the Odoo model to filter
            
        Returns:
            Self for method chaining
        """
        self._model_name = model_name
        return self
    
    def fields(self, fields: List[str]) -> "LeadFilter":
        """
        Set the fields to retrieve.
        
        Args:
            fields: List of field names to retrieve
            
        Returns:
            Self for method chaining
        """
        self._fields = fields
        return self
    
    def limit(self, limit: int) -> "LeadFilter":
        """
        Set the maximum number of records to return.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            Self for method chaining
        """
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> "LeadFilter":
        """
        Set the number of records to skip.
        
        Args:
            offset: Number of records to skip
            
        Returns:
            Self for method chaining
        """
        self._offset = offset
        return self
    
    def order(self, order: str) -> "LeadFilter":
        """
        Set the sort order for results.
        
        Args:
            order: Sort order string (e.g., 'create_date desc')
            
        Returns:
            Self for method chaining
        """
        self._order = order
        return self
    
    def by_date_range(
        self,
        start_date: Optional[Union[datetime, date, str]] = None,
        end_date: Optional[Union[datetime, date, str]] = None,
        field_name: str = "date"
    ) -> "LeadFilter":
        """
        Filter leads by date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            field_name: Date field name to filter on
            
        Returns:
            Self for method chaining
        """
        if start_date:
            start_str = self._format_date(start_date)
            self._domain.append([field_name, ">=", start_str])
        
        if end_date:
            end_str = self._format_date(end_date)
            self._domain.append([field_name, "<=", end_str])
            
        return self
    
    def by_web_source_ids(self, source_ids: Union[List[str], List[int], str, int]) -> "LeadFilter":
        """
        Filter leads by category/source tags.
        
        Args:
            source_ids: Single category ID or list of category IDs
            
        Returns:
            Self for method chaining
        """
        if isinstance(source_ids, (str, int)):
            source_ids = [source_ids]
        
        if source_ids:
            # Use category_id which corresponds to partner tags/categories
            self._domain.append(["category_id", "in", source_ids])
            
        return self
    
    def by_status(self, statuses: Union[List[str], str, LeadStatus]) -> "LeadFilter":
        """
        Filter leads by status.
        
        Args:
            statuses: Single status or list of statuses
            
        Returns:
            Self for method chaining
        """
        if isinstance(statuses, (str, LeadStatus)):
            statuses = [statuses]
        
        # Convert enum values to strings
        status_strings = []
        for status in statuses:
            if isinstance(status, LeadStatus):
                status_strings.append(status.value)
            else:
                status_strings.append(str(status))
        
        if status_strings:
            self._domain.append(["status", "in", status_strings])
            
        return self
    
    def by_type(self, lead_type: str) -> "LeadFilter":
        """
        Filter leads by type (lead or opportunity).
        
        Args:
            lead_type: Type to filter by ('lead' or 'opportunity')
            
        Returns:
            Self for method chaining
        """
        self._domain.append(["type", "=", lead_type])
        return self
    
    def by_user_assignments(
        self,
        user_ids: Optional[Union[List[int], int]] = None,
        closer_ids: Optional[Union[List[int], int]] = None,
        open_user_ids: Optional[Union[List[int], int]] = None,
        user_names: Optional[Union[List[str], str]] = None,
        closer_names: Optional[Union[List[str], str]] = None,
        open_user_names: Optional[Union[List[str], str]] = None,
        exact: bool = False
    ) -> "LeadFilter":
        """
        Filter leads by user assignments using IDs or names.
        
        Args:
            user_ids: User IDs assigned to leads
            closer_ids: Closer IDs assigned to leads
            open_user_ids: Open user IDs assigned to leads
            user_names: User names to match against assigned users
            closer_names: User names to match against closers
            open_user_names: User names to match against open users
            exact: Whether to do exact name matching (default: False for backward compatibility)
            
        Returns:
            Self for method chaining
        """
        # Handle user assignments by ID
        if user_ids:
            if isinstance(user_ids, int):
                user_ids = [user_ids]
            self._domain.append(["user_id", "in", user_ids])
        
        if closer_ids:
            if isinstance(closer_ids, int):
                closer_ids = [closer_ids]
            self._domain.append(["closer_id", "in", closer_ids])
        
        if open_user_ids:
            if isinstance(open_user_ids, int):
                open_user_ids = [open_user_ids]
            self._domain.append(["open_user_id", "in", open_user_ids])
        
        # Handle user assignments by name
        if user_names:
            self._add_name_filters(user_names, "user_id", exact)
        
        if closer_names:
            self._add_name_filters(closer_names, "closer_id", exact)
        
        if open_user_names:
            self._add_name_filters(open_user_names, "open_user_id", exact)
            
        return self
    
    def exclude_users(
        self,
        user_names: Optional[Union[List[str], str]] = None,
        exact: bool = True
    ) -> "LeadFilter":
        """
        Exclude leads assigned to specific users by name.
        
        Args:
            user_names: User names to exclude from results
            exact: Whether to do exact name matching (default: True for exclusions)
            
        Returns:
            Self for method chaining
        """
        if user_names:
            if isinstance(user_names, str):
                user_names = [user_names]
            
            # Add exclusion filters for user assignments
            for name in user_names:
                name = name.strip()
                if exact:
                    # Exact name matching for exclusion
                    self._domain.append(["user_id.name", "!=", name])
                else:
                    # Partial name matching for exclusion
                    self._domain.append(["user_id.name", "not ilike", f"%{name}%"])
        
        return self
    
    def by_customer_name(self, name_pattern: str, exact: bool = False) -> "LeadFilter":
        """
        Filter leads by customer name pattern.
        
        Args:
            name_pattern: Name to search for
            exact: Whether to do exact match or partial match
            
        Returns:
            Self for method chaining
        """
        if exact:
            self._domain.append(["name", "=", name_pattern])
        else:
            self._domain.append(["name", "ilike", f"%{name_pattern}%"])
            
        return self
    
    def by_email(self, email_pattern: str, exact: bool = False) -> "LeadFilter":
        """
        Filter leads by email pattern.
        
        Args:
            email_pattern: Email to search for
            exact: Whether to do exact match or partial match
            
        Returns:
            Self for method chaining
        """
        if exact:
            self._domain.append(["email", "=", email_pattern])
        else:
            self._domain.append(["email", "ilike", f"%{email_pattern}%"])
            
        return self
    
    def by_phone(self, phone_pattern: str, exact: bool = False) -> "LeadFilter":
        """
        Filter leads by phone pattern.
        
        Args:
            phone_pattern: Phone to search for
            exact: Whether to do exact match or partial match
            
        Returns:
            Self for method chaining
        """
        if exact:
            self._domain.append(["phone", "=", phone_pattern])
        else:
            self._domain.append(["phone", "ilike", f"%{phone_pattern}%"])
            
        return self
    
    def by_tags(self, tags: Union[List[str], str]) -> "LeadFilter":
        """
        Filter leads by tags.
        
        Args:
            tags: Single tag or list of tags
            
        Returns:
            Self for method chaining
        """
        if isinstance(tags, str):
            tags = [tags]
        
        if tags:
            self._domain.append(["category_id.name", "in", tags])
            
        return self
    
    def custom_filter(self, domain: List[List[Any]]) -> "LeadFilter":
        """
        Add custom domain filter.
        
        Args:
            domain: Custom Odoo domain
            
        Returns:
            Self for method chaining
        """
        self._domain.extend(domain)
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the final filter configuration.
        
        Returns:
            Dictionary with all filter parameters
        """
        return {
            "model_name": self._model_name,
            "domain": self._domain,
            "fields": self._fields,
            "limit": self._limit,
            "offset": self._offset,
            "order": self._order
        }
    
    def clear(self) -> "LeadFilter":
        """
        Clear all filters.
        
        Returns:
            Self for method chaining
        """
        self._domain = []
        return self
    
    def copy(self) -> "LeadFilter":
        """
        Create a copy of the current filter.
        
        Returns:
            New LeadFilter instance with same configuration
        """
        new_filter = LeadFilter()
        new_filter._model_name = self._model_name
        new_filter._domain = self._domain.copy()
        new_filter._fields = self._fields.copy()
        new_filter._limit = self._limit
        new_filter._offset = self._offset
        new_filter._order = self._order
        return new_filter
    
    def _format_date(self, date_value: Union[datetime, date, str]) -> str:
        """Format date value to Odoo-compatible string."""
        if isinstance(date_value, (datetime, date)):
            return date_value.strftime("%Y-%m-%d")
        return str(date_value)
    
    def _add_name_filters(self, names: Union[List[str], str], field: str, exact: bool = False) -> None:
        """Add name-based filters for user assignments."""
        if isinstance(names, str):
            names = [names]
        
        # Create OR condition for multiple names
        name_conditions = []
        for name in names:
            if exact:
                # Exact name matching
                name_conditions.append([f"{field}.name", "=", name.strip()])
            else:
                # Flexible partial matching (existing behavior)
                name_parts = re.split(r'\s+', name.strip())
                if len(name_parts) > 1:
                    # Multi-part name - search in both first and last name
                    name_conditions.extend([
                        [f"{field}.name", "ilike", f"%{name}%"],
                        [f"{field}.first_name", "ilike", f"%{name_parts[0]}%"],
                        [f"{field}.last_name", "ilike", f"%{name_parts[-1]}%"]
                    ])
                else:
                    # Single name - search in full name
                    name_conditions.append([f"{field}.name", "ilike", f"%{name}%"])
        
        # Add OR condition if we have multiple name patterns
        if name_conditions:
            if len(name_conditions) == 1:
                self._domain.extend(name_conditions)
            else:
                # Use OR operator for name matching
                or_condition = "|" * (len(name_conditions) - 1)
                self._domain.append(or_condition)
                self._domain.extend(name_conditions)
    
    def __repr__(self) -> str:
        """String representation of the filter."""
        return f"LeadFilter(domain={self._domain}, fields={self._fields})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        filters = []
        for condition in self._domain:
            if isinstance(condition, str):
                filters.append(condition)
            else:
                field, operator, value = condition
                filters.append(f"{field} {operator} {value}")
        
        return f"LeadFilter: {' AND '.join(filters) if filters else 'No filters'}"