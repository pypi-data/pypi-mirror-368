# Testing Guide

## Running Tests

### Prerequisites

The Flow SDK uses `pytest` for testing. Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

### Running Tests Without Authentication

By default, the SDK tries to access the system keychain for stored API keys. 
To run tests without authentication prompts:

```bash
# Option 1: Tests automatically set FLOW_DISABLE_KEYCHAIN=1
uv run pytest tests/

# Option 2: Explicitly disable keychain access
FLOW_DISABLE_KEYCHAIN=1 uv run pytest tests/

# Option 3: Provide a test API key
Mithril_API_KEY=test-key uv run pytest tests/
```

### Test Categories

- **Unit tests**: `tests/unit/` - Fast, isolated tests
- **Integration tests**: `tests/integration/` - Tests with mocked external services
- **E2E tests**: `tests/e2e/` - Tests requiring real infrastructure (skipped by default)

### Common Issues

#### Authentication Prompts

If you see macOS Keychain prompts during tests, ensure:
1. `FLOW_DISABLE_KEYCHAIN=1` is set (automatic in pytest.ini)
2. You're using `uv run pytest` or `python -m pytest`

#### Missing Dependencies

Some tests require optional dependencies:
- Docker tests: Install `docker` package or tests will skip
- E2E tests: Require real Mithril API credentials

## Writing Tests

### Test Isolation

Tests should be self-contained and not rely on:
- System keychain access
- User configuration files
- Environment-specific settings

### Mocking Authentication

```python
def test_with_mock_auth(monkeypatch):
    # Disable keychain access
    monkeypatch.setenv("FLOW_DISABLE_KEYCHAIN", "1")
    
    # Provide test credentials
    monkeypatch.setenv("Mithril_API_KEY", "test-key")
    monkeypatch.setenv("Mithril_DEFAULT_PROJECT", "test-project")
    
    # Your test code here
```

### Best Practices

1. Use fixtures from `tests/fixtures/` for common test data
2. Mock external services rather than calling real APIs
3. Use `tmp_path` fixture for file system operations
4. Set explicit environment variables for each test's needs