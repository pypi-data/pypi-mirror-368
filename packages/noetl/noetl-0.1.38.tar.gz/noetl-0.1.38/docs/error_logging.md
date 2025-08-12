# Error Logging in NoETL

This document describes the error logging functionality in NoETL, which allows for capturing and storing detailed information about errors that occur during template rendering and other operations.

## Overview

NoETL now includes a dedicated `error_log` table in the NoETL meta schema that stores comprehensive information about errors, including:

- Error type and message
- Execution context (execution_id, step_id, step_name)
- Template information (template string, context data)
- Stack trace
- Input and output data
- Severity
- Resolution status and notes

This functionality is particularly useful for debugging template rendering errors, which can be difficult to diagnose without detailed context information.

## Error Log Table Schema

The `error_log` table has the following schema:

```sql
CREATE TABLE IF NOT EXISTS noetl.error_log (
    error_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_type VARCHAR(50),
    error_message TEXT,
    execution_id VARCHAR,
    step_id VARCHAR,
    step_name VARCHAR,
    template_string TEXT,
    context_data JSONB,
    stack_trace TEXT,
    input_data JSONB,
    output_data JSONB,
    severity VARCHAR(20) DEFAULT 'error',
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    resolution_timestamp TIMESTAMP
)
```

Indexes are created on `timestamp`, `error_type`, `execution_id`, and `resolved` columns for efficient querying.

## Logging Errors

Errors are automatically logged to the `error_log` table when they occur during template rendering. The following error types are currently logged:

- `template_rendering`: Errors that occur when rendering Jinja2 templates
- `sql_template_rendering`: Errors that occur when rendering SQL templates

You can also log errors manually using the `log_error` method of the `DatabaseSchema` class:

```python
from noetl.schema import DatabaseSchema

db_schema = DatabaseSchema()
db_schema.log_error(
    error_type="custom_error",
    error_message="An error occurred",
    execution_id="execution_123",
    step_id="step_456",
    step_name="my_step",
    template_string="Template that caused the error",
    context_data={"key": "value"},
    stack_trace="Stack trace of the error",
    input_data={"input": "data"},
    output_data={"output": "data"},
    severity="error"
)
```

## Querying Errors

You can query errors from the `error_log` table using the `get_errors` method of the `DatabaseSchema` class:

```python
from noetl.schema import DatabaseSchema

db_schema = DatabaseSchema()

# Get all errors
all_errors = db_schema.get_errors()

# Get errors of a specific type
template_errors = db_schema.get_errors(error_type="template_rendering")

# Get errors for a specific execution
execution_errors = db_schema.get_errors(execution_id="execution_123")

# Get unresolved errors
unresolved_errors = db_schema.get_errors(resolved=False)

# Get errors with pagination
paginated_errors = db_schema.get_errors(limit=10, offset=20)
```

You can also query the `error_log` table directly using SQL:

```sql
-- Get all errors
SELECT * FROM noetl.error_log ORDER BY timestamp DESC;

-- Get errors of a specific type
SELECT * FROM noetl.error_log WHERE error_type = 'template_rendering' ORDER BY timestamp DESC;

-- Get errors for a specific execution
SELECT * FROM noetl.error_log WHERE execution_id = 'execution_123' ORDER BY timestamp DESC;

-- Get unresolved errors
SELECT * FROM noetl.error_log WHERE resolved = FALSE ORDER BY timestamp DESC;
```

## Marking Errors as Resolved

You can mark errors as resolved using the `mark_error_resolved` method of the `DatabaseSchema` class:

```python
from noetl.schema import DatabaseSchema

db_schema = DatabaseSchema()
db_schema.mark_error_resolved(
    error_id=123,
    resolution_notes="Fixed by updating the template"
)
```

You can also mark errors as resolved directly using SQL:

```sql
UPDATE noetl.error_log
SET resolved = TRUE,
    resolution_notes = 'Fixed by updating the template',
    resolution_timestamp = CURRENT_TIMESTAMP
WHERE error_id = 123;
```

## Best Practices

1. **Review errors regularly**: Set up a process to regularly review unresolved errors in the `error_log` table.

2. **Add resolution notes**: When resolving an error, add detailed notes about how it was resolved to help with future troubleshooting.

3. **Use error_type for categorization**: Use consistent error types to categorize errors, which makes it easier to filter and analyze them.

4. **Include context information**: When logging custom errors, include as much context information as possible to help with debugging.

5. **Clean up old errors**: Consider implementing a process to archive or delete old resolved errors to prevent the `error_log` table from growing too large.

## Example: Debugging Template Rendering Errors

Here's an example of how to use the error logging functionality to debug template rendering errors:

1. Run your workflow and notice that a template rendering error occurs.

2. Query the `error_log` table to get detailed information about the error:

```python
from noetl.schema import DatabaseSchema

db_schema = DatabaseSchema()
errors = db_schema.get_errors(error_type="template_rendering", resolved=False)

for error in errors:
    print(f"Error ID: {error['error_id']}")
    print(f"Error Message: {error['error_message']}")
    print(f"Template: {error['template_string']}")
    print(f"Context Data: {error['context_data']}")
    print(f"Stack Trace: {error['stack_trace']}")
    print(f"Input Data: {error['input_data']}")
    print("---")
```

3. Use the detailed information to diagnose and fix the error.

4. Mark the error as resolved:

```python
db_schema.mark_error_resolved(
    error_id=errors[0]['error_id'],
    resolution_notes="Fixed by updating the template to use the correct variable name"
)
```

5. Run your workflow again to verify that the error is resolved.

## Conclusion

The error logging functionality in NoETL provides a powerful way to capture, store, and analyze errors that occur during template rendering and other operations. By using this functionality, you can more easily diagnose and fix errors, leading to more robust and reliable workflows.