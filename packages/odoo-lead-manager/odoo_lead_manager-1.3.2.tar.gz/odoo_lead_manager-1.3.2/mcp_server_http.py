#!/usr/bin/env python3
"""
MCP Server for Odoo Lead Manager - HTTP Version

This server uses FastMCP for HTTP-based MCP server compatible with Claude Desktop.
Compatible with Claude Desktop and other MCP clients.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, date

from mcp.server.fastmcp import FastMCP

from odoo_lead_manager.client import OdooClient
from odoo_lead_manager.lead_manager import LeadManager
from odoo_lead_manager.filters import LeadFilter

# Initialize FastMCP server
mcp = FastMCP("Odoo Lead Manager", host="0.0.0.0", port=8001)

class OdooMCPBridge:
    """Bridge between MCP server and Odoo Lead Manager."""
    
    def __init__(self):
        self.client = None
        self.lead_manager = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize connection to Odoo."""
        try:
            self.client = OdooClient()
            self.lead_manager = LeadManager(self.client)
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Odoo connection: {e}", file=sys.stderr)
            return False
    
    def query_leads(self, 
                   date_from: Optional[str] = None,
                   date_to: Optional[str] = None,
                   status: Optional[str] = None,
                   user: Optional[str] = None,
                   source: Optional[str] = None,
                   limit: int = 100,
                   fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Query leads with various filters."""
        if not self._initialized:
            raise RuntimeError("Odoo not initialized")
        
        filter_obj = LeadFilter().model("crm.lead")
        
        if date_from:
            filter_obj.by_date_range(start_date=date_from, field_name="source_date")
        if date_to:
            filter_obj.by_date_range(end_date=date_to, field_name="source_date")
        if status:
            filter_obj.by_status([status])
        if user:
            filter_obj.by_user_assignments(user_names=[user])
        if source:
            filter_obj.by_web_source_ids([source])
        
        filter_obj.limit(limit)
        
        return self.lead_manager.get_leads(filter_obj, fields=fields)
    
    def update_leads(self,
                    lead_ids: List[int],
                    user_id: Optional[int] = None,
                    user_name: Optional[str] = None,
                    closer_id: Optional[int] = None,
                    closer_name: Optional[str] = None,
                    open_user_id: Optional[int] = None,
                    open_user_name: Optional[str] = None,
                    status: Optional[str] = None,
                    model: str = "crm.lead") -> Dict[str, Any]:
        """Update leads with new assignments and fields."""
        if not self._initialized:
            raise RuntimeError("Odoo not initialized")
        
        update_values = {}
        
        # Resolve user names to IDs if provided
        def resolve_user(name_or_id):
            if isinstance(name_or_id, int):
                return name_or_id
            if name_or_id:
                users = self.client.search_read(
                    "res.users",
                    domain=[["name", "ilike", name_or_id]],
                    fields=["id", "name"],
                    limit=1
                )
                if users:
                    return users[0]["id"]
            return None
        
        if user_id is not None:
            update_values["user_id"] = user_id
        elif user_name:
            user_id = resolve_user(user_name)
            if user_id:
                update_values["user_id"] = user_id
        
        if closer_id is not None:
            update_values["closer_id"] = closer_id
        elif closer_name:
            closer_id = resolve_user(closer_name)
            if closer_id:
                update_values["closer_id"] = closer_id
        
        if open_user_id is not None:
            update_values["open_user_id"] = open_user_id
        elif open_user_name:
            open_user_id = resolve_user(open_user_name)
            if open_user_id:
                update_values["open_user_id"] = open_user_id
        
        if status:
            update_values["status"] = status
        
        if not update_values:
            raise ValueError("No update values provided")
        
        return self.lead_manager.update_lead_assignments(
            lead_ids, model=model, **update_values
        )
    
    def count_leads(self,
                   date_from: Optional[str] = None,
                   date_to: Optional[str] = None,
                   status: Optional[str] = None,
                   user: Optional[str] = None,
                   source: Optional[str] = None) -> int:
        """Count leads matching criteria."""
        if not self._initialized:
            raise RuntimeError("Odoo not initialized")
        
        filter_obj = LeadFilter().model("crm.lead")
        
        if date_from:
            filter_obj.by_date_range(start_date=date_from, field_name="source_date")
        if date_to:
            filter_obj.by_date_range(end_date=date_to, field_name="source_date")
        if status:
            filter_obj.by_status([status])
        if user:
            filter_obj.by_user_assignments(user_names=[user])
        if source:
            filter_obj.by_web_source_ids([source])
        
        return self.lead_manager.count_leads(filter_obj)

    def query_invoices(self,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      partner_id: Optional[int] = None,
                      state: Optional[str] = None,
                      type: Optional[str] = None,
                      limit: int = 200,
                      fields: Optional[List[str]] = None,
                      amount_min: Optional[float] = None,
                      amount_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """Query invoices with various filters."""
        if not self._initialized:
            raise RuntimeError("Odoo not initialized")
        
        domain = []
        
        if date_from:
            domain.append(["date_invoice", ">=", date_from])
        if date_to:
            domain.append(["date_invoice", "<=", date_to])
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        if state:
            domain.append(["state", "=", state])
        if type:
            domain.append(["type", "=", type])
        if amount_min:
            domain.append(["amount_total", ">=", amount_min])
        if amount_max:
            domain.append(["amount_total", "<=", amount_max])
        
        # Default fields if none specified
        if fields is None:
            fields = ["id", "name", "partner_id", "date_invoice", "amount_total", "state", "type"]
        
        return self.client.search_read(
            "account.invoice",
            domain=domain,
            fields=fields,
            limit=limit,
            order="date_invoice desc"
        )

    def join_leads_invoices(self,
                           date_from: Optional[str] = None,
                           date_to: Optional[str] = None,
                           invoice_date_from: Optional[str] = None,
                           invoice_date_to: Optional[str] = None,
                           status: Optional[str] = None,
                           user: Optional[str] = None,
                           source: Optional[str] = None,
                           invoice_state: Optional[str] = None,
                           include_all_leads: bool = True) -> List[Dict[str, Any]]:
        """Join leads with their invoice data based on partner_id."""
        if not self._initialized:
            raise RuntimeError("Odoo not initialized")
        
        # Get leads
        filter_obj = LeadFilter().model("crm.lead")
        
        if date_from:
            filter_obj.by_date_range(start_date=date_from, field_name="source_date")
        if date_to:
            filter_obj.by_date_range(end_date=date_to, field_name="source_date")
        if status:
            filter_obj.by_status([status])
        if user:
            filter_obj.by_user_assignments(user_names=[user])
        if source:
            filter_obj.by_web_source_ids([source])
        
        leads = self.lead_manager.get_leads(filter_obj, fields=[
            "id", "name", "partner_id", "email_from", "phone", "source_date", 
            "status", "user_id", "closer_id", "open_user_id"
        ])
        
        if not leads:
            return []
        
        # Get partner IDs from leads
        partner_ids = [lead.get("partner_id")[0] if isinstance(lead.get("partner_id"), list) 
                      else lead.get("partner_id") 
                      for lead in leads if lead.get("partner_id")]
        
        if not partner_ids:
            return leads
        
        # Get invoices for these partners
        invoice_domain = [["partner_id", "in", partner_ids]]
        
        if invoice_date_from:
            invoice_domain.append(["date_invoice", ">=", invoice_date_from])
        if invoice_date_to:
            invoice_domain.append(["date_invoice", "<=", invoice_date_to])
        if invoice_state:
            invoice_domain.append(["state", "=", invoice_state])
        
        invoices = self.client.search_read(
            "account.invoice",
            domain=invoice_domain,
            fields=["id", "name", "partner_id", "date_invoice", "amount_total", "state", "type"],
            order="date_invoice desc"
        )
        
        # Create invoice map by partner_id
        invoice_map = {}
        for invoice in invoices:
            partner_id = invoice.get("partner_id")
            if isinstance(partner_id, list):
                partner_id = partner_id[0]
            if partner_id not in invoice_map:
                invoice_map[partner_id] = []
            invoice_map[partner_id].append(invoice)
        
        # Join leads with invoices
        result = []
        for lead in leads:
            partner_id = lead.get("partner_id")
            if isinstance(partner_id, list):
                partner_id = partner_id[0]
            
            lead_invoices = invoice_map.get(partner_id, [])
            
            # Skip leads without invoices if include_all_leads is False
            if not include_all_leads and not lead_invoices:
                continue
            
            combined_data = {
                "lead": lead,
                "invoices": lead_invoices,
                "total_invoiced": sum(inv.get("amount_total", 0) for inv in lead_invoices),
                "invoice_count": len(lead_invoices)
            }
            
            result.append(combined_data)
        
        return result

# Initialize the bridge
bridge = OdooMCPBridge()

@mcp.tool()
def query_leads(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    user: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    fields: Optional[List[str]] = None
) -> str:
    """Query Odoo leads with various filters."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        leads = bridge.query_leads(
            date_from=date_from,
            date_to=date_to,
            status=status,
            user=user,
            source=source,
            limit=limit,
            fields=fields
        )
        return json.dumps(leads, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def update_leads(
    lead_ids: List[int],
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    closer_id: Optional[int] = None,
    closer_name: Optional[str] = None,
    open_user_id: Optional[int] = None,
    open_user_name: Optional[str] = None,
    status: Optional[str] = None,
    model: str = "crm.lead"
) -> str:
    """Update leads with new assignments and fields."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        result = bridge.update_leads(
            lead_ids=lead_ids,
            user_id=user_id,
            user_name=user_name,
            closer_id=closer_id,
            closer_name=closer_name,
            open_user_id=open_user_id,
            open_user_name=open_user_name,
            status=status,
            model=model
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def query_with_filter(
    query: str,
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    closer_id: Optional[int] = None,
    closer_name: Optional[str] = None,
    open_user_id: Optional[int] = None,
    open_user_name: Optional[str] = None,
    status: Optional[str] = None,
    fields: Optional[List[str]] = None
) -> str:
    """Query leads using JSON query filter."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        # Parse the JSON query
        query_filters = json.loads(query)
        filter_obj = LeadFilter().model("crm.lead").custom_filter(query_filters)
        
        # Get leads to update
        leads = bridge.lead_manager.get_leads(filter_obj, fields=["id"])
        lead_ids = [lead["id"] for lead in leads]
        
        if not lead_ids:
            return f"No leads found matching query: {query}"
        
        # Prepare update arguments
        update_args = {"lead_ids": lead_ids, "model": "crm.lead"}
        
        # Add optional update parameters
        for key in ["user_id", "user_name", "closer_id", "closer_name", "open_user_id", "open_user_name", "status"]:
            if locals().get(key) is not None:
                update_args[key] = locals()[key]
        
        result = bridge.update_leads(**update_args)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def count_leads(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    user: Optional[str] = None,
    source: Optional[str] = None
) -> str:
    """Count leads matching criteria."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        count = bridge.count_leads(
            date_from=date_from,
            date_to=date_to,
            status=status,
            user=user,
            source=source
        )
        return str(count)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def query_invoices(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    partner_id: Optional[int] = None,
    state: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 200,
    fields: Optional[List[str]] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None
) -> str:
    """Query invoices with various filters."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        invoices = bridge.query_invoices(
            date_from=date_from,
            date_to=date_to,
            partner_id=partner_id,
            state=state,
            type=type,
            limit=limit,
            fields=fields,
            amount_min=amount_min,
            amount_max=amount_max
        )
        return json.dumps(invoices, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def join_leads_invoices(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    invoice_date_from: Optional[str] = None,
    invoice_date_to: Optional[str] = None,
    status: Optional[str] = None,
    user: Optional[str] = None,
    source: Optional[str] = None,
    invoice_state: Optional[str] = None,
    include_all_leads: bool = True
) -> str:
    """Join leads with their invoice data based on partner_id."""
    if not bridge._initialized:
        if not bridge.initialize():
            return "Failed to initialize Odoo connection. Please check your configuration."
    
    try:
        results = bridge.join_leads_invoices(
            date_from=date_from,
            date_to=date_to,
            invoice_date_from=invoice_date_from,
            invoice_date_to=invoice_date_to,
            status=status,
            user=user,
            source=source,
            invoice_state=invoice_state,
            include_all_leads=include_all_leads
        )
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Check if Odoo is configured
    try:
        from odoo_lead_manager.client import OdooClient
        client = OdooClient()
        try:
            client.connect()  # Test actual connection
            print("✅ Odoo connection verified", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Warning: Odoo connection failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Warning: Odoo configuration error: {e}", file=sys.stderr)
    
    # Run the server
    mcp.run(transport="sse")