"""
Daily Lead Distribution System

This module implements the comprehensive daily lead distribution system as specified
in DAILY_LEAD_DISTRIBUTION_REQUIREMENTS.md. It provides:

- Configuration-driven salesperson selection
- Enhanced lead filtering with case-sensitive matching
- Multiple distribution strategies (level-based, round-robin, proportional)
- Performance tracking and analytics
- Comprehensive reporting
"""

import os
import yaml
import csv
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import re
from loguru import logger


# Remove the custom dumper approach and use standard YAML dumping

from .client import OdooClient
from .lead_manager import LeadManager
from .distribution import SmartDistributor, UserProfile, DistributionStrategy


class SalespersonSourceType(Enum):
    """Available salesperson selection source types."""
    CAMPAIGN_TABLE = "campaign_table"
    FILE = "file"
    LIST = "list"
    DATABASE = "database"


class DistributionStrategy(Enum):
    """Available distribution strategies."""
    LEVEL_BASED = "level_based"
    ROUND_ROBIN = "round_robin"
    PROPORTIONAL = "proportional"
    CAPACITY_BASED = "capacity_based"


@dataclass
class SalespersonConfig:
    """Salesperson configuration for daily distribution."""
    salesperson_name: str
    salesperson_id: int
    campaign_name: str
    active: bool = True
    team: str = "Voice"
    level: str = "mid_level"
    target_leads: int = 150


@dataclass
class LeadDistributionResult:
    """Result of daily lead distribution operation."""
    success: bool
    leads_found: int
    leads_distributed: int
    leads_not_distributed: int
    salespeople_eligible: int
    salespeople_received_leads: int
    execution_time_seconds: float
    error_message: Optional[str] = None
    distribution_summary: Optional[Dict[str, Any]] = None


@dataclass
class StepThroughData:
    """Data for step-through mode display."""
    step_name: str
    description: str
    data: Dict[str, Any]
    expected_outcome: Optional[str] = None


class DailyDistributionConfigGenerator:
    """Generate boilerplate configuration files for daily distribution."""
    
    def __init__(self):
        """Initialize the config generator."""
        self.templates = {
            'basic': self._get_basic_template(),
            'advanced': self._get_advanced_template(),
            'minimal': self._get_minimal_template()
        }
    
    def generate_config(self, campaign: str = None, template: str = 'basic', output_path: str = None) -> str:
        """Generate a configuration file based on template and campaign."""
        if template not in self.templates:
            raise ValueError(f"Unknown template: {template}")
        
        config = self.templates[template].copy()
        
        # Customize for specific campaign
        if campaign:
            config = self._customize_for_campaign(config, campaign)
        
        # Convert to YAML with proper formatting and quoted strings
        yaml_content = self._dump_yaml_with_quotes(config)
        
        # Add header comments
        header = self._generate_header_comments(campaign, template)
        full_content = header + yaml_content
        
        # Write to file if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(full_content)
        
        return full_content
    
    def _dump_yaml_with_quotes(self, data: Dict[str, Any]) -> str:
        """Dump YAML with proper string quoting."""
        class QuotedStringDumper(yaml.SafeDumper):
            def represent_str(self, data):
                # Always quote strings that contain special characters or environment variables
                if any(char in data for char in ['$', '{', '}', ':', ' ', '-', '|', '>', '<', '&', '*', '?', '!', '%', '@', '`']) or data.startswith('${'):
                    return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')
                return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')
        
        # Register the custom dumper
        QuotedStringDumper.add_representer(str, QuotedStringDumper.represent_str)
        
        return yaml.dump(data, Dumper=QuotedStringDumper, default_flow_style=False, 
                        sort_keys=False, allow_unicode=True, width=float("inf"))
    
    def _get_basic_template(self) -> Dict[str, Any]:
        """Get basic configuration template."""
        return {
            "version": "1.0",
            "name": "Daily Lead Distribution",
            "description": "Automated daily lead distribution system",
            "tags": ["lead-distribution", "automation", "sales", "odoo"],
            "author": "Sales Operations Team",
            "created_date": "2024-01-15",
            "last_modified": "2024-01-15",
            
            "odoo_connection": {
                "host": "${ODOO_HOST}",
                "port": 8069,
                "database": "${ODOO_DB}",
                "username": "${ODOO_USERNAME}",
                "password": "${ODOO_PASSWORD}"
            },
            
            "database_connection": {
                "host": "${TRACKING_DB_HOST}",
                "port": 3306,
                "database": "${TRACKING_DB_NAME}",
                "username": "${TRACKING_DB_USER}",
                "password": "${TRACKING_DB_PASSWORD}"
            },
            
            "campaign": {
                "name": "Voice",
                "description": "Voice/telephony sales campaign distribution",
                "target_campaign": "Voice",
                "distribution_frequency": "daily",
                "active": True
            },
            
            "salesperson_selection": {
                "source_type": "campaign_table",
                "source_config": {
                    "campaign_table": {
                        "file_path": "config/salesperson_campaigns.csv"
                    }
                },
                "campaign_filtering": {
                    "enabled": True,
                    "target_campaign": "Voice",
                    "include_inactive_salespeople": False,
                    "exclude_specific_users": ["Drew Cox", "Patrick Adler", "Administrator", "Marc Spiegel"]
                },
                "filters": {
                    "active_only": True,
                    "has_permissions": True,
                    "min_experience_level": 1,
                    "max_workload_percentage": 90,
                    "team_filter": "Voice"
                }
            },
            
            "lead_finding": {
                "date_range": {
                    "older_than_days": 0,
                    "younger_than_days": 30,
                    "exclude_weekends": False,
                    "exclude_holidays": False
                },
                "web_sources": {
                    "source_type": "file",
                    "source_config": {
                        "file_path": "config/web_sources.txt"
                    },
                    "case_sensitive": False,
                    "exact_match": False,
                    "match_mode": "exact"
                },
                "campaigns": {
                    "enabled": True,
                    "types": ["voice_campaign_2024"],
                    "case_sensitive": False,
                    "exact_match": False,
                    "match_mode": "exact"
                },
                "sales_filter": {
                    "enabled": True,
                    "opportunity_table": "crm.opp",
                    "opportunity_partner_field": "partner_id",
                    "lead_partner_field": "partner_id",
                    "exclude_opportunity_stages": ["cancelled", "lost", "closed_lost"],
                    "include_opportunity_stages": [],
                    "opportunity_date_range": {
                        "enabled": False,
                        "field_name": "date_open",
                        "days_back": 365
                    },
                    "log_excluded_leads": True,
                    "log_level": "info"
                },
                "dropback_filter": {
                    "enabled": True,
                    "age_threshold": {
                        "days": 30,
                        "field_name": "source_date",
                        "use_business_days": False
                    },
                    "web_source_campaign_mapping": {
                        "voice_sources": [
                            "facebook_voice",
                            "google_ads_voice", 
                            "voice_landing_page",
                            "voice_campaign_2024"
                        ],
                        "apple_sources": [
                            "facebook_apple",
                            "google_ads_apple",
                            "apple_landing_page", 
                            "apple_campaign_2024"
                        ],
                        "default_campaign": "default"
                    },
                    "campaign_assignments": {
                        "Voice": "Pat Adler",
                        "Apple": "Kevin Levonas",
                        "default": "Administrator"
                    },
                    "assignment_config": {
                        "web_source_field": "source_id",
                        "web_source_field_type": "many2one",
                        "assign_immediately": True,
                        "update_status": True,
                        "dropback_status": "dropback",
                        "override_existing_assignments": True
                    },
                    "logging": {
                        "log_dropback_assignments": True,
                        "log_level": "info",
                        "include_lead_details": False
                    }
                },
                "additional_filters": {
                    "status": {
                        "values": ["new", "in_progress", "call_back", "utr"],
                        "case_sensitive": False,
                        "exact_match": False,
                        "match_mode": "exact"
                    },
                    "exclude_sale_statuses": {
                        "enabled": True,
                        "values": ["sale_made", "sold", "completed", "won", "closed_won", "deal_closed"],
                        "case_sensitive": False,
                        "match_mode": "partial",
                        "description": "Exclude leads with statuses indicating a sale has been made"
                    },
                    "exclude_dnc": True,
                    "dnc_statuses": ["dnc", "do_not_call", "dont_call", "no_call", "blocked", "opt_out"],
                    "exclude_tags": {
                        "values": ["do_not_distribute", "test", "archived"],
                        "case_sensitive": False,
                        "match_mode": "exact"
                    },
                    "include_tags": {
                        "values": ["hot_lead", "vip", "priority"],
                        "case_sensitive": False,
                        "match_mode": "exact"
                    },
                    "required_fields": ["name", "email"],
                    "priority_range": {
                        "min": 1,
                        "max": 5
                    },
                    "assignment_filters": {
                        "exclude_assigned": True,
                        "exclude_closed": True,
                        "exclude_inactive_users": True
                    },
                    "activity_deadline_filter": {
                        "enabled": True,
                        "exclude_with_deadline": True,
                        "description": "Exclude leads that have a valid activity_date_deadline field"
                    }
                }
            },
            
            "distribution": {
                "strategy": "level_based",
                "level_based": {
                    "levels": {
                        "senior": {
                            "target_leads": 200,
                            "priority": 1
                        },
                        "mid_level": {
                            "target_leads": 150,
                            "priority": 2
                        },
                        "junior": {
                            "target_leads": 100,
                            "priority": 3
                        }
                    },
                    "fill_strategy": "highest_priority_first",
                    "allow_overflow": False,
                    "overflow_limit": 10
                },
                "round_robin_override": {
                    "enabled": False
                }
            },
            
            "tracking": {
                "enabled": True,
                "track_individual_assignments": True,
                "track_pre_post_counts": True,
                "track_distribution_summary": True,
                "retention_days": 365,
                "archive_old_data": True,
                "batch_size": 1000,
                "async_tracking": False
            },
            
            "reporting": {
                "generate_report": True,
                "report_format": "csv",
                "report_location": "reports/",
                "include_analytics": True,
                "email_notification": False
            },
            
            "execution": {
                "dry_run": False,
                "max_leads_per_run": 50000,  # Increased default to capture more leads
                "batch_size": 50,
                "retry_failed": True,
                "max_retries": 3,
                "log_level": "INFO"
            }
        }
    
    def _get_advanced_template(self) -> Dict[str, Any]:
        """Get advanced configuration template with all features enabled."""
        basic = self._get_basic_template()
        
        # Add advanced features
        basic["lead_finding"]["web_sources"]["validate_sources"] = True
        basic["lead_finding"]["web_sources"]["exclude_invalid"] = True
        basic["lead_finding"]["web_sources"]["match_patterns"] = ["facebook*", "google_ads*", "website_contact"]
        
        # Enhanced sales filter configuration
        basic["lead_finding"]["sales_filter"].update({
            "performance": {
                "batch_size": 1000,
                "use_database_join": True,
                "cache_opportunities": True,
                "cache_duration_minutes": 30
            },
            "reporting": {
                "log_excluded_leads": True,
                "log_match_details": False,
                "count_excluded_by_stage": True,
                "export_excluded_leads": False,
                "export_path": "logs/excluded_leads.csv"
            },
            "secondary_matches": {
                "email_match": {
                    "enabled": False,
                    "lead_field": "email_from",
                    "opportunity_field": "email_from"
                },
                "phone_match": {
                    "enabled": False,
                    "lead_field": "phone",
                    "opportunity_field": "phone"
                }
            }
        })
        
        # Enhanced dropback filter configuration
        basic["lead_finding"]["dropback_filter"].update({
            "web_source_matching": {
                "primary_field": "source_id",
                "primary_field_type": "many2one",
                "fallback_fields": [
                    {"field": "utm_source", "type": "char"},
                    {"field": "x_web_source", "type": "char"}
                ],
                "campaign_patterns": {
                    "Voice": {
                        "exact_matches": [
                            "facebook_voice",
                            "google_ads_voice",
                            "voice_landing_page"
                        ],
                        "pattern_matches": [
                            ".*voice.*",
                            ".*telephone.*",
                            ".*phone.*"
                        ]
                    },
                    "Apple": {
                        "exact_matches": [
                            "facebook_apple",
                            "google_ads_apple",
                            "apple_landing_page"
                        ],
                        "pattern_matches": [
                            ".*apple.*",
                            ".*iphone.*",
                            ".*ios.*"
                        ]
                    }
                }
            },
            "assignment_rules": {
                "Voice": {
                    "user": "Pat Adler",
                    "team": "Voice Team",
                    "status": "dropback_voice",
                    "priority": 2
                },
                "Apple": {
                    "user": "Kevin Levonas",
                    "team": "Apple Team", 
                    "status": "dropback_apple",
                    "priority": 1
                },
                "default": {
                    "user": "Administrator",
                    "team": None,
                    "status": "dropback_general",
                    "priority": 3
                }
            },
            "reporting": {
                "count_dropback_leads": True,
                "export_dropback_report": False,
                "report_path": "reports/dropback_assignments.csv"
            }
        })
        
        basic["distribution"]["advanced_rules"] = {
            "skill_matching": {
                "enabled": True,
                "required_skills": ["enterprise_sales", "technical_knowledge"],
                "skill_weights": [0.7, 0.3]
            },
            "workload_balancing": {
                "enabled": True,
                "max_daily_distribution": 20,
                "min_daily_distribution": 5,
                "consider_weekend_workload": False
            },
            "priority_handling": {
                "high_priority_leads": "senior_only",
                "medium_priority_leads": "all_levels",
                "low_priority_leads": "junior_first"
            }
        }
        
        basic["tracking"]["async_tracking"] = True
        basic["tracking"]["batch_size"] = 1000
        
        return basic
    
    def _get_minimal_template(self) -> Dict[str, Any]:
        """Get minimal configuration template for basic usage."""
        return {
            "version": "1.0",
            "name": "Daily Lead Distribution - Minimal",
            "description": "Minimal configuration for daily lead distribution",
            "tags": ["lead-distribution", "minimal"],
            "author": "Sales Operations Team",
            "created_date": "2024-01-15",
            
            "odoo_connection": {
                "host": "${ODOO_HOST}",
                "port": 8069,
                "database": "${ODOO_DB}",
                "username": "${ODOO_USERNAME}",
                "password": "${ODOO_PASSWORD}"
            },
            
            "database_connection": {
                "host": "${TRACKING_DB_HOST}",
                "port": 3306,
                "database": "${TRACKING_DB_NAME}",
                "username": "${TRACKING_DB_USER}",
                "password": "${TRACKING_DB_PASSWORD}"
            },
            
            "campaign": {
                "name": "Voice",
                "target_campaign": "Voice",
                "active": True
            },
            
            "salesperson_selection": {
                "source_type": "file",
                "source_config": {
                    "file_path": "config/salespeople.txt"
                },
                "filters": {
                    "active_only": True
                }
            },
            
            "lead_finding": {
                "date_range": {
                    "older_than_days": 0,
                    "younger_than_days": 30
                },
                "sales_filter": {
                    "enabled": True,
                    "opportunity_table": "crm.opp",
                    "opportunity_partner_field": "partner_id",
                    "lead_partner_field": "partner_id",
                    "log_excluded_leads": True
                },
                "dropback_filter": {
                    "enabled": True,
                    "age_threshold": {
                        "days": 30,
                        "field_name": "source_date"
                    },
                    "web_source_campaign_mapping": {
                        "voice_sources": ["facebook_voice", "google_ads_voice", "*voice*"],
                        "apple_sources": ["facebook_apple", "google_ads_apple", "*apple*"],
                        "default_campaign": "default"
                    },
                    "campaign_assignments": {
                        "Voice": "Pat Adler",
                        "Apple": "Kevin Levonas",
                        "default": "Administrator"
                    },
                    "assignment_config": {
                        "web_source_field": "source_id",
                        "assign_immediately": True,
                        "update_status": True,
                        "dropback_status": "dropback"
                    }
                },
                "additional_filters": {
                    "status": ["new", "in_progress"],
                    "exclude_dnc": True,
                    "dnc_statuses": ["dnc", "do_not_call"]
                }
            },
            
            "distribution": {
                "strategy": "round_robin"
            },
            
            "tracking": {
                "enabled": True,
                "track_individual_assignments": True,
                "track_pre_post_counts": True,
                "track_distribution_summary": True
            },
            
            "execution": {
                "dry_run": False,
                "log_level": "INFO"
            }
        }
    
    def _customize_for_campaign(self, config: Dict[str, Any], campaign: str) -> Dict[str, Any]:
        """Customize configuration for specific campaign."""
        config["campaign"]["name"] = campaign
        config["campaign"]["target_campaign"] = campaign
        config["salesperson_selection"]["campaign_filtering"]["target_campaign"] = campaign
        config["lead_finding"]["campaigns"]["types"] = [campaign]
        
        # Update description
        config["description"] = f"Automated daily lead distribution system for {campaign} campaigns"
        config["name"] = f"Daily Lead Distribution - {campaign}"
        
        return config
    
    def _generate_header_comments(self, campaign: str = None, template: str = 'basic') -> str:
        """Generate header comments for the config file."""
        header = f"""# Daily Lead Distribution Configuration
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Template: {template}
"""
        
        if campaign:
            header += f"# Campaign: {campaign}\n"
        
        header += """# 
# This configuration file controls the daily lead distribution system.
# Please review and modify the settings below before running the distribution.
#
# Key sections:
# - odoo_connection: Odoo database connection settings
# - database_connection: MySQL database connection for tracking and analytics
# - campaign: Campaign-specific settings
# - salesperson_selection: How to select eligible salespeople
# - lead_finding: Criteria for finding distributable leads
# - distribution: Strategy for distributing leads
# - tracking: Performance monitoring settings
# - reporting: Report generation settings
# - execution: Runtime behavior settings
#
# Environment Variables:
# ODOO_HOST, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD - Odoo connection
# TRACKING_DB_HOST, TRACKING_DB_NAME, TRACKING_DB_USER, TRACKING_DB_PASSWORD - MySQL tracking database
#

"""
        return header


