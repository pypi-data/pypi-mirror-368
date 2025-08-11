# Test-Driven Development (TDD) Practices

This guide captures practical TDD workflows and patterns discovered during bug fixes and feature development in the Zenodotos project.

## Overview

Test-Driven Development follows a simple but powerful cycle: **RED → GREEN → REFACTOR**. This approach helps ensure code quality, prevents regressions, and provides confidence when making changes.

## TDD Workflow

### 🔴 RED Phase: Write a Failing Test

1. **Identify the Problem/Requirement**
   - Understand what needs to be fixed or implemented
   - Define the expected behavior clearly
   - Consider edge cases and user scenarios

2. **Write the Test First**
   ```bash
   # Create a test that captures the desired behavior
   uv run pytest tests/unit/test_module.py::test_new_feature -v
   ```

3. **Confirm It Fails**
   - The test should fail for the right reason
   - Verify you're testing what you think you're testing
   - Document the failure mode

### 🟢 GREEN Phase: Make It Pass

1. **Implement Minimal Fix**
   - Write just enough code to make the test pass
   - Don't over-engineer the solution
   - Focus on making the test green

2. **Verify the Fix**
   ```bash
   # Run the specific test
   uv run pytest tests/unit/test_module.py::test_new_feature -v

   # Run related tests to check for regressions
   uv run pytest tests/unit/test_module.py -v
   ```

### 🔵 REFACTOR Phase: Improve and Verify

1. **Run All Related Tests**
   ```bash
   # Run comprehensive test suite
   uv run pytest tests/unit/ -v

   # Check test coverage
uv run pytest --cov=zenodotos --cov-report=term-missing
   ```

2. **Improve Code Quality**
   - Refactor for maintainability
   - Remove duplication
   - Improve naming and structure

3. **Ensure No Regressions**
   - All existing tests must still pass
   - Coverage should remain high (≥80%)

## Real-World Examples

### Example 1: ID Truncation Bug

**Problem**: Google Drive IDs were truncated, making them unusable.

**🔴 RED Phase:**
```python
def test_format_file_list_with_complete_google_drive_id():
    """Test formatting with realistic Google Drive ID length (should not be truncated)."""
    full_drive_id = "1ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqr"  # 44 chars
    file = DriveFile(id=full_drive_id, name="test.txt", mime_type="text/plain", size=100)
    result = format_file_list([file], requested_fields=["id", "name"])

    # This should fail initially
    assert full_drive_id in result
    assert "..." not in result  # No truncation indicator
```

**🟢 GREEN Phase:**
```python
# In src/zenodotos/formatters/display.py
field_config = {
    "id": {"header": "ID", "width": 45, "align": "<"},  # Increased from 30 to 45
    # ... other fields
}
```

**🔵 REFACTOR Phase:**
- Ran all formatter tests to ensure no regressions
- Verified the fix works in actual CLI usage

### Example 2: Duplicate Fields Bug

**Problem**: `--fields "id,name,id,size"` created duplicate columns and broken formatting.

**🔴 RED Phase:**
```python
@pytest.mark.parametrize("fields_input,expected_order", [
    ("id,name,id,size", ["id", "name", "size"]),  # Remove duplicate 'id'
    ("name,name,size", ["name", "size"]),         # Remove duplicate 'name'
    ("size,size,size", ["size"]),                # Multiple duplicates
])
def test_cli_field_processing_removes_duplicates(fields_input, expected_order):
    # Test the current buggy logic (should fail)
    user_fields = [f.strip() for f in fields_input.split(",") if f.strip()]
    requested_fields = user_fields  # This preserves duplicates (buggy)

    assert requested_fields == expected_order  # This will fail
```

**🟢 GREEN Phase:**
```python
# In src/zenodotos/cli/commands.py
user_fields_raw = [f.strip() for f in fields.split(",") if f.strip()]
# Remove duplicates while preserving order of first occurrence
seen = set()
user_fields = []
for field in user_fields_raw:
    if field not in seen:
        seen.add(field)
        user_fields.append(field)
```

**🔵 REFACTOR Phase:**
- Updated test to reflect fixed logic
- Used `@pytest.mark.parametrize` for comprehensive coverage
- Verified end-to-end CLI behavior

## Testing Patterns

### Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple scenarios efficiently:

```python
@pytest.mark.parametrize("input_data,expected_output", [
    ("case1", "result1"),
    ("case2", "result2"),
    ("edge_case", "expected_result"),
])
def test_multiple_scenarios(input_data, expected_output):
    result = function_under_test(input_data)
    assert result == expected_output
```

### Edge Case Testing

Always consider and test edge cases:
- Empty inputs
- Duplicate values
- Invalid parameters
- Boundary conditions
- Error scenarios

