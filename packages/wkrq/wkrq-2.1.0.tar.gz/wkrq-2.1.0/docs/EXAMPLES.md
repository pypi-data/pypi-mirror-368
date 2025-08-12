# wKrQ Examples

## Basic Propositional Logic

### Satisfiability Testing
```python
from wkrq import parse, solve

# Contradiction (unsatisfiable)
result = solve(parse("p & ~p"))
assert not result.satisfiable

# Tautology
result = solve(parse("p | ~p"))
assert result.satisfiable
assert len(result.models) == 3  # t, f, e for p

# Contingent formula
result = solve(parse("p -> q"))
assert result.satisfiable

# With construction tracing
result = solve(parse("p & ~p"), trace=True)
result.print_trace()  # Shows step-by-step construction
```

### Validity Checking
```python
from wkrq import valid, parse

# Classical tautologies (not all hold in weak Kleene)
# p -> p is NOT valid in weak Kleene (undefined when p is undefined)
assert not valid(parse("p -> p"))  # Can be undefined!

# Not valid in weak Kleene
assert not valid(parse("p | ~p"))  # Can be undefined
```

### Inference Testing
```python
from wkrq import entails, parse

# Valid inferences
p = parse("p")
p_implies_q = parse("p -> q")
q = parse("q")

assert entails([p, p_implies_q], q)  # Modus ponens
assert entails([parse("p | q"), parse("~p")], q)  # Disjunctive syllogism

# Invalid inference
assert not entails([p], q)  # p doesn't entail q
```

## First-Order Logic

### Restricted Quantifiers
```python
from wkrq import parse, solve

# Universal quantifier: [∀x P(x)]Q(x) means "for all x, if P(x) then Q(x)"
formula = parse("[∀x Human(x)]Mortal(x)")
result = solve(formula)

# Existential quantifier: [∃x P(x)]Q(x) means "there exists x such that P(x) and Q(x)"
formula = parse("[∃x Student(x)]Smart(x)")
result = solve(formula)
```

### Quantified Inference
```python
from wkrq import parse_inference, check_inference

# Valid: Universal instantiation
inference = parse_inference("[∀x Human(x)]Mortal(x), Human(socrates) |- Mortal(socrates)")
result = check_inference(inference)
assert result.valid

# Invalid: Existential to universal
inference = parse_inference("[∃x P(x)]Q(x) |- [∀x P(x)]Q(x)")
result = check_inference(inference)
assert not result.valid
```

## ACrQ Paraconsistent Logic

### Bilateral Predicates
```python
from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t

# Glut: both Human and Human* are true
formula = parse_acrq_formula("Human(alice) & ~Human(alice)")
tableau = ACrQTableau([SignedFormula(t, formula)])
result = tableau.construct()
assert result.satisfiable  # Gluts are allowed!

# In the model - valuations map to TruthValue objects
model = result.models[0]
from wkrq import TRUE
assert model.valuations["Human(alice)"] == TRUE
assert model.valuations["Human*(alice)"] == TRUE
```

### Knowledge Gaps and Gluts
```python
from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, f

# Gap: neither Robot nor Robot* is true
robot = parse_acrq_formula("Robot(alice)")
robot_star = parse_acrq_formula("Robot*(alice)")
tableau = ACrQTableau([
    SignedFormula(f, robot),
    SignedFormula(f, robot_star)
])
result = tableau.construct()
assert result.satisfiable  # Gaps are allowed
```

## LLM Integration

### Basic LLM Evaluator
```python
from wkrq import ACrQTableau, BilateralTruthValue, TRUE, FALSE, UNDEFINED

def penguin_evaluator(formula):
    """LLM that knows about penguins."""
    formula_str = str(formula)
    
    if formula_str == "Penguin(tweety)":
        return BilateralTruthValue(positive=TRUE, negative=FALSE)
    elif formula_str == "Flies(tweety)":
        # Penguins don't fly
        return BilateralTruthValue(positive=FALSE, negative=TRUE)
    elif formula_str == "Bird(tweety)":
        # Penguins are birds
        return BilateralTruthValue(positive=TRUE, negative=FALSE)
    else:
        # Unknown - return gap
        return BilateralTruthValue(positive=FALSE, negative=FALSE)
```

