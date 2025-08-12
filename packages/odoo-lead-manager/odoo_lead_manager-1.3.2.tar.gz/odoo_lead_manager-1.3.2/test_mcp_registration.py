#!/usr/bin/env python3
"""
Test MCP server tool registration without running the full server.
"""

import re
import sys
from pathlib import Path

def validate_mcp_tools():
    """Validate MCP tool registration."""
    server_file = Path(__file__).parent / "mcp_server_http.py"
    
    if not server_file.exists():
        print("❌ MCP server file not found")
        return False
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Extract tool names from list_tools
    list_tools_match = re.search(r'@server\.list_tools\(\)(.*?)@server\.call_tool\(\)', content, re.DOTALL)
    if not list_tools_match:
        print("❌ Could not find list_tools section")
        return False
    
    list_tools_content = list_tools_match.group(1)
    tool_names = re.findall(r'name="([^"]+)"', list_tools_content)
    
    # Extract handler functions
    handlers = re.findall(r'elif name == "([^"]+)":', content)
    
    # Check for handler function definitions
    handler_functions = re.findall(r'async def handle_([^(]+)\(', content)
    
    print("✅ MCP Tool Registration Analysis:")
    print("=" * 50)
    print(f"Tools in list_tools(): {len(tool_names)}")
    print(f"Handler mappings: {len(handlers)}")
    print(f"Handler functions: {len(handler_functions)}")
    
    print("\n📋 Registered tools:")
    for tool in tool_names:
        print(f"  • {tool}")
    
    print("\n📋 Handler mappings:")
    for handler in handlers:
        print(f"  • {handler}")
    
    print("\n📋 Handler functions:")
    for func in handler_functions:
        print(f"  • {func}")
    
    # Check for mismatches
    missing_handlers = [tool for tool in tool_names if tool not in handlers]
    extra_handlers = [handler for handler in handlers if handler not in tool_names]
    
    if missing_handlers:
        print(f"\n❌ Missing handlers: {missing_handlers}")
    
    if extra_handlers:
        print(f"\n⚠️  Extra handlers: {extra_handlers}")
    
    # Check if all tools have handler functions
    missing_functions = []
    for tool in tool_names:
        handler_name = f"handle_{tool}"
        if handler_name not in [f"handle_{f}" for f in handler_functions]:
            missing_functions.append(handler_name)
    
    if missing_functions:
        print(f"\n❌ Missing handler functions: {missing_functions}")
    
    # Check for Odoo model compatibility
    if 'account.invoice' in content and 'account.move' not in content:
        print("\n⚠️  Using old 'account.invoice' model - may need 'account.move' for newer Odoo")
    
    return len(missing_handlers) == 0 and len(missing_functions) == 0

if __name__ == "__main__":
    success = validate_mcp_tools()
    sys.exit(0 if success else 1)