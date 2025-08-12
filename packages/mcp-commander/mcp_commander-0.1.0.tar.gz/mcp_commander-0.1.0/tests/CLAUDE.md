# Testing Context - mcpCommander/tests

## Testing Strategy Overview

This directory will contain comprehensive testing infrastructure for the MCP Commander project, following enterprise-grade testing patterns observed in the jira-mcp reference implementation.

## Current Testing State

**Status**: No testing infrastructure currently exists
**Priority**: Critical - Testing is essential for production readiness

## Target Testing Architecture

### Directory Structure (Planned)
```
tests/
├── CLAUDE.md                    # This file - testing context
├── conftest.py                  # Pytest configuration and fixtures
├── __init__.py                  # Package initialization
├── unit/                        # Unit tests for individual components
│   ├── __init__.py
│   ├── test_manager.py          # MCPManager class tests
│   ├── test_config.py           # Configuration handling tests
│   ├── test_cli.py              # CLI interface tests
│   └── test_validators.py       # Input validation tests
├── integration/                 # Integration tests
│   ├── __init__.py
│   ├── test_editor_integration.py   # Editor config file manipulation
│   ├── test_cross_platform.py      # Platform-specific behavior
│   └── test_config_migration.py    # Configuration migration tests
├── e2e/                         # End-to-end workflow tests
│   ├── __init__.py
│   ├── test_full_workflow.py    # Complete add/remove/list workflows
│   ├── test_error_scenarios.py  # Error handling and edge cases
│   └── test_real_editors.py     # Tests with actual editor installations
├── fixtures/                    # Test data and mock configurations
│   ├── __init__.py
│   ├── sample_configs.py        # Sample editor configurations
│   ├── mock_responses.py        # Mock data for external services
│   └── test_environments.py     # Test environment configurations
└── helpers/                     # Test utilities and helpers
    ├── __init__.py
    ├── mock_filesystem.py       # Filesystem mocking utilities
    ├── assertion_helpers.py     # Custom assertions
    └── test_factories.py        # Test data factories
```

## Testing Framework Selection

### Primary Framework: pytest
**Rationale**: Matches jira-mcp testing approach and provides:
- Simple, pythonic test writing
- Powerful fixture system
- Extensive plugin ecosystem
- Excellent coverage reporting
- CI/CD integration support

### Supporting Tools
```python
# Core testing dependencies (planned)
pytest>=7.0.0              # Main testing framework
pytest-cov>=4.0.0          # Coverage reporting
pytest-mock>=3.10.0        # Mocking framework
pytest-xdist>=3.0.0        # Parallel test execution
pytest-timeout>=2.1.0      # Test timeout handling
```

### Additional Quality Tools
```python
# Code quality and testing support
black>=22.0.0              # Code formatting
mypy>=1.0.0               # Type checking
flake8>=5.0.0             # Linting
coverage>=7.0.0           # Coverage analysis
```

## Test Categories and Coverage Goals

### 1. Unit Tests (90%+ coverage target)
**Scope**: Individual functions and methods in isolation

**Key Components to Test**:
- `MCPManager` class methods
- Configuration loading and validation
- JSON path manipulation
- CLI argument parsing
- Error handling functions

**Example Test Structure**:
```python
# test_manager.py
class TestMCPManager:
    def test_init_loads_config(self, mock_config_file):
        manager = MCPManager(mock_config_file.path)
        assert manager.config is not None

    def test_add_server_simple_command(self, manager, temp_config):
        manager.add_server("test", "/path/to/server")
        assert "test" in manager.list_servers()

    def test_add_server_invalid_editor_raises_error(self, manager):
        with pytest.raises(ValueError, match="Unknown editor"):
            manager.add_server("test", "/path", "invalid-editor")
```

### 2. Integration Tests (80%+ coverage target)
**Scope**: Component interaction and external dependencies

**Key Integration Points**:
- File system operations (config file read/write)
- Cross-platform path handling
- Editor-specific configuration formats
- Configuration migration scenarios

**Example Test Structure**:
```python
# test_editor_integration.py
class TestEditorIntegration:
    def test_claude_code_config_creation(self, temp_directory):
        manager = MCPManager()
        manager.add_server("test", "/path", "claude-code")

        claude_config = temp_directory / ".claude.json"
        assert claude_config.exists()
        config_data = json.loads(claude_config.read_text())
        assert "mcpServers" in config_data
        assert config_data["mcpServers"]["test"]["command"] == "/path"
```

### 3. End-to-End Tests (70%+ coverage target)
**Scope**: Complete user workflows and system behavior

**Key Workflows to Test**:
- Complete server lifecycle (add → list → remove)
- Multi-editor operations
- Error recovery scenarios
- CLI interface complete workflows

