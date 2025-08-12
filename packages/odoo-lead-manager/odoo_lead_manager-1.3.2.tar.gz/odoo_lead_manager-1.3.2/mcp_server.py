#!/usr/bin/env python3
"""
MCP Server for Odoo Lead Manager

This server provides tools to interact with Odoo leads through MCP:
- Query leads with various filters
- Update lead assignments and fields
- Count leads matching criteria
- Get lead summaries and analytics

Compatible with Claude Desktop and other MCP clients.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, date

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from odoo_lead_manager.client import OdooClient
from odoo_lead_manager.lead_manager import LeadManager
from odoo_lead_manager.filters import LeadFilter


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

# Create the MCP server
server = Server("odoo-lead-manager")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="query_leads",
            description="Query Odoo leads with various filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "date_to": {
                        "type": "string", 
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lead status (new, in_progress, won, lost, etc.)"
                    },
                    "user": {
                        "type": "string",
                        "description": "Assigned user name or partial match"
                    },
                    "source": {
                        "type": "string",
                        "description": "Web source name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of leads to return (default: 100)",
                        "default": 100
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return"
                    }
                }
            }
        ),
        Tool(
            name="update_leads",
            description="Update leads with new assignments and fields",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of lead IDs to update"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID to assign leads to"
                    },
                    "user_name": {
                        "type": "string",
                        "description": "User name to assign leads to (will be resolved to ID)"
                    },
                    "closer_id": {
                        "type": "integer",
                        "description": "Closer ID to assign"
                    },
                    "closer_name": {
                        "type": "string",
                        "description": "Closer name to assign (will be resolved to ID)"
                    },
                    "open_user_id": {
                        "type": "integer",
                        "description": "Open user ID to assign"
                    },
                    "open_user_name": {
                        "type": "string",
                        "description": "Open user name to assign (will be resolved to ID)"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status to set"
                    },
                    "model": {
                        "type": "string",
                        "description": "Odoo model to update (default: crm.lead)",
                        "default": "crm.lead"
                    }
                },
                "required": ["lead_ids"]
            }
        ),
        Tool(
            name="query_with_filter",
            description="Query leads using JSON query filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "JSON string of Odoo domain filters"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID to assign to matching leads"
                    },
                    "user_name": {
                        "type": "string",
                        "description": "User name to assign to matching leads"
                    },
                    "closer_id": {
                        "type": "integer",
                        "description": "Closer ID to assign"
                    },
                    "closer_name": {
                        "type": "string",
                        "description": "Closer name to assign"
                    },
                    "open_user_id": {
                        "type": "integer",
                        "description": "Open user ID to assign"
                    },
                    "open_user_name": {
                        "type": "string",
                        "description": "Open user name to assign"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status to set"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="count_leads",
            description="Count leads matching criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lead status"
                    },
                    "user": {
                        "type": "string",
                        "description": "Assigned user name"
                    },
                    "source": {
                        "type": "string",
                        "description": "Web source name"
                    }
                }
            }
        ),
        Tool(
            name="query_invoices",
            description="Query invoices with various filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "partner_id": {
                        "type": "integer",
                        "description": "Partner ID (customer)"
                    },
                    "state": {
                        "type": "string",
                        "description": "Invoice state (draft, open, paid, cancel)"
                    },
                    "type": {
                        "type": "string",
                        "description": "Invoice type (out_invoice, in_invoice, out_refund, in_refund)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 200
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return"
                    },
                    "amount_min": {
                        "type": "number",
                        "description": "Minimum invoice amount"
                    },
                    "amount_max": {
                        "type": "number",
                        "description": "Maximum invoice amount"
                    }
                }
            }
        ),
        Tool(
            name="join_leads_invoices",
            description="Join leads with their invoice data based on partner_id",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date for leads (YYYY-MM-DD)"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date for leads (YYYY-MM-DD)"
                    },
                    "invoice_date_from": {
                        "type": "string",
                        "description": "Start date for invoices (YYYY-MM-DD)"
                    },
                    "invoice_date_to": {
                        "type": "string",
                        "description": "End date for invoices (YYYY-MM-DD)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lead status"
                    },
                    "user": {
                        "type": "string",
                        "description": "Assigned user name"
                    },
                    "source": {
                        "type": "string",
                        "description": "Web source name"
                    },
                    "invoice_state": {
                        "type": "string",
                        "description": "Invoice state"
                    },
                    "include_all_leads": {
                        "type": "boolean",
                        "description": "Include leads without invoices (default: true)"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    # Initialize if not already done
    if not bridge._initialized:
        if not bridge.initialize():
            return [TextContent(type="text", text="Failed to initialize Odoo connection. Please check your configuration.")]
    
    try:
        if name == "query_leads":
            leads = bridge.query_leads(**arguments)
            return [TextContent(type="text", text=json.dumps(leads, indent=2, default=str))]
        
        elif name == "update_leads":
            result = bridge.update_leads(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "query_with_filter":
            # Parse the JSON query
            query_filters = json.loads(arguments["query"])
            filter_obj = LeadFilter().model("crm.lead").custom_filter(query_filters)
            
            # Get leads to update
            leads = bridge.lead_manager.get_leads(filter_obj, fields=["id"])
            lead_ids = [lead["id"] for lead in leads]
            
            if not lead_ids:
                return [TextContent(type="text", text=f"No leads found matching query: {arguments['query']}")]
            
            # Prepare update arguments
            update_args = {"lead_ids": lead_ids, "model": "crm.lead"}
            
            # Add optional update parameters
            for key in ["user_id", "user_name", "closer_id", "closer_name", "open_user_id", "open_user_name", "status"]:
                if key in arguments and arguments[key] is not None:
                    update_args[key] = arguments[key]
            
            result = bridge.update_leads(**update_args)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        elif name == "count_leads":
            count = bridge.count_leads(**arguments)
            return [TextContent(type="text", text=str(count))]
        
        elif name == "query_invoices":
            invoices = bridge.query_invoices(**arguments)
            return [TextContent(type="text", text=json.dumps(invoices, indent=2, default=str))]
        
        elif name == "join_leads_invoices":
            results = bridge.join_leads_invoices(**arguments)
            return [TextContent(type="text", text=json.dumps(results, indent=2, default=str))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
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
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())