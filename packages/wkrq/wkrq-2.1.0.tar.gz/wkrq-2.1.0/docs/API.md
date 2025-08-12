# wKrQ API Reference

## Core API Functions

### `solve(formula, sign=t)`
Solve a formula with the given sign using tableau method.

```python
from wkrq import solve, parse

formula = parse("p & ~p")
result = solve(formula)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")
```

### `valid(formula)`
Check if a formula is valid (true in all models).

```python
from wkrq import valid, parse

formula = parse("p -> p")
print(f"Valid: {valid(formula)}")  # True for tautologies
```

### `entails(premises, conclusion)`
Check if premises entail conclusion.

```python
from wkrq import entails, parse

premises = [parse("p"), parse("p -> q")]
conclusion = parse("q")
print(f"Entails: {entails(premises, conclusion)}")  # True (modus ponens)
```

## Formula Construction

### Parsing
```python
from wkrq import parse, parse_inference

# Parse formulas
formula = parse("p & (q | r)")
formula = parse("[∀x Human(x)]Mortal(x)")  # Restricted quantifier

# Parse inference
inference = parse_inference("p, p -> q |- q")
```

### Direct Construction
```python
from wkrq import Formula, PropositionalAtom, PredicateFormula, Constant, Variable

# Propositional
p = PropositionalAtom("p")
q = PropositionalAtom("q")
formula = p.implies(q)  # p -> q

# First-order
human = PredicateFormula("Human", [Variable("x")])
mortal = PredicateFormula("Mortal", [Variable("x")])
```

## Tableau System

### Unified Tableau
```python
from wkrq import WKrQTableau, ACrQTableau, SignedFormula, t, f

# wKrQ tableau
formulas = [SignedFormula(t, parse("p & ~p"))]
tableau = WKrQTableau(formulas)
result = tableau.construct()

# ACrQ tableau (paraconsistent)
formulas = [SignedFormula(t, parse_acrq_formula("Human(x) & ~Human(x)"))]
tableau = ACrQTableau(formulas)
result = tableau.construct()

# Enable construction tracing
tableau = WKrQTableau(formulas, trace=True)
result = tableau.construct()
result.print_trace()  # Shows complete rule applications
```

### LLM Integration
```python
from wkrq import ACrQTableau, BilateralTruthValue, TRUE, FALSE

def llm_evaluator(formula):
    """Custom LLM evaluator for atomic formulas."""
    if str(formula) == "Human(socrates)":
        return BilateralTruthValue(positive=TRUE, negative=FALSE)
    # Return gap (no knowledge)
    return BilateralTruthValue(positive=FALSE, negative=FALSE)

tableau = ACrQTableau(formulas, llm_evaluator=llm_evaluator)
result = tableau.construct()
```

## Signs and Semantics

### Signs (Ferguson's 6-sign system)
```python
from wkrq import t, f, e, m, n, SignedFormula

# Truth value signs
t  # true
f  # false  
e  # error/undefined

# Branching signs
m  # meaningful (branches to t or f)
n  # nontrue (branches to f or e)
```

### Truth Values
```python
from wkrq import TRUE, FALSE, UNDEFINED, WeakKleeneSemantics

# Evaluate with weak Kleene semantics
semantics = WeakKleeneSemantics()
result = semantics.evaluate_formula(formula, interpretation)
```

## Construction Tracing

### Enable Tracing for Any Proof
```python
from wkrq import solve, valid, entails, check_inference

# Trace formula solving
result = solve(formula, trace=True)
result.print_trace()  # Shows step-by-step construction
result.print_trace(verbose=True)  # More detailed output

# Trace validity checking
formula = parse("P | ~P")
result = solve(formula, f, trace=True)  # Check if can be false
if result.construction_trace:
    # Access trace programmatically
    for step in result.construction_trace.rule_applications:
        print(f"Step {step.step_number}: {step.rule_name}")
        print(f"  Produced: {step.produced_formulas}")

# Trace inference checking
result = check_inference(inference, trace=True)
result.tableau_result.print_trace()
```

### Understanding Rule Applications
```python
# The trace shows:
# 1. What each rule produces (complete output)
# 2. Which formulas actually get added to the tree
# 3. When and why branches close
# 4. Formulas that weren't added due to early closure

# Example: LLM gap produces both f:P(x) and f:P*(x)
# but if f:P(x) causes immediate closure, f:P*(x) won't appear in tree
# The trace shows both were produced by the rule
```

## ACrQ Bilateral Predicates

### Parsing ACrQ Formulas
```python
from wkrq import parse_acrq_formula, SyntaxMode

# Transparent mode (default): ~P(x) becomes P*(x)
formula = parse_acrq_formula("Human(x) & ~Human(x)")

# Bilateral mode: explicit R/R* syntax
formula = parse_acrq_formula("Human*(x)", SyntaxMode.BILATERAL)

# Mixed mode: both syntaxes allowed
formula = parse_acrq_formula("Human(x) & Robot*(x)", SyntaxMode.MIXED)
```

### Bilateral Truth Values
```python
from wkrq import BilateralTruthValue, TRUE, FALSE, UNDEFINED

# Four information states
btv_true = BilateralTruthValue(positive=TRUE, negative=FALSE)   # True
btv_false = BilateralTruthValue(positive=FALSE, negative=TRUE)  # False
btv_gap = BilateralTruthValue(positive=FALSE, negative=FALSE)   # Gap
btv_glut = BilateralTruthValue(positive=TRUE, negative=TRUE)     # Glut
```

## Models and Results

### TableauResult
```python
result = tableau.construct()

print(f"Satisfiable: {result.satisfiable}")
print(f"Valid: {result.valid}")  # True if NOT satisfiable
print(f"Models: {len(result.models)}")
print(f"Open branches: {result.open_branches}")
print(f"Closed branches: {result.closed_branches}")
print(f"Total nodes: {result.total_nodes}")

# Access tableau tree
if result.tableau:
    for node_id, node in result.tableau.nodes.items():
        print(f"Node {node_id}: {node.formula}")
```

### Model
```python
for model in result.models:
    # Valuations: atom -> TruthValue
    for atom, value in model.valuations.items():
        print(f"{atom} = {value}")
    
    # Constants (for first-order models)
    for const, formulas in model.constants.items():
        print(f"{const}: {formulas}")
```

## Complete Example

```python
from wkrq import (
    parse, solve, valid, entails,
    ACrQTableau, parse_acrq_formula,
    SignedFormula, t, f,
    BilateralTruthValue, TRUE, FALSE
)

# Basic wKrQ  
# Note: In weak Kleene logic, no formulas are tautologies!
# Everything can be undefined when inputs are undefined
formula = parse("p & ~p")  # Contradiction
print(f"Can be true: {solve(formula, t).satisfiable}")  # False
print(f"Can be false: {solve(formula, f).satisfiable}")  # True

# ACrQ with LLM
def my_llm(formula):
    # Your LLM logic here
    return BilateralTruthValue(positive=TRUE, negative=FALSE)

formula = parse_acrq_formula("[∀x Human(x)]Mortal(x)")
tableau = ACrQTableau([SignedFormula(t, formula)], llm_evaluator=my_llm)
result = tableau.construct()

print(f"Satisfiable: {result.satisfiable}")
for model in result.models:
    print(f"Model: {model}")
```