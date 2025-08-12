# Odoo Lead Manager MCP Server

This MCP (Model Context Protocol) server provides seamless integration between Claude Desktop and the Odoo Lead Manager package, allowing AI assistants to interact with Odoo leads directly.

## 🚀 Features

- **Query leads** with date ranges, status, user assignments, and more
- **Update lead assignments** for users, closers, and open users
- **Count leads** matching specific criteria
- **Flexible filtering** using JSON query syntax
- **Real-time interaction** with Odoo CRM

## 📋 Available Tools

### 1. `query_leads`
Query leads with various filters.

**Parameters:**
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `status`: Lead status (new, in_progress, won, lost, etc.)
- `user`: Assigned user name
- `source`: Web source name
- `limit`: Maximum results (default: 100)
- `fields`: Specific fields to return

**Example:**
```json
{
  "date_from": "2024-01-01",
  "status": "new",
  "limit": 50
}
```

### 2. `update_leads`
Update specific leads with new assignments.

**Parameters:**
- `lead_ids`: List of lead IDs to update
- `user_id`: User ID to assign
- `user_name`: User name (auto-resolved to ID)
- `closer_id`: Closer ID to assign
- `closer_name`: Closer name (auto-resolved)
- `open_user_id`: Open user ID
- `open_user_name`: Open user name
- `status`: New status
- `model`: Odoo model (default: crm.lead)

**Example:**
```json
{
  "lead_ids": [123, 456, 789],
  "user_id": 1,
  "status": "in_progress"
}
```

### 3. `query_with_filter`
Query and optionally update leads using JSON query filters.

**Parameters:**
- `query`: JSON string of Odoo domain filters
- `user_id`: User ID to assign (optional)
- `user_name`: User name to assign (optional)
- `closer_id`: Closer ID (optional)
- `closer_name`: Closer name (optional)
- `open_user_id`: Open user ID (optional)
- `open_user_name`: Open user name (optional)
- `status`: Status to set (optional)

**Example:**
```json
{
  "query": "[[\"source_date\", \">=\", \"2024-01-01\"], [\"status\", \"=\", \"new\"]]",
  "user_id": 1,
  "status": "assigned"
}
```

### 4. `count_leads`
Count leads matching criteria.

**Parameters:** Same as `query_leads`.

**Example:**
```json
{
  "date_from": "2024-01-01",
  "status": "won"
}
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
# Install MCP dependencies
pip install fastmcp

# Or use the setup script
python setup_mcp.py
```

### 2. Configure Odoo Credentials

```bash
# Interactive configuration
odlm configure

# Or set environment variables
export ODOO_HOST=your-odoo-server.com
export ODOO_PORT=8069
export ODOO_DB=your-database
export ODOO_USERNAME=your-username
export ODOO_PASSWORD=your-password
```

### 3. Claude Desktop Setup

#### macOS
Copy the configuration to Claude Desktop:

```bash
# The setup script will do this automatically
python setup_mcp.py

# Or manually:
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Manual Configuration
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo-lead-manager": {
      "command": "/path/to/python",
      "args": ["/path/to/odoo_lead_distribution/mcp_server.py"],
      "env": {
        "ODOO_HOST": "your-odoo-server.com",
        "ODOO_PORT": "8069",
        "ODOO_DB": "your-database",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After configuration, restart Claude Desktop to load the new MCP server.

## 🧪 Testing

### Test the MCP Server

```bash
# Test server directly
python mcp_server.py

# Test with CLI tools
odlm query --date-from 2024-01-01 --limit 5
```

### Test with Claude Desktop

Once configured, you can use natural language with Claude:

- "Show me new leads from January 2024"
- "Count leads assigned to Alice"
- "Update leads 123, 456, 789 to user John"
- "Find leads from Google ads and assign them to user 1"

## 📝 Usage Examples

### Querying Leads
```
Show me all new leads from this week
→ Uses: query_leads with date_from and status filters

Get leads assigned to 'Alice Smith' from Facebook
→ Uses: query_leads with user and source filters

Count leads from January 2024 that are still new
→ Uses: count_leads with date and status filters
```

### Updating Leads
```
Update leads 1001, 1002, 1003 to user Alice
→ Uses: update_leads with lead_ids and user_name

Assign all new leads from this week to user 5
→ Uses: query_with_filter with date range and status

Change status of leads assigned to Bob to 'in_progress'
→ Uses: query_with_filter with user and status update
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check Odoo credentials in environment variables
   - Ensure Odoo server is accessible
   - Verify RPC/XML-RPC is enabled on Odoo

2. **No leads found**
   - Check date format (YYYY-MM-DD)
   - Verify user names exist in the system
   - Ensure source names match exactly

3. **Invalid field errors**
   - Use correct field names from your Odoo model
   - Check available fields with: `odlm leads --limit 1 --format json`

### Debug Mode

Enable debug logging:
```bash
python mcp_server.py --debug
```

### Configuration Check

```bash
# Check Odoo connection
odlm check --verbose

# Test configuration
python -c "from odoo_lead_manager.client import OdooClient; OdooClient().connect()"
```

## 📊 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ODOO_HOST` | Odoo server hostname | `legacy.approvedprovidersnetwork.com` |
| `ODOO_PORT` | Odoo server port | `8069` |
| `ODOO_DB` | Database name | `mydb` |
| `ODOO_USERNAME` | Username | `admin` |
| `ODOO_PASSWORD` | Password | `secret123` |
| `ODOO_PROTOCOL` | Protocol (jsonrpc/https) | `jsonrpc` |

## 🔄 Development

### Running in Development

```bash
# Install in development mode
pip install -e .

# Run MCP server
python mcp_server.py

# Test with Claude Desktop
# Use the configuration file provided
```

### Adding New Tools

To add new tools, edit the `list_tools()` and `call_tool()` functions in `mcp_server.py`.

## 📞 Support

- **Issues**: Create GitHub issues for bugs or feature requests
- **Configuration**: Run `odlm configure` for setup help
- **Documentation**: Check this README and inline tool descriptions