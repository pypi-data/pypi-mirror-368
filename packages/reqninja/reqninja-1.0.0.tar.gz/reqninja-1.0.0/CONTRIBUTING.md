# Contributing to ReqNinja

We welcome contributions to ReqNinja! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/vishal-ravi/reqninja.git
   cd reqninja
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,test]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the existing style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   pytest
   ```

4. **Run linting and formatting**
   ```bash
   black .
   isort .
   flake8 .
   mypy .
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use type hints where appropriate
- Write descriptive docstrings

## Testing

- Write unit tests for all new functionality
- Ensure test coverage remains high
- Use pytest for testing
- Use mocks for external dependencies

## Documentation

- Update README.md if adding new features
- Add docstrings to all public functions and classes
- Update CLI help text for new commands

## Submitting Changes

1. Ensure all tests pass
2. Ensure code follows style guidelines
3. Write clear commit messages
4. Submit a pull request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots if UI changes are involved

## Reporting Issues

When reporting issues, please include:

- ReqNinja version
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

Thank you for contributing to ReqNinja!
