<img src="docs/assets/logo.jpg" alt="ArchiPy Logo" width="150"/>

# ArchiPy - Architecture + Python

[![Forks](https://img.shields.io/github/forks/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/network/members)
[![Stars](https://img.shields.io/github/stars/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/stargazers)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue.svg)](https://syntaxarc.github.io/ArchiPy/)
[![License](https://img.shields.io/github/license/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/blob/master/LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-yes-brightgreen)](https://github.com/SyntaxArc/ArchiPy)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](https://github.com/SyntaxArc/ArchiPy/blob/master/CONTRIBUTING.md)
[![PyPI - Version](https://img.shields.io/pypi/v/archipy)](https://pypi.org/project/archipy/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/archipy)](https://pypi.org/project/archipy/)
[![Contributors](https://img.shields.io/github/contributors/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/commits/main)
[![Open Issues](https://img.shields.io/github/issues/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/issues?q=is%3Aissue+is%3Aclosed)
[![Pull Requests](https://img.shields.io/github/issues-pr/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy/pulls)
[![Repo Size](https://img.shields.io/github/repo-size/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy)
[![Code Size](https://img.shields.io/github/languages/code-size/SyntaxArc/ArchiPy)](https://github.com/SyntaxArc/ArchiPy)

## **Structured Python Development Made Simple**

ArchiPy is a Python framework designed to provide a standardized, scalable, and maintainable architecture for modern applications. Built with Python 3.13+, it offers a suite of tools, utilities, and best practices to streamline configuration management, testing, and development workflows while adhering to clean architecture principles.

---

## 📋 Table of Contents

- [Goals](#-goals)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Sponsors](#-sponsors)
- [Contact](#-contact)
- [Links](#-links)

---

## 🎯 Goals

ArchiPy is built with the following objectives in mind:

1. **Configuration Management & Injection** - Simplify and standardize configuration handling
2. **Common Adapters & Mocks** - Provide ready-to-use adapters with testing mocks
3. **Standardized Entities & DTOs** - Enforce consistency in data modeling
4. **Common Helpers for Everyday Tasks** - Simplify routine development work
5. **Behavior-Driven Development (BDD) Support** - Enable robust feature validation
6. **Best Practices & Development Structure** - Enforce coding standards

[Read more about ArchiPy's architecture and design](https://syntaxarc.github.io/ArchiPy/architecture)

---

## ✨ Features

- **Config Standardization**: Tools for managing and injecting configurations
- **Adapters & Mocks**: Pre-built adapters for Redis, SQLAlchemy, and email with testing mocks
- **Data Standardization**: Base entities, DTOs, and type safety
- **Helper Utilities**: Reusable tools for common tasks
- **BDD Testing**: Fully integrated Behave setup
- **Modern Tooling**: Dependency management and code quality tools

[Explore the complete feature set](https://syntaxarc.github.io/ArchiPy/features)

---

## 🛠️ Prerequisites

- **Python 3.13 or higher**
- **Poetry** (recommended for development)

---

## 📥 Installation
 Install using pip
```bash
# Basic installation
pip install archipy

# With optional dependencies (e.g., Redis and FastAPI)
pip install archipy[redis,fastapi]
```

Using Poetry:
```bash
poetry add archipy

# With optional dependencies
poetry add archipy[redis,fastapi]
```

[View installation documentation](https://syntaxarc.github.io/ArchiPy/installation)

---

## 🎯 Usage

### Optional Dependencies

ArchiPy's modular design lets you install only what you need:

```bash
# Examples
pip install archipy[redis]        # Redis support
pip install archipy[fastapi]      # FastAPI framework
pip install archipy[postgres]     # PostgreSQL support
```

[See the documentation for all available options and examples](https://syntaxarc.github.io/ArchiPy/usage)

---

## 🛠️ Development

### Quick Commands

```bash
# Format code
make format

# Run tests
make behave

# Lint code
make lint
```

[View the complete development guide](https://syntaxarc.github.io/ArchiPy/development)

---

## 🤝 Contributing

Contributions are welcome! See our [contribution guidelines](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

---

## 🙌 Sponsors

Support ArchiPy by checking out our amazing sponsors! [View Sponsors](SPONSORS.md)

---

## 📞 Contact

- **Mehdi Einali**: [einali@gmail.com](mailto:einali@gmail.com)
- **Hossein Nejati**: [hosseinnejati14@gmail.com](mailto:hosseinnejati14@gmail.com)

---

## 🔗 Links

- [Documentation](https://syntaxarc.github.io/ArchiPy/)
- [GitHub Repository](https://github.com/SyntaxArc/ArchiPy)
- [PyPI Package](https://pypi.org/project/archipy/)

## 📚 Documentation

ArchiPy's documentation has been migrated from Sphinx to MkDocs for improved readability and organization:

- **Modern Interface**: Material theme with responsive design
- **Improved Navigation**: Intuitive organization and search
- **Clearer Examples**: Expanded code samples with explanations
- **API Reference**: Auto-generated from source code docstrings

To run the documentation locally:

```bash
# Install documentation dependencies
poetry install --with docs

# Serve documentation locally
make docs-serve

# Build documentation
make docs-build

# Deploy to GitHub Pages
make docs-deploy
```

[View the latest documentation](https://syntaxarc.github.io/ArchiPy/)
