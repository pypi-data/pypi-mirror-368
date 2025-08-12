# Contributing to MCP CSV Database Server

We welcome contributions to the MCP CSV Database Server! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/mcp-csv-database.git
   cd mcp-csv-database
   ```

3. Set up the development environment:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installing Dependencies

```bash
# Install package in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/mcp_csv_database

# Run specific test file
pytest tests/test_server.py

# Run with verbose output
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black src/ tests/ examples/

# Sort imports with isort
isort src/ tests/ examples/

# Lint with flake8
flake8 src/ tests/ examples/

# Type checking with mypy
mypy src/
```

## Making Changes

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards
3. Add tests for any new functionality
4. Update documentation if necessary
5. Run the test suite to ensure everything works
6. Commit your changes with a descriptive message

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length to 100 characters maximum

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and error cases

### Documentation

- Update the README.md if you add new features
- Document any new command-line options
- Include examples for new functionality
- Update docstrings for modified functions

## Submitting Changes

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub with:
   - Clear description of the changes
   - Reference to any related issues
   - Screenshots if applicable
   - Test results

## Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Follow the existing code style
- Write clear commit messages

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or stack traces
- Sample data if relevant

## Feature Requests

We welcome feature requests! Please:

- Check if the feature already exists or is planned
- Describe the use case clearly
- Provide examples of how it would be used
- Consider contributing the implementation

## Code of Conduct

Please note that this project follows a Code of Conduct. By participating, you agree to uphold this code:

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a positive community
- Report any unacceptable behavior

## Development Tips

### Testing with Sample Data

Create sample CSV files for testing:

```python
import pandas as pd
import tempfile

# Create sample data
df = pd.DataFrame({
    'column1': ['value1', 'value2'],
    'column2': [1, 2]
})

# Save to temporary file
with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
    df.to_csv(f.name, index=False)
    # Use f.name as your test CSV file
```

### Running the Server Locally

```bash
# Run with sample data
python -m mcp_csv_database.server --csv-folder ./examples/sample_data

# Run with different transport
python -m mcp_csv_database.server --transport sse --port 8080
```

## Release Process

1. Update version in `pyproject.toml` and `src/mcp_csv_database/__init__.py`
2. Update `CHANGELOG.md` with new features and fixes
3. Create a new release on GitHub
4. The package will be automatically published to PyPI

## Questions?

If you have questions about contributing:

- Check the existing issues and discussions
- Create a new issue with the "question" label
- Reach out to the maintainers

Thank you for contributing to MCP CSV Database Server!