# wKrQ: A Python Implementation of a Semantic Tableau Calculus for Weak Kleene Logic with Restricted Quantification

[![PyPI version](https://badge.fury.io/py/wkrq.svg?v=2.1.0)](https://badge.fury.io/py/wkrq)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bradleypallen/wkrq/actions/workflows/tests.yml/badge.svg)](https://github.com/bradleypallen/wkrq/actions/workflows/tests.yml)

An implementation of a semantic tableau calculus for first-order weak
Kleene logic with restricted quantification, featuring a command-line
interface for satisfiability and inference checking.

## Citation

This implementation is based on the wKrQ tableau system defined in:

**Ferguson, Thomas Macaulay**. "Tableaux and restricted quantification for
systems related to weak Kleene logic." In *International Conference on
Automated Reasoning with Analytic Tableaux and Related Methods*, pp. 3-19.
Cham: Springer International Publishing, 2021.

The tableau construction algorithms and six-sign system (t, f, e, m, n, v)
implemented here follow Ferguson's formal definitions exactly. This is a research
implementation created for experimental and educational purposes.

## Research Software Disclaimer

⚠️ **This is research software.** While extensively tested, this
implementation may contain errors or behave unexpectedly in edge cases. It
is intended for research, education, and experimentation. Use in production
systems is not recommended without thorough validation. Please report any
issues or unexpected behavior through the [issue
tracker](https://github.com/bradleypallen/wkrq/issues).

## Features

- 🎯 **Three-valued semantics**: true (t), false (f), undefined (e)
- 🔤 **Weak Kleene logic**: Operations with undefined propagate undefinedness
- 🔢 **Restricted quantification**: Domain-bounded first-order reasoning
- 📋 **Ferguson's six-sign system**: t, f, e, m, n, v exactly as in the 2021 paper
- 🔄 **ACrQ extension**: Analytic Containment for paraconsistent/paracomplete reasoning
- ⚡ **Industrial performance**: Optimized tableau with sub-millisecond response
- 🖥️ **CLI and API**: Both command-line and programmatic interfaces
- 📚 **Comprehensive docs**: Full documentation with examples
- 🔍 **Construction tracing**: Step-by-step proof visualization showing all rule applications

## Quick Start

### Installation

```bash
pip install wkrq
```

### Command Line Usage

```bash
# Test a simple formula
wkrq "p & q"

# Test with specific sign (t, f, e, m, n)
wkrq --sign=n "p | ~p"

# Show all models
wkrq --models "p | q"

# Display tableau tree
wkrq --tree "p -> q"

# Show construction trace
wkrq --trace "p & ~p"

# First-order logic with restricted quantifiers
# Unicode syntax:
wkrq "[∃X Student(X)]Human(X)"
wkrq "[∀X Human(X)]Mortal(X)"

# ASCII syntax (easier to type):
wkrq "[exists X Student(X)]Human(X)"
wkrq "[forall X Human(X)]Mortal(X)"

# Inference checking
wkrq --inference "p & q |- p"
wkrq --inference "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"

# ACrQ paraconsistent reasoning (handles contradictions gracefully)
wkrq "Human(x) & ~Human(x)"  # Shows paraconsistent model with "glut"
```

### Python API

```python
from wkrq import Formula, solve, valid, t, f, e, m, n

# Create formulas
p, q = Formula.atoms('p', 'q')
formula = p & (q | ~p)

# Test satisfiability
result = solve(formula, t)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")

# Test validity - Ferguson uses classical validity with weak Kleene
# semantics
tautology = p | ~p
print(f"Valid in Ferguson's system: {valid(tautology)}")  # True (classical
                                                         # tautologies are valid)

# Three-valued reasoning
result = solve(p | ~p, e)  # Can it be undefined?
print(f"Can be undefined: {result.satisfiable}")  # True

# ACrQ paraconsistent reasoning
from wkrq import parse_acrq_formula, SyntaxMode

# Handle contradictions gracefully (no explosion)
contradiction = parse_acrq_formula("Human(x) & ~Human(x)")
result = solve(contradiction, t)
print(f"Contradiction satisfiable: {result.satisfiable}")  # True (glut allowed)

# Different syntax modes for ACrQ
transparent = parse_acrq_formula("~Human(x)", SyntaxMode.TRANSPARENT)  # Standard syntax
bilateral = parse_acrq_formula("Human*(x)", SyntaxMode.BILATERAL)      # Explicit bilateral
```

## Syntax and Semantics

### Formal Language Definition

The language of wKrQ is defined by the following BNF grammar:

```bnf
⟨formula⟩ ::= ⟨atom⟩ | ⟨compound⟩ | ⟨quantified⟩

⟨atom⟩ ::= p | q | r | ... | ⟨predicate⟩

⟨predicate⟩ ::= P(⟨term⟩,...,⟨term⟩)

⟨term⟩ ::= ⟨variable⟩ | ⟨constant⟩

⟨variable⟩ ::= X | Y | Z | ...

⟨constant⟩ ::= a | b | c | ...

⟨compound⟩ ::= ¬⟨formula⟩ | (⟨formula⟩ ∧ ⟨formula⟩) | 
               (⟨formula⟩ ∨ ⟨formula⟩) | (⟨formula⟩ → ⟨formula⟩)

⟨quantified⟩ ::= [∃⟨variable⟩ ⟨formula⟩]⟨formula⟩ | 
                 [∀⟨variable⟩ ⟨formula⟩]⟨formula⟩
```

### Truth Tables

wKrQ implements **weak Kleene** three-valued logic with truth values:

- **t** (true)
- **f** (false)  
- **e** (undefined/error)

#### Negation (¬)

| p | ¬p |
|---|-----|
| t | f |
| f | t |
| e | e |

#### Conjunction (∧)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | f | e |
| **f** | f | f | e |
| **e** | e | e | e |

#### Disjunction (∨)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | t | e |
| **f** | t | f | e |
| **e** | e | e | e |

#### Material Implication (→)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | f | e |
| **f** | t | t | e |
| **e** | e | e | e |

### Quantifier Semantics

#### Restricted Existential Quantification: [∃X φ(X)]ψ(X)

The formula is true iff there exists a domain element d such that both
φ(d) and ψ(d) are true. It is false iff for all domain elements d, either
φ(d) is false or ψ(d) is false (but not undefined). It is undefined if any
evaluation results in undefined.

#### Restricted Universal Quantification: [∀X φ(X)]ψ(X)  

The formula is true iff for all domain elements d, either φ(d) is false
or ψ(d) is true. It is false iff there exists a domain element d such that
φ(d) is true and ψ(d) is false. It is undefined if any evaluation results
in undefined.

The key principle of weak Kleene logic is that **any operation involving
an undefined value produces an undefined result**. This differs from strong
Kleene logic where, for example, `t ∨ e = t`.

## ACrQ: Analytic Containment with restricted Quantification

ACrQ extends wKrQ with **bilateral predicates** for paraconsistent and paracomplete reasoning:

### Key Features

- **Paraconsistent**: Handle contradictory information without explosion
- **Paracomplete**: Handle incomplete information without classical assumptions  
- **Bilateral predicates**: Each predicate R has a dual R* for independent positive/negative tracking
- **Information states**: Distinguishes true, false, gaps (missing info), and gluts (conflicting info)

### Usage Modes

```python
from wkrq import parse_acrq_formula, SyntaxMode

# Transparent mode (default): Standard syntax, automatic translation
formula1 = parse_acrq_formula("Human(x) & ~Human(x)")  # Handles gluts

# Bilateral mode: Explicit R/R* syntax required
formula2 = parse_acrq_formula("Human(x) & Human*(x)", SyntaxMode.BILATERAL)

# Mixed mode: Both syntaxes allowed
formula3 = parse_acrq_formula("Human(x) & Robot*(y)", SyntaxMode.MIXED)
```

### Information States

| State | R(a) | R*(a) | Meaning |
|-------|------|-------|---------|
| True | t | f | Positive evidence only |
| False | f | t | Negative evidence only |
| Gap | f | f | No evidence (incomplete) |
| Glut | t | t | Conflicting evidence (paraconsistent) |

## Documentation

- 📖 [CLI Guide](https://github.com/bradleypallen/wkrq/blob/main/docs/CLI_GUIDE.md) - Complete command-line reference with examples
- 🔧 [API Reference](https://github.com/bradleypallen/wkrq/blob/main/docs/API_REFERENCE.md) - Full Python API documentation with code examples
- 📋 [Comprehensive Examples](https://github.com/bradleypallen/wkrq/blob/main/examples/validation.txt) - Literature validation with tableau trees

## Examples

### Philosophical Logic: Sorites Paradox

```python
from wkrq import Formula, solve, T, N

# Model vague predicates with three-valued logic
heap_1000 = Formula.atom("Heap1000")  # Clearly a heap
heap_999 = Formula.atom("Heap999")    # Borderline case
heap_1 = Formula.atom("Heap1")        # Clearly not a heap

# Sorites principle
sorites = heap_1000.implies(heap_999)

# The paradox dissolves with undefined values
result = solve(heap_999, N)  # Can be undefined
print(f"Borderline case can be undefined: {result.satisfiable}")
```

### First-Order Reasoning

```python
from wkrq import Formula

# Variables and predicates
x = Formula.variable("X")
human = Formula.predicate("Human", [x])
mortal = Formula.predicate("Mortal", [x])

# Restricted quantification
all_humans_mortal = Formula.restricted_forall(x, human, mortal)
print(f"∀-formula: {all_humans_mortal}")  # [∀X Human(X)]Mortal(X)
```

## Development

```bash
# Clone repository
git clone https://github.com/bradleypallen/wkrq.git
cd wkrq

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
ruff check src tests

# Type checking
mypy src
```

## Implementation Approach

The wKrQ package implements a semantic tableau calculus for three-valued weak Kleene logic with restricted quantification. The tableau engine (`tableau.py`) uses a six-sign system (t, f, e, m, n, v) following Ferguson (2021), where t and f represent definite truth values, e represents error/undefined, m represents epistemic uncertainty (both true and false are possible), n represents nontrue (false or undefined), and v is a meta-sign used in rule notation. The core algorithm maintains branches as collections of signed formulas, with hash-based indexing by sign and formula for O(1) contradiction detection. The system applies tableau rules in priority order: alpha-rules (non-branching) before beta-rules (branching), with explicit priority values assigned to each rule type. For quantifier instantiation, the engine tracks ground terms per branch and attempts unification with existing constants before generating fresh ones. Universal quantifiers are re-instantiated with new constants as they appear, with the system tracking which constants have been used for each quantified formula to prevent redundant applications. The implementation supports extension to ACrQ through polymorphic branch creation, where bilateral predicates R and R* are processed independently—t:R(a) generates only t:R(a) rather than also concluding f:R*(a), enabling paraconsistent reasoning where contradictory information (t:R(a) ∧ t:R*(a)) remains satisfiable. Model extraction from open branches assigns truth values based on the signs present: t-signed atoms map to true, f-signed to false, e-signed to undefined, with m-signed atoms arbitrarily assigned (true or false) to maintain completeness.

The ACrQ implementation extends wKrQ's tableau calculus to handle bilateral predicates for paraconsistent reasoning. Each predicate R has an associated dual predicate R*, with the system maintaining bidirectional mappings between them. The `ACrQTableau` class overrides the base tableau's branch creation to use `ACrQBranch` instances that track bilateral predicate pairs. During formula processing, negated predicates in transparent syntax mode are automatically converted: ¬R(x) becomes R*(x). The tableau rules for bilateral predicates differ fundamentally from standard predicates: t:R(x) produces only t:R(x) as a conclusion, while t:R*(x) produces only t:R*(x), without generating complementary constraints. Similarly, f:R(x) yields only f:R(x), and f:R*(x) yields only f:R*(x). The m-sign rules branch on individual predicates (m:R(x) branches to t:R(x) or f:R(x)), while n-sign rules generate knowledge gaps (n:R(x) produces f:R(x) and f:R*(x)). This design permits gluts where both R(a) and R*(a) hold true simultaneously—the `_check_contradiction` method in `ACrQBranch` explicitly allows t:R(a) and t:R*(a) to coexist without closing the branch. Model extraction constructs `ACrQModel` instances containing bilateral valuations: for each predicate-argument combination, the model tracks both positive and negative truth values as a `BilateralTruthValue` object. The semantic evaluator (`ACrQEvaluator`) retrieves the appropriate component based on whether the formula references R (positive component) or R* (negative component), maintaining weak Kleene semantics where any operation involving undefined values produces undefined results.

**Note**: Our implementation is validated against Ferguson (2021) and uses
classical validity with weak Kleene semantics, meaning classical tautologies
remain valid. The implementation has been thoroughly tested against literature
examples - see the [validation examples](https://github.com/bradleypallen/wkrq/blob/main/examples/validation.txt) for comprehensive test results.

## Citation

If you use wKrQ in academic work, please cite:

```bibtex
@software{wkrq2025,
  title={wKrQ: A Python Implementation of a Semantic Tableau Calculus for
         Weak Kleene Logic with Restricted Quantification},
  author={Allen, Bradley P.},
  year={2025},
  version={1.2.0},
  url={https://github.com/bradleypallen/wkrq}
}
```

## License

MIT License - see [LICENSE](https://github.com/bradleypallen/wkrq/blob/main/LICENSE) file for details.

## Links

- [PyPI Package](https://pypi.org/project/wkrq/)
- [GitHub Repository](https://github.com/bradleypallen/wkrq)
- [Issue Tracker](https://github.com/bradleypallen/wkrq/issues)
- [CLI Guide](https://github.com/bradleypallen/wkrq/blob/main/docs/CLI_GUIDE.md)
- [API Reference](https://github.com/bradleypallen/wkrq/blob/main/docs/API_REFERENCE.md)
- [wKrQ vs ACrQ Comparison](https://github.com/bradleypallen/wkrq/blob/main/docs/wKrQ_vs_ACrQ_COMPARISON.md)