**Example Test Structure**:
```python
# test_full_workflow.py
class TestCompleteWorkflows:
    def test_server_lifecycle_all_editors(self, clean_environment):
        # Add server to all editors
        result = run_cli(["add", "test-server", "/path/to/server"])
        assert result.exit_code == 0

        # Verify in all editors
        result = run_cli(["list"])
        assert "claude-code" in result.output
        assert "test-server" in result.output

        # Remove from specific editor
        result = run_cli(["remove", "test-server", "cursor"])
        assert result.exit_code == 0

        # Verify removal
        result = run_cli(["list", "cursor"])
        assert "test-server" not in result.output
```

## Test Fixtures and Utilities

### Configuration Fixtures
```python
# conftest.py
@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide temporary directory with sample config files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create sample editor configs
    claude_config = config_dir / ".claude.json"
    claude_config.write_text('{"mcpServers": {}}')

    return config_dir

@pytest.fixture
def mock_manager(temp_config_dir):
    """Provide MCPManager instance with test configuration."""
    config_path = temp_config_dir / "config.json"
    return MCPManager(str(config_path))
```

### Mock Utilities
```python
# helpers/mock_filesystem.py
class MockFilesystem:
    """Mock filesystem operations for testing."""

    def mock_editor_configs(self, editors: List[str]):
        """Mock editor configuration files."""
        for editor in editors:
            # Create appropriate mock files for each editor
            pass

    def simulate_permission_error(self, path: str):
        """Simulate file permission errors."""
        pass
```

## Testing Infrastructure

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=mcpcommander
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=25
    -ra
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = src/mcpcommander
omit =
    tests/*
    */venv/*
    */env/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Test Execution Strategy

### Development Testing
```bash
# Quick unit tests during development
pytest tests/unit -v

# Integration tests with coverage
pytest tests/integration --cov=mcpcommander

# Full test suite with coverage
pytest --cov=mcpcommander --cov-report=html

# Specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e
```

### CI/CD Testing
```bash
# Complete test suite for CI/CD
pytest tests/ --cov=mcpcommander --cov-report=xml --junitxml=test-results.xml

# Performance and timeout testing
pytest tests/ --timeout=300

# Parallel execution for speed
pytest tests/ -n auto
```

## Test Data Management

### Sample Configurations
```python
# fixtures/sample_configs.py
CLAUDE_CODE_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        }
    }
}

EDITOR_CONFIGS = {
    "claude-code": CLAUDE_CODE_CONFIG,
    "claude-desktop": {...},
    "cursor": {...}
}
```

### Mock Data Factories
```python
# helpers/test_factories.py
class ConfigFactory:
    @staticmethod
    def create_manager_config(editors: List[str] = None) -> Dict:
        """Create test manager configuration."""
        pass

    @staticmethod
    def create_server_config(command: str, args: List[str] = None) -> Dict:
        """Create test server configuration."""
        pass
```

## Error Testing Strategy

### Error Scenarios to Test
1. **File System Errors**:
   - Permission denied
   - Disk full
   - Invalid paths
   - Missing directories

2. **Configuration Errors**:
   - Invalid JSON
   - Missing required fields
   - Malformed editor configs
   - Schema validation failures

3. **CLI Errors**:
   - Invalid arguments
   - Missing parameters
   - Conflicting options
   - Help and usage display

### Error Assertion Patterns
```python
def test_invalid_config_raises_appropriate_error():
    with pytest.raises(ConfigurationError, match="Invalid JSON"):
        MCPManager("invalid-config.json")

def test_permission_error_provides_helpful_message():
    with pytest.raises(FilePermissionError) as exc_info:
        manager.add_server("test", "/path")
    assert "Permission denied" in str(exc_info.value)
    assert "Try running with elevated privileges" in str(exc_info.value)
```

## Performance Testing

### Performance Benchmarks
```python
# test_performance.py
class TestPerformance:
    def test_large_config_loading_performance(self, large_config):
        """Test performance with large configuration files."""
        start_time = time.time()
        manager = MCPManager(large_config)
        manager.list_servers()
        execution_time = time.time() - start_time

        assert execution_time < 1.0  # Should complete within 1 second

    def test_concurrent_operations(self):
        """Test thread safety and concurrent operations."""
        pass
```

## Pre-commit Integration

### Testing in Pre-commit Hooks
```yaml
# .pre-commit-config.yaml (future)
repos:
  - repo: local
    hooks:
      - id: unit-tests
        name: Run unit tests
        entry: pytest tests/unit
        language: system
        pass_filenames: false

      - id: type-check
        name: Type checking
        entry: mypy src/mcpcommander
        language: system
        pass_filenames: false
```

## Future Testing Enhancements

### Advanced Testing Features
1. **Property-based Testing**: Use hypothesis for edge case discovery
2. **Mutation Testing**: Verify test quality with mutation testing
3. **Visual Testing**: Screenshot testing for CLI output
4. **Load Testing**: Performance under high load scenarios
5. **Security Testing**: Input validation and security checks

### Test Analytics
- Test execution time tracking
- Flaky test identification
- Coverage trend analysis
- Test effectiveness metrics

---

*Testing strategy defined: 2025-08-11*
*Based on jira-mcp enterprise testing patterns*
*Target: 85%+ coverage with comprehensive test categories*
