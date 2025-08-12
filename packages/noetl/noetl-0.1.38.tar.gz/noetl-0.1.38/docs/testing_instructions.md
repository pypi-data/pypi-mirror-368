# Testing Instructions for GitHub Metrics Example Fix

This document provides instructions for testing the changes made to fix the template rendering errors in the GitHub metrics example.

## Prerequisites

- NoETL server running
- Access to the NoETL CLI or API
- The updated GitHub metrics example YAML file

## Testing Steps

1. **Register the GitHub metrics example playbook**

   ```bash
   noetl playbooks --register examples/github/github_metrics_example.yaml --port 8080 --host localhost
   ```

   This will register the updated GitHub metrics example playbook with the NoETL server.

2. **Execute the GitHub metrics example playbook**

   ```bash
   noetl playbooks --execute --path examples/github/github_metrics_example --port 8080 --host localhost
   ```

   This will execute the GitHub metrics example playbook.

3. **Check the logs for template rendering errors**

   ```bash
   docker-compose logs --tail=200 server | grep -i "template rendering error"
   ```

   If our changes were successful, there should be no template rendering errors related to the GitHub metrics example.

4. **Check the logs for successful execution**

   ```bash
   docker-compose logs --tail=200 server | grep -i "BROKER.EXECUTE_STEP: Step 'generate_report' completed with status"
   ```

   If our changes were successful, you should see a log entry indicating that the `generate_report` step completed with status `success`.

5. **Check the error_log table for template rendering errors**

   ```sql
   SELECT * FROM noetl.error_log 
   WHERE error_type = 'template_rendering' 
   AND template_string LIKE '%extract_repo_metrics.result.command%'
   ORDER BY timestamp DESC
   LIMIT 10;
   ```

   If our changes were successful, there should be no new template rendering errors related to the GitHub metrics example.

## Expected Outcomes

If our changes were successful, you should observe the following:

1. No template rendering errors related to the GitHub metrics example in the logs
2. The `generate_report` step completes with status `success`
3. No new template rendering errors in the `error_log` table

## Troubleshooting

If you encounter any issues during testing, here are some troubleshooting steps:

1. **Check the logs for any errors**

   ```bash
   docker-compose logs --tail=500 server | grep -i "error"
   ```

   This will show any errors that occurred during execution.

2. **Check the context data in the error logs**

   If there are still template rendering errors, check the context data in the error logs to understand the structure of the data available during template rendering.

3. **Verify the changes to the GitHub metrics example YAML file**

   Make sure that all the template references have been updated to use `.data` instead of `.result`:

   - `extract_repo_metrics.data.command_1.rows` instead of `extract_repo_metrics.result.command_1.rows`
   - `extract_repo_metrics.data.command_3.rows` instead of `extract_repo_metrics.result.command_3.rows`
   - `query_and_analyze.data.command_10.rows` instead of `query_and_analyze.result.command_10.rows`

4. **Check the fallback mechanisms in the Python code**

   Make sure that the Python code in the `generate_report` step is trying to access the data using `.data` first and then falling back to `.result` if needed.

## Conclusion

By following these testing steps, you can verify that our changes have fixed the template rendering errors in the GitHub metrics example. If you encounter any issues, please refer to the troubleshooting steps or consult the documentation on template references in NoETL.

## Related Documentation

- [Template References in NoETL](template_references.md)
- [GitHub Metrics Example Fix Summary](github_metrics_fix_summary.md)