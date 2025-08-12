#!/usr/bin/env python3
"""
Gradio-based MCP Server for Odoo Lead Manager

This server uses Gradio's built-in MCP support to automatically convert
our Odoo Lead Manager functions into MCP tools.

Installation:
pip install "gradio[mcp]" "gradio>=5.0.0"

Usage:
python mcp_server_gradio.py
"""

import gradio as gr
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from odoo_lead_manager.client import OdooClient
from odoo_lead_manager.lead_manager import LeadManager
from odoo_lead_manager.filters import LeadFilter


class OdooMCPService:
    """Service class for Odoo operations"""
    
    def __init__(self):
        self.client = None
        self.lead_manager = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize connection to Odoo"""
        try:
            self.client = OdooClient()
            self.lead_manager = LeadManager(self.client)
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Odoo: {e}")
            return False
    
    def query_leads(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        user: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        fields: Optional[str] = None  # JSON string of list
    ) -> str:
        """
        Query Odoo leads with various filters.
        
        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format  
            status: Lead status (new, in_progress, won, lost, etc.)
            user: Assigned user name
            source: Web source name
            limit: Maximum number of results (default: 100)
            fields: JSON array of specific fields to return
        
        Returns:
            JSON string of leads data
        """
        if not self._initialized and not self.initialize():
            return json.dumps({"error": "Failed to initialize Odoo connection"})
        
        try:
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
            
            # Parse fields if provided
            field_list = None
            if fields:
                try:
                    field_list = json.loads(fields)
                except:
                    field_list = None
            
            leads = self.lead_manager.get_leads(filter_obj, fields=field_list)
            return json.dumps(leads, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def update_leads(
        self,
        lead_ids: str,  # JSON string of list
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
        closer_id: Optional[int] = None,
        closer_name: Optional[str] = None,
        open_user_id: Optional[int] = None,
        open_user_name: Optional[str] = None,
        status: Optional[str] = None,
        model: str = "crm.lead"
    ) -> str:
        """
        Update leads with new assignments and fields.
        
        Args:
            lead_ids: JSON array of lead IDs to update
            user_id: User ID to assign leads to
            user_name: User name to assign (resolves to ID)
            closer_id: Closer ID to assign
            closer_name: Closer name to assign (resolves to ID)
            open_user_id: Open user ID to assign
            open_user_name: Open user name to assign (resolves to ID)
            status: New status to set
            model: Odoo model to update (default: crm.lead)
        
        Returns:
            JSON string with update results
        """
        if not self._initialized and not self.initialize():
            return json.dumps({"error": "Failed to initialize Odoo connection"})
        
        try:
            # Parse lead_ids
            lead_ids_list = json.loads(lead_ids)
            if not isinstance(lead_ids_list, list):
                return json.dumps({"error": "lead_ids must be a JSON array"})
            
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
                return json.dumps({"error": "No update values provided"})
            
            result = self.lead_manager.update_lead_assignments(
                lead_ids_list, model=model, **update_values
            )
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def count_leads(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        user: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Count leads matching criteria.
        
        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            status: Lead status to filter by
            user: Assigned user name
            source: Web source name
        
        Returns:
            Count as string
        """
        if not self._initialized and not self.initialize():
            return "0"
        
        try:
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
            
            count = self.lead_manager.count_leads(filter_obj)
            return str(count)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def query_invoices(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 200,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None
    ) -> str:
        """
        Query invoices with various filters.
        
        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            partner_id: Partner ID (customer)
            state: Invoice state (draft, open, paid, cancel)
            type: Invoice type (out_invoice, in_invoice, out_refund, in_refund)
            limit: Maximum results (default: 200)
            amount_min: Minimum invoice amount
            amount_max: Maximum invoice amount
        
        Returns:
            JSON string of invoices data
        """
        if not self._initialized and not self.initialize():
            return json.dumps({"error": "Failed to initialize Odoo connection"})
        
        try:
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
            
            fields = ["id", "name", "partner_id", "date_invoice", "amount_total", "state", "type"]
            
            invoices = self.client.search_read(
                "account.invoice",
                domain=domain,
                fields=fields,
                limit=limit,
                order="date_invoice desc"
            )
            
            return json.dumps(invoices, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


# Initialize the service
service = OdooMCPService()

# Create Gradio interface
def create_gradio_interface():
    """Create the Gradio MCP interface"""
    
    with gr.Blocks(title="Odoo Lead Manager MCP") as demo:
        gr.Markdown("# 🤖 Odoo Lead Manager MCP Server")
        gr.Markdown("Use this interface to interact with Odoo leads via MCP")
        
        with gr.Tab("Query Leads"):
            with gr.Row():
                date_from = gr.Textbox(label="Date From (YYYY-MM-DD)", placeholder="2024-01-01")
                date_to = gr.Textbox(label="Date To (YYYY-MM-DD)", placeholder="2024-12-31")
            
            with gr.Row():
                status = gr.Dropdown(
                    label="Status",
                    choices=["new", "in_progress", "won", "lost", "cancelled"],
                    allow_custom_value=True
                )
                user = gr.Textbox(label="Assigned User")
                source = gr.Textbox(label="Web Source")
            
            limit = gr.Slider(label="Limit", minimum=1, maximum=1000, value=100, step=1)
            fields = gr.Textbox(label="Fields (JSON array)", placeholder='["id", "name", "email"]')
            
            query_btn = gr.Button("Query Leads", variant="primary")
            query_output = gr.JSON(label="Results")
            
            query_btn.click(
                fn=service.query_leads,
                inputs=[date_from, date_to, status, user, source, limit, fields],
                outputs=query_output
            )
        
        with gr.Tab("Update Leads"):
            lead_ids = gr.Textbox(label="Lead IDs (JSON array)", placeholder="[123, 456, 789]")
            
            with gr.Row():
                user_id = gr.Number(label="User ID", precision=0)
                user_name = gr.Textbox(label="User Name")
            
            with gr.Row():
                closer_id = gr.Number(label="Closer ID", precision=0)
                closer_name = gr.Textbox(label="Closer Name")
            
            with gr.Row():
                open_user_id = gr.Number(label="Open User ID", precision=0)
                open_user_name = gr.Textbox(label="Open User Name")
            
            status_update = gr.Textbox(label="New Status")
            model = gr.Textbox(label="Model", value="crm.lead")
            
            update_btn = gr.Button("Update Leads", variant="primary")
            update_output = gr.JSON(label="Update Results")
            
            update_btn.click(
                fn=service.update_leads,
                inputs=[lead_ids, user_id, user_name, closer_id, closer_name, 
                       open_user_id, open_user_name, status_update, model],
                outputs=update_output
            )
        
        with gr.Tab("Count Leads"):
            with gr.Row():
                count_date_from = gr.Textbox(label="Date From", placeholder="2024-01-01")
                count_date_to = gr.Textbox(label="Date To", placeholder="2024-12-31")
                count_status = gr.Textbox(label="Status")
                count_user = gr.Textbox(label="User")
                count_source = gr.Textbox(label="Source")
            
            count_btn = gr.Button("Count Leads", variant="primary")
            count_output = gr.Textbox(label="Count")
            
            count_btn.click(
                fn=service.count_leads,
                inputs=[count_date_from, count_date_to, count_status, count_user, count_source],
                outputs=count_output
            )
        
        with gr.Tab("Query Invoices"):
            with gr.Row():
                inv_date_from = gr.Textbox(label="Date From", placeholder="2024-01-01")
                inv_date_to = gr.Textbox(label="Date To", placeholder="2024-12-31")
                inv_partner_id = gr.Number(label="Partner ID", precision=0)
            
            with gr.Row():
                inv_state = gr.Dropdown(
                    label="State",
                    choices=["draft", "open", "paid", "cancel"],
                    allow_custom_value=True
                )
                inv_type = gr.Dropdown(
                    label="Type",
                    choices=["out_invoice", "in_invoice", "out_refund", "in_refund"],
                    allow_custom_value=True
                )
            
            inv_limit = gr.Slider(label="Limit", minimum=1, maximum=500, value=200, step=1)
            inv_amount_min = gr.Number(label="Amount Min")
            inv_amount_max = gr.Number(label="Amount Max")
            
            inv_btn = gr.Button("Query Invoices", variant="primary")
            inv_output = gr.JSON(label="Invoice Results")
            
            inv_btn.click(
                fn=service.query_invoices,
                inputs=[inv_date_from, inv_date_to, inv_partner_id, inv_state, inv_type,
                       inv_limit, inv_amount_min, inv_amount_max],
                outputs=inv_output
            )
        
        gr.Markdown("""
        ### 🚀 MCP Server
        This interface is automatically available as an MCP server at:
        - **HTTP**: `http://localhost:7860/gradio_api/mcp/sse`
        - **STDIO**: Use `mcp_server.py` for CLI mode
        """)
    
    return demo


if __name__ == "__main__":
    # Initialize connection test
    print("🔍 Testing Odoo connection...")
    if service.initialize():
        print("✅ Odoo connection established")
    else:
        print("⚠️ Warning: Odoo connection failed - check .env configuration")
    
    # Create and launch Gradio interface with MCP support
    demo = create_gradio_interface()
    
    # Launch with MCP server enabled
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        mcp_server=True  # Enable MCP server
    )