### Using LLM in Tableau
```python
from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t

# Create formula
formula = parse_acrq_formula("[∀x Penguin(x)]~Flies(x)")

# Create tableau with LLM
tableau = ACrQTableau(
    [SignedFormula(t, formula), SignedFormula(t, parse_acrq_formula("Penguin(tweety)"))],
    llm_evaluator=penguin_evaluator
)

result = tableau.construct()
# The LLM will be consulted for atomic formulas like Flies(tweety)
```

## Construction Tracing

### Understanding Tableau Construction
```python
from wkrq import parse, solve, check_inference

# Trace a complex inference
inference = parse_inference("p → q, q → r |- p → r")
result = check_inference(inference, trace=True)

# Shows:
# - Each rule application in sequence
# - What formulas each rule produces
# - Which branches are created
# - When and why branches close

result.tableau_result.print_trace()

# Access trace programmatically
if result.tableau_result.construction_trace:
    trace = result.tableau_result.construction_trace
    print(f"Total steps: {len(trace.rule_applications)}")
    print(f"Branches created: {trace.total_branches}")
    print(f"Branches closed: {trace.closed_branches}")
    
    # Examine specific steps
    for step in trace.rule_applications:
        if "LLM-Eval" in step.rule_name:
            print(f"LLM evaluated: {step.source_node.formula}")
            print(f"Produced: {step.produced_formulas}")
```

### Debugging with Traces
```python
# When a formula doesn't appear in the final tree
formula = parse("[∀X P(X)]Q(X) & P(a) & ~Q(a)")
result = solve(formula, trace=True)

# The trace shows ALL formulas produced by rules,
# even those not added due to branch closure
for step in result.construction_trace.rule_applications:
    if step.closures_caused:
        print(f"Step {step.step_number} caused closure")
        print(f"Formulas not added: {step.produced_formulas}")
```

## Complex Examples

### Classical Paradoxes
```python
# Liar paradox: "This sentence is false"
# Represented as: p ↔ ~p
from wkrq import parse, solve

liar = parse("(p -> ~p) & (~p -> p)")
result = solve(liar)
# In weak Kleene, this has a model where p is undefined
assert result.satisfiable
assert any(m.valuations.get("p") == UNDEFINED for m in result.models)
```

### Paraconsistent Reasoning
```python
from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t

# Contradictory information doesn't explode
premises = [
    "Bird(tweety)",           # Tweety is a bird
    "Penguin(tweety)",        # Tweety is a penguin
    "[∀x Bird(x)]Flies(x)",   # Birds fly
    "[∀x Penguin(x)]~Flies(x)" # Penguins don't fly
]

formulas = [SignedFormula(t, parse_acrq_formula(p)) for p in premises]
tableau = ACrQTableau(formulas)
result = tableau.construct()

# System remains consistent despite contradiction about Flies(tweety)
assert result.satisfiable
```

### Tableau Visualization
```python
from wkrq import parse, solve
from wkrq.cli import TableauTreeRenderer

# Solve formula
formula = parse("(p | q) & ~p")
result = solve(formula)

# Visualize tableau tree
if result.tableau:
    renderer = TableauTreeRenderer(show_rules=True)
    tree = renderer.render_unicode(result.tableau)
    print(tree)
```

Output:
```
 0. t: (p | q) & (~p)
    ├─── 1. t: p | q                [t:∧]
    │    └─── 2. t: ~p               [t:∧]
    │         └─── 3. f: p           [t:~]
    │              ├─── 4. t: p  ×   [t:∨]
    │              └─── 5. t: q      [t:∨]
```

## CLI Examples

### Basic Usage
```bash
# Test formulas
wkrq "p & ~p"                    # Contradiction
wkrq "p -> (q -> p)"            # Valid
wkrq --models "p | q"           # Show models

# Inference
wkrq "p, p -> q |- q"           # Modus ponens
wkrq --tree "p | q, ~p |- q"    # With proof tree

# ACrQ mode
wkrq --mode=acrq "Human(x) & ~Human(x)"  # Glut allowed
```

### Advanced CLI
```bash
# Different signs
wkrq --sign=f "p | q"           # Can be false?
wkrq --sign=e "p -> q"          # Can be undefined?

# Tree visualization
wkrq --tree --format=unicode --show-rules "p & (q | r)"

# JSON output for processing
wkrq --json "p -> q" | jq '.models'

# Quantifiers
wkrq "[∀x Human(x)]Mortal(x), Human(socrates) |- Mortal(socrates)"
```