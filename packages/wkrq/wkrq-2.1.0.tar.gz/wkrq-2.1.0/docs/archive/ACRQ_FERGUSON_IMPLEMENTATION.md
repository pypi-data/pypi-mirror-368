# ACrQ Implementation Based on Ferguson (2021) Definition 18

**Version**: 2.0.0  
**Date**: August 2025  
**Status**: Complete

## Overview

This document describes the implementation of ACrQ (Analytic Containment with restricted Quantification) based on Ferguson's Definition 18. ACrQ is obtained by modifying wKrQ in a specific way: dropping the general negation elimination rule and adding special handling for bilateral predicates.

## Ferguson's Definition 18

From the paper:

> **Definition 18.** Let wKrQ* be the result of dropping the ~ rule from wKrQ. Then the tableau calculus ACrQ is defined by adding to wKrQ*:
> - Rules for bilateral predicates R and R*
> - Special branch closure conditions (Lemma 5)

## Key Implementation Details

### 1. Dropped Negation Elimination

In wKrQ, the general negation rule is:
```
v : ~φ
------
~v : φ
```

In ACrQ, this rule is **dropped** except for specific cases:
- Double negation: `v : ~~φ → v : φ`
- Negated predicates: `v : ~R(x) → v : R*(x)`
- Negated bilateral predicates: `v : ~R*(x) → v : R(x)`

### 2. Bilateral Predicate Handling

Each predicate R has a dual R* for tracking negative evidence independently:
- `R(a)`: Positive evidence for R at a
- `R*(a)`: Negative evidence for R at a

This creates four information states:
1. **True**: R(a)=t, R*(a)=f (positive evidence only)
2. **False**: R(a)=f, R*(a)=t (negative evidence only)
3. **Gap**: R(a)=f, R*(a)=f (no evidence)
4. **Glut**: R(a)=t, R*(a)=t (conflicting evidence)

### 3. Branch Closure (Lemma 5)

Branches close when:
- Standard contradiction: `u:φ` and `v:φ` for distinct u,v ∈ {t,f,e}
- **NOT** when `t:R(a)` and `t:R*(a)` (gluts are allowed!)

The key insight from Lemma 5 is that bilateral predicates share a common logical operator, preventing closure in glut cases.

### 4. Lemma 6: Validity Preservation

Lemma 6 states: `Γ ⊢_ACrQ φ` if and only if `Γ* ⊢_ACrQ φ*`

This ensures that proofs in ACrQ are preserved under the bilateral transformation.

## Implementation Structure

### Core Files

1. **`acrq_ferguson_rules.py`**: Implements ACrQ-specific tableau rules
   - `get_acrq_negation_rule()`: Handles restricted negation
   - `get_acrq_rule()`: Main rule dispatcher

2. **`acrq_tableau.py`**: Extended tableau for ACrQ
   - `ACrQBranch`: Paraconsistent branch closure
   - `ACrQTableau`: Uses Ferguson rules
   - `ACrQModel`: Bilateral valuations

3. **`test_acrq_ferguson.py`**: Comprehensive test suite
   - Tests Definition 18 compliance
   - Validates Lemma 5 (gluts allowed)
   - Checks negation handling

### Key Design Decisions

1. **Transparent Negation Translation**: `~Human(x)` automatically becomes `Human*(x)`
2. **Paraconsistent Branch Closure**: Gluts don't close branches
3. **Reuse of wKrQ Rules**: All non-negation rules inherited from wKrQ
4. **Bilateral Model Extraction**: Models show gap/glut states

## Usage Examples

```python
from wkrq import SignedFormula, t, parse_acrq_formula
from wkrq.acrq_tableau import ACrQTableau

# 1. Gluts are allowed
human = parse_acrq_formula("Human(alice) & ~Human(alice)")
tableau = ACrQTableau([SignedFormula(t, human)])
result = tableau.construct()
assert result.satisfiable  # True! Glut allowed

# 2. Negation translation
neg_human = parse_acrq_formula("~Human(alice)")
# Automatically converted to Human*(alice)

# 3. No general negation elimination
compound = parse("~(p & q)")
# Remains as ~(p & q), not decomposed
```

## Differences from wKrQ

| Feature | wKrQ | ACrQ |
|---------|------|------|
| Negation elimination | Full (v:~φ → ~v:φ) | Restricted (predicates only) |
| Predicates | Single-sided | Bilateral (R/R*) |
| Contradictions | R(a) ∧ ¬R(a) closes | R(a) ∧ R*(a) allowed (glut) |
| Knowledge gaps | Not explicit | R(a)=f ∧ R*(a)=f |
| Paraconsistency | No | Yes |

## Testing

The implementation includes comprehensive tests:
- Negation elimination correctly dropped
- Bilateral predicate conversion
- Glut handling (Lemma 5)
- Standard contradictions still close
- Quantifier rules work correctly
- Model extraction with bilateral valuations

All tests pass, confirming exact compliance with Ferguson's Definition 18.

## Future Work

- Optimize bilateral predicate indexing
- Add more complex ACrQ examples
- Implement Lemma 6 proof transformation
- Create visualization for bilateral models

## References

Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic." In *International Conference on Automated Reasoning with Analytic Tableaux and Related Methods*, pp. 3-19. Springer.