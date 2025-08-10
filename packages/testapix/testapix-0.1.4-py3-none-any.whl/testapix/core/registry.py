"""Plugin registry system for TestAPIX extensibility.

This module provides the core plugin architecture that allows TestAPIX to be extended
with custom authentication providers, health checks, data generators, and assertion plugins.
The registry follows a type-safe, event-driven design that supports both built-in
and third-party extensions.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from testapix.core.exceptions import TestAPIXError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="TestAPIXPlugin")
EventHandler = Callable[[Any], None]


class PluginError(TestAPIXError):
    """Raised when plugin operations fail."""

    def __init__(self, message: str, plugin_name: str | None = None) -> None:
        super().__init__(message)
        self.plugin_name = plugin_name


class TestAPIXPlugin(ABC):
    """Base interface for all TestAPIX plugins.

    All extensible components in TestAPIX must implement this interface to ensure
    consistent initialization, configuration, and lifecycle management.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name identifier for this plugin."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the version string for this plugin."""

    @property
    def description(self) -> str:
        """Return a human-readable description of this plugin."""
        return f"{self.name} v{self.version}"

    @property
    def dependencies(self) -> list[str]:
        """Return list of plugin names this plugin depends on."""
        return []

    @abstractmethod
    def initialize(self, config: Mapping[str, Any]) -> None:
        """Initialize the plugin with the given configuration.

        Args:
        ----
            config: Plugin-specific configuration mapping

        Raises:
        ------
            PluginError: If initialization fails

        """

    def cleanup(self) -> None:
        """Clean up plugin resources. Called when plugin is unregistered.

        Default implementation does nothing. Subclasses should override
        this method if they need to clean up resources like connections,
        files, or background tasks.
        """
        # Default implementation - no cleanup needed for basic plugins
        return


