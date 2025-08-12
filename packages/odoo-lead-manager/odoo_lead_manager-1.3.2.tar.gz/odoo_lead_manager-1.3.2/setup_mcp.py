#!/usr/bin/env python3
"""
Setup script for Odoo Lead Manager MCP Server

This script installs the necessary dependencies for the MCP server
and provides instructions for Claude Desktop configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mcp_dependencies():
    """Install MCP server dependencies."""
    print("🔧 Setting up MCP server dependencies...")
    
    try:
        # Install fastmcp
        subprocess.run([
            sys.executable, "-m", "pip", "install", "fastmcp"
        ], check=True)
        
        # Install mcp server
        subprocess.run([
            sys.executable, "-m", "pip", "install", "mcp"
        ], check=True)
        
        print("✅ MCP dependencies installed successfully!")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_odoo_config():
    """Check if Odoo is configured."""
    try:
        from odoo_lead_manager.client import OdooClient
        client = OdooClient()
        config = client._get_config()
        
        required_vars = ['host', 'db', 'username', 'password']
        missing = [var for var in required_vars if not config.get(var)]
        
        if missing:
            print(f"⚠️  Missing Odoo configuration: {', '.join(missing)}")
            print("💡 Run 'odlm configure' to set up credentials")
            return False
        else:
            print("✅ Odoo configuration found")
            return True
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False

def setup_claude_desktop():
    """Setup Claude Desktop configuration."""
    config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Read the template config
    template_path = Path(__file__).parent / "claude_desktop_config.json"
    
    if not template_path.exists():
        print("❌ Claude Desktop config template not found")
        return False
    
    try:
        with open(template_path) as f:
            config = json.load(f)
        
        # Update with actual paths
        config["mcpServers"]["odoo-lead-manager"]["args"][0] = sys.executable
        config["mcpServers"]["odoo-lead-manager"]["args"][1] = str(Path(__file__).parent / "mcp_server.py")
        
        # Write to Claude Desktop config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Claude Desktop config written to: {config_path}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to setup Claude Desktop config: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Odoo Lead Manager MCP Server...")
    
    # Install dependencies
    if not install_mcp_dependencies():
        return 1
    
    # Check configuration
    config_ok = check_odoo_config()
    
    # Setup Claude Desktop (macOS)
    if sys.platform == "darwin":
        claude_setup = setup_claude_desktop()
    else:
        claude_setup = False
        print("ℹ️  Claude Desktop setup skipped (non-macOS system)")
    
    print("\n" + "="*50)
    print("🎉 MCP Server Setup Complete!")
    print("="*50)
    
    if not config_ok:
        print("\n⚠️  Next steps:")
        print("1. Run: odlm configure")
        print("2. Update environment variables in claude_desktop_config.json")
        print("3. Restart Claude Desktop")
    
    print("\n📋 Usage examples:")
    print("Query leads: odlm query --date-from 2024-01-01 --limit 10")
    print("Test MCP: python mcp_server.py")
    print("Claude Desktop: Use the MCP tools after configuration")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())