#!/usr/bin/env python3
"""
MCP Server for PostgreSQL to ClickHouse synchronization.
Provides tools for database schema synchronization and table management.
"""

import os
import sys
import asyncio
import argparse
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import hashlib
import hmac
import time

# Add src to path for imports
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import local modules
from config import Config
from database import DatabaseManager
from converter import TypeConverter

# Load environment variables
load_dotenv()

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mcp_debug.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Output to stderr for MCP
        logging.FileHandler(log_file, mode='a')  # Also log to file for debugging
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
logger.info("=== MCP SERVER STARTING ===")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment PG2CK_API_KEY: {'SET' if os.getenv('PG2CK_API_KEY') else 'NOT_SET'}")

mcp = FastMCP("mcp-pg2ck")
logger.info("FastMCP server initialized")

# Global database manager and config
db_manager: Optional[DatabaseManager] = None
_config: Optional[Config] = None


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""
    pass


def get_config() -> Config:
    """Get or create configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def validate_api_key(provided_key: str) -> bool:
    """
    Validate the provided API key against the configured one.
    
    Args:
        provided_key: The API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    config = get_config()
    
    logger.info(f"=== API KEY VALIDATION ===")
    logger.info(f"Environment PG2CK_API_KEY raw: '{os.getenv('PG2CK_API_KEY')}'")
    logger.info(f"Configured API key exists: {bool(config.api_key)}")
    logger.info(f"Configured API key value: '{config.api_key[:10]}...'" if config.api_key and len(config.api_key) > 10 else f"Configured API key: '{config.api_key}'")
    logger.info(f"Provided API key: '{provided_key[:10]}...'" if provided_key and len(provided_key) > 10 else f"Provided API key: '{provided_key}'")
    
    # If no API key is configured, allow access (development mode)
    if not config.api_key:
        logger.info("No API key configured - allowing access (development mode)")
        return True
    
    # Use constant-time comparison to prevent timing attacks
    result = hmac.compare_digest(config.api_key, provided_key)
    logger.info(f"API key comparison result: {result}")
    return result


def require_auth(func):
    """
    Decorator to require API key authentication for MCP tools.
    
    The API key should be provided as the first parameter to any tool call.
    """
    def wrapper(*args, **kwargs):
        logger.info(f"=== AUTH DEBUG for {func.__name__} ===")
        logger.info(f"Args received: {len(args)} args, content: {args}")
        logger.info(f"Kwargs received: {list(kwargs.keys())}, content: {kwargs}")
        
        # Extract API key from arguments - handle MCP parameter structure
        api_key = None
        
        # Check if MCP is passing arguments in 'args' kwarg
        if 'args' in kwargs and isinstance(kwargs['args'], (str, list)):
            mcp_args = kwargs['args']
            logger.info(f"Found MCP args structure: {mcp_args}")
            
            if isinstance(mcp_args, str):
                # API key passed directly as string
                api_key = mcp_args
                logger.info(f"API key extracted from MCP args (string): {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API key from MCP args: {api_key}")
            elif isinstance(mcp_args, list) and len(mcp_args) > 0:
                # API key passed as first element in list
                api_key = mcp_args[0]
                logger.info(f"API key extracted from MCP args (list): {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API key from MCP args: {api_key}")
        
        # Fallback to traditional argument handling
        if not api_key:
            if args:
                api_key = args[0]
                args = args[1:]  # Remove API key from arguments
                logger.info(f"API key extracted from args: {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API key from args: {api_key}")
            elif 'api_key' in kwargs:
                api_key = kwargs.pop('api_key')
                logger.info(f"API key extracted from kwargs: {api_key[:10]}..." if api_key and len(api_key) > 10 else f"API key from kwargs: {api_key}")
            else:
                logger.info("No API key found in args or kwargs")
        
        # Validate API key
        logger.info(f"Validating API key...")
        is_valid = validate_api_key(api_key) if api_key else False
        logger.info(f"API key validation result: {is_valid}")
        
        if not api_key or not is_valid:
            logger.error(f"Authentication failed for {func.__name__}: Invalid or missing API key")
            raise AuthenticationError("Invalid or missing API key")
        
        logger.info(f"Authentication successful for {func.__name__}")
        
        # Prepare arguments for the actual function call
        # Remove MCP-specific kwargs before calling the function
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ['args', 'kwargs']}
        
        # Call the original function with clean arguments
        return func(*args, **clean_kwargs)
    
    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


