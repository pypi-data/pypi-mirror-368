# Contributing to Shopify Multipass

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. Clone your fork of the repository:
   ```bash
   git clone https://github.com/yourusername/shopify-multipass.git
   cd shopify-multipass
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Testing

Run the test suite to make sure everything works:

```bash
python -m unittest tests/test_multipass.py -v
```

### Writing Tests

- Add tests for any new functionality
- Ensure tests cover both success and error cases
- Test edge cases and boundary conditions
- Use descriptive test method names

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and small
- Use meaningful variable and function names

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/yourusername/shopify-multipass/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/shopify-multipass/issues/new).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature has already been requested
2. Clearly describe the feature and its use case
3. Explain how it would benefit users of the library
4. Consider if it fits within the scope of the project

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md).
