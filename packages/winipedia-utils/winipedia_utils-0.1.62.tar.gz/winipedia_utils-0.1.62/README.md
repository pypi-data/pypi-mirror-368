# Winipedia Utils

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20management-poetry-blue.svg)](https://python-poetry.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)

A comprehensive Python utility ecosystem designed to scale into an all-in-one toolkit for Python development. Winipedia Utils provides battle-tested utilities for Django, dataframes, strings, concurrent processing, iterating, and any other tools needed for full Python projects, while enforcing clean code practices through automated tooling.

## 🎯 Core Purpose

Winipedia Utils serves as the **foundation for reducing repeated code** across Python projects while **enforcing clean code practices** through automated tooling. The project setup script automatically configures your development environment with industry best practices, ensuring consistent code quality across all your projects.

### Key Benefits

- **🚀 Zero-configuration setup** - Complete development environment in one command
- **🧪 Automated test generation** - 100% test coverage scaffolding for your entire codebase
- **🔍 Quality assurance** - Automated linting, type checking, and security scanning
- **📦 Comprehensive utilities** - Growing collection of production-ready utility functions
- **🔄 Consistent standards** - Enforced code style and testing patterns across projects

## 🏗️ Some Implementation

### Project Setup & Automation
- **Automated dependency installation** (ruff, mypy, pytest, bandit, pre-commit)
- **Pre-commit hook configuration** for code quality enforcement
- **pyproject.toml configuration** with optimal tool settings
- **Complete development environment setup** in a single command

### Core Utility Modules

#### 🧪 Testing Infrastructure (`testing/`)
- **Automated test file generation** for entire codebases
- **Test stub creation** for every function, class, and method
- **Mirror test structure** maintaining 1:1 correspondence with source code
- **Testing convention enforcement** with pytest integration

#### 🔍 Module Introspection (`modules/`)
- **Package discovery and manipulation** utilities
- **Dynamic module creation and import** capabilities
- **Code analysis and extraction** tools
- **Python object introspection** and manipulation

#### ⚡ Concurrent Processing (`concurrent/`)
- **Multiprocessing utilities** with automatic worker optimization
- **Multithreading support** for I/O-bound tasks
- **Timeout handling** and process management
- **Progress tracking** with tqdm integration

#### 🌐 Django Utilities (`django/`)
- **Bulk operations** with multithreaded processing for create, update, delete
- **Advanced BaseCommand** with logging, validation, and common arguments
- **Database utilities** including model hashing and topological sorting
- **Model introspection** and dependency analysis tools

#### 📊 Data Processing (`data/`)
- **DataFrame utilities** for data manipulation and analysis
- **Data cleaning and transformation** operations
- **Aggregation and preprocessing** tools

#### 🔄 Iterating Utilities (`iterating/`)
- **Iterable manipulation** with safe length operations
- **Generator utilities** and iteration helpers
- **Collection processing** tools

#### 📝 Text Processing (`text/`)
- **String manipulation** utilities
- **XML parsing** with security features
- **Input handling** with timeout support
- **Hash generation** and text truncation

#### 🔧 Development Tools
- **Git integration** (`git/`) - gitignore handling, pre-commit management
- **Logging configuration** (`logging/`) - standardized logging setup
- **OS utilities** (`os/`) - command finding, subprocess management
- **OOP enhancements** (`oop/mixins/`) - advanced metaclasses and mixins
- **Project configuration** (`projects/poetry/`) - Poetry integration and management

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)

### Installation

```bash
# Add to your project
poetry add winipedia-utils

# Run the setup script
poetry run python -m winipedia_utils.setup
```

### What Happens During Setup

The setup script automatically:

1. **Installs development dependencies**: ruff, mypy, pytest, bandit, pre-commit, and type stubs
2. **Configures pre-commit hooks**: Automated code quality checks on every commit
3. **Sets up pyproject.toml**: Optimal configurations for all development tools
4. **Generates comprehensive tests**: Creates test files for your entire codebase
5. **Runs initial quality checks**: Ensures everything is properly configured

```python
# winipedia_utils/setup.py
def _setup() -> None:
    """Set up the project."""
    _install_dev_dependencies()           # Install quality tools
    _add_package_hook_to_pre_commit_config()  # Configure pre-commit
    _add_tool_configurations_to_pyproject_toml()  # Setup tool configs
    _run_all_hooks()                      # Generate tests & run checks
    logger.info("Setup complete!")
```

## 💡 Usage Examples

### Automated Test Generation

```python
from winipedia_utils.testing.create_tests import create_tests

# Automatically generate test files for your entire project
create_tests()
# Creates comprehensive test structure with stubs for every function/class
```

### Module Introspection

```python
from winipedia_utils.modules.package import get_src_package, walk_package
from winipedia_utils.modules.function import get_all_functions_from_module

# Discover your main source package
src_package = get_src_package()

# Walk through all modules in a package
for package, modules in walk_package(src_package):
    for module in modules:
        functions = get_all_functions_from_module(module)
        print(f"Found {len(functions)} functions in {module.__name__}")
```

