# wKrQ API Reference: Python Implementation of a Semantic Tableau Calculus

**Version**: 1.1.2  
**Last Updated**: August 2025  
**License**: MIT  

## Table of Contents

1. [Overview](#overview)
2. [Installation & Import](#installation--import)
3. [Core Classes](#core-classes)
4. [Formula Construction](#formula-construction)
5. [Tableau Operations](#tableau-operations)
6. [Semantic Operations](#semantic-operations)
7. [First-Order Logic](#first-order-logic)
8. [ACrQ Paraconsistent Reasoning](#acrq-paraconsistent-reasoning)
9. [Advanced Features](#advanced-features)
10. [Error Handling](#error-handling)
11. [Performance Considerations](#performance-considerations)
12. [Complete Examples](#complete-examples)

## Overview

The wKrQ API provides programmatic access to an implementation of a semantic tableau calculus for three-valued weak Kleene logic with restricted quantification. The API is designed for both research applications and industrial automated reasoning systems.

### Key Features

- **Three-valued semantics**: Handles true (t), false (f), and undefined (e) truth values
- **Weak Kleene logic**: Any operation with undefined input produces undefined output
- **Restricted quantification**: First-order logic with domain-restricted quantifiers
- **Industrial performance**: Sub-millisecond tableau construction with optimization
- **Rich result objects**: Detailed information about satisfiability, models, and proofs
- **Type safety**: Full type hints for development environments

### Quick Example

```python
from wkrq import formula, solve, t, f, m, n

# Create formulas
p = Formula.atom("p")
q = Formula.atom("q")
formula = p & (q | ~p)

# Test satisfiability
result = solve(formula, t)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")
```text

## Installation & Import

### Basic Import

```python
# Core functionality
from wkrq import formula, solve, valid, entails

# Tableau signs
from wkrq import t, f, e, m, n

# Semantic values
from wkrq.semantics import TRUE, FALSE, UNDEFINED

# Parser functionality
from wkrq import parse, parse_inference, check_inference

# Advanced classes
from wkrq.tableau import Tableau, TableauResult
from wkrq.signs import SignedFormula
```text

### Comprehensive Import

```python
import wkrq
from wkrq import (
    # Core classes
    Formula, Variable, Constant, PredicateFormula,
    RestrictedExistentialFormula, RestrictedUniversalFormula,
    
    # Operations
    solve, valid, entails, parse,
    
    # Signs and semantics
    t, f, m, n, TRUE, FALSE, UNDEFINED,
    
    # Advanced
    Tableau, TableauResult, Model
)
```text

## Core Classes

### Formula

The base class for all logical formulas in wKrQ.

```python
class Formula:
    """Base class for all wKrQ formulas."""
    
    # Abstract methods (implemented by subclasses)
    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def get_atoms(self) -> Set[str]: ...  # Returns only ground atoms (no variables)
    def substitute(self, mapping: Dict[str, 'Formula']) -> 'Formula': ...
    def is_atomic(self) -> bool: ...
    
    # Operator overloading
    def __and__(self, other: 'Formula') -> 'Formula': ...  # p & q
    def __or__(self, other: 'Formula') -> 'Formula': ...   # p | q
    def __invert__(self) -> 'Formula': ...                 # ~p
    def implies(self, other: 'Formula') -> 'Formula': ...  # p.implies(q)
    
    # Utility methods
    def complexity(self) -> int: ...
    def substitute_term(self, mapping: Dict[str, 'Term']) -> 'Formula': ...
```text

#### Static Constructors

```python
# Propositional atoms
p = Formula.atom("p")
p, q, r = Formula.atoms("p", "q", "r")

# First-order terms
x = Formula.variable("X")
a = Formula.constant("a")

# Predicates
human_x = Formula.predicate("Human", [x])
loves_ab = Formula.predicate("Loves", [a, Formula.constant("b")])

# Restricted quantifiers
exists_formula = Formula.restricted_exists(x, student_x, human_x)
forall_formula = Formula.restricted_forall(x, human_x, mortal_x)
```text

### TableauResult

Result object returned by tableau operations.

```python
@dataclass
class TableauResult:
    """Result of tableau construction."""
    
    satisfiable: bool              # Whether formula is satisfiable
    models: List[Model]            # All satisfying models found
    closed_branches: int           # Number of closed tableau branches
    open_branches: int             # Number of open tableau branches
    total_nodes: int               # Total nodes in tableau
    tableau: Optional[Tableau]     # Full tableau object (if requested)
    
    @property
    def valid(self) -> bool:       # True if formula is valid (no models)
        return not self.satisfiable
```text

### Model

Represents a satisfying model (interpretation) for a formula.

```python
@dataclass
class Model:
    """A model extracted from an open tableau branch."""
    
    valuations: Dict[str, TruthValue]      # Atom → truth value mappings
    constants: Dict[str, Set[Formula]]     # Constant interpretations (first-order)
    
    def __str__(self) -> str: ...
```text

### Signs

Tableau signs for proof construction in three-valued logic.

```python
# Sign objects
t  # Formula must be true (t)
f  # Formula must be false (f)
m  # Formula can be true or false (t or f)
n  # Formula must be undefined (e)

# Usage
signed_formula = SignedFormula(t, formula)
result = solve(formula, sign=t)
```text

## Formula Construction

### Propositional Logic

```python
# Basic atoms
p = Formula.atom("p")
q = Formula.atom("q")
r = Formula.atom("r")

# Multiple atoms at once
p, q, r = Formula.atoms("p", "q", "r")

# Compound formulas using operators
conjunction = p & q                    # Conjunction
disjunction = p | q                    # Disjunction
negation = ~p                          # Negation
implication = p.implies(q)             # Implication

# Complex formulas
complex_formula = (p & q) | (~p & r)
nested_formula = p.implies(q.implies(r))

# Parentheses are handled automatically
formula = p & (q | r)  # Equivalent to: p ∧ (q ∨ r)
```text

### First-Order Logic

```python
# Variables and constants
x = Formula.variable("X")
y = Formula.variable("Y")
a = Formula.constant("a")
b = Formula.constant("b")

# Predicates
human_x = Formula.predicate("Human", [x])
mortal_x = Formula.predicate("Mortal", [x])
loves_xy = Formula.predicate("Loves", [x, y])
student_a = Formula.predicate("Student", [a])

# Restricted quantifiers
# [∃X Human(X)]Mortal(X): "There exists something that is both human and mortal"
exists_human_mortal = Formula.restricted_exists(x, human_x, mortal_x)

# [∀X Human(X)]Mortal(X): "All humans are mortal"
all_humans_mortal = Formula.restricted_forall(x, human_x, mortal_x)

# Complex first-order formulas
complex_fo = exists_human_mortal & all_humans_mortal & student_a
```text

### Formula Properties

```python
formula = (p & q) | (~p & r)

# Basic properties
print(formula.is_atomic())        # False
print(formula.get_atoms())        # {"p", "q", "r"}
print(formula.complexity())       # 4 (number of connectives)

# String representation
print(str(formula))               # "(p & q) | (~p & r)"
print(repr(formula))              # CompoundFormula("|", [...])

# Equality and hashing
formula1 = p & q
formula2 = p & q
print(formula1 == formula2)       # True
print(hash(formula1))             # Hashable for use in sets/dicts
```text

## Tableau Operations

### Basic Satisfiability

```python
from wkrq import solve, t, f, m, n

formula = p & (q | ~q)

# Test with different signs
result_t = solve(formula, t)      # Must be true
result_f = solve(formula, f)      # Must be false
result_m = solve(formula, m)      # Can be true or false
result_n = solve(formula, n)      # Must be undefined

print(f"t: {result_t.satisfiable}")
print(f"f: {result_f.satisfiable}")
print(f"m: {result_m.satisfiable}")
print(f"n: {result_n.satisfiable}")
```text

### Detailed Results

```python
formula = p | q
result = solve(formula, t)

print(f"Satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")
print(f"Tableau nodes: {result.total_nodes}")
print(f"Open branches: {result.open_branches}")
print(f"Closed branches: {result.closed_branches}")

# Access individual models
for i, model in enumerate(result.models, 1):
    print(f"Model {i}: {model}")
    
    # Access specific atom valuations
    p_value = model.valuations.get("p", UNDEFINED)
    q_value = model.valuations.get("q", UNDEFINED)
    print(f"  p = {p_value}, q = {q_value}")
```text

### Validity and Entailment

```python
# Test validity (true in all models)
tautology = p | ~p
is_valid = valid(tautology)
print(f"p | ~p is valid: {is_valid}")

# Test entailment
premises = [p, p.implies(q)]
conclusion = q
is_entailed = entails(premises, conclusion)
print(f"Modus ponens valid: {is_entailed}")

# Complex entailment
premises = [
    p.implies(q),
    q.implies(r),
    r.implies(s),
    p
]
conclusion = s
print(f"Chain entailment: {entails(premises, conclusion)}")
```text

### Advanced Tableau Construction

```python
from wkrq.tableau import Tableau
from wkrq.signs import SignedFormula

# Manual tableau construction
signed_formulas = [SignedFormula(t, p & ~p)]
tableau = Tableau(signed_formulas)
result = tableau.construct()

# Access tableau structure
print(f"Root node: {tableau.root}")
print(f"All nodes: {len(tableau.nodes)}")
print(f"Branches: {len(tableau.branches)}")

# Examine individual branches
for i, branch in enumerate(tableau.branches):
    print(f"Branch {i}: {'CLOSED' if branch.is_closed else 'OPEN'}")
    if branch.is_closed:
        print(f"  Closure reason: {branch.closure_reason}")
```text

## Semantic Operations

### Three-Valued Truth Functions

```python
from wkrq.semantics import WeakKleeneSemantics, TRUE, FALSE, UNDEFINED

semantics = WeakKleeneSemantics()

# Test conjunction
result = semantics.conjunction(TRUE, UNDEFINED)
print(f"t ∧ e = {result}")  # Output: e (undefined)

# Test disjunction  
result = semantics.disjunction(TRUE, UNDEFINED)
print(f"t ∨ e = {result}")  # Output: e (undefined in weak Kleene)

# Test negation
result = semantics.negation(UNDEFINED)
print(f"¬e = {result}")     # Output: e (undefined)

# Test implication
result = semantics.implication(UNDEFINED, TRUE)
print(f"e → t = {result}")  # Output: e (undefined)
```text

### Truth Value Properties

```python
# Truth value objects
print(f"TRUE: {TRUE}")           # t
print(f"FALSE: {FALSE}")         # f  
print(f"UNDEFINED: {UNDEFINED}") # e

# Semantic properties
print(f"Designated values: {semantics.designated_values}")  # {TRUE}
print(f"All truth values: {semantics.truth_values}")        # {TRUE, FALSE, UNDEFINED}

# Test designation
print(f"TRUE is designated: {semantics.is_designated(TRUE)}")      # True
print(f"FALSE is designated: {semantics.is_designated(FALSE)}")    # False
print(f"UNDEFINED is designated: {semantics.is_designated(UNDEFINED)}") # False
```text

### Model Evaluation

```python
# Evaluate formulas in specific models
formula = p & (q | r)

# Create model
model_valuations = {"p": TRUE, "q": FALSE, "r": TRUE}

# Manual evaluation (conceptual - actual evaluation would use tableau)
result = solve(formula, t)
for model in result.models:
    p_val = model.valuations["p"]
    q_val = model.valuations["q"] 
    r_val = model.valuations.get("r", UNDEFINED)
    print(f"Model: p={p_val}, q={q_val}, r={r_val}")
```text

## First-Order Logic

### Terms and Predicates

```python
# Terms
x = Formula.variable("X")
y = Formula.variable("Y")
alice = Formula.constant("alice")
bob = Formula.constant("bob")

# Predicates with different arities
student_x = Formula.predicate("Student", [x])           # Unary
loves_xy = Formula.predicate("Loves", [x, y])           # Binary
between_xyz = Formula.predicate("Between", [x, y, Formula.constant("c")])  # Ternary

# Complex predicate formulas
formula = student_x & loves_xy.substitute_term({"Y": alice})
print(f"Formula: {formula}")
```text

### Term Substitution

```python
# Original formula with variables
formula = Formula.predicate("Loves", [x, y])
print(f"Original: {formula}")  # Loves(X, Y)

# Substitute variables with constants
substitution = {"X": alice, "Y": bob}
substituted = formula.substitute_term(substitution)
print(f"Substituted: {substituted}")  # Loves(alice, bob)

# Partial substitution
partial_substitution = {"X": alice}
partial = formula.substitute_term(partial_substitution)
print(f"Partial: {partial}")  # Loves(alice, Y)
```text

### Restricted Quantification

```python
# Restricted existential quantification
x = Formula.variable("X")
student_x = Formula.predicate("Student", [x])
human_x = Formula.predicate("Human", [x])

# [∃X Student(X)]Human(X): "There exists something that is both a student and human"
exists_student_human = Formula.restricted_exists(x, student_x, human_x)

# Test satisfiability
result = solve(exists_student_human, t)
print(f"Exists student-human: {result.satisfiable}")

# Restricted universal quantification  
mortal_x = Formula.predicate("Mortal", [x])

# [∀X Human(X)]Mortal(X): "All humans are mortal"
all_humans_mortal = Formula.restricted_forall(x, human_x, mortal_x)

# Test satisfiability
result = solve(all_humans_mortal, t)
print(f"All humans mortal: {result.satisfiable}")

# Complex first-order reasoning
alice_student = Formula.predicate("Student", [Formula.constant("alice")])
complex_reasoning = exists_student_human & all_humans_mortal & alice_student

result = solve(complex_reasoning, t)
print(f"Complex reasoning: {result.satisfiable}")
print(f"Models: {len(result.models)}")
```text

### First-Order Model Extraction

```python
# First-order formulas create models with constant interpretations
x = Formula.variable("X")
a = Formula.constant("a")
b = Formula.constant("b")

human_x = Formula.predicate("Human", [x])
loves_ab = Formula.predicate("Loves", [a, b])

formula = Formula.restricted_exists(x, human_x, human_x) & loves_ab
result = solve(formula, t)

for model in result.models:
    print(f"Valuations: {model.valuations}")
    print(f"Constants: {model.constants}")
```

## ACrQ Paraconsistent Reasoning

ACrQ (Analytic Containment with restricted Quantification) extends wKrQ with bilateral predicates for handling contradictory and incomplete information. The API provides seamless integration with paraconsistent and paracomplete reasoning capabilities.

### Importing ACrQ Components

```python
from wkrq import (
    parse_acrq_formula, 
    SyntaxMode, 
    BilateralPredicateFormula, 
    BilateralTruthValue,
    solve, t, f, m, n
)
```

### Basic ACrQ Formula Construction

```python
# Transparent mode: Standard syntax with automatic translation
contradiction = parse_acrq_formula("Human(socrates) & ~Human(socrates)")
print(f"Paraconsistent formula: {contradiction}")
# Output: Human(socrates) & Human*(socrates)

# Test paraconsistent satisfiability
result = solve(contradiction, t)
print(f"Contradiction satisfiable: {result.satisfiable}")  # True!

# Bilateral mode: Explicit R/R* syntax
bilateral_formula = parse_acrq_formula(
    "Human(x) & Human*(x)", 
    SyntaxMode.BILATERAL
)

# Mixed mode: Both syntaxes allowed
mixed_formula = parse_acrq_formula(
    "Human(a) & Robot*(b) & ~Alien(c)", 
    SyntaxMode.MIXED
)
```

### Working with Bilateral Predicates

```python
# Direct bilateral predicate construction
from wkrq import Variable, Constant

x = Variable("x")
socrates = Constant("socrates")

# Positive bilateral predicate: Human(socrates)
human_pos = BilateralPredicateFormula(
    positive_name="Human",
    terms=[socrates],
    is_negative=False
)

# Negative bilateral predicate: Human*(socrates)  
human_neg = BilateralPredicateFormula(
    positive_name="Human", 
    terms=[socrates],
    is_negative=True
)

# Create knowledge glut (conflicting information)
glut = human_pos & human_neg
result = solve(glut, t)
print(f"Glut satisfiable: {result.satisfiable}")  # True (paraconsistent)
```

### Information States and Bilateral Truth Values

```python
# Working with bilateral truth values
from wkrq.semantics import TRUE, FALSE, UNDEFINED

# Four information states
btv_true = BilateralTruthValue(positive=TRUE, negative=FALSE)   # True
btv_false = BilateralTruthValue(positive=FALSE, negative=TRUE)  # False  
btv_gap = BilateralTruthValue(positive=FALSE, negative=FALSE)   # Gap (no info)
# Note: glut (TRUE, TRUE) would raise ValueError - handled by tableau

print(f"Gap state: {btv_gap.to_simple_value()}")     # "undefined (gap)"
print(f"Is gap: {btv_gap.is_gap()}")                 # True
print(f"Is determinate: {btv_false.is_determinate()}")  # True
```

### Paraconsistent Reasoning Examples

```python
# Explosion principle doesn't hold (paraconsistency)
premises = [
    parse_acrq_formula("P(a)"),      # P(a) is true
    parse_acrq_formula("~P(a)")      # P(a) is false (becomes P*(a))
]

arbitrary_conclusion = parse_acrq_formula("Q(b)")

# In classical logic: contradiction entails everything
# In ACrQ: contradictions don't entail arbitrary conclusions
result = entails(premises, arbitrary_conclusion)
print(f"Explosion prevented: {not result}")  # True

# But valid inferences still work
valid_conclusion = parse_acrq_formula("P(a) | R(c)")
result = entails(premises, valid_conclusion)
print(f"Valid inference: {result}")  # True
```

### Paracomplete Reasoning Examples

```python
# Handling incomplete information (gaps)
incomplete_formula = parse_acrq_formula("Human(unknown_person)")

# Check if it can be undefined (gap)
result = solve(incomplete_formula, n)
print(f"Can be undefined: {result.satisfiable}")  # True

# Law of excluded middle may not hold for incomplete info
lem = parse_acrq_formula("Human(x) | ~Human(x)")
result = solve(lem, f)  # Can it be false?
print(f"LEM can be false: {result.satisfiable}")  # True (paracomplete)
```

### Advanced ACrQ Operations

```python
# Complex paraconsistent formulas
complex_acrq = parse_acrq_formula(
    "(Human(a) & ~Human(a)) -> (Mortal(a) | ~Mortal(a))"
)

# Restricted quantification with bilateral predicates
quantified_acrq = parse_acrq_formula(
    "[∀X Human(X)]Mortal(X) & Human(socrates) & ~Human(socrates)"
)

# Mixed classical and paraconsistent reasoning  
mixed_reasoning = parse_acrq_formula(
    "Classical(p) & ~Classical(p) & (Paraconsistent(q) | Normal(r))"
)

for formula in [complex_acrq, quantified_acrq, mixed_reasoning]:
    result = solve(formula, t)
    print(f"Formula satisfiable: {result.satisfiable}")
```

### Error Handling in ACrQ

```python
from wkrq.parser import ParseError

try:
    # This fails in BILATERAL mode (¬ not allowed)
    formula = parse_acrq_formula("~Human(x)", SyntaxMode.BILATERAL)
except ParseError as e:
    print(f"Expected error: {e}")
    # Suggests using Human*(x) instead

try:
    # This fails in TRANSPARENT mode (* not allowed)  
    formula = parse_acrq_formula("Human*(x)", SyntaxMode.TRANSPARENT)
except ParseError as e:
    print(f"Expected error: {e}")
    # Suggests using ~Human(x) instead
```

## Advanced Features

### Parsing

```python
from wkrq import parse, parse_inference, check_inference

# Parse formulas from strings
formula = parse("(p & q) -> (r | s)")
print(f"Parsed: {formula}")

# Parse complex formulas
complex_formula = parse("P(x) & [∃Y Student(Y)]Human(Y)")
print(f"Complex: {complex_formula}")

# Parse inferences
inference = parse_inference("p, p -> q |- q")
print(f"Premises: {inference.premises}")
print(f"Conclusion: {inference.conclusion}")

# Check inference validity
result = check_inference(inference)
print(f"Valid: {result.valid}")
print(f"Countermodels: {len(result.countermodels)}")
```text

### Performance Optimization

```python
# Access optimization settings
from wkrq.tableau import Tableau

# Create tableau with custom settings
tableau = Tableau([SignedFormula(t, formula)])
tableau.max_branching_factor = 500      # Limit branching
tableau.max_tableau_depth = 50         # Limit depth
tableau.early_termination = True       # Stop on first model

result = tableau.construct()

# Performance statistics
print(f"Nodes created: {result.total_nodes}")
print(f"Branches: {result.open_branches + result.closed_branches}")
```text

### Custom Formula Construction

```python
from wkrq.formula import CompoundFormula, PropositionalAtom

# Manual formula construction (advanced)
atom_p = PropositionalAtom("p")
atom_q = PropositionalAtom("q")
conjunction = CompoundFormula("&", [atom_p, atom_q])

print(f"Manual construction: {conjunction}")

# Equivalent to: p & q
automatic = Formula.atom("p") & Formula.atom("q")
print(f"Automatic construction: {automatic}")
print(f"Equal: {conjunction == automatic}")
```text

## Error Handling

### Parse Errors

```python
from wkrq.parser import ParseError

try:
    formula = parse("p &")  # Incomplete formula
except ParseError as e:
    print(f"Parse error: {e}")
    print(f"Position: {e.position}")

# Safe parsing with error handling
def safe_parse(formula_str):
    try:
        return parse(formula_str)
    except ParseError as e:
        print(f"Failed to parse '{formula_str}': {e}")
        return None
```text

### Runtime Errors

```python
# Handle tableau construction errors
try:
    result = solve(very_complex_formula, t)
except Exception as e:
    print(f"Tableau construction failed: {e}")
    
# Timeout handling (conceptual - actual implementation may vary)
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Tableau construction timed out")

# Set timeout for complex formulas
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 second timeout

try:
    result = solve(complex_formula, t)
    signal.alarm(0)  # Cancel timeout
except TimeoutError:
    print("Formula too complex, timed out")
```text

### Validation

```python
# Validate formula structure
def validate_formula(formula):
    """Validate that formula is well-formed."""
    try:
        atoms = formula.get_atoms()
        complexity = formula.complexity()
        is_atomic = formula.is_atomic()
        
        # Basic validation checks
        if complexity < 0:
            raise ValueError("Invalid complexity")
        if not atoms and not is_atomic:
            raise ValueError("Non-atomic formula with no atoms")
            
        return True
    except Exception as e:
        print(f"Formula validation failed: {e}")
        return False

# Example usage
formula = p & (q | r)
is_valid = validate_formula(formula)
print(f"Formula valid: {is_valid}")
```text

## Performance Considerations

### Optimization Guidelines

```python
# Efficient formula construction
# Good: Build incrementally
atoms = Formula.atoms("p", "q", "r", "s")
formula = atoms[0]
for atom in atoms[1:]:
    formula = formula & atom

# Less efficient: Deep nesting
# Avoid: deeply_nested = p & (q & (r & (s & ...)))

# Efficient tableau operations
# Use early termination for satisfiability testing
result = solve(formula, t)  # Stops at first model

# For model enumeration, be aware of complexity
result = solve(formula, t)
if len(result.models) > 100:
    print("Warning: Many models found, consider simplifying formula")
```text

### Memory Management

```python
# For large formulas, avoid storing unnecessary data
def efficient_satisfiability_test(formula):
    """Test satisfiability without storing tableau."""
    result = solve(formula, t)
    return result.satisfiable  # Don't store models or tableau

# Batch processing
formulas = [parse(f"p{i} & q{i}") for i in range(100)]

results = []
for formula in formulas:
    result = solve(formula, t)
    results.append(result.satisfiable)  # Store only what you need
    # Don't store the full result object if not needed
```text

### Performance Monitoring

```python
import time

def benchmark_formula(formula, iterations=10):
    """Benchmark formula solving performance."""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        result = solve(formula, t)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    return {
        'average_time': avg_time,
        'min_time': min(times),
        'max_time': max(times),
        'satisfiable': result.satisfiable,
        'nodes': result.total_nodes
    }

# Example usage
formula = (p & q) | (r & s)
stats = benchmark_formula(formula)
print(f"Average time: {stats['average_time']:.3f}s")
print(f"Nodes created: {stats['nodes']}")
```text

## Complete Examples

### Example 1: Basic Propositional Reasoning

```python
from wkrq import formula, solve, valid, entails, t, f, m, n

# Create formulas
p, q, r = Formula.atoms("p", "q", "r")

# Test De Morgan's law: ¬(p ∧ q) ↔ (¬p ∨ ¬q)
left_side = ~(p & q)
right_side = ~p | ~q
biconditional = (left_side.implies(right_side)) & (right_side.implies(left_side))

# Check if it's a tautology
is_tautology = valid(biconditional)
print(f"De Morgan's law is valid: {is_tautology}")

# Find models to understand the truth conditions
result = solve(biconditional, t)
print(f"Models for De Morgan's law: {len(result.models)}")
for model in result.models:
    print(f"  {model}")
```text

### Example 2: Three-Valued Logic Exploration

```python
from wkrq import formula, solve, t, f, m, n
from wkrq.semantics import WeakKleeneSemantics, TRUE, FALSE, UNDEFINED

# Explore weak Kleene semantics
p = Formula.atom("WeatherStatus")
semantics = WeakKleeneSemantics()

print("Testing formula 'WeatherStatus' with all signs:")
for sign, description in [(t, "true"), (f, "false"), (m, "true or false"), (n, "undefined")]:
    result = solve(p, sign)
    print(f"  Sign {sign} ({description}): satisfiable = {result.satisfiable}")
    
    if result.satisfiable and result.models:
        model = result.models[0]
        value = model.valuations.get("WeatherStatus", UNDEFINED)
        print(f"    Model assigns: WeatherStatus = {value}")

# Test conjunction with undefined
print("\nTesting conjunction with undefined values:")
q = Formula.atom("OtherFactor")
conjunction = p & q

# Can the conjunction be undefined?
result = solve(conjunction, n)
print(f"Can 'p & q' be undefined? {result.satisfiable}")

# Test weak Kleene property: any undefined input → undefined output
print("\nWeak Kleene property demonstration:")
print(f"TRUE ∧ UNDEFINED = {semantics.conjunction(TRUE, UNDEFINED)}")
print(f"TRUE ∨ UNDEFINED = {semantics.disjunction(TRUE, UNDEFINED)}")
print(f"¬UNDEFINED = {semantics.negation(UNDEFINED)}")
```text

### Example 3: First-Order Reasoning

```python
from wkrq import formula, solve, entails, t

# Set up first-order reasoning scenario
x = Formula.variable("X")
alice = Formula.constant("alice")
bob = Formula.constant("bob")

# Predicates
human = Formula.predicate("Human", [x])
mortal = Formula.predicate("Mortal", [x]) 
student = Formula.predicate("Student", [x])

# Facts about individuals
human_alice = Formula.predicate("Human", [alice])
student_alice = Formula.predicate("Student", [alice])
human_bob = Formula.predicate("Human", [bob])

# Universal principle: All humans are mortal
all_humans_mortal = Formula.restricted_forall(x, human, mortal)

# Existential claim: There exists a human student
exists_human_student = Formula.restricted_exists(x, student, human)

# Combine premises
premises = [
    all_humans_mortal,
    human_alice,
    student_alice,
    human_bob
]

# Test entailment: Do the premises entail that Alice is mortal?
mortal_alice = Formula.predicate("Mortal", [alice])
alice_mortal_entailed = entails(premises, mortal_alice)
print(f"Premises entail 'Alice is mortal': {alice_mortal_entailed}")

# Test satisfiability of the existential claim
result = solve(exists_human_student, t)
print(f"'There exists a human student' is satisfiable: {result.satisfiable}")

# Complex reasoning: Combine all premises
all_premises = premises[0]
for premise in premises[1:]:
    all_premises = all_premises & premise

all_premises = all_premises & exists_human_student

result = solve(all_premises, t)
print(f"All premises together are satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")
```text

### Example 4: Philosophical Logic Application

```python
from wkrq import formula, solve, t, f, n

# Sorites Paradox: Heap of sand
# Model the vagueness of "heap" predicate

heap_1000 = Formula.atom("Heap1000")  # 1000 grains clearly form a heap
heap_999 = Formula.atom("Heap999")    # 999 grains - borderline?
heap_1 = Formula.atom("Heap1")        # 1 grain clearly doesn't form a heap

print("Sorites Paradox Analysis:")

# Clear cases
print("\nClear cases:")
result = solve(heap_1000, t)
print(f"1000 grains form a heap: {result.satisfiable}")

result = solve(heap_1, f)
print(f"1 grain doesn't form a heap: {result.satisfiable}")

# Borderline case - can be undefined in three-valued logic
print("\nBorderline case:")
result = solve(heap_999, n)
print(f"999 grains can be undefined (borderline): {result.satisfiable}")

# Sorites principle: If n grains form a heap, then n-1 grains form a heap
sorites_step = heap_1000.implies(heap_999)
print(f"\nSorites step satisfiable: {solve(sorites_step, t).satisfiable}")

# The paradox: Combining clear truths with sorites principle
paradox = heap_1000 & sorites_step & ~heap_1
result = solve(paradox, t)
print(f"Full paradox satisfiable: {result.satisfiable}")

if result.satisfiable:
    print("Three-valued logic resolves the paradox by allowing borderline cases!")
    for model in result.models:
        print(f"  Model: {model}")
else:
    print("Paradox leads to contradiction even in three-valued logic.")
```text

### Example 5: Performance Analysis

```python
import time
from wkrq import formula, solve, t

def create_test_formula(size):
    """Create test formula of given complexity."""
    atoms = [Formula.atom(f"p{i}") for i in range(size)]
    
    # Create alternating conjunction and disjunction
    formula = atoms[0]
    for i, atom in enumerate(atoms[1:], 1):
        if i % 2 == 0:
            formula = formula & atom
        else:
            formula = formula | atom
    
    return formula

def performance_test():
    """Test performance with increasing formula complexity."""
    print("Performance Analysis:")
    print(f"{'Size':<6} {'Time (ms)':<12} {'Nodes':<8} {'Satisfiable':<12}")
    print("-" * 45)
    
    for size in [5, 10, 15, 20, 25]:
        formula = create_test_formula(size)
        
        start = time.time()
        result = solve(formula, t)
        end = time.time()
        
        elapsed_ms = (end - start) * 1000
        satisfiable = "Yes" if result.satisfiable else "No"
        
        print(f"{size:<6} {elapsed_ms:>8.2f}    {result.total_nodes:<8} {satisfiable:<12}")
        
        # Performance check
        if elapsed_ms > 100:  # If taking more than 100ms
            print(f"  Warning: Size {size} took {elapsed_ms:.1f}ms")

# Run performance test
performance_test()

# Memory efficiency test
def memory_test():
    """Test memory efficiency by checking model count."""
    sizes = [3, 4, 5, 6]
    
    print("\nMemory Efficiency Test:")
    print(f"{'Size':<6} {'Models':<8} {'Branches':<10}")
    print("-" * 30)
    
    for size in sizes:
        # Create formula that can have many models
        atoms = [Formula.atom(f"q{i}") for i in range(size)]
        formula = atoms[0]
        for atom in atoms[1:]:
            formula = formula | atom  # Disjunction creates multiple models
        
        result = solve(formula, t)
        total_branches = result.open_branches + result.closed_branches
        
        print(f"{size:<6} {len(result.models):<8} {total_branches:<10}")

memory_test()
```text

---

This API reference provides comprehensive documentation for the wKrQ system. For command-line usage, see the CLI Guide. For implementation details, see the Architecture documentation.
