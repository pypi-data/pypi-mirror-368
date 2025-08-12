# PyVetic

## Overview

PyVetic is a shared Python utility library designed to provide common functionality across multiple Vetic projects. This library serves as a central repository for reusable code, ensuring consistency and reducing duplication across different repositories.

## Features

- **Unified Logging System**: Advanced logging with Loki integration, colored console output, and file rotation
- **Monitoring Integration**: Prometheus metrics collection and reporting
- **Framework Support**:
  - Django integration
  - FastAPI integration
  - Instrumentation utilities
- **Performance Monitoring**: System resource monitoring with psutil
- **Configuration Management**: Centralized constants and settings

## Installation

### From PyPI

```bash
pip install pyvetic
```

### Development Installation

```bash
git clone https://github.com/vetic-in/pyvetic.git
cd pyvetic
pip install -e .
```

### Optional Dependencies

- For Django support:
  ```bash
  pip install pyvetic[django]
  ```

- For FastAPI support:
  ```bash
  pip install pyvetic[fastapi]
  ```

## Usage

### Basic Logging

```python
from pyvetic import get_logger

logger = get_logger(__name__)
logger.info("Hello, PyVetic!")
```

### Loki Integration

```python
from pyvetic import set_logging_config

config = {
    "handlers": ["loki"],
    "loki": {
        "host": "your-loki-host",
        "port": 3100,
        "username": "your-username",
        "password": "your-password"
    }
}
set_logging_config(config)
```

## Project Structure

```
pyvetic/
├── django/           # Django-specific utilities
├── fastapi/          # FastAPI-specific utilities
├── instrument/       # Monitoring and instrumentation tools
├── logger.py         # Advanced logging system
└── constants.py      # Shared constants and configurations
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For support, please contact techadmin@vetic.in or open an issue in the GitHub repository.

## Acknowledgments

- Thanks to all contributors who have helped make this project better
