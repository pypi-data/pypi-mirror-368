# wKrQ Documentation

**wKrQ** (weak Kleene logic with restricted quantification) is a three-valued logic system with restricted quantifiers for first-order reasoning, based on Ferguson (2021).

## Quick Start

```bash
# Install
pip install wkrq

# Test a formula
wkrq "p & ~p"                    # Contradiction (unsatisfiable)
wkrq "p | ~p"                    # Tautology in classical logic
wkrq --tree "p -> q"             # Show tableau proof tree

# Test an inference
wkrq "p, p -> q |- q"            # Modus ponens (valid)

# ACrQ mode (paraconsistent with bilateral predicates)
wkrq --mode=acrq "Human(x) & ~Human(x)"  # Glut allowed!
```

## Documentation

- **[API.md](API.md)** - Complete API reference for Python usage
- **[CLI.md](CLI.md)** - Command-line interface guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and Ferguson compliance
- **[EXAMPLES.md](EXAMPLES.md)** - Usage patterns and examples

## System Overview

### wKrQ (Standard System)
- Three-valued logic: `t` (true), `f` (false), `e` (undefined/error)
- Weak Kleene semantics: any operation with undefined yields undefined
- No tautologies: every formula can be undefined when inputs are undefined
- Restricted quantification: `[∃x P(x)]Q(x)` and `[∀x P(x)]Q(x)`
- Ferguson's 6-sign tableau system: `t`, `f`, `e`, `m`, `n`, `v`

### ACrQ (Paraconsistent Extension)
- Bilateral predicates: each predicate R has dual R* for negative evidence
- Four information states: true, false, gap (no info), glut (conflicting info)
- Paraconsistent: handles contradictions without explosion
- Based on Ferguson Definition 18

## Key Features

1. **Unified Tableau Engine** - Single implementation for both wKrQ and ACrQ
2. **LLM Integration** - Optional LLM evaluation of atomic formulas
3. **Complete Ferguson Compliance** - Exact implementation of Ferguson (2021)
4. **Rich CLI** - Interactive mode, tree visualization, inference testing
5. **Python API** - Full programmatic access to all features

## Installation

```bash
# From PyPI
pip install wkrq

# Development install
git clone https://github.com/yourusername/wkrq.git
cd wkrq
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_wkrq_basic.py  # Run specific test
pytest --cov=wkrq        # With coverage
```

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed examples including:
- Basic propositional logic
- First-order logic with quantifiers
- ACrQ paraconsistent reasoning
- LLM integration
- Complex inference patterns

## References

Ferguson, T. M. (2021). *Weak Kleene Logics with Restricted Quantification*.