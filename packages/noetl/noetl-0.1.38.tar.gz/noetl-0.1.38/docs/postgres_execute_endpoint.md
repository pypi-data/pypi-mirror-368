# PostgreSQL Execute Endpoint

This document describes the `/postgres/execute` endpoint, which allows you to execute PostgreSQL queries and stored procedures directly through the NoETL API.

## Endpoint Details

- **URL**: `/api/postgres/execute`
- **Method**: `POST`
- **Content-Type**: `application/json`

## Request Parameters

The endpoint accepts the following parameters in the request body:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | One of `query`, `query_base64`, or `procedure` must be provided | SQL query to execute |
| `query_base64` | string | One of `query`, `query_base64`, or `procedure` must be provided | Base64-encoded SQL query to execute |
| `procedure` | string | One of `query`, `query_base64`, or `procedure` must be provided | Stored procedure to call |
| `parameters` | array | Yes | List of parameters for the query or procedure (use an empty list `[]` if no parameters are needed) |
| `schema` | string | No | Optional schema to use (defaults to NOETL_SCHEMA from environment) |
| `connection_string` | string | No | Optional custom connection string to use instead of the default connection pool |

**Notes**: 
- You must provide exactly one of `query`, `query_base64`, or `procedure`.
- The `parameters` field should always be included in the request payload, even if it's `null` or an empty list. Omitting this field may result in a 422 validation error.
- When `connection_string` is provided, a new connection will be created using that string and closed after the operation completes. This is useful when you need to connect to a different database or use different credentials.
- Use `query_base64` when your SQL query contains special characters like newlines (`\n`), tabs, or other characters that might cause issues with JSON encoding. This is particularly useful for complex, multi-line SQL queries.

## Response Format

The endpoint returns a JSON response with the following structure:

```json
{
  "success": true,
  "rows_affected": 5,
  "columns": ["column1", "column2", "column3"],
  "results": [
    {"column1": "value1", "column2": "value2", "column3": "value3"},
    {"column1": "value4", "column2": "value5", "column3": "value6"}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the operation was successful |
| `rows_affected` | integer | Number of rows affected by the operation |
| `columns` | array | List of column names in the result set |
| `results` | array | List of result rows as dictionaries |

## Error Responses

If an error occurs, the endpoint returns a JSON response with an error message:

```json
{
  "detail": "Error message"
}
```

Common error status codes:

- `400 Bad Request`: Invalid input parameters
- `500 Internal Server Error`: Error executing the query or procedure

## Examples

### Executing a Simple Query

```python
import requests

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "query": "SELECT * FROM noetl.executions LIMIT 5"
    }
)

print(response.json())
```

### Executing a Parameterized Query

```python
import requests

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "query": "SELECT * FROM noetl.executions WHERE playbook_path = %s LIMIT %s",
        "parameters": ["examples/weather_example", 3]
    }
)

print(response.json())
```

### Executing a Stored Procedure

First, create a stored procedure in your PostgreSQL database:

```sql
CREATE OR REPLACE PROCEDURE get_execution_stats(
    OUT total_executions INTEGER,
    OUT completed_executions INTEGER,
    OUT failed_executions INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT COUNT(*) INTO total_executions FROM noetl.executions;
    SELECT COUNT(*) INTO completed_executions FROM noetl.executions WHERE status = 'completed';
    SELECT COUNT(*) INTO failed_executions FROM noetl.executions WHERE status = 'failed';
END;
$$;
```

Then call it using the API:

```python
import requests

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "procedure": "get_execution_stats"
    }
)

print(response.json())
```

### Executing a Stored Procedure with Parameters

```python
import requests

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "procedure": "update_execution_status",
        "parameters": ["abc123", "completed"]
    }
)

print(response.json())
```

### Using a Custom Connection String

```python
import requests

# Custom connection string to connect to a different database
custom_conn_string = "dbname=analytics user=reporter password=readonly host=reporting-db.example.com port=5432"

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "query": "SELECT * FROM public.report_data LIMIT 10",
        "connection_string": custom_conn_string
    }
)

print(response.json())
```

This example shows how to use a custom connection string to connect to a different database server with different credentials. The connection will be created specifically for this request and closed immediately after the operation completes.

### Using Base64-Encoded Queries

When working with complex, multi-line SQL queries, it's recommended to use base64 encoding to avoid issues with special characters in JSON:

```python
import requests
import base64

# A complex multi-line SQL query
sql_query = """
SELECT 
    step_id, 
    step_name, 
    result_data,
    created_at
FROM noetl.execution_results
WHERE execution_id = '008ceaf8-bf2e-4a9e-a32f-25978824d1ba'
ORDER BY created_at
"""

# Encode the query as base64
query_base64 = base64.b64encode(sql_query.encode('utf-8')).decode('utf-8')

response = requests.post(
    "http://localhost:8080/api/postgres/execute",
    json={
        "query_base64": query_base64,
        "parameters": []
    }
)

print(response.json())
```

This approach is particularly useful when:
- Your SQL query contains multiple lines, tabs, or other whitespace
- You're dynamically generating SQL queries that might contain special characters
- You're experiencing 422 validation errors with regular query strings due to JSON encoding issues

## Complete Example Script

See the [postgres_execute_example.py](../examples/postgres_execute_example.py) script for a complete example of how to use this endpoint.