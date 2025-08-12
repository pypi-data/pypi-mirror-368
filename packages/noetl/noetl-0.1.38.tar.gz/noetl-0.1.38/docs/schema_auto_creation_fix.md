# NoETL Schema Auto-Creation Fix

## Issue Description

The NoETL application was not automatically creating the required database schema during server provisioning. This resulted in errors like:

```
relation "catalog" does not exist
LINE 1: SELECT COUNT(*) FROM catalog WHERE resource_path = $1
```

The issue occurred because:
1. The admin connection credentials (POSTGRES_USER and POSTGRES_PASSWORD) were not properly handled when environment variables were not set
2. The schema creation process had conditional logic that prevented it from running in some cases
3. Error handling was insufficient to provide clear guidance on what went wrong

## Solution

The following changes were made to fix the issue:

1. Added default values for POSTGRES_USER and POSTGRES_PASSWORD in the initialize_connection method:
   ```python
   postgres_user = os.environ.get('POSTGRES_USER', 'postgres')
   postgres_password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
   ```

2. Removed conditional logic that prevented schema creation when environment variables were not set:
   ```python
   # Always attempt to create the schema if connection fails
   logger.info(f"NoETL user connection failed, attempting to create user/schema: {e}")
   self.create_noetl_schema()
   ```

3. Improved error handling in the create_noetl_schema method:
   ```python
   try:
       self.admin_connection = psycopg.connect(self.admin_conn)
       logger.info("Connected to database with admin credentials.")
   except Exception as admin_conn_error:
       logger.error(f"Failed to connect with admin credentials: {admin_conn_error}")
       logger.error("Make sure POSTGRES_USER and POSTGRES_PASSWORD environment variables are set correctly.")
       raise
   ```

These changes ensure that:
- The schema creation process always has valid credentials
- The schema is always created when needed
- Clear error messages are provided when something goes wrong

## Testing

A test script was created to verify the schema creation fix:

```bash
#!/bin/bash
# test_schema_auto_creation.sh

# Set environment variables for testing
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres"
export POSTGRES_DB="postgres"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export NOETL_USER="noetl_test"
export NOETL_PASSWORD="noetl_test"
export NOETL_SCHEMA="noetl_test"

# Run a test to initialize the database schema
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from noetl.schema import DatabaseSchema

print('Creating DatabaseSchema with auto_setup=True')
db_schema = DatabaseSchema(auto_setup=True)

print('Calling create_noetl_metadata()')
db_schema.create_noetl_metadata()

print('Calling init_database()')
db_schema.init_database()

print('Listing tables')
tables = db_schema.list_tables()
print(f'Tables in schema: {tables}')
"
```

To run the test:
```bash
chmod +x test_schema_auto_creation.sh
./test_schema_auto_creation.sh
```

## Environment Variables

The following environment variables are used for database configuration:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| POSTGRES_USER | Username for PostgreSQL admin connection | postgres |
| POSTGRES_PASSWORD | Password for PostgreSQL admin connection | postgres |
| POSTGRES_DB | Database name for PostgreSQL connection | postgres |
| POSTGRES_HOST | Host address for PostgreSQL server | localhost |
| POSTGRES_PORT | Port for PostgreSQL server | 5432 |
| NOETL_USER | Username for NoETL database connection | noetl |
| NOETL_PASSWORD | Password for NoETL database connection | noetl |
| NOETL_SCHEMA | Schema for NoETL database connection | noetl |

Make sure these are properly configured in your environment.

## Deployment

When deploying NoETL in Kubernetes or other environments, ensure that:

1. The POSTGRES_USER and POSTGRES_PASSWORD environment variables are set with admin credentials that have permission to create users and schemas
2. The NOETL_USER, NOETL_PASSWORD, and NOETL_SCHEMA variables are set to the desired values for the NoETL application

With these changes, the NoETL schema will be automatically created during server provisioning if it doesn't already exist.