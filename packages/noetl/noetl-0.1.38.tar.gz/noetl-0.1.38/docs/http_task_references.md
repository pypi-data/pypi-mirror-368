# HTTP Task References in Templates

## Issue Description

The issue description "you keep fetch_github_repo.data" refers to how we reference HTTP task results in templates. Unlike database tasks (DuckDB and Postgres) where we updated references from `data` to `result`, for HTTP tasks we should continue using the `data` attribute.

## HTTP Task Result Structure

When an HTTP task is executed in NoETL, it returns a result with the following structure:

```json
{
    "id": "task_id",
    "status": "success",
    "data": {
        "property1": "value1",
        "property2": "value2",
        "additional_properties": "additional_values"
    }
}
```

The `data` field contains the parsed JSON response from the HTTP request. This is different from database tasks where the `data` field contains command results indexed by `command_0`, `command_1`, etc.

## Correct Way to Reference HTTP Task Results

For HTTP tasks, the correct way to reference results in templates is:

```
{{ step_name.data.property_name }}
```

For example, to reference the `name` property of a GitHub repository response:

```
{{ fetch_github_repo.data.name }}
```

## Why We Keep `fetch_github_repo.data`

In the GitHub metrics example YAML file, we have several references to `fetch_github_repo.data`:

```yaml
repo_name: "{{ fetch_github_repo.data.name }}"
repo_full_name: "{{ fetch_github_repo.data.full_name }}"
stars_count: "{{ fetch_github_repo.data.stargazers_count }}"
forks_count: "{{ fetch_github_repo.data.forks_count }}"
language: "{{ fetch_github_repo.data.language }}"
created_at: "{{ fetch_github_repo.data.created_at }}"
updated_at: "{{ fetch_github_repo.data.updated_at }}"
```

And later:

```yaml
original_api_data: "{{ fetch_github_repo.data }}"
```

These references are correct and should be kept as they are. The HTTP task result is properly stored under the `data` attribute, and this is how it should be referenced in templates.

## Difference from Database Tasks

For database tasks (DuckDB and Postgres), we updated references from `data` to `result` because the task results were stored under the `result` attribute in the context. This was a specific fix for database tasks and does not apply to HTTP tasks.

## Summary

- **HTTP Tasks**: Use `step_name.data.property_name` to reference properties of the HTTP response
- **Database Tasks**: Use `step_name.result.command_X` to reference command results from database tasks

By maintaining this distinction, we ensure that templates correctly reference task results based on the task type.