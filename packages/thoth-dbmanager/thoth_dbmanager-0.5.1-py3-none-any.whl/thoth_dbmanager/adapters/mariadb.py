"""
MariaDB adapter for Thoth SQL Database Manager.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbAdapter


class MariaDBAdapter(DbAdapter):
    """MariaDB database adapter."""
    
    def __init__(self, connection_string: str, **kwargs: Any) -> None:
        """
        Initialize MariaDB adapter.
        
        Args:
            connection_string: MariaDB connection string
            **kwargs: Additional connection parameters
        """
        self.connection_string = connection_string
        self.engine = None
        self.connection_params = kwargs
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                **self.connection_params
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MariaDB: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self.engine:
            self.connect()
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            raise RuntimeError(f"MariaDB query failed: {e}")
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an update query and return affected row count."""
        if not self.engine:
            self.connect()
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except SQLAlchemyError as e:
            raise RuntimeError(f"MariaDB update failed: {e}")
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database."""
        query = "SHOW TABLES"
        result = self.execute_query(query)
        return [list(row.values())[0] for row in result]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        query = f"DESCRIBE {table_name}"
        columns = self.execute_query(query)
        
        schema = {
            'table_name': table_name,
            'columns': []
        }
        
        for col in columns:
            schema['columns'].append({
                'name': col['Field'],
                'type': col['Type'],
                'nullable': col['Null'] == 'YES',
                'default': col['Default'],
                'primary_key': col['Key'] == 'PRI'
            })
        
        return schema
    
    def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        query = f"SHOW INDEX FROM {table_name}"
        indexes = self.execute_query(query)
        
        result = []
        for idx in indexes:
            result.append({
                'name': idx['Key_name'],
                'column': idx['Column_name'],
                'unique': not idx['Non_unique'],
                'type': idx['Index_type']
            })
        
        return result
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        query = f"""
        SELECT 
            CONSTRAINT_NAME as name,
            COLUMN_NAME as column_name,
            REFERENCED_TABLE_NAME as referenced_table,
            REFERENCED_COLUMN_NAME as referenced_column
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = '{table_name}' 
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        
        return self.execute_query(query)
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create a new table with the given schema."""
        columns = []
        for col in schema.get('columns', []):
            col_def = f"{col['name']} {col['type']}"
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if col.get('default') is not None:
                col_def += f" DEFAULT {col['default']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            columns.append(col_def)
        
        query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        self.execute_update(query)
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_update(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = f"""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = '{table_name}'
        """
        result = self.execute_query(query)
        return result[0]['count'] > 0
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'type': 'mariadb',
            'connection_string': self.connection_string,
            'connected': self.engine is not None
        }
