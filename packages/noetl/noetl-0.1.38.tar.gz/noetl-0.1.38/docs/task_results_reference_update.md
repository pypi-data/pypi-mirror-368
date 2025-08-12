# Task Results Reference Guide

## Overview

This document provides guidance on how to properly reference task results in templates within NoETL workflows. It addresses common issues and provides best practices for accessing data from different task types.

## Task Result Structure

When a task is executed in NoETL, it returns a result with the following structure:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        // Task-specific data structure
    }
}
```

The `data` field contains the task-specific results, which vary depending on the task type.

## Different Task Types, Different Reference Patterns

One of the most important things to understand is that different task types store their results in different ways:

### HTTP Tasks

HTTP tasks store their results directly in the `data` attribute:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "property1": "value1",
        "property2": "value2",
        // HTTP response body
    }
}
```

To reference HTTP task results in templates, use:

```
{{ step_name.data.property_name }}
```

For example:
```
{{ fetch_github_repo.data.name }}
{{ fetch_github_repo.data.stargazers_count }}
```

### Database Tasks (DuckDB and Postgres)

Database tasks store their results in a more structured format, with each SQL command's results indexed by command number:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "command_0": {
            "status": "success",
            "rows": [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"}
            ],
            "row_count": 2,
            "columns": ["column1", "column2"]
        },
        "command_1": {
            // Results of the second command
        }
    }
}
```

To reference database task results in templates, you can use either:

```
{{ step_name.result.command_X.rows }}  // Recommended
```

or

```
{{ step_name.data.command_X.rows }}    // Alternative
```

For example:
```
{{ extract_repo_metrics.result.command_1.rows }}
{{ query_and_analyze.result.command_10.rows }}
```

## Common Issues and Solutions

### Issue: Template Rendering Errors

You might encounter template rendering errors like:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ step_name.data.command_X.rows }}
```

or

```
Template rendering error: 'dict object' has no attribute 'result', template: {{ step_name.result.command_X.rows }}
```

### Solution: Provide Both Reference Patterns

To handle both cases, you can provide both reference patterns in your YAML file:

```yaml
- step: next_step
  with:
    # Primary option using result attribute
    data_from_previous: "{{ previous_step.result.command_0.rows }}"
    # Fallback option using data attribute
    data_from_previous_alt: "{{ previous_step.data.command_0.rows if previous_step.data is defined else [] }}"
```

Then, in your Python code, check both options:

```python
data = context.get('data_from_previous', [])
data_alt = context.get('data_from_previous_alt', [])

# Use alternative if primary is empty or didn't resolve
if not data or (isinstance(data, str) and ('{{' in data or '}}' in data)):
    if data_alt and not (isinstance(data_alt, str) and ('{{' in data_alt or '}}' in data_alt)):
        data = data_alt
```

### Issue: Command Indexing

Another common issue is determining the correct command index. Commands are indexed starting from 0, but the actual index assigned to each command may vary depending on how the commands are parsed and executed.

### Solution: Check Logs for Actual Command Index

To determine the correct command index:

1. Run the workflow and check the logs
2. Look for log entries that show the step result data structure
3. Identify the actual command index used for the data you want to reference

For example, you might see a log entry like:

```
BROKER.EXECUTE_STEP: Updated context key=query_and_analyze, value={'command_10': {'status': 'success', 'rows': [{'repo_name': 'vscode', ...}], ...}}
```

This indicates that the data is stored under `command_10` rather than `command_0`.

## Best Practices

1. **Add Debug Output**: Include debug output in your Python code to show the actual data structure received:

```python
print(f"Data type: {type(data)}")
print(f"Data value: {data}")
```

2. **Add Type Checking**: Always check the type of data before trying to access its properties:

```python
if isinstance(data, dict):
    value = data.get('property', default_value)
elif isinstance(data, list) and data and isinstance(data[0], dict):
    value = data[0].get('property', default_value)
else:
    # Handle error case
```

3. **Provide Fallback Options**: As shown above, provide multiple reference patterns to handle different cases.

4. **Document Reference Patterns**: In your YAML files, add comments explaining which reference pattern to use for which task type.

## Summary

- **HTTP Tasks**: Use `{{ step_name.data.property_name }}`
- **Database Tasks**: Use `{{ step_name.result.command_X.rows }}` or `{{ step_name.data.command_X.rows }}`
- **Add Fallbacks**: Provide both reference patterns to handle different cases
- **Add Type Checking**: Always check the type of data before accessing its properties
- **Check Logs**: Look at the logs to determine the correct command index and data structure

By following these guidelines, you can avoid common issues with referencing task results in templates and make your workflows more robust.