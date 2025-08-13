import os
import importlib
import importlib.util
from typing import List, Optional
import logging

from .route import Route
from .router import APIRouter

logger = logging.getLogger(__name__)


def discover_endpoints(path: str, package: Optional[str] = None) -> APIRouter:
    """
    Scan a directory for endpoint files and register @route decorated functions.
    
    Args:
        path: Path to directory containing endpoint files
        package: Optional package name for relative imports
        
    Returns:
        APIRouter with discovered routes
        
    Example:
        If examples/demo/endpoints/ contains users.py with a @route("/users") 
        function, that route will be registered in the returned router.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Endpoint directory not found: {path}")
        
    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path}")
    
    router = APIRouter()
    discovered_files = []
    
    # Scan directory for Python files
    for filename in os.listdir(path):
        # Skip files starting with underscore
        if filename.startswith('_'):
            continue
            
        # Only process .py files
        if not filename.endswith('.py'):
            continue
            
        file_path = os.path.join(path, filename)
        if not os.path.isfile(file_path):
            continue
            
        module_name = filename[:-3]  # Remove .py extension
        discovered_files.append((file_path, module_name))
    
    # Import each file and discover routes
    for file_path, module_name in discovered_files:
        try:
            # Import the module
            module = _import_module(file_path, module_name, package)
            
            # Find @route decorated functions
            routes = _find_route_decorated_functions(module)
            
            # Add routes to router
            for route in routes:
                router.add_route(route)
                
            logger.debug(f"Discovered {len(routes)} routes from {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to import or process {file_path}: {e}")
            continue
    
    return router


def _import_module(file_path: str, module_name: str, package: Optional[str] = None):
    """
    Import a Python module from a file path.
    
    Args:
        file_path: Path to the Python file
        module_name: Name to give the module
        package: Optional package name for relative imports
        
    Returns:
        Imported module
    """
    # If package is specified, use relative import
    if package:
        full_module_name = f"{package}.{module_name}"
        spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    else:
        # Use absolute import
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
    if spec is None:
        raise ImportError(f"Could not create spec for {file_path}")
        
    module = importlib.util.module_from_spec(spec)
    
    # Execute the module
    spec.loader.exec_module(module)
    
    return module


def _find_route_decorated_functions(module) -> List[Route]:
    """
    Find functions in a module decorated with @route.
    
    Args:
        module: Module to search
        
    Returns:
        List of Route objects
    """
    routes = []
    
    # Get all attributes of the module
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        
        # Check if attribute is a function with _route attribute
        if callable(attr) and hasattr(attr, '_route'):
            route = attr._route
            if isinstance(route, Route):
                routes.append(route)
    
    return routes