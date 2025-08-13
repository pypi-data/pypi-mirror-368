import pytest
from pacificpy.core.plugins import Plugin, PluginManager


# Global variables to track plugin execution
plugin_startup_called = False
plugin_shutdown_called = False
plugin_name = None
plugin_config = None


class TestPlugin(Plugin):
    """Test plugin for testing."""
    
    async def on_startup(self) -> None:
        """Called when the application starts up."""
        global plugin_startup_called, plugin_name, plugin_config
        plugin_startup_called = True
        plugin_name = self.name
        plugin_config = self.config
    
    async def on_shutdown(self) -> None:
        """Called when the application shuts down."""
        global plugin_shutdown_called
        plugin_shutdown_called = True


class TestPluginWithoutHooks(Plugin):
    """Test plugin without lifecycle hooks."""
    pass


def test_plugin_manager_register_plugin():
    """Test that plugin manager can register plugins."""
    global plugin_startup_called, plugin_shutdown_called, plugin_name, plugin_config
    
    # Reset global variables
    plugin_startup_called = False
    plugin_shutdown_called = False
    plugin_name = None
    plugin_config = None
    
    # Create plugin manager
    manager = PluginManager()
    
    # Create plugin
    plugin = TestPlugin("test-plugin", {"key": "value"})
    
    # Register plugin
    manager.register_plugin(plugin)
    
    # Check that plugin is registered
    assert manager.get_plugin("test-plugin") is plugin
    assert manager.list_plugins() == ["test-plugin"]


def test_plugin_manager_register_duplicate_plugin():
    """Test that plugin manager raises error for duplicate plugin names."""
    # Create plugin manager
    manager = PluginManager()
    
    # Create plugins
    plugin1 = TestPlugin("test-plugin")
    plugin2 = TestPlugin("test-plugin")
    
    # Register first plugin
    manager.register_plugin(plugin1)
    
    # Try to register second plugin with same name (should raise error)
    with pytest.raises(ValueError):
        manager.register_plugin(plugin2)


def test_plugin_manager_get_nonexistent_plugin():
    """Test that plugin manager returns None for nonexistent plugins."""
    # Create plugin manager
    manager = PluginManager()
    
    # Try to get nonexistent plugin
    assert manager.get_plugin("nonexistent-plugin") is None


@pytest.mark.asyncio
async def test_plugin_manager_run_startup_hooks():
    """Test that plugin manager can run startup hooks."""
    global plugin_startup_called, plugin_shutdown_called, plugin_name, plugin_config
    
    # Reset global variables
    plugin_startup_called = False
    plugin_shutdown_called = False
    plugin_name = None
    plugin_config = None
    
    # Create plugin manager
    manager = PluginManager()
    
    # Create plugin
    plugin = TestPlugin("test-plugin", {"key": "value"})
    
    # Register plugin
    manager.register_plugin(plugin)
    
    # Run startup hooks
    await manager.run_startup_hooks()
    
    # Check that startup hook was called
    assert plugin_startup_called is True
    assert plugin_name == "test-plugin"
    assert plugin_config == {"key": "value"}


@pytest.mark.asyncio
async def test_plugin_manager_run_shutdown_hooks():
    """Test that plugin manager can run shutdown hooks."""
    global plugin_startup_called, plugin_shutdown_called
    
    # Reset global variables
    plugin_startup_called = False
    plugin_shutdown_called = False
    
    # Create plugin manager
    manager = PluginManager()
    
    # Create plugin
    plugin = TestPlugin("test-plugin")
    
    # Register plugin
    manager.register_plugin(plugin)
    
    # Run shutdown hooks
    await manager.run_shutdown_hooks()
    
    # Check that shutdown hook was called
    assert plugin_shutdown_called is True


@pytest.mark.asyncio
async def test_plugin_manager_run_hooks_without_plugins():
    """Test that plugin manager can handle running hooks without plugins."""
    # Create plugin manager
    manager = PluginManager()
    
    # Run startup and shutdown hooks (should not raise exception)
    await manager.run_startup_hooks()
    await manager.run_shutdown_hooks()


@pytest.mark.asyncio
async def test_plugin_manager_run_hooks_with_plugin_without_hooks():
    """Test that plugin manager can handle plugins without hooks."""
    # Create plugin manager
    manager = PluginManager()
    
    # Create plugin without hooks
    plugin = TestPluginWithoutHooks("test-plugin")
    
    # Register plugin
    manager.register_plugin(plugin)
    
    # Run startup and shutdown hooks (should not raise exception)
    await manager.run_startup_hooks()
    await manager.run_shutdown_hooks()


def test_plugin_manager_load_plugins_from_entry_points():
    """Test that plugin manager can load plugins from entry points (placeholder)."""
    # Create plugin manager
    manager = PluginManager()
    
    # Load plugins from entry points (should not raise exception)
    manager.load_plugins_from_entry_points()


def test_plugin_base_class():
    """Test that plugin base class works correctly."""
    # Create plugin
    plugin = Plugin("test-plugin", {"key": "value"})
    
    # Check plugin attributes
    assert plugin.name == "test-plugin"
    assert plugin.config == {"key": "value"}
    
    # Check that default lifecycle methods exist and do nothing
    assert hasattr(plugin, 'on_startup')
    assert hasattr(plugin, 'on_shutdown')
    
    # Call default lifecycle methods (should not raise exception)
    import asyncio
    asyncio.run(plugin.on_startup())
    asyncio.run(plugin.on_shutdown())