### Concurrent Processing

```python
from winipedia_utils.concurrent.multiprocessing import multiprocess_loop
from winipedia_utils.concurrent.multithreading import multithread_loop

# CPU-bound tasks with multiprocessing
def cpu_intensive_task(data):
    return complex_calculation(data)

results = multiprocess_loop(
    process_function=cpu_intensive_task,
    process_args=[[item] for item in large_dataset]
)

# I/O-bound tasks with multithreading
def io_task(url):
    return fetch_data(url)

results = multithread_loop(
    process_function=io_task,
    process_args=[[url] for url in urls]
)
```

### Django Bulk Operations

```python
from winipedia_utils.django.bulk import (
    bulk_create_in_steps,
    bulk_update_in_steps,
    bulk_delete_in_steps
)

# Efficient bulk creation with multithreading
created_objects = bulk_create_in_steps(
    model=MyModel,
    bulk=[MyModel(name=f"item_{i}") for i in range(10000)],
    step=1000
)

# Bulk update with field specification
updated_count = bulk_update_in_steps(
    model=MyModel,
    bulk=objects_to_update,
    update_fields=['name', 'status'],
    step=1000
)

# Safe bulk deletion with cascade handling
deleted_count, deletion_summary = bulk_delete_in_steps(
    model=MyModel,
    bulk=objects_to_delete,
    step=1000
)
```

### Django Management Commands

```python
from winipedia_utils.django.command import ABCBaseCommand

class MyCommand(ABCBaseCommand):
    """Custom Django command with built-in logging and validation."""

    help = "Process data with automatic logging and error handling"

    def add_command_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=1000)

    def handle_command(self, *args, **options):
        # Command logic with automatic logging and performance tracking
        batch_size = options['batch_size']
        self.stdout.write(f"Processing with batch size: {batch_size}")
```

### String Utilities

```python
from winipedia_utils.text.string import (
    value_to_truncated_string,
    ask_for_input_with_timeout,
    get_reusable_hash
)

# Safely truncate any value to string
truncated = value_to_truncated_string(large_object, max_length=100)

# Get user input with timeout
try:
    user_input = ask_for_input_with_timeout("Enter value: ", timeout=30)
except TimeoutError:
    print("Input timeout exceeded")

# Generate consistent hashes
hash_value = get_reusable_hash("some data")
```

### Iterating Utilities

```python
from winipedia_utils.iterating.iterate import get_len_with_default

# Safe length operations with fallback
length = get_len_with_default(some_iterable, default=0)

# Works with generators and other iterables that don't support len()
gen = (x for x in range(100))
safe_length = get_len_with_default(gen, default=100)
```

### Advanced OOP Features

```python
from winipedia_utils.oop.mixins.meta import ABCImplementationLoggingMeta

class MyClass(metaclass=ABCImplementationLoggingMeta):
    """Class with automatic logging and implementation enforcement."""

    def my_method(self):
        # Automatically logged with performance tracking
        return "result"
```

## 🔮 Future Vision

Winipedia Utils is designed to scale into a comprehensive ecosystem covering many utilities

## 🛡️ Development Standards

### Automated Quality Assurance

Every utility in the ecosystem benefits from:

- **🧪 100% Test Coverage Scaffolding**: Automated test generation ensures no function goes untested
- **🔍 Static Type Checking**: MyPy ensures type safety across all utilities
- **🎨 Code Formatting**: Ruff enforces consistent code style
- **🔒 Security Scanning**: Bandit identifies potential security issues
- **📝 Documentation Standards**: Consistent docstring patterns and examples

### Pre-commit Hooks

Automatically configured hooks ensure:
- Code formatting with ruff
- Type checking with mypy
- Security scanning with bandit
- Test generation and execution
- Dependency validation
See details in `winipedia_utils/git/pre_commit/hooks.py` and `winipedia_utils/git/pre_commit/run_hooks.py`

## 🏗️ Project Structure

```
winipedia_utils/
├── concurrent/          # Parallel processing utilities
├── conventions/         # Testing and naming conventions
├── data/               # Data science utilities (expanding)
├── git/                # Git integration and workflows
├── logging/            # Standardized logging configuration
├── modules/            # Package/module introspection
├── oop/                # Object-oriented programming enhancements
├── os/                 # Operating system utilities
├── projects/           # Project configuration (Poetry, etc.)
├── testing/            # Automated test generation
├── text/               # String and text processing
└── setup.py           # Main setup script
```

## 🤝 Contributing

Winipedia Utils welcomes contributions! The automated setup ensures that all contributions maintain high quality standards:

1. Fork the repository
2. Run `poetry run python -m winipedia_utils.setup` in your fork
3. Add your utilities following the established patterns
4. Tests are automatically generated - implement the test logic
5. Pre-commit hooks ensure code quality
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Note**: All `_private_methods` are intended for internal use within the winipedia_utils package and cannot be used directly in external projects.
