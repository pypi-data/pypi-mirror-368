"""
MariaDB plugin for Thoth SQL Database Manager.
Unified implementation combining plugin architecture with full database functionality.
"""

import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin
from ..documents import TableDocument, ColumnDocument, ForeignKeyDocument, SchemaDocument, IndexDocument

logger = logging.getLogger(__name__)


class MariaDBAdapter(DbAdapter):
    """MariaDB database adapter with full functionality."""
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.host = connection_params.get('host')
        self.port = connection_params.get('port', 3306)
        self.dbname = connection_params.get('database') or connection_params.get('dbname')
        self.user = connection_params.get('user') or connection_params.get('username')
        self.password = connection_params.get('password')
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            # Try different connection methods for MariaDB
            connection_methods = [
                # Use MySQL driver (MariaDB is MySQL-compatible)
                f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}",
                # Use MySQL connector with explicit TCP
                f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}",
                # Use MariaDB connector with TCP parameters
                f"mariadb+mariadbconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?unix_socket=",
            ]

            last_error = None
            for connection_string in connection_methods:
                try:
                    self.engine = create_engine(connection_string, pool_pre_ping=True)
                    # Test the connection
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    self.connection = self.engine
                    self._initialized = True
                    logger.info(f"MariaDB connected using: {connection_string.split('://')[0]}")
                    return
                except Exception as e:
                    last_error = e
                    logger.debug(f"MariaDB connection failed with {connection_string.split('://')[0]}: {e}")
                    if self.engine:
                        self.engine.dispose()
                        self.engine = None
                    continue

            # If all methods fail, raise the last error
            raise ConnectionError(f"Failed to connect to MariaDB: {last_error}")

        except Exception as e:
            raise ConnectionError(f"Failed to connect to MariaDB: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute a query and return results."""
        if not self.engine:
            self.connect()

        with self.engine.connect() as connection:
            try:
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))

                # Check if this is a query that returns rows (SELECT, SHOW, etc.)
                query_upper = query.strip().upper()
                if query_upper.startswith(('SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN', 'WITH')):
                    if fetch == "all":
                        return [row._asdict() for row in result.fetchall()]
                    elif fetch == "one":
                        row = result.fetchone()
                        return row._asdict() if row else None
                    elif isinstance(fetch, int) and fetch > 0:
                        return [row._asdict() for row in result.fetchmany(fetch)]
                    else:
                        return [row._asdict() for row in result.fetchall()]
                else:
                    # For DDL/DML queries (CREATE, INSERT, UPDATE, DELETE), return rowcount
                    connection.commit()
                    return result.rowcount
            except SQLAlchemyError as e:
                logger.error(f"Error executing SQL: {str(e)}")
                raise e
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Return tables as document objects."""
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        tables = []
        
        for table_name in table_names:
            try:
                table_comment = inspector.get_table_comment(table_name).get('text', '')
            except SQLAlchemyError:
                table_comment = ''
            
            tables.append(TableDocument(
                table_name=table_name,
                schema_name="",  # MariaDB doesn't have explicit schemas like PostgreSQL
                comment=table_comment or "",
                row_count=None  # Could be populated if needed
            ))
        
        return tables
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Return columns as document objects."""
        inspector = inspect(self.engine)
        columns_metadata = inspector.get_columns(table_name)
        pk_columns = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
        
        columns = []
        for col_meta in columns_metadata:
            columns.append(ColumnDocument(
                table_name=table_name,
                column_name=col_meta['name'],
                data_type=str(col_meta['type']),
                is_nullable=col_meta.get('nullable', True),
                is_pk=col_meta['name'] in pk_columns,
                comment=col_meta.get('comment', '') or ""
            ))
        
        return columns
    
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """Return foreign keys as document objects."""
        inspector = inspect(self.engine)
        all_foreign_keys = []
        
        for table_name in inspector.get_table_names():
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                all_foreign_keys.append(ForeignKeyDocument(
                    source_table_name=table_name,
                    source_column_name=fk['constrained_columns'][0],
                    target_table_name=fk['referred_table'],
                    target_column_name=fk['referred_columns'][0],
                    constraint_name=fk.get('name', '')
                ))
        
        return all_foreign_keys
    
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Return schemas as document objects."""
        # MariaDB doesn't have explicit schemas like PostgreSQL
        return [SchemaDocument(
            schema_name="default",
            comment="Default MariaDB schema"
        )]
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """Return indexes as document objects."""
        inspector = inspect(self.engine)
        indexes = []
        
        tables = [table_name] if table_name else inspector.get_table_names()
        
        for tbl_name in tables:
            try:
                table_indexes = inspector.get_indexes(tbl_name)
                for idx in table_indexes:
                    indexes.append(IndexDocument(
                        table_name=tbl_name,
                        index_name=idx['name'],
                        column_names=idx['column_names'],
                        is_unique=idx['unique'],
                        index_type="BTREE"  # Default for MariaDB
                    ))
            except SQLAlchemyError as e:
                logger.warning(f"Could not get indexes for table {tbl_name}: {e}")
        
        return indexes
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from the database."""
        # This is a placeholder implementation.
        # A more sophisticated version like in ThothPgManager should be implemented.
        return {}
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data (most frequent values) for each column in a table."""
        inspector = inspect(self.engine)
        try:
            columns = inspector.get_columns(table_name)
        except SQLAlchemyError as e:
            logger.error(f"Error inspecting columns for table {table_name}: {e}")
            raise e

        if not columns:
            logger.warning(f"No columns found for table {table_name}")
            return {}

        most_frequent_values: Dict[str, List[Any]] = {}
        
        with self.engine.connect() as connection:
            for col_info in columns:
                column_name = col_info['name']
                # MariaDB uses backticks for identifier quoting (same as MySQL)
                quoted_column_name = f'`{column_name}`'
                quoted_table_name = f'`{table_name}`'

                query_str = f"""
                    SELECT {quoted_column_name}
                    FROM (
                        SELECT {quoted_column_name}, COUNT(*) as _freq
                        FROM {quoted_table_name}
                        WHERE {quoted_column_name} IS NOT NULL
                        GROUP BY {quoted_column_name}
                        ORDER BY _freq DESC
                        LIMIT :num_rows
                    ) as subquery;
                """
                try:
                    result = connection.execute(text(query_str), {"num_rows": number_of_rows})
                    values = [row[0] for row in result]
                    most_frequent_values[column_name] = values
                except SQLAlchemyError as e:
                    logger.error(f"Error fetching frequent values for {column_name} in {table_name}: {e}")
                    most_frequent_values[column_name] = []

        # Normalize list lengths
        max_length = 0
        if most_frequent_values:
            max_length = max(len(v) for v in most_frequent_values.values()) if most_frequent_values else 0
        
        for column_name in most_frequent_values:
            current_len = len(most_frequent_values[column_name])
            if current_len < max_length:
                most_frequent_values[column_name].extend([None] * (max_length - current_len))
                
        return most_frequent_values


@register_plugin("mariadb")
class MariaDBPlugin(DbPlugin):
    """MariaDB database plugin with full functionality."""
    
    plugin_name = "MariaDB Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["mariadb"]
    required_dependencies = ["mariadb", "SQLAlchemy"]
    
    _instances = {}
    _lock = Lock()
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None
        self.host = None
        self.port = None
        self.dbname = None
        self.user = None
        self.password = None
        
        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None
    
    @classmethod
    def get_instance(cls, host: str, port: int, dbname: str, user: str, password: str, 
                    db_root_path: str, db_mode: str = "dev", **kwargs):
        """Get or create a singleton instance based on connection parameters."""
        required_params = ['host', 'port', 'dbname', 'user', 'password', 'db_root_path']

        all_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
            'db_root_path': db_root_path,
            'db_mode': db_mode,
            **kwargs
        }

        missing_params = [param for param in required_params if all_params.get(param) is None]
        if missing_params:
            raise ValueError(f"Missing required parameter{'s' if len(missing_params) > 1 else ''}: {', '.join(missing_params)}")

        with cls._lock:
            instance_key = (host, port, dbname, user, password, db_root_path, db_mode)
            
            if instance_key not in cls._instances:
                instance = cls(db_root_path=db_root_path, db_mode=db_mode, **all_params)
                instance.initialize(**all_params)
                cls._instances[instance_key] = instance
                
            return cls._instances[instance_key]
    
    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return a MariaDB adapter instance."""
        return MariaDBAdapter(kwargs)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for MariaDB."""
        required = ['host', 'port', 'user', 'password']
        database = kwargs.get('database') or kwargs.get('dbname')
        
        if not database:
            logger.error("Either 'database' or 'dbname' is required for MariaDB")
            return False
        
        for param in required:
            if param not in kwargs:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        port = kwargs.get('port')
        if not isinstance(port, int) or not (1 <= port <= 65535):
            logger.error("port must be an integer between 1 and 65535")
            return False
        
        return True
    
    def initialize(self, **kwargs) -> None:
        """Initialize the MariaDB plugin."""
        # Validate and extract parameters
        self.host = kwargs.get('host')
        self.port = kwargs.get('port', 3306)
        self.dbname = kwargs.get('database') or kwargs.get('dbname')
        self.user = kwargs.get('user') or kwargs.get('username')
        self.password = kwargs.get('password')
        
        # Set additional attributes
        for key, value in kwargs.items():
            if key not in ['host', 'port', 'database', 'dbname', 'user', 'username', 'password']:
                setattr(self, key, value)
        
        # Initialize with updated kwargs
        super().initialize(**kwargs)
        
        # Set up database directory path and ID
        self.db_id = self.dbname
        self._setup_directory_path(self.db_id)
        
        logger.info(f"MariaDB plugin initialized for database: {self.db_id} at {self.host}:{self.port}")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """Set up the database directory path."""
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = Path(self.db_root_path) / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None
    
    @property
    def lsh_manager(self):
        """Lazy load LSH manager for backward compatibility."""
        if self._lsh_manager is None and self.db_directory_path:
            from ..lsh.manager import LshManager
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager
    
    # LSH integration methods for backward compatibility
    def set_lsh(self) -> str:
        """Set LSH for backward compatibility."""
        try:
            if self.lsh_manager and self.lsh_manager.load_lsh():
                return "success"
            else:
                return "error"
        except Exception as e:
            logger.error(f"Error loading LSH: {e}")
            return "error"
    
    def query_lsh(self, keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH for backward compatibility."""
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logger.error(f"LSH query failed: {e}")
                raise Exception(f"Error querying LSH for {self.db_id}: {e}")
        else:
            raise Exception(f"LSH not available for {self.db_id}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        base_info = super().get_plugin_info()
        
        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            base_info.update(adapter_info)
        
        base_info.update({
            "db_id": self.db_id,
            "host": self.host,
            "port": self.port,
            "database": self.dbname,
            "user": self.user,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None
        })
        
        return base_info
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter."""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
