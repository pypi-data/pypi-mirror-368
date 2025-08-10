import logging
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union, ClassVar, Type, TypeVar

from .lsh.manager import LshManager
from .core.factory import ThothDbFactory

T = TypeVar('T', bound='ThothDbManager')

class ThothDbManager(ABC):
    """
    Modern database manager interface using plugin architecture.
    
    This class provides a unified interface for database operations
    across multiple database types through the plugin system.
    """
    _instances: ClassVar[Dict[tuple, Any]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_instance(cls: Type[T], db_type: str, **kwargs) -> T:
        """
        Get or create a singleton instance using the plugin architecture.
        
        Args:
            db_type (str): The type of database (e.g., 'postgresql', 'sqlite', 'mysql').
            **kwargs: Connection parameters specific to the database implementation.
            
        Returns:
            An instance of the appropriate database manager.
            
        Raises:
            ValueError: If the database type is unsupported or required parameters are missing.
        """
        # Import all plugins to ensure they're registered
        from . import plugins
        
        try:
            # Create plugin instance using factory
            plugin = ThothDbFactory.create_manager(db_type, **kwargs)
            return plugin
            
        except Exception as e:
            logging.error(f"Failed to create {db_type} manager: {e}")
            raise ValueError(f"Unsupported database type '{db_type}' or invalid parameters: {e}")
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", db_type: Optional[str] = None, **kwargs) -> None:
        """
        Initialize the database manager.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str, optional): Database mode (dev, prod, etc.). Defaults to "dev".
            db_type (Optional[str], optional): Type of database. Defaults to None.
            **kwargs: Additional parameters specific to the database implementation.
        """
        self._validate_common_params(db_root_path, db_mode)
        
        self.db_root_path = db_root_path
        self.db_mode = db_mode
        self.db_type = db_type
        
        # These will be set by subclasses
        self.engine = None
        self.db_id = None
        self.db_directory_path = None
        
        # New LSH manager (lazy initialization)
        self._lsh_manager = None
        
        # Flag to track initialization
        self._initialized = False
    
    def _validate_common_params(self, db_root_path: str, db_mode: str) -> None:
        """
        Validate common parameters for all database implementations.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str): Database mode (dev, prod, etc.).
            
        Raises:
            ValueError: If parameters are invalid.
        """
        if not db_root_path:
            raise ValueError("db_root_path is required")
        
        if not isinstance(db_mode, str):
            raise TypeError("db_mode must be a string")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """
        Set up the database directory path.
        
        Args:
            db_id (str): Database identifier.
        """
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = self.db_root_path / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None

    @property
    def lsh_manager(self) -> Optional[LshManager]:
        """
        Lazy load LSH manager.
        
        Returns:
            LshManager instance if db_directory_path is set, None otherwise
        """
        if self._lsh_manager is None and self.db_directory_path:
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager

    @abstractmethod
    def execute_sql(self,
                   sql: str, 
                   params: Optional[Dict] = None, 
                   fetch: Union[str, int] = "all", 
                   timeout: int = 60) -> Any:
        """
        Abstract method to execute SQL queries.

        Args:
            sql (str): The SQL query to execute.
            params (Optional[Dict]): Parameters for the SQL query.
            fetch (Union[str, int]): Specifies how to fetch the results.
            timeout (int): Timeout for the query execution.

        Returns:
            Any: The result of the SQL query execution.
        """
        pass
    
    @abstractmethod
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get unique values from the database.
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of unique values
        """
        pass

    @abstractmethod
    def get_tables(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of tables in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a table with 'name' and 'comment' keys.
        """
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Abstract method to get a list of columns for a given table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a column with 'name', 'data_type',
                                  'comment', and 'is_pk' keys.
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of foreign key relationships in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a foreign key relationship with
                                  'source_table_name', 'source_column_name',
                                  'target_table_name', and 'target_column_name' keys.
        """
        pass
    
    @abstractmethod
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Abstract method to get example data (most frequent values) for each column in a table.

        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.

        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        pass
    
    def query_lsh(self,
                 keyword: str,
                 signature_size: int = 30,
                 n_gram: int = 3,
                 top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """
        Queries the LSH for similar values to the given keyword.

        Args:
            keyword (str): The keyword to search for.
            signature_size (int, optional): The size of the MinHash signature. Defaults to 30.
            n_gram (int, optional): The n-gram size for the MinHash. Defaults to 3.
            top_n (int, optional): The number of top results to return. Defaults to 10.

        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of similar strings
        """
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logging.error(f"LSH manager query failed: {e}")
                raise Exception(f"Error querying LSH for {self.db_id}: {e}")
        else:
            raise Exception(f"LSH manager not initialized for {self.db_id}")

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            self.execute_sql("SELECT 1", fetch="one")
            return True
        except Exception:
            return False