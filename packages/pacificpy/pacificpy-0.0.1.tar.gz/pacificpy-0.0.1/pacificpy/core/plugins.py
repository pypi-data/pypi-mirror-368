from typing import Any, Callable, Dict, List, Optional, Union
import importlib
import sys


class Plugin:
    """
    Base class for plugins.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the plugin.
        
        Args:
            name: The name of the plugin.
            config: Optional configuration for the plugin.
        """
        self.name = name
        self.config = config or {}
    
    async def on_startup(self) -> None:
        """
        Called when the application starts up.
        Override this method to implement startup logic.
        """
        pass
    
    async def on_shutdown(self) -> None:
        """
        Called when the application shuts down.
        Override this method to implement shutdown logic.
        """
        pass


class PluginManager:
    """
    Manager for plugins with lifecycle hooks and configuration.
    """
    
    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self._plugins: Dict[str, Plugin] = {}
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
    
    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a plugin.
        
        Args:
            plugin: The plugin to register.
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin with name '{plugin.name}' is already registered")
        
        self._plugins[plugin.name] = plugin
        
        # Register lifecycle hooks
        if hasattr(plugin, 'on_startup'):
            self._startup_hooks.append(plugin.on_startup)
        if hasattr(plugin, 'on_shutdown'):
            self._shutdown_hooks.append(plugin.on_shutdown)
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a registered plugin by name.
        
        Args:
            name: The name of the plugin.
            
        Returns:
            The plugin or None if not found.
        """
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List of plugin names.
        """
        return list(self._plugins.keys())
    
    async def run_startup_hooks(self) -> None:
        """
        Run all registered startup hooks.
        """
        for hook in self._startup_hooks:
            if hasattr(hook, '__call__'):
                if hasattr(hook, '__self__') and hasattr(hook.__self__, '__class__'):
                    # This is a method, call it on the plugin instance
                    await hook()
                else:
                    # This is a function, call it directly
                    result = hook()
                    if hasattr(result, '__await__'):
                        await result
    
    async def run_shutdown_hooks(self) -> None:
        """
        Run all registered shutdown hooks.
        """
        for hook in self._shutdown_hooks:
            if hasattr(hook, '__call__'):
                if hasattr(hook, '__self__') and hasattr(hook.__self__, '__class__'):
                    # This is a method, call it on the plugin instance
                    await hook()
                else:
                    # This is a function, call it directly
                    result = hook()
                    if hasattr(result, '__await__'):
                        await result
    
    def load_plugins_from_entry_points(self, group: str = "pacificpy.plugins") -> None:
        """
        Load plugins from entry points (placeholder implementation).
        
        Args:
            group: The entry point group to load plugins from.
        """
        try:
            # This is a placeholder implementation
            # In a real implementation, this would use importlib.metadata (Python 3.8+)
            # to discover and load plugins from entry points
            if sys.version_info >= (3, 8):
                import importlib.metadata
                # This would be the real implementation:
                # entry_points = importlib.metadata.entry_points()
                # if hasattr(entry_points, 'select'):
                #     plugins = entry_points.select(group=group)
                # else:
                #     plugins = entry_points.get(group, [])
                pass
            else:
                # For older Python versions, we can't load entry points
                pass
        except Exception:
            # If entry point loading fails, just continue
            pass
    
    def load_plugin_from_module(self, module_name: str, plugin_class_name: str, 
                               plugin_name: Optional[str] = None, 
                               config: Optional[Dict[str, Any]] = None) -> Plugin:
        """
        Load a plugin from a module.
        
        Args:
            module_name: The name of the module containing the plugin.
            plugin_class_name: The name of the plugin class.
            plugin_name: Optional name for the plugin (defaults to class name).
            config: Optional configuration for the plugin.
            
        Returns:
            The loaded plugin.
        """
        # Import the module
        module = importlib.import_module(module_name)
        
        # Get the plugin class
        plugin_class = getattr(module, plugin_class_name)
        
        # Create plugin instance
        name = plugin_name or plugin_class_name
        plugin = plugin_class(name, config)
        
        # Register the plugin
        self.register_plugin(plugin)
        
        return plugin