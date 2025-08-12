# Contributing to MCP Commander

Thank you for your interest in contributing to MCP Commander! This guide will help you get started with development and understand our contribution workflow.

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- Git
- GitHub account

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nmindz/mcp-commander.git
   cd mcp-commander
   ```

2. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Verify installation**:
   ```bash
   mcp --help
   pytest tests/
   ```

## 🔧 Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and checks**:
   ```bash
   # Run all tests
   pytest

   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration/

   # Run code quality checks
   pre-commit run --all-files

   # Type checking
   mypy src/mcpcommander
   ```

4. **Build and test package**:
   ```bash
   python -m build
   pip install dist/*.whl
   mcp --help  # Test CLI works
   ```

### Code Quality Standards

- **Code Formatting**: We use `black` and `ruff` for code formatting
- **Import Sorting**: `isort` keeps imports organized
- **Type Hints**: All public APIs must have type hints
- **Documentation**: Public functions need docstrings
- **Testing**: Aim for >85% test coverage

### Pre-commit Hooks

Our pre-commit configuration runs:
- Code formatting (black, ruff)
- Import sorting (isort)
- Type checking (mypy)
- Security scanning (bandit)
- Tests (pytest)
- Package build verification

## 🧪 Testing

### Test Structure

```
tests/
├── unit/          # Fast, isolated unit tests
├── integration/   # Component integration tests
├── e2e/          # End-to-end workflow tests
├── fixtures/     # Test data and fixtures
└── helpers/      # Test utilities
```

### Running Tests

```bash
# All tests
pytest

# Specific categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# With coverage
pytest --cov=mcpcommander --cov-report=html

# Specific test file
pytest tests/unit/test_manager.py

# Specific test function
pytest tests/unit/test_manager.py::test_add_server
```

### Writing Tests

- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and error cases

Example:
```python
def test_add_server_success(mock_config_manager):
    # Arrange
    manager = MCPManager()
    server_config = {"command": "test-server"}

    # Act
    manager.add_server("test", server_config)

    # Assert
    assert "test" in manager.list_servers()
```

## 📦 Package Release Process

### Automated Release (Recommended)

1. **Tag a release**:
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

2. **GitHub Actions handles**:
   - Running all tests across Python versions
   - Building package
   - Publishing to TestPyPI
   - Publishing to PyPI
   - Creating GitHub release

### Manual Release (Maintainers Only)

1. **Update version** in `pyproject.toml`
2. **Build package**:
   ```bash
   python -m build
   ```
3. **Test build**:
   ```bash
   twine check dist/*
   ```
4. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```
5. **Test installation**:
   ```bash
   pip install -i https://test.pypi.org/simple/ mcp-commander
   ```
6. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## 🏗️ Architecture

### Project Structure

```
src/mcpcommander/
├── cli/                 # Command-line interface
├── core/               # Core business logic
├── schemas/            # Data validation models
└── utils/              # Utility functions
```

### Key Components

- **MCPManager**: Main orchestration class
- **ConfigManager**: Configuration file handling
- **EditorHandlers**: Editor-specific implementations
- **ServerConfig**: Pydantic models for validation

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## 🐛 Issue Reporting

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Impact assessment

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## 📞 Getting Help

- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions
- **Security**: Email evandro@camargo.uk for security issues

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation

Thank you for contributing to MCP Commander!
