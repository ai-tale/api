# AI Tale API

Official API service for the [AI Tale](https://aitale.tech/) platform - generating beautifully illustrated fairy tales using large language models.

## Overview

This API provides a flexible interface for the AI Tale story generation engine. It handles requests for creating new stories, retrieving existing ones, and managing user content.

## Features

- Story generation with customizable parameters
- Image generation for story illustrations
- User authentication and session management
- Story saving and retrieval
- Support for multiple languages and story styles

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)

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

## API Documentation

Full API documentation is available at `/docs` when running the server or in the [API_DOCS.md](./docs/API_DOCS.md) file.

## Deployment

The API can be deployed using Docker:

```bash
docker build -t aitale-api .
docker run -p 8000:8000 aitale-api
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Alexander Monash - [GitHub](https://github.com/morfun95)
- AI Tale Project - [Website](https://aitale.tech/) 