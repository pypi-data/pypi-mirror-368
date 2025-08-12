# reqtracker

**Intelligent Python dependency tracking and requirements.txt generation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

reqtracker automatically detects and manages Python dependencies in your projects using static analysis, dynamic tracking, or hybrid approaches. Unlike traditional tools like `pip freeze`, reqtracker focuses on generating accurate `requirements.txt` files based on *actual project usage*.

---

## ✨ Features

- **🔍 Smart Dependency Detection**: Analyzes your code to find actually used packages
- **⚡ Multiple Analysis Modes**: Static (AST), Dynamic (runtime), or Hybrid (both)
- **🎯 Accurate Package Mapping**: Maps imports like `cv2` to `opencv-python`
- **📦 Flexible Output**: Multiple version strategies and output formats
- **🛠️ Zero Configuration**: Works out of the box with sensible defaults
- **⚙️ Highly Configurable**: Customize analysis via config files or API
- **🚀 CLI & Library**: Use as command-line tool or Python library
- **🧪 Well-Tested**: 204 comprehensive tests with >95% coverage

---

## 📦 Installation

Install reqtracker using pip:

```bash
pip install reqtracker
```

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Analyze current directory and generate requirements.txt
reqtracker analyze

# Track dependencies in specific paths
reqtracker track ./src ./app

# Generate with exact versions
reqtracker generate --version-strategy exact

# Use static analysis only
reqtracker analyze --mode static --output deps.txt
```

### Python Library Usage

```python
import reqtracker

# Simple usage - analyze current directory
packages = reqtracker.track()
print(packages)  # {"requests", "numpy", "pandas"}

# Generate requirements.txt
reqtracker.generate()

# Complete workflow
reqtracker.analyze()  # Track dependencies and generate requirements.txt
```

---

## 🧪 Testing

The project includes comprehensive testing with 204 tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/reqtracker --cov-report=html

# Run integration tests only
pytest tests/integration -v
```

### Test Categories
- **Unit Tests**: Core functionality testing
- **Integration Tests**: Real project scenarios
- **Performance Tests**: Benchmarking different project sizes
- **Cross-Platform Tests**: Compatibility across operating systems

---

## 📚 Documentation

- [Getting Started](https://github.com/oleksii-shcherbak/reqtracker#getting-started) - Overview and quick start guide
- [API Documentation](https://github.com/oleksii-shcherbak/reqtracker/tree/main/docs/api) - Complete API reference for all modules
- [Configuration Guide](https://github.com/oleksii-shcherbak/reqtracker/blob/main/docs/guides/configuration.md) - All configuration options
- [Examples](https://github.com/oleksii-shcherbak/reqtracker/tree/main/examples) - Real-world usage examples and tutorials


---

## 🤝 Contributing

I welcome contributions! Please see [CONTRIBUTING.md](https://github.com/oleksii-shcherbak/reqtracker/blob/main/CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/oleksii-shcherbak/reqtracker/blob/main/LICENSE) file for details.
