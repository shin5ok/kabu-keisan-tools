# Tests for Kabu Keisan Tools

This directory contains tests for the Kabu Keisan Tools application. The tests are written using pytest and cover the main functionality of the application.

## Test Files

- `test_utils.py`: Tests for utility functions in utils.py
- `test_main.py`: Tests for the main calculation function in main.py
- `conftest.py`: Pytest configuration and fixtures

## Running Tests

To run the tests, execute the following command from the root directory:

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=.
```

## Test Coverage

The tests cover the following functionality:

### Utils Tests
- Date format conversion
- Exchange rate initialization from HTML content
- Exchange rate retrieval
- Error handling for API requests

### Main Tests
- Total value calculation with sample data
- Support for different date formats (Date vs. Vest Date columns)
- Calculation with different exchange rates
- Handling cases where exchange rates are not available

## Adding New Tests

When adding new tests:
- Place them in the appropriate test file based on what they're testing
- Use pytest fixtures where appropriate for test data
- Use mocking to isolate tests from external dependencies
