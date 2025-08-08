import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from converter import TypeConverter
from config import Config


class TestTypeConverter(unittest.TestCase):
    def test_map_type_basic(self):
        """Test basic type mapping."""
        self.assertEqual(TypeConverter.map_type('integer'), 'Int32')
        self.assertEqual(TypeConverter.map_type('bigint'), 'Int64')
        self.assertEqual(TypeConverter.map_type('boolean'), 'UInt8')
        self.assertEqual(TypeConverter.map_type('text'), 'String')
        self.assertEqual(TypeConverter.map_type('date'), 'Date')

    def test_map_type_parameterized(self):
        """Test parameterized type mapping."""
        self.assertEqual(TypeConverter.map_type('character varying'), 'String')
        self.assertEqual(TypeConverter.map_type('character varying(255)'), 'String')
        self.assertEqual(TypeConverter.map_type('timestamp without time zone'), 'DateTime')
        self.assertEqual(TypeConverter.map_type('timestamp with time zone'), 'DateTime')

    def test_map_type_unknown(self):
        """Test mapping of unknown types."""
        self.assertEqual(TypeConverter.map_type('unknown_type'), 'String')


class TestConfig(unittest.TestCase):
    @patch.dict(os.environ, {
        "POSTGRES_HOST": "pg_host",
        "POSTGRES_PORT": "5433",
        "POSTGRES_DB": "pg_db",
        "POSTGRES_USER": "pg_user",
        "POSTGRES_PASSWORD": "pg_pass",
        "CLICKHOUSE_HOST": "ch_host",
        "CLICKHOUSE_PORT": "9001",
        "CLICKHOUSE_USER": "ch_user",
        "CLICKHOUSE_PASSWORD": "ch_pass",
        "CLICKHOUSE_DB": "ch_db"
    })
    def test_config_from_env(self):
        """Test config loading from environment variables."""
        config = Config()
        self.assertEqual(config.postgres_host, "pg_host")
        self.assertEqual(config.postgres_port, 5433)
        self.assertEqual(config.postgres_db, "pg_db")
        self.assertEqual(config.postgres_user, "pg_user")
        self.assertEqual(config.postgres_password, "pg_pass")
        self.assertEqual(config.clickhouse_host, "ch_host")
        self.assertEqual(config.clickhouse_port, 9001)
        self.assertEqual(config.clickhouse_user, "ch_user")
        self.assertEqual(config.clickhouse_password, "ch_pass")
        self.assertEqual(config.clickhouse_db, "ch_db")

    @patch.dict(os.environ, {
        "POSTGRES_DB": "test_db"
    })
    def test_config_default_clickhouse_db(self):
        """Test that clickhouse_db defaults to postgres_db if not set."""
        config = Config()
        self.assertEqual(config.clickhouse_db, "test_db")


if __name__ == '__main__':
    unittest.main()