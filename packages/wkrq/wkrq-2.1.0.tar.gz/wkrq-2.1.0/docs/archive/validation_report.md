# wKrQ Validation Report

This report demonstrates the behavior of the wKrQ system through examples extracted from the test suite. Generated for review by experts in philosophical logic.

## Important Note

This report was generated after fixing a critical bug in the restricted quantifier instantiation. The bug caused invalid inferences like `[∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)` to be incorrectly marked as valid. This has been fixed.

## Table of Contents

- [Ferguson Six-Sign System](#ferguson-six-sign-system)
- [Ferguson Negation Rules](#ferguson-negation-rules)
- [Weak Kleene Semantics](#weak-kleene-semantics)
- [Restricted Quantifiers](#restricted-quantifiers)
- [Classical Inferences](#classical-inferences)
- [Invalid Inferences](#invalid-inferences)
- [Aristotelian Syllogisms](#aristotelian-syllogisms)
- [De Morgan's Laws](#de-morgans-laws)
- [ACrQ Paraconsistent Reasoning](#acrq-paraconsistent-reasoning)

---

## Ferguson Six-Sign System

### Sign t constrains to true

**Formula**: `p`

**Result**:
```
Satisfiable: True
Models (1):
  1. {p=t}
```
---

### Sign m allows both true and false

**Formula**: `p | ~p`

**Result**:
```
Satisfiable: True
Models (2):
  1. {p=t}
  2. {p=e}
```
---

## Ferguson Negation Rules

### t-negation: t:¬φ leads to f:φ

**Formula**: `~p |- q`

**Result**:
```
✗ Invalid inference
Countermodels:
  1. {p=f, q=f}

Tableau tree:
 0. t: (~p) & (~q)
    ├──  1. t: ~p      [t-conjunction: 0]
    │   └──  3. f: p   [t-negation: 1]
    └──  2. t: ~q      [t-conjunction: 0]
        └──  4. f: q   [t-negation: 2]
```
---

## Weak Kleene Semantics

### Undefined is contagious in disjunction

**Formula**: `(p | q)`

**Result**:
```
Satisfiable: True
Models (2):
  1. {p=t, q=e}
  2. {p=e, q=t}
```
---

### Classical tautology can be undefined

**Formula**: `p | ~p`

**Result**:
```
Satisfiable: True
Models (2):
  1. {p=t}
  2. {p=e}
```
---

## Restricted Quantifiers

### Universal instantiation (valid)

**Formula**: `[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)`

**Result**:
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X Human(X)]Mortal(X) & Human(socrates)) & (~Mortal(socrates))
    ├──  1. t: [∀X Human(X)]Mortal(X) & Human(socrates)                     [t-conjunction: 0]
    │   ├──  3. t: [∀X Human(X)]Mortal(X)                                   [t-conjunction: 1]
    │   │   ├──  6. f: Human(socrates)  ×                                   [t-restricted-forall: 3]
    │   │   └──  7. t: Mortal(socrates)  ×                                  [t-restricted-forall: 3]
    │   └──  4. t: Human(socrates)  ×                                       [t-conjunction: 1]
    └──  2. t: ~Mortal(socrates)                                            [t-conjunction: 0]
        └──  5. f: Mortal(socrates)  ×                                      [t-negation: 2]
```
---

### Existential to universal (invalid) - THE BUG WE FIXED

**Formula**: `[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)`

**Result**:
```
✗ Invalid inference
Countermodels:
  1. {A(c_3)=t, A(c_6)=t, B(c_3)=t, B(c_6)=f}

Tableau tree:
 0. t: [∃X A(X)]B(X) & (~[∀Y A(Y)]B(Y))
    ├──  1. t: [∃X A(X)]B(X)                [t-conjunction: 0]
    │   ├──  3. t: A(c_3)                   [t-restricted-exists: 1]
    │   └──  4. t: B(c_3)                   [t-restricted-exists: 1]
    └──  2. t: ~[∀Y A(Y)]B(Y)               [t-conjunction: 0]
        └──  5. f: [∀Y A(Y)]B(Y)            [t-negation: 2]
            ├──  6. t: A(c_6)               [f-restricted-forall: 5]
            └──  7. f: B(c_6)               [f-restricted-forall: 5]
```
---

## Classical Inferences

### Modus Ponens

**Formula**: `p, p -> q |- q`

**Result**:
```
✓ Valid inference
```
---

### Modus Tollens

**Formula**: `p -> q, ~q |- ~p`

**Result**:
```
✓ Valid inference
```
---

### Hypothetical Syllogism

**Formula**: `p -> q, q -> r |- p -> r`

**Result**:
```
✓ Valid inference
```
---

## Invalid Inferences

### Affirming the Consequent

**Formula**: `p -> q, q |- p`

**Result**:
```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}
```
---

### Denying the Antecedent

**Formula**: `p -> q, ~p |- ~q`

**Result**:
```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}
```
---

## Aristotelian Syllogisms

### Barbara: All M are P, All S are M ⊢ All S are P

**Formula**: `[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)`

**Result**:
```
✓ Valid inference
```
---

### Celarent: No M are P, All S are M ⊢ No S are P

**Formula**: `[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))`

**Result**:
```
✓ Valid inference
```
---

## De Morgan's Laws

### ¬(p ∧ q) ⊢ ¬p ∨ ¬q

**Formula**: `~(p & q) |- (~p | ~q)`

**Result**:
```
✓ Valid inference
```
---

### Quantified De Morgan (now valid after our fix)

**Formula**: `~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))`

**Result**:
```
✓ Valid inference
```
---

## ACrQ Paraconsistent Reasoning

### Knowledge gluts don't explode

**Formula**: `Symptom(patient, fever) & ~Symptom(patient, fever) |- Unrelated(claim)`
**Mode**: ACRQ

**Result**:
```
ACrQ Inference (transparent mode):
  Premises: Symptom(patient, fever) & Symptom*(patient, fever)
  Conclusion: Unrelated(claim)
  ✗ Invalid inference
  Countermodels:
    1. {Symptom(patient, fever)=t, Symptom*(patient, fever)=t, Unrelated(claim)=f}
```
---

### Local inconsistency preserved

**Formula**: `P(a) & P*(a)`
**Mode**: ACRQ

**Result**:
```

```
---

