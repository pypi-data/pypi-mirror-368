# InfraLib: Infrastructure Management for RL and Optimization

**InfraLib** is a comprehensive Python library for modeling, simulating, and analyzing large-scale infrastructure management problems using reinforcement learning and stochastic optimization. It provides realistic deterioration modeling, partial observability, and scalable simulation supporting millions of components.

[![Documentation Status](https://readthedocs.org/projects/infralib/badge/?version=latest)](https://infralib.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/infralib.svg)](https://badge.fury.io/py/infralib)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Quick Links

- **Documentation**: [infralib.readthedocs.io](https://infralib.readthedocs.io/)
- **Website**: [infralib.github.io](https://infralib.github.io/)
- **Research Paper**: [arXiv](https://arxiv.org/abs/2409.03167)
- **Issues**: [GitHub Issues](https://github.com/pthangeda/InfraLib/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pthangeda/InfraLib/discussions)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install infralib
```

### Option 2: Install with uv (Advanced Users)

First install [uv](https://github.com/astral-sh/uv):

```bash
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install InfraLib:

```bash
# Install from PyPI
uv add infralib

# Or install from source
git clone https://github.com/pthangeda/InfraLib.git
cd InfraLib
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv pip install -e .
```

## Documentation

Comprehensive documentation is available at [infralib.readthedocs.io](https://infralib.readthedocs.io/), including:

- **API Reference**: Detailed documentation for all classes and functions
- **Tutorials**: Step-by-step guides for common use cases
- **Examples**: Complete example implementations
- **Theory**: Mathematical foundations and model descriptions

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/pthangeda/InfraLib.git
cd InfraLib

# Install with development dependencies
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e \".[dev]\"

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Running Tests and Code Quality

```bash
# Run tests
uv run pytest

# Run linting and formatting
uv run ruff check --fix
uv run ruff format

# Run all quality checks
uv run pre-commit run --all-files
```

### Build Documentation

```bash
# Install documentation dependencies
uv add --group docs sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Build documentation
cd docs
uv run sphinx-build -b html . _build/html
```

## Contributing

We welcome contributions from the community! Here's how to get involved:

1. **Report Issues**: Found a bug? [Open an issue](https://github.com/pthangeda/InfraLib/issues)
2. **Request Features**: Have an idea? [Start a discussion](https://github.com/pthangeda/InfraLib/discussions)
3. **Contribute Code**:
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/amazing-feature`)
   - Make your changes and add tests
   - Run quality checks (`uv run pre-commit run --all-files`)
   - Commit your changes (`git commit -m 'Add amazing feature'`)
   - Push to your branch (`git push origin feature/amazing-feature`)
   - Open a Pull Request

4. **Improve Documentation**: Help us make the docs better
5. **Spread the Word**: Star the repo and tell others about InfraLib!

## Support & Community

- **Contact**: Pranay Thangeda (pranayt2@illinois.edu or contact@prny.me) - We're happy to help with questions and feature requests
- **Collaboration**: We welcome collaborations and are willing to implement features that help researchers and practitioners use InfraLib for their specific use cases
- **Bug Reports**: [GitHub Issues](https://github.com/pthangeda/InfraLib/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pthangeda/InfraLib/discussions)

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 InfraLib Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---
