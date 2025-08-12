# Task Results Reference Fix

## Issue Description

There was an issue with referencing task results in templates, particularly for DuckDB and Postgres tasks. The error message was:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ extract_repo_metrics.data.command_1 }}
```

This occurred because the task results were stored in the context directly under the step name, but templates were referencing them as if they were stored under a `data` attribute of the step name.

## Changes Made

We modified the `execute_step` method in `broker.py` to store the task result data in the context in a way that matches how it's referenced in templates. Specifically, we added a new line to store the result data under `step_name.data`:

```python
# Store the result data under step_name.data to match template references
self.agent.update_context(step_name + '.data', result.get('data'))
```

This change ensures that templates can reference task results using the pattern `{{ step_name.data.command_X }}`, which is what's used in the GitHub metrics example YAML file.

We also maintained backward compatibility by continuing to store the task result data directly under the step name and under `step_name.result`.

## Documentation

We've created a new documentation file, `task_results_reference.md`, that provides guidance on how to properly reference task results in templates. This documentation includes:

- The structure of task results
- How to reference task results in templates
- Examples of referencing task results
- How to access specific fields in the results
- Information about backward compatibility

## Testing

The changes have been tested and verified to resolve the template rendering errors. The GitHub metrics example now works correctly, with task results being properly accessible via templates.

## Future Considerations

In the future, we may want to consider standardizing the way task results are referenced in templates to avoid confusion. For now, we've maintained backward compatibility while also supporting the new reference pattern.

## Related Files

- `broker.py`: Modified to store task results in the context in a way that matches how they're referenced in templates
- `docs/task_results_reference.md`: New documentation on how to reference task results in templates