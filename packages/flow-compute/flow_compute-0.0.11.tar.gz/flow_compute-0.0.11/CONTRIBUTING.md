# Contributing to Flow SDK

We love your input! We want to make contributing to Flow SDK as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/flow-compute
cd flow-sdk

# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Code Style

- We use [Black](https://github.com/psf/black) for Python code formatting
- We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Run `black .` before committing
- Run `ruff check .` to check for common issues

## Testing

- Write tests for any new functionality
- Ensure all tests pass: `pytest`
- Aim for high test coverage
- Test edge cases and error conditions

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable
2. Update the CHANGELOG.md with your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## Any contributions you make will be under the Apache 2.0 License

When you submit code changes, your submissions are understood to be under the same [Apache 2.0 License](LICENSE.txt) that covers the project.

## Report bugs using GitHub Issues

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/mithrilcompute/flow/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License

By contributing, you agree that your contributions will be licensed under its Apache 2.0 License.