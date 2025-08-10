"""
SQLite adapter implementation.
"""
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbAdapter
from ..documents import (
    TableDocument,
    ColumnDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument
)

logger = logging.getLogger(__name__)


class SQLiteAdapter(DbAdapter):
    """
    SQLite database adapter implementation.
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.raw_connection = None
        self.database_path = None
    
    def connect(self) -> None:
        """Establish SQLite connection"""
        try:
            # Get database path
            self.database_path = self.connection_params.get('database_path')
            if not self.database_path:
                raise ValueError("database_path is required for SQLite")
            
            # Ensure directory exists
            db_path = Path(self.database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create SQLAlchemy engine
            connection_string = f"sqlite:///{self.database_path}"
            self.engine = create_engine(connection_string, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Also create raw sqlite3 connection for specific operations
            self.raw_connection = sqlite3.connect(self.database_path)
            self.raw_connection.row_factory = sqlite3.Row  # Enable column access by name
            
            self._initialized = True
            logger.info(f"SQLite connection established successfully: {self.database_path}")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close SQLite connection"""
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
            
            if self.raw_connection:
                self.raw_connection.close()
                self.raw_connection = None
            
            self._initialized = False
            logger.info("SQLite connection closed")
            
        except Exception as e:
            logger.error(f"Error closing SQLite connection: {e}")
    
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            with self.engine.connect() as conn:
                # SQLite doesn't have query timeout, but we can set a connection timeout
                conn.execute(text(f"PRAGMA busy_timeout = {timeout * 1000}"))  # SQLite uses milliseconds
                
                # Execute query
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Handle different fetch modes
                if query.strip().upper().startswith(('SELECT', 'WITH', 'PRAGMA')):
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
            logger.error(f"SQLite query error: {e}")
            raise
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Get tables as document objects"""
        query = """
        SELECT 
            name as table_name,
            sql as table_sql
        FROM sqlite_master 
        WHERE type = 'table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
        
        results = self.execute_query(query)
        documents = []
        
        for row in results:
            # Extract comment from CREATE TABLE statement if present
            comment = ""
            if row.table_sql:
                # Simple comment extraction - could be improved
                sql_lines = row.table_sql.split('\n')
                for line in sql_lines:
                    if '-- ' in line:
                        comment = line.split('-- ', 1)[1].strip()
                        break
            
            doc = TableDocument(
                table_name=row.table_name,
                schema_name="main",  # SQLite default schema
                comment=comment
            )
            documents.append(doc)
        
        return documents
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Get columns as document objects"""
        # Use PRAGMA table_info to get column information
        query = f"PRAGMA table_info({table_name})"
        
        results = self.execute_query(query)
        documents = []
        
        for row in results:
            doc = ColumnDocument(
                table_name=table_name,
                column_name=row.name,
                data_type=row.type,
                comment="",  # SQLite doesn't support column comments natively
                is_pk=bool(row.pk),
                is_nullable=not bool(row.notnull),
                default_value=row.dflt_value,
                schema_name="main"
            )
            documents.append(doc)
        
        return documents
    
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """Get foreign keys as document objects"""
        documents = []
        
        # Get all tables first
        tables = self.get_tables_as_documents()
        
        for table_doc in tables:
            table_name = table_doc.table_name
            
            # Use PRAGMA foreign_key_list to get foreign keys for each table
            query = f"PRAGMA foreign_key_list({table_name})"
            
            try:
                results = self.execute_query(query)
                
                for row in results:
                    doc = ForeignKeyDocument(
                        source_table_name=table_name,
                        source_column_name=row.from_,
                        target_table_name=row.table,
                        target_column_name=row.to,
                        constraint_name=f"fk_{table_name}_{row.id}",  # SQLite doesn't name FKs
                        schema_name="main"
                    )
                    documents.append(doc)
                    
            except Exception as e:
                logger.warning(f"Could not get foreign keys for table {table_name}: {e}")
        
        return documents
    
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Get schemas as document objects"""
        # SQLite has limited schema support, mainly 'main', 'temp', and attached databases
        query = "PRAGMA database_list"
        
        results = self.execute_query(query)
        documents = []
        
        for row in results:
            doc = SchemaDocument(
                schema_name=row.name,
                description=f"SQLite database: {row.file or 'in-memory'}"
            )
            documents.append(doc)
        
        return documents
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """Get indexes as document objects"""
        documents = []
        
        if table_name:
            tables = [table_name]
        else:
            # Get all tables
            table_docs = self.get_tables_as_documents()
            tables = [doc.table_name for doc in table_docs]
        
        for table in tables:
            # Get indexes for this table
            query = f"PRAGMA index_list({table})"
            
            try:
                results = self.execute_query(query)
                
                for row in results:
                    index_name = row.name
                    
                    # Get index columns
                    col_query = f"PRAGMA index_info({index_name})"
                    col_results = self.execute_query(col_query)
                    columns = [col_row.name for col_row in col_results]
                    
                    doc = IndexDocument(
                        index_name=index_name,
                        table_name=table,
                        columns=columns,
                        is_unique=bool(row.unique),
                        is_primary=index_name.startswith('sqlite_autoindex_'),  # SQLite auto-creates these for PKs
                        index_type="btree",  # SQLite primarily uses B-tree indexes
                        schema_name="main"
                    )
                    documents.append(doc)
                    
            except Exception as e:
                logger.warning(f"Could not get indexes for table {table}: {e}")
        
        return documents
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from the database"""
        result = {}
        
        # Get all tables
        tables = self.get_tables_as_documents()
        
        for table_doc in tables:
            table_name = table_doc.table_name
            
            # Get columns for this table
            columns = self.get_columns_as_documents(table_name)
            
            result[table_name] = {}
            
            for column_doc in columns:
                column_name = column_doc.column_name
                
                # Only get unique values for text columns to avoid large datasets
                if column_doc.data_type.upper() in ['TEXT', 'VARCHAR', 'CHAR', 'STRING']:
                    try:
                        query = f"""
                        SELECT DISTINCT "{column_name}"
                        FROM "{table_name}"
                        WHERE "{column_name}" IS NOT NULL
                        AND LENGTH("{column_name}") > 0
                        ORDER BY "{column_name}"
                        LIMIT 1000
                        """
                        
                        values = self.execute_query(query)
                        result[table_name][column_name] = [str(row[0]) for row in values if row[0]]
                        
                    except Exception as e:
                        logger.warning(f"Could not get unique values for {table_name}.{column_name}: {e}")
                        result[table_name][column_name] = []
                else:
                    result[table_name][column_name] = []
        
        return result
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Retrieves the most frequent values for each column in the specified table.
        
        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.
            
        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        # First, verify the table exists
        table_check_query = """
        SELECT name FROM sqlite_master 
        WHERE type = 'table' AND name = :table_name
        """
        
        try:
            table_check_result = self.execute_query(table_check_query, {"table_name": table_name})
            if not table_check_result:
                logger.warning(f"Table {table_name} not found")
                return {}
        except Exception as e:
            logger.error(f"Error checking table {table_name}: {e}")
            return {}
        
        # Get column information using PRAGMA
        try:
            columns_result = self.execute_query(f"PRAGMA table_info({table_name})")
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return {}
        
        if not columns_result:
            logger.warning(f"No columns found for table {table_name}")
            return {}
        
        most_frequent_values: Dict[str, List[Any]] = {}
        
        for row in columns_result:
            column_name = row[1]  # column name is at index 1 in PRAGMA table_info
            data_type = row[2]    # data type is at index 2 in PRAGMA table_info
            
            # SQLite uses double quotes for identifier quoting
            quoted_column_name = f'"{column_name}"'
            quoted_table_name = f'"{table_name}"'
            
            # Query to get most frequent values
            query_str = f"""
                SELECT {quoted_column_name}
                FROM (
                    SELECT {quoted_column_name}, COUNT(*) as _freq
                    FROM {quoted_table_name}
                    WHERE {quoted_column_name} IS NOT NULL
                    GROUP BY {quoted_column_name}
                    ORDER BY _freq DESC
                    LIMIT :num_rows
                )
            """
            
            try:
                result = self.execute_query(query_str, {"num_rows": number_of_rows})
                values = [row[0] for row in result]
                most_frequent_values[column_name] = values
            except Exception as e:
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
