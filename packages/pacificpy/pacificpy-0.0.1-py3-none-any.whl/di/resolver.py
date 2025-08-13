"""
Dependency Injection: Resolver
"""
import asyncio
import inspect
from typing import Any, Dict, Callable, get_type_hints
from .dependency import Depends, Dependency
from .cache import DependencyCache

class DependencyResolver:
    """
    Resolves dependencies recursively, supporting both sync and async dependencies.
    Uses per-request caching to ensure dependencies are only resolved once per request.
    """
    
    def __init__(self):
        pass
    
    async def resolve_dependencies(
        self, 
        callable_obj: Callable, 
        cache: DependencyCache,
        dependency_overrides: Dict[Callable, Callable] = None
    ) -> Dict[str, Any]:
        """
        Recursively resolve all dependencies for a callable.
        
        Args:
            callable_obj: The callable (function or class) to resolve dependencies for
            cache: The per-request cache for dependency resolution
            dependency_overrides: Optional dictionary of dependency overrides for testing
            
        Returns:
            Dictionary of resolved dependencies keyed by parameter name
        """
        if dependency_overrides is None:
            dependency_overrides = {}
            
        # Get function signature
        sig = inspect.signature(callable_obj)
        resolved = {}
        
        # Resolve each parameter
        for param_name, param in sig.parameters.items():
            # Check if parameter has a Depends annotation
            dependency = None
            if isinstance(param.annotation, Depends):
                dependency = param.annotation
            elif isinstance(param.default, Depends):
                dependency = param.default
                
            # If we found a dependency, resolve it
            if dependency:
                dep_callable = dependency.dependency.callable_or_class
                
                # Check for override
                if dep_callable in dependency_overrides:
                    override = dependency_overrides[dep_callable]
                    resolved[param_name] = await self._resolve_callable(
                        override, cache, dependency_overrides
                    )
                else:
                    # Resolve the dependency
                    resolved[param_name] = await self._resolve_dependency(
                        dependency.dependency, cache, dependency_overrides
                    )
                    
        return resolved
    
    async def _resolve_dependency(
        self, 
        dependency: Dependency, 
        cache: DependencyCache,
        dependency_overrides: Dict[Callable, Callable]
    ) -> Any:
        """
        Resolve a single dependency, using cache if appropriate.
        """
        # Check cache first if caching is enabled
        if dependency.use_cache:
            cached_value = cache.get(dependency.callable_or_class)
            if cached_value is not DependencyCache.NOT_FOUND:
                return cached_value
        
        # Resolve the dependency
        result = await self._resolve_callable(
            dependency.callable_or_class, cache, dependency_overrides
        )
        
        # Cache the result if caching is enabled
        if dependency.use_cache:
            cache.set(dependency.callable_or_class, result)
            
        return result
    
    async def _resolve_callable(
        self, 
        callable_obj: Callable, 
        cache: DependencyCache,
        dependency_overrides: Dict[Callable, Callable]
    ) -> Any:
        """
        Resolve a callable (function or class), handling both sync and async cases.
        """
        # First resolve its own dependencies
        sub_dependencies = await self.resolve_dependencies(
            callable_obj, cache, dependency_overrides
        )
        
        # Check if it's a class
        if inspect.isclass(callable_obj):
            # For classes, we instantiate with resolved dependencies
            if asyncio.iscoroutinefunction(callable_obj):
                return await callable_obj(**sub_dependencies)
            else:
                return callable_obj(**sub_dependencies)
        
        # For functions, we call them with resolved dependencies
        if asyncio.iscoroutinefunction(callable_obj):
            return await callable_obj(**sub_dependencies)
        else:
            return callable_obj(**sub_dependencies)