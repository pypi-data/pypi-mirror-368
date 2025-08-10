# Shopify Multipass

[![PyPI version](https://badge.fury.io/py/shopify-multipass.svg)](https://badge.fury.io/py/shopify-multipass)
[![Python versions](https://img.shields.io/pypi/pyversions/shopify-multipass.svg)](https://pypi.org/project/shopify-multipass/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for generating Shopify multipass tokens for customer authentication.

## Overview

This library provides a simple interface to generate Shopify multipass tokens, which allow you to authenticate customers on your Shopify store without requiring them to enter their credentials. Multipass is particularly useful for integrating external systems with Shopify stores while providing a seamless user experience.

## Features

- 🔐 Generate multipass tokens for customer authentication
- 🔗 Create complete login URLs with embedded tokens
- ✅ Validate email formats and Shopify domains
- 🛡️ Support for both `.myshopify.com` domains and custom domains
- 📝 Comprehensive error handling with descriptive messages
- 🔍 Type hints for better IDE support
- 🧪 Extensive test coverage

## Installation

Install from PyPI:

```bash
pip install shopify-multipass
```

Or install from source:

```bash
git clone https://github.com/yourusername/shopify-multipass.git
cd shopify-multipass
pip install -e .
```

### Requirements

- Python 3.7+
- pycryptodome>=3.20.0

## Quick Start

```python
from shopify_multipass import MultiPass

# Initialize with your Shopify multipass secret
multipass = MultiPass("your_multipass_secret_here")

# Generate a complete login URL (most common use case)
result = multipass.generate_login_url(
    email="customer@example.com",
    domain="your-shop.myshopify.com",
    return_to="https://your-shop.myshopify.com/pages/welcome"
)

if result["error"] == 0:
    print(f"Login URL: {result['redirect']}")
else:
    print(f"Error: {result['message']}")
```

## API Reference

### MultiPass Class

#### `__init__(secret: str)`

Initialize the multipass service with your Shopify multipass secret.

**Parameters:**
- `secret` (str): Your Shopify multipass secret key

**Raises:**
- `ValueError`: If secret is empty or None

#### `get_token_only(email: str, return_to: str) -> dict`

Generate only a multipass token for the given email and return URL.

**Parameters:**
- `email` (str): Customer email address
- `return_to` (str): URL to redirect to after authentication

**Returns:**
- `dict`: Response with error code and token or error message
  ```python
  # Success
  {"error": 0, "token": "generated_token_here"}
  
  # Error
  {"error": 1, "message": "Error description"}
  ```

#### `get_login_url_with_token(token: str, domain: str) -> dict`

Generate a login URL using an existing token and domain.

**Parameters:**
- `token` (str): Previously generated multipass token
- `domain` (str): Shopify domain for multipass authentication

**Returns:**
- `dict`: Response with error code and redirect URL or error message
  ```python
  # Success
  {"error": 0, "redirect": "https://domain.com/account/login/multipass/token"}
  
  # Error
  {"error": 1, "message": "Error description"}
  ```

#### `generate_login_url(email: str, domain: str, return_to: str) -> dict`

Generate a complete multipass login URL for a customer.

**Parameters:**
- `email` (str): Customer email address
- `domain` (str): Shopify domain for multipass authentication
- `return_to` (str): URL to redirect to after authentication

**Returns:**
- `dict`: Response with error code and redirect URL or error message

## Usage Examples

### Basic Token Generation

```python
from shopify_multipass import MultiPass

multipass = MultiPass("your_secret_key")

# Generate just a token
token_result = multipass.get_token_only(
    email="customer@example.com",
    return_to="https://shop.com/welcome"
)

if token_result["error"] == 0:
    token = token_result["token"]
    print(f"Generated token: {token}")
```

### Generate Login URL from Existing Token

```python
# Use a previously generated token
url_result = multipass.get_login_url_with_token(
    token="previously_generated_token",
    domain="your-shop.myshopify.com"
)

if url_result["error"] == 0:
    print(f"Login URL: {url_result['redirect']}")
```

### Complete Workflow

```python
from shopify_multipass import MultiPass

def authenticate_customer(email, shop_domain, welcome_page):
    multipass = MultiPass("your_multipass_secret")
    
    result = multipass.generate_login_url(
        email=email,
        domain=shop_domain,
        return_to=welcome_page
    )
    
    if result["error"] == 0:
        # Redirect customer to this URL
        return result["redirect"]
    else:
        # Handle error
        raise Exception(f"Authentication failed: {result['message']}")

# Usage
login_url = authenticate_customer(
    email="customer@example.com",
    shop_domain="mystore.myshopify.com",
    welcome_page="https://mystore.myshopify.com/pages/dashboard"
)
```

## Error Handling

All methods return a dictionary with an `error` field:
- `error: 0` - Success
- `error: 1` - Error occurred, check `message` field for details

Common error scenarios:
- Invalid or missing email address
- Invalid domain format
- Missing required parameters
- Encryption/signing errors

```python
result = multipass.generate_login_url(email, domain, return_to)

if result["error"] == 1:
    print(f"Error occurred: {result['message']}")
    # Handle error appropriately
else:
    # Use result["redirect"] or result["token"]
    pass
```

## Domain Validation

The library validates Shopify domains and supports:
- Standard Shopify domains: `shop-name.myshopify.com`
- Custom domains: `shop.example.com`
- URLs with or without protocol (automatically adds `https://`)

## Security Notes

1. **Keep your multipass secret secure** - Never expose it in client-side code
2. **Use HTTPS** - Always use secure connections for multipass URLs
3. **Validate return URLs** - Ensure return_to URLs are trusted domains
4. **Token expiration** - Multipass tokens have a limited lifetime (configurable in Shopify)

## Testing

Run the test suite:

```bash
python -m unittest tests/test_multipass.py -v
```

The test suite includes:
- Token generation and validation
- URL creation and formatting
- Email and domain validation
- Error handling scenarios
- Cryptographic operations

## Development

### Project Structure

```
shopify_multipass/
├── __init__.py          # Package initialization
├── multipass.py         # Main MultiPass class
└── __pycache__/

tests/
├── __init__.py
└── test_multipass.py    # Comprehensive test suite

requirements.txt         # Dependencies
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shopify-multipass.git
   cd shopify-multipass
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. Run tests:
   ```bash
   python -m unittest tests/test_multipass.py -v
   ```

### Building for PyPI

1. Install build tools:
   ```bash
   pip install build twine
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Shopify Multipass Setup

To use this library, you need to:

1. **Enable multipass in your Shopify admin:**
   - Go to Settings > Checkout
   - Scroll down to "Customer accounts"
   - Enable "Multipass"
   - Copy your multipass secret

2. **Configure your application:**
   ```python
   from shopify_multipass import MultiPass
   
   # Use your actual multipass secret from Shopify
   multipass = MultiPass("your_actual_multipass_secret_from_shopify")
   ```

3. **Set up your authentication flow:**
   ```python
   # In your application
   def shopify_login(request):
       email = request.user.email
       shop_domain = "your-shop.myshopify.com"
       return_url = "https://your-shop.myshopify.com/pages/welcome"
       
       result = multipass.generate_login_url(email, shop_domain, return_url)
       
       if result["error"] == 0:
           return redirect(result["redirect"])
       else:
           return JsonResponse({"error": result["message"]})
   ```

For more information about Shopify multipass, visit the [Shopify documentation](https://shopify.dev/docs/api/multipass).

## Support

- 📖 [Documentation](https://github.com/yourusername/shopify-multipass#readme)
- 🐛 [Bug Reports](https://github.com/yourusername/shopify-multipass/issues)
- 💬 [Discussions](https://github.com/yourusername/shopify-multipass/discussions)
- 📧 [Email Support](mailto:your.email@example.com)
