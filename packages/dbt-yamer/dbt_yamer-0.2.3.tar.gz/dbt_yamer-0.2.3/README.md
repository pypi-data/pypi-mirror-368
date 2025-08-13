# dbt-yamer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-docker--ready-blue.svg)](docker-test/)

> **🧪 Want to test dbt-yamer?** → Run `cd docker-test && ./test_dbt_yamer.sh` (see [Testing Guide](TESTING.md))

## Overview

`dbt-yamer` is a secure, enterprise-ready Python CLI tool designed to streamline the generation of YAML schema files and documentation for dbt projects. With a focus on automation, security, and developer productivity, dbt-yamer helps teams maintain consistent documentation standards and avoid technical debt in their data transformation workflows.

### Key Features

✨ **Automated Schema Generation**
- Generates dbt YAML schema files with proper data contracts
- Automatically integrates doc blocks into column descriptions
- Smart column-to-documentation mapping with fuzzy matching

🔒 **Security First**
- Input validation and sanitization for all user inputs
- Safe subprocess execution with timeout protection
- Path traversal prevention and secure file handling

🚀 **Developer Productivity**
- Support for tag-based model selection (`tag:nightly`)
- Batch processing of multiple models
- Intelligent versioning of existing schema files
- Concurrent processing for improved performance

🛠 **Enterprise Ready**
- Comprehensive error handling and logging
- Support for multiple dbt environments/targets
- Configurable manifest paths and output directories
- Clean temporary file management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)  
- dbt-core (any supported version)
- A working dbt project with a `dbt_project.yml` file

### Installing dbt-yamer

```bash
pip install dbt-yamer
```

### Verify Installation

```bash
dbt-yamer --help
```

You should see the available commands: `run`, `yaml`, `md`, and `yamd`.

## 🧪 Testing

dbt-yamer includes a comprehensive Docker-based test environment to validate all functionality.

### Quick Test (Recommended)

```bash
# Clone the repository
git clone https://github.com/Muizzkolapo/dbt-yamer.git
cd dbt-yamer

# Run automated tests
cd docker-test
./test_dbt_yamer.sh
```

This will:
- ✅ Set up PostgreSQL + dbt containers
- ✅ Install dbt-yamer from source  
- ✅ Create sample e-commerce data
- ✅ Test all commands and security features
- ✅ Validate bug fixes and improvements

### Manual Testing

```bash
# Start test environment
docker-compose up -d

# Access dbt container
docker-compose exec dbt /bin/bash

# Test commands interactively
dbt-yamer yaml -s stg_customers
dbt-yamer md -s dim_customers
```

See [Testing Guide](docker-test/README.md) for detailed instructions.

<<<<<<< HEAD
## 🧪 Testing

dbt-yamer includes a comprehensive Docker-based test environment to validate all functionality.

### Quick Test (Recommended)

```bash
# Clone the repository
git clone https://github.com/Muizzkolapo/dbt-yamer.git
cd dbt-yamer

# Run automated tests
cd docker-test
./test_dbt_yamer.sh
```

This will:
- ✅ Set up PostgreSQL + dbt containers
- ✅ Install dbt-yamer from source  
- ✅ Create sample e-commerce data
- ✅ Test all commands and security features
- ✅ Validate bug fixes and improvements

### Manual Testing

```bash
# Start test environment
docker-compose up -d

# Access dbt container
docker-compose exec dbt /bin/bash

# Test commands interactively
dbt-yamer yaml -s stg_customers
dbt-yamer md -s dim_customers
```

See [Testing Guide](docker-test/README.md) for detailed instructions.

=======
>>>>>>> 89f940a (done)
## Quick Start

Make sure you're in your dbt project directory and have run `dbt run` on your models first:

```bash
cd your-dbt-project/
dbt run --select your_model

# Now generate YAML schema
dbt-yamer yaml -s your_model
```

## Usage

### Available Commands

- `dbt-yamer run` - Run dbt models with selection syntax
- `dbt-yamer yaml` - Generate YAML schema files  
- `dbt-yamer md` - Generate markdown documentation files
- `dbt-yamer yamd` - Generate both YAML and markdown files

### Generate YAML Schema Files

#### Basic Usage

```bash
# Generate YAML for a single model
dbt-yamer yaml -s customer_data

# Generate YAML for multiple models
dbt-yamer yaml -s model_a model_b model_c

# Use tag selectors to process multiple models at once
dbt-yamer yaml -s tag:nightly

# Mix model names and tag selectors
dbt-yamer yaml -s customer_data tag:daily model_x
```

#### Advanced Options

