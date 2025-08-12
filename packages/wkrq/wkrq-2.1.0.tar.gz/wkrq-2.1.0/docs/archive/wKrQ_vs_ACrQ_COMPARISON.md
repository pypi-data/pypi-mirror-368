# wKrQ vs ACrQ: Key Implementation Differences

**Version**: 2.0.0  
**Date**: August 2025  
**Based on**: Ferguson (2021) Definitions 9 and 18

## Overview

This document provides a detailed comparison between the wKrQ and ACrQ implementations in this codebase. Both systems are based on Ferguson's 2021 paper, with wKrQ implementing Definition 9 and ACrQ implementing Definition 18 (which modifies wKrQ by dropping negation elimination and adding bilateral predicates).

## Key Differences

### 1. Negation Handling

**wKrQ**:
- Has general negation elimination rule: `v : ~φ → ~v : φ`
- Where `~t = f`, `~f = t`, `~e = e`
- Applies to all formulas including compound formulas

**ACrQ**:
- Drops general negation elimination for compound formulas
- Only handles specific cases:
  - Double negation: `v : ~~φ → v : φ`
  - Negated predicates: `v : ~R(c) → v : R*(c)`
  - Negated bilateral: `v : ~R*(c) → v : R(c)`
- This is the key modification in Ferguson's Definition 18

### 2. Bilateral Predicates

**wKrQ**:
- Standard predicates only: `R(a)`
- Single truth value per predicate instance

**ACrQ**:
- Each predicate R has a dual R* for tracking negative evidence
- Creates four possible information states:
  - `R(a)=t, R*(a)=f`: Positive evidence only (clearly true)
  - `R(a)=f, R*(a)=t`: Negative evidence only (clearly false)
  - `R(a)=f, R*(a)=f`: No evidence either way (knowledge gap)
  - `R(a)=t, R*(a)=t`: Conflicting evidence (knowledge glut)

### 3. Branch Closure Rules

**wKrQ**:
- Branch closes when `u:φ` and `v:φ` appear for distinct `u,v ∈ {t,f,e}`
- Standard contradiction detection per Definition 10

**ACrQ**:
- Modified closure per Ferguson's Lemma 5
- Standard contradictions still close: `t:φ` and `f:φ` for same φ
- **Critical difference**: Gluts are allowed - `t:R(a)` and `t:R*(a)` can coexist
- This enables paraconsistent reasoning (handling contradictions without explosion)

### 4. Parser Modes

**wKrQ**:
- Single parser mode
- Standard logical syntax

**ACrQ**:
- Three parser modes for different use cases:
  - **Transparent Mode** (default): 
    - User writes standard syntax: `¬P(x)`
    - System internally converts to: `P*(x)`
    - Star syntax (`P*`) is forbidden
  - **Bilateral Mode**: 
    - Must use explicit star syntax: `P*(x)`
    - Negated predicates (`¬P(x)`) are forbidden
  - **Mixed Mode**: 
    - Both `¬P(x)` and `P*(x)` syntaxes allowed
    - Both convert to same internal representation

### 5. Model Representation

**wKrQ**:
- Standard `Model` class with simple valuations
- Maps atoms to truth values: `{p: TRUE, q: FALSE, r: UNDEFINED}`

**ACrQ**:
- Extended `ACrQModel` with bilateral valuations
- Tracks both positive and negative evidence
- Provides `BilateralTruthValue` objects:
  ```python
  bilateral_valuations = {
      "Human(alice)": BilateralTruthValue(positive=TRUE, negative=FALSE),  # Clearly true
      "Robot(alice)": BilateralTruthValue(positive=TRUE, negative=TRUE),   # Glut
      "Alien(alice)": BilateralTruthValue(positive=FALSE, negative=FALSE), # Gap
  }
  ```

### 6. Rule Application

**wKrQ**:
- Uses Ferguson rules from Definition 9
- Full negation elimination for all formulas
- Standard tableau expansion

**ACrQ**:
- Uses modified rules from Definition 18
- Same rules for quantifiers and connectives (∧, ∨, →)
- Different negation handling (no general elimination)
- Special handling for bilateral predicates

### 7. Formula Type Hierarchy

**wKrQ**:
```
Formula (abstract)
├── PropositionalAtom
├── CompoundFormula
├── PredicateFormula
└── RestrictedQuantifierFormula
    ├── RestrictedExistentialFormula
    └── RestrictedUniversalFormula
```

