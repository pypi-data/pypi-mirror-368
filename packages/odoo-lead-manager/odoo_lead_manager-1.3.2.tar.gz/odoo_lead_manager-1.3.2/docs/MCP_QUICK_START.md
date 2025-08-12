# MCP Quick Start

## 30-Second Setup

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup project
uv venv && uv pip install -e . && uv pip install -r requirements.txt

# 3. Configure
export ODOO_HOST=your-server.com
export ODOO_DB=your-db
export ODOO_USERNAME=your-user
export ODOO_PASSWORD=your-pass

# 4. Run
uv run python mcp_server.py
```

## One-Liner Commands

**STDIO Server:** `uv run python mcp_server.py`

**HTTP Server:** `uv run python mcp_server_http.py`

**Docker:** `docker run -e ODOO_HOST=... -p 8001:8001 odoo-mcp`

**Test:** `uv run python -c "from odoo_lead_manager.client import OdooClient; OdooClient().connect(); print('✅ Working')"`