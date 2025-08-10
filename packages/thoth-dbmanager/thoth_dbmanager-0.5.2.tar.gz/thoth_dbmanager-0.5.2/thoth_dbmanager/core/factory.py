"""
Factory for creating database manager instances with plugin support.
"""
import logging
from typing import Any, Dict, List, Optional
from .registry import DbPluginRegistry
from .interfaces import DbPlugin

logger = logging.getLogger(__name__)


class ThothDbFactory:
    """
    Factory class for creating database manager instances.
    Provides plugin-based instantiation with backward compatibility.
    """
    
    @staticmethod
    def create_manager(db_type: str, db_root_path: Optional[str] = None, db_mode: str = "dev", **kwargs) -> DbPlugin:
        """
        Create a database manager instance using the plugin system.
        
        Args:
            db_type: Database type identifier (e.g., 'postgresql', 'sqlite')
            db_root_path: Path to database root directory (can be in kwargs)
            db_mode: Database mode (dev, prod, etc.)
            **kwargs: Database-specific connection parameters
            
        Returns:
            Database plugin instance
            
        Raises:
            ValueError: If database type is not supported
            RuntimeError: If plugin initialization fails
        """
        try:
            # Handle db_root_path from kwargs for backward compatibility
            if db_root_path is None:
                db_root_path = kwargs.get('db_root_path')
            if db_root_path is None:
                raise ValueError("db_root_path is required")

            # Handle db_mode from kwargs for backward compatibility
            if 'db_mode' in kwargs:
                db_mode = kwargs.get('db_mode', db_mode)

            # Remove extracted parameters from kwargs to avoid duplicate parameter errors
            kwargs_clean = kwargs.copy()
            kwargs_clean.pop('db_root_path', None)
            kwargs_clean.pop('db_mode', None)

            # Create plugin instance
            plugin = DbPluginRegistry.create_plugin(
                db_type=db_type,
                db_root_path=db_root_path,
                db_mode=db_mode,
                **kwargs_clean
            )
            
            # Initialize the plugin
            plugin.initialize(**kwargs_clean)
            
            logger.info(f"Successfully created {db_type} manager for {db_root_path}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to create {db_type} manager: {e}")
            raise RuntimeError(f"Failed to create {db_type} manager: {e}") from e
    
    @staticmethod
    def list_available_databases() -> List[str]:
        """
        List all available database types.
        
        Returns:
            List of supported database type identifiers
        """
        return DbPluginRegistry.list_plugins()
    
    @staticmethod
    def get_database_info(db_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about available database plugins.
        
        Args:
            db_type: Specific database type, or None for all
            
        Returns:
            Database plugin information
        """
        return DbPluginRegistry.get_plugin_info(db_type)
    
    @staticmethod
    def validate_database_type(db_type: str) -> bool:
        """
        Check if a database type is supported.
        
        Args:
            db_type: Database type identifier
            
        Returns:
            True if supported, False otherwise
        """
        return db_type in DbPluginRegistry.list_plugins()
    
    @staticmethod
    def get_required_parameters(db_type: str) -> Dict[str, Any]:
        """
        Get required connection parameters for a database type.
        
        Args:
            db_type: Database type identifier
            
        Returns:
            Dictionary describing required parameters
        """
        try:
            plugin_class = DbPluginRegistry.get_plugin_class(db_type)
            
            # This would ideally be defined in the plugin class
            # For now, return common parameters based on database type
            common_params = {
                "postgresql": {
                    "required": ["host", "port", "database", "user", "password"],
                    "optional": ["schema", "sslmode", "connect_timeout"]
                },
                "sqlite": {
                    "required": ["database_path"],
                    "optional": ["timeout", "check_same_thread"]
                },
                "mariadb": {
                    "required": ["host", "port", "database", "user", "password"],
                    "optional": ["charset", "autocommit", "connect_timeout"]
                },
                "sqlserver": {
                    "required": ["server", "database", "user", "password"],
                    "optional": ["driver", "trusted_connection", "timeout"]
                }
            }
            
            return common_params.get(db_type, {
                "required": [],
                "optional": [],
                "note": f"Parameters for {db_type} not defined. Check plugin documentation."
            })
            
        except ValueError:
            return {
                "error": f"Database type '{db_type}' not supported",
                "available_types": DbPluginRegistry.list_plugins()
            }
    
    @staticmethod
    def create_with_validation(db_type: str, db_root_path: str, db_mode: str = "dev", **kwargs) -> DbPlugin:
        """
        Create a database manager with parameter validation.
        
        Args:
            db_type: Database type identifier
            db_root_path: Path to database root directory
            db_mode: Database mode
            **kwargs: Connection parameters
            
        Returns:
            Database plugin instance
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If creation fails
        """
        # Validate database type
        if not ThothDbFactory.validate_database_type(db_type):
            available = ThothDbFactory.list_available_databases()
            raise ValueError(f"Unsupported database type '{db_type}'. Available: {available}")
        
        # Get required parameters
        param_info = ThothDbFactory.get_required_parameters(db_type)
        
        if "required" in param_info:
            # Check required parameters
            missing_params = []
            for param in param_info["required"]:
                if param not in kwargs:
                    missing_params.append(param)
            
            if missing_params:
                raise ValueError(f"Missing required parameters for {db_type}: {missing_params}")
        
        # Create the manager
        return ThothDbFactory.create_manager(db_type, db_root_path, db_mode, **kwargs)
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> DbPlugin:
        """
        Create a database manager from a configuration dictionary.
        
        Args:
            config: Configuration dictionary containing all parameters
            
        Returns:
            Database plugin instance
            
        Example config:
            {
                "db_type": "postgresql",
                "db_root_path": "/path/to/db",
                "db_mode": "dev",
                "host": "localhost",
                "port": 5432,
                "database": "mydb",
                "user": "user",
                "password": "pass"
            }
        """
        # Extract factory parameters
        db_type = config.pop("db_type")
        db_root_path = config.pop("db_root_path")
        db_mode = config.pop("db_mode", "dev")
        
        # Remaining parameters are connection parameters
        return ThothDbFactory.create_with_validation(
            db_type=db_type,
            db_root_path=db_root_path,
            db_mode=db_mode,
            **config
        )
    
    @staticmethod
    def get_plugin_status() -> Dict[str, Any]:
        """
        Get status information about all registered plugins.
        
        Returns:
            Status information for all plugins
        """
        plugins = DbPluginRegistry.list_plugins()
        status = {
            "total_plugins": len(plugins),
            "available_types": plugins,
            "plugins": {}
        }
        
        for db_type in plugins:
            try:
                plugin_info = DbPluginRegistry.get_plugin_info(db_type)
                status["plugins"][db_type] = {
                    "status": "available",
                    "info": plugin_info
                }
            except Exception as e:
                status["plugins"][db_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status
