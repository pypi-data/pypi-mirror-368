"""
SQL Server adapter implementation.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbAdapter
from ..documents import TableDocument, ColumnDocument, ForeignKeyDocument, SchemaDocument, IndexDocument

logger = logging.getLogger(__name__)


class SQLServerAdapter(DbAdapter):
    """SQL Server database adapter implementation."""

    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.host = connection_params.get('host', 'localhost')
        self.port = connection_params.get('port', 1433)
        self.database = connection_params.get('database')
        self.user = connection_params.get('user')
        self.password = connection_params.get('password')
        self.driver = connection_params.get('driver', 'ODBC Driver 17 for SQL Server')
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            # Build connection string for SQL Server (this will test drivers)
            connection_string = self._build_connection_string()

            # Create the engine (connection already tested in _build_connection_string)
            self.engine = create_engine(connection_string, pool_pre_ping=True)

            self._initialized = True
            logger.info("SQL Server connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            raise ConnectionError(f"Failed to connect to SQL Server: {e}")

    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string for SQL Server"""
        if not all([self.database, self.user, self.password]):
            raise ValueError("Missing required connection parameters: database, user, password")

        # Try different connection methods in order of preference
        connection_methods = [
            # Try pyodbc with ODBC Driver 18 and SSL bypass (for testing with containers)
            lambda: f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes",
            # Try pyodbc with ODBC Driver 18 without encryption
            lambda: f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no",
            # Try pymssql (easier to install, no system dependencies)
            lambda: f"mssql+pymssql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            # Try pyodbc with other drivers
            lambda: f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes",
            lambda: f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=FreeTDS",
        ]

        # Try each connection method until one works
        for i, method in enumerate(connection_methods):
            try:
                connection_string = method()

                # Test the connection string by creating a temporary engine
                test_engine = create_engine(connection_string, pool_pre_ping=True)
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                test_engine.dispose()

                method_name = "pymssql" if i == 0 else f"pyodbc method {i}"
                logger.info(f"Successfully connected using {method_name}")
                return connection_string

            except Exception as e:
                logger.debug(f"Connection method {i+1} failed: {e}")
                continue

        # If all methods fail, raise an error with helpful information
        raise ConnectionError(
            f"Failed to connect to SQL Server using any available method. "
            f"Please ensure SQL Server is running and accessible, and that either "
            f"pymssql or pyodbc with appropriate drivers is installed."
        )

    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self._initialized = False

    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                # Set query timeout (SQL Server uses seconds)
                conn.execute(text(f"SET LOCK_TIMEOUT {timeout * 1000}"))  # SQL Server uses milliseconds

                # Execute query
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                # Handle different fetch modes
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    if fetch == "all":
                        return result.fetchall()
                    elif fetch == "one":
                        return result.fetchone()
                    elif isinstance(fetch, int):
                        return result.fetchmany(fetch)
                    else:
                        return result.fetchall()
                else:
                    # For non-SELECT queries, return rowcount
                    conn.commit()
                    return result.rowcount

        except SQLAlchemyError as e:
            logger.error(f"SQL Server query error: {e}")
            raise
    
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
            raise RuntimeError(f"SQL Server update failed: {e}")
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database."""
        query = """
        SELECT TABLE_NAME as name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        result = self.execute_query(query)
        return [row['name'] for row in result]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        query = f"""
        SELECT 
            COLUMN_NAME as name,
            DATA_TYPE as type,
            IS_NULLABLE as nullable,
            COLUMN_DEFAULT as default_value,
            CASE WHEN COLUMNPROPERTY(OBJECT_ID(TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1 THEN 1 ELSE 0 END as is_identity,
            CASE WHEN EXISTS (
                SELECT 1 FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME = c.COLUMN_NAME 
                AND CONSTRAINT_NAME LIKE 'PK_%'
            ) THEN 1 ELSE 0 END as is_primary_key
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        
        columns = self.execute_query(query)
        
        schema = {
            'table_name': table_name,
            'columns': []
        }
        
        for col in columns:
            schema['columns'].append({
                'name': col['name'],
                'type': col['type'],
                'nullable': col['nullable'] == 'YES',
                'default': col['default_value'],
                'primary_key': bool(col['is_primary_key']),
                'auto_increment': bool(col['is_identity'])
            })
        
        return schema
    
    def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        query = f"""
        SELECT 
            i.name as index_name,
            c.name as column_name,
            i.is_unique as unique_index,
            i.type_desc as index_type
        FROM sys.indexes i
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        JOIN sys.tables t ON i.object_id = t.object_id
        WHERE t.name = '{table_name}'
        ORDER BY i.name, ic.key_ordinal
        """
        
        return self.execute_query(query)
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        query = f"""
        SELECT 
            fk.name as constraint_name,
            c.name as column_name,
            OBJECT_NAME(fk.referenced_object_id) as referenced_table,
            rc.name as referenced_column
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
        JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
        JOIN sys.tables t ON fk.parent_object_id = t.object_id
        WHERE t.name = '{table_name}'
        """
        
        return self.execute_query(query)
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create a new table with the given schema."""
        columns = []
        for col in schema.get('columns', []):
            col_def = f"[{col['name']}] {col['type']}"
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if col.get('default') is not None:
                col_def += f" DEFAULT {col['default']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('auto_increment'):
                col_def += " IDENTITY(1,1)"
            columns.append(col_def)
        
        query = f"CREATE TABLE [{table_name}] ({', '.join(columns)})"
        self.execute_update(query)
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        query = f"DROP TABLE IF EXISTS [{table_name}]"
        self.execute_update(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = f"""
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = '{table_name}'
        AND TABLE_TYPE = 'BASE TABLE'
        """
        result = self.execute_query(query)
        return result[0]['count'] > 0
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'type': 'sqlserver',
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'connected': self.engine is not None and self._initialized
        }

    def get_tables_as_documents(self) -> List[TableDocument]:
        """Get tables as TableDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        query = """
        SELECT
            TABLE_NAME as name,
            TABLE_SCHEMA as schema_name,
            '' as comment
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """

        try:
            result = self.execute_query(query)
            tables = []

            for row in result:
                # Handle both tuple and dict results from SQLAlchemy
                # Try dict-style access first, fall back to tuple-style if it fails
                try:
                    table_name = row['name']
                    schema_name = row.get('schema_name', 'dbo')
                    comment = row.get('comment', '')
                except (TypeError, KeyError):
                    # Fall back to tuple-style access
                    table_name = row[0]  # name is the first column
                    schema_name = row[1] if len(row) > 1 else 'dbo'  # schema_name is second
                    comment = row[2] if len(row) > 2 else ''  # comment is third

                table_doc = TableDocument(
                    table_name=table_name,
                    schema_name=schema_name,
                    comment=comment,
                    columns=[],  # Will be populated separately if needed
                    foreign_keys=[],
                    indexes=[]
                )
                tables.append(table_doc)

            return tables

        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            raise

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

        for column in columns:
            column_name = column['name']
            try:
                # Get most frequent values for this column
                query = f"""
                SELECT TOP {number_of_rows} [{column_name}], COUNT(*) as frequency
                FROM [{table_name}]
                WHERE [{column_name}] IS NOT NULL
                GROUP BY [{column_name}]
                ORDER BY COUNT(*) DESC
                """

                result = self.execute_query(query)
                values = [row[column_name] for row in result]
                most_frequent_values[column_name] = values

            except Exception as e:
                logger.warning(f"Error getting example data for column {column_name}: {e}")
                most_frequent_values[column_name] = []

        return most_frequent_values

    def get_columns_as_documents(self, table_name: str = None) -> List[ColumnDocument]:
        """Get columns as ColumnDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            # Get columns for specific table
            query = f"""
            SELECT
                c.TABLE_NAME as table_name,
                c.COLUMN_NAME as column_name,
                c.DATA_TYPE as data_type,
                c.IS_NULLABLE as is_nullable,
                c.COLUMN_DEFAULT as default_value,
                CASE WHEN COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') = 1 THEN 1 ELSE 0 END as is_identity,
                CASE WHEN EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = c.TABLE_NAME
                    AND COLUMN_NAME = c.COLUMN_NAME
                    AND CONSTRAINT_NAME LIKE 'PK_%'
                ) THEN 1 ELSE 0 END as is_primary_key
            FROM INFORMATION_SCHEMA.COLUMNS c
            WHERE c.TABLE_NAME = '{table_name}'
            ORDER BY c.ORDINAL_POSITION
            """
        else:
            # Get all columns
            query = """
            SELECT
                c.TABLE_NAME as table_name,
                c.COLUMN_NAME as column_name,
                c.DATA_TYPE as data_type,
                c.IS_NULLABLE as is_nullable,
                c.COLUMN_DEFAULT as default_value,
                CASE WHEN COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') = 1 THEN 1 ELSE 0 END as is_identity,
                CASE WHEN EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = c.TABLE_NAME
                    AND COLUMN_NAME = c.COLUMN_NAME
                    AND CONSTRAINT_NAME LIKE 'PK_%'
                ) THEN 1 ELSE 0 END as is_primary_key
            FROM INFORMATION_SCHEMA.COLUMNS c
            ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
            """

        try:
            result = self.execute_query(query)
            columns = []

            for row in result:
                # Handle both tuple and dict results from SQLAlchemy
                # Try dict-style access first, fall back to tuple-style if it fails
                try:
                    # For dict results, access by key
                    column_doc = ColumnDocument(
                        table_name=row['table_name'],
                        column_name=row['column_name'],
                        data_type=row['data_type'],
                        is_nullable=row['is_nullable'] == 'YES',
                        default_value=row.get('default_value'),
                        is_pk=bool(row.get('is_primary_key', 0)),  # Use is_pk, not is_primary_key
                        comment=''
                    )
                except (TypeError, KeyError):
                    # For tuple results, access by index based on SELECT order
                    # Query order: table_name, column_name, data_type, is_nullable, default_value, is_identity, is_primary_key
                    column_doc = ColumnDocument(
                        table_name=row[0],  # table_name
                        column_name=row[1],  # column_name
                        data_type=row[2],  # data_type
                        is_nullable=row[3] == 'YES',  # is_nullable
                        default_value=row[4] if len(row) > 4 else None,  # default_value
                        is_pk=bool(row[6]) if len(row) > 6 else False,  # is_pk (index 6, not 5)
                        comment=''
                    )
                columns.append(column_doc)

            return columns

        except Exception as e:
            logger.error(f"Error getting columns: {e}")
            raise

    def get_foreign_keys_as_documents(self, table_name: str = None) -> List[ForeignKeyDocument]:
        """Get foreign keys as ForeignKeyDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            where_clause = f"WHERE t.name = '{table_name}'"
        else:
            where_clause = ""

        query = f"""
        SELECT
            fk.name as constraint_name,
            t.name as table_name,
            c.name as column_name,
            OBJECT_NAME(fk.referenced_object_id) as referenced_table,
            rc.name as referenced_column
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
        JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
        JOIN sys.tables t ON fk.parent_object_id = t.object_id
        {where_clause}
        ORDER BY fk.name
        """

        try:
            result = self.execute_query(query)
            foreign_keys = []

            for row in result:
                # Handle both tuple and dict results from SQLAlchemy
                # Try dict-style access first, fall back to tuple-style if it fails
                try:
                    fk_doc = ForeignKeyDocument(
                        constraint_name=row['constraint_name'],
                        source_table_name=row['table_name'],
                        source_column_name=row['column_name'],
                        target_table_name=row['referenced_table'],
                        target_column_name=row['referenced_column']
                    )
                except (TypeError, KeyError):
                    # Fall back to tuple-style access based on SELECT order
                    fk_doc = ForeignKeyDocument(
                        constraint_name=row[0],  # constraint_name
                        source_table_name=row[1],       # table_name
                        source_column_name=row[2],      # column_name
                        target_table_name=row[3], # referenced_table
                        target_column_name=row[4] # referenced_column
                    )
                foreign_keys.append(fk_doc)

            return foreign_keys

        except Exception as e:
            logger.error(f"Error getting foreign keys: {e}")
            raise

    def get_indexes_as_documents(self, table_name: str = None) -> List[IndexDocument]:
        """Get indexes as IndexDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            where_clause = f"WHERE t.name = '{table_name}'"
        else:
            where_clause = ""

        query = f"""
        SELECT
            i.name as index_name,
            t.name as table_name,
            c.name as column_name,
            i.is_unique,
            i.is_primary_key
        FROM sys.indexes i
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        JOIN sys.tables t ON i.object_id = t.object_id
        {where_clause}
        WHERE i.name IS NOT NULL
        ORDER BY i.name, ic.key_ordinal
        """

        try:
            result = self.execute_query(query)
            indexes = []

            for row in result:
                index_doc = IndexDocument(
                    index_name=row['index_name'],
                    table_name=row['table_name'],
                    column_name=row['column_name'],
                    is_unique=bool(row['is_unique']),
                    is_primary=bool(row['is_primary_key'])
                )
                indexes.append(index_doc)

            return indexes

        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            raise

    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Get schemas as SchemaDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        query = """
        SELECT
            SCHEMA_NAME as schema_name,
            '' as comment
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME NOT IN ('information_schema', 'sys', 'guest', 'INFORMATION_SCHEMA')
        ORDER BY SCHEMA_NAME
        """

        try:
            result = self.execute_query(query)
            schemas = []

            for row in result:
                schema_doc = SchemaDocument(
                    schema_name=row['schema_name'],
                    comment=row.get('comment', ''),
                    tables=[],  # Will be populated separately if needed
                    views=[]
                )
                schemas.append(schema_doc)

            return schemas

        except Exception as e:
            logger.error(f"Error getting schemas: {e}")
            raise

    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from the database."""
        # This is a placeholder implementation.
        # A more sophisticated version should be implemented based on requirements.
        return {}
