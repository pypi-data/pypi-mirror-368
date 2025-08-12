# Testing the DuckDB Decimal Separator Handler

This document explains how to test the decimal separator handler functionality in `action.py` by temporarily commenting it out.

## Background

The decimal separator handler in `action.py` is a critical component that enables DuckDB to properly handle CSV files with comma (`,`) as decimal separators. When this handler is active, it:

1. Detects when a non-standard decimal separator is specified in the task configuration
2. Uses regex to find all `CAST(X AS NUMERIC)` patterns in SQL commands
3. Replaces them with `CAST(REPLACE(X, ',', '.') AS NUMERIC)` to convert the decimal separator before casting

This ensures that string values with comma decimal separators are properly converted to numeric types.

## Testing Procedure

To verify that this handler is working correctly, you can temporarily comment it out and observe the behavior:

### Step 1: Comment Out the Handler

Run the provided script to comment out the decimal separator handler:

```bash
python test_without_decimal_handler.py
```

This script:
- Creates a backup of the original `action.py` file
- Comments out the decimal separator handler code
- Provides instructions for restoring the original file

### Step 2: Run a Test with Comma Decimal Separators

Execute a DuckDB query that processes CSV data with comma decimal separators, such as:

```bash
cd /Users/kadyapam/projects/noetl/noetl
python -m noetl run examples/tradetrend/load_ng.yaml
```

### Step 3: Observe the Error

Without the decimal separator handler, you should see an error similar to:

```
Conversion Error: Could not convert string "2,458" to DECIMAL(18,3) when casting from source column high

LINE 1: ... NUMERIC) as trades , CAST(bar_size AS NUMERIC) as bar_size , CAST(high AS NUMERIC) as high , CAST(low AS NUMERIC) as...
                                                                         ^
```

This error occurs because:
- The CSV file is read with `decimal_separator=','` which correctly identifies commas as decimal separators
- The columns are read as VARCHAR types to preserve the original format
- When `CAST(high AS NUMERIC)` is executed, DuckDB tries to convert the string "2,458" to a numeric value
- Without the handler, the CAST operation doesn't know about the decimal separator setting and expects a period (`.`)
- The conversion fails because "2,458" is not a valid numeric format with the default decimal separator

### Step 4: Restore the Original File

After testing, restore the original `action.py` file:

```bash
python test_without_decimal_handler.py restore
```

Or use the specific backup file path that was displayed when you ran the script:

```bash
cp /Users/kadyapam/projects/noetl/noetl/noetl/action.py.bak.YYYYMMDDHHMMSS /Users/kadyapam/projects/noetl/noetl/noetl/action.py
```

### Step 5: Verify the Fix

Run the same test again with the original file restored:

```bash
cd /Users/kadyapam/projects/noetl/noetl
python -m noetl run examples/tradetrend/load_ng.yaml
```

The query should now execute successfully, demonstrating that the decimal separator handler is working correctly.

## Conclusion

This testing procedure confirms that:

1. The decimal separator handler is necessary for processing CSV files with comma decimal separators
2. The implementation correctly modifies CAST operations to handle custom decimal separators
3. Without this handler, DuckDB would fail to process such files

The handler is a critical component for ensuring compatibility with international data formats that use comma as the decimal separator.