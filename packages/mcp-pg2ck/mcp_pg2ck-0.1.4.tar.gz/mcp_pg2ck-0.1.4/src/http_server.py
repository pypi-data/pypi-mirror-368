#!/usr/bin/env python3
"""
HTTP streaming interface for the pg2ck MCP server.
Provides RESTful HTTP endpoints with Server-Sent Events (SSE) support.
"""

import os
import sys
import json
import asyncio
import hmac
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Header, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Add src to path for imports
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import MCP server components
from mcp_server import (
    get_config, list_postgres_tables, get_table_schema, create_clickhouse_table,
    sync_all_tables, test_connections, TableInfo, SyncResult
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="mcp-pg2ck HTTP Server",
    description="HTTP streaming interface for PostgreSQL to ClickHouse synchronization",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""
    pass


def validate_api_key(provided_key: str) -> bool:
    """
    Validate the provided API key against the configured one.
    
    Args:
        provided_key: The API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    config = get_config()
    
    # If no API key is configured, allow access (development mode)
    if not config.api_key:
        return True
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(config.api_key, provided_key)


class HTTPRequest(BaseModel):
    """Base model for HTTP API requests."""
    api_key: str


class TableSchemaRequest(HTTPRequest):
    """Request model for table schema endpoint."""
    table_name: str


class CreateTableRequest(HTTPRequest):
    """Request model for create table endpoint."""
    table_name: str
    database_name: Optional[str] = None


class SyncTablesRequest(HTTPRequest):
    """Request model for sync tables endpoint."""
    database_name: Optional[str] = None


class StreamEvent(BaseModel):
    """Model for Server-Sent Events."""
    event: str
    data: Dict[str, Any]
    id: Optional[str] = None


def get_api_key_from_request(
    header_key: Optional[str] = None,
    query_key: Optional[str] = None,
    body_key: Optional[str] = None
) -> Optional[str]:
    """Extract API key from various sources (header, query, body)."""
    return header_key or query_key or body_key


def validate_request_auth(api_key: Optional[str]) -> bool:
    """Validate API key from HTTP request."""
    # If no API key is configured in environment, allow access (development mode)
    config = get_config()
    if not config.api_key:
        return True
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if not validate_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


def create_sse_response(data: Dict[str, Any], event: str = "data") -> str:
    """Create a Server-Sent Event formatted response."""
    event_data = {
        "event": event,
        "data": json.dumps(data)
    }
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "mcp-pg2ck HTTP Server",
        "version": "0.1.0",
        "description": "HTTP streaming interface for PostgreSQL to ClickHouse synchronization",
        "authentication": {
            "methods": [
                "HTTP Header: X-API-Key",
                "Query Parameter: api_key",
                "Request Body: api_key"
            ],
            "development_mode": "No API key required when PG2CK_API_KEY is not configured"
        },
        "endpoints": {
            "tables": {
                "GET": "/api/v1/tables?api_key=YOUR_KEY",
                "POST": "/api/v1/tables"
            },
            "schema": {
                "GET": "/api/v1/schema?table_name=TABLE&api_key=YOUR_KEY",
                "POST": "/api/v1/schema"
            },
            "create": {
                "GET": "/api/v1/create?table_name=TABLE&api_key=YOUR_KEY",
                "POST": "/api/v1/create"
            },
            "sync": {
                "GET": "/api/v1/sync?api_key=YOUR_KEY",
                "POST": "/api/v1/sync"
            },
            "test": {
                "GET": "/api/v1/test?api_key=YOUR_KEY",
                "POST": "/api/v1/test"
            },
            "streaming": {
                "tables": "/api/v1/stream/tables?api_key=YOUR_KEY",
                "sync": "/api/v1/stream/sync?api_key=YOUR_KEY"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-pg2ck"}


# REST API Endpoints

@app.post("/api/v1/tables", response_model=List[str])
async def get_tables(
    request: HTTPRequest,
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Get list of PostgreSQL tables."""
    api_key = get_api_key_from_request(api_key_header, api_key_query, request.api_key)
    validate_request_auth(api_key)
    
    try:
        tables = list_postgres_tables()
        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tables", response_model=List[str])
async def get_tables_get(
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Get list of PostgreSQL tables (GET method)."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    try:
        tables = list_postgres_tables()
        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/schema", response_model=TableInfo)
async def get_schema(
    request: TableSchemaRequest,
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Get table schema information."""
    api_key = get_api_key_from_request(api_key_header, api_key_query, request.api_key)
    validate_request_auth(api_key)
    
    try:
        schema = get_table_schema(request.table_name)
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/schema", response_model=TableInfo)
async def get_schema_get(
    table_name: str = Query(..., description="Name of the table"),
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Get table schema information (GET method)."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    try:
        schema = get_table_schema(table_name)
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/create")
async def create_table(
    request: CreateTableRequest,
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Create a single ClickHouse table."""
    api_key = get_api_key_from_request(api_key_header, api_key_query, request.api_key)
    validate_request_auth(api_key)
    
    try:
        result = create_clickhouse_table(request.table_name, request.database_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/create")
async def create_table_get(
    table_name: str = Query(..., description="Name of the table to create"),
    database_name: Optional[str] = Query(None, description="ClickHouse database name"),
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Create a single ClickHouse table (GET method)."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    try:
        result = create_clickhouse_table(table_name, database_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sync", response_model=SyncResult)
async def sync_tables(
    request: SyncTablesRequest,
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Synchronize all PostgreSQL tables to ClickHouse."""
    api_key = get_api_key_from_request(api_key_header, api_key_query, request.api_key)
    validate_request_auth(api_key)
    
    try:
        result = sync_all_tables(request.database_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sync", response_model=SyncResult)
async def sync_tables_get(
    database_name: Optional[str] = Query(None, description="ClickHouse database name"),
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Synchronize all PostgreSQL tables to ClickHouse (GET method)."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    try:
        result = sync_all_tables(database_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/test")
async def test_connections_endpoint(
    request: HTTPRequest,
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Test database connections."""
    api_key = get_api_key_from_request(api_key_header, api_key_query, request.api_key)
    validate_request_auth(api_key)
    
    try:
        result = test_connections()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/test")
async def test_connections_get(
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Test database connections (GET method)."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    try:
        result = test_connections()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Streaming Endpoints (Server-Sent Events)

async def stream_tables():
    """Stream table list with SSE."""
    try:
        yield create_sse_response({"status": "started"}, "start")
        
        tables = list_postgres_tables()
        
        yield create_sse_response({
            "tables": tables,
            "count": len(tables)
        }, "tables")
        
        yield create_sse_response({"status": "completed"}, "complete")
        
    except Exception as e:
        yield create_sse_response({
            "error": str(e),
            "status": "error"
        }, "error")


async def stream_sync(database_name: Optional[str] = None):
    """Stream sync operation with real-time progress."""
    try:
        yield create_sse_response({"status": "started"}, "start")
        
        # Get table list first
        tables = list_postgres_tables()
        total_tables = len(tables)
        
        yield create_sse_response({
            "total_tables": total_tables,
            "tables": tables
        }, "tables")
        
        # Process each table individually and stream progress
        successful_tables = 0
        errors = []
        
        for i, table_name in enumerate(tables):
            try:
                yield create_sse_response({
                    "current_table": table_name,
                    "progress": i + 1,
                    "total": total_tables,
                    "percentage": round(((i + 1) / total_tables) * 100, 2)
                }, "progress")
                
                # Create individual table
                result = create_clickhouse_table(table_name, database_name)
                
                if result.get("success", False):
                    successful_tables += 1
                    yield create_sse_response({
                        "table": table_name,
                        "status": "success",
                        "message": result.get("message", "")
                    }, "table_success")
                else:
                    error_msg = result.get("message", f"Failed to create table {table_name}")
                    errors.append(error_msg)
                    yield create_sse_response({
                        "table": table_name,
                        "status": "error",
                        "error": error_msg
                    }, "table_error")
                
            except Exception as e:
                error_msg = f"Failed to sync table {table_name}: {str(e)}"
                errors.append(error_msg)
                yield create_sse_response({
                    "table": table_name,
                    "status": "error",
                    "error": error_msg
                }, "table_error")
        
        # Final result
        final_result = {
            "success": len(errors) == 0,
            "message": f"Processed {total_tables} tables. {successful_tables} successful, {len(errors)} failed.",
            "tables_processed": total_tables,
            "successful_tables": successful_tables,
            "errors": errors
        }
        
        yield create_sse_response(final_result, "complete")
        
    except Exception as e:
        yield create_sse_response({
            "error": str(e),
            "status": "error"
        }, "error")


@app.get("/api/v1/stream/tables")
async def stream_tables_endpoint(
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Stream table list endpoint."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    return StreamingResponse(
        stream_tables(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "X-API-Key"
        }
    )


@app.get("/api/v1/stream/sync")
async def stream_sync_endpoint(
    database_name: Optional[str] = Query(None, description="ClickHouse database name"),
    api_key_query: Optional[str] = Query(None, alias="api_key"),
    api_key_header: Optional[str] = Header(None, alias="X-API-Key")
):
    """Stream sync operation endpoint."""
    api_key = get_api_key_from_request(api_key_header, api_key_query)
    validate_request_auth(api_key)
    
    return StreamingResponse(
        stream_sync(database_name),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "X-API-Key"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return Response(
        content=json.dumps({
            "error": exc.detail,
            "status_code": exc.status_code
        }),
        status_code=exc.status_code,
        media_type="application/json"
    )


def create_http_server(host: str = "127.0.0.1", port: int = 8000) -> uvicorn.Server:
    """Create and configure the HTTP server."""
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    return uvicorn.Server(config)


async def run_http_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the HTTP server."""
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    await server.serve()


def main():
    """Main entry point for the HTTP server."""
    # Get configuration from environment
    host = os.getenv("HTTP_HOST", "127.0.0.1")
    port = int(os.getenv("HTTP_PORT", "8000"))
    
    print(f"Starting mcp-pg2ck HTTP server on {host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()