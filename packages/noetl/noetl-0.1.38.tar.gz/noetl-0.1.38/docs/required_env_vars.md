# NoETL Required Environment Variables

## Issue Description

Previously, NoETL would use default values for critical environment variables related to database schema and user credentials. This could lead to unexpected behavior when these variables were not explicitly set, as the server would still start but might not function correctly.

The requirement is that the server should fail with a clear error message if critical environment variables are not provided, rather than using default values.

## Solution

The following changes have been made to enforce required environment variables:

1. Modified `set_noetl_credentials` method in `schema.py` to:
   - Check for NOETL_SCHEMA, NOETL_USER, and NOETL_PASSWORD environment variables
   - Raise a ValueError with a clear error message if any of these variables are missing
   - Remove default values for these critical variables

2. Modified `initialize_connection` method in `schema.py` to:
   - Check for POSTGRES_USER and POSTGRES_PASSWORD environment variables
   - Raise a ValueError with a clear error message if any of these variables are missing
   - Remove default values for these critical variables

3. Improved logging throughout the schema initialization process:
   - Added "SCHEMA VERIFICATION" prefix to logs in create_noetl_metadata method
   - Added "SCHEMA INSTALLATION" prefix to logs in create_noetl_schema method
   - Added "SCHEMA INSTALLATION FAILED" prefix to error logs
   - Included more detailed information about the schema creation process

## Required Environment Variables

The following environment variables are now required for NoETL to start:

| Variable | Description |
|----------|-------------|
| `NOETL_SCHEMA` | Schema name for NoETL database tables |
| `NOETL_USER` | Username for NoETL database connection |
| `NOETL_PASSWORD` | Password for NoETL database connection |
| `POSTGRES_USER` | Username for PostgreSQL admin connection (needs privileges to create users and schemas) |
| `POSTGRES_PASSWORD` | Password for PostgreSQL admin connection |

## Error Messages

If any of the required environment variables are missing, the server will fail to start with one of the following error messages:

- `NOETL_SCHEMA environment variable is required but not provided`
- `NOETL_USER environment variable is required but not provided`
- `NOETL_PASSWORD environment variable is required but not provided`
- `POSTGRES_USER environment variable is required but not provided`
- `POSTGRES_PASSWORD environment variable is required but not provided`

## Testing

A test script `test_required_env_vars.sh` has been created to verify that the server fails with appropriate error messages when required environment variables are not provided. The script tests the following scenarios:

1. Missing NOETL_SCHEMA
2. Missing NOETL_USER
3. Missing NOETL_PASSWORD
4. Missing POSTGRES_USER
5. Missing POSTGRES_PASSWORD
6. All required variables set (should proceed to connection attempt)

To run the test script:

```bash
chmod +x test_required_env_vars.sh
./test_required_env_vars.sh
```

## Deployment Considerations

When deploying NoETL in Kubernetes or other environments, ensure that all required environment variables are set in your configuration files:

- In Kubernetes, update the ConfigMap and Secret resources to include all required variables
- For Docker deployments, ensure your .env file or docker-compose.yml includes all required variables
- For local development, set these variables in your shell environment or .env file

## Example Configuration

### Example Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: noetl-config
data:
  POSTGRES_USER: "postgres"
  NOETL_USER: "noetl"
  NOETL_SCHEMA: "noetl"
  # Other non-sensitive configuration...
```

### Example Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: noetl-secret
type: Opaque
data:
  POSTGRES_PASSWORD: "cG9zdGdyZXM=" # base64 encoded
  NOETL_PASSWORD: "bm9ldGw=" # base64 encoded
```