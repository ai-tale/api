# Contributing to AI Tale API

Thank you for your interest in contributing to the AI Tale API! We welcome contributions from everyone.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before submitting a bug report:

1. Check if the issue has already been reported.
2. Make sure you're using the latest version.
3. Determine if the issue is with the API or another component.

When submitting a bug report, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior and what actually happened
- Any relevant logs or error messages
- Environment details (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! When submitting a feature request:

1. Use a clear, descriptive title
2. Explain in detail how the feature would work
3. Explain why this feature would be useful
4. Provide examples of how the feature would be used

### Pull Requests

1. Fork the repository and create a new branch
2. Make your changes
3. Add tests for your changes when applicable
4. Run the test suite to make sure everything passes
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ai-tale/api.git
   cd api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the development server:
   ```bash
   python run.py
   ```

### Using Docker

Alternatively, you can use Docker Compose:

```bash
docker-compose up
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Coding Standards

- Follow PEP 8 for Python code
- Write docstrings for all functions, classes, and modules
- Include type hints where possible
- Write tests for your code

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 