# Templating Guide for PacificPy

This guide covers templating in PacificPy, including best practices and security considerations.

## Overview

PacificPy uses Jinja2 as its template engine, providing a powerful and flexible way to generate HTML, XML, and other text-based formats.

## Basic Usage

### Template Engine Setup

```python
from pacificpy.templates.engine import configure_templates

# Configure the template engine
template_engine = configure_templates(
    template_dir="templates",
    autoescape=True,
    enable_async=True
)
```

### Rendering Templates

```python
from pacificpy.templates.engine import render_template, render_response

# Render a template to a string
html = render_template("index.html", {"name": "World"})

# Render a template to an HTMLResponse
@app.get("/")
async def homepage(request):
    return render_response("index.html", {"name": "World"}, request)
```

## Template Inheritance

Use template inheritance to create consistent layouts:

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My App{% endblock %}</title>
</head>
<body>
    <header>
        <!-- Header content -->
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <!-- Footer content -->
    </footer>
</body>
</html>
```

```html
<!-- index.html -->
{% extends "base.html" %}

{% block title %}Home - My App{% endblock %}

{% block content %}
<h1>Welcome to My App</h1>
<p>Hello, {{ user.name }}!</p>
{% endblock %}
```

## Context Processors

Context processors add global variables to all templates:

```python
from pacificpy.templates.context import register_context_processor

@register_context_processor
def user_processor(request):
    return {
        "current_user": getattr(request.state, "user", None),
        "is_logged_in": getattr(request.state, "user", None) is not None
    }
```

## Template Filters

PacificPy provides several built-in filters for common tasks:

```html
<!-- Date formatting -->
<p>Created: {{ user.created_at | format_date }}</p>

<!-- JSON serialization -->
<script>
var userData = {{ user | safe_json }};
</script>

<!-- JavaScript escaping -->
<script>
var message = "{{ message | escape_js }}";
</script>

<!-- URL encoding -->
<a href="/search?q={{ query | urlencode }}">Search</a>
```

### Custom Filters

```python
from pacificpy.templates.filters import template_filter

@template_filter("truncate_words")
def truncate_words(text, length):
    words = text.split()
    if len(words) <= length:
        return text
    return " ".join(words[:length]) + "..."
```

## Form Helpers

PacificPy provides form helpers for creating secure forms:

```html
<!-- Login form with CSRF protection -->
<form method="POST">
    {{ form.hidden_csrf_token() | safe }}
    
    <div class="form-group">
        <label for="username">Username</label>
        <input type="text" name="username" id="username" required>
    </div>
    
    <div class="form-group">
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
    </div>
    
    <button type="submit">Login</button>
</form>
```

## Components

Create reusable components for common UI elements:

```python
from pacificpy.templates.components import Component, register_component

# Create a component
alert_component = Component("alert", """
<div class="alert alert-{{ level | default('info') }}" role="alert">
    {{ message }}
</div>
""")

# Register the component
register_component(alert_component, template_engine.env)
```

```html
<!-- Use the component -->
{{ alert(message="This is an info message", level="info") }}
{{ alert(message="This is a warning", level="warning") }}
{{ alert(message="This is an error", level="danger") }}
```

## Security Best Practices

### 1. Automatic Escaping

PacificPy enables autoescaping by default to prevent XSS attacks:

```python
# Template engine with autoescape enabled (default)
template_engine = configure_templates(autoescape=True)
```

### 2. Safe Usage of User Data

Always escape user-provided data:

```html
<!-- Good: Autoescaped by default -->
<p>User name: {{ user.name }}</p>

<!-- Good: Explicit escaping -->
<p>User bio: {{ user.bio | e }}</p>

<!-- Dangerous: Only use |safe when absolutely necessary -->
<p>User content: {{ user.content | safe }}</p>
```

### 3. JavaScript Context Safety

Use the `escape_js` filter for JavaScript contexts:

```html
<!-- Good: Safe JavaScript variable -->
<script>
var userName = "{{ user.name | escape_js }}";
</script>

<!-- Bad: Vulnerable to XSS -->
<script>
var userName = "{{ user.name }}";
</script>
```

### 4. JSON Data Serialization

Use the `safe_json` filter for JSON data:

```html
<!-- Good: Safe JSON serialization -->
<script>
var userData = {{ user | safe_json }};
</script>

<!-- Bad: Vulnerable to XSS -->
<script>
var userData = {{ user | tojson }};
</script>
```

### 5. URL Safety

Use the `urlencode` filter for URL parameters:

```html
<!-- Good: Safe URL encoding -->
<a href="/search?q={{ query | urlencode }}">Search</a>

<!-- Bad: Potentially unsafe -->
<a href="/search?q={{ query }}">Search</a>
```

## CSRF Protection

PacificPy automatically includes CSRF protection in forms:

```html
<!-- Form with CSRF protection -->
<form method="POST">
    {{ form.hidden_csrf_token() | safe }}
    <!-- Form fields -->
</form>
```

## Static Files

Serve static files with proper caching and security:

```python
from pacificpy.templates.static import static_files_middleware

# Add static files middleware
app.add_middleware(
    static_files_middleware,
    static_dir="static",
    path_prefix="/static",
    cache_max_age=3600
)
```

## Performance Optimization

### Template Caching

Enable template caching in production:

```python
# Configure template engine with caching
template_engine = TemplateEngine(
    template_dir="templates",
    autoescape=True,
    enable_async=True
)

# Jinja2 automatically caches templates
```

### Async Template Rendering

Use async template rendering for better performance:

```python
# Template engine with async enabled
template_engine = configure_templates(enable_async=True)

# Async template rendering
@app.get("/")
async def homepage(request):
    return await render_response("index.html", {"name": "World"}, request)
```

## Development Best Practices

### Template Auto-Reload

Enable auto-reload during development:

```python
from pacificpy.templates.dev import configure_template_reload

# Configure template auto-reload for development
if app.debug:
    configure_template_reload(app, template_dirs=["templates"])
```

### Error Handling

Provide user-friendly error pages:

```html
<!-- 404.html -->
{% extends "base.html" %}

{% block content %}
<h1>Page Not Found</h1>
<p>The page you're looking for doesn't exist.</p>
<a href="/">Go Home</a>
{% endblock %}
```

```html
<!-- 500.html -->
{% extends "base.html" %}

{% block content %}
<h1>Server Error</h1>
<p>Something went wrong on our end.</p>
{% if trace_id %}
<p>Error ID: {{ trace_id }}</p>
{% endif %}
<a href="/">Go Home</a>
{% endblock %}
```

## Example Implementation

Here's a complete example of a PacificPy app with templating:

```python
from pacificpy import PacificPy
from pacificpy.templates.engine import configure_templates
from pacificpy.templates.context import register_default_context_processors
from pacificpy.templates.filters import register_filters

# Create app
app = PacificPy()

# Configure templates
template_engine = configure_templates("templates")
register_default_context_processors()
register_filters(template_engine.env)

# Add template engine to app state
app.state.template_engine = template_engine

@app.get("/")
async def homepage(request):
    return template_engine.render_response(
        "index.html", 
        {"title": "Home", "user": getattr(request.state, "user", None)}, 
        request
    )

if __name__ == "__main__":
    app.run()
```

This guide provides a comprehensive overview of templating in PacificPy with a focus on security and best practices. Always follow these guidelines to ensure your applications are secure and maintainable.