**ACrQ** (extends wKrQ):
```
Formula (abstract)
├── PropositionalAtom
├── CompoundFormula
├── PredicateFormula
│   └── BilateralPredicateFormula (new)
└── RestrictedQuantifierFormula
    ├── RestrictedExistentialFormula
    └── RestrictedUniversalFormula
```

### 8. Implementation File Structure

**wKrQ Core Files**:
- `ferguson_rules.py`: Standard wKrQ tableau rules
- `tableau.py`: Standard tableau engine with contradiction detection
- `parser.py`: Basic formula parser
- `signs.py`: Six-sign system (t, f, e, m, n, v)

**ACrQ Extension Files**:
- `acrq_ferguson_rules.py`: Modified rules without general negation elimination
- `acrq_tableau.py`: Extended tableau with paraconsistent glut handling
- `acrq_parser.py`: Mode-aware parser with bilateral support
- Formula types share same signs system

### 9. Key Implementation Details

#### ACrQ Negation Rule (`acrq_ferguson_rules.py`):
```python
def get_acrq_negation_rule(signed_formula: SignedFormula) -> Optional[FergusonRule]:
    """ACrQ drops the general negation elimination rule.
    Only handles:
    1. Double negation: v : ~~φ → v : φ
    2. Negated predicates: v : ~R(c) → v : R*(c)
    3. Negated bilateral: v : ~R*(c) → v : R(c)
    """
    # No general negation elimination for compound formulas
    # This is the key difference from wKrQ
```

#### ACrQ Glut Detection (`acrq_tableau.py`):
```python
def _check_contradiction(self, new_formula: SignedFormula) -> bool:
    """Check for contradictions per Ferguson's Lemma 5.
    
    A branch closes when:
    1. Standard contradiction: u:φ and v:φ for distinct u,v ∈ {t,f,e}
    2. But NOT when t:R(a) and t:R*(a) appear (this is a glut, allowed)
    """
    if self._is_bilateral_glut(formula, sign):
        return False  # Don't close on gluts - key for paraconsistency
```

### 10. Practical Impact

**wKrQ**:
- Classical-style reasoning with undefined values
- Suitable for modeling partial information
- Contradictions lead to branch closure
- Three truth values: true, false, undefined

**ACrQ**:
- Paraconsistent and paracomplete reasoning
- Can handle:
  - **Knowledge gluts**: Conflicting information without explosion
  - **Knowledge gaps**: Missing information without assumptions
  - **Mixed evidence**: Some positive, some negative
- Four information states per predicate
- More nuanced representation of real-world knowledge

### 11. Example: Knowledge Representation

Consider the statement "Alice is human":

**In wKrQ**:
- `Human(alice) = TRUE`: Alice is human
- `Human(alice) = FALSE`: Alice is not human
- `Human(alice) = UNDEFINED`: Unknown if Alice is human

**In ACrQ**:
- `Human(alice)=t, Human*(alice)=f`: Clear evidence Alice is human
- `Human(alice)=f, Human*(alice)=t`: Clear evidence Alice is not human
- `Human(alice)=f, Human*(alice)=f`: No evidence either way (gap)
- `Human(alice)=t, Human*(alice)=t`: Conflicting evidence (glut)

The last case (glut) allows ACrQ to handle situations like:
- Database inconsistencies
- Conflicting expert opinions
- Sensor disagreements
- Historical contradictions

### 12. Use Case Recommendations

**Use wKrQ when**:
- You need standard three-valued logic
- Contradictions should fail/close branches
- Simpler semantic model is sufficient
- Classical reasoning with undefined is adequate

**Use ACrQ when**:
- You need to handle conflicting information gracefully
- Knowledge gaps and gluts must be distinguished
- Paraconsistent reasoning is required
- Modeling real-world inconsistent data sources

## Testing Coverage

Both implementations have comprehensive test suites:
- **wKrQ**: Full test coverage including Ferguson compliance tests
- **ACrQ**: Extended tests including glut handling and bilateral predicates
- **Total**: 311 tests passing across both systems

## Conclusion

ACrQ extends wKrQ with bilateral predicates and modified negation handling to enable paraconsistent reasoning. The key innovation is allowing knowledge gluts (t:R(a) and t:R*(a)) to coexist without causing logical explosion, making it suitable for reasoning with inconsistent information sources while maintaining logical rigor.