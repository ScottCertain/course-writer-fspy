# Testing Framework

This directory contains the testing framework for the Course Writer application. The testing setup leverages `pytest`, `pytest-watch`, `coverage.py`, and `Pynguin` to ensure code reliability and maintainability.

## Directory Structure

```
tests/
├── __init__.py           # Makes tests a package
├── conftest.py           # Shared pytest fixtures
├── README.md             # This file
├── unit/                 # Unit tests
│   ├── __init__.py
│   ├── models/           # Tests for model components
│   │   └── ...
│   └── services/         # Tests for service components
│       └── ...
└── integration/          # Integration tests
    ├── __init__.py
    └── ...
```

## Test Logs

All test logs are stored in the `test_logs/` directory at the project root:

```
test_logs/
├── pytest.log            # Main pytest log file
├── htmlcov/              # HTML coverage report directory
└── ...                   # Additional test-specific log files
```

## Getting Started

### Prerequisites

Ensure you have the required testing dependencies installed:

```bash
pip install -r requirements.txt
```

## Running Tests

### Basic Test Execution

To run all tests:

```bash
pytest
```

To run specific test files or directories:

```bash
pytest tests/unit/services/test_anthropic_service.py
pytest tests/unit/
```

### Continuous Testing with pytest-watch

For automatic test execution upon file changes:

```bash
ptw
```

This will watch your project files and re-run tests automatically when changes are detected.

### Code Coverage

To measure code coverage and identify untested parts of your codebase:

```bash
# Run tests with coverage
coverage run -m pytest

# Generate a coverage report
coverage report

# Create an HTML coverage report
coverage html
```

The HTML report will be generated in the `test_logs/htmlcov` directory.

## Automated Test Generation

`Pynguin` can help generate unit tests automatically, enhancing test coverage:

```bash
# Set the required environment variable
set PYNGUIN_DANGER_AWARE=1

# Generate tests for a specific module
pynguin --project-path . --module-name your_module
```

Generated tests will be placed in the `pynguin_tests` directory by default.

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual components in isolation:

- Place tests in the appropriate subdirectory (e.g., `tests/unit/services/` for service components)
- Name test files with the `test_` prefix
- Use mocks to isolate components from their dependencies
- Test both normal behavior and error handling

### Integration Tests

Integration tests should focus on testing the interaction between multiple components:

- Place tests in the `tests/integration/` directory
- Focus on verifying that components work together correctly
- Use fixtures to set up common test data and environments

### Fixtures

Common fixtures are defined in `conftest.py`. These include:

- `mock_llm_service`: A mock LLM service for testing without making actual API calls
- `test_course_dir`: A path to a test course directory
- `test_config`: A test configuration for use in tests

## Best Practices

1. Keep tests independent from one another
2. Use descriptive test names that explain what is being tested
3. Follow the Arrange-Act-Assert pattern in tests
4. Mock external dependencies to keep tests fast and reliable
5. Aim for high test coverage, but focus on critical paths and edge cases
6. Regularly run tests during development
