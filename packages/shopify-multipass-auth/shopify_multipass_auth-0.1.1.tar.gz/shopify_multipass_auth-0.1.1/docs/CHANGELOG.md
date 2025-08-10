# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-08-09

### Added
- Initial release of shopify-multipass
- `MultiPass` class for generating Shopify multipass tokens
- `get_token_only()` method for generating tokens only
- `get_login_url_with_token()` method for creating URLs from existing tokens
- `generate_login_url()` method for complete workflow
- Email and domain validation
- Comprehensive error handling
- Type hints support
- Extensive test coverage
- Documentation and examples

### Security
- Secure token generation using AES encryption and HMAC signatures
- Input validation for email addresses and domains
- Protection against common security vulnerabilities

[Unreleased]: https://github.com/yourusername/shopify-multipass/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/shopify-multipass/releases/tag/v0.1.0
