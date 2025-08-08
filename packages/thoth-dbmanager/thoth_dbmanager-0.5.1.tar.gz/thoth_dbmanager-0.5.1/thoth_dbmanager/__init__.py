"""
Thoth Database Manager - A unified interface for multiple database systems.

This package provides database-agnostic operations, LSH similarity search,
and an extensible plugin architecture for managing SQL databases.
"""

# Core classes
from .ThothDbManager import ThothDbManager
from .core.factory import ThothDbFactory
from .core.interfaces import DbPlugin, DbAdapter
from .core.registry import DbPluginRegistry

# Document models
from .documents import (
    BaseThothDbDocument,
    TableDocument,
    ColumnDocument,
    QueryDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument,
    ThothDbType,
    create_document
)

# LSH functionality
from .lsh.factory import make_db_lsh
from .lsh import LshManager, LshFactory

# Dynamic import system
from .dynamic_imports import (
    import_manager,
    import_adapter,
    import_plugin,
    get_available_databases,
    import_database_components,
    DatabaseImportError,
)

# Public API - Modern Plugin Architecture Only
__all__ = [
    # Core API
    "ThothDbManager",
    "ThothDbFactory", 
    "DbPluginRegistry",
    "DbPlugin",
    "DbAdapter",
    
    # Document models
    "BaseThothDbDocument",
    "TableDocument",
    "ColumnDocument", 
    "QueryDocument",
    "SchemaDocument",
    "ForeignKeyDocument",
    "IndexDocument",
    "ThothDbType",
    "create_document",
    
    # LSH functionality
    "make_db_lsh",
    "LshManager",
    "LshFactory",
    
    # Dynamic import system
    "import_manager",
    "import_adapter", 
    "import_plugin",
    "get_available_databases",
    "import_database_components",
    "DatabaseImportError",
]

__version__ = "0.5.0"