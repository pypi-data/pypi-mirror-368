"""
Template components and layouts for PacificPy.

This module provides utilities for simplifying component reuse
and documenting best practices for template layouts.
"""

from typing import Dict, Any, Optional, Callable
from jinja2 import Environment, Template

class Component:
    """Base class for template components."""
    
    def __init__(self, name: str, template: str):
        """
        Initialize a component.
        
        Args:
            name: The name of the component
            template: The template string for the component
        """
        self.name = name
        self.template = template
        self.env: Optional[Environment] = None
    
    def render(self, context: Dict[str, Any] = None) -> str:
        """
        Render the component with context.
        
        Args:
            context: The context to render with
            
        Returns:
            The rendered component
        """
        if not self.env:
            raise RuntimeError("Component environment not set")
        
        template = self.env.from_string(self.template)
        return template.render(context or {})
    
    def register(self, env: Environment) -> None:
        """
        Register the component with a Jinja2 environment.
        
        Args:
            env: The Jinja2 environment
        """
        self.env = env
        
        # Add component as a global function
        env.globals[self.name] = self.render

# Component registry
_components: Dict[str, Component] = {}

def register_component(component: Component, env: Environment) -> None:
    """
    Register a component with an environment.
    
    Args:
        component: The component to register
        env: The Jinja2 environment
    """
    component.register(env)
    _components[component.name] = component

def get_component(name: str) -> Optional[Component]:
    """
    Get a registered component by name.
    
    Args:
        name: The name of the component
        
    Returns:
        The component, or None if not found
    """
    return _components.get(name)

# Built-in components
def create_alert_component() -> Component:
    """Create a reusable alert component."""
    return Component("alert", """
<div class="alert alert-{{ level | default('info') }}" role="alert">
    {{ message }}
</div>
""")

def create_card_component() -> Component:
    """Create a reusable card component."""
    return Component("card", """
<div class="card">
    {% if title %}
    <div class="card-header">
        <h5 class="card-title">{{ title }}</h5>
    </div>
    {% endif %}
    <div class="card-body">
        {{ content | safe }}
    </div>
    {% if footer %}
    <div class="card-footer">
        {{ footer }}
    </div>
    {% endif %}
</div>
""")

def create_button_component() -> Component:
    """Create a reusable button component."""
    return Component("button", """
<button type="{{ type | default('button') }}" 
        class="btn btn-{{ variant | default('primary') }} {{ class | default('') }}"
        {% if disabled %}disabled{% endif %}>
    {{ text }}
</button>
""")

# Layout utilities
def extend_base_template(template_name: str, block_name: str = "content") -> str:
    """
    Create a template that extends a base template.
    
    Args:
        template_name: The name of the base template
        block_name: The name of the block to fill
        
    Returns:
        A template string that extends the base template
    """
    return f"""{{% extends "{template_name}" %}}
{{% block {block_name} %}}
{{% endblock %}}"""

# Best practices documentation
BEST_PRACTICES = """
Template Layout Best Practices:

1. Use a base template with defined blocks:
   - Define consistent page structure in base.html
   - Use named blocks for content areas (header, content, footer)

2. Componentize reusable elements:
   - Create components for alerts, cards, buttons, forms
   - Use macros or custom components for complex reusable parts

3. Separate concerns:
   - Keep logic in Python, not templates
   - Use context processors for global data
   - Use filters for data transformation

4. Security:
   - Always escape user input
   - Use safe filters only when necessary
   - Validate data before rendering

5. Performance:
   - Minimize template inheritance depth
   - Use template caching in production
   - Avoid complex logic in templates

6. Maintainability:
   - Use consistent naming conventions
   - Document complex templates
   - Keep templates focused on presentation
"""

# Example usage function
def setup_default_components(env: Environment) -> None:
    """
    Set up default components with an environment.
    
    Args:
        env: The Jinja2 environment
    """
    # Register built-in components
    components = [
        create_alert_component(),
        create_card_component(),
        create_button_component(),
    ]
    
    for component in components:
        register_component(component, env)