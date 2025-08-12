#\!/usr/bin/env python3
"""Debug script to check web_source_id format from crm.lead"""

from odoo_lead_manager.client import OdooClient

# Connect to Odoo
client = OdooClient()
client.connect()
client.authenticate()

# Get leads from crm.lead with web_source_id not null
leads = client.search_read(
    "crm.lead",
    domain=[("web_source_id", "\!=", False)],
    fields=["id", "web_source_id", "name", "status"],
    limit=10
)

print("Sample crm.lead records with web_source_id:")
print("-" * 60)
for lead in leads:
    web_source = lead.get('web_source_id')
    print(f"Lead ID: {lead['id']}")
    print(f"  Type: {type(web_source)}")
    print(f"  Value: {web_source}")
    print(f"  Repr: {repr(web_source)}")
    if isinstance(web_source, list) and len(web_source) == 2:
        print(f"  Extracted name: {web_source[1]}")
    print()