class TableInfo(BaseModel):
    """Model for table information."""
    name: str
    columns: List[Dict[str, Any]]
    row_count: Optional[int] = None


class SyncResult(BaseModel):
    """Model for synchronization results."""
    success: bool
    message: str
    tables_processed: int
    errors: List[str] = []


def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance."""
    global db_manager
    if db_manager is None:
        config = get_config()
        db_manager = DatabaseManager(config)
    return db_manager


@mcp.tool()
def list_postgres_tables() -> List[str]:
    """
    List all tables in the PostgreSQL public schema.
    
    Returns:
        List of table names from the PostgreSQL database.
    """
    try:
        manager = get_db_manager()
        manager.connect_postgres()
        tables = manager.get_postgres_tables()
        return tables
    except Exception as e:
        raise Exception(f"Failed to list PostgreSQL tables: {str(e)}")
    finally:
        if db_manager:
            db_manager.close_connections()


@mcp.tool()
def get_table_schema(table_name: str) -> TableInfo:
    """
    Get the schema information for a specific PostgreSQL table.
    
    Args:
        table_name: Name of the table to inspect
        
    Returns:
        TableInfo object with table name and column details
    """
    try:
        manager = get_db_manager()
        manager.connect_postgres()
        
        # Get table schema
        columns = manager.get_postgres_table_schema(table_name)
        
        # Convert to more readable format
        column_info = []
        for col_name, pg_type, is_nullable in columns:
            ch_type = TypeConverter.map_type(pg_type)
            column_info.append({
                "name": col_name,
                "postgres_type": pg_type,
                "clickhouse_type": ch_type,
                "nullable": is_nullable == 'YES'
            })
        
        return TableInfo(name=table_name, columns=column_info)
    except Exception as e:
        raise Exception(f"Failed to get schema for table {table_name}: {str(e)}")
    finally:
        if db_manager:
            db_manager.close_connections()


@mcp.tool()
def create_clickhouse_table(table_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a single ClickHouse table with PostgreSQL engine for the specified table.
    
    Args:
        table_name: Name of the PostgreSQL table to sync
        database_name: Optional ClickHouse database name (uses config default if not provided)
        
    Returns:
        Dictionary with operation result and details
    """
    try:
        manager = get_db_manager()
        config = manager.config
        
        # Use provided database name or default from config
        target_db = database_name or config.clickhouse_db
        
        # Connect to both databases
        manager.connect_postgres()
        ch_client = manager.connect_clickhouse()
        
        # Get table schema
        columns = manager.get_postgres_table_schema(table_name)
        if not columns:
            raise Exception(f"Table {table_name} not found or has no columns")
        
        # Create database if it doesn't exist
        ch_client.command(f"CREATE DATABASE IF NOT EXISTS `{target_db}`")
        
        # Map PostgreSQL columns to ClickHouse columns
        ch_columns = []
        for col_name, pg_type, is_nullable in columns:
            ch_type = TypeConverter.map_type(pg_type)
            if is_nullable == 'YES' and not ch_type.startswith('Nullable'):
                ch_type = f'Nullable({ch_type})'
            ch_columns.append(f"`{col_name}` {ch_type}")
        
        # Create the table with explicit columns and PostgreSQL engine
        columns_definition = ', '.join(ch_columns)
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{target_db}`.`{table_name}` (
                {columns_definition}
            )
            ENGINE = PostgreSQL(
                '{config.postgres_host}:{config.postgres_port}', 
                '{config.postgres_db}', 
                '{table_name}', 
                '{config.postgres_user}', 
                '{config.postgres_password}'
            )
        """
        
        ch_client.command(create_table_sql)
        
        return {
            "success": True,
            "message": f"Successfully created table {table_name} in ClickHouse database {target_db}",
            "table_name": table_name,
            "database": target_db,
            "columns_mapped": len(ch_columns)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create ClickHouse table {table_name}: {str(e)}",
            "table_name": table_name,
            "database": database_name or "default"
        }
    finally:
        if db_manager:
            db_manager.close_connections()


@mcp.tool()
def sync_all_tables(database_name: Optional[str] = None) -> SyncResult:
    """
    Synchronize all PostgreSQL tables to ClickHouse with PostgreSQL engine.
    
    Args:
        database_name: Optional ClickHouse database name (uses config default if not provided)
        
    Returns:
        SyncResult with operation summary and any errors
    """
    try:
        manager = get_db_manager()
        config = manager.config
        
        # Use provided database name or default from config
        target_db = database_name or config.clickhouse_db
        
        # Connect to both databases
        manager.connect_postgres()
        ch_client = manager.connect_clickhouse()
        
        # Get all tables from PostgreSQL
        tables = manager.get_postgres_tables()
        
        if not tables:
            return SyncResult(
                success=True,
                message="No tables found in PostgreSQL public schema",
                tables_processed=0
            )
        
        errors = []
        successful_tables = 0
        
        # Create database if it doesn't exist
        ch_client.command(f"CREATE DATABASE IF NOT EXISTS `{target_db}`")
        
        # Process each table
        for table_name in tables:
            try:
                # Get table schema
                columns = manager.get_postgres_table_schema(table_name)
                
                # Map PostgreSQL columns to ClickHouse columns
                ch_columns = []
                for col_name, pg_type, is_nullable in columns:
                    ch_type = TypeConverter.map_type(pg_type)
                    if is_nullable == 'YES' and not ch_type.startswith('Nullable'):
                        ch_type = f'Nullable({ch_type})'
                    ch_columns.append(f"`{col_name}` {ch_type}")
                
                # Create the table with explicit columns and PostgreSQL engine
                columns_definition = ', '.join(ch_columns)
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS `{target_db}`.`{table_name}` (
                        {columns_definition}
                    )
                    ENGINE = PostgreSQL(
                        '{config.postgres_host}:{config.postgres_port}', 
                        '{config.postgres_db}', 
                        '{table_name}', 
                        '{config.postgres_user}', 
                        '{config.postgres_password}'
                    )
                """
                
                ch_client.command(create_table_sql)
                successful_tables += 1
                
            except Exception as e:
                errors.append(f"Failed to sync table {table_name}: {str(e)}")
        
        return SyncResult(
            success=len(errors) == 0,
            message=f"Processed {len(tables)} tables. {successful_tables} successful, {len(errors)} failed.",
            tables_processed=len(tables),
            errors=errors
        )
        
    except Exception as e:
        return SyncResult(
            success=False,
            message=f"Failed to sync tables: {str(e)}",
            tables_processed=0,
            errors=[str(e)]
        )
    finally:
        if db_manager:
            db_manager.close_connections()


@mcp.tool()
def test_connections() -> Dict[str, Any]:
    """
    Test connections to both PostgreSQL and ClickHouse databases.
    
    Returns:
        Dictionary with connection test results for both databases
    """
    # Debug logging for environment variables
    logger.info("=== test_connections DEBUG INFO ===")
    logger.info("Running in stdio/development mode - no API key required")
    
    # Log environment variables (masked for security)
    env_vars = {
        "PG2CK_API_KEY": os.getenv("PG2CK_API_KEY", "NOT_SET"),
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "NOT_SET"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "NOT_SET"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "NOT_SET"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "NOT_SET"),
        "POSTGRES_PASSWORD": "***" if os.getenv("POSTGRES_PASSWORD") else "NOT_SET",
        "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_HOST", "NOT_SET"),
        "CLICKHOUSE_PORT": os.getenv("CLICKHOUSE_PORT", "NOT_SET"),
        "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER", "NOT_SET"),
        "CLICKHOUSE_PASSWORD": "***" if os.getenv("CLICKHOUSE_PASSWORD") else "NOT_SET",
        "CLICKHOUSE_DB": os.getenv("CLICKHOUSE_DB", "NOT_SET"),
    }
    
    logger.info("Environment variables:")
    for key, value in env_vars.items():
        logger.info(f"  {key}: {value}")
    
    result = {
        "postgres": {"connected": False, "error": None},
        "clickhouse": {"connected": False, "error": None},
        "debug_info": {
            "mode": "stdio/development",
            "auth_required": False,
            "env_vars": env_vars,
            "log_file_location": log_file
        }
    }
    
    try:
        manager = get_db_manager()
        logger.info(f"Database manager config - PG: {manager.config.postgres_host}:{manager.config.postgres_port}/{manager.config.postgres_db}")
        logger.info(f"Database manager config - CH: {manager.config.clickhouse_host}:{manager.config.clickhouse_port}/{manager.config.clickhouse_db}")
        
        # Test PostgreSQL connection
        try:
            logger.info("Testing PostgreSQL connection...")
            manager.connect_postgres()
            result["postgres"]["connected"] = True
            logger.info("PostgreSQL connection successful!")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {str(e)}")
            result["postgres"]["error"] = str(e)
        
        # Test ClickHouse connection
        try:
            logger.info("Testing ClickHouse connection...")
            manager.connect_clickhouse()
            result["clickhouse"]["connected"] = True
            logger.info("ClickHouse connection successful!")
        except Exception as e:
            logger.error(f"ClickHouse connection failed: {str(e)}")
            result["clickhouse"]["error"] = str(e)
            
    except Exception as e:
        logger.error(f"General error in test_connections: {str(e)}")
        result["general_error"] = str(e)
    finally:
        if db_manager:
            db_manager.close_connections()
    
    logger.info("=== test_connections DEBUG INFO END ===")
    return result


@mcp.resource("schema://postgres/{table_name}")
def get_postgres_table_resource(table_name: str) -> str:
    """
    Resource to get PostgreSQL table schema as a formatted string.
    Note: Resources don't support API key authentication in the same way as tools.
    Ensure proper network-level security for resource access.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Formatted string representation of the table schema
    """
    try:
        # For resources, we'll check if API key is configured but not enforce it
        # since the MCP resource protocol doesn't support authentication parameters
        config = get_config()
        if config.api_key:
            # Log access attempt (in production, you might want proper logging)
            pass
            
        # For resources, bypass API key check by calling the underlying function directly
        manager = get_db_manager()
        manager.connect_postgres()
        
        # Get table schema
        columns = manager.get_postgres_table_schema(table_name)
        
        # Convert to more readable format
        column_info = []
        for col_name, pg_type, is_nullable in columns:
            ch_type = TypeConverter.map_type(pg_type)
            column_info.append({
                "name": col_name,
                "postgres_type": pg_type,
                "clickhouse_type": ch_type,
                "nullable": is_nullable == 'YES'
            })
        
        table_info = TableInfo(name=table_name, columns=column_info)
        
        schema_lines = [f"Table: {table_info.name}"]
        schema_lines.append("Columns:")
        
        for col in table_info.columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            schema_lines.append(f"  - {col['name']}: {col['postgres_type']} -> {col['clickhouse_type']} ({nullable})")
        
        return "\n".join(schema_lines)
        
    except Exception as e:
        return f"Error retrieving schema for {table_name}: {str(e)}"
    finally:
        if db_manager:
            db_manager.close_connections()


async def run_dual_server():
    """Run both MCP stdio server and HTTP server concurrently."""
    config = get_config()
    
    tasks = []
    
    # Always run MCP stdio server
    stdio_task = asyncio.create_task(asyncio.to_thread(mcp.run))
    tasks.append(stdio_task)
    print("Started MCP stdio server")
    
    # Run HTTP server if enabled
    if config.http_enabled:
        from http_server import run_http_server
        http_task = asyncio.create_task(
            run_http_server(config.http_host, config.http_port)
        )
        tasks.append(http_task)
        print(f"Started HTTP server on {config.http_host}:{config.http_port}")
    
    # Wait for all tasks
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for task in tasks:
            task.cancel()


def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(description="mcp-pg2ck MCP Server")
    parser.add_argument(
        "--http", 
        action="store_true", 
        help="Enable HTTP server alongside MCP stdio"
    )
    parser.add_argument(
        "--http-only", 
        action="store_true", 
        help="Run only HTTP server (no MCP stdio)"
    )
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="HTTP server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="HTTP server port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables from command line args
    if args.http or args.http_only:
        os.environ["HTTP_ENABLED"] = "true"
        os.environ["HTTP_HOST"] = args.host
        os.environ["HTTP_PORT"] = str(args.port)
    
    if args.http_only:
        # Run only HTTP server
        from http_server import app
        import uvicorn
        print(f"Starting HTTP-only server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.http:
        # Run both servers
        print("Starting dual-mode server (MCP stdio + HTTP)")
        asyncio.run(run_dual_server())
    else:
        # Run only MCP stdio server (default)
        print("Starting MCP stdio server")
        mcp.run()


if __name__ == "__main__":
    main()