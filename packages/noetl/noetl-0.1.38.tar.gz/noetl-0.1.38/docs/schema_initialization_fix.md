# NoETL Database Schema Initialization Fix

## Issue Description

The NoETL application was encountering errors related to database schema initialization:

1. `relation "catalog" does not exist` errors when trying to register resources
2. `generator didn't stop after throw()` errors in async functions
3. Database connection errors with incorrect credentials

The root cause was that the application was not properly initializing the database schema when it didn't exist, and there was a mismatch between the configured environment variables and what was being used.

## Solution

The following changes were made to fix the issues:

1. Modified `main.py` to initialize `DatabaseSchema` with `auto_setup=True` instead of `auto_setup=False`:
   ```python
   db_schema = DatabaseSchema(auto_setup=True)
   ```

2. Updated `worker.py` to also initialize `DatabaseSchema` with `auto_setup=True`:
   ```python
   self.db_schema = DatabaseSchema(pgdb=pgdb, auto_setup=True)
   ```

These changes ensure that:
- The database schema is automatically created if it doesn't exist
- The required tables (catalog, resource, workload, etc.) are created
- The application can properly register and execute resources

## Technical Details

The `auto_setup` parameter in `DatabaseSchema` controls whether the schema and user should be automatically created during initialization. When set to `True`, it:

1. Attempts to create the NoETL user if it doesn't exist
2. Creates the NoETL schema if it doesn't exist
3. Grants the necessary permissions to the NoETL user
4. Creates all required tables in the schema

By enabling this in both `main.py` and `worker.py`, we ensure that the database is properly initialized regardless of which component is started first.

## Testing

The fix was tested by:
1. Creating a test script that initializes the database schema with `auto_setup=True`
2. Verifying that all required tables are created
3. Confirming that resource registration works correctly

## Environment Variables

The application uses the following environment variables for database configuration:

- `POSTGRES_USER`: Username for PostgreSQL database connection
- `POSTGRES_PASSWORD`: Password for PostgreSQL database connection
- `POSTGRES_DB`: Database name for PostgreSQL connection
- `POSTGRES_HOST`: Host address for PostgreSQL server
- `POSTGRES_PORT`: Port for PostgreSQL server
- `POSTGRES_SCHEMA`: Schema for PostgreSQL database connection
- `NOETL_USER`: Username for NoETL database connection
- `NOETL_PASSWORD`: Password for NoETL database connection
- `NOETL_SCHEMA`: Schema for NoETL database connection

Make sure these are properly configured in your environment.