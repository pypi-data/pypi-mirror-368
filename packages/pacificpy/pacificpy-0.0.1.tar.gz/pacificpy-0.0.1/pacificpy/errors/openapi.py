"""
OpenAPI error documentation.

This module provides utilities for automatically documenting
standard error responses in OpenAPI specifications.
"""

from typing import Dict, Any

# Standard error responses for OpenAPI documentation
STANDARD_ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "oneOf": [
                                {"type": "string"},
                                {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "loc": {"type": "array", "items": {"type": "string"}},
                                            "msg": {"type": "string"},
                                            "type": {"type": "string"}
                                        }
                                    }
                                }
                            ]
                        },
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    405: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    409: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    422: {
        "description": "Unprocessable Entity",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "loc": {"type": "array", "items": {"type": "string"}},
                                    "msg": {"type": "string"},
                                    "type": {"type": "string"}
                                }
                            }
                        },
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    429: {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    502: {
        "description": "Bad Gateway",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    },
    503: {
        "description": "Service Unavailable",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "trace_id": {"type": "string"}
                    }
                }
            }
        }
    }
}

def add_standard_error_responses(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add standard error responses to an OpenAPI schema.
    
    Args:
        openapi_schema: The OpenAPI schema to modify
        
    Returns:
        The modified OpenAPI schema
    """
    # Ensure paths exist in the schema
    if "paths" not in openapi_schema:
        openapi_schema["paths"] = {}
    
    # Add standard responses to each path operation
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if isinstance(operation, dict):
                # Ensure responses exist
                if "responses" not in operation:
                    operation["responses"] = {}
                
                # Add standard error responses
                for status_code, response in STANDARD_ERROR_RESPONSES.items():
                    # Only add if not already defined
                    if str(status_code) not in operation["responses"]:
                        operation["responses"][str(status_code)] = response
    
    return openapi_schema