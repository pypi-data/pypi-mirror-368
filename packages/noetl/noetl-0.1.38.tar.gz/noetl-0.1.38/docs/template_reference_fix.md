# Template Reference Fix for GitHub Metrics Example

## Issue Description

When running the GitHub metrics example, the following error was observed in the logs:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ extract_repo_metrics.data.command_1 }}
```

Similar errors were also observed for other template references:

```
Template rendering error: 'dict object' has no attribute 'data', template: {{ extract_repo_metrics.data.command_3 }}
Template rendering error: 'dict object' has no attribute 'data', template: {{ query_and_analyze.data.command_10.rows }}
```

These errors occurred because the templates were trying to access task results using the `data` attribute, but the actual data was stored under the `result` attribute in the context.

## Root Cause Analysis

In the `broker.py` file, task results are stored in the context in three different ways:

1. Directly under the step name:
   ```python
   self.agent.update_context(step_name, result.get('data'))
   ```

2. Under `step_name.result`:
   ```python
   self.agent.update_context(step_name + '.result', result.get('data'))
   ```

3. Under `step_name.data`:
   ```python
   self.agent.update_context(step_name + '.data', result.get('data'))
   ```

The documentation in `task_results_reference.md` recommends using the `step_name.data.command_X` pattern, but in practice, the `step_name.result.command_X` pattern has proven more reliable.

## Changes Made

We modified the GitHub metrics example YAML file to use `result` instead of `data` in template references:

1. Changed `extract_repo_metrics.data.command_1` to `extract_repo_metrics.result.command_1`
2. Changed `extract_repo_metrics.data.command_3` to `extract_repo_metrics.result.command_3`
3. Changed `query_and_analyze.data.command_10.rows` to `query_and_analyze.result.command_10.rows`

## Expected Impact

These changes should resolve the template rendering errors and allow the GitHub metrics example to run successfully. By using the `result` attribute instead of the `data` attribute, we're accessing the task results in a way that matches how they're actually stored in the context.

## Recommendations for Future Work

1. **Update Documentation**: The `task_results_reference.md` file should be updated to recommend using the `step_name.result.command_X` pattern instead of the `step_name.data.command_X` pattern. This would align the documentation with the actual behavior of the system.

2. **Standardize Template References**: Consider standardizing the way task results are stored in the context to avoid confusion. Instead of storing the data in three different ways, it might be clearer to have a single recommended way to access task results.

3. **Add Validation**: Add validation for template references to catch errors before execution. This could include checking if the referenced attributes exist in the context and providing helpful error messages if they don't.

4. **Improve Error Messages**: Enhance error messages to provide more context about what might be wrong with a template reference. For example, if a template tries to access `step_name.data.command_X` but the data is only available under `step_name.result.command_X`, the error message could suggest the correct reference pattern.

## Related Files

- `/examples/github/github_metrics_example.yaml`: Modified to use `result` instead of `data` in template references
- `/noetl/broker.py`: Contains the code that stores task results in the context
- `/docs/task_results_reference.md`: Documentation on how to reference task results in templates (needs to be updated)

## Testing

The changes have been implemented, but due to the nature of the development environment, we couldn't directly test the execution of the GitHub metrics example. We recommend testing the fix by:

1. Running the GitHub metrics example
2. Checking the logs for any template rendering errors
3. Verifying that all steps complete successfully

If the issue persists, further investigation may be needed to determine the exact way task results are stored in the context.