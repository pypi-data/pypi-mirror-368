# ACrQ Bilateral Predicate Example: Understanding the System

This document provides a concrete example demonstrating how ACrQ (Analytic Containment with restricted Quantification) works, focusing on the bilateral predicate system and its relationship to weak Kleene semantics.

## Overview: Three Layers of ACrQ

ACrQ combines three key concepts:

1. **Syntactic Layer**: Bilateral predicates (R and R*) for independent tracking
2. **Semantic Layer**: Weak Kleene three-valued logic (true, false, undefined)
3. **Information Layer**: Four possible states (determinate true/false, gap, glut)

## Concrete Example: The Robot Classification System

Let's model a robot classification system where robots can be classified as "Human-like" or not. This example will show how ACrQ handles incomplete and conflicting information better than standard wKrQ.

### Scenario Setup

We have three robots:
- **Alice**: Clearly human-like (walks, talks, has emotions)
- **Bob**: Clearly not human-like (industrial arm, no speech)
- **Charlie**: Ambiguous case (some human features, some not)

### 1. Standard wKrQ Representation

In standard wKrQ, we would represent this with a single predicate:

```python
# Standard wKrQ formulas
Human(alice)    # true
¬Human(bob)     # true (meaning Human(bob) is false)
Human(charlie)  # undefined (we're uncertain)
```

**Limitation**: wKrQ cannot distinguish between:
- "We don't know if Charlie is human-like" (knowledge gap)
- "Charlie has both human-like and non-human-like features" (knowledge glut)

### 2. ACrQ Bilateral Representation

In ACrQ, we have two independent predicates:
- `Human(x)`: Evidence that x IS human-like
- `Human*(x)`: Evidence that x IS NOT human-like

```python
# ACrQ bilateral predicates
# Alice: Clearly human-like
Human(alice) = true      # Positive evidence
Human*(alice) = false    # No negative evidence

# Bob: Clearly not human-like
Human(bob) = false       # No positive evidence
Human*(bob) = true       # Negative evidence

# Charlie Case 1: Knowledge Gap (no information)
Human(charlie) = false   # No positive evidence
Human*(charlie) = false  # No negative evidence

# Charlie Case 2: Knowledge Glut (conflicting information)
Human(charlie) = true    # Has human-like features
Human*(charlie) = true   # Also has non-human-like features
```

### 3. Internal Representation

Here's how ACrQ represents these internally:

```python
from wkrq.formula import BilateralPredicateFormula, Constant
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE

# Create bilateral predicate instances
alice_human = BilateralPredicateFormula(
    positive_name="Human",
    terms=[Constant("alice")],
    is_negative=False  # This represents Human(alice)
)

alice_human_star = BilateralPredicateFormula(
    positive_name="Human",
    terms=[Constant("alice")],
    is_negative=True   # This represents Human*(alice)
)

# Bilateral truth values for each robot
alice_btv = BilateralTruthValue(positive=TRUE, negative=FALSE)   # Determinate true
bob_btv = BilateralTruthValue(positive=FALSE, negative=TRUE)     # Determinate false
charlie_gap_btv = BilateralTruthValue(positive=FALSE, negative=FALSE)  # Gap
charlie_glut_btv = BilateralTruthValue(positive=TRUE, negative=TRUE)   # Glut

# User-friendly representations
print(alice_btv.to_simple_value())        # "true"
print(bob_btv.to_simple_value())          # "false"
print(charlie_gap_btv.to_simple_value())  # "undefined (gap)"
print(charlie_glut_btv.to_simple_value()) # "both (glut)"
```

### 4. Semantic Evaluation Under Weak Kleene

ACrQ still uses weak Kleene semantics for logical operations. The key is how bilateral predicates interact with these semantics:

```python
# Example: "Charlie is human-like AND Charlie is not human-like"
# In standard logic, this would be a contradiction (always false)

# In wKrQ (if Charlie's status is undefined):
Human(charlie) ∧ ¬Human(charlie) = undefined ∧ undefined = undefined

# In ACrQ with a knowledge glut:
Human(charlie) ∧ Human*(charlie) = true ∧ true = true
# This correctly models that Charlie has both properties!

# In ACrQ with a knowledge gap:
Human(charlie) ∧ Human*(charlie) = false ∧ false = false
# This correctly models that we have no evidence either way
```

### 5. Translation from User Formulas

ACrQ can transparently translate standard formulas:

```python
# User writes (in transparent mode):
formula = "Human(alice) ∧ ¬Human(bob) ∧ ¬Human(charlie)"

# ACrQ internally translates to:
# Human(alice) ∧ Human*(bob) ∧ Human*(charlie)

# This is evaluated based on the bilateral truth values:
# - Human(alice) = true (from alice_btv.positive)
# - Human*(bob) = true (from bob_btv.negative)
# - Human*(charlie) depends on charlie's state:
#   - If gap: false (no negative evidence)
#   - If glut: true (has negative evidence)
```

### 6. Practical Benefits

#### Handling Conflicting Information (Paraconsistent)

```python
# Knowledge base with conflict
kb = [
    "Human(charlie)",      # Source A says Charlie is human-like
    "¬Human(charlie)"      # Source B says Charlie is not human-like
]

# In standard logic: EXPLOSION! Everything becomes provable
# In wKrQ: System might fail or give undefined for everything
# In ACrQ: Handled gracefully as a knowledge glut

# ACrQ can still make valid inferences:
# From kb, we CANNOT infer "Robot(alice)" (no explosion)
# But we CAN infer "Human(charlie) ∨ Human*(charlie)" (trivially true)
```

#### Handling Missing Information (Paracomplete)

```python
# Query: "Is every robot either human-like or not human-like?"
# Classical logic: ∀x(Human(x) ∨ ¬Human(x)) = TRUE (law of excluded middle)

# ACrQ perspective:
# For alice: Human(alice) ∨ Human*(alice) = true ∨ false = true ✓
# For bob: Human(bob) ∨ Human*(bob) = false ∨ true = true ✓
# For charlie (gap): Human(charlie) ∨ Human*(charlie) = false ∨ false = false ✗

# ACrQ correctly identifies that excluded middle fails for entities with gaps
```

### 7. Tableau Reasoning Example

Here's how ACrQ's tableau system would handle a query:

```python
# Query: "If Charlie has human features, is Charlie human-like?"
# Premise: HasHumanFeatures(charlie)
# Query: Human(charlie)?

# Tableau construction:
1. t: HasHumanFeatures(charlie)     [premise]
2. f: Human(charlie)                 [negated conclusion]

# The tableau cannot close without additional information
# This correctly models that having human features doesn't 
# determine Human/Human* status in ACrQ

# But if we add a rule:
3. t: HasHumanFeatures(x) → Human(x)  [domain knowledge]

# Now the tableau closes, proving the inference
```

## Key Distinctions from wKrQ

1. **Richer Information States**: ACrQ distinguishes gaps from gluts
2. **Paraconsistent Behavior**: Contradictions don't cause explosion
3. **Independent Evidence Tracking**: R and R* are tracked separately
4. **Transparent Usage**: Users can write familiar syntax while getting bilateral benefits
5. **Practical Modeling**: Better represents real-world scenarios with conflicting sources

## Summary

ACrQ extends wKrQ by:
- **Syntactically**: Adding bilateral predicates (R/R*) for independent tracking
- **Semantically**: Still using weak Kleene three-valued logic for operations
- **Pragmatically**: Enabling paraconsistent and paracomplete reasoning

The bilateral predicate system is not just a syntactic trick—it fundamentally changes how the system handles information, making it more robust for real-world applications where knowledge is often incomplete or conflicting.