### Integration Testing

Test the complete flow:
```python
def test_cli_end_to_end():
    """Test complete CLI workflow with real command execution."""
    # This helps catch issues that unit tests might miss
    result = run_cli_command(["list-files", "--fields", "id,name"])
    assert "ID" in result
    assert "Name" in result
```

## Project-Specific Commands

### Running Tests
```bash
# Run specific test
uv run pytest tests/unit/test_cli.py::test_specific_function -v

# Run with coverage
uv run pytest --cov=zenodotos --cov-report=term-missing

# Run tests in specific module
uv run pytest tests/unit/formatters/ -v

# Run parametrized test cases
uv run pytest tests/unit/test_cli.py::test_field_processing -v
```

### Debugging Failed Tests
```bash
# Show more detailed output
uv run pytest tests/unit/test_cli.py::test_failing -vvs

# Drop into debugger on failure
uv run pytest tests/unit/test_cli.py::test_failing --pdb

# Show coverage gaps
uv run pytest --cov=zenodotos --cov-report=html
# Open htmlcov/index.html to see detailed coverage
```

### Development Workflow
```bash
# 1. Write failing test
uv run pytest tests/unit/test_module.py::test_new_feature -v

# 2. Implement fix
# ... edit source code ...

# 3. Verify fix
uv run pytest tests/unit/test_module.py::test_new_feature -v

# 4. Run regression tests
uv run pytest tests/unit/test_module.py -v

# 5. Check overall coverage
uv run pytest --cov=zenodotos --cov-report=term-missing
```

## Common Pitfalls and Solutions

### 1. Testing Implementation Instead of Behavior
❌ **Wrong:**
```python
def test_uses_specific_algorithm():
    # Testing how something is done, not what it does
    assert function_calls_specific_method()
```

✅ **Right:**
```python
def test_produces_correct_output():
    # Testing the behavior and output
    result = function_under_test(input_data)
    assert result == expected_output
```

### 2. Tests That Always Pass
❌ **Wrong:**
```python
def test_something():
    result = function_under_test()
    assert result  # Too vague, might always be truthy
```

✅ **Right:**
```python
def test_something():
    result = function_under_test("specific_input")
    assert result == "specific_expected_output"
```

### 3. Not Testing Edge Cases
❌ **Wrong:**
```python
def test_happy_path_only():
    assert function_under_test("normal_input") == "expected"
```

✅ **Right:**
```python
@pytest.mark.parametrize("input_val,expected", [
    ("normal_input", "expected"),
    ("", "empty_case_result"),
    ("duplicate,duplicate", "deduplicated_result"),
    ("invalid_input", "error_or_default"),
])
def test_various_scenarios(input_val, expected):
    assert function_under_test(input_val) == expected
```

## Integration with Project Workflow

### Commit Messages
Follow conventional commits when fixing bugs with TDD:
```
fix(scope): brief description of what was fixed

- Implement failing test for the identified bug
- Add minimal fix to make the test pass
- Refactor and ensure no regressions
- Include comprehensive test coverage for edge cases

Resolves: #issue_number
```

### Coverage Requirements
- Maintain ≥80% test coverage (enforced by pytest-cov)
- Focus on testing critical paths and edge cases
- Use coverage reports to identify gaps

### Code Review Checklist
When reviewing TDD-driven changes:
- [ ] Test was written before the fix
- [ ] Test fails without the fix
- [ ] Test passes with the fix
- [ ] No regressions in existing tests
- [ ] Edge cases are covered
- [ ] Code is clean and maintainable

## Benefits Observed

From applying TDD to real bugs in this project:

1. **Clear Problem Definition**: Tests forced us to understand exactly what was broken
2. **Focused Solutions**: We implemented minimal fixes rather than over-engineering
3. **Confidence in Changes**: Comprehensive tests provided safety for refactoring
4. **Regression Prevention**: Tests will catch if these bugs reappear
5. **Better Documentation**: Tests serve as executable specifications
6. **Easier Debugging**: When tests fail, they pinpoint exactly what's wrong

## Next Steps

1. **Practice**: Apply this workflow to new features and bug fixes
2. **Expand**: Add more comprehensive test coverage for existing code
3. **Refine**: Continuously improve test quality and maintainability
4. **Share**: Help team members adopt these practices

## Resources

- [Contributing Guide](contributing.md) - General development guidelines
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/) - Coverage measurement
- [Conventional Commits](https://conventionalcommits.org/) - Commit message format

---

*This guide was developed through practical application of TDD to real bugs in the Zenodotos project. It captures patterns and practices that proved effective for maintaining code quality while delivering reliable features.*
