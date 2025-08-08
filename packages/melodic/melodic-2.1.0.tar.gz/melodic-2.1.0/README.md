# Melodic

<p align="center">
  <a href="https://pypi.org/project/melodic/"><img alt="PyPI" src="https://img.shields.io/pypi/v/melodic?color=blue"></a>
  <a href="https://pypi.org/project/melodic/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/melodic"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

Melodic is a Python client for fetching artist lyrical discographies. This library provides an asynchronous interface to retrieve complete artist discographies, including album metadata and song lyrics, with built-in database storage, proxy support, and robust error handling.

---

## Features

- **Complete Discography Fetching:** Retrieves full album and track listings for any given artist.
- **Asynchronous Interface:** Built with modern `async with` patterns for efficient, safe I/O operations.
- **Database Storage:** Optional built-in storage system for organizing artist, album, and track metadata.
- **Proxy Support:** Easily pass a list of proxies to route requests through.
- **Robust Error Handling:** Comprehensive error handling and logging for reliable operation.
- **Modern Development Tools:** Includes ruff, mypy, pre-commit, and commitizen for high-quality code.

---

## Installation

### From PyPI (Recommended)

```bash
pip install melodic
```

### From Source

You can install melodic by cloning the repository directly or using pre-built wheel files.

**Prerequisites:** This project requires [uv](https://github.com/astral-sh/uv) for dependency management.

#### Option 1: Clone and Build

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/melodic.git
   cd melodic
   ```

2. Install the project and its dependencies:
   ```bash
   uv sync
   ```

#### Option 2: Install from Pre-built Wheels

Pre-built wheel files are automatically generated and attached to each GitHub release. You can download and install them directly:

1. Go to the [GitHub releases page](https://github.com/filming/melodic/releases)
2. Download the `.whl` file from the latest release
3. Install using pip:
   ```bash
   pip install path/to/downloaded/melodic-*.whl
   ```

---

## Usage

```
Usage examples will be shown in the future.
```

---

## Configuration

Configuration is passed directly to the `Melodic` class instance during initialization.

- **`storage_dir`**: An optional string or `Path` object pointing to a directory where the database and other files will be stored. If not provided, no data will be saved to disk.
- **`proxies`**: An optional list of proxy strings (e.g., `["http://user:pass@host:port"]`). If provided, all network requests will be routed through these proxies.

---

## Development

This project uses modern Python development tools:

- **[uv](https://github.com/astral-sh/uv)** for dependency management
- **[ruff](https://github.com/astral-sh/ruff)** for linting and formatting
- **[mypy](https://mypy.readthedocs.io/)** for type checking
- **[pre-commit](https://pre-commit.com/)** for git hooks
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** for conventional commits

### Setting up for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/melodic.git
   cd melodic
   ```

2. Install dependencies (including dev tools):
   ```bash
   uv sync --extra dev
   ```

3. Set up pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

4. Start developing!

---

## Dependencies

All project dependencies are managed via [`pyproject.toml`](pyproject.toml) and use Python 3.10+.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/melodic).
