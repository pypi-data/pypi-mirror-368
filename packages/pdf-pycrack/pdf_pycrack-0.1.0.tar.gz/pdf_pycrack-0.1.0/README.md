
# PDF-PyCrack

[![PyPI version](https://badge.fury.io/py/pdf-pycrack.svg)](https://badge.fury.io/py/pdf-pycrack)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**A not yet blazing fast, parallel PDF password cracker for Python 3.12+.**

---


## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Benchmarking](#benchmarking)
- [Testing & Error Handling](#testing--error-handling)
- [Contributing](#contributing)
- [License](#license)


## Features

- **Multi-core Cracking:** Utilizes all CPU cores for maximum speed.
- **Efficient Memory Usage:** Handles large PDFs with minimal RAM.
- **Resilient Workers:** Worker processes handle errors gracefully; the main process continues.
- **Progress Tracking:** Real-time progress bar and statistics.
- **Customizable:** Tune password length, charset, batch size, and more.
- **Comprehensive Error Handling:** Clear error messages and robust test coverage for all edge cases.


## Installation

Install from PyPI (recommended):

```bash
uv pip install pdf-pycrack
```

For development:

```bash
git clone https://github.com/hornikmatej/pdf_pycrack.git
cd pdf_pycrack
uv sync
```


## Quick Start

```bash
uv run pdf-pycrack <path_to_pdf>
```

For all options:

```bash
uv run pdf-pycrack --help
```

## Usage

**Basic usage:**

```bash
uv run pdf-pycrack tests/test_pdfs/numbers/100.pdf
```

**Custom charset and length:**

```bash
uv run pdf-pycrack tests/test_pdfs/letters/ab.pdf --min-len 2 --max-len 2 --charset abcdef
```

### Using as a Python Library

You can also use pdf-pycrack programmatically in your Python code:

```python
from pdf_pycrack import crack_pdf_password, PasswordFound

result = crack_pdf_password(
    pdf_path="my_encrypted_file.pdf",
    min_len=4,
    max_len=6,
    charset="0123456789"
)

if isinstance(result, PasswordFound):
    print(f"Password found: {result.password}")
```


## Benchmarking

Measure and compare password cracking speed with the advanced benchmarking tool:

```bash
uv run python benchmark/benchmark.py --standard
```

**Custom runs:**

```bash
uv run python benchmark/benchmark.py --pdf tests/test_pdfs/letters/ab.pdf --min-len 1 --max-len 2 --charset abcdef
uv run python benchmark/benchmark.py --processes 4 --batch-size 1000
```

Results are saved in `benchmark/results/` as JSON and CSV. See [`benchmark/README.md`](benchmark/README.md) for full details, options, and integration tips.


## Testing & Error Handling

Run all tests:

```bash
uv run pytest
```

Tests are marked by category:

- `numbers`, `letters`, `special_chars`, `mixed`

Run a subset:

```bash
uv run pytest -m numbers
```

**Error Handling:**

The suite in `tests/test_error_handling.py` covers:
- File not found, permission denied, directory instead of file
- Corrupted/unencrypted PDFs
- Empty charset, invalid parameters
- Memory errors, worker process failures

All errors are reported with clear messages and suggested actions.


## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes and add/update tests
4. Run all tests and pre-commit hooks:
    ```bash
    uv run pre-commit install
    uv run pre-commit run --all-files
    uv run pytest
    ```
5. Open a pull request


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Further documentation:**
- [Benchmarking Guide](benchmark/README.md)
- [Test PDF Generation](scripts/README.md)
