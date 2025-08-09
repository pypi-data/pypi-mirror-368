# Contributing to ServiceTitan Python API Client

Thank you for your interest in contributing to the ServiceTitan Python API Client! This document provides guidelines for contributing to the project.

## 🚀 Quick Start for Contributors

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of ServiceTitan API

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/n90-co/servicetitan-pyapi.git
   cd servicetitan-pyapi
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   pip install pytest>=7.0.0 pytest-mock requests-mock
   ```

4. **Run tests to verify setup:**
   ```bash
   python -m pytest tests/ -v
   ```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following our coding standards**

3. **Write or update tests for your changes**

4. **Run the test suite:**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

## 📖 Development Guidelines

### Code Style

- **PEP 8 compliance**: Follow Python style guidelines
- **Type hints**: Use type annotations for all public APIs
- **Docstrings**: Use Google-style docstrings for all public methods
- **Naming**: Use descriptive, clear names for variables and functions

#### Example:
```python
def get_customers_batch(self, 
                       continuation_token: Optional[str] = None,
                       include_recent_changes: bool = False) -> ExportResponse:
    """
    Retrieve a single batch of customers from ServiceTitan.
    
    Args:
        continuation_token: Token from previous export to continue from
        include_recent_changes: If True, get recent changes quicker but may see duplicates
        
    Returns:
        ExportResponse with batch data and continuation token for next call
        
    Raises:
        requests.HTTPError: If the API request fails
    """
```

### Testing Requirements

- **All new code must have tests** with minimum 90% coverage
- **Test naming**: Use descriptive test names that explain what is being tested
- **Test structure**: Follow the Arrange-Act-Assert pattern
- **Mocking**: Use mocks for external API calls

#### Test Example:
```python
def test_get_customers_batch_with_continuation_token(self, mock_get, customers_client):
    """Test get_customers_batch with continuation token parameter."""
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {"data": [...], "hasMore": True}
    mock_get.return_value = mock_response
    
    # Act
    result = customers_client.get_batch(continuation_token="test_token")
    
    # Assert
    assert isinstance(result, ExportResponse)
    mock_get.assert_called_once_with(..., params={"from": "test_token"})
```

### Architecture Principles

1. **Single Responsibility**: Each class/module should have one clear purpose
2. **DRY (Don't Repeat Yourself)**: Reuse common functionality in BaseClient
3. **Consistent API**: All client classes should follow the same patterns
4. **Error Handling**: Proper exception handling with meaningful error messages

## 🎯 Types of Contributions

### 🐛 Bug Fixes
- Fix issues in existing functionality
- Add regression tests
- Update documentation if needed

### ✨ New Features
- Add support for new ServiceTitan API endpoints
- Enhance existing functionality
- Improve performance or usability

### 📚 Documentation
- Improve README, docstrings, or examples
- Add tutorials or guides
- Fix typos or unclear explanations

### 🧪 Testing
- Add missing test coverage
- Improve test quality or performance
- Add integration tests

## 📝 Commit Message Guidelines

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or modifying tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

### Examples:
```
feat(customers): add support for customer notes endpoint
fix(auth): handle token refresh edge case
docs(readme): add installation instructions
test(jobs): add integration tests for jobs client
```

## 🔍 Pull Request Process

1. **Ensure your PR:**
   - Has a clear title and description
   - Includes tests for new functionality
   - Updates documentation if needed
   - Passes all existing tests
   - Follows coding standards

2. **PR Description should include:**
   - What changes were made and why
   - How to test the changes
   - Any breaking changes
   - Related issue numbers

3. **Review Process:**
   - All PRs require review before merging
   - Address feedback promptly
   - Keep PRs focused and reasonably sized

## 🌟 Areas Where We Need Help

### High Priority
- **New API Endpoints**: ServiceTitan regularly adds new endpoints
- **Error Handling**: Better retry logic and error messages  
- **Performance**: Optimize pagination and caching
- **Documentation**: More examples and tutorials

### Medium Priority
- **Type Safety**: Improve type annotations and validation
- **Logging**: Better debugging and monitoring capabilities
- **CLI Tools**: Command-line interface for common operations

### Good First Issues
- **Add missing docstrings**
- **Improve test coverage**
- **Fix documentation typos**
- **Add usage examples**

## 📞 Getting Help

- **Create an issue** for bugs or feature requests
- **Start a discussion** for questions or ideas
- **Check existing issues** before creating new ones

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor statistics

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional tone

Thank you for contributing to making ServiceTitan API integration easier for everyone! 🚀
