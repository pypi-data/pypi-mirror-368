# b64encode Filter Implementation

## Issue Description

The NoETL system was encountering an error when trying to use the `b64encode` filter in Jinja2 templates:

```
[ERROR] 2025-07-30T21:21:42,319 (noetl.render:render_template:63) - Template rendering error: No filter named 'b64encode' found., template: INSERT INTO api_results (execution_id, source, result)
```

This error occurred when the Amadeus API playbook tried to encode markdown text to base64 for storage in PostgreSQL JSONB fields.

## Solution

The solution was implemented in two parts:

1. First, we added the `b64encode` filter to the Jinja2 environment in the `worker.py` file.
2. Then, we enhanced the solution by adding a helper function in `render.py` to ensure all Jinja2 environments have the filter available.

This filter converts input to a string if needed, encodes it to bytes, applies base64 encoding, and then decodes back to a UTF-8 string.

### Implementation

#### Initial Fix in worker.py

The filter was initially added to the Jinja2 environment in the `Worker.__init__` method in `worker.py`. Here's a conceptual example of how it was implemented:

```python
# Conceptual implementation in worker.py
from jinja2 import Environment
import base64

# Create a Jinja2 environment
jinja_environment = Environment()

# Add the b64encode filter
jinja_environment.filters['b64encode'] = lambda s: base64.b64encode(s.encode('utf-8')).decode('utf-8') \
    if isinstance(s, str) else base64.b64encode(str(s).encode('utf-8')).decode('utf-8')
```

#### Enhanced Solution in render.py

To ensure all Jinja2 environments have the filter available, we added a helper function in `render.py`. Here's a conceptual example of the implementation:

```python
# Conceptual implementation in render.py
import base64
from jinja2 import Environment

def add_b64encode_filter(jinja_env):
    """
    Add the b64encode filter to a Jinja2 environment.
    
    Args:
        jinja_env: The Jinja2 environment
        
    Returns:
        The Jinja2 environment with the b64encode filter added
    """
    if 'b64encode' not in jinja_env.filters:
        jinja_env.filters['b64encode'] = lambda s: base64.b64encode(s.encode('utf-8')).decode('utf-8') \
            if isinstance(s, str) else base64.b64encode(str(s).encode('utf-8')).decode('utf-8')
    return jinja_env
```

We then updated the `render_template` and `render_sql_template` functions to use this helper:

```python
# Conceptual implementation in render.py
def render_template(jinja_env, template, context, rules=None):
    """NoETL Jinja2 rendering."""
    # Ensure the environment has the b64encode filter
    if 'b64encode' not in jinja_env.filters:
        # Add the filter using the helper function
        import base64
        jinja_env.filters['b64encode'] = lambda s: base64.b64encode(s.encode('utf-8')).decode('utf-8') \
            if isinstance(s, str) else base64.b64encode(str(s).encode('utf-8')).decode('utf-8')
    
    # Continue with template rendering
    # ...
```

Similarly for the SQL template rendering function:

```python
# Conceptual implementation in render.py
def render_sql_template(jinja_env, sql_template, context):
    """Render SQL template while preserving comments."""
    # Ensure the environment has the b64encode filter
    if 'b64encode' not in jinja_env.filters:
        # Add the filter
        import base64
        jinja_env.filters['b64encode'] = lambda s: base64.b64encode(s.encode('utf-8')).decode('utf-8') \
            if isinstance(s, str) else base64.b64encode(str(s).encode('utf-8')).decode('utf-8')
    
    # Continue with SQL template rendering
    # ...
```

This implementation:
1. Checks if the input is a string
2. If it is a string, encodes it to UTF-8 bytes, applies base64 encoding, and decodes back to a UTF-8 string
3. If it's not a string, converts it to a string first, then follows the same process

## Usage

The filter can be used in Jinja2 templates like this:

```jinja
{{ some_variable | b64encode }}
```

This is particularly useful when storing markdown text or other content that might contain special characters in PostgreSQL JSONB fields.

## Related Files

- `/Users/kadyapam/projects/noetl/noetl/noetl/worker.py` - Initially modified to add the b64encode filter
- `/Users/kadyapam/projects/noetl/noetl/noetl/render.py` - Enhanced with a helper function to ensure all Jinja2 environments have the b64encode filter
- `/Users/kadyapam/projects/noetl/noetl/examples/amadeus/amadeus_api_playbook.yaml` - Uses the b64encode filter to encode markdown text
- `/Users/kadyapam/projects/noetl/noetl/debug_templates.py` - Updated to use the add_b64encode_filter helper

## Date Fixed

2025-07-30