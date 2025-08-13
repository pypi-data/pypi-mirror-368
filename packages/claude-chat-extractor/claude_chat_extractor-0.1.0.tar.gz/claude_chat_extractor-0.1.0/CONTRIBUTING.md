# Contributing to Claude Conversation Extractor

Thank you for your interest in contributing to Claude Conversation Extractor! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- UV package manager
- Git

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-conversation-extractor.git
   cd claude-conversation-extractor
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/claude-conversation-extractor.git
   ```
4. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/your-bug-description
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the existing code style and patterns
- Add type hints where appropriate
- Include docstrings for new functions and classes

### 3. Test Your Changes

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/ --cov-report=html

# Run linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run type checking
uv run mypy src/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit Message Format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding or updating tests
- `refactor:` for code refactoring
- `style:` for formatting changes
- `perf:` for performance improvements

### 5. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reference to any related issues
- Screenshots if UI changes are involved

## 📋 Code Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function parameters and return values
- Keep functions small and focused on single responsibility
- Use descriptive variable and function names

### Code Quality

- All new code must have corresponding tests
- Maintain or improve test coverage
- Ensure all tests pass before submitting PR
- Follow SOLID principles where applicable

### Documentation

- Update relevant documentation for new features
- Add docstrings for new public functions and classes
- Update README.md if user-facing changes are made
- Keep implementation status documentation current

## 🧪 Testing Guidelines

### Writing Tests

- Test both success and failure scenarios
- Use descriptive test names that explain the expected behavior
- Mock external dependencies when appropriate
- Test edge cases and boundary conditions

### Test Structure

```python
def test_function_name_expected_behavior():
    """Test description of what this test verifies."""
    # Arrange
    input_data = "test input"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == "expected output"
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, etc.)
5. **Sample data** if applicable
6. **Error messages** and stack traces

## 💡 Feature Requests

For feature requests, please:

1. **Describe the feature** in detail
2. **Explain the use case** and why it's needed
3. **Provide examples** of how it would work
4. **Consider alternatives** and trade-offs

## 🔍 Review Process

1. **Automated checks** must pass (tests, linting, type checking)
2. **Code review** by maintainers
3. **Address feedback** and make requested changes
4. **Maintainer approval** required for merge

## 📚 Additional Resources

- [Project Requirements](docs/requirements.md)
- [Usage Guide](docs/usage.md)
- [Implementation Status](docs/implementation-status.md)
- [Python Development Guide](https://docs.python.org/3/)

## 🎯 Areas for Contribution

We welcome contributions in these areas:

- **Performance improvements** for large file processing
- **Additional output formats** (HTML, PDF, etc.)
- **Enhanced CLI features** (filters, search, etc.)
- **Better error handling** and user feedback
- **Documentation improvements** and examples
- **Test coverage** expansion
- **CI/CD pipeline** enhancements

## 🤝 Questions or Need Help?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Join our community channels (if available)

Thank you for contributing to making Claude Conversation Extractor better! 🎉
