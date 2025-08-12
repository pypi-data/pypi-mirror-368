# wKrQ CLI Guide

**Version:** 1.2.0  
**Date:** August 2025  
**Author:** Bradley P. Allen

The wKrQ (weak Kleene logic with restricted Quantification) command-line interface provides comprehensive tools for logical reasoning, tableau construction, and inference validation.

## Installation

```bash
pip install wkrq
```

## Basic Usage

### Formula Satisfiability Testing

Test if a formula can be satisfied under different signs:

```bash
# Test if formula is satisfiable under t (true) sign
wkrq "p & q"

# Test under specific signs
wkrq --sign=t "p | q"    # Must be true
wkrq --sign=f "p & ~p"   # Must be false (unsatisfiable)
wkrq --sign=m "p | ~p"   # Can be true or false
wkrq --sign=n "p"        # Must be undefined
```

### Tableau Tree Visualization

Display the reasoning process with tableau trees:

```bash
# Basic ASCII tree
wkrq --tree "p & q"

# Unicode tree with rule annotations
wkrq --tree --format=unicode --show-rules "p -> q"

# Show all models found
wkrq --models --tree "p | q"
```

### Inference Testing

Test if premises logically entail a conclusion:

```bash
# Using turnstile notation
wkrq "p, p -> q |- q"

# Using --inference flag
wkrq --inference "p, p -> q, q"

# Complex inference with explanation
wkrq --explain --tree --show-rules "p -> (q -> r), p, q |- r"
```

## Signs System

wKrQ uses a six-sign system for tableau construction:

- **t**: Formula must be true
- **f**: Formula must be false
- **e**: Formula must be undefined/error  
- **m**: Formula can be true or false (meaningful - branching instruction)
- **n**: Formula can be false or undefined (nontrue - branching instruction)
- **v**: Variable sign (meta-sign used in rule notation, not in formulas)

## Tableau Rules Reference

### Alpha Rules (Non-branching)

These rules extend a single branch:

```bash
# t-Conjunction: t:(A & B) → t:A, t:B
wkrq --sign=t --tree --show-rules "p & q"

# f-Disjunction: f:(A | B) → f:A, f:B  
wkrq --sign=f --tree --show-rules "p | q"

# t-Negation: t:~A → f:A
wkrq --sign=t --tree --show-rules "~p"

# f-Negation: f:~A → t:A
wkrq --sign=f --tree --show-rules "~p"

# f-Implication: f:(A -> B) → t:A, f:B
wkrq --sign=f --tree --show-rules "p -> q"
```

### Beta Rules (Branching)

These rules create multiple branches:

```bash
# t-Disjunction: t:(A | B) → t:A | t:B
wkrq --sign=t --tree --show-rules "p | q"

# f-Conjunction: f:(A & B) → f:A | f:B
wkrq --sign=f --tree --show-rules "p & q"

# t-Implication: t:(A -> B) → f:A | t:B
wkrq --sign=t --tree --show-rules "p -> q"
```

### Epistemic Rules (m/n Signs)

```bash
# m-signs branch to both t and f possibilities
wkrq --sign=m --tree --show-rules "p & q"

# n-signs propagate undefined values
wkrq --sign=n --tree --show-rules "p -> q"
```

## Restricted Quantifiers

wKrQ supports restricted quantification for domain-specific reasoning:

```bash
# Universal quantification: "All humans are mortal"
wkrq --tree --show-rules "[∀X Human(X)]Mortal(X)"

# Existential quantification: "Some human is mortal"  
wkrq --tree --show-rules "[∃X Human(X)]Mortal(X)"

# Quantified inference
wkrq --tree --show-rules "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
```

## Advanced Features

### Output Formats

```bash
# JSON output for programmatic use
wkrq --json "p & q"

# LaTeX for academic papers
wkrq --tree --format=latex "p -> q"

# Statistical analysis
wkrq --stats --tree "complex_formula"
```

### Performance Optimization

```bash
# Show debug information
wkrq --debug --tree "p & q & r"

# Compact display
wkrq --compact --tree "large_formula"
```

### ACrQ Mode (Bilateral Predicates)

```bash
# Enable ACrQ for paraconsistent reasoning
wkrq --mode=acrq "Human(alice) & ¬Human(alice)"

# Bilateral syntax mode
wkrq --mode=acrq --syntax=bilateral "Human*(alice)"
```

## Common Patterns

### Validating Classical Reasoning

```bash
# Modus ponens (valid)
wkrq "p, p -> q |- q"

# Affirming the consequent (invalid)
wkrq "p -> q, q |- p"

# Hypothetical syllogism (valid)
wkrq "p -> q, q -> r |- p -> r"
```

### Testing Logical Properties

```bash
# Classical tautology (not valid in weak Kleene)
wkrq --sign=f "p | ~p"  # Unsatisfiable (cannot be false)
wkrq --sign=n "p | ~p"  # Satisfiable (can be undefined)

# Contradiction
wkrq --sign=t "p & ~p"  # Unsatisfiable (cannot be true)
```

### Complex Formula Analysis

```bash
# Show complete reasoning process
wkrq --tree --show-rules --format=unicode --stats "((p -> q) -> ((q -> r) -> (p -> r)))"

# Find all satisfying models
wkrq --models --tree "(p | q) & (q | r) & (r | p)"
```

## Integration Examples

### Batch Processing

```bash
# Process multiple formulas
echo "p & q" | wkrq --tree
echo "p -> q" | wkrq --inference --explain
```

### Educational Use

```bash
# Step-by-step tableau construction
wkrq --tree --show-rules --format=unicode --explain "complex_inference"

# Visual comparison of different signs
wkrq --sign=t --tree "p | ~p"
wkrq --sign=f --tree "p | ~p" 
wkrq --sign=n --tree "p | ~p"
```

This guide demonstrates the wKrQ CLI's comprehensive features for logical analysis, education, and research applications.
