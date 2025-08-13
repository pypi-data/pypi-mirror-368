import inspect
from typing import List, Optional


def infer_http_methods(func: callable, explicit_methods: Optional[List[str]] = None) -> List[str]:
    """
    Infer HTTP methods for a route based on function name and signature.
    
    If explicit methods are provided, they are returned as-is.
    Otherwise, methods are inferred from:
    1. Function name prefix (get_, post_, create_, etc.)
    2. Presence of body parameters (suggests POST/PUT)
    
    Args:
        func: The function to analyze
        explicit_methods: Explicitly specified methods, if any
        
    Returns:
        List of inferred HTTP methods
    """
    # If explicit methods are provided, use them
    if explicit_methods is not None:
        return [method.upper() for method in explicit_methods]
    
    # Get function name
    func_name = func.__name__
    
    # Infer from function name prefix
    name_based_method = _infer_from_name(func_name)
    if name_based_method:
        return [name_based_method]
    
    # Infer from function signature (body parameters)
    signature_based_methods = _infer_from_signature(func)
    if signature_based_methods:
        return signature_based_methods
    
    # Default to GET
    return ["GET"]


def _infer_from_name(func_name: str) -> Optional[str]:
    """
    Infer HTTP method from function name prefix.
    
    Args:
        func_name: Name of the function
        
    Returns:
        Inferred HTTP method or None if no match
    """
    # Direct mappings
    prefix_map = {
        'get_': 'GET',
        'post_': 'POST',
        'put_': 'PUT',
        'delete_': 'DELETE',
        'patch_': 'PATCH',
        'head_': 'HEAD',
        'options_': 'OPTIONS',
    }
    
    # Special cases
    if func_name.startswith('create_'):
        return 'POST'
    
    if func_name.startswith('update_'):
        return 'PUT'
    
    # Check standard prefixes
    for prefix, method in prefix_map.items():
        if func_name.startswith(prefix):
            return method
    
    return None


def _infer_from_signature(func: callable) -> List[str]:
    """
    Infer HTTP methods from function signature (body parameters).
    
    Args:
        func: The function to analyze
        
    Returns:
        List of inferred HTTP methods or empty list if no inference can be made
    """
    try:
        # Get function signature
        sig = inspect.signature(func)
        parameters = sig.parameters
        
        # Look for body parameters (parameters that are not typical path/query params)
        body_param_count = 0
        for param_name, param in parameters.items():
            # Skip typical path/query parameters
            if param_name in ('request', 'id', 'user_id', 'pk'):
                continue
                
            # Count non-default parameters (likely body parameters)
            if param.default == inspect.Parameter.empty:
                body_param_count += 1
                    
        # If we have body parameters, suggest POST
        if body_param_count > 0:
            return ['POST']
        
        # No body parameters found
        return []
        
    except Exception:
        # If we can't analyze the signature, return empty list
        return []