"""
Odoo Lead Manager - A comprehensive package for managing Odoo leads with smart distribution.

This package provides tools to:
- Fetch and filter leads from Odoo's res.partner model
- Apply various filtering criteria (date ranges, source IDs, status, user assignments)
- Summarize lead characteristics
- Implement smart lead distribution algorithms based on user capacity and expected proportions
"""

__version__ = "1.3.2"
__author__ = "Lead Management Team"

from .client import OdooClient
from .lead_manager import LeadManager
from .filters import LeadFilter
from .distribution import SmartDistributor

__all__ = [
    "OdooClient",
    "LeadManager", 
    "LeadFilter",
    "SmartDistributor",
]