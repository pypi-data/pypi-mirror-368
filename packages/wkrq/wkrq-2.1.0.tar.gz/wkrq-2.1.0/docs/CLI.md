# wKrQ CLI Guide

## Basic Usage

```bash
# Test satisfiability
wkrq "p & ~p"                    # Contradiction
wkrq "p | q"                     # Satisfiable

# Test with different signs
wkrq --sign=f "p | q"            # Test if formula can be false
wkrq --sign=e "p -> q"           # Test if formula can be undefined

# Test inference validity
wkrq "p, p -> q |- q"            # Modus ponens (valid)
wkrq --inference "p, q, r"       # Last item is conclusion

# Show models
wkrq --models "p | q"            # Show all satisfying models
```

## Visualization

### Tree Display
```bash
# ASCII tree (default)
wkrq --tree "p & (q | r)"

# Unicode tree (prettier)
wkrq --tree --format=unicode "p -> q"

# Show rule names
wkrq --tree --show-rules "[∀x P(x)]Q(x)"

# Highlight closed branches
wkrq --tree --highlight-closures "p & ~p"

# JSON output
wkrq --tree --format=json "p | q" | jq
```

### LaTeX Export
```bash
# Generate LaTeX/TikZ code
wkrq --tree --format=latex "p -> q" > tableau.tex
```

## ACrQ Mode (Paraconsistent)

```bash
# Enable ACrQ mode
wkrq --mode=acrq "Human(alice) & ~Human(alice)"  # Glut allowed!

# Syntax modes for ACrQ
wkrq --mode=acrq --syntax=transparent "~P(x)"    # Default: ~P(x) → P*(x)
wkrq --mode=acrq --syntax=bilateral "P*(x)"      # Explicit R/R* syntax
wkrq --mode=acrq --syntax=mixed "P(x) & Q*(x)"   # Both syntaxes

# ACrQ inference
wkrq --mode=acrq "Human(x), ~Human(x) |- Robot(x)"
```

## Inference Testing

```bash
# Basic inference
wkrq "p, p -> q |- q"                  # Valid (modus ponens)
wkrq "p | q, ~p |- q"                  # Valid (disjunctive syllogism)

# With countermodels
wkrq --inference --countermodel "p |- q"  # Shows countermodel

# Explain inference
wkrq --inference --explain "p, p -> q |- q"

# Quantified inference
wkrq "[∀x Human(x)]Mortal(x), Human(socrates) |- Mortal(socrates)"
```

## Advanced Options

### Output Formats
```bash
# JSON output for programmatic use
wkrq --json "p & q"

# Show statistics
wkrq --stats "p | (q & r)"

# Debug mode
wkrq --debug "p -> q"
```

### Construction Tracing
```bash
# Show complete construction trace
wkrq --trace "p & ~p"

# Verbose trace with all details
wkrq --trace-verbose "p -> q, q -> r |- p -> r"

# Combine with tree visualization
wkrq --tree --trace "[∀X P(X)]Q(X) & P(a) & ~Q(a)"

# Trace shows:
# - Every rule application in sequence
# - What each rule produces (all formulas)
# - Which formulas get added to the tree
# - Why certain formulas don't appear (e.g., branch already closed)
# - When and why branches close
```

### Interactive Mode
```bash
# Start interactive REPL
wkrq
wkrq> p & q
Satisfiable: True
wkrq> p, p -> q |- q
✓ Valid inference
wkrq> quit
```

## Complete Examples

### Example 1: Propositional Logic
```bash
# Test satisfiability
wkrq "p & ~p"                    # Unsatisfiable (contradiction)
wkrq "(p -> q) -> (~q -> ~p)"    # Valid (contraposition)

# Show proof tree
wkrq --tree --show-rules "p | ~p"

# Test inference with tree
wkrq --tree --inference "p | q, ~p |- q"
```

### Example 2: First-Order Logic
```bash
# Universal quantifier
wkrq "[∀x Human(x)]Mortal(x)"

# Existential quantifier
wkrq "[∃x Student(x)]Smart(x)"

# Complex quantified formula
wkrq "[∀x Bird(x)]([∃y Worm(y)]Eats(x,y))"

# Quantified inference
wkrq --tree "[∀x P(x)]Q(x), P(a) |- Q(a)"
```

### Example 3: ACrQ Paraconsistent
```bash
# Glut (both R and R* true)
wkrq --mode=acrq "Human(alice) & Human*(alice)"

# Gap (neither R nor R* true)  
wkrq --mode=acrq --sign=n "Robot(alice)"

# Complex ACrQ reasoning
wkrq --mode=acrq --tree "Human(x) & ~Human(x) -> Nice(x)"

# ACrQ with quantifiers
wkrq --mode=acrq "[∀x Human(x) & ~Human(x)]Confused(x)"
```

### Example 4: Validation Testing
```bash
# Validate classical theorems
wkrq "((p -> q) & (q -> r)) -> (p -> r)"  # Transitivity
wkrq "(p & (p -> q)) -> q"                # Modus ponens theorem

# Test De Morgan's laws
wkrq "~(p & q) -> (~p | ~q)"
wkrq "~(p | q) -> (~p & ~q)"

# Test quantifier duality
wkrq "~[∀x P(x)] -> [∃x ~P(x)]"
```

## Options Reference

```
wkrq [OPTIONS] [INPUT]

Options:
  --version             Show version
  --sign {t,f,e,m,n}    Sign to test (default: t)
  --mode {wkrq,acrq}    Logic mode (default: wkrq)
  --syntax {transparent,bilateral,mixed}  ACrQ syntax mode
  --models              Show all models
  --stats               Show statistics
  --debug               Show debug information
  
Inference:
  --inference           Treat input as inference
  --consequence {strong,weak}  Consequence relation type
  --explain             Explain inference result
  --countermodel        Show countermodel for invalid inference
  
Tree Display:
  --tree                Display tableau tree
  --format {ascii,unicode,latex,json}  Tree format
  --show-rules          Show rule names in tree
  --show-steps          Show step numbers
  --highlight-closures  Highlight closed branches
  --compact             Compact tree display
  
Output:
  --json                Output as JSON
  --interactive         Interactive mode
```

## Tips

1. **Use quotes** around formulas to prevent shell interpretation
2. **Unicode input** is supported: `∀`, `∃`, `∧`, `∨`, `→`, `¬`
3. **ASCII alternatives**: `forall`, `exists`, `&`, `|`, `->`, `~`
4. **Inference separator**: Use `|-` for turnstile
5. **Multiple premises**: Separate with commas
6. **ACrQ mode**: Enables paraconsistent reasoning with bilateral predicates