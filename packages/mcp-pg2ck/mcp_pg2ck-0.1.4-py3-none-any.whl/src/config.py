import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    # API Key configuration
    api_key: str = None
    
    # HTTP Server configuration
    http_host: str = None
    http_port: int = None
    http_enabled: bool = False
    
    # PostgreSQL configuration
    postgres_host: str = None
    postgres_port: int = None
    postgres_db: str = None
    postgres_user: str = None
    postgres_password: str = None
    
    # ClickHouse configuration
    clickhouse_host: str = None
    clickhouse_port: int = None
    clickhouse_user: str = None
    clickhouse_password: str = None
    clickhouse_db: str = None
    clickhouse_https: bool = False  # Whether to use HTTPS
    clickhouse_verify: bool = True  # Whether to verify SSL certificates
    
    def __post_init__(self):
        # API Key configuration
        self.api_key = os.getenv("PG2CK_API_KEY", "")
        
        # HTTP Server configuration
        self.http_host = os.getenv("HTTP_HOST", "127.0.0.1")
        self.http_port = int(os.getenv("HTTP_PORT", "8000"))
        self.http_enabled = os.getenv("HTTP_ENABLED", "false").lower() == "true"
        
        # PostgreSQL configuration
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db = os.getenv("POSTGRES_DB", "")
        self.postgres_user = os.getenv("POSTGRES_USER", "")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "")
        
        # ClickHouse configuration
        self.clickhouse_host = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.clickhouse_port = int(os.getenv("CLICKHOUSE_PORT", "8123"))
        self.clickhouse_user = os.getenv("CLICKHOUSE_USER", "default")
        self.clickhouse_password = os.getenv("CLICKHOUSE_PASSWORD", "")
        self.clickhouse_db = os.getenv("CLICKHOUSE_DB", "")
        self.clickhouse_https = os.getenv("CLICKHOUSE_HTTPS", "false").lower() == "true"
        self.clickhouse_verify = os.getenv("CLICKHOUSE_VERIFY", "true").lower() == "true"
        
        # Use postgres_db as clickhouse_db if not explicitly set
        if not self.clickhouse_db:
            self.clickhouse_db = self.postgres_db