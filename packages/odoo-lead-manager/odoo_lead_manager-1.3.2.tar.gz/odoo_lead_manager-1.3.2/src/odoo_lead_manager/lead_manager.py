"""
Lead Manager module for comprehensive lead management operations.

This module provides high-level operations for fetching, filtering, and managing leads
from Odoo's res.partner model with support for various filtering criteria and
lead characteristics analysis.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
import pandas as pd
from loguru import logger

from .client import OdooClient
from .filters import LeadFilter


class LeadManager:
    """
    High-level lead management interface for Odoo leads.
    
    This class provides comprehensive methods for:
    - Fetching leads with various criteria
    - Analyzing lead characteristics
    - Managing lead assignments
    - Generating lead summaries
    """
    
    def __init__(self, client: OdooClient):
        """
        Initialize LeadManager with an OdooClient instance.
        
        Args:
            client: Configured OdooClient instance
        """
        self.client = client
        self._default_fields = [
            "id",
            "web_source_id",
            "create_date",
            "source_date",
            "campaign_id",
            "source_id",
            "medium_id",
            "term_id",
            "content_id",
            "team_id",
            "partner_name",
            "contact_name",
            "partner_id",
            "stage_id",
            "closer_id",
            "open_user_id",
            "user_id",
            "status",
            "is_mobile1",
            "phone",
            "mobile",
            "email_from",
            "is_mobile2",
            "activity_date_deadline",
            "tag_ids",
            "is_email_valid",
            "street",
            "street2",
            "city",
            "state_id",
            "zip",
            "country_id",
            "status_date",
            "company_id"
        ]
    
    def get_leads(
        self,
        filter_obj: Optional[LeadFilter] = None,
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads based on filter criteria.
        
        Args:
            filter_obj: LeadFilter instance with criteria
            fields: Specific fields to retrieve
            **kwargs: Additional filter parameters for quick filtering
            
        Returns:
            List of lead dictionaries
        """
        if filter_obj is None:
            filter_obj = LeadFilter()
        
        # Handle quick filter parameters
        if kwargs:
            filter_obj = self._apply_quick_filters(filter_obj, **kwargs)
        
        # Set fields if provided
        if fields:
            filter_obj.fields(fields)
        elif not filter_obj._fields:
            filter_obj.fields(self._default_fields)
        
        # Build and execute query
        filter_config = filter_obj.build()
        
        try:
            leads = self.client.search_read(
                model_name=filter_config["model_name"],
                domain=filter_config["domain"],
                fields=filter_config["fields"],
                limit=filter_config["limit"],
                offset=filter_config["offset"],
                order=filter_config["order"]
            )
            
            logger.info(f"Retrieved {len(leads)} leads")
            return leads
            
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            raise
    
    def get_leads_by_date_range(
        self,
        start_date: Optional[Union[datetime, date, str]] = None,
        end_date: Optional[Union[datetime, date, str]] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads within a specific date range.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            fields: Specific fields to retrieve
            
        Returns:
            List of lead dictionaries
        """
        filter_obj = LeadFilter().by_date_range(start_date, end_date)
        return self.get_leads(filter_obj, fields)
    
    def get_leads_by_source(
        self,
        source_ids: Union[List[str], List[int], str, int],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads by web source ID.
        
        Args:
            source_ids: Source ID(s) to filter by
            fields: Specific fields to retrieve
            
        Returns:
            List of lead dictionaries
        """
        filter_obj = LeadFilter().by_web_source_ids(source_ids)
        return self.get_leads(filter_obj, fields)
    
    def get_leads_by_status(
        self,
        statuses: Union[List[str], str],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads by status.
        
        Args:
            statuses: Status(es) to filter by
            fields: Specific fields to retrieve
            
        Returns:
            List of lead dictionaries
        """
        filter_obj = LeadFilter().by_status(statuses)
        return self.get_leads(filter_obj, fields)
    
    def get_leads_by_users(
        self,
        user_ids: Optional[Union[List[int], int]] = None,
        user_names: Optional[Union[List[str], str]] = None,
        closer_ids: Optional[Union[List[int], int]] = None,
        closer_names: Optional[Union[List[str], str]] = None,
        open_user_ids: Optional[Union[List[int], int]] = None,
        open_user_names: Optional[Union[List[str], str]] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads by user assignments.
        
        Args:
            user_ids: User ID(s) assigned to leads
            user_names: User name(s) to match against assigned users
            closer_ids: Closer ID(s) assigned to leads
            closer_names: Closer name(s) to match against closers
            open_user_ids: Open user ID(s) assigned to leads
            open_user_names: Open user name(s) to match against open users
            fields: Specific fields to retrieve
            
        Returns:
            List of lead dictionaries
        """
        filter_obj = LeadFilter().by_user_assignments(
            user_ids=user_ids,
            user_names=user_names,
            closer_ids=closer_ids,
            closer_names=closer_names,
            open_user_ids=open_user_ids,
            open_user_names=open_user_names
        )
        return self.get_leads(filter_obj, fields)
    
    def count_leads(self, filter_obj: Optional[LeadFilter] = None, **kwargs) -> int:
        """
        Count leads matching filter criteria.
        
        Args:
            filter_obj: LeadFilter instance with criteria
            **kwargs: Additional filter parameters
            
        Returns:
            Number of matching leads
        """
        if filter_obj is None:
            filter_obj = LeadFilter()
        
        if kwargs:
            filter_obj = self._apply_quick_filters(filter_obj, **kwargs)
        
        # Ensure we're using crm.lead model for counting
        filter_obj.model("crm.lead")
        filter_config = filter_obj.build()
        
        try:
            return self.client.search_count(
                model_name=filter_config["model_name"],
                domain=filter_config["domain"]
            )
        except Exception as e:
            logger.error(f"Error counting leads: {e}")
            raise
    
    def get_lead_summary(self, filter_obj: Optional[LeadFilter] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate comprehensive summary of lead characteristics.
        
        Args:
            filter_obj: LeadFilter instance with criteria
            **kwargs: Additional filter parameters
            
        Returns:
            Dictionary with lead summary statistics
        """
        leads = self.get_leads(filter_obj, **kwargs)
        
        if not leads:
            return {
                "total_leads": 0,
                "leads": [],
                "statistics": {},
                "user_assignments": {},
                "source_distribution": {},
                "status_distribution": {},
                "date_range": {},
                "geographic_distribution": {}
            }
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(leads)
        
        summary = {
            "total_leads": len(leads),
            "leads": leads,
            "statistics": self._calculate_statistics(df),
            "user_assignments": self._get_user_assignments(df),
            "source_distribution": self._get_source_distribution(df),
            "status_distribution": self._get_status_distribution(df),
            "date_range": self._get_date_range(df),
            "geographic_distribution": self._get_geographic_distribution(df)
        }
        
        return summary
    
    def update_lead_assignments(
        self,
        lead_ids: Union[List[int], int],
        user_id: Optional[int] = None,
        closer_id: Optional[int] = None,
        open_user_id: Optional[int] = None,
        status: Optional[str] = None,
        model: str = "res.partner",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Update lead assignments and status.
        
        Args:
            lead_ids: Lead ID(s) to update
            user_id: New user ID for assignment
            closer_id: New closer ID for assignment
            open_user_id: New open user ID for assignment
            status: New lead status
            model: Odoo model to update (default: res.partner, use crm.lead for leads)
            
        Returns:
            Dictionary with update results:
            {
                "success": bool,          # True if any updates succeeded
                "updated_count": int,     # Number of successfully updated records
                "non_existent": List[int], # List of non-existent lead IDs
                "errors": List[Dict]      # List of update errors {lead_id, error}
            }
        """
        if isinstance(lead_ids, int):
            lead_ids = [lead_ids]
        
        update_values = {}
        if user_id is not None:
            update_values["user_id"] = user_id
        if closer_id is not None:
            update_values["closer_id"] = closer_id
        if open_user_id is not None:
            update_values["open_user_id"] = open_user_id
        if status is not None:
            update_values["status"] = status
        
        if not update_values:
            logger.warning("No assignment updates provided")
            return {
                "success": False,
                "updated_count": 0,
                "non_existent": [],
                "errors": []
            }
        
        try:
            # Verify which lead IDs exist
            existing_leads = self.client.search_read(
                model, 
                domain=[("id", "in", lead_ids)], 
                fields=["id"]
            )
            existing_ids = [lead["id"] for lead in existing_leads]
            non_existent = sorted(set(lead_ids) - set(existing_ids))
            
            # Skip non-existent IDs and process only valid ones
            valid_lead_ids = [lid for lid in lead_ids if lid in existing_ids]
            
            if not valid_lead_ids:
                logger.warning(f"No valid lead IDs found in {model}")
                return {
                    "success": False,
                    "updated_count": 0,
                    "non_existent": non_existent,
                    "errors": []
                }
            
            # Update records individually to avoid singleton issues
            updated_count = 0
            update_errors = []
            
            # Progress tracking
            total_to_update = len(valid_lead_ids)
            progress_interval = max(100, total_to_update // 20)  # Report every 100 leads or 5% of total
            
            for i, lead_id in enumerate(valid_lead_ids, 1):
                try:
                    self.client.write(model, [lead_id], update_values)
                    updated_count += 1
                    
                    # Progress reporting
                    if progress_callback:
                        progress_callback(i, total_to_update, lead_id)
                    else:
                        # Default progress logging
                        if i % progress_interval == 0 or i == total_to_update or i == 1:
                            logger.info(f"Progress: {i}/{total_to_update} leads processed ({(i/total_to_update)*100:.1f}%)")
                        
                except Exception as e:
                    error_msg = f"Failed to update record {lead_id} in {model}: {e}"
                    logger.error(error_msg)
                    update_errors.append({
                        "lead_id": lead_id,
                        "error": str(e)
                    })
            
            success = updated_count > 0
            
            if success:
                logger.info(f"Updated assignments for {updated_count} records in {model}")
            
            if non_existent:
                logger.warning(f"Ignored {len(non_existent)} non-existent lead IDs in {model}")
            
            return {
                "success": success,
                "updated_count": updated_count,
                "non_existent": non_existent,
                "errors": update_errors
            }
            
        except Exception as e:
            logger.error(f"Error updating assignments in {model}: {e}")
            return {
                "success": False,
                "updated_count": 0,
                "non_existent": [],
                "errors": [{"lead_id": "general", "error": str(e)}]
            }
    
    def get_user_lead_counts(self, user_ids: Optional[List[int]] = None) -> Dict[int, int]:
        """
        Get count of leads assigned to users.
        
        Args:
            user_ids: Specific user IDs to check (None for all)
            
        Returns:
            Dictionary mapping user IDs to lead counts
        """
        domain = []
        if user_ids:
            domain.append(["user_id", "in", user_ids])
        
        try:
            leads = self.client.search_read(
                model_name="res.partner",
                domain=domain,
                fields=["id", "user_id"]
            )
            
            user_counts = {}
            for lead in leads:
                user_id = lead.get("user_id")
                if user_id and isinstance(user_id, list):
                    user_id = user_id[0]
                if user_id:
                    user_counts[user_id] = user_counts.get(user_id, 0) + 1
            
            return user_counts
            
        except Exception as e:
            logger.error(f"Error getting user lead counts: {e}")
            raise
    
    def export_to_dataframe(self, filter_obj: Optional[LeadFilter] = None, **kwargs) -> pd.DataFrame:
        """
        Export leads to pandas DataFrame.
        
        Args:
            filter_obj: LeadFilter instance with criteria
            **kwargs: Additional filter parameters
            
        Returns:
            Pandas DataFrame with lead data
        """
        leads = self.get_leads(filter_obj, **kwargs)
        return pd.DataFrame(leads)

    def group_by_and_pivot(self, filter_obj: Optional[LeadFilter] = None, 
                          group_by: Optional[List[str]] = None,
                          pivot_rows: Optional[List[str]] = None,
                          pivot_cols: Optional[List[str]] = None,
                          **kwargs) -> pd.DataFrame:
        """
        Group and pivot lead data for analysis.
        
        Args:
            filter_obj: LeadFilter instance with criteria
            group_by: List of columns to group by for simple aggregation
            pivot_rows: List of columns for pivot table rows
            pivot_cols: List of columns for pivot table columns
            **kwargs: Additional filter parameters
            
        Returns:
            Pandas DataFrame with grouped or pivoted data
        """
        df = self.export_to_dataframe(filter_obj, **kwargs)
        
        if df.empty:
            return pd.DataFrame()
        
        # Handle tuple format from Odoo (id, name) -> extract name
        def extract_name(value):
            if isinstance(value, list) and len(value) > 1:
                return value[1]  # Return the name part
            return value
        
        # Apply name extraction to relevant columns
        for col in df.columns:
            if col in ['user_id', 'closer_id', 'open_user_id', 'stage_id', 'team_id', 'country_id', 'state_id', 'web_source_id']:
                df[col] = df[col].apply(extract_name)
        
        # Simple group_by operation
        if group_by:
            # Filter out non-existent columns
            valid_groups = [col for col in group_by if col in df.columns]
            if not valid_groups:
                raise ValueError(f"None of the group_by columns exist: {group_by}")
            
            grouped = df.groupby(valid_groups).size().reset_index(name='count')
            return grouped
        
        # Pivot table operation
        if pivot_rows or pivot_cols:
            valid_rows = [col for col in (pivot_rows or []) if col in df.columns]
            valid_cols = [col for col in (pivot_cols or []) if col in df.columns]
            
            if not valid_rows and not valid_cols:
                raise ValueError("No valid pivot columns found")
            
            index_cols = valid_rows if valid_rows else None
            columns_cols = valid_cols if valid_cols else None
            
            # Use all available columns if none specified
            if index_cols is None and columns_cols is None:
                return pd.DataFrame()
            
            pivot = df.pivot_table(
                index=index_cols,
                columns=columns_cols,
                values='id',
                aggfunc='count',
                fill_value=0
            )
            
            # Reset index to make it a flat DataFrame
            if isinstance(pivot, pd.DataFrame):
                pivot = pivot.reset_index()
            
            return pivot
        
        # If no grouping specified, return basic counts
        return pd.DataFrame({'total_leads': [len(df)]})
    
    def _apply_quick_filters(self, filter_obj: LeadFilter, **kwargs) -> LeadFilter:
        """Apply quick filter parameters to the filter object."""
        if "start_date" in kwargs or "end_date" in kwargs:
            filter_obj.by_date_range(
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                field_name=kwargs.get("date_field", "source_date")
            )
        
        if "source_ids" in kwargs:
            filter_obj.by_web_source_ids(kwargs["source_ids"])
        
        if "statuses" in kwargs:
            filter_obj.by_status(kwargs["statuses"])
        
        if any(k in kwargs for k in ["user_ids", "user_names", "closer_ids", "closer_names", "open_user_ids", "open_user_names"]):
            filter_obj.by_user_assignments(
                user_ids=kwargs.get("user_ids"),
                user_names=kwargs.get("user_names"),
                closer_ids=kwargs.get("closer_ids"),
                closer_names=kwargs.get("closer_names"),
                open_user_ids=kwargs.get("open_user_ids"),
                open_user_names=kwargs.get("open_user_names")
            )
        
        if "limit" in kwargs:
            filter_obj.limit(kwargs["limit"])
        
        if "offset" in kwargs:
            filter_obj.offset(kwargs["offset"])
        
        if "order" in kwargs:
            filter_obj.order(kwargs["order"])
        
        return filter_obj
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics from lead data."""
        stats = {
            "total_leads": len(df),
            "leads_with_email": len(df[df["email"].notna()]),
            "leads_with_phone": len(df[df["phone"].notna()]),
            "leads_with_mobile": len(df[df["mobile"].notna()]),
            "unique_emails": df["email"].nunique(),
            "unique_phones": df["phone"].nunique(),
            "assigned_leads": len(df[df["user_id"].notna()]),
            "unassigned_leads": len(df[df["user_id"].isna()])
        }
        
        # Date statistics
        if "source_date" in df.columns:
            source_dates = pd.to_datetime(df["source_date"], errors="coerce")
            if not source_dates.empty:
                stats["earliest_lead"] = source_dates.min().isoformat() if not source_dates.empty else None
                stats["latest_lead"] = source_dates.max().isoformat() if not source_dates.empty else None
        
        return stats
    
    def _get_user_assignments(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of leads by user assignments."""
        assignments = {}
        
        for col in ["user_id", "closer_id", "open_user_id"]:
            if col in df.columns:
                # Handle tuple format from Odoo (id, name)
                user_counts = df[col].apply(
                    lambda x: x[1] if isinstance(x, list) and len(x) > 1 else str(x)
                ).value_counts().to_dict()
                assignments[col] = user_counts
        
        return assignments
    
    def _get_source_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of leads by web source."""
        if "web_source_id" not in df.columns:
            return {}
        
        # Handle both ID and name format
        source_counts = {}
        for source in df["web_source_id"]:
            if isinstance(source, list) and len(source) > 1:
                source_name = source[1]
            else:
                source_name = str(source)
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
        
        return source_counts
    
    def _get_status_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of leads by status."""
        if "status" not in df.columns:
            return {}
        
        return df["status"].value_counts().to_dict()
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get date range information from leads."""
        date_range = {}
        
        for date_col in ["create_date", "write_date", "source_date"]:
            if date_col in df.columns:
                dates = pd.to_datetime(df[date_col], errors="coerce")
                if not dates.empty:
                    date_range[date_col] = {
                        "min": dates.min().isoformat() if not dates.empty else None,
                        "max": dates.max().isoformat() if not dates.empty else None,
                        "count": dates.count()
                    }
        
        return date_range
    
    def _get_geographic_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get geographic distribution of leads."""
        geo_dist = {}
        
        for geo_col in ["city", "country_id", "state_id"]:
            if geo_col in df.columns:
                # Handle tuple format from Odoo
                counts = {}
                for value in df[geo_col]:
                    if isinstance(value, list) and len(value) > 1:
                        name = value[1]
                    else:
                        name = str(value) if pd.notna(value) else "Unknown"
                    counts[name] = counts.get(name, 0) + 1
                
                geo_dist[geo_col] = counts
        
        return geo_dist

    def get_all_leads(self, fields: Optional[List[str]] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all leads from CRM using your exact CSV fields and search pattern.
        
        Args:
            fields: Fields to retrieve (uses your exact CSV field list if None)
            limit: Maximum number of results
            
        Returns:
            List of lead dictionaries matching your CSV structure
        """
        if fields is None:
            fields = self._default_fields
            
        # For leads, we typically want all records without filtering
        domain = []
            
        return self.client.search_read(
            model_name="crm.lead",
            domain=domain,
            fields=fields,
            limit=limit
        )
    
    def get_all_partners(self, include_companies: bool = True, include_individuals: bool = True, 
                        fields: Optional[List[str]] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all partners using your exact search pattern.
        
        Args:
            include_companies: Include company partners
            include_individuals: Include individual partners
            fields: Fields to retrieve (uses your exact field list if None)
            limit: Maximum number of results
            
        Returns:
            List of partner dictionaries matching your search pattern
        """
        if fields is None:
            fields = ["id", "name", "phone", "email", "commercial_company_name", "create_date", "is_company"]
            
        # Build domain matching your exact pattern: ["|", ("is_company", "=", True), ("is_company", "=", False)]
        if include_companies and include_individuals:
            domain = ["|", ("is_company", "=", True), ("is_company", "=", False)]
        elif include_companies:
            domain = [("is_company", "=", True)]
        elif include_individuals:
            domain = [("is_company", "=", False)]
        else:
            domain = []
            
        return self.client.search_read(
            model_name="res.partner",
            domain=domain,
            fields=fields,
            limit=limit
        )