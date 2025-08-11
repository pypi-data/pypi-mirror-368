# Dotloop Python API Wrapper

[![PyPI version](https://badge.fury.io/py/dotloop.svg)](https://badge.fury.io/py/dotloop)
[![Python Support](https://img.shields.io/pypi/pyversions/dotloop.svg)](https://pypi.org/project/dotloop/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Tests](https://github.com/theperrygroup/dotloop/workflows/Tests/badge.svg)](https://github.com/theperrygroup/dotloop/actions)
[![Coverage](https://codecov.io/gh/theperrygroup/dotloop/branch/main/graph/badge.svg)](https://codecov.io/gh/theperrygroup/dotloop)

A comprehensive Python wrapper for the Dotloop API, providing easy access to real estate transaction management and document handling functionality.

## Features

- **Complete API Coverage**: Full support for all Dotloop API endpoints
- **Type Safety**: Comprehensive type hints and validation using Pydantic
- **Authentication**: Secure API key-based authentication
- **Error Handling**: Detailed error messages and custom exception types
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Documentation**: Extensive documentation with examples
- **Testing**: 100% test coverage with comprehensive test suite

## Installation

Install the package using pip:

```bash
pip install dotloop
```

For development installation with all dependencies:

```bash
pip install dotloop[dev]
```

## Quick Start

```python
import os
from dotloop import DotloopClient

# Initialize the client
client = DotloopClient(api_key=os.getenv("DOTLOOP_API_KEY"))

# Search for teams
teams = client.teams.search_teams(status="ACTIVE")
print(f"Found {len(teams['data'])} active teams")

# Get team details
team_id = teams['data'][0]['id']
team_details = client.teams.get_team_without_agents(team_id)
print(f"Team: {team_details['name']}")

# Search transactions
transactions = client.transactions.search_transactions(
    team_id=team_id,
    status="ACTIVE"
)
print(f"Found {len(transactions['data'])} active transactions")
```

## Authentication

The Dotloop API requires an API key for authentication. You can obtain an API key from the [Dotloop Developer Portal](https://www.dotloop.com/api).

### Setting up Authentication

1. **Environment Variable (Recommended)**:
   ```bash
   export DOTLOOP_API_KEY="your_api_key_here"
   ```

2. **Direct Parameter**:
   ```python
   client = DotloopClient(api_key="your_api_key_here")
   ```

3. **Configuration File**:
   Create a `.env` file in your project root:
   ```
   DOTLOOP_API_KEY=your_api_key_here
   ```

## API Coverage

This wrapper provides access to all major Dotloop API endpoints:

### Teams API
- Search teams
- Get team details
- Team management

### Transactions API  
- Search transactions
- Get transaction details
- Transaction management
- Document handling

### Transaction Builder API
- Create transactions
- Update transaction details
- Manage transaction workflow

### Agents API
- Agent search and management
- Agent profile information

### Directory API
- Contact management
- Directory search

## Configuration

The client can be configured with various options:

```python
from dotloop import DotloopClient

client = DotloopClient(
    api_key="your_api_key",
    base_url="https://api.dotloop.com/v1",  # Custom base URL
    timeout=30,  # Request timeout in seconds
    max_retries=3,  # Maximum number of retries
    retry_delay=1.0,  # Delay between retries
)
```

## Error Handling

The wrapper provides detailed error handling with custom exception types:

```python
from dotloop import DotloopClient, DotloopError, AuthenticationError

try:
    client = DotloopClient(api_key="invalid_key")
    teams = client.teams.search_teams()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except DotloopError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Rate Limiting

The wrapper automatically handles rate limiting according to Dotloop's API limits:

- Built-in retry logic with exponential backoff
- Automatic rate limit detection and handling
- Configurable retry attempts and delays

## Development

### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/theperrygroup/dotloop.git
   cd dotloop
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dotloop --cov-report=html

# Run specific test file
pytest tests/test_teams.py

# Run with verbose output
pytest -v
```

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Format code
black dotloop tests

# Sort imports
isort dotloop tests

# Lint code
flake8 dotloop tests

# Type checking
mypy dotloop

# Security scan
bandit -r dotloop
```

### Building and Publishing

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style

This project follows the [Black](https://black.readthedocs.io/) code style with:
- Line length: 88 characters
- Import sorting with [isort](https://pycqa.github.io/isort/)
- Type hints for all public APIs
- Google-style docstrings

## Documentation

- [API Documentation](https://dotloop.readthedocs.io)
- [Dotloop API Reference](https://www.dotloop.com/api/docs)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/theperrygroup/dotloop/issues)
- [Documentation](https://dotloop.readthedocs.io)
- [Dotloop API Support](https://www.dotloop.com/api/support)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Related Projects

- [Dotloop API Documentation](https://www.dotloop.com/api/docs)
- [Real Estate API Tools](https://github.com/theperrygroup)

---

Made with ❤️ by [The Perry Group](https://theperry.group) 