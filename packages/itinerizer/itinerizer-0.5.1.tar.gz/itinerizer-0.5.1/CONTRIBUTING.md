# Contributing to Itinerizer

Thank you for your interest in contributing to Itinerizer! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the community's best interests

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/itinerizer.git
   cd itinerizer
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/original/itinerizer.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- Git

### Setting Up Your Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[all]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running the Development Server

For the FastAPI server:
```bash
uvicorn itinerizer.server.app:app --reload --port 8000
```

For the Flask web UI:
```bash
cd web_ui
python app.py
```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/itinerizer/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information (OS, Python version, etc.)
   - Error messages and stack traces

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue with the "enhancement" label
3. Describe the feature and its use case
4. Provide examples if possible

### Contributing Code

1. Find an issue to work on or create a new one
2. Comment on the issue to let others know you're working on it
3. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes following our coding standards
5. Write or update tests as needed
6. Update documentation if necessary
7. Commit your changes with clear messages

## Coding Standards

### Python Style Guide

We follow PEP 8 with these specifications:
- Maximum line length: 100 characters
- Use type hints for all functions
- Use docstrings for all public functions and classes

### Code Formatting

We use Black for code formatting:
```bash
black src/ tests/
```

### Linting

We use Flake8 for linting:
```bash
flake8 src/ tests/
```

### Type Checking

We use MyPy for type checking:
```bash
mypy src/
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Each group should be separated by a blank line.

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=itinerizer --cov-report=html
```

Run specific test file:
```bash
pytest tests/unit/test_models.py
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Place end-to-end tests in `tests/e2e/`
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data

Example test:
```python
def test_itinerary_creation_with_valid_data():
    """Test that an itinerary can be created with valid data."""
    # Arrange
    title = "Tokyo Business Trip"
    start_date = date(2025, 3, 15)
    end_date = date(2025, 3, 22)
    travelers = [create_test_traveler()]
    
    # Act
    itinerary = Itinerary(
        title=title,
        start_date=start_date,
        end_date=end_date,
        travelers=travelers
    )
    
    # Assert
    assert itinerary.title == title
    assert itinerary.start_date == start_date
    assert len(itinerary.travelers) == 1
```

## Documentation

### Docstrings

Use Google-style docstrings:
```python
def calculate_total_price(segments: List[Segment]) -> Optional[Money]:
    """Calculate the total price from a list of segments.
    
    Args:
        segments: List of travel segments
        
    Returns:
        Total price as Money object, or None if no prices
        
    Raises:
        ValueError: If segments have mixed currencies
    """
```

### README Updates

Update the README.md when:
- Adding new features
- Changing installation instructions
- Modifying API endpoints
- Adding new dependencies

### API Documentation

- Keep OpenAPI/Swagger documentation up to date
- Document all endpoints with descriptions
- Provide example requests and responses

## Submitting Changes

### Commit Messages

Follow the Conventional Commits specification:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Example:
```
feat: add support for train segments

- Add TrainSegment model
- Update segment validation
- Add tests for train segments
```

### Pull Request Process

1. Update your branch with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request with:
   - Clear title describing the change
   - Reference to related issues
   - Description of changes made
   - Screenshots for UI changes
   - Test results

4. Wait for review and address feedback

5. Once approved, your PR will be merged

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main
- [ ] No merge conflicts

## Release Process

### Version Numbering

We use Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, backwards compatible

### Release Steps

1. Update version in:
   - `pyproject.toml`
   - `src/itinerizer/__version__.py`
   - API documentation

2. Update CHANGELOG.md

3. Create a release branch:
   ```bash
   git checkout -b release/v0.5.0
   ```

4. Create and push a tag:
   ```bash
   git tag v0.5.0
   git push origin v0.5.0
   ```

5. Build and publish to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Getting Help

- Check the [documentation](https://itinerizer.readthedocs.io)
- Ask questions in [Discussions](https://github.com/yourusername/itinerizer/discussions)
- Join our [Discord server](https://discord.gg/itinerizer)
- Email: contact@itinerizer.io

## Recognition

Contributors will be recognized in:
- The AUTHORS file
- The project README
- Release notes

Thank you for contributing to Itinerizer!