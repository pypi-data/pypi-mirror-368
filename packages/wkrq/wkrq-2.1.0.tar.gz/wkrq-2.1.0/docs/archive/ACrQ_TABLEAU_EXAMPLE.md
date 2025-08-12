# ACrQ Tableau Example: How It Works

This document demonstrates how the ACrQ tableau procedure works through a concrete example, showing both the conceptual steps and CLI usage.

## Example Problem: Robot Classification with Conflicting Evidence

### Scenario
We have a robot classification system with conflicting information:
- Some sensors say robot Charlie is human-like
- Other sensors say Charlie is not human-like
- We want to check if we can still make valid inferences

### Knowledge Base
```
1. Human(charlie)     # Sensor A says Charlie is human-like
2. Human*(charlie)    # Sensor B says Charlie is NOT human-like (¬Human(charlie) in transparent mode)
3. Human(x) → Nice(x) # All human-like robots are nice
4. Human*(x) → Industrial(x) # All non-human-like robots are industrial
```

### Query
Can we infer that Charlie is either nice or industrial?
`Nice(charlie) ∨ Industrial(charlie)`

## How ACrQ Tableau Works

### Step 1: Parse Formulas with Bilateral Predicates

In ACrQ, the parser converts formulas to bilateral representation:

```python
# User input (transparent mode):
premises = [
    "Human(charlie)",
    "¬Human(charlie)",  # Converted to Human*(charlie)
    "Human(x) → Nice(x)",
    "¬Human(x) → Industrial(x)"  # Converted to Human*(x) → Industrial(x)
]
conclusion = "Nice(charlie) | Industrial(charlie)"
```

### Step 2: Tableau Construction

The tableau starts by:
1. Adding all premises with sign t (must be true)
2. Adding negated conclusion with sign t (to test for contradiction)

```
Initial tableau:
1. t: Human(charlie)                      [premise]
2. t: Human*(charlie)                     [premise] 
3. t: Human(x) → Nice(x)                  [premise]
4. t: Human*(x) → Industrial(x)           [premise]
5. t: ¬(Nice(charlie) ∨ Industrial(charlie))  [negated conclusion]
```

### Step 3: Apply Tableau Rules

Apply De Morgan's law to line 5:
```
6. t: ¬Nice(charlie) ∧ ¬Industrial(charlie)   [from 5]
7. t: ¬Nice(charlie)                           [from 6]
8. t: ¬Industrial(charlie)                     [from 6]
```

In ACrQ, these negations become:
```
7. t: Nice*(charlie)                           [¬Nice becomes Nice*]
8. t: Industrial*(charlie)                     [¬Industrial becomes Industrial*]
```

Apply universal instantiation to lines 3 and 4:
```
9. t: Human(charlie) → Nice(charlie)           [from 3, x=charlie]
10. t: Human*(charlie) → Industrial(charlie)   [from 4, x=charlie]
```

Apply implication rule to line 9:
```
Branch 1:                    Branch 2:
11a. f: Human(charlie)       11b. t: Nice(charlie)
```

Branch 1 closes immediately (contradicts line 1).

In Branch 2, apply implication rule to line 10:
```
Branch 2.1:                  Branch 2.2:
12a. f: Human*(charlie)      12b. t: Industrial(charlie)
```

Branch 2.1 closes (contradicts line 2).
Branch 2.2 closes (contradicts line 8).

**All branches close, so the inference is valid!**

### Key Insight: No Explosion Despite Contradiction

Notice that even though we have `Human(charlie)` and `Human*(charlie)` (a contradiction in classical logic), the system:
1. Doesn't explode (we can't prove arbitrary statements)
2. Still makes valid inferences based on the available rules
3. Correctly concludes Charlie must be either nice or industrial

## CLI Usage Example

### 1. Basic ACrQ Query (Not Yet Implemented)

```bash
# Check if the inference is valid
wkrq check --mode acrq "Human(charlie), ¬Human(charlie), Human(x) → Nice(x), ¬Human(x) → Industrial(x) |- Nice(charlie) | Industrial(charlie)"

# Expected output:
Valid: The inference holds in ACrQ
```

### 2. Step-by-Step Tableau (Verbose Mode)

```bash
# Show tableau construction
wkrq check --mode acrq --verbose "Human(charlie), ¬Human(charlie) |- Nice(charlie) | Industrial(charlie)"

# Expected output:
Parsing in ACrQ transparent mode...
- Human(charlie) → Human(charlie) [bilateral positive]
- ¬Human(charlie) → Human*(charlie) [bilateral negative]

Building tableau...
1. t: Human(charlie)
2. t: Human*(charlie)
3. t: ¬(Nice(charlie) ∨ Industrial(charlie))

Applying rules...
4. t: Nice*(charlie) ∧ Industrial*(charlie) [from 3]
5. t: Nice*(charlie) [from 4]
6. t: Industrial*(charlie) [from 4]

Checking for contradictions...
No contradictions found. Inference is invalid.
```

### 3. Different Parser Modes

```bash
# Transparent mode (default) - accepts standard syntax
wkrq parse --mode acrq "¬Human(x) → Robot(x)"
# Output: Human*(x) → Robot(x)

# Bilateral mode - requires explicit star syntax
wkrq parse --mode acrq-bilateral "Human*(x) → Robot(x)"
# Output: Human*(x) → Robot(x)

wkrq parse --mode acrq-bilateral "¬Human(x) → Robot(x)"
# Error: Negated predicates not allowed in bilateral mode. Use Human* instead.

# Mixed mode - accepts both
wkrq parse --mode acrq-mixed "¬Human(x) ∧ Robot*(y)"
# Output: Human*(x) ∧ Robot*(y)
```

### 4. Handling Knowledge Gaps vs Gluts

```bash
# Knowledge gap example
wkrq check --mode acrq "|- Human(charlie) | Human*(charlie)"
# Output: Invalid (Charlie might have neither property)

# Knowledge glut example  
wkrq check --mode acrq "Human(charlie), Human*(charlie) |- Human(charlie) & Human*(charlie)"
# Output: Valid (Charlie has both properties)
```

## Implementation Status

Currently implemented:
- ✅ ACrQ parser with three modes (transparent, bilateral, mixed)
- ✅ BilateralPredicateFormula representation
- ✅ BilateralTruthValue for four-valued semantics

Not yet implemented:
- ❌ ACrQ-specific tableau rules
- ❌ CLI integration with --mode acrq flag
- ❌ Semantic evaluation for bilateral predicates

## How ACrQ Tableau Differs from wKrQ

1. **Sign System**: Still uses t, f, m, n signs but interprets them for bilateral predicates
2. **Negation Handling**: ¬P(x) creates P*(x), not a negated P(x)
3. **Contradiction Detection**: P(x) and P*(x) can coexist (paraconsistent)
4. **Closure Conditions**: Modified to handle bilateral predicates correctly

The tableau procedure remains structurally similar to wKrQ but with enhanced rules for bilateral predicates, enabling reasoning about incomplete and conflicting information.