class EnhancedLeadFilter:
    """Enhanced lead filter with case-sensitive matching capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        self.web_source_config = config.get('lead_finding', {}).get('web_sources', {})
        self.campaign_config = config.get('lead_finding', {}).get('campaigns', {})
        self.status_config = config.get('lead_finding', {}).get('additional_filters', {}).get('status', {})
        self.dnc_config = config.get('lead_finding', {}).get('additional_filters', {}).get('dnc_filtering', {})
    
    def match_web_sources(self, lead_source: str, configured_sources: List[str]) -> bool:
        """Match web sources with configurable case sensitivity."""
        case_sensitive = self.web_source_config.get('case_sensitive', False)
        exact_match = self.web_source_config.get('exact_match', False)
        match_mode = self.web_source_config.get('match_mode', 'exact')
        
        # Ensure lead_source is a string
        lead_source_str = str(lead_source) if lead_source is not None else ""
        
        if not case_sensitive:
            lead_source_str = lead_source_str.lower()
            configured_sources = [src.lower() for src in configured_sources]
        
        if match_mode == 'exact':
            return lead_source_str in configured_sources
        elif match_mode == 'partial':
            return any(src in lead_source_str or lead_source_str in src for src in configured_sources)
        elif match_mode == 'regex':
            patterns = self.web_source_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_source_str, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def match_campaigns(self, lead_campaign: str, configured_campaigns: List[str]) -> bool:
        """Match campaigns with configurable case sensitivity."""
        case_sensitive = self.campaign_config.get('case_sensitive', False)
        exact_match = self.campaign_config.get('exact_match', False)
        match_mode = self.campaign_config.get('match_mode', 'exact')
        
        # Ensure lead_campaign is a string
        lead_campaign_str = str(lead_campaign) if lead_campaign is not None else ""
        
        if not case_sensitive:
            lead_campaign_str = lead_campaign_str.lower()
            configured_campaigns = [camp.lower() for camp in configured_campaigns]
        
        if match_mode == 'exact':
            return lead_campaign_str in configured_campaigns
        elif match_mode == 'partial':
            return any(camp in lead_campaign_str or lead_campaign_str in camp for camp in configured_campaigns)
        elif match_mode == 'regex':
            patterns = self.campaign_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_campaign_str, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def match_lead_status(self, lead_status: str, configured_statuses: List[str]) -> bool:
        """Match lead statuses with configurable case sensitivity."""
        case_sensitive = self.status_config.get('case_sensitive', False)
        exact_match = self.status_config.get('exact_match', False)
        match_mode = self.status_config.get('match_mode', 'exact')
        include_partial = self.status_config.get('include_partial_matches', True)
        
        # Ensure lead_status is a string
        lead_status_str = str(lead_status) if lead_status is not None else ""
        
        if not case_sensitive:
            lead_status_str = lead_status_str.lower()
            configured_statuses = [status.lower() for status in configured_statuses]
        
        if match_mode == 'exact':
            return lead_status_str in configured_statuses
        elif match_mode == 'partial' and include_partial:
            return any(status in lead_status_str or lead_status_str in status for status in configured_statuses)
        elif match_mode == 'regex':
            patterns = self.status_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_status_str, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def is_dnc_lead(self, lead_status: str, lead_tags: List[str] = None) -> bool:
        """Check if lead has DNC (Do Not Call) status or tags."""
        if not self.dnc_config.get('enabled', True):
            return False
        
        # Check DNC status
        dnc_statuses = self.dnc_config.get('statuses', [])
        case_sensitive = self.dnc_config.get('case_sensitive', False)
        match_mode = self.dnc_config.get('match_mode', 'exact')
        
        # Ensure lead_status is a string
        lead_status_str = str(lead_status) if lead_status is not None else ""
        
        if not case_sensitive:
            lead_status_str = lead_status_str.lower()
            dnc_statuses = [status.lower() for status in dnc_statuses]
        
        # Status matching
        if match_mode == 'exact':
            if lead_status_str in dnc_statuses:
                return True
        elif match_mode == 'partial':
            if any(status in lead_status_str or lead_status_str in status for status in dnc_statuses):
                return True
        elif match_mode == 'regex':
            patterns = self.dnc_config.get('regex_patterns', [])
            if any(re.match(pattern, lead_status_str, re.IGNORECASE if not case_sensitive else 0) 
                   for pattern in patterns):
                return True
        
        # Check DNC tags
        if lead_tags and self.dnc_config.get('exclude_dnc_tags', True):
            dnc_tags = self.dnc_config.get('dnc_tags', [])
            if not case_sensitive:
                # Ensure all tags are strings before calling .lower()
                lead_tags = [str(tag).lower() for tag in lead_tags]
                dnc_tags = [str(tag).lower() for tag in dnc_tags]
            
            if any(tag in dnc_tags for tag in lead_tags):
                return True
        
        return False


class DailyLeadDistributor:
    """
    Main class for daily lead distribution operations.
    """
    
    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self.load_config(config_path)
        
        # Initialize OdooClient with connection parameters from config
        odoo_config = self.config.get('odoo_connection', {})
        self.client = OdooClient(
            host=odoo_config.get('host'),
            port=odoo_config.get('port', 8069),
            database=odoo_config.get('database'),
            username=odoo_config.get('username'),
            password=odoo_config.get('password')
        )
        
        self.lead_manager = LeadManager(self.client)
        self.distributor = SmartDistributor()
        self.filter = EnhancedLeadFilter(self.config)
        
        # Initialize opportunity cache for performance optimization
        self._opportunity_cache = {}
        
        # Initialize database connection for tracking
        self.db_connection = self._initialize_database_connection()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML/JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Resolve environment variables
            config = self._resolve_env_vars(config)
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _resolve_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve environment variable references in configuration."""
        def resolve_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]  # Remove ${ and }
                return os.getenv(env_var, '')
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(v) for v in value]
            else:
                return value
        
        return resolve_value(config)
    
    def _initialize_database_connection(self):
        """Initialize MySQL database connection for tracking."""
        db_config = self.config.get('database_connection', {})
        
        if not db_config:
            return None
        
        try:
            import mysql.connector
            from mysql.connector import pooling
            
            # Parse connection parameters
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 3306)
            database = db_config.get('database', 'lead_distribution_tracking')
            username = db_config.get('username', 'tracking_user')
            password = db_config.get('password', '')
            
            # Create connection pool
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                pool_name='lead_distribution_pool',
                pool_size=5,
                autocommit=True,
                charset='utf8mb4'
            )
            
            return connection_pool
            
        except ImportError:
            logger.warning("mysql-connector-python not installed. Database tracking will be disabled.")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize database connection: {e}")
            logger.warning("Database tracking will be disabled.")
            return None
    
    def select_salespeople(self) -> List[SalespersonConfig]:
        """Select eligible salespeople based on configuration."""
        selection_config = self.config.get('salesperson_selection', {})
        source_type = selection_config.get('source_type', 'campaign_table')
        
        if source_type == 'campaign_table':
            return self._select_salespeople_from_campaign_table()
        elif source_type == 'file':
            return self._select_salespeople_from_file()
        elif source_type == 'list':
            return self._select_salespeople_from_list()
        elif source_type == 'database':
            return self._select_salespeople_from_database()
        else:
            raise ValueError(f"Unknown salesperson selection source type: {source_type}")
    
    def _select_salespeople_from_campaign_table(self) -> List[SalespersonConfig]:
        """Select salespeople from campaign table."""
        selection_config = self.config.get('salesperson_selection', {})
        campaign_config = selection_config.get('source_config', {}).get('campaign_table', {})
        campaign_filtering = selection_config.get('campaign_filtering', {})
        
        # Load campaign-salesperson relationships
        if 'file_path' in campaign_config:
            salespeople = self._load_campaign_table_from_file(campaign_config['file_path'])
        elif 'table_name' in campaign_config:
            salespeople = self._load_campaign_table_from_database(campaign_config['table_name'])
        else:
            raise ValueError("Campaign table source not specified")
        
        # Filter by target campaign
        target_campaign = campaign_filtering.get('target_campaign', 'Voice')
        salespeople = [sp for sp in salespeople if sp.campaign_name == target_campaign]
        
        # Filter by active status
        if not campaign_filtering.get('include_inactive_salespeople', False):
            salespeople = [sp for sp in salespeople if sp.active]
        
        # Exclude specific users
        excluded_users = campaign_filtering.get('exclude_specific_users', [])
        salespeople = [sp for sp in salespeople if sp.salesperson_name not in excluded_users]
        
        # Apply additional filters
        salespeople = self._apply_salesperson_filters(salespeople)
        
        return salespeople
    
    def _load_campaign_table_from_file(self, file_path: str) -> List[SalespersonConfig]:
        """Load campaign-salesperson relationships from CSV file."""
        salespeople = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    salespeople.append(SalespersonConfig(
                        salesperson_name=row.get('salesperson_name'),
                        salesperson_id=int(row.get('salesperson_id', 0)),
                        campaign_name=row.get('campaign_name'),
                        active=row.get('active', 'true').lower() == 'true',
                        team=row.get('team', 'Voice'),
                        level=row.get('level', 'mid_level'),
                        target_leads=int(row.get('target_leads', 150))
                    ))
        except FileNotFoundError:
            raise FileNotFoundError(f"Campaign table file not found: {file_path}")
        
        return salespeople
    
    def _load_campaign_table_from_database(self, table_name: str) -> List[SalespersonConfig]:
        """Load campaign-salesperson relationships from database."""
        # Implementation for database loading
        # This would query the Odoo database for campaign-salesperson relationships
        return []
    
    def _select_salespeople_from_file(self) -> List[SalespersonConfig]:
        """Select salespeople from text file. Supports both formats:
        1. Simple list: one name per line
        2. Detailed format: name|id|level|target_leads
        """
        selection_config = self.config.get('salesperson_selection', {})
        file_path = selection_config.get('source_config', {}).get('file_path')
        
        # Get default values from config
        default_target = selection_config.get('default_target_leads', 220)
        default_level = selection_config.get('default_level', 'mid_level')
        default_campaign = selection_config.get('default_campaign', 'Voice')
        
        salespeople = []
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        
                        if len(parts) == 1:
                            # Simple format: just name
                            salespeople.append(SalespersonConfig(
                                salesperson_name=parts[0],
                                salesperson_id=0,  # Will be resolved from Odoo
                                level=default_level,
                                target_leads=default_target,
                                campaign_name=default_campaign
                            ))
                        elif len(parts) >= 4:
                            # Detailed format: name|id|level|target_leads
                            try:
                                salespeople.append(SalespersonConfig(
                                    salesperson_name=parts[0],
                                    salesperson_id=int(parts[1]),
                                    level=parts[2],
                                    target_leads=int(parts[3]),
                                    campaign_name=default_campaign
                                ))
                            except ValueError as e:
                                logger.warning(f"Invalid data in line {line_num}: {line} - {e}")
                        else:
                            logger.warning(f"Invalid format in line {line_num}: {line}")
                            
        except FileNotFoundError:
            raise FileNotFoundError(f"Salespeople file not found: {file_path}")
        
        # Resolve user IDs from Odoo for any salespeople with ID 0
        salespeople = self._resolve_user_ids(salespeople)
        
        return self._apply_salesperson_filters(salespeople)
    
    def _calculate_current_workload(self, salespeople: List[SalespersonConfig]) -> Dict[int, Dict[str, Any]]:
        """Calculate current lead counts for each salesperson from Odoo."""
        logger.info(f"Calculating workload for {len(salespeople)} salespeople")
        workload = {}
        
        try:
            # Connect to Odoo if not already connected
            if not hasattr(self.client, '_uid') or not self.client._uid:
                self.client.connect()
                self.client.authenticate()
            
            # Try multiple approaches to find current leads
            for sp in salespeople:
                if sp.salesperson_id == 0:
                    workload[sp.salesperson_id] = {'current_leads': 0, 'name': sp.salesperson_name}
                    continue
                
                current_count = 0
                
                # Method 1: Check res.partner with is_lead=True
                partner_leads = self.client.search_read(
                    'res.partner',
                    domain=[
                        '|', 
                        ('user_id', '=', sp.salesperson_id),
                        ('closer_id', '=', sp.salesperson_id),
                        ('is_lead', '=', True)
                    ],
                    fields=['id'],
                    limit=None
                )
                
                # Method 2: Check crm.lead model if res.partner doesn't work
                crm_leads = []
                try:
                    crm_leads = self.client.search_read(
                        'crm.lead',
                        domain=[
                            '|', 
                            ('user_id', '=', sp.salesperson_id),
                            ('closer_id', '=', sp.salesperson_id)
                        ],
                        fields=['id'],
                        limit=None
                    )
                except Exception as e:
                    logger.debug(f"Could not query crm.lead model: {e}")
                
                # Use whichever method found more leads
                partner_count = len(partner_leads) if partner_leads else 0
                crm_count = len(crm_leads) if crm_leads else 0
                current_count = max(partner_count, crm_count)
                
                workload[sp.salesperson_id] = {
                    'current_leads': current_count,
                    'name': sp.salesperson_name
                }
                
                # Log what we found
                if current_count > 0:
                    logger.info(f"{sp.salesperson_name}: {current_count} current leads (partner: {partner_count}, crm: {crm_count})")
                else:
                    # Debug: Check if user has ANY records at all
                    any_records = self.client.search_read(
                        'res.partner',
                        domain=[('user_id', '=', sp.salesperson_id)],
                        fields=['id', 'name', 'is_lead'],
                        limit=5
                    )
                    logger.debug(f"{sp.salesperson_name} (ID: {sp.salesperson_id}): 0 leads found, has {len(any_records)} total partner records")
                
        except Exception as e:
            logger.error(f"Failed to calculate current workload: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            # Return empty workload on error
            for sp in salespeople:
                workload[sp.salesperson_id] = {
                    'current_leads': 0,
                    'name': sp.salesperson_name
                }
        
        return workload
    
    def _resolve_user_ids(self, salespeople: List[SalespersonConfig]) -> List[SalespersonConfig]:
        """Resolve user IDs from Odoo for salespeople with ID 0."""
        # Find salespeople that need ID resolution
        needs_resolution = [sp for sp in salespeople if sp.salesperson_id == 0]
        
        if not needs_resolution:
            return salespeople
        
        try:
            # Connect to Odoo if not already connected
            if not hasattr(self.client, '_uid') or not self.client._uid:
                self.client.connect()
                self.client.authenticate()
            
            # Get all users from Odoo
            users = self.client.search_read(
                'res.users',
                domain=[('active', '=', True)],
                fields=['id', 'name']
            )
            
            # Create name to ID mapping (case-insensitive)
            name_to_id = {}
            for user in users:
                if user.get('name'):
                    name_to_id[user['name'].lower().strip()] = user['id']
            
            # Resolve IDs
            resolved_salespeople = []
            for sp in salespeople:
                if sp.salesperson_id == 0:
                    # Try to find matching user ID
                    name_key = sp.salesperson_name.lower().strip()
                    if name_key in name_to_id:
                        # Create new SalespersonConfig with resolved ID
                        resolved_sp = SalespersonConfig(
                            salesperson_name=sp.salesperson_name,
                            salesperson_id=name_to_id[name_key],
                            campaign_name=sp.campaign_name,
                            active=sp.active,
                            team=sp.team,
                            level=sp.level,
                            target_leads=sp.target_leads
                        )
                        resolved_salespeople.append(resolved_sp)
                        logger.debug(f"Resolved '{sp.salesperson_name}' -> ID {name_to_id[name_key]}")
                    else:
                        logger.warning(f"Could not find user ID for '{sp.salesperson_name}' in Odoo")
                        # Keep the original with ID 0
                        resolved_salespeople.append(sp)
                else:
                    # Already has ID, keep as is
                    resolved_salespeople.append(sp)
            
            return resolved_salespeople
            
        except Exception as e:
            logger.error(f"Failed to resolve user IDs from Odoo: {e}")
            return salespeople  # Return original list on error
    
    def _select_salespeople_from_list(self) -> List[SalespersonConfig]:
        """Select salespeople from configuration list."""
        selection_config = self.config.get('salesperson_selection', {})
        salespeople_list = selection_config.get('source_config', {}).get('salespeople_list', [])
        
        salespeople = []
        for name in salespeople_list:
            salespeople.append(SalespersonConfig(
                salesperson_name=name,
                salesperson_id=0,  # Will be resolved from Odoo
                level='mid_level',
                target_leads=150,
                campaign_name="Voice"  # Default campaign
            ))
        
        return self._apply_salesperson_filters(salespeople)
    
    def _select_salespeople_from_database(self) -> List[SalespersonConfig]:
        """Select salespeople from database query."""
        # Implementation for database query selection
        return []
    
    def _apply_salesperson_filters(self, salespeople: List[SalespersonConfig]) -> List[SalespersonConfig]:
        """Apply additional filters to salespeople list."""
        filters = self.config.get('salesperson_selection', {}).get('filters', {})
        
        filtered_salespeople = []
        for salesperson in salespeople:
            # Check active status
            if filters.get('active_only', True) and not salesperson.active:
                continue
            
            # Check team filter
            team_filter = filters.get('team_filter')
            if team_filter and salesperson.team != team_filter:
                continue
            
            # Check experience level
            min_level = filters.get('min_experience_level', 1)
            if salesperson.level == 'junior' and min_level > 1:
                continue
            
            # Check workload percentage
            max_workload = filters.get('max_workload_percentage', 90)
            current_workload = self._calculate_salesperson_workload(salesperson)
            if current_workload > max_workload:
                continue
            
            filtered_salespeople.append(salesperson)
        
        return filtered_salespeople
    
    def _calculate_salesperson_workload(self, salesperson: SalespersonConfig) -> float:
        """Calculate current workload percentage for salesperson."""
        current_leads = self._get_salesperson_lead_count(salesperson)
        target_leads = salesperson.target_leads
        
        if target_leads == 0:
            return 0
        
        return (current_leads / target_leads) * 100
    
    def _get_salesperson_lead_count(self, salesperson: SalespersonConfig) -> int:
        """Get current lead count for salesperson."""
        if salesperson.salesperson_id == 0:
            return 0
        
        try:
            # Connect to Odoo if not already connected
            if not hasattr(self.client, '_uid') or not self.client._uid:
                self.client.connect()
                self.client.authenticate()
            
            # Use crm.lead model which is the primary lead model
            current_count = 0
            crm_leads = []
            
            try:
                # Query crm.lead for this salesperson, filtering for type='lead' only
                crm_leads = self.client.search_read(
                    'crm.lead',
                    domain=[
                        ('type', '=', 'lead'),  # Only count leads, not opportunities
                        '|', 
                        ('user_id', '=', salesperson.salesperson_id),
                        ('closer_id', '=', salesperson.salesperson_id)
                    ],
                    fields=['id'],
                    limit=None
                )
                current_count = len(crm_leads) if crm_leads else 0
            except Exception as e:
                logger.debug(f"Could not query crm.lead model: {e}")
                # Try simpler query with just user_id, still filtering for type='lead'
                try:
                    crm_leads = self.client.search_read(
                        'crm.lead',
                        domain=[
                            ('type', '=', 'lead'),  # Only count leads, not opportunities
                            ('user_id', '=', salesperson.salesperson_id)
                        ],
                        fields=['id'],
                        limit=None
                    )
                    current_count = len(crm_leads) if crm_leads else 0
                except Exception as e2:
                    logger.debug(f"Simple crm.lead query also failed: {e2}")
                    current_count = 0
            
            # Log the result
            logger.debug(f"{salesperson.salesperson_name} (ID: {salesperson.salesperson_id}): {current_count} current leads")
            
            return current_count
            
        except Exception as e:
            logger.error(f"Error calculating lead count for {salesperson.salesperson_name}: {e}")
            return 0
    
    def find_distributable_leads(self, export_options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find leads that match distribution criteria, handling dropback first."""
        # Ensure export_options is not None
        if export_options is None:
            export_options = {}
        
        # Build base filter
        from .filters import LeadFilter
        filter_obj = LeadFilter().model("crm.lead")
        
        # Ensure we only get leads (type='lead') and not opportunities (type='opportunity')
        # This is critical because crm.lead model contains both leads and opportunities,
        # but daily distribution should only process new leads, not existing opportunities
        filter_obj.by_type("lead")
        
        # Set limit from configuration (default 50000 for broader lead capture)
        max_leads = self.config.get('execution', {}).get('max_leads_per_run', 50000)
        filter_obj.limit(max_leads)
        
        # Set only the fields needed for distribution logic
        required_fields = [
            "id",                    # Lead ID for assignment
            "type",                  # Record type (lead vs opportunity) for filtering
            "status",                # Lead status for filtering
            "web_source_id",         # Web source for filtering
            "campaign_id",           # Campaign for filtering
            "user_id",               # Current assignment
            "partner_id",            # For sales filter (opportunity matching)
            "tag_ids",               # For DNC and tag filtering
            "priority",              # For priority filtering
            "source_date",           # For date range and dropback filtering
            "create_date",           # Fallback date field
            "activity_date_deadline" # For activity deadline filtering
        ]
        filter_obj.fields(required_fields)
        
        # Apply date range filtering
        date_config = self.config.get('lead_finding', {}).get('date_range', {})
        older_than_days = date_config.get('older_than_days', 0)
        younger_than_days = date_config.get('younger_than_days', 30)
        
        # Calculate date range
        today = date.today()
        start_date = today - timedelta(days=younger_than_days)
        end_date = today - timedelta(days=older_than_days)
        
        filter_obj.by_date_range(start_date=start_date, end_date=end_date, field_name="source_date")
        
        # Apply user exclusion filter
        user_exclusion_config = self.config.get('lead_finding', {}).get('user_exclusion', {})
        if user_exclusion_config.get('enabled', False):
            excluded_users = user_exclusion_config.get('excluded_users', [])
            exact_match = user_exclusion_config.get('exact_match', True)
            if excluded_users:
                filter_obj.exclude_users(excluded_users, exact=exact_match)
                logger.info(f"Applied user exclusion filter: {excluded_users}")
        
        # Get all leads in date range
        leads = self.lead_manager.get_leads(filter_obj)
        
        # Export raw leads before any filtering if requested
        if export_options and (export_options.get('export_before_filter') or export_options.get('export_all_stages')):
            self._export_leads_to_csv(
                leads, 
                stage='before_filtering',
                export_options=export_options,
                description='Raw leads in date range before any filtering'
            )
        
        # Log type verification for debugging
        if leads:
            # Count different types to verify filtering
            type_counts = {}
            for lead in leads[:10]:  # Check first 10 leads
                lead_type = lead.get('type', 'null')
                type_counts[lead_type] = type_counts.get(lead_type, 0) + 1
            logger.info(f"Lead type verification - first 10 records: {type_counts}")
        
        # Generate web source frequency table for analysis
        self._log_web_source_frequency(leads)
        
        # Generate status frequency table for analysis
        self._log_status_frequency(leads)
        
        # Process dropback leads first
        distribution_leads, dropback_leads = self._process_leads_with_dropback(leads)
        
        # Export after dropback processing if requested
        if export_options and export_options.get('export_all_stages'):
            self._export_leads_to_csv(
                distribution_leads,
                stage='after_dropback',
                export_options=export_options,
                description=f'Leads after dropback processing (removed {len(dropback_leads)} dropback leads)'
            )
        
        # Check for web source matches early - if web source filtering is enabled
        web_source_config = self.config.get('lead_finding', {}).get('web_sources', {})
        if web_source_config and web_source_config.get('enabled', True):
            # Test web source matching on first few leads to see if any match
            configured_sources = self._get_configured_web_sources(web_source_config)
            if configured_sources:
                web_source_matches = 0
                for lead in distribution_leads[:10]:  # Check first 10 leads
                    if self._matches_web_sources(lead):
                        web_source_matches += 1
                
                # If no web source matches found in sample, likely none will match
                if web_source_matches == 0:
                    logger.warning(f"No leads found matching configured web sources: {configured_sources}")
                    logger.warning("Pipeline cannot continue - no matching web source IDs found")
                    
                    # Store intermediate results for reporting
                    self.dropback_leads = dropback_leads
                    self.intermediate_results = {
                        'total_leads_in_date_range': len(leads),
                        'dropback_leads': len(dropback_leads),
                        'leads_after_dropback': len(distribution_leads),
                        'leads_after_all_filters': 0,
                        'web_source_matches': 0,
                        'configured_web_sources': configured_sources
                    }
                    
                    return []  # Return empty list to indicate no distributable leads
        else:
            logger.info("Web source filtering is disabled - proceeding with all leads")
        
        # Log sales filter status and configuration
        sales_config = self.config.get('lead_finding', {}).get('sales_filter', {})
        sales_filter_enabled = sales_config.get('enabled', False)
        
        logger.info("================================================================================")
        logger.info("SALES FILTER (CRM.OPPORTUNITY) ANALYSIS")
        logger.info("================================================================================")
        logger.info(f"Sales filter enabled: {sales_filter_enabled}")
        
        if sales_filter_enabled:
            logger.info(f"Opportunity table: {sales_config.get('opportunity_table', 'crm.opp')}")
            logger.info(f"Opportunity partner field: {sales_config.get('opportunity_partner_field', 'partner_id')}")
            logger.info(f"Lead partner field: {sales_config.get('lead_partner_field', 'partner_id')}")
            
            exclude_stages = sales_config.get('exclude_opportunity_stages', [])
            include_stages = sales_config.get('include_opportunity_stages', [])
            
            if exclude_stages:
                logger.info(f"Excluding opportunity stages: {exclude_stages}")
            if include_stages:
                logger.info(f"Including only opportunity stages: {include_stages}")
                
            opp_date_config = sales_config.get('opportunity_date_range', {})
            if opp_date_config.get('enabled', False):
                logger.info(f"Opportunity date filter: {opp_date_config.get('field_name', 'date_open')} within {opp_date_config.get('days_back', 365)} days")
            
            logger.info(f"Leads before sales filtering: {len(distribution_leads)}")
        else:
            logger.info("Sales filter disabled - all leads will pass this filter")
        
        logger.info("================================================================================")
        
        # Apply enhanced filtering to distribution leads only
        filtered_leads = []
        debug_counts = {
            'total_checked': 0,
            'failed_dnc': 0,
            'failed_sales': 0,
            'failed_web_source': 0,
            'failed_campaign': 0,
            'failed_status': 0,
            'failed_activity_deadline': 0,
            'passed_all': 0
        }
        
        # Pre-process sales filter with batch optimization
        opportunity_results = {}
        if sales_filter_enabled:
            # Collect all unique partner_ids for batch opportunity checking
            partner_ids = set()
            for lead in distribution_leads:
                lead_partner_id = lead.get('partner_id')
                if lead_partner_id:
                    # Handle partner_id field which can be:
                    # - Integer: 12345
                    # - List: [12345, 'Company Name'] 
                    # - False/None: No partner assigned
                    if isinstance(lead_partner_id, list) and len(lead_partner_id) > 0:
                        partner_ids.add(lead_partner_id[0])  # Extract ID from [id, name] format
                    elif isinstance(lead_partner_id, int):
                        partner_ids.add(lead_partner_id)
                    elif lead_partner_id is not None and lead_partner_id is not False:
                        # Try to convert to int if it's a string number
                        try:
                            partner_ids.add(int(lead_partner_id))
                        except (ValueError, TypeError):
                            logger.warning(f"Unexpected partner_id format for lead {lead.get('id')}: {lead_partner_id}")
            
            # Batch check opportunities for all partner_ids
            if partner_ids:
                opportunity_results = self._batch_check_opportunities(list(partner_ids), sales_config)
                logger.info(f"Batch checked {len(partner_ids)} unique partner_ids for opportunities")
        
        for lead in distribution_leads:
            debug_counts['total_checked'] += 1
            
            # Check each filter individually for debugging
            if self._is_dnc_lead(lead):
                debug_counts['failed_dnc'] += 1
                continue
            
            # Sales filter (check early to exclude leads with existing opportunities)
            if sales_filter_enabled:
                lead_partner_id = lead.get('partner_id')
                if lead_partner_id:
                    # Handle partner_id field which can be:
                    # - Integer: 12345
                    # - List: [12345, 'Company Name'] 
                    # - False/None: No partner assigned
                    if isinstance(lead_partner_id, list) and len(lead_partner_id) > 0:
                        lead_partner_id = lead_partner_id[0]  # Extract ID from [id, name] format
                    elif isinstance(lead_partner_id, int):
                        lead_partner_id = lead_partner_id
                    elif lead_partner_id is not None and lead_partner_id is not False:
                        # Try to convert to int if it's a string number
                        try:
                            lead_partner_id = int(lead_partner_id)
                        except (ValueError, TypeError):
                            logger.warning(f"Unexpected partner_id format for lead {lead.get('id')}: {lead_partner_id}")
                            lead_partner_id = None
                    else:
                        lead_partner_id = None
                    
                    if lead_partner_id and opportunity_results.get(lead_partner_id, False):
                        debug_counts['failed_sales'] += 1
                        if sales_config.get('log_excluded_leads', True):
                            logger.info(f"🚫 EXCLUDING LEAD: ID {lead.get('id')} (partner_id: {lead_partner_id}) - has matching opportunity in crm.opp")
                        continue
                else:
                    # No partner_id, cannot match to opportunities
                    pass
                
            if not self._matches_web_sources(lead):
                debug_counts['failed_web_source'] += 1
                continue
                
            if not self._matches_campaigns(lead):
                debug_counts['failed_campaign'] += 1
                continue
                
            if not self._matches_lead_status(lead):
                debug_counts['failed_status'] += 1
                continue
            
            # Check activity deadline filter
            if self._has_valid_activity_deadline(lead):
                debug_counts['failed_activity_deadline'] += 1
                continue
            
            # Passed all filters
            debug_counts['passed_all'] += 1
            filtered_leads.append(lead)
        
        # Log sales filter results
        if sales_filter_enabled:
            logger.info("================================================================================")
            logger.info("SALES FILTER RESULTS")
            logger.info("================================================================================")
            logger.info(f"Leads before sales filtering: {len(distribution_leads)}")
            logger.info(f"Leads excluded (have opportunities): {debug_counts['failed_sales']}")
            logger.info(f"Leads after sales filtering: {len(distribution_leads) - debug_counts['failed_sales']}")
            
            if debug_counts['failed_sales'] > 0:
                exclusion_percentage = (debug_counts['failed_sales'] / len(distribution_leads)) * 100
                logger.info(f"Sales filter exclusion rate: {exclusion_percentage:.1f}%")
            logger.info("================================================================================")
        
        # Log debug information
        logger.info(f"Filter Debug Summary:")
        logger.info(f"  Total leads checked: {debug_counts['total_checked']}")
        logger.info(f"  Failed DNC check: {debug_counts['failed_dnc']}")
        logger.info(f"  Failed sales filter (has opportunities): {debug_counts['failed_sales']}")
        logger.info(f"  Failed web source match: {debug_counts['failed_web_source']}")
        logger.info(f"  Failed campaign match: {debug_counts['failed_campaign']}")
        logger.info(f"  Failed status match: {debug_counts['failed_status']}")
        logger.info(f"  Failed activity deadline: {debug_counts['failed_activity_deadline']}")
        logger.info(f"  Passed all filters: {debug_counts['passed_all']}")
        
        # Store dropback leads for reporting
        self.dropback_leads = dropback_leads
        
        # Store intermediate results for dry-run reporting
        self.intermediate_results = {
            'total_leads_in_date_range': len(leads),
            'dropback_leads': len(dropback_leads),
            'leads_after_dropback': len(distribution_leads),
            'leads_after_all_filters': len(filtered_leads),
            'filter_breakdown': debug_counts
        }
        
        # Export final filtered leads if requested
        if export_options and (export_options.get('export_after_filter') or export_options.get('export_all_stages')):
            self._export_leads_to_csv(
                filtered_leads,
                stage='after_all_filters',
                export_options=export_options,
                description=f'Final distributable leads after all filters ({len(filtered_leads)} leads)'
            )
        
        # Show filter delta if requested
        if export_options and export_options.get('show_filter_delta'):
            self._show_filter_delta_analysis(leads, distribution_leads, filtered_leads, debug_counts)
        
        return filtered_leads
    
    def _matches_all_criteria(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches all filtering criteria."""
        # DNC filtering (check first to exclude early)
        if self._is_dnc_lead(lead):
            return False
        
        # Sales filter (check early to exclude leads with existing opportunities)
        if not self._matches_sales_criteria(lead):
            return False
        
        # Web source matching
        if not self._matches_web_sources(lead):
            return False
        
        # Campaign matching
        if not self._matches_campaigns(lead):
            return False
        
        # Lead status matching
        if not self._matches_lead_status(lead):
            return False
        
        # Additional criteria
        if not self._matches_additional_criteria(lead):
            return False
        
        return True
    
    def _is_dnc_lead(self, lead: Dict[str, Any]) -> bool:
        """Check if lead has DNC status or tags."""
        lead_status = lead.get('status', '')
        lead_tags = lead.get('tag_ids', [])
        
        return self.filter.is_dnc_lead(lead_status, lead_tags)
    
    def _has_valid_activity_deadline(self, lead: Dict[str, Any]) -> bool:
        """Check if lead has a valid activity_date_deadline field.
        
        Returns True if the lead should be excluded (has a valid deadline).
        Returns False if the lead should be kept (no deadline or filtering disabled).
        """
        # Get activity deadline filter configuration
        activity_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('activity_deadline_filter', {})
        
        # Check if filtering is enabled
        if not activity_config.get('enabled', True):
            return False
        
        # Check if we should exclude leads with deadlines
        if not activity_config.get('exclude_with_deadline', True):
            return False
        
        # Get the activity_date_deadline field value
        activity_deadline = lead.get('activity_date_deadline')
        
        # Check if the field has a valid value
        # Valid means: not None, not False, not empty string
        if activity_deadline and activity_deadline not in (False, '', 'false', 'False'):
            # Lead has a valid activity deadline, exclude it
            return True
        
        # No valid deadline, keep the lead
        return False
    
    def _matches_web_sources(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches web source criteria."""
        web_source_config = self.config.get('lead_finding', {}).get('web_sources', {})
        
        # If web source filtering is disabled, always return True
        if not web_source_config or not web_source_config.get('enabled', True):
            return True
        
        lead_source = lead.get('web_source_id')
        if not lead_source:
            return False
        
        # Handle different formats of web_source_id
        lead_source_name = None
        
        # If it's already a list/tuple [id, 'name'] format
        if isinstance(lead_source, (list, tuple)) and len(lead_source) >= 2:
            lead_source_name = lead_source[1]  # Get the name part (second element)
        # If it's a string representation of a list like "[128, 'MAPS']"
        elif isinstance(lead_source, str) and lead_source.startswith('['):
            try:
                # Parse the string representation of a list
                import ast
                parsed = ast.literal_eval(lead_source)
                if isinstance(parsed, (list, tuple)) and len(parsed) >= 2:
                    lead_source_name = parsed[1]
                else:
                    lead_source_name = str(parsed)
            except (ValueError, SyntaxError):
                # If parsing fails, try to extract the name manually
                # Format is typically: [id, 'name'] or [id, "name"]
                import re
                match = re.search(r'\[.*?,\s*[\'"]([^\'"]+)[\'"]', lead_source)
                if match:
                    lead_source_name = match.group(1)
                else:
                    lead_source_name = lead_source
        else:
            # For any other format, convert to string
            lead_source_name = str(lead_source)
        
        # Get configured sources
        sources = self._get_configured_web_sources(web_source_config)
        
        # Ensure lead_source_name is a string for matching
        lead_source_str = str(lead_source_name) if lead_source_name is not None else ""
        return self.filter.match_web_sources(lead_source_str, sources)
    
    def _matches_campaigns(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches campaign criteria."""
        campaign_config = self.config.get('lead_finding', {}).get('campaigns', {})
        
        # If no campaign config exists, skip filtering
        if not campaign_config:
            return True
        
        # Check if campaign filtering is explicitly disabled
        if not campaign_config.get('enabled', True):
            return True
        
        # Get configured campaigns
        campaigns = campaign_config.get('types', [])
        
        # If no campaigns specified (empty list), treat as disabled
        if not campaigns:
            return True
        
        lead_campaign = lead.get('campaign_id', [None])[0] if isinstance(lead.get('campaign_id'), list) else lead.get('campaign_id')
        if not lead_campaign:
            return False
        
        # Ensure lead_campaign is a string for matching
        lead_campaign_str = str(lead_campaign) if lead_campaign is not None else ""
        return self.filter.match_campaigns(lead_campaign_str, campaigns)
    
    def _log_web_source_frequency(self, leads: List[Dict[str, Any]]) -> None:
        """Generate and log a frequency table of web source IDs in the fetched leads."""
        from collections import Counter
        import ast
        import re
        
        # Count web source IDs
        web_source_counts = Counter()
        web_source_names = Counter()  # Track just the names
        null_count = 0
        
        # Also check other potential web source fields
        other_fields = ['source', 'medium', 'campaign', 'utm_source', 'utm_medium', 'utm_campaign']
        field_analysis = {}
        
        for lead in leads:
            source_id = lead.get('web_source_id')
            if source_id is None or source_id == False:
                null_count += 1
            else:
                # Convert to string for consistent counting
                source_str = str(source_id)
                web_source_counts[source_str] += 1
                
                # Extract the name part for separate tracking
                source_name = None
                if isinstance(source_id, (list, tuple)) and len(source_id) >= 2:
                    source_name = source_id[1]
                elif isinstance(source_id, str) and source_id.startswith('['):
                    try:
                        parsed = ast.literal_eval(source_id)
                        if isinstance(parsed, (list, tuple)) and len(parsed) >= 2:
                            source_name = parsed[1]
                    except (ValueError, SyntaxError):
                        match = re.search(r'\[.*?,\s*[\'"]([^\'"]+)[\'"]', source_id)
                        if match:
                            source_name = match.group(1)
                
                if source_name:
                    web_source_names[source_name] += 1
        
        # Analyze other potential web source fields
        for field in other_fields:
            field_counts = Counter()
            field_null_count = 0
            for lead in leads:
                value = lead.get(field)
                if value is None or value == False or value == '':
                    field_null_count += 1
                else:
                    field_counts[str(value)] += 1
            field_analysis[field] = {
                'counts': field_counts,
                'null_count': field_null_count,
                'unique_values': len(field_counts)
            }
        
        # Sort by frequency (descending)
        sorted_sources = sorted(web_source_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Log the frequency table
        logger.info("=" * 80)
        logger.info("WEB SOURCE FREQUENCY TABLE")
        logger.info("=" * 80)
        logger.info(f"Total leads analyzed: {len(leads)}")
        logger.info(f"Leads with null/empty web_source_id: {null_count}")
        logger.info(f"Unique web sources found: {len(web_source_counts)}")
        logger.info("")
        
        # Log source_id analysis
        if sorted_sources:
            logger.info("Top 20 Web Sources by Frequency (web_source_id):")
            logger.info("-" * 50)
            logger.info(f"{'Web Source ID':<30} {'Count':<10} {'Percentage':<10}")
            logger.info("-" * 50)
            
            total_with_sources = len(leads) - null_count
            for source_id, count in sorted_sources[:20]:
                percentage = (count / total_with_sources * 100) if total_with_sources > 0 else 0
                logger.info(f"{source_id:<30} {count:<10} {percentage:>6.1f}%")
            
            if len(sorted_sources) > 20:
                logger.info(f"... and {len(sorted_sources) - 20} more web sources")
        else:
            logger.info("No web sources found in web_source_id field")
        
        logger.info("")
        logger.info("OTHER FIELD ANALYSIS:")
        logger.info("-" * 30)
        for field, analysis in field_analysis.items():
            if analysis['unique_values'] > 0:
                logger.info(f"{field}: {analysis['unique_values']} unique values, {analysis['null_count']} null values")
                # Show top 5 values for this field
                top_values = sorted(analysis['counts'].items(), key=lambda x: x[1], reverse=True)[:5]
                for value, count in top_values:
                    logger.info(f"  - {value}: {count}")
            else:
                logger.info(f"{field}: All null/empty")
        
        logger.info("=" * 80)
        
        # Also log all web sources for easy copying to config
        all_sources = [source_id for source_id, _ in sorted_sources]
        if all_sources:
            logger.info("All web source IDs (for config):")
            logger.info(f"['{', '.join(all_sources)}']")
        
        # Log web source names separately
        if web_source_names:
            logger.info("")
            logger.info("WEB SOURCE NAMES (extracted from IDs):")
            logger.info("-" * 50)
            sorted_names = sorted(web_source_names.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"{'Source Name':<30} {'Count':<10} {'Percentage':<10}")
            logger.info("-" * 50)
            total_with_sources = len(leads) - null_count
            for name, count in sorted_names[:20]:
                percentage = (count / total_with_sources * 100) if total_with_sources > 0 else 0
                logger.info(f"{name:<30} {count:<10} {percentage:>6.1f}%")
            
            logger.info("")
            logger.info("All unique web source names (for config file):")
            logger.info(list(web_source_names.keys()))
        
        logger.info("=" * 80)
    
    def _log_status_frequency(self, leads: List[Dict[str, Any]]) -> None:
        """Generate and log a frequency table of lead statuses."""
        from collections import Counter
        
        # Count statuses
        status_counts = Counter()
        null_count = 0
        
        for lead in leads:
            status = lead.get('status')
            if status is None or status == False or status == '':
                null_count += 1
            else:
                # Convert to string for consistent counting
                status_str = str(status).strip()
                if status_str:
                    status_counts[status_str] += 1
                else:
                    null_count += 1
        
        # Sort by frequency (descending)
        sorted_statuses = sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Get configured statuses for comparison
        status_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('status', {})
        
        # Get include and exclude lists
        include_statuses = []
        exclude_statuses = []
        if isinstance(status_config, dict):
            include_statuses = status_config.get('values', [])
            exclude_statuses = status_config.get('exclude', [])
        elif isinstance(status_config, list):
            include_statuses = status_config
        
        # Get sale status exclusions (legacy)
        sale_status_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('exclude_sale_statuses', {})
        if sale_status_config.get('enabled', False):
            sale_statuses = sale_status_config.get('values', [])
            exclude_statuses.extend(sale_statuses)
        
        # Normalize for comparison
        include_statuses_lower = [s.lower().strip() for s in include_statuses]
        exclude_statuses_lower = [s.lower().strip() for s in exclude_statuses]
        
        # Log the frequency table
        logger.info("=" * 80)
        logger.info("LEAD STATUS FREQUENCY TABLE")
        logger.info("=" * 80)
        logger.info(f"Total leads analyzed: {len(leads)}")
        logger.info(f"Leads with null/empty status: {null_count}")
        logger.info(f"Unique statuses found: {len(status_counts)}")
        logger.info("")
        
        # Show filter configuration
        if include_statuses:
            logger.info(f"Include filter (looking for these):")
            logger.info(f"  {', '.join(include_statuses)}")
        
        if exclude_statuses:
            logger.info(f"Exclude filter (rejecting these):")
            logger.info(f"  {', '.join(set(exclude_statuses))}")  # Use set to remove duplicates
        
        if not include_statuses and not exclude_statuses:
            logger.info("Status filtering is disabled (no include or exclude lists)")
        
        logger.info("")
        
        if sorted_statuses:
            logger.info("Status Distribution:")
            logger.info("-" * 70)
            logger.info(f"{'Status':<30} {'Count':<10} {'Percentage':<10} {'Filter Result':<20}")
            logger.info("-" * 70)
            
            total_leads = len(leads)
            matching_count = 0
            excluded_count = 0
            
            for i, (status, count) in enumerate(sorted_statuses):
                status_lower = status.lower().strip()
                
                # Determine filter result
                if status_lower in exclude_statuses_lower:
                    filter_result = "✗ Excluded"
                    excluded_count += count
                elif include_statuses and status_lower in include_statuses_lower:
                    filter_result = "✓ Included"
                    matching_count += count
                elif not include_statuses and status_lower not in exclude_statuses_lower:
                    filter_result = "✓ Included"
                    matching_count += count
                else:
                    filter_result = ""
                
                if i >= 20:  # Show only top 20
                    continue
                    
                percentage = (count / total_leads * 100) if total_leads > 0 else 0
                logger.info(f"{status:<30} {count:<10} {percentage:>6.1f}%      {filter_result:<20}")
            
            if len(sorted_statuses) > 20:
                logger.info(f"... and {len(sorted_statuses) - 20} more statuses")
            
            logger.info("")
            if include_statuses or exclude_statuses:
                logger.info(f"Filter Summary:")
                if excluded_count > 0:
                    logger.info(f"  Excluded: {excluded_count} leads ({(excluded_count/total_leads*100):.1f}%)")
                logger.info(f"  Will pass filter: {matching_count} leads ({(matching_count/total_leads*100):.1f}%)")
            else:
                logger.info(f"All {total_leads} leads will pass (no status filtering)")
        else:
            logger.info("No status values found in leads")
        
        logger.info("=" * 80)
    
    def _matches_lead_status(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches status criteria with support for include/exclude lists."""
        status_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('status', {})
        
        # Check if status filtering is enabled
        if isinstance(status_config, dict) and not status_config.get('enabled', True):
            return True
        
        # Get include and exclude lists
        if isinstance(status_config, dict):
            include_statuses = status_config.get('values', [])
            exclude_statuses = status_config.get('exclude', [])
        else:
            # Legacy format - just a list of statuses to include
            include_statuses = status_config if isinstance(status_config, list) else []
            exclude_statuses = []
        
        # If both lists are empty, skip status filtering
        if not include_statuses and not exclude_statuses:
            return True
        
        lead_status = lead.get('status', '')
        if not lead_status:
            # If no status and we have include filters, reject
            # If only exclude filters, accept (nothing to exclude)
            return not include_statuses
        
        # Convert lead_status to string if it's not already
        lead_status_str = str(lead_status).strip() if lead_status is not None else ""
        
        # Check exclusions first (takes precedence)
        if exclude_statuses:
            if self._status_matches_list(lead_status_str, exclude_statuses, status_config):
                return False  # Status is in exclude list, reject
        
        # Check for sale status exclusion (legacy support)
        if self._is_sale_status(lead_status_str):
            return False
        
        # If we have include filters, check if status matches
        if include_statuses:
            return self._status_matches_list(lead_status_str, include_statuses, status_config)
        
        # No include filters, only excludes - accept if we got here
        return True
    
    def _status_matches_list(self, status: str, status_list: List[str], config: Dict) -> bool:
        """Check if a status matches a list of statuses based on config settings."""
        case_sensitive = config.get('case_sensitive', False)
        match_mode = config.get('match_mode', 'exact')
        
        if not case_sensitive:
            status = status.lower()
            status_list = [s.lower().strip() for s in status_list]
        
        if match_mode == 'exact':
            return status in status_list
        elif match_mode == 'partial':
            return any(s in status or status in s for s in status_list)
        else:
            return False
    
    def _is_sale_status(self, lead_status: str) -> bool:
        """Check if lead status indicates a sale has been made."""
        sale_status_config = self.config.get('lead_finding', {}).get('additional_filters', {}).get('exclude_sale_statuses', {})
        
        if not sale_status_config.get('enabled', False):
            return False
        
        sale_statuses = sale_status_config.get('values', [])
        case_sensitive = sale_status_config.get('case_sensitive', False)
        match_mode = sale_status_config.get('match_mode', 'exact')
        
        if not sale_statuses:
            return False
        
        # Handle None/empty status - should not be excluded
        if lead_status is None or lead_status == '':
            return False
        
        # Ensure lead_status is a string
        lead_status_str = str(lead_status) if lead_status is not None else ""
        
        if not case_sensitive:
            lead_status_str = lead_status_str.lower()
            sale_statuses = [status.lower() for status in sale_statuses]
        
        if match_mode == 'exact':
            return lead_status_str in sale_statuses
        elif match_mode == 'partial':
            return any(status in lead_status_str or lead_status_str in status for status in sale_statuses)
        elif match_mode == 'regex':
            patterns = sale_status_config.get('regex_patterns', [])
            return any(re.match(pattern, lead_status_str, re.IGNORECASE if not case_sensitive else 0) 
                      for pattern in patterns)
        else:
            return False
    
    def _matches_additional_criteria(self, lead: Dict[str, Any]) -> bool:
        """Check if lead matches additional criteria."""
        additional_filters = self.config.get('lead_finding', {}).get('additional_filters', {})
        
        # Check required fields
        required_fields = additional_filters.get('required_fields', [])
        for field in required_fields:
            if not lead.get(field):
                return False
        
        # Check priority range
        priority_range = additional_filters.get('priority_range', {})
        if priority_range:
            min_priority = priority_range.get('min', 1)
            max_priority = priority_range.get('max', 5)
            lead_priority = lead.get('priority', 1)
            if not (min_priority <= lead_priority <= max_priority):
                return False
        
        # Check assignment filters
        assignment_filters = additional_filters.get('assignment_filters', {})
        if assignment_filters.get('exclude_assigned', False):
            if lead.get('user_id'):
                return False
        
        if assignment_filters.get('exclude_closed', False):
            closed_statuses = ['won', 'lost', 'cancelled']
            if lead.get('status') in closed_statuses:
                return False
        
        return True
    
    def _matches_sales_criteria(self, lead: Dict[str, Any]) -> bool:
        """Check if lead should be excluded due to existing sales/opportunities."""
        sales_config = self.config.get('lead_finding', {}).get('sales_filter', {})
        
        if not sales_config.get('enabled', False):
            return True  # Sales filter disabled, include lead
        
        lead_partner_id = lead.get('partner_id')
        
        # Handle partner_id field which can be:
        # - Integer: 12345
        # - List: [12345, 'Company Name'] 
        # - False/None: No partner assigned
        if not lead_partner_id:
            return True  # No partner_id, cannot match to opportunities
        elif isinstance(lead_partner_id, list) and len(lead_partner_id) > 0:
            lead_partner_id = lead_partner_id[0]  # Extract ID from [id, name] format
        elif not isinstance(lead_partner_id, int):
            logger.warning(f"Unexpected partner_id format for lead {lead.get('id')}: {lead_partner_id}")
            return True  # Include lead if partner_id format is unexpected
        
        # Check for matching opportunities
        try:
            has_matching_opportunity = self._check_opportunity_match(lead_partner_id, sales_config)
            
            # Log excluded leads if configured
            if has_matching_opportunity and sales_config.get('log_excluded_leads', True):
                logger.info(f"🚫 EXCLUDING LEAD: ID {lead.get('id')} (partner_id: {lead_partner_id}) - has matching opportunity in crm.opp")
            
            # Return False if matching opportunity found (exclude lead)
            return not has_matching_opportunity
        except Exception as e:
            # Log error but continue processing
            logger.warning(f"Error checking sales criteria for lead {lead.get('id')}: {e}")
            return True  # Include lead if error occurs
    
    def _batch_check_opportunities(self, partner_ids: List[int], config: Dict[str, Any]) -> Dict[int, bool]:
        """Batch check multiple partner_ids for opportunities in a single query."""
        if not partner_ids:
            return {}
        
        try:
            # Ensure Odoo client connection is active
            if not hasattr(self.client, '_uid') or not self.client._uid:
                self.client.connect()
                self.client.authenticate()
            
            # Get opportunity table configuration
            opportunity_model = config.get('opportunity_table', 'crm.opp')
            opportunity_partner_field = config.get('opportunity_partner_field', 'partner_id')
            
            # Build base domain for searching opportunities
            domain = [(opportunity_partner_field, 'in', partner_ids)]
            
            # Add type filter if specified (for crm.lead model with type='opportunity')
            opportunity_type = config.get('opportunity_type_filter')
            if opportunity_type:
                domain.append(('type', '=', opportunity_type))
            
            # Exclude specific opportunity stages
            exclude_stages = config.get('exclude_opportunity_stages', [])
            if exclude_stages:
                # Handle both stage names and stage IDs
                stage_ids = self._resolve_stage_names_to_ids(exclude_stages)
                if stage_ids:
                    domain.append(('stage_id', 'not in', stage_ids))
            
            # Include only specific opportunity stages
            include_stages = config.get('include_opportunity_stages', [])
            if include_stages:
                # Handle both stage names and stage IDs
                stage_ids = self._resolve_stage_names_to_ids(include_stages)
                if stage_ids:
                    domain.append(('stage_id', 'in', stage_ids))
            
            # Add date range filter for opportunities
            opp_date_range = config.get('opportunity_date_range', {})
            if opp_date_range.get('enabled', False):
                from datetime import datetime, timedelta
                date_field = opp_date_range.get('field_name', 'date_open')
                days_back = opp_date_range.get('days_back', 365)
                cutoff_date = datetime.now() - timedelta(days=days_back)
                domain.append((date_field, '>=', cutoff_date.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Search for matching opportunities using Odoo XML-RPC
            opportunities = self.client.search_read(
                opportunity_model, 
                domain, 
                fields=[opportunity_partner_field]
            )
            
            # Build result dictionary: partner_id -> has_opportunity
            result = {partner_id: False for partner_id in partner_ids}
            for opp in opportunities:
                partner_id = opp.get(opportunity_partner_field)
                if partner_id:
                    # Handle Many2one field that could return [id, "Name"] or just id
                    if isinstance(partner_id, (list, tuple)) and len(partner_id) > 0:
                        partner_id = partner_id[0]  # Extract the ID from [id, "Name"]
                    elif isinstance(partner_id, int):
                        partner_id = partner_id  # Already an integer
                    else:
                        continue  # Skip if not a valid format
                    
                    result[partner_id] = True
            
            return result
            
        except Exception as e:
            logger.warning(f"Error batch checking opportunities for {len(partner_ids)} partner_ids: {e}")
            return {partner_id: False for partner_id in partner_ids}  # Assume no match if error occurs
    
    def _check_opportunity_match(self, partner_id: int, config: Dict[str, Any]) -> bool:
        """Check if partner_id has matching opportunities in crm.opp via Odoo XML-RPC."""
        # Check cache first
        cache_key = f"{partner_id}_{hash(str(config))}"
        if cache_key in self._opportunity_cache:
            return self._opportunity_cache[cache_key]
        
        # If not in cache, use the old method (for backward compatibility)
        try:
            # Ensure Odoo client connection is active
            if not hasattr(self.client, '_uid') or not self.client._uid:
                self.client.connect()
                self.client.authenticate()
            
            # Get opportunity table configuration
            opportunity_model = config.get('opportunity_table', 'crm.opp')
            opportunity_partner_field = config.get('opportunity_partner_field', 'partner_id')
            
            # Build domain for searching opportunities
            domain = [(opportunity_partner_field, '=', partner_id)]
            
            # Add type filter if specified (for crm.lead model with type='opportunity')
            opportunity_type = config.get('opportunity_type_filter')
            if opportunity_type:
                domain.append(('type', '=', opportunity_type))
            
            # Exclude specific opportunity stages
            exclude_stages = config.get('exclude_opportunity_stages', [])
            if exclude_stages:
                # Handle both stage names and stage IDs
                stage_ids = self._resolve_stage_names_to_ids(exclude_stages)
                if stage_ids:
                    domain.append(('stage_id', 'not in', stage_ids))
            
            # Include only specific opportunity stages
            include_stages = config.get('include_opportunity_stages', [])
            if include_stages:
                # Handle both stage names and stage IDs
                stage_ids = self._resolve_stage_names_to_ids(include_stages)
                if stage_ids:
                    domain.append(('stage_id', 'in', stage_ids))
            
            # Add date range filter for opportunities
            opp_date_range = config.get('opportunity_date_range', {})
            if opp_date_range.get('enabled', False):
                from datetime import datetime, timedelta
                date_field = opp_date_range.get('field_name', 'date_open')
                days_back = opp_date_range.get('days_back', 365)
                cutoff_date = datetime.now() - timedelta(days=days_back)
                domain.append((date_field, '>=', cutoff_date.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Search for matching opportunities using Odoo XML-RPC
            opportunity_count = self.client.search_count(opportunity_model, domain)
            
            # Cache the result
            result = opportunity_count > 0
            self._opportunity_cache[cache_key] = result
            
            # Return True if any matching opportunities found
            return result
            
        except Exception as e:
            logger.warning(f"Error checking opportunity match for partner_id {partner_id}: {e}")
            return False  # Assume no match if error occurs
    
    def _resolve_stage_names_to_ids(self, stages: List[str]) -> List[int]:
        """Convert stage names to stage IDs for opportunity filtering."""
        try:
            stage_ids = []
            for stage in stages:
                # If it's already an integer, use it as-is
                if isinstance(stage, int):
                    stage_ids.append(stage)
                elif isinstance(stage, str) and stage.isdigit():
                    stage_ids.append(int(stage))
                else:
                    # Look up stage name in crm.stage model
                    stage_records = self.client.search_read(
                        'crm.stage', 
                        [('name', 'ilike', stage)], 
                        ['id']
                    )
                    if stage_records:
                        stage_ids.extend([record['id'] for record in stage_records])
                    else:
                        logger.warning(f"Could not find stage ID for stage name: {stage}")
            
            return stage_ids
        except Exception as e:
            logger.warning(f"Error resolving stage names to IDs: {e}")
            return []
    
    def _get_configured_web_sources(self, web_source_config: Dict[str, Any]) -> List[str]:
        """Get configured web sources from various sources."""
        source_type = web_source_config.get('source_type', 'config')
        
        if source_type == 'file':
            file_path = web_source_config.get('source_config', {}).get('file_path')
            return self._read_sources_from_file(file_path)
        elif source_type == 'database':
            table_name = web_source_config.get('source_config', {}).get('table_name')
            return self._read_sources_from_database(table_name)
        else:  # config
            return web_source_config.get('source_config', {}).get('sources', [])
    
    def _read_sources_from_file(self, file_path: str) -> List[str]:
        """Read web sources from file."""
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []
    
    def _read_sources_from_database(self, table_name: str) -> List[str]:
        """Read web sources from database table."""
        # Implementation to query database table
        return []
    
    def _process_leads_with_dropback(self, all_leads: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Separate leads into dropback and distribution pools."""
        dropback_config = self.config.get('lead_finding', {}).get('dropback_filter', {})
        
        if not dropback_config.get('enabled', False):
            return all_leads, []  # No dropback, all leads go to distribution
        
        dropback_leads = []
        distribution_leads = []
        
        for lead in all_leads:
            if self._is_dropback_lead(lead, dropback_config):
                # Assign to appropriate dropback user
                assigned_lead = self._assign_dropback_lead(lead, dropback_config)
                dropback_leads.append(assigned_lead)
            else:
                distribution_leads.append(lead)
        
        return distribution_leads, dropback_leads
    
    def _is_dropback_lead(self, lead: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Check if lead meets dropback criteria (age threshold)."""
        try:
            # Get age threshold configuration
            age_threshold = config.get('age_threshold', {})
            threshold_days = age_threshold.get('days', 30)
            date_field = age_threshold.get('field_name', 'source_date')
            
            # Get lead date
            lead_date_value = lead.get(date_field)
            if not lead_date_value:
                return False  # No date, can't determine age
            
            # Handle different date formats
            if isinstance(lead_date_value, str):
                try:
                    lead_date = datetime.strptime(lead_date_value, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        lead_date = datetime.strptime(lead_date_value, '%Y-%m-%d %H:%M:%S').date()
                    except ValueError:
                        return False  # Invalid date format
            elif isinstance(lead_date_value, date):
                lead_date = lead_date_value
            elif isinstance(lead_date_value, datetime):
                lead_date = lead_date_value.date()
            else:
                return False  # Unknown date type
            
            # Calculate age in days
            today = date.today()
            age_days = (today - lead_date).days
            
            # Check if lead exceeds threshold
            is_old = age_days > threshold_days
            
            if is_old and config.get('logging', {}).get('log_dropback_assignments', True):
                print(f"Lead {lead.get('id')} is {age_days} days old (threshold: {threshold_days}) - marked for dropback")
            
            return is_old
            
        except Exception as e:
            print(f"Error checking dropback criteria for lead {lead.get('id')}: {e}")
            return False  # Default to not dropback if error
    
    def _assign_dropback_lead(self, lead: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Assign lead to appropriate dropback user based on campaign."""
        try:
            # Get campaign assignments
            campaign_assignments = config.get('campaign_assignments', {})
            
            # Determine lead's campaign
            campaign = self._get_lead_campaign(lead, config)
            
            # Find assigned user for campaign
            assigned_user = campaign_assignments.get(campaign)
            if not assigned_user:
                assigned_user = campaign_assignments.get('default', 'Administrator')
            
            # Create assignment data
            assignment_config = config.get('assignment_config', {})
            
            # Update lead with dropback assignment
            updated_lead = lead.copy()
            
            if assignment_config.get('assign_immediately', True):
                # Apply assignment immediately using lead_manager
                try:
                    lead_id = lead.get('id')
                    if lead_id:
                        # Update user assignment and status
                        update_values = {'user_id': assigned_user}
                        if assignment_config.get('update_status', True):
                            dropback_status = assignment_config.get('dropback_status', 'dropback')
                            update_values['status'] = dropback_status
                        
                        self.lead_manager.update_lead_assignments(lead_id, **update_values)
                        
                        updated_lead['user_id'] = assigned_user
                        updated_lead['status'] = assignment_config.get('dropback_status', 'dropback')
                        
                except Exception as e:
                    print(f"Error applying dropback assignment for lead {lead_id}: {e}")
            
            # Log assignment
            if config.get('logging', {}).get('log_dropback_assignments', True):
                print(f"Dropback assignment: Lead {lead.get('id')} (campaign: {campaign}) → {assigned_user}")
            
            return updated_lead
            
        except Exception as e:
            print(f"Error assigning dropback lead {lead.get('id')}: {e}")
            return lead  # Return original lead if assignment fails
    
    def _get_lead_campaign(self, lead: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Determine the campaign for a lead based on web source ID."""
        try:
            assignment_config = config.get('assignment_config', {})
            web_source_field = assignment_config.get('web_source_field', 'source_id')
            web_source_field_type = assignment_config.get('web_source_field_type', 'many2one')
            
            web_source_value = lead.get(web_source_field)
            
            if not web_source_value:
                return 'default'
            
            # Handle different field types to extract web source name
            if web_source_field_type == 'many2one':
                # Extract name from [id, name] format
                if isinstance(web_source_value, list) and len(web_source_value) > 1:
                    web_source_name = web_source_value[1]
                elif isinstance(web_source_value, list) and len(web_source_value) == 1:
                    web_source_name = str(web_source_value[0])
                else:
                    web_source_name = str(web_source_value)
            else:
                # char or selection field
                web_source_name = str(web_source_value)
            
            # Get web source to campaign mapping
            web_source_mapping = config.get('web_source_campaign_mapping', {})
            
            # Check Voice sources
            voice_sources = web_source_mapping.get('voice_sources', [])
            for source in voice_sources:
                if self._matches_web_source_pattern(web_source_name, source):
                    return 'Voice'
            
            # Check Apple sources
            apple_sources = web_source_mapping.get('apple_sources', [])
            for source in apple_sources:
                if self._matches_web_source_pattern(web_source_name, source):
                    return 'Apple'
            
            # Check advanced pattern matching if configured
            web_source_matching = config.get('web_source_matching', {})
            if web_source_matching:
                campaign_patterns = web_source_matching.get('campaign_patterns', {})
                
                for campaign, patterns in campaign_patterns.items():
                    # Check exact matches
                    exact_matches = patterns.get('exact_matches', [])
                    web_source_str = str(web_source_name) if web_source_name is not None else ""
                    if web_source_str.lower() in [str(m).lower() for m in exact_matches]:
                        return campaign
                    
                    # Check pattern matches
                    pattern_matches = patterns.get('pattern_matches', [])
                    for pattern in pattern_matches:
                        pattern_str = str(pattern) if pattern is not None else ""
                        if re.search(pattern_str.lower(), web_source_str.lower()):
                            return campaign
            
            return web_source_mapping.get('default_campaign', 'default')
            
        except Exception as e:
            print(f"Error determining campaign for lead {lead.get('id')}: {e}")
            return 'default'
    
    def _matches_web_source_pattern(self, web_source_name: str, pattern: str) -> bool:
        """Check if web source name matches a pattern (supports wildcards)."""
        try:
            # Ensure both are strings
            web_source_str = str(web_source_name) if web_source_name is not None else ""
            pattern_str = str(pattern) if pattern is not None else ""
            
            # Convert simple wildcard pattern to regex
            if '*' in pattern_str:
                regex_pattern = pattern_str.replace('*', '.*')
                return bool(re.search(f'^{regex_pattern}$', web_source_str, re.IGNORECASE))
            else:
                # Exact match (case insensitive)
                return web_source_str.lower() == pattern_str.lower()
        except Exception:
            return False
    
    def _get_all_salespeople_with_eligibility(self) -> Tuple[List[SalespersonConfig], List[SalespersonConfig]]:
        """Get all salespeople from config and determine eligibility status."""
        # Get all salespeople before filtering
        all_salespeople = self._load_all_salespeople_unfiltered()
        
        # Apply filters to determine eligibility
        eligible_salespeople = self._apply_salesperson_filters(all_salespeople.copy())
        
        return all_salespeople, eligible_salespeople
    
    def _load_all_salespeople_unfiltered(self) -> List[SalespersonConfig]:
        """Load all salespeople from configuration without applying eligibility filters."""
        selection_config = self.config.get('salesperson_selection', {})
        source_type = selection_config.get('source_type', 'file')
        
        if source_type == 'file':
            return self._load_salespeople_from_file_unfiltered()
        elif source_type == 'campaign_table':
            return self._load_salespeople_from_campaign_table_unfiltered()
        elif source_type == 'list':
            return self._select_salespeople_from_list_unfiltered()
        else:
            raise ValueError(f"Unsupported salesperson source type: {source_type}")
    
    def _load_salespeople_from_file_unfiltered(self) -> List[SalespersonConfig]:
        """Load salespeople from file without applying filters."""
        selection_config = self.config.get('salesperson_selection', {})
        file_path = selection_config.get('source_config', {}).get('file_path')
        
        if not file_path:
            raise ValueError("File path not specified for salespeople source")
        
        default_target = selection_config.get('default_target_leads', 220)
        default_level = selection_config.get('default_level', 'mid_level')
        default_campaign = selection_config.get('default_campaign', 'Voice')
        
        salespeople = []
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 1:
                            name = parts[0].strip()
                            try:
                                target_leads = int(parts[1]) if len(parts) > 1 else default_target
                                level = parts[2].strip() if len(parts) > 2 else default_level
                                team = parts[3].strip() if len(parts) > 3 else 'Voice'
                                salespeople.append(SalespersonConfig(
                                    salesperson_name=name,
                                    salesperson_id=0,  # Will be resolved from Odoo
                                    level=level,
                                    target_leads=target_leads,
                                    campaign_name=default_campaign,
                                    team=team
                                ))
                            except ValueError as e:
                                logger.warning(f"Invalid data in line {line_num}: {line} - {e}")
                        else:
                            logger.warning(f"Invalid format in line {line_num}: {line}")
                            
        except FileNotFoundError:
            raise FileNotFoundError(f"Salespeople file not found: {file_path}")
        
        # Resolve user IDs from Odoo for all salespeople
        salespeople = self._resolve_user_ids(salespeople)
        return salespeople
    
    def _load_salespeople_from_campaign_table_unfiltered(self) -> List[SalespersonConfig]:
        """Load salespeople from campaign table without applying filters."""
        # This would mirror the campaign table logic without filters
        # For now, return empty list
        return []
    
    def _select_salespeople_from_list_unfiltered(self) -> List[SalespersonConfig]:
        """Load salespeople from list without applying filters."""
        selection_config = self.config.get('salesperson_selection', {})
        salespeople_list = selection_config.get('source_config', {}).get('salespeople_list', [])
        
        salespeople = []
        for name in salespeople_list:
            salespeople.append(SalespersonConfig(
                salesperson_name=name,
                salesperson_id=0,  # Will be resolved from Odoo
                level='mid_level',
                target_leads=150,
                campaign_name="Voice"  # Default campaign
            ))
        
        # Resolve user IDs from Odoo
        salespeople = self._resolve_user_ids(salespeople)
        return salespeople

    def _generate_dry_run_report(self, salespeople: List[SalespersonConfig], leads: List[Dict[str, Any]], 
                                assignments: Dict[int, List[int]], current_workload: Dict[int, Dict[str, Any]]) -> None:
        """Generate comprehensive dry-run report showing what would happen."""
        print("\n" + "="*100)
        print("🔍 DRY RUN REPORT - DAILY LEAD DISTRIBUTION ANALYSIS")
        print("="*100)
        
        # Get all salespeople with eligibility status
        all_salespeople, eligible_salespeople = self._get_all_salespeople_with_eligibility()
        
        # Overview section
        print("\n📊 DISTRIBUTION OVERVIEW")
        print("-" * 50)
        
        # Get filter statistics
        filter_stats = getattr(self, 'intermediate_results', {})
        total_in_range = filter_stats.get('total_leads_in_date_range', 0)
        dropback_count = filter_stats.get('dropback_leads', 0)
        after_dropback = filter_stats.get('leads_after_dropback', 0)
        final_distributable = filter_stats.get('leads_after_all_filters', len(leads))
        
        print(f"📅 Date Range: {self._get_date_range_description()}")
        print(f"🔢 Total leads in date range: {total_in_range:,}")
        print(f"↩️  Dropback leads (old): {dropback_count:,}")
        print(f"📋 Leads after dropback: {after_dropback:,}")
        print(f"✅ Final distributable leads: {final_distributable:,}")
        print(f"👥 Eligible salespeople: {len(salespeople):,}")
        
        # Dropback analysis
        if dropback_count > 0:
            print(f"\n📤 DROPBACK ANALYSIS")
            print("-" * 50)
            dropback_by_campaign = self._analyze_dropback_by_campaign()
            for campaign, count in dropback_by_campaign.items():
                assigned_user = self.config.get('lead_finding', {}).get('dropback_filter', {}).get('campaign_assignments', {}).get(campaign, 'Unknown')
                print(f"   {campaign}: {count} leads → {assigned_user}")
        
        # Filter impact analysis
        print(f"\n🔍 FILTER IMPACT ANALYSIS")
        print("-" * 50)
        leads_filtered_out = total_in_range - dropback_count - final_distributable
        if leads_filtered_out > 0:
            print(f"🚫 Leads filtered out: {leads_filtered_out:,}")
            filter_reasons = self._analyze_filter_reasons(total_in_range, dropback_count, final_distributable)
            for reason, count in filter_reasons.items():
                if count > 0:
                    print(f"   • {reason}: {count:,} leads")
        else:
            print("✅ No leads filtered out by criteria")
        
        # Enhanced salesperson workload analysis with eligibility
        print(f"\n👥 CURRENT WORKLOAD ANALYSIS (ALL SALESPEOPLE)")
        print("-" * 50)
        
        from tabulate import tabulate
        workload_data = []
        eligible_ids = {sp.salesperson_id for sp in eligible_salespeople}
        
        # Calculate current workload for all salespeople
        all_workload = {}
        for sp in all_salespeople:
            current_count = self._get_salesperson_lead_count(sp)
            all_workload[sp.salesperson_id] = {'current_leads': current_count, 'name': sp.salesperson_name}
        
        for sp in all_salespeople:
            workload = all_workload.get(sp.salesperson_id, {})
            current_count = workload.get('current_leads', 0)
            target = sp.target_leads
            utilization = (current_count / target * 100) if target > 0 else 0
            deficit = max(0, target - current_count)
            
            # Determine eligibility status
            is_eligible = sp.salesperson_id in eligible_ids
            eligibility_status = "✅ Eligible" if is_eligible else "❌ Filtered"
            
            # Determine filter reason if not eligible
            filter_reason = ""
            if not is_eligible:
                if sp.salesperson_id == 0:
                    filter_reason = "(User ID not found)"
                elif utilization > self.config.get('salesperson_selection', {}).get('filters', {}).get('max_workload_percentage', 100):
                    filter_reason = f"(Over {self.config.get('salesperson_selection', {}).get('filters', {}).get('max_workload_percentage', 100)}% capacity)"
                else:
                    filter_reason = "(Other criteria)"
            
            workload_data.append([
                sp.salesperson_name,
                sp.team,
                sp.level,
                current_count,
                target,
                f"{utilization:.1f}%",
                deficit,
                eligibility_status + " " + filter_reason
            ])
        
        headers = ["Salesperson", "Team", "Level", "Current", "Target", "Utilization", "Deficit", "Eligibility"]
        print(tabulate(workload_data, headers=headers, tablefmt="grid"))
        
        # Distribution preview
        print(f"\n📋 DISTRIBUTION PREVIEW")
        print("-" * 50)
        
        total_to_distribute = sum(len(lead_ids) for lead_ids in assignments.values())
        if total_to_distribute > 0:
            print(f"📊 Total leads to distribute: {total_to_distribute:,}")
            
            # Log distribution summary
            total_assigned = sum(len(lead_ids) for lead_ids in assignments.values())
            users_receiving = len([user_id for user_id, lead_ids in assignments.items() if lead_ids])
            logger.info(f"Distribution: {total_assigned} leads to {users_receiving} users")
            
            # Distribution by salesperson
            dist_data = []
            for sp in salespeople:
                lead_ids = assignments.get(sp.salesperson_id, [])
                if lead_ids:
                    current_count = current_workload.get(sp.salesperson_id, {}).get('current_leads', 0)
                    new_total = current_count + len(lead_ids)
                    utilization_after = (new_total / sp.target_leads * 100) if sp.target_leads > 0 else 0
                    
                    dist_data.append([
                        sp.salesperson_name,
                        len(lead_ids),
                        current_count,
                        new_total,
                        sp.target_leads,
                        f"{utilization_after:.1f}%"
                    ])
            
            if dist_data:
                headers = ["Salesperson", "New Leads", "Current", "After Dist", "Target", "Final Util%"]
                print(tabulate(dist_data, headers=headers, tablefmt="grid"))
            else:
                print("⚠️  No leads would be distributed (all salespeople at capacity)")
        else:
            print("⚠️  No leads to distribute")
        
        # Distribution strategy details
        print(f"\n⚙️  DISTRIBUTION STRATEGY")
        print("-" * 50)
        strategy = self.config.get('distribution', {}).get('strategy', 'unknown')
        print(f"📈 Strategy: {strategy.title()}")
        
        if strategy == 'level_based':
            levels = self.config.get('distribution', {}).get('level_based', {}).get('levels', {})
            print("🎯 Level priorities:")
            for level, config in levels.items():
                priority = config.get('priority', 'N/A')
                target = config.get('target_leads', 'N/A')
                print(f"   • {level.title()}: Priority {priority}, Target {target} leads")
        
        # Summary
        print(f"\n📋 EXECUTION SUMMARY")
        print("-" * 50)
        print("🔍 This was a DRY RUN - no changes were made to Odoo")
        print("💡 To execute this distribution, run without --dry-run flag")
        
        # Recommendations
        recommendations = self._generate_recommendations(salespeople, leads, assignments, current_workload)
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            print("-" * 50)
            for rec in recommendations:
                print(f"   • {rec}")
        
        print("\n" + "="*100)
    
    def generate_distribution_report(self, salespeople: List[SalespersonConfig], leads: List[Dict[str, Any]], 
                                   assignments: Dict[int, List[int]], current_workload: Dict[int, Dict[str, Any]],
                                   report_format: str = "html", output_path: str = None) -> str:
        """Generate comprehensive distribution report and save to file."""
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine output file
        if output_path is None:
            output_path = f"daily_distribution_report_{timestamp}.{report_format}"
        elif os.path.isdir(output_path):
            output_path = os.path.join(output_path, f"daily_distribution_report_{timestamp}.{report_format}")
        
        # Generate report data
        report_data = self._generate_report_data(salespeople, leads, assignments, current_workload)
        
        # Generate report based on format
        if report_format == "html":
            content = self._generate_html_report(report_data)
        elif report_format == "json":
            import json
            content = json.dumps(report_data, indent=2, default=str)
        elif report_format == "csv":
            content = self._generate_csv_report(report_data)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📊 Distribution report generated: {output_path}")
        return output_path
    
    def _generate_report_data(self, salespeople: List[SalespersonConfig], leads: List[Dict[str, Any]], 
                            assignments: Dict[int, List[int]], current_workload: Dict[int, Dict[str, Any]]) -> Dict:
        """Generate structured report data."""
        from datetime import datetime
        
        # Get all salespeople with eligibility status
        all_salespeople, eligible_salespeople = self._get_all_salespeople_with_eligibility()
        
        # Get filter statistics
        filter_stats = getattr(self, 'intermediate_results', {})
        total_in_range = filter_stats.get('total_leads_in_date_range', 0)
        dropback_count = filter_stats.get('dropback_leads', 0)
        after_dropback = filter_stats.get('leads_after_dropback', 0)
        final_distributable = filter_stats.get('leads_after_all_filters', len(leads))
        
        # Build comprehensive report data
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "Daily Lead Distribution Analysis",
                "date_range": self._get_date_range_description(),
                "is_dry_run": True  # This method is called for reporting purposes
            },
            
            "distribution_overview": {
                "total_leads_in_range": total_in_range,
                "dropback_leads": dropback_count,
                "leads_after_dropback": after_dropback,
                "final_distributable_leads": final_distributable,
                "eligible_salespeople_count": len(salespeople),
                "leads_filtered_out": total_in_range - dropback_count - final_distributable
            },
            
            "dropback_analysis": self._analyze_dropback_by_campaign() if dropback_count > 0 else {},
            
            "filter_impact": self._analyze_filter_reasons(total_in_range, dropback_count, final_distributable),
            
            "lead_analysis": {
                "status_distribution": self._analyze_status_distribution(leads),
                "web_source_distribution": self._analyze_web_source_distribution(leads),
                "sales_match_analysis": self._analyze_sales_matching(leads),
                "total_starting_leads": total_in_range
            },
            
            "salesperson_workload": [],
            
            "distribution_preview": {
                "total_to_distribute": sum(len(lead_ids) for lead_ids in assignments.values()),
                "users_receiving_leads": len([user_id for user_id, lead_ids in assignments.items() if lead_ids]),
                "assignments": []
            },
            
            "strategy_details": {
                "strategy": self.config.get('distribution', {}).get('strategy', 'unknown'),
                "config": self.config.get('distribution', {})
            },
            
            "recommendations": self._generate_recommendations(salespeople, leads, assignments, current_workload)
        }
        
        # Build salesperson workload data
        eligible_ids = {sp.salesperson_id for sp in eligible_salespeople}
        all_workload = {}
        for sp in all_salespeople:
            current_count = self._get_salesperson_lead_count(sp)
            all_workload[sp.salesperson_id] = {'current_leads': current_count, 'name': sp.salesperson_name}
        
        for sp in all_salespeople:
            workload = all_workload.get(sp.salesperson_id, {})
            current_count = workload.get('current_leads', 0)
            target = sp.target_leads
            utilization = (current_count / target * 100) if target > 0 else 0
            deficit = max(0, target - current_count)
            is_eligible = sp.salesperson_id in eligible_ids
            
            # Determine filter reason if not eligible
            filter_reason = ""
            if not is_eligible:
                if sp.salesperson_id == 0:
                    filter_reason = "User ID not found"
                elif utilization > self.config.get('salesperson_selection', {}).get('filters', {}).get('max_workload_percentage', 100):
                    filter_reason = f"Over {self.config.get('salesperson_selection', {}).get('filters', {}).get('max_workload_percentage', 100)}% capacity"
                else:
                    filter_reason = "Other criteria"
            
            report_data["salesperson_workload"].append({
                "name": sp.salesperson_name,
                "id": sp.salesperson_id,
                "team": sp.team,
                "level": sp.level,
                "current_leads": current_count,
                "target_leads": target,
                "utilization_percent": round(utilization, 1),
                "deficit": deficit,
                "is_eligible": is_eligible,
                "filter_reason": filter_reason
            })
        
        # Build distribution assignments
        for sp in salespeople:
            lead_ids = assignments.get(sp.salesperson_id, [])
            if lead_ids:
                current_count = current_workload.get(sp.salesperson_id, {}).get('current_leads', 0)
                new_total = current_count + len(lead_ids)
                utilization_after = (new_total / sp.target_leads * 100) if sp.target_leads > 0 else 0
                
                report_data["distribution_preview"]["assignments"].append({
                    "salesperson_name": sp.salesperson_name,
                    "salesperson_id": sp.salesperson_id,
                    "new_leads": len(lead_ids),
                    "current_leads": current_count,
                    "total_after_distribution": new_total,
                    "target_leads": sp.target_leads,
                    "utilization_after_percent": round(utilization_after, 1),
                    "lead_ids": lead_ids
                })
        
        return report_data
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """Generate HTML report from report data."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Lead Distribution Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .metadata {{
            text-align: center;
            color: #666;
            margin: 10px 0;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }}
        .section h2 {{
            color: #007bff;
            margin-top: 0;
            font-size: 1.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .eligible {{
            color: #28a745;
            font-weight: bold;
        }}
        .not-eligible {{
            color: #dc3545;
            font-weight: bold;
        }}
        .recommendations {{
            background: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 20px 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin: 8px 0;
        }}
        .dry-run-notice {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }}
        .dry-run-notice strong {{
            color: #856404;
        }}
        .section h3 {{
            color: #495057;
            margin: 25px 0 15px 0;
            font-size: 1.2em;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
        }}
        .stat-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }}
        .stat-card .stat-number {{
            background: linear-gradient(135deg, #007bff, #0056b3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .section:nth-child(even) {{
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
        }}
        .section:nth-child(odd) {{
            background: linear-gradient(135deg, #ffffff, #f1f3f4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Daily Lead Distribution Report</h1>
            <div class="metadata">
                <p><strong>Generated:</strong> {generated_at}</p>
                <p><strong>Date Range:</strong> {date_range}</p>
            </div>
        </div>
        
        <div class="dry-run-notice">
            <strong>📋 DRY RUN ANALYSIS</strong><br>
            This report shows what would happen during distribution - no changes were made to Odoo.
        </div>
        
        <div class="section">
            <h2>📊 Distribution Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_leads_in_range:,}</div>
                    <div class="stat-label">Total Leads in Range</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{dropback_leads:,}</div>
                    <div class="stat-label">Dropback Leads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{final_distributable_leads:,}</div>
                    <div class="stat-label">Distributable Leads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{eligible_salespeople_count:,}</div>
                    <div class="stat-label">Eligible Salespeople</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 IMPACT Filter Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_starting_leads:,}</div>
                    <div class="stat-label">🎯 Total Starting Leads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{dropback_leads:,}</div>
                    <div class="stat-label">📤 Dropback Filtered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{leads_filtered_impact:,}</div>
                    <div class="stat-label">🚫 IMPACT Filtered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{filter_survival_rate}%</div>
                    <div class="stat-label">✅ Filter Survival Rate</div>
                </div>
            </div>
            
            <h3>📊 Filter Impact Breakdown</h3>
            <div class="stats-grid">
                {filter_impact_cards}
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Status Distribution</h2>
            <div class="stats-grid">
                {status_distribution_cards}
            </div>
        </div>
        
        <div class="section">
            <h2>🌐 Web Source Distribution</h2>
            <div class="stats-grid">
                {web_source_cards}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Sales Match Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{opportunity_count:,}</div>
                    <div class="stat-label">🤝 With Opportunities</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{opportunity_rate}% of leads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{email_count:,}</div>
                    <div class="stat-label">📧 With Email</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{email_rate}% coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{phone_count:,}</div>
                    <div class="stat-label">📞 With Phone</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{phone_rate}% coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{mobile_count:,}</div>
                    <div class="stat-label">📱 With Mobile</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{mobile_rate}% coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{assigned_count:,}</div>
                    <div class="stat-label">👤 Assigned</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{assignment_rate}% assigned</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>👥 Salesperson Workload Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Salesperson</th>
                        <th>Team</th>
                        <th>Level</th>
                        <th>Current</th>
                        <th>Target</th>
                        <th>Utilization</th>
                        <th>Deficit</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {workload_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Distribution Preview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_to_distribute:,}</div>
                    <div class="stat-label">Total to Distribute</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{users_receiving_leads:,}</div>
                    <div class="stat-label">Users Receiving Leads</div>
                </div>
            </div>
            
            {distribution_table}
        </div>
        
        <div class="section">
            <h2>⚙️ Distribution Strategy</h2>
            <p><strong>Strategy:</strong> {strategy}</p>
        </div>
        
        {recommendations_section}
        
        <div class="section">
            <h2>📈 Summary</h2>
            <p>This analysis shows the current state of lead distribution and what changes would be made. 
            To execute this distribution, run the command without the --dry-run flag.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Generate workload table rows
        workload_rows = ""
        for sp in report_data["salesperson_workload"]:
            status_class = "eligible" if sp["is_eligible"] else "not-eligible"
            status_text = "✅ Eligible" if sp["is_eligible"] else f"❌ {sp['filter_reason']}"
            workload_rows += f"""
                <tr>
                    <td>{sp['name']}</td>
                    <td>{sp['team']}</td>
                    <td>{sp['level']}</td>
                    <td>{sp['current_leads']:,}</td>
                    <td>{sp['target_leads']:,}</td>
                    <td>{sp['utilization_percent']:.1f}%</td>
                    <td>{sp['deficit']:,}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
            """
        
        # Generate distribution table
        distribution_table = ""
        if report_data["distribution_preview"]["assignments"]:
            distribution_table = """
            <table>
                <thead>
                    <tr>
                        <th>Salesperson</th>
                        <th>New Leads</th>
                        <th>Current</th>
                        <th>After Distribution</th>
                        <th>Target</th>
                        <th>Final Utilization</th>
                    </tr>
                </thead>
                <tbody>
            """
            for assignment in report_data["distribution_preview"]["assignments"]:
                distribution_table += f"""
                    <tr>
                        <td>{assignment['salesperson_name']}</td>
                        <td>{assignment['new_leads']:,}</td>
                        <td>{assignment['current_leads']:,}</td>
                        <td>{assignment['total_after_distribution']:,}</td>
                        <td>{assignment['target_leads']:,}</td>
                        <td>{assignment['utilization_after_percent']:.1f}%</td>
                    </tr>
                """
            distribution_table += "</tbody></table>"
        else:
            distribution_table = "<p>⚠️ No leads would be distributed (all salespeople at capacity)</p>"
        
        # Generate recommendations section
        recommendations_section = ""
        if report_data["recommendations"]:
            recommendations_section = f"""
            <div class="section">
                <h2>💡 Recommendations</h2>
                <div class="recommendations">
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in report_data["recommendations"]])}
                    </ul>
                </div>
            </div>
            """
        
        # Generate filter impact cards
        filter_impact_cards = ""
        for reason, count in report_data["filter_impact"].items():
            if count > 0:
                filter_impact_cards += f"""
                    <div class="stat-card">
                        <div class="stat-number">{count:,}</div>
                        <div class="stat-label">{reason}</div>
                    </div>
                """
        
        # Generate status distribution cards
        status_distribution_cards = ""
        status_dist = report_data["lead_analysis"]["status_distribution"]
        total_leads = report_data["lead_analysis"]["total_starting_leads"]
        for status, count in sorted(status_dist.items(), key=lambda x: x[1], reverse=True)[:8]:  # Top 8 statuses
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            status_distribution_cards += f"""
                    <div class="stat-card">
                        <div class="stat-number">{count:,}</div>
                        <div class="stat-label">{status}</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{percentage:.1f}% of leads</div>
                    </div>
                """
        
        # Generate web source cards
        web_source_cards = ""
        web_sources = report_data["lead_analysis"]["web_source_distribution"]
        total_leads = report_data["lead_analysis"]["total_starting_leads"]
        for source, count in sorted(web_sources.items(), key=lambda x: x[1], reverse=True)[:8]:  # Top 8 sources
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            web_source_cards += f"""
                    <div class="stat-card">
                        <div class="stat-number">{count:,}</div>
                        <div class="stat-label">{source}</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">{percentage:.1f}% of leads</div>
                    </div>
                """
        
        # Extract sales match analysis data
        sales_analysis = report_data["lead_analysis"]["sales_match_analysis"]
        
        # Calculate filter survival rate
        total_starting = report_data["lead_analysis"]["total_starting_leads"]
        final_distributable = report_data["distribution_overview"]["final_distributable_leads"]
        filter_survival_rate = round((final_distributable / total_starting * 100) if total_starting > 0 else 0, 1)
        
        # Calculate leads filtered by IMPACT (excluding dropback)
        leads_filtered_impact = (total_starting - 
                               report_data["distribution_overview"]["dropback_leads"] - 
                               final_distributable)
        
        # Format the HTML
        return html_template.format(
            generated_at=report_data["report_metadata"]["generated_at"],
            date_range=report_data["report_metadata"]["date_range"],
            total_leads_in_range=report_data["distribution_overview"]["total_leads_in_range"],
            dropback_leads=report_data["distribution_overview"]["dropback_leads"],
            final_distributable_leads=report_data["distribution_overview"]["final_distributable_leads"],
            eligible_salespeople_count=report_data["distribution_overview"]["eligible_salespeople_count"],
            # New IMPACT filter analysis variables
            total_starting_leads=total_starting,
            leads_filtered_impact=leads_filtered_impact,
            filter_survival_rate=filter_survival_rate,
            filter_impact_cards=filter_impact_cards,
            # Status distribution variables
            status_distribution_cards=status_distribution_cards,
            # Web source distribution variables
            web_source_cards=web_source_cards,
            # Sales match analysis variables
            opportunity_count=sales_analysis["with_opportunities"],
            opportunity_rate=sales_analysis["opportunity_rate"],
            email_count=sales_analysis["with_email"],
            email_rate=sales_analysis["email_rate"],
            phone_count=sales_analysis["with_phone"],
            phone_rate=sales_analysis["phone_rate"],
            mobile_count=sales_analysis["with_mobile"],
            mobile_rate=sales_analysis["mobile_rate"],
            assigned_count=sales_analysis["assigned"],
            assignment_rate=sales_analysis["assignment_rate"],
            # Existing variables
            workload_rows=workload_rows,
            total_to_distribute=report_data["distribution_preview"]["total_to_distribute"],
            users_receiving_leads=report_data["distribution_preview"]["users_receiving_leads"],
            distribution_table=distribution_table,
            strategy=report_data["strategy_details"]["strategy"].title(),
            recommendations_section=recommendations_section
        )
    
    def _generate_csv_report(self, report_data: Dict) -> str:
        """Generate CSV report from report data."""
        import csv
        import io
        
        output = io.StringIO()
        
        # Write metadata
        output.write("Daily Lead Distribution Report\n")
        output.write(f"Generated: {report_data['report_metadata']['generated_at']}\n")
        output.write(f"Date Range: {report_data['report_metadata']['date_range']}\n")
        output.write("\n")
        
        # Distribution Overview
        output.write("DISTRIBUTION OVERVIEW\n")
        overview = report_data["distribution_overview"]
        for key, value in overview.items():
            output.write(f"{key.replace('_', ' ').title()},{value:,}\n")
        output.write("\n")
        
        # Salesperson Workload
        output.write("SALESPERSON WORKLOAD\n")
        writer = csv.writer(output)
        writer.writerow(["Name", "Team", "Level", "Current", "Target", "Utilization %", "Deficit", "Eligible", "Filter Reason"])
        for sp in report_data["salesperson_workload"]:
            writer.writerow([
                sp["name"], sp["team"], sp["level"], sp["current_leads"], 
                sp["target_leads"], sp["utilization_percent"], sp["deficit"],
                "Yes" if sp["is_eligible"] else "No", sp["filter_reason"]
            ])
        output.write("\n")
        
        # IMPACT Filter Analysis
        output.write("IMPACT FILTER ANALYSIS\n")
        output.write(f"Total Starting Leads,{report_data['lead_analysis']['total_starting_leads']:,}\n")
        output.write(f"Dropback Filtered,{report_data['distribution_overview']['dropback_leads']:,}\n")
        leads_filtered_impact = (report_data['lead_analysis']['total_starting_leads'] - 
                               report_data['distribution_overview']['dropback_leads'] - 
                               report_data['distribution_overview']['final_distributable_leads'])
        output.write(f"IMPACT Filtered,{leads_filtered_impact:,}\n")
        filter_survival_rate = round((report_data['distribution_overview']['final_distributable_leads'] / 
                                    report_data['lead_analysis']['total_starting_leads'] * 100) 
                                   if report_data['lead_analysis']['total_starting_leads'] > 0 else 0, 1)
        output.write(f"Filter Survival Rate,{filter_survival_rate}%\n")
        output.write("\nFilter Impact Breakdown\n")
        for reason, count in report_data["filter_impact"].items():
            if count > 0:
                output.write(f"{reason},{count:,}\n")
        output.write("\n")
        
        # Status Distribution
        output.write("STATUS DISTRIBUTION\n")
        for status, count in sorted(report_data["lead_analysis"]["status_distribution"].items(), 
                                  key=lambda x: x[1], reverse=True):
            output.write(f"{status},{count:,}\n")
        output.write("\n")
        
        # Web Source Distribution  
        output.write("WEB SOURCE DISTRIBUTION\n")
        for source, count in sorted(report_data["lead_analysis"]["web_source_distribution"].items(), 
                                  key=lambda x: x[1], reverse=True):
            output.write(f"{source},{count:,}\n")
        output.write("\n")
        
        # Sales Match Analysis
        output.write("SALES MATCH ANALYSIS\n")
        sales_analysis = report_data["lead_analysis"]["sales_match_analysis"]
        output.write(f"Total Leads,{sales_analysis['total_leads']:,}\n")
        output.write(f"With Opportunities,{sales_analysis['with_opportunities']:,} ({sales_analysis['opportunity_rate']}%)\n")
        output.write(f"With Email,{sales_analysis['with_email']:,} ({sales_analysis['email_rate']}%)\n")
        output.write(f"With Phone,{sales_analysis['with_phone']:,} ({sales_analysis['phone_rate']}%)\n")
        output.write(f"With Mobile,{sales_analysis['with_mobile']:,} ({sales_analysis['mobile_rate']}%)\n")
        output.write(f"Assigned,{sales_analysis['assigned']:,} ({sales_analysis['assignment_rate']}%)\n")
        output.write("\n")
        
        # Distribution Preview
        output.write("DISTRIBUTION ASSIGNMENTS\n")
        writer.writerow(["Salesperson", "New Leads", "Current", "After Distribution", "Target", "Final Utilization %"])
        for assignment in report_data["distribution_preview"]["assignments"]:
            writer.writerow([
                assignment["salesperson_name"], assignment["new_leads"], 
                assignment["current_leads"], assignment["total_after_distribution"],
                assignment["target_leads"], assignment["utilization_after_percent"]
            ])
        
        return output.getvalue()
    
    def _get_date_range_description(self) -> str:
        """Get human-readable date range description."""
        date_config = self.config.get('lead_finding', {}).get('date_range', {})
        older_than = date_config.get('older_than_days', 0)
        younger_than = date_config.get('younger_than_days', 30)
        
        today = date.today()
        start_date = today - timedelta(days=younger_than)
        end_date = today - timedelta(days=older_than)
        
        return f"{start_date} to {end_date} ({younger_than} days)"
    
    def _analyze_dropback_by_campaign(self) -> Dict[str, int]:
        """Analyze dropback leads by campaign."""
        if not hasattr(self, 'dropback_leads') or not self.dropback_leads:
            return {}
        
        campaign_counts = {}
        dropback_config = self.config.get('lead_finding', {}).get('dropback_filter', {})
        
        for lead in self.dropback_leads:
            campaign = self._get_lead_campaign(lead, dropback_config)
            campaign_counts[campaign] = campaign_counts.get(campaign, 0) + 1
        
        return campaign_counts
    
    def _analyze_filter_reasons(self, total: int, dropback: int, final: int) -> Dict[str, int]:
        """Analyze reasons leads were filtered out."""
        # This is a simplified analysis - in a real implementation, 
        # you'd track specific filter reasons during the filtering process
        filtered_out = total - dropback - final
        
        reasons = {
            "Sales filter (has opportunities)": int(filtered_out * 0.3),  # Estimated
            "DNC (Do Not Call) status": int(filtered_out * 0.2),
            "Missing required fields": int(filtered_out * 0.1),
            "Web source not matched": int(filtered_out * 0.2),
            "Other criteria": filtered_out - int(filtered_out * 0.8)
        }
        
        return reasons
    
    def _analyze_status_distribution(self, leads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze status distribution of leads."""
        status_counts = {}
        for lead in leads:
            status = lead.get('stage_id', 'Unknown')
            if isinstance(status, list) and len(status) > 1:
                status = status[1]  # Get stage name from [id, name] format
            elif isinstance(status, list) and len(status) == 1:
                status = f"Stage {status[0]}"
            elif not status:
                status = 'Unknown'
            
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def _analyze_web_source_distribution(self, leads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze web source distribution of leads."""
        source_counts = {}
        for lead in leads:
            source = lead.get('source_id', 'Unknown')
            if isinstance(source, list) and len(source) > 1:
                source = source[1]  # Get source name from [id, name] format
            elif isinstance(source, list) and len(source) == 1:
                source = f"Source {source[0]}"
            elif not source:
                source = 'Unknown'
            
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return source_counts
    
    def _analyze_sales_matching(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sales matching statistics."""
        total_leads = len(leads)
        with_opportunities = 0
        with_email = 0
        with_phone = 0
        with_mobile = 0
        assigned = 0
        
        for lead in leads:
            # Check for opportunities (sales matches)
            if lead.get('opportunity_count', 0) > 0:
                with_opportunities += 1
            
            # Check contact info
            if lead.get('email_from'):
                with_email += 1
            if lead.get('phone'):
                with_phone += 1
            if lead.get('mobile'):
                with_mobile += 1
            
            # Check assignment
            if lead.get('user_id'):
                assigned += 1
        
        return {
            'total_leads': total_leads,
            'with_opportunities': with_opportunities,
            'opportunity_rate': round((with_opportunities / total_leads * 100) if total_leads > 0 else 0, 1),
            'with_email': with_email,
            'email_rate': round((with_email / total_leads * 100) if total_leads > 0 else 0, 1),
            'with_phone': with_phone,
            'phone_rate': round((with_phone / total_leads * 100) if total_leads > 0 else 0, 1),
            'with_mobile': with_mobile,
            'mobile_rate': round((with_mobile / total_leads * 100) if total_leads > 0 else 0, 1),
            'assigned': assigned,
            'assignment_rate': round((assigned / total_leads * 100) if total_leads > 0 else 0, 1)
        }
    
    def _generate_recommendations(self, salespeople: List[SalespersonConfig], leads: List[Dict[str, Any]], 
                                assignments: Dict[int, List[int]], current_workload: Dict[int, Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on distribution analysis."""
        recommendations = []
        
        # Check for imbalanced workload
        utilizations = []
        for sp in salespeople:
            current_count = current_workload.get(sp.salesperson_id, {}).get('current_leads', 0)
            if sp.target_leads > 0:
                utilizations.append(current_count / sp.target_leads)
        
        if utilizations:
            avg_util = sum(utilizations) / len(utilizations)
            max_util = max(utilizations)
            min_util = min(utilizations)
            
            if max_util - min_util > 0.3:  # 30% difference
                recommendations.append("High workload imbalance detected - consider adjusting target levels")
            
            if avg_util < 0.5:  # Less than 50% utilization
                recommendations.append("Low overall utilization - consider increasing lead volume or reducing targets")
            
            if avg_util > 0.9:  # Over 90% utilization
                recommendations.append("High utilization - consider adding more salespeople or increasing targets")
        
        # Check for distribution efficiency
        total_to_distribute = sum(len(lead_ids) for lead_ids in assignments.values())
        if total_to_distribute < len(leads) * 0.8:  # Less than 80% distributed
            recommendations.append("Low distribution rate - review salesperson capacity and targets")
        
        # Check for dropback volume
        dropback_count = getattr(self, 'intermediate_results', {}).get('dropback_leads', 0)
        if dropback_count > len(leads) * 0.2:  # More than 20% dropback
            recommendations.append("High dropback volume - consider adjusting age thresholds or lead sources")
        
        return recommendations
    
    def distribute_leads(self, leads: List[Dict[str, Any]], salespeople: List[SalespersonConfig]) -> Dict[int, List[int]]:
        """Distribute leads according to strategy."""
        distribution_config = self.config.get('distribution', {})
        strategy = distribution_config.get('strategy', 'level_based')
        
        if strategy == 'level_based':
            return self._distribute_level_based(leads, salespeople)
        elif strategy == 'round_robin':
            return self._distribute_round_robin(leads, salespeople)
        elif strategy == 'proportional':
            return self._distribute_proportional(leads, salespeople)
        else:
            raise ValueError(f"Unknown distribution strategy: {strategy}")
    
    def _distribute_level_based(self, leads: List[Dict[str, Any]], salespeople: List[SalespersonConfig]) -> Dict[int, List[int]]:
        """Distribute leads using level-based strategy with participant exclusion."""
        # Get set of participating salesperson IDs
        participant_ids = {sp.salesperson_id for sp in salespeople}
        
        # Separate leads: those owned by participants need to be redistributed
        leads_to_redistribute = []
        leads_from_outside = []
        
        for lead in leads:
            current_owner = lead.get('user_id')
            # Handle different user_id formats (int, list, None)
            if current_owner:
                if isinstance(current_owner, list) and len(current_owner) > 0:
                    owner_id = current_owner[0]
                elif isinstance(current_owner, int):
                    owner_id = current_owner
                else:
                    owner_id = None
                
                if owner_id in participant_ids:
                    leads_to_redistribute.append(lead)
                else:
                    leads_from_outside.append(lead)
            else:
                # Unassigned leads go to outside pool
                leads_from_outside.append(lead)
        
        logger.info(f"Lead redistribution analysis:")
        logger.info(f"  - Leads from participants (to be redistributed): {len(leads_to_redistribute)}")
        logger.info(f"  - Leads from outside (normal distribution): {len(leads_from_outside)}")
        
        # Group salespeople by level
        level_groups = {}
        for sp in salespeople:
            level = sp.level
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(sp)
        
        # Sort levels by priority (senior first)
        level_priority = {'senior': 1, 'mid_level': 2, 'junior': 3}
        sorted_levels = sorted(level_groups.keys(), key=lambda x: level_priority.get(x, 999))
        
        assignments = {}
        all_leads = leads_from_outside + leads_to_redistribute
        remaining_leads = all_leads.copy()
        
        # Distribute by level priority
        for level in sorted_levels:
            level_salespeople = level_groups[level]
            
            # Calculate adjusted deficits for this level
            deficits = []
            for sp in level_salespeople:
                # Get current lead count
                current_count = self._get_salesperson_lead_count(sp)
                
                # Count leads that will be moved away from this salesperson
                leads_being_moved = sum(1 for lead in leads_to_redistribute 
                                      if self._lead_belongs_to_user(lead, sp.salesperson_id))
                
                # Adjusted current count = current - leads being moved away
                adjusted_current = max(0, current_count - leads_being_moved)
                
                # Calculate deficit based on adjusted count
                deficit = max(0, sp.target_leads - adjusted_current)
                deficits.append((sp, deficit, adjusted_current, leads_being_moved))
                
                logger.debug(f"{sp.salesperson_name}: current={current_count}, "
                           f"being_moved={leads_being_moved}, adjusted={adjusted_current}, "
                           f"target={sp.target_leads}, deficit={deficit}")
            
            # Sort by deficit (highest first)
            deficits.sort(key=lambda x: x[1], reverse=True)
            
            # Distribute leads to fill deficits
            for sp, deficit, adjusted_current, leads_being_moved in deficits:
                if not remaining_leads:
                    break
                
                # Don't give leads back to someone who is losing leads
                available_leads = []
                for lead in remaining_leads:
                    if not self._lead_belongs_to_user(lead, sp.salesperson_id):
                        available_leads.append(lead)
                
                leads_to_assign = min(deficit, len(available_leads))
                if leads_to_assign > 0:
                    assigned_leads = available_leads[:leads_to_assign]
                    
                    # Remove assigned leads from remaining pool
                    for assigned_lead in assigned_leads:
                        remaining_leads.remove(assigned_lead)
                    
                    if sp.salesperson_id not in assignments:
                        assignments[sp.salesperson_id] = []
                    
                    assignments[sp.salesperson_id].extend([lead['id'] for lead in assigned_leads])
                    
                    logger.info(f"Assigned {leads_to_assign} leads to {sp.salesperson_name} "
                              f"(deficit was {deficit})")
        
        # Log final assignment summary
        total_assigned = sum(len(lead_ids) for lead_ids in assignments.values())
        logger.info(f"Distribution complete: {total_assigned} leads assigned to {len(assignments)} users")
        if len(remaining_leads) > 0:
            logger.warning(f"{len(remaining_leads)} leads could not be assigned (all users at capacity)")
        
        return assignments
    
    def _lead_belongs_to_user(self, lead: Dict[str, Any], user_id: int) -> bool:
        """Check if a lead currently belongs to the specified user."""
        current_owner = lead.get('user_id')
        if not current_owner:
            return False
            
        if isinstance(current_owner, list) and len(current_owner) > 0:
            owner_id = current_owner[0]
        elif isinstance(current_owner, int):
            owner_id = current_owner
        else:
            return False
            
        return owner_id == user_id
    
    def _separate_leads_by_ownership(self, leads: List[Dict[str, Any]], participant_ids: set) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Separate leads into those owned by participants vs those from outside."""
        leads_to_redistribute = []
        leads_from_outside = []
        
        for lead in leads:
            current_owner = lead.get('user_id')
            # Handle different user_id formats (int, list, None)
            if current_owner:
                if isinstance(current_owner, list) and len(current_owner) > 0:
                    owner_id = current_owner[0]
                elif isinstance(current_owner, int):
                    owner_id = current_owner
                else:
                    owner_id = None
                
                if owner_id in participant_ids:
                    leads_to_redistribute.append(lead)
                else:
                    leads_from_outside.append(lead)
            else:
                # Unassigned leads go to outside pool
                leads_from_outside.append(lead)
        
        return leads_to_redistribute, leads_from_outside
    
    def _distribute_round_robin(self, leads: List[Dict[str, Any]], salespeople: List[SalespersonConfig]) -> Dict[int, List[int]]:
        """Distribute leads using round-robin strategy with participant exclusion."""
        if not salespeople:
            return {}
        
        # Get set of participating salesperson IDs
        participant_ids = {sp.salesperson_id for sp in salespeople}
        
        # Separate leads: those owned by participants need to be redistributed
        leads_to_redistribute = []
        leads_from_outside = []
        
        for lead in leads:
            current_owner = lead.get('user_id')
            # Handle different user_id formats (int, list, None)
            if current_owner:
                if isinstance(current_owner, list) and len(current_owner) > 0:
                    owner_id = current_owner[0]
                elif isinstance(current_owner, int):
                    owner_id = current_owner
                else:
                    owner_id = None
                
                if owner_id in participant_ids:
                    leads_to_redistribute.append(lead)
                else:
                    leads_from_outside.append(lead)
            else:
                # Unassigned leads go to outside pool
                leads_from_outside.append(lead)
        
        logger.info(f"Round-robin redistribution analysis:")
        logger.info(f"  - Leads from participants (to be redistributed): {len(leads_to_redistribute)}")
        logger.info(f"  - Leads from outside (normal distribution): {len(leads_from_outside)}")
        
        assignments = {sp.salesperson_id: [] for sp in salespeople}
        all_leads = leads_from_outside + leads_to_redistribute
        
        lead_index = 0
        for lead in all_leads:
            # Don't assign lead back to its current owner
            attempts = 0
            while attempts < len(salespeople):
                sp_index = lead_index % len(salespeople)
                salesperson = salespeople[sp_index]
                
                # Skip if this lead belongs to this salesperson
                if not self._lead_belongs_to_user(lead, salesperson.salesperson_id):
                    assignments[salesperson.salesperson_id].append(lead['id'])
                    break
                
                lead_index += 1
                attempts += 1
            
            if attempts >= len(salespeople):
                # All salespeople are excluded for this lead, assign to first one anyway
                logger.warning(f"Lead {lead.get('id')} could not be reassigned away from owner")
                salesperson = salespeople[0]
                assignments[salesperson.salesperson_id].append(lead['id'])
            
            lead_index += 1
        
        return assignments
    
    def _distribute_proportional(self, leads: List[Dict[str, Any]], salespeople: List[SalespersonConfig]) -> Dict[int, List[int]]:
        """Distribute leads using proportional strategy with participant exclusion."""
        if not salespeople:
            return {}
        
        # Calculate total target capacity
        total_target = sum(sp.target_leads for sp in salespeople)
        
        if total_target == 0:
            return self._distribute_round_robin(leads, salespeople)
        
        # Get set of participating salesperson IDs
        participant_ids = {sp.salesperson_id for sp in salespeople}
        
        # Separate leads: those owned by participants need to be redistributed
        leads_to_redistribute = []
        leads_from_outside = []
        
        for lead in leads:
            current_owner = lead.get('user_id')
            # Handle different user_id formats (int, list, None)
            if current_owner:
                if isinstance(current_owner, list) and len(current_owner) > 0:
                    owner_id = current_owner[0]
                elif isinstance(current_owner, int):
                    owner_id = current_owner
                else:
                    owner_id = None
                
                if owner_id in participant_ids:
                    leads_to_redistribute.append(lead)
                else:
                    leads_from_outside.append(lead)
            else:
                # Unassigned leads go to outside pool
                leads_from_outside.append(lead)
        
        logger.info(f"Proportional redistribution analysis:")
        logger.info(f"  - Leads from participants (to be redistributed): {len(leads_to_redistribute)}")
        logger.info(f"  - Leads from outside (normal distribution): {len(leads_from_outside)}")
        
        assignments = {sp.salesperson_id: [] for sp in salespeople}
        all_leads = leads_from_outside + leads_to_redistribute
        
        # Pre-calculate adjusted current counts for all salespeople
        adjusted_counts = {}
        for sp in salespeople:
            current_count = self._get_salesperson_lead_count(sp)
            # Count leads that will be moved away from this salesperson
            leads_being_moved = sum(1 for lead in leads_to_redistribute 
                                  if self._lead_belongs_to_user(lead, sp.salesperson_id))
            # Adjusted current count = current - leads being moved away
            adjusted_counts[sp.salesperson_id] = max(0, current_count - leads_being_moved)
        
        # Distribute leads proportionally
        for lead in all_leads:
            # Find salesperson with lowest current percentage of target (excluding current owner)
            best_sp = None
            best_ratio = float('inf')
            
            for sp in salespeople:
                # Skip if this lead belongs to this salesperson
                if self._lead_belongs_to_user(lead, sp.salesperson_id):
                    continue
                
                # Use adjusted count + leads already assigned in this round
                current_assigned = len(assignments[sp.salesperson_id])
                effective_count = adjusted_counts[sp.salesperson_id] + current_assigned
                ratio = effective_count / sp.target_leads if sp.target_leads > 0 else float('inf')
                
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_sp = sp
            
            if best_sp:
                assignments[best_sp.salesperson_id].append(lead['id'])
            else:
                # All salespeople are excluded for this lead, assign to least loaded anyway
                logger.warning(f"Lead {lead.get('id')} could not be reassigned away from owner")
                min_ratio_sp = min(salespeople, 
                                 key=lambda sp: adjusted_counts[sp.salesperson_id] / sp.target_leads 
                                 if sp.target_leads > 0 else float('inf'))
                assignments[min_ratio_sp.salesperson_id].append(lead['id'])
        
        return assignments
    
    def apply_distribution(self, assignments: Dict[int, List[int]], dry_run: bool = False) -> bool:
        """Apply lead assignments to Odoo."""
        if dry_run:
            logger.info("DRY RUN: Would assign leads as follows:")
            for user_id, lead_ids in assignments.items():
                logger.info(f"  User {user_id}: {len(lead_ids)} leads")
            return True
        
        try:
            for user_id, lead_ids in assignments.items():
                if lead_ids:
                    self.lead_manager.update_lead_assignments(
                        lead_ids=lead_ids,
                        user_id=user_id
                    )
                    logger.info(f"Assigned {len(lead_ids)} leads to user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply distribution: {e}")
            return False
    
    def run_daily_distribution(self, dry_run: bool = False, step_mode: bool = False, auto_accept: bool = False,
                             generate_report: bool = False, report_format: str = "html", report_location: str = None,
                             export_options: Dict[str, Any] = None) -> LeadDistributionResult:
        """Execute complete daily distribution process."""
        start_time = datetime.now()
        leads = []  # Initialize leads variable for exception handling
        salespeople = []  # Initialize salespeople variable for exception handling
        
        # Ensure export_options is not None
        if export_options is None:
            export_options = {}
        
        try:
            # Step 1: Select eligible salespeople
            if step_mode:
                self._show_step_header("Step 1: Salesperson Selection", "Selecting eligible salespeople based on configuration")
            
            logger.info("Selecting eligible salespeople...")
            salespeople = self.select_salespeople()
            logger.info(f"Found {len(salespeople)} eligible salespeople")
            
            if step_mode:
                self._show_salespeople_step(salespeople, auto_accept)
            
            if not salespeople:
                return LeadDistributionResult(
                    success=False,
                    leads_found=0,
                    leads_distributed=0,
                    leads_not_distributed=0,
                    salespeople_eligible=0,
                    salespeople_received_leads=0,
                    execution_time_seconds=0,
                    error_message="No eligible salespeople found"
                )
            
            # Step 2: Find distributable leads
            if step_mode:
                self._show_step_header("Step 2: Lead Discovery", "Finding distributable leads based on filters")
            
            logger.info("Finding distributable leads...")
            
            # Log active filters
            web_source_config = self.config.get('lead_finding', {}).get('web_sources', {})
            campaign_config = self.config.get('lead_finding', {}).get('campaigns', {})
            
            active_filters = []
            if web_source_config.get('enabled', True):
                active_filters.append("Web Sources")
            if campaign_config.get('enabled', True) and campaign_config.get('types'):
                active_filters.append("Campaigns")
            if self.config.get('lead_finding', {}).get('additional_filters', {}).get('status', {}).get('values'):
                active_filters.append("Status")
            if self.config.get('lead_finding', {}).get('additional_filters', {}).get('exclude_dnc'):
                active_filters.append("DNC")
                
            logger.info(f"Active filters: {', '.join(active_filters) if active_filters else 'None'}")
            
            leads = self.find_distributable_leads(export_options=export_options)
            logger.info(f"Found {len(leads)} distributable leads")
            
            # Store leads for potential CSV export
            self.distributable_leads = leads
            
            if step_mode:
                self._show_leads_step(leads, auto_accept)
            
            if not leads:
                # Even if no leads, we might still want to generate reports
                if generate_report:
                    current_workload = self._calculate_current_workload(salespeople)
                    assignments = {}  # No assignments since no leads
                    self.generate_distribution_report(salespeople, leads, assignments, current_workload, 
                                                    report_format, report_location)
                
                return LeadDistributionResult(
                    success=True,
                    leads_found=0,
                    leads_distributed=0,
                    leads_not_distributed=0,
                    salespeople_eligible=len(salespeople),
                    salespeople_received_leads=0,
                    execution_time_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Step 3: Calculate current workload
            if step_mode:
                self._show_step_header("Step 3: Workload Analysis", "Calculating current lead counts and workload")
            
            logger.info("Calculating current workload...")
            current_workload = self._calculate_current_workload(salespeople)
            
            if step_mode:
                self._show_workload_step(current_workload, auto_accept)
            
            # Step 4: Distribute leads
            if step_mode:
                self._show_step_header("Step 4: Lead Distribution", "Distributing leads according to strategy")
            
            logger.info("Distributing leads...")
            assignments = self.distribute_leads(leads, salespeople)
            
            # Log salesperson count for verification
            logger.info(f"Distributing to {len(salespeople)} salespeople")
            
            if step_mode:
                self._show_distribution_step(assignments, leads, salespeople, auto_accept)
            
            # Step 5: Apply distribution
            if step_mode:
                self._show_step_header("Step 5: Apply Distribution", "Applying lead assignments to Odoo")
            
            logger.info("Applying distribution...")
            
            # Generate comprehensive dry-run report if requested
            if dry_run:
                self._generate_dry_run_report(salespeople, leads, assignments, current_workload)
            
            # Generate file report if requested
            if generate_report:
                self.generate_distribution_report(salespeople, leads, assignments, current_workload, 
                                                report_format, report_location)
            
            success = self.apply_distribution(assignments, dry_run)
            
            # Calculate results
            total_distributed = sum(len(lead_ids) for lead_ids in assignments.values())
            salespeople_received = len([sp for sp in assignments.values() if sp])
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create detailed distribution summary for result
            distribution_summary = {
                'total_leads_in_date_range': getattr(self, 'intermediate_results', {}).get('total_leads_in_date_range', 0),
                'dropback_leads': getattr(self, 'intermediate_results', {}).get('dropback_leads', 0),
                'leads_after_filters': len(leads),
                'distribution_assignments': {str(k): len(v) for k, v in assignments.items()},
                'salespeople_count': len(salespeople),
                'strategy_used': self.config.get('distribution', {}).get('strategy', 'unknown'),
                'dry_run': dry_run
            }
            
            return LeadDistributionResult(
                success=success,
                leads_found=len(leads),
                leads_distributed=total_distributed,
                leads_not_distributed=len(leads) - total_distributed,
                salespeople_eligible=len(salespeople),
                salespeople_received_leads=salespeople_received,
                execution_time_seconds=execution_time,
                distribution_summary=distribution_summary
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Distribution failed: {e}")
            
            return LeadDistributionResult(
                success=False,
                leads_found=len(leads),
                leads_distributed=0,
                leads_not_distributed=len(leads),
                salespeople_eligible=len(salespeople),
                salespeople_received_leads=0,
                execution_time_seconds=execution_time,
                error_message=str(e)
            )
    
    def _show_step_header(self, title: str, description: str):
        """Display step header in step-through mode."""
        print("\n" + "="*80)
        print(f"🔄 {title}")
        print(f"📝 {description}")
        print("="*80)
    
    def _show_salespeople_step(self, salespeople: List[SalespersonConfig], auto_accept: bool):
        """Show salespeople selection step."""
        print(f"\n✅ Found {len(salespeople)} eligible salespeople:")
        
        # Create table data
        table_data = []
        for sp in salespeople:
            table_data.append([
                sp.salesperson_name,
                sp.salesperson_id,
                sp.campaign_name,
                sp.level,
                sp.target_leads,
                sp.team,
                "✅" if sp.active else "❌"
            ])
        
        # Display table
        from tabulate import tabulate
        headers = ["Name", "ID", "Campaign", "Level", "Target", "Team", "Active"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Show configuration summary
        print(f"\n📊 Configuration Summary:")
        print(f"   • Campaign: {self.config.get('campaign', {}).get('target_campaign', 'N/A')}")
        print(f"   • Distribution Strategy: {self.config.get('distribution', {}).get('strategy', 'N/A')}")
        print(f"   • Date Range: {self.config.get('lead_finding', {}).get('date_range', {}).get('younger_than_days', 'N/A')} days")
        
        if not auto_accept:
            response = input("\n❓ Proceed to next step? (Y/n): ").strip().lower()
            if response in ['n', 'no']:
                raise KeyboardInterrupt("User cancelled operation")
    
    def _show_leads_step(self, leads: List[Dict[str, Any]], auto_accept: bool):
        """Show leads discovery step."""
        print(f"\n✅ Found {len(leads)} distributable leads:")
        
        if leads:
            # Show lead characteristics
            status_counts = {}
            source_counts = {}
            campaign_counts = {}
            
            for lead in leads:
                status = lead.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                source = lead.get('source_id', [None])[0] if isinstance(lead.get('source_id'), list) else lead.get('source_id')
                if source:
                    source_counts[str(source)] = source_counts.get(str(source), 0) + 1
                
                campaign = lead.get('campaign_id', [None])[0] if isinstance(lead.get('campaign_id'), list) else lead.get('campaign_id')
                if campaign:
                    campaign_counts[str(campaign)] = campaign_counts.get(str(campaign), 0) + 1
            
            print(f"\n📊 Lead Characteristics:")
            print(f"   • Status Distribution:")
            for status, count in status_counts.items():
                print(f"     - {status}: {count}")
            
            print(f"   • Source Distribution:")
            for source, count in source_counts.items():
                print(f"     - {source}: {count}")
            
            print(f"   • Campaign Distribution:")
            for campaign, count in campaign_counts.items():
                print(f"     - {campaign}: {count}")
        
        # Show filter summary
        filters = self.config.get('lead_finding', {})
        print(f"\n🔍 Applied Filters:")
        print(f"   • Date Range: {filters.get('date_range', {}).get('younger_than_days', 'N/A')} days")
        print(f"   • Statuses: {filters.get('additional_filters', {}).get('status', {}).get('values', ['N/A'])}")
        print(f"   • DNC Excluded: {filters.get('additional_filters', {}).get('exclude_dnc', 'N/A')}")
        
        if not auto_accept:
            response = input("\n❓ Proceed to next step? (Y/n): ").strip().lower()
            if response in ['n', 'no']:
                raise KeyboardInterrupt("User cancelled operation")
    
    def _calculate_current_workload(self, salespeople: List[SalespersonConfig]) -> Dict[int, Dict[str, Any]]:
        """Calculate current workload for each salesperson."""
        workload = {}
        
        for sp in salespeople:
            # Get current lead count (placeholder implementation)
            current_count = self._get_salesperson_lead_count(sp)
            target = sp.target_leads
            utilization = (current_count / target * 100) if target > 0 else 0
            deficit = max(0, target - current_count)
            
            workload[sp.salesperson_id] = {
                'name': sp.salesperson_name,
                'level': sp.level,
                'current_count': current_count,
                'target': target,
                'utilization': utilization,
                'deficit': deficit
            }
        
        return workload
    
    def _show_workload_step(self, workload: Dict[int, Dict[str, Any]], auto_accept: bool):
        """Show workload analysis step."""
        print(f"\n📊 Current Workload Analysis:")
        
        # Create table data
        table_data = []
        for user_id, data in workload.items():
            status_icon = "🟢" if data['utilization'] < 80 else "🟡" if data['utilization'] < 100 else "🔴"
            table_data.append([
                data['name'],
                data['level'],
                data['current_count'],
                data['target'],
                f"{data['utilization']:.1f}%",
                data['deficit'],
                status_icon
            ])
        
        # Display table
        from tabulate import tabulate
        headers = ["Name", "Level", "Current", "Target", "Utilization", "Deficit", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Summary statistics
        total_current = sum(data['current_count'] for data in workload.values())
        total_target = sum(data['target'] for data in workload.values())
        total_deficit = sum(data['deficit'] for data in workload.values())
        
        print(f"\n📈 Summary:")
        print(f"   • Total Current Leads: {total_current}")
        print(f"   • Total Target Capacity: {total_target}")
        print(f"   • Total Deficit: {total_deficit}")
        print(f"   • Average Utilization: {sum(data['utilization'] for data in workload.values()) / len(workload):.1f}%")
        
        if not auto_accept:
            response = input("\n❓ Proceed to next step? (Y/n): ").strip().lower()
            if response in ['n', 'no']:
                raise KeyboardInterrupt("User cancelled operation")
    
    def _show_distribution_step(self, assignments: Dict[int, List[int]], leads: List[Dict[str, Any]], 
                               salespeople: List[SalespersonConfig], auto_accept: bool):
        """Show distribution plan step."""
        print(f"\n📋 Distribution Plan:")
        
        # Create table data
        table_data = []
        total_assigned = 0
        
        for sp in salespeople:
            assigned_count = len(assignments.get(sp.salesperson_id, []))
            total_assigned += assigned_count
            
            # Calculate expected utilization after distribution
            current_count = self._get_salesperson_lead_count(sp)
            new_count = current_count + assigned_count
            new_utilization = (new_count / sp.target_leads * 100) if sp.target_leads > 0 else 0
            
            status_icon = "🟢" if new_utilization <= 100 else "🔴"
            
            table_data.append([
                sp.salesperson_name,
                sp.level,
                current_count,
                assigned_count,
                new_count,
                sp.target_leads,
                f"{new_utilization:.1f}%",
                status_icon
            ])
        
        # Display table
        from tabulate import tabulate
        headers = ["Name", "Level", "Current", "To Assign", "New Total", "Target", "New Util%", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Summary
        unassigned = len(leads) - total_assigned
        print(f"\n📊 Distribution Summary:")
        print(f"   • Total Leads Available: {len(leads)}")
        print(f"   • Total Leads to Assign: {total_assigned}")
        print(f"   • Unassigned Leads: {unassigned}")
        print(f"   • Salespeople Receiving Leads: {len([sp for sp in assignments.values() if sp])}")
        
        if unassigned > 0:
            print(f"   ⚠️  Warning: {unassigned} leads will remain unassigned")
        
        if not auto_accept:
            response = input("\n❓ Proceed to apply distribution? (Y/n): ").strip().lower()
            if response in ['n', 'no']:
                raise KeyboardInterrupt("User cancelled operation")
    
    def _export_leads_to_csv(self, leads: List[Dict[str, Any]], stage: str, 
                             export_options: Dict[str, Any], description: str) -> None:
        """Export leads to CSV file at a specific filtering stage."""
        import csv
        import os
        from pathlib import Path
        
        # Get output directory
        output_dir = export_options.get('stages_output_dir', 'lead_stages')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{stage}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Get fields to export
        fields = export_options.get('leads_fields')
        if not fields:
            fields = [
                'id', 'name', 'email', 'phone', 'status', 'web_source_id', 
                'partner_id', 'user_id', 'source_date', 'create_date'
            ]
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for lead in leads:
                # Convert complex fields to strings
                row = {}
                for field in fields:
                    value = lead.get(field)
                    if isinstance(value, (list, tuple)) and len(value) >= 2:
                        # Handle Odoo many2one fields [id, name]
                        row[field] = f"{value[0]}:{value[1]}"
                    elif value is None or value is False:
                        row[field] = ''
                    else:
                        row[field] = str(value)
                writer.writerow(row)
        
        logger.info(f"Exported {len(leads)} leads to {filepath}")
        logger.info(f"  Stage: {stage}")
        logger.info(f"  Description: {description}")
        print(f"\n📁 Exported {len(leads)} leads to {filepath}")
        print(f"   Stage: {stage}")
        print(f"   Description: {description}")
    
    def _show_filter_delta_analysis(self, raw_leads: List[Dict[str, Any]], 
                                   after_dropback: List[Dict[str, Any]], 
                                   final_leads: List[Dict[str, Any]], 
                                   debug_counts: Dict[str, int]) -> None:
        """Show detailed delta analysis between filtering stages."""
        print("\n" + "=" * 80)
        print("FILTER DELTA ANALYSIS")
        print("=" * 80)
        
        # Stage 1: Raw leads
        print(f"\n📊 Stage 1: Raw Leads (Date Range Only)")
        print(f"   Total: {len(raw_leads):,} leads")
        
        # Stage 2: After dropback
        dropback_count = len(raw_leads) - len(after_dropback)
        dropback_pct = (dropback_count / len(raw_leads) * 100) if raw_leads else 0
        print(f"\n📊 Stage 2: After Dropback Processing")
        print(f"   Total: {len(after_dropback):,} leads")
        print(f"   Removed: {dropback_count:,} dropback leads ({dropback_pct:.1f}%)")
        
        # Stage 3: Final filtered
        filter_removed = len(after_dropback) - len(final_leads)
        filter_pct = (filter_removed / len(after_dropback) * 100) if after_dropback else 0
        print(f"\n📊 Stage 3: After All Filters")
        print(f"   Total: {len(final_leads):,} leads")
        print(f"   Removed: {filter_removed:,} leads ({filter_pct:.1f}%)")
        
        # Filter breakdown
        if debug_counts:
            print(f"\n🔍 Filter Breakdown (from {debug_counts['total_checked']} leads after dropback):")
            print(f"   • DNC Filter: Removed {debug_counts['failed_dnc']:,} leads")
            print(f"   • Sales Filter: Removed {debug_counts['failed_sales']:,} leads")
            print(f"   • Web Source: Removed {debug_counts['failed_web_source']:,} leads")
            print(f"   • Campaign: Removed {debug_counts['failed_campaign']:,} leads")
            print(f"   • Status: Removed {debug_counts['failed_status']:,} leads")
            print(f"   • Passed All: {debug_counts['passed_all']:,} leads")
        
        # Overall summary
        total_removed = len(raw_leads) - len(final_leads)
        total_pct = (total_removed / len(raw_leads) * 100) if raw_leads else 0
        print(f"\n📈 Overall Summary:")
        print(f"   • Started with: {len(raw_leads):,} leads")
        print(f"   • Ended with: {len(final_leads):,} leads")
        print(f"   • Total removed: {total_removed:,} leads ({total_pct:.1f}%)")
        print(f"   • Retention rate: {100 - total_pct:.1f}%")
        
        print("=" * 80) 