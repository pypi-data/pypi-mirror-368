# Referencing Task Results in Templates

This document provides guidance on how to properly reference task results in templates within NoETL workflows.

## Task Result Structure

When a task is executed in NoETL, it returns a result with the following structure:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "command_0": { ... },
        "command_1": { ... },
        ...
    }
}
```

For database tasks (DuckDB and Postgres), the `data` field contains the results of each SQL command executed, indexed by `command_0`, `command_1`, etc.

## Referencing Task Results in Templates

When referencing task results in templates (e.g., in the `with` attribute of a step), you should use the following pattern:

```
{{ step_name.data.command_X }}
```

Where:
- `step_name` is the name of the step that executed the task
- `data` is the field in the task result that contains the command results
- `command_X` is the specific command result you want to reference (e.g., `command_0`, `command_1`, etc.)

For example, to reference the result of the first command executed in a step named `extract_metrics`, you would use:

```
{{ extract_metrics.data.command_0 }}
```

## Example

Here's an example of how to reference task results in a workflow:

```yaml
- step: extract_metrics
  type: duckdb
  command: |
    -- First command
    SELECT * FROM metrics;
    
    -- Second command
    SELECT COUNT(*) AS count FROM metrics;
  next:
    - step: process_metrics
      with:
        metrics: "{{ extract_metrics.data.command_0 }}"
        count: "{{ extract_metrics.data.command_1.rows[0].count }}"
```

In this example:
- `extract_metrics.data.command_0` references the result of the first SQL command
- `extract_metrics.data.command_1.rows[0].count` references the `count` field in the first row of the result of the second SQL command

## Accessing Specific Fields

For SELECT queries, the command result has the following structure:

```json
{
    "status": "success",
    "rows": [
        { "column1": "value1", "column2": "value2", ... },
        { "column1": "value3", "column2": "value4", ... },
        ...
    ],
    "row_count": 2,
    "columns": ["column1", "column2", ...]
}
```

To access specific fields in the result, you can use:

- `{{ step_name.data.command_X.rows }}` to access all rows
- `{{ step_name.data.command_X.rows[0] }}` to access the first row
- `{{ step_name.data.command_X.rows[0].column_name }}` to access a specific column in the first row
- `{{ step_name.data.command_X.row_count }}` to get the number of rows
- `{{ step_name.data.command_X.columns }}` to get the list of column names

## Backward Compatibility

For backward compatibility, NoETL also stores the task result data directly under the step name and under `step_name.result`. This means you can also reference task results using:

```
{{ step_name.command_X }}
```

or

```
{{ step_name.result.command_X }}
```

However, it's recommended to use the `step_name.data.command_X` pattern for clarity and consistency.

## Command Indexing

When referencing SQL commands in database tasks (DuckDB and Postgres), it's important to use the correct command index. Commands are indexed starting from 0, but the actual index assigned to each command may vary depending on how the commands are parsed and executed.

### Determining the Correct Command Index

If you encounter a template rendering error like `'dict object' has no attribute 'data'` or if your template is not accessing the expected data, you may need to check the actual command index in the logs.

To determine the correct command index:

1. Run the workflow and check the logs
2. Look for log entries that show the step result data structure
3. Identify the actual command index used for the data you want to reference

For example, you might see a log entry like:

```
BROKER.EXECUTE_STEP: Updated context key=query_and_analyze, value={'command_10': {'status': 'success', 'rows': [{'repo_name': 'vscode', ...}], ...}}
```

This indicates that the data is stored under `command_10` rather than `command_0`.

### Common Pitfalls

- **Assuming sequential command indexing**: Don't assume that commands will always be indexed as `command_0`, `command_1`, etc. The actual index may be different.
- **Hardcoding command indices**: Consider making command indices configurable or using a more robust way to reference data.
- **Not checking logs**: Always check the logs to verify the actual data structure when debugging template rendering errors.

### Example Fix

If your template is using:

```yaml
repository_info: "{{ query_and_analyze.data.command_0.rows }}"
```

But the logs show the data is under `command_10`, update your template to:

```yaml
repository_info: "{{ query_and_analyze.data.command_10.rows }}"
```