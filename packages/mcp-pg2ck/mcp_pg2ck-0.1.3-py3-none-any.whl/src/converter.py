class TypeConverter:
    """Handles conversion between PostgreSQL and ClickHouse data types."""
    
    # Mapping from PostgreSQL to ClickHouse types
    TYPE_MAPPING = {
        'integer': 'Int32',
        'bigint': 'Int64',
        'smallint': 'Int16',
        'serial': 'Int32',
        'bigserial': 'Int64',
        'real': 'Float32',
        'double precision': 'Float64',
        'numeric': 'Decimal(10,2)',
        'boolean': 'UInt8',
        'character varying': 'String',
        'varchar': 'String',
        'text': 'String',
        'date': 'Date',
        'timestamp without time zone': 'DateTime',
        'timestamp with time zone': 'DateTime',
        'time without time zone': 'Time',
        'uuid': 'UUID',
        'bytea': 'String',
    }
    
    @classmethod
    def map_type(cls, pg_type):
        """Map PostgreSQL data type to ClickHouse data type."""
        # Handle parameterized types like character varying(n)
        if pg_type.startswith('character varying'):
            return 'String'
        elif pg_type.startswith('timestamp'):
            return 'DateTime'
        elif pg_type.startswith('numeric'):
            # Could be more sophisticated to parse precision and scale
            return 'Decimal(10,2)'
        
        return cls.TYPE_MAPPING.get(pg_type, 'String')  # Default to String for unknown types