# Test Plan for DuckDB Results Structure Fix

This document outlines the steps to test the changes made to fix the double array issue in DuckDB query results.

## Prerequisites

- Access to a NoETL environment with the modified code
- The GitHub metrics example YAML file with updated template references

## Test Cases

### 1. Basic DuckDB Query Results Structure

**Objective**: Verify that DuckDB query results are now structured with "rows", "row_count", and "columns" keys.

**Steps**:
1. Create a simple playbook with a DuckDB task that executes a SELECT query
2. Execute the playbook
3. Check the logs to verify the structure of the DuckDB query results

**Expected Result**: The DuckDB query results should be structured with "rows", "row_count", and "columns" keys, similar to Postgres query results.

### 2. GitHub Metrics Example Execution

**Objective**: Verify that the GitHub metrics example executes without template rendering errors.

**Steps**:
1. Execute the GitHub metrics example playbook
2. Check the logs for any template rendering errors

**Expected Result**: The GitHub metrics example should execute without any template rendering errors related to accessing DuckDB query results.

### 3. Template Reference Access

**Objective**: Verify that template references can access DuckDB query results using the new structure.

**Steps**:
1. Create a playbook with a DuckDB task and a subsequent step that references the DuckDB query results
2. Use template references like `{{ step_name.result.command_X.rows }}`
3. Execute the playbook
4. Check the logs to verify that the template references are resolved correctly

**Expected Result**: The template references should be resolved correctly, and the subsequent step should have access to the DuckDB query results.

### 4. Edge Cases

**Objective**: Verify that the changes handle edge cases correctly.

**Test Cases**:
1. **Empty Result Set**: Execute a DuckDB query that returns no rows
2. **Large Result Set**: Execute a DuckDB query that returns a large number of rows
3. **Non-SELECT Queries**: Execute DuckDB commands that don't return rows (e.g., CREATE TABLE, INSERT)
4. **Error Handling**: Execute a DuckDB query that results in an error

**Expected Result**: The changes should handle all edge cases correctly, providing appropriate result structures and error messages.

## Verification Steps

For each test case, verify the following:

1. **Logs**: Check the logs for any errors or warnings related to DuckDB query results or template rendering
2. **Result Structure**: Examine the structure of the DuckDB query results in the logs to ensure they match the expected format
3. **Template Resolution**: Verify that template references to DuckDB query results are resolved correctly
4. **Workflow Execution**: Confirm that the workflow executes successfully without any errors related to DuckDB query results

## Regression Testing

To ensure that the changes don't introduce any regressions, also test the following:

1. **Postgres Query Results**: Verify that Postgres query results are still structured correctly and accessible in templates
2. **HTTP Task Results**: Verify that HTTP task results are still accessible in templates using the existing pattern
3. **Other Task Types**: Verify that results from other task types (e.g., Python, Secrets) are still accessible in templates

## Reporting

Document any issues or unexpected behavior encountered during testing, including:

1. **Issue Description**: A clear description of the issue
2. **Steps to Reproduce**: The steps to reproduce the issue
3. **Expected vs. Actual Behavior**: What was expected and what actually happened
4. **Logs**: Relevant log entries that help diagnose the issue
5. **Suggested Fix**: If applicable, a suggestion for how to fix the issue