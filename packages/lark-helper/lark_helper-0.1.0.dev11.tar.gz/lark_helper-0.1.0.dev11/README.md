# Lark Helper

[![PyPI version](https://badge.fury.io/py/lark-helper.svg)](https://badge.fury.io/py/lark-helper)
[![Python Support](https://img.shields.io/pypi/pyversions/lark-helper.svg)](https://pypi.org/project/lark-helper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for interacting with Lark (Feishu) APIs, providing both synchronous and asynchronous interfaces for seamless integration with Lark's collaboration platform.

## Features

- **Dual Interface Support**: Both synchronous and asynchronous API interfaces
- **Comprehensive API Coverage**: Support for Bitable, Messaging, File operations, and more
- **Token Management**: Automatic tenant access token management with refresh handling
- **Type Safety**: Full type hints and Pydantic model validation
- **Easy Integration**: Simple and intuitive API design
- **Enterprise Ready**: Built for production use with proper error handling

## Installation

### Using pip (recommended)

```bash
pip install lark-helper
```

### Using pip with extras

```bash
# Install with development dependencies
pip install "lark-helper[dev]"

# Install with testing dependencies
pip install "lark-helper[test]"

# Install with documentation dependencies
pip install "lark-helper[docs]"
```

### Using uv (faster installation)

```bash
uv pip install lark-helper
```

## Quick Start

### Synchronous Usage

```python
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1 import message, bitable

# Initialize token manager
token_manager = TenantAccessTokenManager(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# Send a message
from lark_helper.constants.message import MessageType, ReceiveIdType

message_id = message.send_message(
    token_manager=token_manager,
    receive_id="user_id_or_chat_id",
    receive_id_type=ReceiveIdType.USER_ID,
    message_type=MessageType.TEXT,
    content="Hello from Lark Helper!"
)
```

### Asynchronous Usage

```python
import asyncio
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1_async import message, bitable

async def main():
    # Initialize token manager
    token_manager = TenantAccessTokenManager(
        app_id="your_app_id",
        app_secret="your_app_secret"
    )
    
    # Send a message asynchronously
    message_id = await message.send_message(
        token_manager=token_manager,
        receive_id="user_id_or_chat_id",
        receive_id_type=ReceiveIdType.USER_ID,
        message_type=MessageType.TEXT,
        content="Hello from Lark Helper!"
    )
    
    # Work with Bitable asynchronously
    record = await bitable.add_bitable_record(
        token_manager=token_manager,
        app_token="your_app_token",
        table_id="your_table_id",
        fields={"Name": "Jane Doe", "Email": "jane@example.com"}
    )

# Run the async function
asyncio.run(main())
```

## API Coverage

### Messaging

- Send messages (text, rich text, images, etc.)
- Message content formatting
- Support for different recipient types (user, chat, email)

### Bitable (Multi-dimensional Tables)

- Create, read, update, delete records
- Search and filter records
- Manage table views
- Handle field types and validation

### File Operations

- Upload and download files
- File metadata management
- Batch file operations

### User Management

- User information retrieval
- User search and lookup

### Document Operations

- Document creation and editing
- Content management
- Collaborative editing support

## Token Management

The library automatically handles Lark tenant access tokens:

```python
from lark_helper.token_manager import TenantAccessTokenManager

token_manager = TenantAccessTokenManager(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# Token is automatically refreshed when needed
# No manual token management required
```

## Configuration

### Environment Variables

You can set your Lark app credentials using environment variables:

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

### Error Handling

The library provides comprehensive error handling:

```python
from lark_helper.exception import LarkHelperException

try:
    result = message.send_message(...)
except LarkHelperException as e:
    print(f"Lark API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Requirements

- Python 3.12+
- aiohttp (for async operations)
- requests (for sync operations)
- pydantic (for data validation)
- lark-oapi (official Lark SDK)

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/philo-veritas/lark-helper.git
cd lark-helper

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lark_helper

# Run async tests
pytest -m asyncio
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check

# Type checking
mypy src/lark_helper
```

### Building and Publishing

```bash
# Build the package
python -m build

# Check the built package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (for production)
twine upload dist/*
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## PyPI Package

This package is available on PyPI:

- **Package Page**: [lark-helper on PyPI](https://pypi.org/project/lark-helper/)

## Related Projects

- [lark-oapi](https://github.com/larksuite/oapi-sdk-python) - Official Lark Open API SDK
- [Lark Developer Documentation](https://open.feishu.cn/document/)

---

Made with ❤️ for the Lark developer community
