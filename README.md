# STDF Parser

A high-performance Python library for parsing and writing STDF (Standard Test Data Format) files, commonly used in semiconductor testing and manufacturing.

## Overview

STDF (Standard Test Data Format) is a binary format standardized by IEEE 1320.1 for semiconductor test data. This library provides efficient tools for reading and writing STDF files, with Cython compilation for enhanced performance.

## Features

- **Fast Binary Parsing**: Optimized byte-level functions for reading STDF data
- **Cython Compilation**: Pre-compiled modules for improved performance
- **Full STDF Support**: Comprehensive record type handling
- **Write Capability**: Create STDF files programmatically
- **Numpy Integration**: Efficient array operations using NumPy
- **Type-Safe**: Structured record tuples for type safety

## Installation

### From Source

Clone the repository and install:

```bash
git clone <repository-url>
cd stdf_parser
pip install .
```

### Build Wheel

To build a distributable wheel:

```bash
# Windows
build_wheel.bat

# Or manually
python -m build
```

## Requirements

- Python >= 3.8
- NumPy >= 1.21
- Cython >= 3.0 (for building from source)

## Usage

### Reading STDF Files

```python
from stdf_parser import *

# Open and parse an STDF file
with open('test.stdf', 'rb') as f:
    # Use RECFuncs to parse records
    # Example usage here
    pass
```

### Writing STDF Files

```python
from stdf_parser import STDFWriter

# Create a new STDF file
writer = STDFWriter('output.stdf')
# Write records using STDFWriter methods
```

### Working with Byte Functions

```python
from stdf_parser import get_u, get_r, get_cn, write_u, write_r, write_cn

# Read unsigned integer (little-endian)
value = get_u(4, file_handle)

# Read floating point
float_val = get_r(4, file_handle)

# Read character string with length prefix
text = get_cn(file_handle)
```

## Project Structure

```
stdf_parser/
├── ByteFuncs.py      # Low-level byte reading/writing functions
├── RECFuncs.py       # STDF record parsing functions
├── RECRecipes.py     # Record format specifications
├── RecordTuples.py   # Named tuples for STDF records
├── STDFWriter.py     # STDF file writing utilities
└── Debugger.py       # Debugging utilities
```

## Development

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest test_bytefuncs.py
```

### Development Tools

This project uses:
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

## Building from Source

The build process uses Cython to compile Python modules into C extensions for better performance. Source `.py` files are excluded from the wheel, leaving only the compiled `.pyd` files.

```bash
python setup.py build_ext --inplace
```

## License

MIT License

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style
- Tests pass
- New features include tests
- Documentation is updated

## Authors

- Your Name (your.email@example.com)

## Version

Current version: 0.1.1

## Related Resources

- [IEEE 1320.1 STDF Specification](https://www.ieee.org/)
- [Semiconductor Test Data](https://en.wikipedia.org/wiki/Standard_Test_Data_Format)
