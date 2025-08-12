# Gradio MCP Server for Odoo Lead Manager

This implementation uses Gradio's built-in MCP support to create a web-based MCP server with a visual interface.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install gradio with MCP support
uv pip install -r requirements-gradio.txt

# Or install directly
uv pip install "gradio[mcp]>=5.0.0"
```

### 2. Configure Environment

Ensure your `.env` file has the correct Odoo credentials:

```bash
ODOO_HOST=your-odoo-server.com
ODOO_PORT=8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
```

### 3. Launch the Server

```bash
# Start the Gradio MCP server
uv run python mcp_server_gradio.py

# Or with specific host/port
uv run python mcp_server_gradio.py --server_name 0.0.0.0 --server_port 7860
```

## 🎯 Features

### Web Interface
- **Query Leads**: Visual form to query leads with filters
- **Update Leads**: Update lead assignments and status
- **Count Leads**: Get counts with filtering
- **Query Invoices**: Access invoice data
- **Real-time Results**: JSON output in browser

### MCP Server
- **Automatic Tool Discovery**: Gradio converts all functions to MCP tools
- **Type Hints**: Full type annotation support
- **Documentation**: Auto-generated from docstrings
- **Multiple Endpoints**: Access via HTTP or STDIO

## 🔗 MCP Endpoints

### HTTP SSE Endpoint
```
http://localhost:7860/gradio_api/mcp/sse
```

### Web Interface
```
http://localhost:7860
```

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "odoo-gradio": {
      "command": "uv",
      "args": ["run", "python", "/path/to/mcp_server_gradio.py"],
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

## 🧪 Testing

### Test the Setup
```bash
# Test Odoo connection and MCP endpoints
uv run python test_gradio_mcp.py

# Manual test with curl
curl http://localhost:7860/gradio_api/mcp/sse
```

### Verify MCP Tools

The server automatically exposes these MCP tools:

1. **query_leads** - Query leads with filters
2. **update_leads** - Update lead assignments  
3. **count_leads** - Count leads matching criteria
4. **query_invoices** - Query invoice data

## 🐳 Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.0 /uv /bin/uv

# Copy project
COPY . .

# Install dependencies
RUN uv venv && \
    uv pip install -e . && \
    uv pip install -r requirements-gradio.txt

EXPOSE 7860

CMD ["uv", "run", "python", "mcp_server_gradio.py"]
```

## 🔄 Comparison: Gradio vs Traditional MCP

| Feature | Gradio MCP | Traditional MCP |
|---------|------------|-----------------|
| **Setup** | One line: `mcp_server=True` | Manual tool registration |
| **Interface** | Built-in web UI | CLI only |
| **Type Hints** | Auto-generated | Manual specification |
| **Documentation** | Auto from docstrings | Manual JSON schema |
| **Testing** | Web interface + MCP | CLI testing |
| **Deployment** | Single script | Multiple files |

## 📊 Usage Examples

### Via Web Interface
1. Navigate to `http://localhost:7860`
2. Use the visual forms to query/update data
3. See results in real-time

### Via MCP Client
```python
# Example using MCP client
import requests

# Query leads
response = requests.post("http://localhost:7860/gradio_api/mcp/query_leads", json={
    "date_from": "2024-01-01",
    "status": "new",
    "limit": 50
})
```

### Via Claude Desktop
Simply ask Claude: "Query new leads from January 2024" and it will use the MCP tools automatically.

## 🛠️ Customization

### Adding New Tools
Simply add new methods to the `OdooMCPService` class with proper type hints and docstrings:

```python
def new_tool(self, param1: str, param2: int = 10) -> str:
    """Description of what this tool does."""
    # Your implementation
    return json.dumps(result)
```

### Custom Launch Parameters
```bash
uv run python mcp_server_gradio.py \
  --server_name 0.0.0.0 \
  --server_port 8080 \
  --share  # For public URL
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 7860
   lsof -ti:7860 | xargs kill -9
   ```

2. **Odoo connection failed**
   - Check `.env` file configuration
   - Verify network connectivity
   - Test with `test_gradio_mcp.py`

3. **MCP tools not appearing**
   - Ensure all functions have proper type hints
   - Check docstring format
   - Restart the server

### Debug Mode
```bash
uv run python mcp_server_gradio.py --debug
```

## 🚀 Production Deployment

### Systemd Service
```ini
[Unit]
Description=Odoo Gradio MCP Server
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/app
ExecStart=/usr/local/bin/uv run python mcp_server_gradio.py --server_name 0.0.0.0 --server_port 7860
Environment=PATH=/usr/local/bin
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```