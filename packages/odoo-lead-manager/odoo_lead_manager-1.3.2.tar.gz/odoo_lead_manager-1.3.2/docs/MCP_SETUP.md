# MCP Server Setup Guide

This guide provides comprehensive instructions for setting up and running the Odoo Lead Manager MCP server.

## 📋 Prerequisites

- Python 3.8+ 
- uv (Python package manager)
- Odoo instance with valid credentials

## 🔧 Installation

### 1. Install uv (if not already installed)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup
```bash
git clone <repository-url>
cd odoo_lead_distribution

# Create virtual environment and install dependencies
uv venv
uv pip install -e .
uv pip install -r requirements.txt  # Includes MCP dependencies
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required Odoo connection settings
ODOO_HOST=your-odoo-server.com
ODOO_PORT=8069
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional settings
ODOO_PROTOCOL=jsonrpc
ODOO_TIMEOUT=120
```

## 🚀 Running the MCP Server

### Option 1: STDIO Server (Claude Desktop)
```bash
uv run python mcp_server.py
```

### Option 2: HTTP Server (Port 8001)
```bash
uv run python mcp_server_http.py
```

### Option 3: With Docker
```bash
# Build image
docker build -t odoo-mcp-server .

# Run container
docker run -d \
  --name odoo-mcp \
  -e ODOO_HOST=your-odoo-server.com \
  -e ODOO_PORT=8069 \
  -e ODOO_DB=your_database \
  -e ODOO_USERNAME=your_username \
  -e ODOO_PASSWORD=your_password \
  -p 8001:8001 \
  odoo-mcp-server
```

## 🔗 Claude Desktop Integration

Add to Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%/Claude/claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "odoo-lead-manager": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/odoo_lead_distribution/mcp_server.py"],
      "env": {
        "ODOO_HOST": "your-odoo-server.com",
        "ODOO_PORT": "8069",
        "ODOO_DB": "your_database",
        "ODOO_USERNAME": "your_username",
        "ODOO_PASSWORD": "your_password"
      }
    }
  }
}
```

## 🛠️ Available Tools

The MCP server provides these tools:

### 1. `query_leads`
Query leads with various filters.

**Parameters:**
- `date_from` (string): Start date (YYYY-MM-DD)
- `date_to` (string): End date (YYYY-MM-DD)
- `status` (string): Lead status (new, in_progress, won, lost, etc.)
- `user` (string): Assigned user name
- `source` (string): Web source name
- `limit` (integer): Maximum results (default: 100)
- `fields` (array): Specific fields to return

### 2. `update_leads`
Update leads with new assignments and fields.

**Parameters:**
- `lead_ids` (array, required): List of lead IDs to update
- `user_id` (integer): User ID to assign
- `user_name` (string): User name to assign (resolves to ID)
- `closer_id` (integer): Closer ID to assign
- `closer_name` (string): Closer name to assign
- `status` (string): New status to set
- `model` (string): Odoo model (default: crm.lead)

### 3. `count_leads`
Count leads matching criteria.

### 4. `query_invoices`
Query invoices with various filters.

### 5. `join_leads_invoices`
Join leads with their invoice data based on partner_id.

## 🔍 Testing the Connection

```bash
# Test Odoo connection
uv run python -c "from odoo_lead_manager.client import OdooClient; client = OdooClient(); client.connect(); print('✅ Connected successfully')"

# Test MCP server
uv run python mcp_server.py
# Should show: ✅ Odoo connection verified
```

## 📦 Dependencies

- **Core**: `odoorpc`, `python-dateutil`, `pandas`, `numpy`, `pydantic`
- **MCP**: `mcp>=1.0.0`, `fastmcp>=0.4.0`, `typing-extensions>=4.0.0`
- **HTTP**: `fastapi>=0.104.0`, `uvicorn[standard]>=0.24.0`

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'mcp'**
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Connection refused to Odoo**
   - Check Odoo host and port
   - Verify credentials in .env file
   - Ensure Odoo is accessible from the container

3. **Permission denied in Docker**
   ```bash
   docker run --user $(id -u):$(id -g) ...
   ```

### Debug Mode
```bash
# Run with debug output
uv run python -u mcp_server.py
```

## 🚀 Quick Start Script

Save as `setup_mcp.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up Odoo MCP Server..."

# Install uv if not exists
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Setup environment
cd "$(dirname "$0")"
uv venv
source .venv/bin/activate
uv pip install -e .
uv pip install -r requirements.txt

echo "✅ Setup complete! Run: uv run python mcp_server.py"
```

Make it executable:
```bash
chmod +x setup_mcp.sh
./setup_mcp.sh
```