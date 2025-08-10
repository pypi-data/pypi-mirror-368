"""
Dynamic import system for database-specific functionality.
This module provides lazy loading of database managers and adapters.
"""

import importlib
from typing import Dict, Any, Optional, List
import warnings

# Mapping of database names to their required packages
DATABASE_DEPENDENCIES = {
    'postgresql': ['psycopg2'],
    'mariadb': ['mariadb'],
    'sqlserver': ['pyodbc'],
    'sqlite': [],  # Built into Python
}

# Note: DATABASE_MANAGERS is no longer used - managers are created via factory pattern

# Mapping of database names to their adapter classes
DATABASE_ADAPTERS = {
    'postgresql': 'thoth_dbmanager.adapters.postgresql.PostgreSQLAdapter',
    'mariadb': 'thoth_dbmanager.adapters.mariadb.MariaDBAdapter',
    'sqlserver': 'thoth_dbmanager.adapters.sqlserver.SQLServerAdapter',
    'sqlite': 'thoth_dbmanager.adapters.sqlite.SQLiteAdapter',
}

# Mapping of database names to their plugin classes
DATABASE_PLUGINS = {
    'postgresql': 'thoth_dbmanager.plugins.postgresql.PostgreSQLPlugin',
    'mariadb': 'thoth_dbmanager.plugins.mariadb.MariaDBPlugin',
    'sqlserver': 'thoth_dbmanager.plugins.sqlserver.SQLServerPlugin',
    'sqlite': 'thoth_dbmanager.plugins.sqlite.SQLitePlugin',
}


class DatabaseImportError(ImportError):
    """Custom exception for database import errors."""
    
    def __init__(self, database: str, missing_deps: List[str]):
        self.database = database
        self.missing_deps = missing_deps
        super().__init__(
            f"Missing dependencies for {database}: {', '.join(missing_deps)}. "
            f"Install with: pip install thoth-sqldb[{database}]"
        )


def check_dependencies(database: str) -> List[str]:
    """
    Check if required dependencies for a database are available.
    
    Args:
        database: Name of the database
        
    Returns:
        List of missing dependency names
    """
    if database not in DATABASE_DEPENDENCIES:
        raise ValueError(f"Unknown database: {database}")
    
    missing_deps = []
    for dep in DATABASE_DEPENDENCIES[database]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    return missing_deps


def import_manager(database: str) -> Any:
    """
    Dynamically import a database manager using the factory pattern.

    Args:
        database: Name of the database

    Returns:
        The database manager class (factory-created)

    Raises:
        DatabaseImportError: If dependencies are missing
        ImportError: If the manager class cannot be imported
    """
    if database not in DATABASE_PLUGINS:
        raise ValueError(f"Unknown database: {database}")

    # Check dependencies
    missing_deps = check_dependencies(database)
    if missing_deps:
        raise DatabaseImportError(database, missing_deps)

    # Import the factory and create a manager class
    from thoth_dbmanager.core.factory import ThothDbFactory

    # Create a wrapper class that can be instantiated like the old managers
    class DatabaseManagerWrapper:
        def __init__(self, *args, **kwargs):
            # Create manager using factory
            self._manager = ThothDbFactory.create_manager(database, *args, **kwargs)

        def __getattr__(self, name):
            return getattr(self._manager, name)

    return DatabaseManagerWrapper


def import_adapter(database: str) -> Any:
    """
    Dynamically import a database adapter class.
    
    Args:
        database: Name of the database
        
    Returns:
        The database adapter class
        
    Raises:
        DatabaseImportError: If dependencies are missing
        ImportError: If the adapter class cannot be imported
    """
    if database not in DATABASE_ADAPTERS:
        raise ValueError(f"Unknown database: {database}")
    
    # Check dependencies
    missing_deps = check_dependencies(database)
    if missing_deps:
        raise DatabaseImportError(database, missing_deps)
    
    # Import the adapter class
    module_path, class_name = DATABASE_ADAPTERS[database].rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def import_plugin(database: str) -> Any:
    """
    Dynamically import a database plugin class.
    
    Args:
        database: Name of the database
        
    Returns:
        The database plugin class
        
    Raises:
        DatabaseImportError: If dependencies are missing
        ImportError: If the plugin class cannot be imported
    """
    if database not in DATABASE_PLUGINS:
        raise ValueError(f"Unknown database: {database}")
    
    # Check dependencies
    missing_deps = check_dependencies(database)
    if missing_deps:
        raise DatabaseImportError(database, missing_deps)
    
    # Import the plugin class
    module_path, class_name = DATABASE_PLUGINS[database].rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_available_databases() -> Dict[str, bool]:
    """
    Get a dictionary of available databases and their dependency status.
    
    Returns:
        Dictionary mapping database names to availability (True if all dependencies are available)
    """
    availability = {}
    for db in DATABASE_DEPENDENCIES:
        missing_deps = check_dependencies(db)
        availability[db] = len(missing_deps) == 0
    
    return availability


def import_database_components(databases: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Import components for specified databases.
    
    Args:
        databases: List of database names to import
        
    Returns:
        Dictionary mapping database names to their components
    """
    components = {}
    
    for db in databases:
        try:
            components[db] = {
                'manager': import_manager(db),
                'adapter': import_adapter(db),
                'plugin': import_plugin(db)
            }
        except DatabaseImportError as e:
            warnings.warn(str(e))
            components[db] = None
    
    return components


# Convenience functions for common use cases
def import_postgresql():
    """Import PostgreSQL components."""
    return import_database_components(['postgresql'])['postgresql']

def import_mysql():
    """Import MySQL components."""
    return import_database_components(['mysql'])['mysql']

def import_sqlite():
    """Import SQLite components."""
    return import_database_components(['sqlite'])['sqlite']

def import_sqlserver():
    """Import SQL Server components."""
    return import_database_components(['sqlserver'])['sqlserver']

def import_oracle():
    """Import Oracle components."""
    return import_database_components(['oracle'])['oracle']

def import_mariadb():
    """Import MariaDB components."""
    return import_database_components(['mariadb'])['mariadb']

def import_supabase():
    """Import Supabase components."""
    return import_database_components(['supabase'])['supabase']
