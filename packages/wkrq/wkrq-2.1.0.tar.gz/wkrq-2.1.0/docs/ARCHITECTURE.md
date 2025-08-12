# wKrQ Architecture & Ferguson Compliance

## System Architecture

### Unified Tableau Engine

The system uses a unified tableau implementation for both wKrQ and ACrQ:

```
tableau.py
├── Tableau (base class)
│   ├── Shared mechanics
│   ├── Node management
│   ├── Branch tracking
│   └── Model extraction
├── WKrQTableau
│   └── Uses wkrq_rules.py
└── ACrQTableau
    ├── Uses acrq_rules.py
    ├── Bilateral predicate support
    └── Optional LLM integration
```

### Core Components

```
src/wkrq/
├── formula.py              # Formula types & bilateral predicates
├── semantics.py            # Weak Kleene semantics
├── signs.py                # Ferguson's 6-sign system
├── parser.py               # Standard formula parser
├── acrq_parser.py          # ACrQ parser with syntax modes
├── wkrq_rules.py          # wKrQ tableau rules (Definition 9)
├── acrq_rules.py          # ACrQ rules (Definition 18)
├── tableau.py              # Unified tableau engine
├── api.py                  # High-level API functions
└── cli.py                  # Command-line interface
```

### Key Design Patterns

1. **Single Source of Truth**: `TableauNode` stores all node information
2. **Reference by ID**: Branches reference nodes by ID only
3. **Explicit Closure Tracking**: Nodes track `causes_closure` and `contradicts_with`
4. **Formula Indexing**: O(1) contradiction checking via formula index
5. **Lazy Model Extraction**: Models built only from open branches

## Ferguson (2021) Compliance

### Definition 9: wKrQ Tableau Rules

Our implementation exactly follows Ferguson's six-sign system:

| Sign | Meaning | Tableau Behavior |
|------|---------|------------------|
| `t` | True | Definite truth value |
| `f` | False | Definite truth value |
| `e` | Error/undefined | Definite truth value |
| `m` | Meaningful | Branches to `t` or `f` |
| `n` | Nontrue | Branches to `f` or `e` |
| `v` | Variable | Meta-sign for any of {t,f,e} |

### Tableau Rules Implementation

#### Negation Rules
```python
# t:~φ → f:φ
# f:~φ → t:φ
# e:~φ → e:φ
# m:~φ → n:φ
# n:~φ → m:φ
```

#### Conjunction Rules
```python
# t:φ∧ψ → t:φ, t:ψ
# f:φ∧ψ → branches: f:φ | f:ψ | e:φ,n:ψ | n:φ,e:ψ
# e:φ∧ψ → branches: e:φ,v:ψ | v:φ,e:ψ
# m:φ∧ψ → branches: t:φ,t:ψ | f:φ | f:ψ | e:φ,n:ψ | n:φ,e:ψ
# n:φ∧ψ → branches: f:φ | f:ψ | e:φ,n:ψ | n:φ,e:ψ | e:φ,e:ψ
```

#### Implication as Disjunction
```python
# φ→ψ treated as ~φ∨ψ
```

#### Restricted Quantifiers
```python
# [∃x P(x)]Q(x): "There exists x such that P(x) and Q(x)"
# [∀x P(x)]Q(x): "For all x, if P(x) then Q(x)"
```

### Definition 10: Branch Closure

A branch closes when there is a formula φ and distinct v, u ∈ {t,f,e} such that both v:φ and u:φ appear on the branch.

```python
def _check_contradiction(self, node, branch):
    for other_sign in [t, f, e]:
        if other_sign != node.formula.sign:
            if formula exists with other_sign:
                return True, contradicting_node_id
    return False, None
```

### Definition 18: ACrQ System

ACrQ = wKrQ minus general negation elimination plus bilateral predicates:

1. **No general negation elimination** for compound formulas
2. **Bilateral predicates**: ~R(x) → R*(x)
3. **Glut tolerance**: R(x) ∧ R*(x) is satisfiable
4. **Gap allowance**: ¬R(x) ∧ ¬R*(x) is satisfiable

### Lemma 5: ACrQ Branch Closure

In ACrQ, branches close only for standard contradictions, not gluts:

```python
def _check_contradiction(self, node, branch):
    # Check if this is a bilateral glut
    if self._is_bilateral_glut(node, branch):
        return False, None  # Gluts allowed
    
    # Otherwise use standard contradiction checking
    return super()._check_contradiction(node, branch)
```

## Weak Kleene Semantics

The system implements weak Kleene three-valued logic:

| Operation | True | False | Undefined |
|-----------|------|-------|-----------|
| p ∧ q | Standard | Standard | Any undefined → undefined |
| p ∨ q | Standard | Standard | Any undefined → undefined |
| p → q | Standard | Standard | Any undefined → undefined |
| ¬p | Standard | Standard | Undefined → undefined |

Key principle: **Any operation with undefined yields undefined**

## Quantifier Handling

### Universal Quantifier Strategy
1. Try existing constants first (unification)
2. Generate fresh constant only if needed
3. Track instantiations to avoid redundancy

### Existential Quantifier Strategy
1. Always generate fresh witness
2. Add witness to ground terms for future universal instantiations

## Model Extraction

Models are extracted from open branches:

```python
def _extract_model(self, branch):
    # Collect all atoms
    for node_id in branch.node_ids:
        atoms.update(node.formula.formula.get_atoms())
    
    # Determine valuations
    for atom in atoms:
        if has_t: valuations[atom] = TRUE
        elif has_f: valuations[atom] = FALSE
        elif has_e: valuations[atom] = UNDEFINED
        elif has_m: valuations[atom] = TRUE  # or FALSE
        elif has_n: valuations[atom] = FALSE  # or UNDEFINED
        else: valuations[atom] = UNDEFINED
```

## Performance Optimizations

1. **Formula Indexing**: O(1) contradiction checking
2. **Node ID References**: Minimize memory duplication
3. **Lazy Processing**: Only process nodes when needed
4. **Branch Pruning**: Stop processing closed branches immediately
5. **Unification**: Reuse existing constants for universal quantifiers

## LLM Integration (ACrQ only)

Optional LLM evaluation for atomic formulas:

```python
def llm_evaluator(formula) -> BilateralTruthValue:
    # Returns bilateral truth value:
    # - positive=TRUE, negative=FALSE: standard true
    # - positive=FALSE, negative=TRUE: standard false
    # - positive=FALSE, negative=FALSE: gap
    # - positive=TRUE, negative=TRUE: glut
```

The LLM evaluator is called for atomic formulas when no logical rules apply, enabling hybrid symbolic-neural reasoning.