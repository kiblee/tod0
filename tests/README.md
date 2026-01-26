# Tests

This directory contains unit and integration tests for the tod0 project.

## Test Files

### Unit Tests (run in CI/CD)
- **test_datetime_parser.py** - Tests for natural language datetime parsing
- **test_task_names_with_slashes.py** - Tests for `parse_task_path()` with URLs and slashes
- **test_cli_commands.py** - Tests for CLI argument parsing and command setup
- **test_models.py** - Tests for TodoList and Task data models
- **test_wrapper.py** - Tests for API wrapper exceptions and constants

### Integration Tests (require API credentials)
- **test_cli_url_integration.py** - End-to-end test creating tasks with URLs in Microsoft To-Do

## Running Tests

### Run all unit tests:
```bash
source venv/bin/activate
python3 run_tests.py
```

### Run a specific test file:
```bash
source venv/bin/activate
python3 tests/test_cli_commands.py
```

### Run integration tests (requires API credentials):
```bash
source venv/bin/activate
python3 tests/test_cli_url_integration.py
```

## CI/CD

CircleCI automatically runs all unit tests on every push. See `.circleci/config.yml` for configuration.

Integration tests are NOT run in CI/CD because they require:
- Valid Microsoft API credentials
- Network access
- A real Microsoft To-Do account

## Test Coverage

Current coverage includes:
- ✓ CLI argument parsing for all commands
- ✓ Task path parsing with URLs and special characters
- ✓ Natural language datetime parsing
- ✓ Data model initialization
- ✓ Exception handling
- ✓ End-to-end task creation/completion/deletion

## Adding New Tests

1. Create test file: `tests/test_<module_name>.py`
2. Import unittest: `import unittest`
3. Create test class: `class TestFeature(unittest.TestCase):`
4. Add test methods: `def test_something(self):`
5. Update `run_tests.py` to include new test
6. Update `.circleci/config.yml` if test should run in CI
