# Dotloop Python API Wrapper

A comprehensive Python wrapper for the Dotloop API v2, providing easy access to real estate transaction management and document handling functionality.

## Features

- **Complete API Coverage**: Implements all major Dotloop API endpoints
- **Type Safety**: Full type hints and Pydantic validation
- **Error Handling**: Comprehensive exception handling with detailed error messages
- **Easy to Use**: Intuitive client interface with method chaining
- **Well Documented**: Extensive docstrings and examples
- **Testing**: 100% test coverage with pytest

## Installation

```bash
pip install dotloop-api
```

## Quick Start

```python
from dotloop import DotloopClient, TransactionType, LoopStatus

# Initialize the client
client = DotloopClient(api_key="your_api_key")

# Or use environment variable DOTLOOP_API_KEY
client = DotloopClient()

# Get account information
account = client.account.get_account()
print(f"Account: {account['data']['firstName']} {account['data']['lastName']}")

# List profiles
profiles = client.profile.list_profiles()
for profile in profiles['data']:
    print(f"Profile: {profile['name']}")

# Create a new loop
loop = client.loop_it.create_loop(
    name="123 Main St Property",
    transaction_type=TransactionType.PURCHASE_OFFER,
    status=LoopStatus.PRE_OFFER,
    profile_id=123,
    street_number="123",
    street_name="Main St",
    city="San Francisco",
    state="CA",
    zip_code="94105"
)
```

## Authentication

The Dotloop API uses OAuth 2.0 Bearer tokens for authentication. You can obtain an access token through the OAuth flow and then use it with this wrapper.

### Setting up Authentication

1. **Environment Variable** (Recommended):
   ```bash
   export DOTLOOP_API_KEY="your_access_token"
   ```

2. **Direct Parameter**:
   ```python
   client = DotloopClient(api_key="your_access_token")
   ```

## Available Endpoints

### Account
- `client.account.get_account()` - Get current account details

### Profiles
- `client.profile.list_profiles()` - List all profiles
- `client.profile.get_profile(profile_id)` - Get profile by ID
- `client.profile.create_profile(...)` - Create a new profile
- `client.profile.update_profile(profile_id, ...)` - Update profile

### Loops
- `client.loop.list_loops(profile_id, ...)` - List loops for a profile
- `client.loop.get_loop(profile_id, loop_id)` - Get loop by ID
- `client.loop.create_loop(profile_id, ...)` - Create a new loop
- `client.loop.update_loop(profile_id, loop_id, ...)` - Update loop

### Loop-It (Simplified Loop Creation)
- `client.loop_it.create_loop(...)` - Create loop with property and participant data

### Contacts
- `client.contact.list_contacts()` - List all contacts
- `client.contact.get_contact(contact_id)` - Get contact by ID
- `client.contact.create_contact(...)` - Create a new contact
- `client.contact.update_contact(contact_id, ...)` - Update contact
- `client.contact.delete_contact(contact_id)` - Delete contact

## Examples

### Creating a Complete Real Estate Transaction

```python
from dotloop import DotloopClient, TransactionType, LoopStatus, ParticipantRole

client = DotloopClient()

# Create a comprehensive loop with property and participants
loop = client.loop_it.create_loop(
    name="John Doe - 456 Oak Avenue",
    transaction_type=TransactionType.PURCHASE_OFFER,
    status=LoopStatus.PRE_OFFER,
    profile_id=123,
    
    # Property information
    street_number="456",
    street_name="Oak Avenue",
    city="Los Angeles",
    state="CA",
    zip_code="90210",
    
    # Participants
    participants=[
        {
            "fullName": "John Doe",
            "email": "john.doe@example.com",
            "role": ParticipantRole.BUYER.value
        },
        {
            "fullName": "Jane Smith",
            "email": "jane.smith@realty.com",
            "role": ParticipantRole.BUYING_AGENT.value
        },
        {
            "fullName": "Bob Johnson",
            "email": "bob.johnson@realty.com",
            "role": ParticipantRole.LISTING_AGENT.value
        }
    ],
    
    # Optional MLS information
    mls_property_id="ML123456",
    template_id=1001
)

print(f"Created loop: {loop['data']['loopUrl']}")
```

### Managing Contacts

```python
# Create a new contact
contact = client.contact.create_contact(
    first_name="Alice",
    last_name="Johnson",
    email="alice.johnson@example.com",
    phone="+1 (555) 123-4567",
    company="Johnson Realty"
)

# Update the contact
updated_contact = client.contact.update_contact(
    contact_id=contact['data']['id'],
    phone="+1 (555) 987-6543",
    company="Johnson Premium Realty"
)

# List all contacts
contacts = client.contact.list_contacts()
for contact in contacts['data']:
    print(f"{contact['firstName']} {contact['lastName']} - {contact.get('email', 'No email')}")
```

### Working with Profiles

```python
# Create a new profile
profile = client.profile.create_profile(
    name="My Real Estate Business",
    company="ABC Realty",
    phone="+1 (555) 123-4567",
    address="123 Business Ave",
    city="New York",
    state="NY",
    zip_code="10001"
)

# List loops for this profile
loops = client.loop.list_loops(
    profile_id=profile['data']['id'],
    batch_size=50,
    sort="updated:desc",
    include_details=True
)
```

## Error Handling

The wrapper provides comprehensive error handling with specific exception types:

```python
from dotloop import DotloopClient
from dotloop.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError
)

client = DotloopClient()

try:
    account = client.account.get_account()
except AuthenticationError:
    print("Invalid or expired API token")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except RateLimitError:
    print("Rate limit exceeded, please wait")
```

## Enums and Constants

The wrapper provides enums for common values:

```python
from dotloop import (
    TransactionType,
    LoopStatus,
    ParticipantRole,
    SortDirection
)

# Transaction types
TransactionType.PURCHASE_OFFER
TransactionType.LISTING_FOR_SALE
TransactionType.PURCHASED
TransactionType.SOLD

# Loop statuses
LoopStatus.PRE_OFFER
LoopStatus.UNDER_CONTRACT
LoopStatus.SOLD
LoopStatus.ARCHIVED

# Participant roles
ParticipantRole.BUYER
ParticipantRole.SELLER
ParticipantRole.LISTING_AGENT
ParticipantRole.BUYING_AGENT
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/dotloop-python.git
cd dotloop-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=dotloop --cov-report=html
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dotloop

# Run specific test file
pytest tests/test_account.py

# Run with verbose output
pytest -v
```

## API Reference

For detailed API documentation, see the [official Dotloop API documentation](https://dotloop.github.io/public-api/).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [API Documentation](https://dotloop.github.io/public-api/)
- **Issues**: [GitHub Issues](https://github.com/your-org/dotloop-python/issues)
- **Email**: dev@theperry.group

## Changelog

### v1.0.0
- Initial release
- Complete implementation of core Dotloop API endpoints
- Account, Profile, Loop, Loop-It, and Contact management
- Comprehensive error handling and type safety
- 100% test coverage 