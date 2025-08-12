# HTTP vs Database Task References in Templates

## Issue Analysis

The issue description points out the use of `fetch_github_repo.data` in the GitHub metrics example YAML file:

```yaml
next:
  - step: extract_repo_metrics
    with:
      repo_name: "{{ fetch_github_repo.data.name }}"
      repo_full_name: "{{ fetch_github_repo.data.full_name }}"
```

This raises the question of whether these references should be updated to use `result` instead of `data`, similar to how we updated database task references in previous fixes.

## Different Task Types, Different Reference Patterns

After analyzing the codebase and the way task results are stored in the context, we've determined that:

1. **HTTP Tasks**: Results are stored under the `data` attribute
2. **Database Tasks** (DuckDB and Postgres): Results are stored under the `result` attribute

This difference is by design and reflects how the different task types structure their results.

## HTTP Task Result Structure

When an HTTP task is executed, it returns a result with the following structure:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "name": "vscode",
        "full_name": "microsoft/vscode",
        "stargazers_count": 175000,
        "forks_count": 34000,
        "language": "TypeScript",
        "created_at": "2015-09-03T20:23:38Z",
        "updated_at": "2025-07-31T20:23:38Z"
    }
}
```

The `data` field contains the parsed JSON response from the HTTP request, with properties directly accessible.

## Database Task Result Structure

In contrast, database tasks return results with a different structure:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "command_0": { "status": "success", "rows": [] },
        "command_1": { "status": "success", "rows": [] },
        "command_3": { "status": "success", "rows": [] },
        "command_10": { "status": "success", "rows": [] }
    }
}
```

The `data` field contains the results of each SQL command executed, indexed by command numbers.

## Correct Reference Patterns

Based on this understanding, the correct reference patterns are:

- **HTTP Tasks**: `{{ step_name.data.property_name }}`
- **Database Tasks**: `{{ step_name.result.command_X }}`

## Verification in the GitHub Metrics Example

In the GitHub metrics example YAML file, we can see both patterns used correctly:

1. HTTP task references:
   ```yaml
   repo_name: "{{ fetch_github_repo.data.name }}"
   repo_full_name: "{{ fetch_github_repo.data.full_name }}"
   stars_count: "{{ fetch_github_repo.data.stargazers_count }}"
   ```

2. Database task references:
   ```yaml
   repo_data: "{{ extract_repo_metrics.result.command_1 }}"
   stats_data: "{{ extract_repo_metrics.result.command_3 }}"
   repository_info: "{{ query_and_analyze.result.command_10.rows }}"
   ```

## Conclusion

The references to `fetch_github_repo.data` in the GitHub metrics example YAML file are correct and should be kept as they are. The distinction between using `data` for HTTP tasks and `result` for database tasks is intentional and reflects the different ways these task types structure their results.

This understanding helps ensure that templates correctly reference task results based on the task type, preventing template rendering errors.