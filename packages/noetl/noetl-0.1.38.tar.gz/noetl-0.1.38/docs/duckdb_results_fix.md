# DuckDB Results Structure Fix

## Issue Description

When running the GitHub metrics example, the following error was observed in the logs:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ extract_repo_metrics.data.command_1 }}
```

The issue was related to how DuckDB query results were being stored and accessed in templates. The results were being stored as raw lists of tuples (double arrays), making it difficult to access the data in templates.

## Root Cause Analysis

The root cause of the issue was in the `execute_duckdb_task` function in `action.py`. The function was storing the raw `fetchall()` results directly:

```python
result = duckdb_con.execute(cmd).fetchall()
results[f"command_{i}"] = result
```

This resulted in a double array structure like `[[1]]` for `command_1` and `[['vscode', 'microsoft/vscode', 175204, ...]]` for `command_2`.

In contrast, the `execute_postgres_task` function was processing the results into a more structured format with "rows", "row_count", and "columns" keys:

```python
results[f"command_{i}"] = {
    "status": "success",
    "rows": result_data,
    "row_count": len(rows),
    "columns": column_names
}
```

This difference in result structure was causing template rendering errors when trying to access DuckDB results in the same way as Postgres results.

## Changes Made

### 1. Modified `execute_duckdb_task` Function

We updated the `execute_duckdb_task` function in `action.py` to process query results similar to how `execute_postgres_task` does it:

```python
cursor = duckdb_con.execute(cmd)
result = cursor.fetchall()

# Process results similar to execute_postgres_task
if cmd.strip().upper().startswith("SELECT") or "RETURNING" in cmd.upper():
    column_names = [desc[0] for desc in cursor.description] if cursor.description else []
    result_data = []
    for row in result:
        row_dict = {}
        for j, col_name in enumerate(column_names):
            if isinstance(row[j], dict) or (isinstance(row[j], str) and (row[j].startswith('{') or row[j].startswith('['))):
                try:
                    row_dict[col_name] = row[j]
                except:
                    row_dict[col_name] = row[j]
            elif isinstance(row[j], Decimal):
                row_dict[col_name] = float(row[j])
            else:
                row_dict[col_name] = row[j]
        result_data.append(row_dict)
    
    results[f"command_{i}"] = {
        "status": "success",
        "rows": result_data,
        "row_count": len(result),
        "columns": column_names
    }
else:
    results[f"command_{i}"] = {
        "status": "success",
        "message": f"Command executed successfully",
        "raw_result": result
    }
```

This change ensures that DuckDB query results are processed into a more accessible format with "rows", "row_count", and "columns" keys, similar to Postgres query results.

### 2. Updated Template References

We also updated the template references in the GitHub metrics example YAML file to access the "rows" key for DuckDB task results:

```yaml
repo_data: "{{ extract_repo_metrics.result.command_1.rows }}"
stats_data: "{{ extract_repo_metrics.result.command_3.rows }}"
```

This ensures that the templates are accessing the rows of data rather than the entire result object.

## Accessing Database Query Results in Templates

With these changes, database query results (both DuckDB and Postgres) can be accessed in templates using the following pattern:

```
{{ step_name.result.command_X.rows }}
```

Where:
- `step_name` is the name of the step that executed the database task
- `result` is the field in the step result that contains the command results
- `command_X` is the specific command result you want to reference (e.g., `command_0`, `command_1`, etc.)
- `rows` is the field in the command result that contains the rows of data

For example, to access the rows of data from the first command executed in a step named `extract_metrics`, you would use:

```
{{ extract_metrics.result.command_1.rows }}
```

You can also access other fields in the command result:

- `{{ step_name.result.command_X.row_count }}` to get the number of rows
- `{{ step_name.result.command_X.columns }}` to get the list of column names
- `{{ step_name.result.command_X.status }}` to get the status of the command execution

## Testing

To test these changes, run the GitHub metrics example and check the logs for any template rendering errors. The workflow should now execute without any errors related to accessing DuckDB query results.

## Future Considerations

In the future, we may want to consider:

1. Standardizing the result structure for all task types to make it more consistent and easier to access in templates.
2. Adding more robust error handling for template rendering errors to provide more helpful error messages.
3. Providing helper functions or macros to simplify accessing complex data structures in templates.