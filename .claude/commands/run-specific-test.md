# Run Specific Test

Run a specific test file

## Usage
```bash
source venv/bin/activate && pytest tests/$1 -v
```

## Parameters
- `$1`: Name of test file (e.g., "test_models.py")

## Example
```
/run-specific-test "test_models.py"
```