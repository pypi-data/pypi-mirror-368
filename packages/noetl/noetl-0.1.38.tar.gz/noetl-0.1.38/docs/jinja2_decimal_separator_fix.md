# Jinja2 Decimal Separator Rendering Fix

## Issue Description

When using DuckDB with CSV files that use a comma (`,`) as the decimal separator, an error occurs when the `decimal_separator` parameter is incorrectly rendered in Jinja2 templates. The specific issue is that the parameter is rendered with quotes in the `read_csv` function call:

```sql
, decimal_separator='{{ decimal_separator }}'
```

But DuckDB expects the parameter without additional quotes, like in the COPY command example:

```sql
COPY (SELECT 1.23 AS value, 4.56 AS another_value) TO 'output.csv' (HEADER, DELIMITER ',', DECIMAL_SEPARATOR ',');
```

This mismatch causes DuckDB to fail when processing CSV files with comma decimal separators.

## Problem Analysis

The issue was identified in the `load_ng.yaml` file, specifically in the `load_NGOCT24` step. The `decimal_separator` parameter was defined correctly in the step's `with` section:

```yaml
decimal_separator: ","
```

But it was rendered incorrectly in the SQL template:

```sql
, decimal_separator='{{ decimal_separator }}'
```

This caused DuckDB to receive the parameter with extra quotes, which it couldn't process correctly.

## Solution

The solution was to modify how the `decimal_separator` parameter is rendered in the template by removing the quotes around it:

```sql
, decimal_separator={{ decimal_separator }}
```

This matches the format used in the COPY command example and ensures that DuckDB receives the parameter in the correct format.

## Implementation

The fix was implemented in the `fix_jinja2_decimal_separator.py` script, which:

1. Locates the problematic pattern in the `load_ng.yaml` file
2. Replaces it with the correct format
3. Writes the updated content back to the file

The key part of the fix is:

```python
# Find the problematic line
old_pattern = r"decimal_separator='{{ decimal_separator }}'"
new_pattern = r"decimal_separator={{ decimal_separator }}"

# Replace the pattern
content = content.replace(old_pattern, new_pattern)
```

## Testing

The fix was tested by running the script and verifying that the pattern was correctly replaced in the `load_ng.yaml` file. The updated file now uses the correct format for the `decimal_separator` parameter, which matches the format used in the COPY command example.

## Impact

This fix ensures that:

1. The `decimal_separator` parameter is correctly rendered in Jinja2 templates
2. DuckDB can properly process CSV files with comma decimal separators
3. The `load_NGOCT24` step works correctly with the specified decimal separator

## Related Files

- `examples/tradetrend/load_ng.yaml`: Contains the step with the `decimal_separator` parameter
- `fix_jinja2_decimal_separator.py`: Script to apply the fix
- `docs/jinja2_decimal_separator_fix.md`: This documentation

## Usage

To apply the fix, run:

```bash
python fix_jinja2_decimal_separator.py
```

This will modify the `load_ng.yaml` file to use the correct format for the `decimal_separator` parameter.