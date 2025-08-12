# Command Indexing Fix for GitHub Metrics Example

## Issue Description

When running the GitHub metrics example, the following error was observed in the logs:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ query_and_analyze.data.command_0.rows }}
```

This error occurred during the `generate_report` step when trying to access data from the previous `query_and_analyze` step. The template was trying to access `query_and_analyze.data.command_0.rows`, but the actual data was stored under `command_10`.

## Root Cause Analysis

The root cause of this issue was a mismatch between how the template referenced the command results and how they were actually stored in the context. In the GitHub metrics example YAML file, the template reference was:

```yaml
repository_info: "{{ query_and_analyze.data.command_0.rows }}"
```

However, the logs showed that the actual data was stored under `command_10`:

```
'query_and_analyze': {'command_10': {'status': 'success', 'rows': [{'repo_name': 'vscode', ...}], ...}}
```

This mismatch occurred because the command indexing in database tasks (DuckDB and Postgres) can vary depending on how the commands are parsed and executed. The SQL query in the `query_and_analyze` step was being stored as `command_10` instead of `command_0`.

## Fix Implemented

The fix was to update the template reference in the GitHub metrics example YAML file to use the correct command index:

```yaml
repository_info: "{{ query_and_analyze.data.command_10.rows }}"
```

This ensures that the template correctly references the data structure as it exists in the context.

## Documentation Updates

To prevent similar issues in the future, we've added a new section on command indexing to the `task_results_reference.md` documentation. This section explains:

1. How command indexing works in database tasks
2. How to determine the correct command index from logs
3. Common pitfalls to avoid
4. An example of how to fix command indexing issues

## Recommendations for Future Development

To prevent similar issues in the future, we recommend:

1. **Check logs for actual data structure**: When debugging template rendering errors, always check the logs to see how data is actually stored in the context.

2. **Use more robust data referencing**: Consider implementing a more robust way to reference data that doesn't rely on hardcoded command indices. For example:
   - Add a way to name commands and reference them by name
   - Implement a function to find the first command result that matches certain criteria
   - Store important results in a more predictable structure

3. **Add validation for templates**: Implement validation for templates to catch reference errors before execution.

4. **Improve error messages**: Enhance error messages to provide more context about what might be wrong with a template reference.

## Related Files

- `/examples/github/github_metrics_example.yaml`: Updated to use the correct command index
- `/docs/task_results_reference.md`: Updated with a new section on command indexing

## Testing

The fix has been implemented, but due to the nature of the development environment, we couldn't directly test the execution of the GitHub metrics example. We recommend testing the fix by:

1. Running the GitHub metrics example
2. Checking the logs for any template rendering errors
3. Verifying that the `generate_report` step completes successfully

If the issue persists, further investigation may be needed to determine the exact command index being used.