@dataclass
class PluginMetadata:
    """Metadata about a registered plugin."""

    name: str
    version: str
    description: str
    plugin_class: type[TestAPIXPlugin]
    instance: TestAPIXPlugin | None = None
    dependencies: list[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    initialized: bool = False


class PluginRegistry(Generic[T]):
    """Type-safe registry for managing TestAPIX plugins.

    This registry provides centralized management of plugin lifecycle,
    dependency resolution, and configuration. It supports both programmatic
    registration and configuration-driven plugin loading.
    """

    def __init__(self, plugin_type_name: str) -> None:
        """Initialize the plugin registry.

        Args:
        ----
            plugin_type_name: Human-readable name for this plugin type (e.g., "Auth Provider")

        """
        self._plugin_type_name = plugin_type_name
        self._plugins: dict[str, PluginMetadata] = {}
        self._event_handlers: dict[str, list[EventHandler]] = {}
        self._logger = logging.getLogger(f"{__name__}.{plugin_type_name}")

    @property
    def plugin_type_name(self) -> str:
        """Return the human-readable name for this plugin type."""
        return self._plugin_type_name

    def register(
        self,
        name: str,
        plugin_class: type[T],
        config: Mapping[str, Any] | None = None,
        auto_initialize: bool = True,
    ) -> None:
        """Register a plugin class with the registry.

        Args:
        ----
            name: Unique identifier for the plugin
            plugin_class: Plugin class that implements TestAPIXPlugin
            config: Optional configuration for plugin initialization
            auto_initialize: Whether to initialize the plugin immediately

        Raises:
        ------
            PluginError: If registration or initialization fails
            ValueError: If plugin name is already registered

        """
        if name in self._plugins:
            raise ValueError(
                f"{self._plugin_type_name} plugin '{name}' is already registered"
            )

        if not issubclass(plugin_class, TestAPIXPlugin):
            raise PluginError(
                f"Plugin class {plugin_class.__name__} must implement TestAPIXPlugin interface",
                plugin_name=name,
            )

        try:
            # Create plugin instance for metadata extraction
            temp_instance = plugin_class()
            metadata = PluginMetadata(
                name=name,
                version=temp_instance.version,
                description=temp_instance.description,
                plugin_class=plugin_class,
                dependencies=temp_instance.dependencies.copy(),
            )

            self._plugins[name] = metadata
            self._logger.info(
                f"Registered {self._plugin_type_name} plugin: {name} v{metadata.version}"
            )

            if auto_initialize:
                self._initialize_plugin(name, config or {})

            self._emit_event("plugin.registered", {"name": name, "metadata": metadata})

        except Exception as e:
            raise PluginError(
                f"Failed to register plugin '{name}': {e}", plugin_name=name
            ) from e

    def unregister(self, name: str) -> None:
        """Unregister a plugin and clean up its resources.

        Args:
        ----
            name: Name of the plugin to unregister

        Raises:
        ------
            PluginError: If plugin is not found or cleanup fails

        """
        if name not in self._plugins:
            raise PluginError(
                f"{self._plugin_type_name} plugin '{name}' is not registered",
                plugin_name=name,
            )

        metadata = self._plugins[name]

        try:
            # Cleanup plugin instance if it exists
            if metadata.instance:
                metadata.instance.cleanup()

            del self._plugins[name]
            self._logger.info(f"Unregistered {self._plugin_type_name} plugin: {name}")

            self._emit_event("plugin.unregistered", {"name": name})

        except Exception as e:
            raise PluginError(
                f"Failed to unregister plugin '{name}': {e}", plugin_name=name
            ) from e

    def get(self, name: str) -> T:
        """Get an initialized plugin instance by name.

        Args:
        ----
            name: Name of the plugin to retrieve

        Returns:
        -------
            The initialized plugin instance

        Raises:
        ------
            PluginError: If plugin is not found or not initialized

        """
        if name not in self._plugins:
            raise PluginError(
                f"{self._plugin_type_name} plugin '{name}' is not registered",
                plugin_name=name,
            )

        metadata = self._plugins[name]
        if not metadata.initialized or metadata.instance is None:
            raise PluginError(
                f"{self._plugin_type_name} plugin '{name}' is not initialized",
                plugin_name=name,
            )

        return metadata.instance  # type: ignore[return-value]

    def list_plugins(self) -> list[PluginMetadata]:
        """Return list of all registered plugin metadata."""
        return list(self._plugins.values())

    def is_registered(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins

    def is_initialized(self, name: str) -> bool:
        """Check if a plugin is registered and initialized."""
        return name in self._plugins and self._plugins[name].initialized

    def initialize_all(self, global_config: Mapping[str, Any] | None = None) -> None:
        """Initialize all registered plugins with dependency resolution.

        Args:
        ----
            global_config: Global configuration that may contain plugin-specific settings

        Raises:
        ------
            PluginError: If dependency resolution or initialization fails

        """
        global_config = global_config or {}
        initialization_order = self._resolve_dependencies()

        for name in initialization_order:
            if not self._plugins[name].initialized:
                plugin_config = global_config.get(name, {})
                self._initialize_plugin(name, plugin_config)

    def add_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """Add an event handler for plugin events.

        Args:
        ----
            event_type: Type of event to listen for (e.g., "plugin.registered")
            handler: Callable that will be invoked when the event occurs

        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """Remove an event handler."""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
            except ValueError:
                pass  # Handler wasn't in the list

    def _initialize_plugin(self, name: str, config: Mapping[str, Any]) -> None:
        """Initialize a single plugin with the given configuration."""
        metadata = self._plugins[name]

        try:
            # Create and initialize plugin instance
            instance = metadata.plugin_class()
            instance.initialize(config)

            metadata.instance = instance
            metadata.initialized = True

            self._logger.info(f"Initialized {self._plugin_type_name} plugin: {name}")
            self._emit_event("plugin.initialized", {"name": name, "config": config})

        except Exception as e:
            raise PluginError(
                f"Failed to initialize plugin '{name}': {e}", plugin_name=name
            ) from e

    def _resolve_dependencies(self) -> list[str]:
        """Resolve plugin dependencies and return initialization order.

        Returns
        -------
            List of plugin names in dependency-resolved order

        Raises
        ------
            PluginError: If circular dependencies are detected

        """
        # Topological sort to resolve dependencies
        visited = set()
        temp_visited = set()
        result: list[str] = []

        def visit(name: str) -> None:
            if name in temp_visited:
                raise PluginError(
                    f"Circular dependency detected involving plugin '{name}'"
                )

            if name not in visited:
                temp_visited.add(name)

                # Visit dependencies first
                if name in self._plugins:
                    for dep in self._plugins[name].dependencies:
                        if dep not in self._plugins:
                            raise PluginError(
                                f"Plugin '{name}' depends on unregistered plugin '{dep}'",
                                plugin_name=name,
                            )
                        visit(dep)

                temp_visited.remove(name)
                visited.add(name)
                result.append(name)

        # Visit all plugins
        for plugin_name in self._plugins:
            if plugin_name not in visited:
                visit(plugin_name)

        return result

    def _emit_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self._logger.warning(f"Event handler failed for {event_type}: {e}")


class GlobalPluginRegistry:
    """Global registry that manages all plugin types in TestAPIX.

    This provides a centralized access point for all plugin registries
    and supports configuration-driven plugin loading.
    """

    def __init__(self) -> None:
        self._registries: dict[str, PluginRegistry[Any]] = {}
        self._logger = logging.getLogger(__name__)

    def create_registry(self, plugin_type: str) -> PluginRegistry[Any]:
        """Create a new plugin registry for the given type.

        Args:
        ----
            plugin_type: Unique identifier for the plugin type

        Returns:
        -------
            New plugin registry instance

        Raises:
        ------
            ValueError: If registry type already exists

        """
        if plugin_type in self._registries:
            raise ValueError(f"Plugin registry for '{plugin_type}' already exists")

        registry: PluginRegistry[Any] = PluginRegistry(plugin_type)
        self._registries[plugin_type] = registry
        self._logger.info(f"Created plugin registry for: {plugin_type}")

        return registry

    def get_registry(self, plugin_type: str) -> PluginRegistry[Any]:
        """Get an existing plugin registry by type.

        Args:
        ----
            plugin_type: Type of plugin registry to retrieve

        Returns:
        -------
            The plugin registry instance

        Raises:
        ------
            KeyError: If registry type doesn't exist

        """
        if plugin_type not in self._registries:
            raise KeyError(f"No plugin registry found for type: {plugin_type}")

        return self._registries[plugin_type]

    def list_registry_types(self) -> list[str]:
        """Return list of all registered plugin types."""
        return list(self._registries.keys())

    def initialize_all_registries(
        self, config: Mapping[str, Any] | None = None
    ) -> None:
        """Initialize all plugins in all registries.

        Args:
        ----
            config: Global configuration that may contain plugin-specific settings

        """
        config = config or {}

        for plugin_type, registry in self._registries.items():
            try:
                registry_config = config.get(plugin_type, {})
                registry.initialize_all(registry_config)
                self._logger.info(
                    f"Initialized all plugins for registry: {plugin_type}"
                )
            except Exception as e:
                self._logger.error(
                    f"Failed to initialize plugins for {plugin_type}: {e}"
                )
                raise


# Global singleton instance
global_registry = GlobalPluginRegistry()
