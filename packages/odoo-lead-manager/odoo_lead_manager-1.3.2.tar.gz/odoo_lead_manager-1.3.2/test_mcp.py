#!/usr/bin/env python3
"""
Test script for MCP server functionality
"""

import json
import asyncio
from mcp_server import bridge

async def test_mcp_server():
    """Test MCP server functionality."""
    print("🧪 Testing MCP Server...")
    
    # Initialize bridge
    if not bridge.initialize():
        print("❌ Failed to initialize Odoo connection")
        return
    
    print("✅ Odoo connection established")
    
    # Test count leads
    try:
        count = bridge.count_leads()
        print(f"📊 Total leads: {count}")
    except Exception as e:
        print(f"❌ Error counting leads: {e}")
    
    # Test query leads
    try:
        leads = bridge.query_leads(limit=2)
        print(f"🔍 Sample leads: {len(leads)} found")
        if leads:
            print(f"   Example lead: ID {leads[0]['id']}, Status: {leads[0].get('status', 'N/A')}")
    except Exception as e:
        print(f"❌ Error querying leads: {e}")
    
    print("✅ MCP server test completed")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())