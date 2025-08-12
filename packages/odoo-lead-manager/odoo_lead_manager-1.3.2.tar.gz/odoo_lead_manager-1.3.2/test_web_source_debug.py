#\!/usr/bin/env python3
"""Debug script to check web_source_id format"""

from odoo_lead_manager import OdooClient, LeadManager
from odoo_lead_manager.filters import LeadFilter
import json

# Connect to Odoo
client = OdooClient()
lead_manager = LeadManager(client)

# Get a few leads to inspect
filter_obj = LeadFilter().limit(5).fields(["id", "web_source_id", "name", "status"])
leads = lead_manager.get_leads(filter_obj)

print("Sample leads with web_source_id:")
print("-" * 60)
for lead in leads:
    web_source = lead.get('web_source_id')
    print(f"Lead ID: {lead['id']}")
    print(f"  Type: {type(web_source)}")
    print(f"  Value: {web_source}")
    print(f"  Repr: {repr(web_source)}")
    if isinstance(web_source, str):
        print(f"  Is string starting with '[': {web_source.startswith('[') if web_source else False}")
    print()

