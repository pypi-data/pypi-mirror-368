# darkfield CLI

Command-line interface for the darkfield ML Safety Platform.

## Installation

### For Development

```bash
# From the cli directory
./install-local.sh
```

### For Production (when published)

```bash
pip install darkfield-cli
# or
npm install -g @darkfield/cli
```

## First Run

When you first run darkfield, you'll see:

```
    ██████╗  █████╗ ██████╗ ██╗  ██╗███████╗██╗███████╗██╗     ██████╗ 
    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██║██╔════╝██║     ██╔══██╗
    ██║  ██║███████║██████╔╝█████╔╝ █████╗  ██║█████╗  ██║     ██║  ██║
    ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝  ██║██╔══╝  ██║     ██║  ██║
    ██████╔╝██║  ██║██║  ██║██║  ██╗██║     ██║███████╗███████╗██████╔╝
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚═════╝ 

    ML Safety Platform Command Line Interface
    Protecting AI from harmful personas • v0.1.0
```

## Quick Start

```bash
# Authenticate
darkfield auth login

# Run a demo
darkfield analyze demo --trait sycophancy

# Check your usage
darkfield billing usage
```

## Development

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Build distribution
python setup.py sdist bdist_wheel
```

## Publishing

```bash
# PyPI
python -m twine upload dist/*

# NPM (wrapper)
npm publish
```