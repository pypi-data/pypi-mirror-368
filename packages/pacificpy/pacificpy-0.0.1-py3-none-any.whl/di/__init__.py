"""
Dependency Injection package
"""
from .dependency import Depends, Dependency
from .resolver import DependencyResolver
from .cache import DependencyCache
from .binder import HandlerBinder
from .testing import override_dependencies, set_app_dependency_override, clear_app_dependency_overrides, get_app_dependency_overrides
from .lifecycle import LifecycleManager
from .typing import TypeValidationError

__all__ = [
    "Depends",
    "Dependency",
    "DependencyResolver",
    "DependencyCache",
    "HandlerBinder",
    "override_dependencies",
    "set_app_dependency_override",
    "clear_app_dependency_overrides",
    "get_app_dependency_overrides",
    "LifecycleManager",
    "TypeValidationError"
]