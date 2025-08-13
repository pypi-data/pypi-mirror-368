
# python_code_changed



![CI](https://github.com/DeanGodfreeItalia/python_code_changed/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/python_code_changed)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Coverage](./coverage.svg)

![Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![isort](https://img.shields.io/badge/imports-isort-ef8336.svg)
![mypy](https://img.shields.io/badge/type%20checker-mypy-blue.svg)
![pip-audit](https://img.shields.io/badge/security-pip--audit-yellow)


## Overview
`python_code_changed` is a tool to detect real logic changes in Python code, ignoring trivial changes like formatting, comments, import reordering, and unreachable code. It is designed for code review automation and CI pipelines.

#### PIP Package Usage

After installing via PIP, run:

```sh
python-code-changed [FILES or OPTIONS]
```

For example, to check for real code changes in staged files:

```sh
python-code-changed --staged
```

See all options:

```sh
python-code-changed --help
```

## Project Structure

```
python_code_changed/
├── src/
│   ├── ast_utils.py
│   ├── detect_real_code_changes.py
│   ├── helpers_logic.py
│   └── helpers_trivial.py
├── tests/
│   └── test_detect_real_code_changes.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .devcontainer/
│   └── devcontainer.json
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## Getting Started

### Development Environment
This project supports [Dev Containers](https://containers.dev/) for reproducible development. Open in VS Code and install the recommended extensions. NB. You will need to set your git user.name and git user.email on the devcontainer terminal after its loaded.
```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```


### Installation
Install dependencies using [uv](https://github.com/astral-sh/uv):

```sh
uv pip install -e .'[dev]'
```

### Configuration

`python_code_changed` uses an optional configuration file named `real_code_checks.ini` (located in the project root) to control analysis options and behavior. You can customise which checks are enabled, ignored, or how the tool treats certain code changes by editing this file. You can alternatively pass in command-line arguments when runnin the script.

See the comments in `real_code_checks.ini` for available options and usage examples.
### Usage

You can use `python_code_changed` as a CLI tool or as a Python library.

#### CLI Usage

After installing dependencies, run:

```sh
uv run python-code-changed [FILES or OPTIONS]
```

For example, to check for real code changes in staged files:

```sh
uv run python-code-changed --staged
```

See all options:

```sh
uv run python-code-changed --help
```

#### Library Usage

You can import and use the main functions in your own Python code:

```python
from python_code_changed import detect_real_code_changes
# Use detect_real_code_changes(...) as needed
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

MIT License
