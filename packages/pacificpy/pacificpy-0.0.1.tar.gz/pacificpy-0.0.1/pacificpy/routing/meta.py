from typing import Any, Dict, List, Optional, Union


class OpenAPIMetadata:
    """
    OpenAPI metadata for a route.
    
    Collects metadata like summary, description, tags, and responses
    that can be used for OpenAPI documentation generation.
    """
    
    def __init__(
        self,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize OpenAPI metadata.
        
        Args:
            summary: Short summary of what the route does
            description: Detailed description of the route
            tags: Tags for grouping operations
            responses: Response definitions
        """
        self.summary = summary
        self.description = description
        self.tags = tags or []
        self.responses = responses or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary format.
        
        Returns:
            Dictionary representation of the metadata
        """
        result = {}
        
        if self.summary:
            result["summary"] = self.summary
            
        if self.description:
            result["description"] = self.description
            
        if self.tags:
            result["tags"] = self.tags
            
        if self.responses:
            result["responses"] = self.responses
            
        return result


def collect_openapi_metadata(
    func: callable,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
) -> OpenAPIMetadata:
    """
    Collect OpenAPI metadata from function and explicit parameters.
    
    Args:
        func: The function to collect metadata from
        summary: Explicit summary
        description: Explicit description
        tags: Explicit tags
        responses: Explicit responses
        
    Returns:
        OpenAPIMetadata object
    """
    # Use explicit values or fall back to function attributes
    final_summary = summary or getattr(func, '__openapi_summary__', None)
    final_description = description or getattr(func, '__doc__', None)
    final_tags = tags or getattr(func, '__openapi_tags__', [])
    final_responses = responses or getattr(func, '__openapi_responses__', {})
    
    # If no explicit summary, try to generate from function name
    if not final_summary:
        final_summary = _generate_summary_from_name(func.__name__)
    
    return OpenAPIMetadata(
        summary=final_summary,
        description=final_description,
        tags=final_tags,
        responses=final_responses
    )


def _generate_summary_from_name(func_name: str) -> str:
    """
    Generate a summary from a function name.
    
    Args:
        func_name: Name of the function
        
    Returns:
        Generated summary
    """
    # Replace underscores with spaces and capitalize
    summary = func_name.replace('_', ' ')
    
    # Capitalize first letter
    if summary:
        summary = summary[0].upper() + summary[1:]
        
    return summary


def merge_openapi_metadata(
    base_metadata: Optional[OpenAPIMetadata],
    additional_metadata: Optional[OpenAPIMetadata]
) -> OpenAPIMetadata:
    """
    Merge two OpenAPI metadata objects.
    
    Args:
        base_metadata: Base metadata
        additional_metadata: Additional metadata to merge
        
    Returns:
        Merged metadata
    """
    if not base_metadata:
        return additional_metadata or OpenAPIMetadata()
        
    if not additional_metadata:
        return base_metadata
        
    # Merge tags (avoid duplicates)
    merged_tags = list(set(base_metadata.tags + additional_metadata.tags))
    
    # Merge responses (additional overrides base)
    merged_responses = {**base_metadata.responses, **additional_metadata.responses}
    
    return OpenAPIMetadata(
        summary=additional_metadata.summary or base_metadata.summary,
        description=additional_metadata.description or base_metadata.description,
        tags=merged_tags,
        responses=merged_responses
    )