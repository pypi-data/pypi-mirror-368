import psycopg2
import clickhouse_connect
import os
import sys

# Add src to path for imports
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import modules
from config import Config


class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.pg_conn = None
        self.ch_client = None

    def connect_postgres(self):
        """Establish connection to PostgreSQL."""
        self.pg_conn = psycopg2.connect(
            host=self.config.postgres_host,
            port=self.config.postgres_port,
            database=self.config.postgres_db,
            user=self.config.postgres_user,
            password=self.config.postgres_password,
        )
        return self.pg_conn

    def connect_clickhouse(self):
        """Establish connection to ClickHouse using HTTP interface."""
        self.ch_client = clickhouse_connect.get_client(
            host=self.config.clickhouse_host,
            port=self.config.clickhouse_port,
            username=self.config.clickhouse_user,
            password=self.config.clickhouse_password,
            secure=self.config.clickhouse_https,
            verify=self.config.clickhouse_verify,
        )
        return self.ch_client

    def get_postgres_tables(self):
        """Get all table names from the public schema in PostgreSQL."""
        if not self.pg_conn:
            raise Exception("PostgreSQL connection not established")
            
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            return [row[0] for row in cur.fetchall()]

    def get_postgres_table_schema(self, table_name):
        """Get the schema (column names and types) for a PostgreSQL table."""
        if not self.pg_conn:
            raise Exception("PostgreSQL connection not established")
            
        with self.pg_conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            return cur.fetchall()

    def close_connections(self):
        """Close database connections."""
        if self.pg_conn:
            self.pg_conn.close()
        if self.ch_client:
            self.ch_client.close()