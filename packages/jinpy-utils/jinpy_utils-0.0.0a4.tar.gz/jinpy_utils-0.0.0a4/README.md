# jinpy-utils

![CI](https://github.com/jinto-ag/jinpy-utils/actions/workflows/ci.yml/badge.svg)
![PyPI - Version](https://img.shields.io/pypi/v/jinpy-utils?label=pypi)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)

> Status: alpha (v0.1.0-alpha.2)

Minimal, type-safe utilities for **Caching**, **Logging**, **Settings**, and **ORM**. Built with modern Python practices (PEP 8, mypy, ruff) and high test coverage. This is an early release; APIs may evolve.

## Features

- **🚀 Caching**: Advanced caching utilities with multiple backends
- **📝 Logging**: Structured logging with configurable console/file/REST/WebSocket backends
- **⚙️ Settings**: Configuration management with environment variable support
- **🗄️ ORM**: Database operations and migrations with SQLModel integration
- **✅ Type Safe**: Full type hints and mypy compatibility
- **🧪 Well Tested**: Comprehensive test coverage with pytest
- **🔧 Developer Friendly**: Pre-commit hooks and code quality tools

## Requirements

- **Python**: 3.12 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended)

## Installation

### Using uv (Recommended)

```bash
uv add jinpy-utils
```

### Using pip

```bash
pip install jinpy-utils
```

## Quick Start (Logging)

```python
from jpy_utils.logger.config import GlobalLoggerConfig, ConsoleBackendConfig
from jpy_utils.logger.core import Logger

# 1) Configure once (12-factor friendly; env helpers available)
cfg = GlobalLoggerConfig(backends=[ConsoleBackendConfig(name="console")])
Logger.set_global_config(cfg)

# 2) Get a logger and log
log = Logger.get_logger("app")
log.info("hello", {"env": "dev"})
```

## Core Dependencies

This library is built on top of these excellent packages:

- **[Pydantic](https://docs.pydantic.dev/latest/)** (v2+): Data validation and settings management
- **[SQLModel](https://sqlmodel.tiangolo.com/)** (v0.0.24+): SQL databases with Python type hints
- **[Structlog](https://www.structlog.org/)** (v24+): Structured logging
- **[Cachetools](https://cachetools.readthedocs.io/)** (v5+): Caching utilities
- **[Alembic](https://alembic.sqlalchemy.org/)** (v1.13+): Database migrations
- **[Python-dotenv](https://saurabh-kumar.com/python-dotenv/)** (v1+): Environment variables

## Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Development Environment

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd jinpy-utils
   ```

2. **Install dependencies**

   ```bash
   uv sync --all-extras
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

### Commands

- Format code: `uv run ruff format .`
- Lint and fix issues: `uv run ruff check --fix .`
- Type checking: `uv run mypy .`
- Run tests: `uv run pytest`
- Run tests with coverage: `uv run pytest`
- Security scanning: `uv run bandit -r jpy_utils`
- Run all pre-commit hooks: `uv run pre-commit run --all-files`

## Code Quality

This project maintains high code quality standards:

- **Code Formatting**: [Black](https://black.readthedocs.io/)
- **Linting**: [Ruff](https://docs.astral.sh/ruff/)
- **Type Checking**: [MyPy](https://mypy-lang.org/) with strict configuration
- **Security**: [Bandit](https://bandit.readthedocs.io/) for security issue detection
- **Testing**: [Pytest](https://docs.pytest.org/) with coverage reporting
- **Pre-commit Hooks**: Automated quality checks before commits

## Project Structure (partial)

```txt
jinpy-utils/
├── src/
│   └── jpy_utils/      # Main package directory
│       ├── __init__.py
│       └── py.typed         # Type information marker
├── tests/              # Test suite
├── docs/               # Documentation (coming soon)
├── pyproject.toml      # Project configuration
├── README.md           # This file
└── .pre-commit-config.yaml  # Pre-commit configuration
```

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Roadmap (high-level)

- [ ] Core caching implementations
- [ ] Structured logging utilities
- [ ] Settings management system
- [ ] ORM helpers and utilities
- [ ] Comprehensive documentation
- [ ] Performance benchmarks
- [ ] Plugin system

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jinto A G**

- Email: [project.jintoag@gmail.com](mailto:project.jintoag@gmail.com)
- GitHub: [jintoag](https://github.com/jinto-ag)

## Support

If you encounter any issues or have questions:

1. Check the [issues](https://github.com/jinto-ag/jinpy-utils/issues) page
2. Create a new issue with detailed information
3. Contact the maintainer via email

---

**Made with ❤️ and Python**
