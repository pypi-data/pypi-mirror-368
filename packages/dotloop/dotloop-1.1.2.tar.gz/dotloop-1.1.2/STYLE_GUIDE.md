# Dotloop Python API Wrapper Style Guide

This document outlines the coding standards and conventions for the Dotloop Python API wrapper project. All contributors should follow these guidelines to ensure consistency and maintainability.

## Table of Contents

1. [General Principles](#general-principles)
2. [Code Formatting](#code-formatting)
3. [Import Organization](#import-organization)
4. [Type Hints](#type-hints)
5. [Documentation](#documentation)
6. [Naming Conventions](#naming-conventions)
7. [Class Structure](#class-structure)
8. [Method Implementation](#method-implementation)
9. [Error Handling](#error-handling)
10. [Enums](#enums)
11. [Testing](#testing)
12. [File Organization](#file-organization)

## General Principles

- **Consistency**: Follow established patterns in the codebase
- **Readability**: Code should be self-documenting and easy to understand
- **Type Safety**: Use comprehensive type hints throughout
- **Documentation**: All public APIs must have Google-style docstrings
- **Testing**: Maintain 100% test coverage
- **Error Handling**: Use custom exceptions with meaningful messages

## Code Formatting

### Tools Configuration
- **Black**: Line length 88 characters, target Python 3.8+
- **isort**: Black-compatible profile, multi-line output 3
- **flake8**: Standard configuration
- **mypy**: Strict type checking enabled

### Line Length
- Maximum 88 characters per line (Black default)
- Break long lines at logical points
- Use parentheses for line continuation when needed

### Spacing
```python
# Good
def method(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Method with proper spacing."""
    return {"key": "value"}

# Bad
def method(self,param1:str,param2:Optional[int]=None)->Dict[str,Any]:
    return {"key":"value"}
```

## Import Organization

Follow this order (enforced by isort):
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
"""Module docstring."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv

from .base_client import BaseClient
from .exceptions import DotloopError
```

## Type Hints

### Required Type Hints
- All function/method parameters
- All function/method return types
- Class attributes when not obvious
- Complex variable assignments

```python
def search_teams(
    self,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    sort_direction: Optional[Union[SortDirection, str]] = None,
    team_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Search teams with proper type hints."""
    params: Dict[str, Any] = {}
    # Implementation...
```

### Type Hint Patterns
- Use `Optional[T]` for nullable parameters
- Use `Union[EnumType, str]` for enum parameters that accept strings
- Use `Dict[str, Any]` for API response data
- Use `List[T]` for list parameters
- Use `Union[List[T], T]` for parameters that accept single item or list

## Documentation

### Module Docstrings
```python
"""Brief description of the module.

Longer description if needed, explaining the module's purpose
and main functionality.
"""
```

### Class Docstrings
```python
class TeamsClient(BaseClient):
    """Client for teams API endpoints.

    This client provides access to team search functionality and team details.
    Note: This uses a different base URL than the main Dotloop API.
    """
```

### Method Docstrings
Use Google-style docstrings with complete parameter and return documentation:

```python
def search_teams(
    self,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[Union[TeamStatus, str]] = None,
) -> Dict[str, Any]:
    """Search teams given a set of criteria.

    Args:
        page_number: Page number for pagination (default: 0)
        page_size: Number of results per page (default: 20, min: 1)
        status: Filter by team status (ACTIVE or INACTIVE)

    Returns:
        Dictionary containing team search results with pagination information

    Raises:
        DotloopError: If the API request fails
        ValidationError: If parameters are invalid

    Example:
        ```python
        # Search for active teams
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            page_size=50
        )
        ```
    """
```

### Documentation Requirements
- All public methods must have docstrings
- Include parameter descriptions with types and defaults
- Document return value structure
- List possible exceptions
- Provide usage examples for complex methods
- Use proper Markdown formatting in examples

## Naming Conventions

### Files and Modules
- Use snake_case for file names: `transaction_builder.py`
- Module names should be descriptive and concise

### Classes
- Use PascalCase: `TransactionBuilderClient`
- Client classes should end with "Client": `TeamsClient`
- Exception classes should end with "Error": `ValidationError`

### Methods and Functions
- Use snake_case: `search_teams()`, `get_team_without_agents()`
- Use descriptive names that indicate the action
- Prefix with HTTP method when appropriate: `get_`, `post_`, `put_`, `delete_`

### Variables
- Use snake_case: `page_number`, `sort_direction`
- Use descriptive names, avoid abbreviations
- Constants use UPPER_SNAKE_CASE: `DEFAULT_PAGE_SIZE`

### Parameters
- API parameter names should match the API specification
- Use camelCase for API parameters: `pageNumber`, `sortDirection`
- Use snake_case for Python parameter names, convert in method body

## Class Structure

### Client Class Pattern
```python
class ExampleClient(BaseClient):
    """Client for example API endpoints."""

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
        """
        # Set appropriate base URL for this client
        example_base_url = base_url or "https://api.example.com/v1"
        super().__init__(api_key=api_key, base_url=example_base_url)

    # Public methods in logical order
    # GET methods first, then POST, PUT, PATCH, DELETE
```

### Property-based Client Access
```python
@property
def example_client(self) -> ExampleClient:
    """Access to example endpoints.

    Returns:
        ExampleClient instance
    """
    if self._example_client is None:
        self._example_client = ExampleClient(
            api_key=self._api_key, base_url=self._base_url
        )
    return self._example_client
```

## Method Implementation

### Parameter Processing Pattern
```python
def search_method(
    self,
    required_param: str,
    optional_param: Optional[int] = None,
    enum_param: Optional[Union[MyEnum, str]] = None,
    list_param: Optional[List[Union[MyEnum, str]]] = None,
) -> Dict[str, Any]:
    """Method with standard parameter processing."""
    params: Dict[str, Any] = {}

    # Required parameters (validate if needed)
    # No need to add to params dict for path parameters

    # Optional simple parameters
    if optional_param is not None:
        params["optionalParam"] = optional_param

    # Enum parameters
    if enum_param is not None:
        if isinstance(enum_param, MyEnum):
            params["enumParam"] = enum_param.value
        else:
            params["enumParam"] = enum_param

    # List parameters with enum support
    if list_param is not None:
        params["listParam"] = [
            item.value if isinstance(item, MyEnum) else item
            for item in list_param
        ]

    return self.get("endpoint", params=params)
```

### Date Parameter Handling
```python
# For date parameters
if date_param is not None:
    if isinstance(date_param, date):
        params["dateParam"] = date_param.isoformat()
    else:
        params["dateParam"] = date_param
```

## Error Handling

### Exception Hierarchy
```python
class DotloopError(Exception):
    """Base exception for all Dotloop API errors."""

class AuthenticationError(DotloopError):
    """Raised when authentication fails."""

class ValidationError(DotloopError):
    """Raised when request validation fails."""
```

### Error Documentation
- Document all possible exceptions in method docstrings
- Use specific exception types when appropriate
- Include helpful error messages with context

## Enums

### Enum Definition Pattern
```python
class SortDirection(Enum):
    """Sort direction options."""

    ASC = "ASC"
    DESC = "DESC"


class TeamStatus(Enum):
    """Team status options."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
```

### Enum Usage
- Use descriptive enum names
- Values should match API specification exactly
- Include docstring describing the enum's purpose
- Export enums in `__init__.py` for public use

## Testing

### Test File Structure
```python
"""Tests for the example client."""

import pytest
import responses

from dotloop.example import ExampleClient
from dotloop.exceptions import DotloopError


class TestExampleClientInit:
    """Test ExampleClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        # Test implementation


class TestExampleClientMethods:
    """Test ExampleClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = ExampleClient(api_key="test_key")

    @responses.activate
    def test_method_success(self) -> None:
        """Test successful method call."""
        # Test implementation
```

### Testing Requirements
- 100% code coverage required
- Test all success paths
- Test all error conditions
- Use `responses` library for HTTP mocking
- Test parameter validation and conversion
- Test enum handling
- Include integration tests where appropriate

### Test Naming
- Test classes: `TestClassName`
- Test methods: `test_method_name_condition`
- Use descriptive names that explain what is being tested

## File Organization

### Directory Structure
```
dotloop/
├── __init__.py          # Package exports
└── py.typed          # Type hint marker

tests/
├── __init__.py
```

### Module Organization
- One client class per module
- Related enums in the same module as the client
- Keep modules focused and cohesive
- Export public APIs through `__init__.py`

### Import/Export Pattern
```python
# In client module
from .base_client import BaseClient

# In __init__.py
from .example import ExampleClient, ExampleEnum

__all__ = [
    "ExampleClient",
    "ExampleEnum",
    # ... other exports
]
```

## Version Management

### Version Updates
- Update version in `pyproject.toml`
- Update version in `__init__.py`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Document changes in release notes

## Documentation Updates

### When Adding New Endpoints
1. Update the appropriate client class
2. Add comprehensive docstrings with examples
3. Update `__init__.py` exports if needed
4. Add/update tests with 100% coverage
5. Update API documentation in `docs/` directory
6. Mark endpoint as completed in `tasks/` files

This style guide ensures consistency across the Dotloop API wrapper codebase and should be followed for all new implementations and modifications.
