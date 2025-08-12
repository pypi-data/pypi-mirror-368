# DuckDB Decimal Separator Fix

## Issue Description

When using DuckDB with CSV files that use a comma (`,`) as the decimal separator, an error occurs when trying to cast string values to numeric types. This is because the `decimal_separator` parameter is correctly passed to the `read_csv` function, but the subsequent `CAST` operations in SQL don't respect this setting.

The error looks like this:

```
Conversion Error: Could not convert string "2,458" to DECIMAL(18,3) when casting from source column high
```

This happens because:

1. The CSV file is read with `decimal_separator=','` which correctly identifies commas as decimal separators
2. The columns are read as VARCHAR types to preserve the original format
3. When `CAST(high AS NUMERIC)` is executed, DuckDB tries to convert the string "2,458" to a numeric value
4. The CAST operation doesn't know about the decimal_separator setting and expects a period (`.`) as the decimal separator
5. The conversion fails because "2,458" is not a valid numeric format with the default decimal separator

## Solution

The solution is to modify the `execute_duckdb_task` function in `action.py` to detect when a non-standard decimal separator is used and modify the CAST operations accordingly. The fix:

1. Checks if a decimal_separator other than the default period (`.`) is specified
2. If so, it uses a regular expression to find all `CAST(X AS NUMERIC)` patterns in the SQL
3. Replaces them with `CAST(REPLACE(X, ',', '.') AS NUMERIC)` to convert the decimal separator before casting

This ensures that string values with comma decimal separators are properly converted to numeric types.

## Implementation

The fix is implemented in the `fix_duckdb_decimal_separator.py` script, which modifies the `execute_duckdb_task` function in `action.py`. The key part of the fix is:

```python
# Handle decimal separator in CAST operations if needed
decimal_separator = task_with.get('decimal_separator')
if decimal_separator and decimal_separator != '.':
    # Replace CAST operations to handle custom decimal separator
    # This regex finds CAST(X AS NUMERIC) patterns
    cast_pattern = r'CAST\\s*\\(\\s*([^\\s]+)\\s+AS\\s+NUMERIC[^)]*\\)'
    
    def replace_cast(match):
        column = match.group(1)
        # For columns that might contain the decimal separator,
        # replace the separator with a period before casting
        return f"CAST(REPLACE({column}, '{decimal_separator}', '.') AS NUMERIC)"
    
    cmd = re.sub(cast_pattern, replace_cast, cmd, flags=re.IGNORECASE)
```

## Testing

The fix was tested with a simple script that simulates the issue:

1. Creates a CSV file with comma decimal separators
2. Attempts to cast the values to NUMERIC without the fix (fails)
3. Applies the fix by using REPLACE before CAST (succeeds)

The test confirms that the fix correctly handles comma decimal separators in CAST operations.

## Usage

To apply the fix, run:

```bash
python fix_duckdb_decimal_separator.py
```

This will modify the `action.py` file to handle decimal separators correctly in CAST operations.

## Related Files

- `examples/tradetrend/load_ng.yaml`: Contains the configuration with `decimal_separator: ","`
- `noetl/action.py`: Contains the `execute_duckdb_task` function that was modified
- `fix_duckdb_decimal_separator.py`: Script to apply the fix
- `test_decimal_separator_fix.py`: Script to test the fix