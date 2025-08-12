# NoETL Port Parameter Fix

## Issue Description

When using the `noetl catalog register playbook` command with a `--port` parameter, the following error occurred:

```
[ERROR] (main:manage_catalog:180)
     Message: Error reading or parsing file playbook: expected '<document start>', but found '<scalar>'
               in "<unicode string>", line 16, column 1:
                 DEFAULT_PORT=8080
                 ^
```

This error occurred because the command was treating "playbook" as a file path instead of a resource type. In the project directory, there was a file named "playbook" which is a bash script containing "DEFAULT_PORT=8080" at line 16, which matched the error message.

## Solution

The solution was to modify the `manage_catalog` function in `main.py` to handle the case where "playbook" is being treated as a file path. The fix adds a special case to check if `resource_type_or_path` is "playbook" and `path` is provided, then treats it as explicit resource type mode.

```python
if action == "register":
    # Special case: if resource_type_or_path is "playbook" and path is provided,
    # treat it as explicit resource type mode
    if resource_type_or_path == "playbook" and path and os.path.exists(path):
        resource_type = "playbook"
        file_path = path
        detected_resource_type = "Playbook"
        auto_detect_mode = False
        logger.info(f"Using explicit resource type: {resource_type} for file: {file_path}")
    elif os.path.exists(resource_type_or_path):
        # Existing auto-detection logic...
```

This fix ensures that when the command is used in the format `noetl catalog register playbook <file_path> --port <port>`, it correctly treats "playbook" as a resource type and not as a file path.

## Testing

The fix was tested with the following scenarios:

1. Auto-detection mode with direct port parameter:
   ```
   python -m noetl.main catalog register examples/amadeus/amadeus_api_playbook.yaml --port 30080
   ```

2. Explicit resource type mode with direct port parameter:
   ```
   python -m noetl.main catalog register playbook examples/amadeus/amadeus_api_playbook.yaml --port 30080
   ```

3. Auto-detection mode with environment variable:
   ```
   export NOETL_PORT=30080
   python -m noetl.main catalog register examples/amadeus/amadeus_api_playbook.yaml
   ```

4. Explicit resource type mode with environment variable:
   ```
   export NOETL_PORT=30080
   python -m noetl.main catalog register playbook examples/amadeus/amadeus_api_playbook.yaml
   ```

All tests passed successfully, confirming that the fix works for all scenarios.

## Usage

Users can now use the `noetl catalog register` command in either of these formats:

1. Auto-detection mode (recommended):
   ```
   noetl catalog register <file_path> [--port <port>]
   ```

2. Explicit resource type mode:
   ```
   noetl catalog register playbook <file_path> [--port <port>]
   ```

Both formats will work correctly with either direct port parameter or environment variable.