# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WeTextProcessing is a production-ready text processing toolkit for Text Normalization (TN) and Inverse Text Normalization (ITN) supporting Chinese, English, Japanese, Catalan, Galician, and Basque. Built on OpenFst and Pynini for finite-state transducers (FST).

- **TN**: Converts written text to spoken form (e.g., "2.5" → "二点五")
- **ITN**: Reverses the process (e.g., "二点五" → "2.5")

## Common Commands

### Installation
```bash
pip install -e .
pip install -r requirements.txt
```

### Running Tests
```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest tn/chinese/test/             # Run Chinese TN tests
pytest tn/english/test/             # Run English TN tests
pytest itn/chinese/test/            # Run Chinese ITN tests
pytest tn/chinese/test/cardinal_test.py  # Run single test file
```

### Linting
```bash
flake8                              # Run linter (max-line-length: 80)
pre-commit run --all-files          # Run all pre-commit hooks (yapf, flake8)
```

### CLI Usage
```bash
wetn --text "2.5平方电线"            # TN Chinese (default)
wetn --language en --text "Hello"   # TN English
wetn --language ca --text "25"      # TN Catalan
wetn --language gl --text "25"      # TN Galician
wetn --language eu --text "25"      # TN Basque
weitn --text "二点五平方电线"         # ITN Chinese
python -m tn --text "..." --overwrite_cache  # Rebuild FST cache
```

### Building C++ Runtime
```bash
cmake -B build -S runtime -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

## Architecture

### Core Components

1. **Processor** (`tn/processor.py`): Base class managing FST tagger/verbalizer operations with Pynini. Methods: `tag()`, `verbalize()`, `normalize()`. Supports FST caching as `.fst` files.

2. **Normalizers**: Language-specific classes orchestrating multiple rule FSTs:
   - `tn.chinese.normalizer.Normalizer`
   - `tn.english.normalizer.Normalizer`
   - `itn.chinese.inverse_normalizer.InverseNormalizer`

3. **Rule Modules** (`*/rules/*.py`): Each rule (cardinal, date, fraction, measure, money, time, etc.) implements:
   - `build_tagger()`: Creates input tagging FST
   - `build_verbalizer()`: Creates output conversion FST

4. **Token Parser** (`tn/token_parser.py`): Reorders token components based on language-specific ordering rules (TN_ORDERS, ITN_ORDERS, EN_TN_ORDERS).

### Data Files

TSV files in `*/data/` directories define character mappings, number conversions, currency units, etc. Used with Pynini's `string_file()` for FST creation.

### Key Pynini Patterns
```python
from pynini import cross, string_file, union
from pynini.lib.pynutil import delete, insert, add_weight
# Weighted unions for rule combination
# cdrewrite() for contextual rewriting
# @ operator for FST composition
```

### Test Structure

Tests use pytest with parametrized data from TSV files:
- Test files: `*_test.py` in `*/test/` directories
- Test data: TSV files parsed via `utils.parse_test_case(filename)`

## Language Modules

Each language has parallel TN structures (ITN available for zh, ja):
```
tn/{language}/
├── rules/           # Rule modules (cardinal.py, date.py, etc.)
├── data/            # TSV lookup data
├── test/            # pytest test files with test data
└── normalizer.py    # Main Normalizer class
```

Supported languages:
- `zh` - Chinese
- `en` - English
- `ja` - Japanese
- `ca` - Catalan (vigesimal-influenced decimal)
- `gl` - Galician
- `eu` - Basque (vigesimal number system)