```bash
# Specify a custom manifest path
dbt-yamer yaml -s model_a --manifest path/to/manifest.json

# Use a specific dbt target/environment
dbt-yamer yaml -s model_a -t production

# Combine all options
dbt-yamer yaml -s model_a tag:nightly --manifest custom/manifest.json -t uat
```

### Generate Documentation

```bash
# Generate markdown documentation
dbt-yamer md -s customer_data

# Generate both YAML and markdown
dbt-yamer yamd -s customer_data tag:docs
```

### Run dbt Models

```bash
# Run specific models
dbt-yamer run -s model_a model_b

# Run models with tag selectors
dbt-yamer run -s tag:nightly

# Exclude specific models
dbt-yamer run -s tag:daily -e problematic_model

# Use specific target
dbt-yamer run -s tag:nightly -t production
```

### Command Options

| Option | Short | Description | Default |
|--------|--------|-------------|---------|
| `--select` | `-s` | Select models to process | Required |
| `--exclude` | `-e` | Exclude models (run command only) | None |
| `--target` | `-t` | dbt target environment | None |
| `--manifest` | | Path to dbt manifest.json | `target/manifest.json` |

## Output Behavior

### YAML Schema Files
- Generated in the same directory as their corresponding `.sql` files
- Automatic versioning: `model.yml`, `model_v1.yml`, `model_v2.yml`, etc.
- Smart doc block integration with multiple fallback strategies:
  ```yaml
  columns:
    - name: customer_id
      data_type: varchar
      description: "{{ doc('col_customers_customer_id') }}"  # Exact match
    - name: status  
      data_type: varchar
      description: "{{ doc('col_status') }}"  # Generic match
  ```

### Documentation Files
- Markdown files created with dbt doc block templates
- Structured format with common documentation sections
- Ready for customization with your specific model details

### Doc Block Matching Priority
1. **Exact match**: `col_{model_name}_{column_name}`
2. **Model-specific**: `{model_name}_{column_name}`  
3. **Generic**: `col_{column_name}`
4. **Fuzzy match**: Best similarity match (80%+ confidence)
5. **Fallback**: Empty description for manual completion

### Error Handling
dbt-yamer provides clear, actionable error messages:
- ✅ Input validation with specific guidance
- ✅ Secure subprocess execution with timeouts  
- ✅ Comprehensive logging for troubleshooting
- ✅ Graceful handling of missing models or doc blocks

## Security Features

dbt-yamer prioritizes security in enterprise environments:

- 🔒 **Input Validation**: All user inputs are validated and sanitized
- 🛡️ **Command Injection Prevention**: Safe subprocess execution with parameter validation
- 🚫 **Path Traversal Protection**: Prevents access to files outside the project directory
- ⏱️ **Timeout Protection**: All operations have configurable timeouts
- 🔍 **Audit Logging**: Comprehensive logging for security monitoring

## Troubleshooting

### Common Issues

**"dbt command not found"**
```bash
# Ensure dbt is installed and in PATH
which dbt
dbt --version
```

**"No models found for tag selector"**
```bash
# Verify the tag exists in your dbt project
dbt list --select tag:your_tag
```

**"Manifest file not found"**
```bash
# Generate the manifest first
dbt compile
# Or specify a custom path
dbt-yamer yaml -s model --manifest path/to/manifest.json
```

**"No columns detected"**
```bash
# Make sure you've run the model first
dbt run --select your_model
```

### Getting Help

- 📖 Check the [documentation](https://github.com/Muizzkolapo/dbt-yamer)
- 🐛 [Report bugs](https://github.com/Muizzkolapo/dbt-yamer/issues) 
- 💬 [Start a discussion](https://github.com/Muizzkolapo/dbt-yamer/discussions)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Muizzkolapo/dbt-yamer.git
cd dbt-yamer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints for new code
- Include docstrings for public functions
- Write tests for new features
- Ensure security best practices

### Running Tests

```bash
# Run the test suite
make test

# Run with coverage
make test-coverage

# Lint the code
make lint
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## Acknowledgments

- The dbt community for inspiration and feedback
- Contributors who have helped improve the project
- Users who have provided valuable bug reports and feature requests

## Authors

**Muizz Lateef** - *Creator and Lead Maintainer*
- 📧 Email: [lateefmuizz@gmail.com](mailto:lateefmuizz@gmail.com)
- 🌐 Website: [https://muizzkolapo.github.io/blog/](https://muizzkolapo.github.io/blog/)
- 🐱 GitHub: [@Muizzkolapo](https://github.com/Muizzkolapo)

---

⭐ **Found dbt-yamer helpful?** Give us a star on [GitHub](https://github.com/Muizzkolapo/dbt-yamer)!
