"""
Smart Lead Distribution Algorithm

This module implements intelligent lead distribution algorithms that consider:
- Current lead load for each user
- Expected percentage/proportion settings for users
- User capacity constraints
- Fair distribution based on configurable weights
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import pandas as pd
from loguru import logger


class DistributionStrategy(Enum):
    """Available distribution strategies."""
    PROPORTIONAL = "proportional"
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED_RANDOM = "weighted_random"
    CAPACITY_BASED = "capacity_based"


@dataclass
class UserProfile:
    """User profile with distribution parameters."""
    user_id: int
    name: str
    current_leads: int = 0
    expected_percentage: float = 0.0
    max_capacity: Optional[int] = None
    priority: int = 1
    is_active: bool = True
    skills: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []


@dataclass
class Lead:
    """Lead information for distribution."""
    lead_id: int
    name: str
    source_id: Optional[str] = None
    tags: List[str] = None
    priority: int = 1
    required_skills: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.required_skills is None:
            self.required_skills = []


class SmartDistributor:
    """
    Intelligent lead distribution system.
    
    This class implements various algorithms for distributing leads among users
    based on their current load, expected proportions, capacity, and other factors.
    """
    
    def __init__(self):
        """Initialize the smart distributor."""
        self.user_profiles: Dict[int, UserProfile] = {}
        self.distribution_history: List[Dict[str, Any]] = []
        self.strategy = DistributionStrategy.PROPORTIONAL
    
    def add_user_profile(self, profile: UserProfile) -> None:
        """
        Add or update a user profile.
        
        Args:
            profile: UserProfile instance with user information
        """
        self.user_profiles[profile.user_id] = profile
        logger.info(f"Added user profile: {profile.name} (ID: {profile.user_id})")
    
    def remove_user_profile(self, user_id: int) -> bool:
        """
        Remove a user profile.
        
        Args:
            user_id: User ID to remove
            
        Returns:
            True if user was removed, False if not found
        """
        if user_id in self.user_profiles:
            removed = self.user_profiles.pop(user_id)
            logger.info(f"Removed user profile: {removed.name} (ID: {user_id})")
            return True
        return False
    
    def update_user_current_leads(self, user_id: int, current_leads: int) -> None:
        """
        Update the current lead count for a user.
        
        Args:
            user_id: User ID to update
            current_leads: New lead count
        """
        if user_id in self.user_profiles:
            self.user_profiles[user_id].current_leads = current_leads
            logger.debug(f"Updated lead count for user {user_id}: {current_leads}")
    
    def set_distribution_strategy(self, strategy: DistributionStrategy) -> None:
        """
        Set the distribution strategy.
        
        Args:
            strategy: DistributionStrategy to use
        """
        self.strategy = strategy
        logger.info(f"Distribution strategy changed to: {strategy.value}")
    
    def distribute_leads(
        self,
        leads: List[Lead],
        strategy: Optional[DistributionStrategy] = None
    ) -> Dict[int, List[int]]:
        """
        Distribute leads among users according to the selected strategy.
        
        Args:
            leads: List of Lead objects to distribute
            strategy: Override distribution strategy
            
        Returns:
            Dictionary mapping user IDs to list of assigned lead IDs
        """
        if not leads:
            logger.warning("No leads provided for distribution")
            return {}
        
        strategy = strategy or self.strategy
        active_users = self._get_active_users()
        
        if not active_users:
            logger.error("No active users available for distribution")
            return {}
        
        logger.info(f"Distributing {len(leads)} leads using {strategy.value} strategy")
        
        # Route leads based on strategy
        if strategy == DistributionStrategy.PROPORTIONAL:
            assignments = self._distribute_proportional(leads, active_users)
        elif strategy == DistributionStrategy.ROUND_ROBIN:
            assignments = self._distribute_round_robin(leads, active_users)
        elif strategy == DistributionStrategy.LEAST_LOADED:
            assignments = self._distribute_least_loaded(leads, active_users)
        elif strategy == DistributionStrategy.WEIGHTED_RANDOM:
            assignments = self._distribute_weighted_random(leads, active_users)
        elif strategy == DistributionStrategy.CAPACITY_BASED:
            assignments = self._distribute_capacity_based(leads, active_users)
        else:
            raise ValueError(f"Unsupported distribution strategy: {strategy}")
        
        # Update user lead counts and record distribution
        self._update_user_counts(assignments)
        self._record_distribution(leads, assignments, strategy)
        
        return assignments
    
    def get_distribution_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive distribution report.
        
        Returns:
            Dictionary with distribution statistics and user information
        """
        active_users = self._get_active_users()
        
        report = {
            "total_users": len(self.user_profiles),
            "active_users": len(active_users),
            "user_details": {},
            "expected_vs_actual": {},
            "distribution_history": self.distribution_history[-50:]  # Last 50 distributions
        }
        
        total_expected = sum(user.expected_percentage for user in active_users)
        total_current = sum(user.current_leads for user in active_users)
        
        for user in active_users:
            expected_ratio = user.expected_percentage / total_expected if total_expected > 0 else 0
            expected_leads = total_current * expected_ratio if total_current > 0 else 0
            
            report["user_details"][user.user_id] = {
                "name": user.name,
                "current_leads": user.current_leads,
                "expected_percentage": user.expected_percentage,
                "max_capacity": user.max_capacity,
                "utilization_rate": (user.current_leads / user.max_capacity) if user.max_capacity else None,
                "expected_leads": expected_leads,
                "deviation": user.current_leads - expected_leads
            }
        
        return report
    
    def load_user_profiles_from_odoo(self, lead_manager) -> None:
        """
        Load user profiles from Odoo.
        
        Args:
            lead_manager: LeadManager instance to fetch user data
        """
        try:
            users = lead_manager.client.search_read(
                model_name="res.users",
                domain=[["active", "=", True]],
                fields=["id", "name", "email", "login"]
            )
            
            # Get current lead counts for each user
            user_lead_counts = lead_manager.get_user_lead_counts()
            
            for user in users:
                user_id = user["id"]
                current_leads = user_lead_counts.get(user_id, 0)
                
                profile = UserProfile(
                    user_id=user_id,
                    name=user["name"],
                    current_leads=current_leads,
                    expected_percentage=100.0 / len(users),  # Default equal distribution
                    max_capacity=None  # No limit by default
                )
                
                self.add_user_profile(profile)
                
        except Exception as e:
            logger.error(f"Error loading user profiles from Odoo: {e}")
            raise
    
    def save_proportions_to_odoo(self, lead_manager, table_name: str = "lead_distribution_proportions") -> bool:
        """
        Save expected proportions to Odoo table.
        
        Args:
            lead_manager: LeadManager instance
            table_name: Name of the proportions table in Odoo
            
        Returns:
            True if successful
        """
        try:
            for user_id, profile in self.user_profiles.items():
                # Check if record exists
                existing = lead_manager.client.search_read(
                    model_name=table_name,
                    domain=[["user_id", "=", user_id]],
                    fields=["id"]
                )
                
                values = {
                    "user_id": user_id,
                    "expected_percentage": profile.expected_percentage,
                    "max_capacity": profile.max_capacity,
                    "priority": profile.priority,
                    "is_active": profile.is_active
                }
                
                if existing:
                    # Update existing record
                    lead_manager.client.write(table_name, [existing[0]["id"]], values)
                else:
                    # Create new record
                    lead_manager.client.create(table_name, values)
            
            logger.info("Proportions saved to Odoo successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving proportions to Odoo: {e}")
            return False
    
    def load_proportions_from_odoo(self, lead_manager, table_name: str = "lead_distribution_proportions") -> bool:
        """
        Load expected proportions from Odoo table.
        
        Args:
            lead_manager: LeadManager instance
            table_name: Name of the proportions table in Odoo
            
        Returns:
            True if successful
        """
        try:
            proportions = lead_manager.client.search_read(
                model_name=table_name,
                domain=[["is_active", "=", True]],
                fields=["user_id", "expected_percentage", "max_capacity", "priority"]
            )
            
            for prop in proportions:
                user_id = prop["user_id"][0] if isinstance(prop["user_id"], list) else prop["user_id"]
                
                if user_id in self.user_profiles:
                    profile = self.user_profiles[user_id]
                    profile.expected_percentage = prop.get("expected_percentage", 0.0)
                    profile.max_capacity = prop.get("max_capacity")
                    profile.priority = prop.get("priority", 1)
            
            logger.info("Proportions loaded from Odoo successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading proportions from Odoo: {e}")
            return False
    
    def _get_active_users(self) -> List[UserProfile]:
        """Get list of active users with capacity."""
        active_users = []
        
        for profile in self.user_profiles.values():
            if profile.is_active:
                # Check capacity
                if profile.max_capacity is None or profile.current_leads < profile.max_capacity:
                    active_users.append(profile)
        
        return active_users
    
    def _distribute_proportional(self, leads: List[Lead], users: List[UserProfile]) -> Dict[int, List[int]]:
        """Distribute leads proportionally based on expected percentages."""
        assignments = {user.user_id: [] for user in users}
        
        if not users:
            return assignments
        
        total_expected = sum(user.expected_percentage for user in users)
        if total_expected == 0:
            # Equal distribution if no percentages set
            total_expected = len(users)
            for user in users:
                user.expected_percentage = 1.0
        
        # Calculate target counts
        total_leads = len(leads)
        user_targets = {}
        
        for user in users:
            target = (user.expected_percentage / total_expected) * total_leads
            user_targets[user.user_id] = int(target)
        
        # Distribute leads
        lead_index = 0
        for user in sorted(users, key=lambda u: u.expected_percentage, reverse=True):
            target = user_targets[user.user_id]
            while len(assignments[user.user_id]) < target and lead_index < len(leads):
                if self._can_assign_lead_to_user(leads[lead_index], user):
                    assignments[user.user_id].append(leads[lead_index].lead_id)
                    lead_index += 1
                else:
                    break
        
        # Distribute remaining leads
        remaining_users = [u for u in users if len(assignments[u.user_id]) < user_targets[u.user_id]]
        while lead_index < len(leads) and remaining_users:
            for user in remaining_users:
                if lead_index < len(leads) and self._can_assign_lead_to_user(leads[lead_index], user):
                    assignments[user.user_id].append(leads[lead_index].lead_id)
                    lead_index += 1
            remaining_users = [u for u in users if len(assignments[u.user_id]) < user_targets[u.user_id]]
        
        return assignments
    
    def _distribute_round_robin(self, leads: List[Lead], users: List[UserProfile]) -> Dict[int, List[int]]:
        """Distribute leads in round-robin fashion."""
        assignments = {user.user_id: [] for user in users}
        
        if not users:
            return assignments
        
        user_cycle = [u for u in users for _ in range(u.priority)]
        user_index = 0
        
        for lead in leads:
            attempts = 0
            while attempts < len(user_cycle):
                user = user_cycle[user_index % len(user_cycle)]
                if self._can_assign_lead_to_user(lead, user):
                    assignments[user.user_id].append(lead.lead_id)
                    user_index += 1
                    break
                attempts += 1
                user_index += 1
        
        return assignments
    
    def _distribute_least_loaded(self, leads: List[Lead], users: List[UserProfile]) -> Dict[int, List[int]]:
        """Distribute leads to the least loaded users first."""
        assignments = {user.user_id: [] for user in users}
        
        if not users:
            return assignments
        
        for lead in leads:
            # Sort users by current load (leads per expected percentage)
            sorted_users = sorted(users, key=lambda u: u.current_leads / max(u.expected_percentage, 0.01))
            
            for user in sorted_users:
                if self._can_assign_lead_to_user(lead, user):
                    assignments[user.user_id].append(lead.lead_id)
                    user.current_leads += 1  # Update for this distribution
                    break
        
        return assignments
    
    def _distribute_weighted_random(self, leads: List[Lead], users: List[UserProfile]) -> Dict[int, List[int]]:
        """Distribute leads using weighted random selection."""
        assignments = {user.user_id: [] for user in users}
        
        if not users:
            return assignments
        
        # Create weighted list based on expected percentages
        weights = [max(user.expected_percentage, 0.01) for user in users]
        
        for lead in leads:
            available_users = [u for u in users if self._can_assign_lead_to_user(lead, u)]
            if not available_users:
                continue
            
            available_weights = [weights[users.index(u)] for u in available_users]
            selected_user = random.choices(available_users, weights=available_weights)[0]
            assignments[selected_user.user_id].append(lead.lead_id)
        
        return assignments
    
    def _distribute_capacity_based(self, leads: List[Lead], users: List[UserProfile]) -> Dict[int, List[int]]:
        """Distribute leads based on remaining capacity."""
        assignments = {user.user_id: [] for user in users}
        
        if not users:
            return assignments
        
        for lead in leads:
            # Calculate remaining capacity for each user
            capacity_weights = []
            for user in users:
                if user.max_capacity:
                    remaining = max(0, user.max_capacity - user.current_leads)
                    capacity_weights.append(remaining)
                else:
                    capacity_weights.append(1.0)  # No capacity limit
            
            available_users = [u for u, w in zip(users, capacity_weights) if w > 0 and self._can_assign_lead_to_user(lead, u)]
            available_weights = [w for u, w in zip(users, capacity_weights) if w > 0 and self._can_assign_lead_to_user(lead, u)]
            
            if available_users and available_weights:
                selected_user = random.choices(available_users, weights=available_weights)[0]
                assignments[selected_user.user_id].append(lead.lead_id)
        
        return assignments
    
    def _can_assign_lead_to_user(self, lead: Lead, user: UserProfile) -> bool:
        """Check if a lead can be assigned to a user."""
        # Check capacity
        if user.max_capacity and user.current_leads >= user.max_capacity:
            return False
        
        # Check required skills (simplified - in real implementation, check user skills)
        # This is a placeholder for skill-based filtering
        
        return True
    
    def _update_user_counts(self, assignments: Dict[int, List[int]]) -> None:
        """Update user lead counts based on new assignments."""
        for user_id, assigned_leads in assignments.items():
            if user_id in self.user_profiles:
                self.user_profiles[user_id].current_leads += len(assigned_leads)
    
    def _record_distribution(
        self,
        leads: List[Lead],
        assignments: Dict[int, List[int]],
        strategy: DistributionStrategy
    ) -> None:
        """Record distribution for history tracking."""
        distribution_record = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "strategy": strategy.value,
            "total_leads": len(leads),
            "assignments": assignments,
            "user_states": {
                user_id: {
                    "name": profile.name,
                    "current_leads": profile.current_leads,
                    "expected_percentage": profile.expected_percentage
                }
                for user_id, profile in self.user_profiles.items()
            }
        }
        
        self.distribution_history.append(distribution_record)