# wKrQ CLI Guide: Command-Line Interface for the Tableau Calculus Implementation

**Version**: 1.1.2  
**Last Updated**: August 2025  
**License**: MIT  

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage](#basic-usage)
4. [Three-Valued Semantics](#three-valued-semantics)
5. [Tableau Signs](#tableau-signs)
6. [First-Order Features](#first-order-features)
7. [ACrQ Paraconsistent Reasoning](#acrq-paraconsistent-reasoning)
8. [Interactive Mode](#interactive-mode)
9. [Advanced Options](#advanced-options)
10. [Performance Features](#performance-features)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

## Overview

The wKrQ (weak Kleene logic with restricted quantification) CLI provides a powerful command-line interface for automated reasoning with three-valued logic. Unlike classical binary logic, wKrQ handles uncertainty and vagueness through a third truth value (undefined), making it ideal for philosophical logic, AI reasoning, and handling incomplete information.

### Key Features

- **Three-valued semantics**: True (t), False (f), Undefined (e)
- **Four tableau signs**: t, f, m, n for proof construction
- **Restricted quantification**: First-order logic with bounded quantifiers
- **Industrial performance**: Optimized tableau construction with sub-millisecond response times
- **Interactive mode**: Real-time exploration of logical systems
- **Multiple output formats**: Text, JSON, detailed tableau trees

## Installation & Setup

### Verify Installation

```bash
# Test basic functionality
python -m wkrq "p | ~p"

# Check version and help
python -m wkrq --version
python -m wkrq --help
```text

### Expected Output

```text
Testing formula: p | ~p
Result: SATISFIABLE
Models found: 1
  Model 1: {p=t}
Tableau nodes: 3
```text

## Basic Usage

### Command Structure

```bash
python -m wkrq [OPTIONS] "FORMULA"
```text

### Simple Examples

```bash
# Test satisfiability
python -m wkrq "p & q"

# Test tautologies
python -m wkrq "p | ~p"

# Test contradictions
python -m wkrq "p & ~p"

# Complex formulas
python -m wkrq "(p & q) | (~p & r)"
```text

### Basic Options

```bash
# Specify tableau sign
python -m wkrq --sign=t "p"        # Must be true
python -m wkrq --sign=f "p"        # Must be false
python -m wkrq --sign=m "p"        # Can be true or false
python -m wkrq --sign=n "p"        # Must be undefined

# Verbose output
python -m wkrq --verbose "p -> q"

# Show models
python -m wkrq --models "p | q"

# JSON output
python -m wkrq --format=json "p & q"
```text

## Three-Valued Semantics

wKrQ implements **weak Kleene** three-valued logic where any operation involving an undefined value results in undefined.

### Truth Values

- **t (true)**: Classical truth
- **f (false)**: Classical falsity  
- **e (undefined)**: Neither true nor false

### Truth Tables

#### Conjunction (∧)

```text
  ∧ | t | f | e
  --|---|---|---
  t | t | f | e
  f | f | f | e  
  e | e | e | e
```text

#### Disjunction (∨)

```text
  ∨ | t | f | e
  --|---|---|---
  t | t | t | e
  f | t | f | e
  e | e | e | e
```text

#### Negation (~)

```text
  ~ | t | f | e
  --|---|---|---
    | f | t | e
```text

#### Implication (→)

```text
  → | t | f | e
  --|---|---|---
  t | t | f | e
  f | t | t | e
  e | e | e | e
```text

### Testing Three-Valued Behavior

```bash
# In weak Kleene, these behave differently than classical logic:

# Test conjunction with undefined
python -m wkrq --sign=n "p & q"    # Can be undefined

# Test disjunction with undefined  
python -m wkrq --sign=n "p | q"    # Can be undefined (unlike strong Kleene)

# Test negation of undefined
python -m wkrq --sign=n "~p"       # Can be undefined
```text

## Tableau Signs

The tableau system uses six signs to construct proofs in three-valued logic:

### Sign Meanings

- **t**: Formula must have truth value **t** (true)
- **f**: Formula must have truth value **f** (false)
- **m**: Formula can have truth value **t or f** (multiple possibilities)
- **n**: Formula must have truth value **e** (neither/undefined)

### Using Signs

```bash
# Test all possible signs for a formula
python -m wkrq --sign=t "p"        # p must be true
python -m wkrq --sign=f "p"        # p must be false
python -m wkrq --sign=m "p"        # p can be true or false
python -m wkrq --sign=n "p"        # p must be undefined

# Complex formulas with specific signs
python -m wkrq --sign=n "p & q"    # Conjunction must be undefined
python -m wkrq --sign=m "p | q"    # Disjunction has multiple possibilities
```text

### Sign Relationships

```bash
# t and f are contradictory
python -m wkrq --sign=t "p & ~p"   # Unsatisfiable
python -m wkrq --sign=f "p | ~p"   # Unsatisfiable (in weak Kleene)

# m allows classical values
python -m wkrq --sign=m "p"        # Can be true or false

# n requires undefined values
python -m wkrq --sign=n "p"        # Must be undefined
```text

## First-Order Features

wKrQ supports first-order logic with restricted quantification.

### Predicates

```bash
# Simple predicates
python -m wkrq "P(a)"
python -m wkrq "R(x, y)"

# Complex predicate formulas
python -m wkrq "P(a) & Q(b)"
python -m wkrq "P(x) -> Q(x)"
```text

### Restricted Quantification

wKrQ uses restricted quantifiers that limit the domain of quantification.

#### Restricted Existential: [∃X P(X)]Q(X)

"There exists an X such that P(X) and Q(X)"

```bash
# Basic restricted existential
python -m wkrq "[∃X Student(X)]Human(X)"

# Complex restricted existential
python -m wkrq "[∃X Student(X)]Human(X) & Smart(a)"
```text

#### Restricted Universal: [∀X P(X)]Q(X)  

"For all X, if P(X) then Q(X)"

```bash
# Basic restricted universal
python -m wkrq "[∀X Human(X)]Mortal(X)"

# Complex restricted universal
python -m wkrq "[∀X Human(X)]Mortal(X) & Human(socrates)"
```text

### First-Order Examples

```bash
# Philosophical reasoning
python -m wkrq "[∃X Student(X)]Human(X)"
python -m wkrq "[∀X Human(X)]Mortal(X)"

# Complex reasoning
python -m wkrq "[∃X Student(X)]Human(X) & [∀X Human(X)]Mortal(X)"
```

## ACrQ Paraconsistent Reasoning

ACrQ (Analytic Containment with restricted Quantification) extends wKrQ with bilateral predicates to handle contradictory and incomplete information gracefully. The CLI automatically detects and processes ACrQ formulas using the underlying `parse_acrq_formula` functionality.

### Key ACrQ Features

- **Paraconsistent**: Handle contradictions without system explosion
- **Paracomplete**: Handle incomplete information without classical assumptions
- **Bilateral predicates**: Each R has a dual R* for independent positive/negative tracking
- **Information states**: True, False, Gaps (missing), Gluts (conflicting)

### Basic ACrQ Usage

```bash
# Contradictions don't cause explosion (paraconsistent)
python -m wkrq "Human(socrates) & ~Human(socrates)"
# Output shows "glut" - conflicting information

# Mixed reasoning with gaps and gluts
python -m wkrq "Human(x) & ~Robot(y)" --models
# Shows models with bilateral truth values

# Complex paraconsistent reasoning
python -m wkrq "(P(a) & ~P(a)) -> Q(b)" --sign=t
# Paraconsistent implication handling
```

### ACrQ with Quantifiers

```bash
# Paraconsistent universal reasoning
python -m wkrq "[∀X Human(X)]Mortal(X) & Human(socrates) & ~Human(socrates)"

# Existential with contradictory information
python -m wkrq "[∃X Student(X)]Human(X) & ~Human(john)"
```

### Understanding ACrQ Output

ACrQ extends standard output with bilateral information states:

```text
Formula: Human(x) & ~Human(x)
Result: Satisfiable
Model:
  Human(x) = glut (both positive and negative evidence)
```

**Information State Meanings:**

- `true`: Only positive evidence (R=t, R*=f)
- `false`: Only negative evidence (R=f, R*=t)  
- `gap`: No evidence (R=f, R*=f)
- `glut`: Conflicting evidence (R=t, R*=t) - paraconsistent

### Advanced ACrQ Usage

```bash
# Show detailed bilateral values
python -m wkrq "Human(x) & ~Human(x)" --models --json
# JSON output includes bilateral_valuations

# Complex paraconsistent entailment
python -m wkrq --inference "P(a) & ~P(a), Q(b) |- R(c)"
# Contradictory premises don't entail arbitrary conclusions
```

## Interactive Mode

Launch interactive mode for exploratory reasoning:

```bash
python -m wkrq
```text

### Interactive Commands

```text
wKrQ> test p & q
Testing formula: p & q
Result: SATISFIABLE
Models: [{p=t, q=t}]

wKrQ> sign n
Current sign: n (neither/undefined)

wKrQ> test p | ~p
Testing formula: p | ~p with sign n
Result: SATISFIABLE (in weak Kleene, this can be undefined)

wKrQ> models p | q
Models for p | q:
  Model 1: {p=t, q=f}
  Model 2: {p=f, q=t}
  Model 3: {p=t, q=t}

wKrQ> tableau p & ~p
Tableau construction for: p & ~p
t: p & ~p
├─ t: p        [t-Conjunction]
├─ t: ~p       [t-Conjunction]
   └─ f: p     [t-Negation]
      └─ ✗ CLOSED (t:p contradicts f:p)

wKrQ> help
Available commands:
  test FORMULA          - Test formula satisfiability
  models FORMULA        - Show all models
  tableau FORMULA       - Show tableau construction
  sign SIGN            - Set current sign (t, f, m, n)
  valid FORMULA        - Check if formula is valid
  help                 - Show this help
  quit                 - Exit interactive mode

wKrQ> quit
```text

### Interactive Features

- **Real-time testing**: Immediate feedback on formulas
- **Sign switching**: Change default sign for testing
- **Model exploration**: See all satisfying models
- **Tableau visualization**: Step-by-step proof construction
- **Command history**: Use up/down arrows for previous commands

## Advanced Options

### Detailed Output

```bash
# Show tableau construction steps
python -m wkrq --tableau "p | q"

# Show performance statistics
python -m wkrq --stats "complex_formula"

# Debug mode with detailed tracing
python -m wkrq --debug "p -> q"

# Combine multiple options
python -m wkrq --verbose --models --stats "p & (q | r)"
```text

### Output Formats

```bash
# JSON output for programmatic use
python -m wkrq --format=json "p & q"

# Compact output (minimal)
python -m wkrq --format=compact "p | q"

# Detailed human-readable (default)
python -m wkrq --format=detailed "p -> q"
```text

### Performance Options

```bash
# Limit tableau depth (for very complex formulas)
python -m wkrq --max-depth=50 "complex_formula"

# Enable/disable specific optimizations
python -m wkrq --no-early-termination "p | q"
python -m wkrq --no-subsumption "p & (q | r)"

# Benchmark mode
python -m wkrq --benchmark "p & q & r & s"
```text

## Performance Features

wKrQ includes industrial-grade optimizations:

### Optimization Categories

1. **Alpha/Beta Rule Prioritization**: Non-branching rules processed first
2. **Early Contradiction Detection**: O(1) contradiction detection
3. **Intelligent Branch Selection**: Least complex branches first
4. **Subsumption Elimination**: Remove redundant formulas
5. **Early Termination**: Stop on first satisfying model

### Performance Examples

```bash
# Show optimization effects
python -m wkrq --stats --verbose "p & q & r & (s | t | u)"

# Benchmark complex formulas
python -m wkrq --benchmark "(p1 | q1) & (p2 | q2) & (p3 | q3)"

# Compare with/without optimizations
python -m wkrq --no-optimization --stats "complex_formula"
python -m wkrq --stats "complex_formula"
```text

### Performance Monitoring

```bash
# Time individual operations
python -m wkrq --time "p & q"

# Memory usage statistics
python -m wkrq --memory "large_formula"

# Node count and branch statistics
python -m wkrq --tableau-stats "p | (q & r & s)"
```text

## Examples

### Basic Propositional Logic

```bash
# Tautologies
python -m wkrq "p | ~p"              # Classical tautology
python -m wkrq --sign=n "p | ~p"     # Can be undefined in weak Kleene

# Contradictions
python -m wkrq "p & ~p"              # Always unsatisfiable

# Contingent formulas
python -m wkrq "p -> q"              # Satisfiable
python -m wkrq --models "p -> q"     # Show all models
```text

### Three-Valued Reasoning

```bash
# Undefined value propagation
python -m wkrq --sign=n "p & q"      # Conjunction with undefined
python -m wkrq --sign=n "p | q"      # Disjunction with undefined
python -m wkrq --sign=n "~p"         # Negation of undefined

# Mixed truth values
python -m wkrq --models "p | q"      # Show classical and non-classical models
```text

### First-Order Logic

```bash
# Basic predicates
python -m wkrq "P(a) & Q(b)"
python -m wkrq "P(x) -> Q(x)"

# Restricted quantifiers
python -m wkrq "[∃X Student(X)]Human(X)"
python -m wkrq "[∀X Human(X)]Mortal(X)"

# Complex first-order reasoning
python -m wkrq "[∃X Student(X)]Human(X) & [∀X Human(X)]Mortal(X) & Student(alice)"
```text

### Philosophical Examples

```bash
# Sorites paradox
python -m wkrq "Heap(1000) & (Heap(1000) -> Heap(999)) & ~Heap(1)"

# Non-monotonic reasoning
python -m wkrq "Bird(tweety) & (Bird(tweety) -> Flies(tweety)) & Penguin(tweety) & ~Flies(tweety)"

# Vague predicates
python -m wkrq --sign=n "Tall(person) & Short(person)"
```text

### Performance Testing

```bash
# Scalability test
python -m wkrq --stats "p1 & p2 & p3 & p4 & p5 & p6 & p7 & p8"

# Branching complexity
python -m wkrq --tableau-stats "(p1 | q1) & (p2 | q2) & (p3 | q3)"

# Deep nesting
python -m wkrq --stats "p -> (q -> (r -> (s -> t)))"
```text

## Troubleshooting

### Common Issues

#### Parse Errors

```bash
# Problem: Syntax error
python -m wkrq "p &"
# Error: Parse error: Unexpected end of input

# Solution: Check formula syntax
python -m wkrq "p & q"  # Correct
```text

#### Performance Issues

```bash
# Problem: Formula takes too long
python -m wkrq "very_complex_formula"

# Solutions:
python -m wkrq --max-depth=20 "very_complex_formula"     # Limit depth
python -m wkrq --timeout=5000 "very_complex_formula"     # Set timeout (ms)
```text

#### Memory Issues

```bash
# Problem: High memory usage

# Solutions:
python -m wkrq --no-models "complex_formula"             # Don't compute models
python -m wkrq --early-termination "complex_formula"     # Stop early
```text

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Parse error" | Invalid formula syntax | Check parentheses, operators |
| "Timeout exceeded" | Formula too complex | Use `--max-depth` or `--timeout` |
| "Unknown predicate" | Undefined predicate in formula | Check predicate names |
| "Invalid sign" | Wrong sign specification | Use t, f, m, or n |

### Getting Help

```bash
# Command help
python -m wkrq --help

# Interactive help
python -m wkrq
wKrQ> help

# Version information
python -m wkrq --version

# Debug information
python -m wkrq --debug "formula"
```text

### Contact and Support

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory  
- **Issue Reporting**: GitHub issues
- **Performance Issues**: Include `--stats` output

---

*This guide covers the wKrQ command-line interface. For programmatic usage, see the API documentation. For theoretical background, see the architecture documentation.*
