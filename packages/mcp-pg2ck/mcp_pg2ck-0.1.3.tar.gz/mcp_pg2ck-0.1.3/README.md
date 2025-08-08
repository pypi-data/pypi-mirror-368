# mcp-pg2ck

An MCP (Model Context Protocol) server that provides secure, authenticated tools for synchronizing PostgreSQL tables to ClickHouse databases.

## Overview

This tool reads all tables from the `public` schema of a PostgreSQL database and creates corresponding tables in a ClickHouse database with the same name. The tables use the PostgreSQL engine, allowing ClickHouse to directly read data from PostgreSQL.

## Setup

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables by copying `.env.example` to `.env` and updating the values:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

## Usage

### MCP Server (Stdio)
```bash
# Default MCP stdio server
python mcp_server.py
# or
mcp-pg2ck
```

### HTTP Streaming Server
```bash
# HTTP-only server
python http_server.py
# or
pg2ck-http

# HTTP server with custom host/port
python mcp_server.py --http-only --host 0.0.0.0 --port 9000
```

### Dual Mode (MCP + HTTP)
```bash
# Run both MCP stdio and HTTP server
python mcp_server.py --http

# Custom HTTP configuration
python mcp_server.py --http --host 0.0.0.0 --port 9000
```

### Available APIs

#### MCP Tools (All require API key authentication)
- `list_postgres_tables(api_key)`: List all tables in PostgreSQL public schema
- `get_table_schema(api_key, table_name)`: Get detailed schema information for a specific table
- `create_clickhouse_table(api_key, table_name, database_name?)`: Create a single ClickHouse table with PostgreSQL engine
- `sync_all_tables(api_key, database_name?)`: Synchronize all PostgreSQL tables to ClickHouse
- `test_connections(api_key)`: Test connectivity to both databases

#### HTTP REST Endpoints
- `POST /api/v1/tables`: List PostgreSQL tables
- `POST /api/v1/schema`: Get table schema information  
- `POST /api/v1/create`: Create a single ClickHouse table
- `POST /api/v1/sync`: Synchronize all tables
- `POST /api/v1/test`: Test database connections

#### HTTP Streaming Endpoints (Server-Sent Events)
- `GET /api/v1/stream/tables`: Stream table list
- `GET /api/v1/stream/sync`: Stream sync operation with real-time progress

All HTTP endpoints require API key in `X-API-Key` header or request body.

### Authentication

All MCP tools require an API key for authentication. Set the `PG2CK_API_KEY` environment variable:

```bash
export PG2CK_API_KEY="your-secure-api-key-here"
```

If no API key is configured, the server runs in development mode (not recommended for production).

## Environment Variables

The following environment variables can be set in your `.env` file:

### Authentication
- `PG2CK_API_KEY`: API key for authenticating MCP tool calls (required for production)

### HTTP Server Configuration
- `HTTP_HOST`: HTTP server host (default: 127.0.0.1)
- `HTTP_PORT`: HTTP server port (default: 8000)  
- `HTTP_ENABLED`: Enable HTTP server (default: false)

### PostgreSQL Configuration
- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password

### ClickHouse Configuration
- `CLICKHOUSE_HOST`: ClickHouse host (default: localhost)
- `CLICKHOUSE_PORT`: ClickHouse port (default: 8123)
- `CLICKHOUSE_USER`: ClickHouse username (default: default)
- `CLICKHOUSE_PASSWORD`: ClickHouse password
- `CLICKHOUSE_HTTPS`: Whether to use HTTPS (default: true)
- `CLICKHOUSE_VERIFY`: Whether to verify SSL certificates (default: true)
- `CLICKHOUSE_DB`: ClickHouse database name (defaults to POSTGRES_DB if not set)

## How It Works

Instead of copying data, this tool creates tables in ClickHouse that use the PostgreSQL engine. This allows ClickHouse to directly query the PostgreSQL database, providing:

1. Real-time access to PostgreSQL data
2. No data duplication
3. Automatic schema synchronization

The created tables have explicit column definitions mapped from PostgreSQL types to ClickHouse types for better performance and type safety.

## MCP Integration

This server can be used with any MCP-compatible client. To integrate with Claude Desktop or other MCP clients, add the server configuration to your MCP settings.

#### MCP Client Configuration:
```json
{
  "mcpServers": {
    "pg2ck": {
      "command": "python",
      "args": ["/path/to/pg2ck/mcp_server.py"],
      "env": {
        "PG2CK_API_KEY": "your-secure-api-key",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_DB": "your_db",
        "POSTGRES_USER": "your_user",
        "POSTGRES_PASSWORD": "your_password",
        "CLICKHOUSE_HOST": "localhost",
        "CLICKHOUSE_USER": "default"
      }
    }
  }
}
```

#### HTTP Client Example:
```bash
# List tables using curl
curl -X POST http://localhost:8000/api/v1/tables \
  -H "X-API-Key: your-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-secure-api-key"}'

# Stream sync operation
curl -H "X-API-Key: your-secure-api-key" \
  http://localhost:8000/api/v1/stream/sync
```

#### HTTP Documentation:
When running the HTTP server, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Security Notes

- Always set a strong `PG2CK_API_KEY` in production environments
- The API key is required as the first parameter for all MCP tool calls
- HTTP endpoints require API key in `X-API-Key` header or request body
- MCP resources (schema endpoints) have limited authentication - use network-level security
- Never expose database credentials in client configurations
- Configure CORS appropriately for production HTTP deployments

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Development

To install the package in development mode:

```bash
pip install -e .
```