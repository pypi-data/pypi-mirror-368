"""
Database plugins for Thoth SQL Database Manager.
"""

# Import all plugins to ensure they are registered
from .postgresql import PostgreSQLPlugin
from .sqlite import SQLitePlugin
from .mariadb import MariaDBPlugin
from .sqlserver import SQLServerPlugin

# This ensures all plugins are registered when the module is imported
__all__ = [
    "PostgreSQLPlugin",
    "SQLitePlugin",
    "MariaDBPlugin",
    "SQLServerPlugin",
]
