"""
Plugin registry system for database plugins.
"""
import logging
from typing import Dict, List, Type, Optional, Any
from .interfaces import DbPlugin

logger = logging.getLogger(__name__)


class DbPluginRegistry:
    """
    Registry for database plugins.
    Manages plugin registration, discovery, and instantiation.
    """
    
    _plugins: Dict[str, Type[DbPlugin]] = {}
    _instances: Dict[tuple, DbPlugin] = {}  # Singleton instances
    _registered_plugins: set = set()  # Track already registered plugins to avoid spam
    
    @classmethod
    def register(cls, db_type: str, plugin_class: Type[DbPlugin]) -> None:
        """
        Register a plugin for a specific database type.
        
        Args:
            db_type: Database type identifier (e.g., 'postgresql', 'sqlite')
            plugin_class: Plugin class implementing DbPlugin interface
        """
        if not issubclass(plugin_class, DbPlugin):
            raise TypeError(f"Plugin class {plugin_class.__name__} must inherit from DbPlugin")
        
        # Check if plugin is already registered to avoid spam logs
        plugin_key = f"{db_type}:{plugin_class.__name__}"
        if plugin_key in cls._registered_plugins:
            # Plugin already registered, don't log again
            cls._plugins[db_type] = plugin_class
            return
        
        cls._plugins[db_type] = plugin_class
        cls._registered_plugins.add(plugin_key)
        logger.info(f"Registered plugin {plugin_class.__name__} for database type '{db_type}'")
    
    @classmethod
    def unregister(cls, db_type: str) -> None:
        """
        Unregister a plugin for a specific database type.
        
        Args:
            db_type: Database type identifier
        """
        if db_type in cls._plugins:
            plugin_class = cls._plugins.pop(db_type)
            logger.info(f"Unregistered plugin {plugin_class.__name__} for database type '{db_type}'")
            
            # Remove from registered plugins set
            plugin_key = f"{db_type}:{plugin_class.__name__}"
            cls._registered_plugins.discard(plugin_key)
            
            # Remove any cached instances
            keys_to_remove = [key for key in cls._instances.keys() if key[0] == db_type]
            for key in keys_to_remove:
                del cls._instances[key]
    
    @classmethod
    def get_plugin_class(cls, db_type: str) -> Type[DbPlugin]:
        """
        Get plugin class for a specific database type.
        
        Args:
            db_type: Database type identifier
            
        Returns:
            Plugin class
            
        Raises:
            ValueError: If no plugin is registered for the database type
        """
        if db_type not in cls._plugins:
            available_types = list(cls._plugins.keys())
            raise ValueError(f"No plugin registered for database type '{db_type}'. Available types: {available_types}")
        
        return cls._plugins[db_type]
    
    @classmethod
    def create_plugin(cls, db_type: str, db_root_path: str, db_mode: str = "dev", use_singleton: bool = True, **kwargs) -> DbPlugin:
        """
        Create a plugin instance for a specific database type.
        
        Args:
            db_type: Database type identifier
            db_root_path: Path to database root directory
            db_mode: Database mode
            use_singleton: Whether to use singleton pattern
            **kwargs: Additional plugin-specific parameters
            
        Returns:
            Plugin instance
        """
        plugin_class = cls.get_plugin_class(db_type)
        
        if use_singleton:
            # Create instance key for singleton pattern
            instance_key = (db_type, db_root_path, db_mode, tuple(sorted(kwargs.items())))
            
            if instance_key in cls._instances:
                return cls._instances[instance_key]
            
            # Create new instance
            plugin_instance = plugin_class(db_root_path=db_root_path, db_mode=db_mode, **kwargs)
            cls._instances[instance_key] = plugin_instance
            return plugin_instance
        else:
            # Create new instance without caching
            return plugin_class(db_root_path=db_root_path, db_mode=db_mode, **kwargs)
    
    @classmethod
    def list_plugins(cls) -> List[str]:
        """
        List all registered database types.
        
        Returns:
            List of registered database type identifiers
        """
        return list(cls._plugins.keys())
    
    @classmethod
    def get_plugin_info(cls, db_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about registered plugins.
        
        Args:
            db_type: Specific database type, or None for all plugins
            
        Returns:
            Plugin information dictionary
        """
        if db_type:
            if db_type not in cls._plugins:
                raise ValueError(f"No plugin registered for database type '{db_type}'")
            
            plugin_class = cls._plugins[db_type]
            return {
                "db_type": db_type,
                "plugin_name": plugin_class.plugin_name,
                "plugin_version": plugin_class.plugin_version,
                "supported_db_types": plugin_class.supported_db_types,
                "required_dependencies": plugin_class.required_dependencies,
                "class_name": plugin_class.__name__,
                "module": plugin_class.__module__
            }
        else:
            # Return info for all plugins
            return {
                db_type: {
                    "plugin_name": plugin_class.plugin_name,
                    "plugin_version": plugin_class.plugin_version,
                    "supported_db_types": plugin_class.supported_db_types,
                    "required_dependencies": plugin_class.required_dependencies,
                    "class_name": plugin_class.__name__,
                    "module": plugin_class.__module__
                }
                for db_type, plugin_class in cls._plugins.items()
            }
    
    @classmethod
    def validate_plugin(cls, plugin_class: Type[DbPlugin]) -> bool:
        """
        Validate that a plugin class implements the required interface.
        
        Args:
            plugin_class: Plugin class to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if it's a subclass of DbPlugin
            if not issubclass(plugin_class, DbPlugin):
                logger.error(f"Plugin {plugin_class.__name__} does not inherit from DbPlugin")
                return False
            
            # Check required class attributes
            required_attrs = ['plugin_name', 'plugin_version', 'supported_db_types']
            for attr in required_attrs:
                if not hasattr(plugin_class, attr):
                    logger.error(f"Plugin {plugin_class.__name__} missing required attribute: {attr}")
                    return False
            
            # Check required methods
            required_methods = ['create_adapter', 'validate_connection_params']
            for method in required_methods:
                if not hasattr(plugin_class, method) or not callable(getattr(plugin_class, method)):
                    logger.error(f"Plugin {plugin_class.__name__} missing required method: {method}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating plugin {plugin_class.__name__}: {e}")
            return False
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached plugin instances."""
        cls._instances.clear()
        logger.info("Cleared all cached plugin instances")
    
    @classmethod
    def clear_registry(cls) -> None:
        """Clear the entire plugin registry."""
        cls._plugins.clear()
        cls._instances.clear()
        cls._registered_plugins.clear()
        logger.info("Cleared plugin registry")


# Auto-discovery decorator
def register_plugin(db_type: str):
    """
    Decorator to automatically register a plugin.
    
    Args:
        db_type: Database type identifier
        
    Example:
        @register_plugin("postgresql")
        class PostgreSQLPlugin(DbPlugin):
            pass
    """
    def decorator(plugin_class: Type[DbPlugin]):
        DbPluginRegistry.register(db_type, plugin_class)
        return plugin_class
    return decorator