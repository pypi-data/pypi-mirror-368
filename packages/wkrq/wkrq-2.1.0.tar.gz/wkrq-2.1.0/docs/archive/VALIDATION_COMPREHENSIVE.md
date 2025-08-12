# wKrQ Comprehensive Validation Document

Generated: 2025-08-05 16:34:39

## Introduction

This document provides a comprehensive validation of the wKrQ (weak Kleene logic with restricted Quantification) implementation. All examples are extracted from the pytest test suite to ensure consistency between tests and documentation.

## Tableau Rules Reference

This section provides a complete reference for the tableau rules as implemented in wKrQ and ACrQ systems. Each rule shows the pattern matching format used in the tableau tree displays.

### wKrQ Tableau Rules (Ferguson (2021) Definition 9)

**Negation Rules:**
- `t-negation`: `t : ~φ → f : φ`
- `f-negation`: `f : ~φ → t : φ`
- `e-negation`: `e : ~φ → e : φ`
- `m-negation`: `m : ~φ → n : φ`
- `n-negation`: `n : ~φ → m : φ`

**Conjunction Rules:**
- `t-conjunction`: `t : φ ∧ ψ → t : φ, t : ψ`
- `f-conjunction`: `f : φ ∧ ψ → [f : φ | f : ψ]` (branches)
- `e-conjunction`: `e : φ ∧ ψ → [e : φ | e : ψ]` (branches)
- `m-conjunction`: `m : φ ∧ ψ → [t : φ, t : ψ | f : φ | f : ψ]` (branches)
- `n-conjunction`: `n : φ ∧ ψ → [f : φ | f : ψ | e : φ | e : ψ]` (branches)

**Disjunction Rules:**
- `t-disjunction`: `t : φ ∨ ψ → [t : φ | t : ψ]` (branches)
- `f-disjunction`: `f : φ ∨ ψ → f : φ, f : ψ`
- `e-disjunction`: `e : φ ∨ ψ → e : φ, e : ψ`
- `m-disjunction`: `m : φ ∨ ψ → [t : φ | t : ψ | f : φ, f : ψ]` (branches)
- `n-disjunction`: `n : φ ∨ ψ → [f : φ, f : ψ | e : φ, e : ψ]` (branches)

**Implication Rules:**
- `t-implication`: `t : φ → ψ → [f : φ | t : ψ]` (branches)
- `f-implication`: `f : φ → ψ → t : φ, f : ψ`
- `e-implication`: `e : φ → ψ → e : φ, e : ψ`
- `m-implication`: `m : φ → ψ → [f : φ | t : ψ | t : φ, f : ψ]` (branches)
- `n-implication`: `n : φ → ψ → [t : φ, f : ψ | t : φ, e : ψ | e : φ, f : ψ | e : φ, e : ψ]` (branches)

**Restricted Quantifier Rules:**
- `t-restricted-forall`: `t : [∀X R(X,v₁,...,vₙ)]S(X,u₁,...,uₘ) → t : R(c,v₁,...,vₙ) → t : S(c,u₁,...,uₘ)` (for constants c)
- `f-restricted-forall`: `f : [∀X R(X,v₁,...,vₙ)]S(X,u₁,...,uₘ) → t : R(c,v₁,...,vₙ), f : S(c,u₁,...,uₘ)` (fresh constant c)
- `t-restricted-exists`: `t : [∃X R(X,v₁,...,vₙ)]S(X,u₁,...,uₘ) → t : R(c,v₁,...,vₙ), t : S(c,u₁,...,uₘ)` (fresh constant c)
- `f-restricted-exists`: `f : [∃X R(X,v₁,...,vₙ)]S(X,u₁,...,uₘ) → [m : R(c₁,v₁,...,vₙ), m : S(c₁,u₁,...,uₘ) | n : R(c₁ₐᵣᵦ,v₁,...,vₙ), n : S(c₁ₐᵣᵦ,u₁,...,uₘ)]` (branches)

### ACrQ Additional Rules (Ferguson (2021) Definition 18)

ACrQ = wKrQ rules **minus** general negation elimination **plus** bilateral predicate rules.

**Bilateral Predicate Negation (ACrQ only):**
- `t-predicate-negation`: `t : ~R(t₁,...,tₙ) → t : R*(t₁,...,tₙ)` (only for predicates)
- `f-predicate-negation`: `f : ~R(t₁,...,tₙ) → f : R*(t₁,...,tₙ)`
- `e-predicate-negation`: `e : ~R(t₁,...,tₙ) → e : R*(t₁,...,tₙ)`
- `m-predicate-negation`: `m : ~R(t₁,...,tₙ) → m : R*(t₁,...,tₙ)`
- `n-predicate-negation`: `n : ~R(t₁,...,tₙ) → n : R*(t₁,...,tₙ)`

**Branch Closure Conditions:**
- **wKrQ**: Branch closes when distinct signs v, u ∈ {t,f,e} appear for same formula
- **ACrQ**: Modified per Ferguson (2021) Lemma 5 - gluts allowed (t:R(a) and t:R*(a) can coexist)

**Sign Meanings:**
- `t`: Formula must be true
- `f`: Formula must be false
- `e`: Formula must be undefined/error
- `m`: Formula is meaningful (branches to t or f)
- `n`: Formula is nontrue (branches to f or e)

## Table of Contents

- [Six-Sign Tableau System](#six-sign-tableau-system)
- [Sign Interactions and Edge Cases](#sign-interactions-and-edge-cases)
- [Weak Kleene Three-Valued Logic](#weak-kleene-three-valued-logic)
- [Weak vs Strong Kleene Boundary Cases](#weak-vs-strong-kleene-boundary-cases)
- [Classical Valid Inferences](#classical-valid-inferences)
- [Classical Invalid Inferences](#classical-invalid-inferences)
- [Restricted Quantification](#restricted-quantification)
- [Quantifier Scoping and Complex Cases](#quantifier-scoping-and-complex-cases)
- [Constant Generation and Witness Management](#constant-generation-and-witness-management)
- [Aristotelian Syllogisms](#aristotelian-syllogisms)
- [De Morgan's Laws](#de-morgans-laws)
- [Tableau Rule Application and Proof Structure](#tableau-rule-application-and-proof-structure)
- [Three-Valued Model Construction](#three-valued-model-construction)
- [Tableau System Properties](#tableau-system-properties)
- [ACrQ Paraconsistent Logic](#acrq-paraconsistent-logic)
- [ACrQ Glut and Gap Complex Interactions](#acrq-glut-and-gap-complex-interactions)
- [Countermodel Construction and Quality](#countermodel-construction-and-quality)
- [Performance and Complexity Boundaries](#performance-and-complexity-boundaries)
- [Ferguson (2021) Literature Examples](#ferguson-(2021)-literature-examples)

---

## Six-Sign Tableau System

Basic sign behaviors in the wKrQ tableau system

### t-sign forces true

**CLI Command:**
```bash
python -m wkrq --sign=t --tree --show-rules --models p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=t}

Tableau tree:
 0. t: p
```
---

### f-sign forces false

**CLI Command:**
```bash
python -m wkrq --sign=f --tree --show-rules --models p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=f}

Tableau tree:
 0. f: p
```
---

### e-sign forces undefined

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e}

Tableau tree:
 0. e: p
```
---

### m-sign allows true or false

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules --models p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=t}

Tableau tree:
 0. m: p
```
---

### n-sign allows false or undefined

**CLI Command:**
```bash
python -m wkrq --sign=n --tree --show-rules --models p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=f}

Tableau tree:
 0. n: p
```
---

## Sign Interactions and Edge Cases

Complex interactions between signs and branch closure conditions

### m-sign branching on complex formula

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules p & (q | r)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: p & (q | r)
    ├──  1. t: p       [m-conjunction: 0]
    ├──  2. t: q | r   [m-conjunction: 0]
    ├──  3. f: p       [m-conjunction: 0]
    └──  4. f: q | r   [m-conjunction: 0]
```
---

### n-sign branching on implication

**CLI Command:**
```bash
python -m wkrq --sign=n --tree --show-rules p -> q
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. n: p -> q
    ├──  1. t: p  [n-implication: 0]
    ├──  2. f: q  [n-implication: 0]
    ├──  3. e: p  [n-implication: 0]
    └──  4. e: q  [n-implication: 0]
```
---

### Sign propagation through negation

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules ~~p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: ~(~p)
    ├──  1. f: ~p    [m-negation: 0]
    │   └──  3. t: p [f-negation: 1]
    └──  2. t: ~p    [m-negation: 0]
        └──  4. f: p [t-negation: 2]
```
---

### Branch closure from different signs

**CLI Command:**
```bash
python -m wkrq --tree --show-rules p & (q | ~p)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: p & (q | (~p))
    ├──  1. t: p          [t-conjunction: 0]
    └──  2. t: q | (~p)   [t-conjunction: 0]
        ├──  3. t: q      [t-disjunction: 2]
        └──  4. t: ~p     [t-disjunction: 2]
```
---

### No closure with compatible signs

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules p | q
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: p | q
    ├──  1. t: p [m-disjunction: 0]
    ├──  2. t: q [m-disjunction: 0]
    ├──  3. f: p [m-disjunction: 0]
    └──  4. f: q [m-disjunction: 0]
```
---

### Closure through formula decomposition

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p & ~p) | (q & ~q)
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. t: (p & (~p)) | (q & (~q))
    ├──  1. t: p & (~p)            [t-disjunction: 0]
    │   ├──  3. t: p  ×            [t-conjunction: 1]
    │   └──  4. t: ~p              [t-conjunction: 1]
    │       └──  7. f: p  ×        [t-negation: 4]
    └──  2. t: q & (~q)            [t-disjunction: 0]
        ├──  5. t: q  ×            [t-conjunction: 2]
        └──  6. t: ~q              [t-conjunction: 2]
            └──  8. f: q  ×        [t-negation: 6]
```
---

### No closure from m:p alone

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: p
```
---

### Complex formula with multiple sign interactions

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules (p -> q) & (q -> r)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: (p -> q) & (q -> r)
    ├──  1. t: p -> q          [m-conjunction: 0]
    │   ├──  9. f: p           [t-implication: 1]
    │   └── 10. t: q           [t-implication: 1]
    ├──  2. t: q -> r          [m-conjunction: 0]
    ├──  3. f: p -> q          [m-conjunction: 0]
    │   ├──  5. t: p           [f-implication: 3]
    │   └──  6. f: q           [f-implication: 3]
    └──  4. f: q -> r          [m-conjunction: 0]
        ├──  7. t: q           [f-implication: 4]
        └──  8. f: r           [f-implication: 4]
```
---

## Weak Kleene Three-Valued Logic

Core semantic behaviors of weak Kleene logic

### Undefined is contagious in conjunction

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models p & q
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e}

Tableau tree:
 0. e: p & q
    ├──  1. e: p [e-conjunction: 0]
    └──  2. e: q [e-conjunction: 0]
```
---

### Undefined is contagious in disjunction

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models p | q
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e}

Tableau tree:
 0. e: p | q
    ├──  1. e: p [e-disjunction: 0]
    └──  2. e: q [e-disjunction: 0]
```
---

### Classical tautologies can be undefined

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models p | ~p
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e}

Tableau tree:
 0. e: p | (~p)
    ├──  1. e: p    [e-disjunction: 0]
    └──  2. e: ~p   [e-disjunction: 0]
```
---

### Excluded middle cannot be false

**CLI Command:**
```bash
python -m wkrq --sign=f --tree --show-rules --models p | ~p
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. f: p | (~p)
    ├──  1. f: p  ×     [f-disjunction: 0]
    └──  2. f: ~p       [f-disjunction: 0]
        └──  3. t: p  × [f-negation: 2]
```
---

### Contradiction cannot be true

**CLI Command:**
```bash
python -m wkrq --sign=t --tree --show-rules --models p & ~p
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. t: p & (~p)
    ├──  1. t: p  ×     [t-conjunction: 0]
    └──  2. t: ~p       [t-conjunction: 0]
        └──  3. f: p  × [t-negation: 2]
```
---

## Weak vs Strong Kleene Boundary Cases

Cases highlighting differences between weak and strong Kleene logic

### True AND undefined = undefined

*Note: With p=t, q=e, result is e (not t as in strong Kleene)*

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models (p & q)
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=t, q=t}

Tableau tree:
 0. t: p & q
    ├──  1. t: p [t-conjunction: 0]
    └──  2. t: q [t-conjunction: 0]
```
---

### False OR undefined = undefined

*Note: With p=f, q=e, result is e (not f as in strong Kleene)*

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models (p | q)
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {p=t, q=e}
  2. {p=e, q=t}

Tableau tree:
 0. t: p | q
    ├──  1. t: p [t-disjunction: 0]
    └──  2. t: q [t-disjunction: 0]
```
---

### Implication with undefined antecedent

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models p -> q
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e}

Tableau tree:
 0. e: p -> q
    ├──  1. e: p  [e-implication: 0]
    └──  2. e: q  [e-implication: 0]
```
---

### Implication with undefined consequent

*Note: With p=t, q=e, result is e*

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models p -> q
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {p=f, q=e}
  2. {p=e, q=t}

Tableau tree:
 0. t: p -> q
    ├──  1. f: p  [t-implication: 0]
    └──  2. t: q  [t-implication: 0]
```
---

### Chain of undefined propagation

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models ((p & q) | r) & s
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e, r=e, s=e}

Tableau tree:
 0. e: ((p & q) | r) & s
    ├──  1. e: (p & q) | r   [e-conjunction: 0]
    └──  2. e: s             [e-conjunction: 0]
```
---

### Nested operations with mixed values

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models (p | (q & r)) -> s
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {p=e, q=e, r=e, s=e}
  2. {p=e, q=e, r=e, s=t}

Tableau tree:
 0. t: (p | (q & r)) -> s
    ├──  1. f: p | (q & r)    [t-implication: 0]
    └──  2. t: s              [t-implication: 0]
```
---

### Complex tautology that can be undefined

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models (p -> p) & (q | ~q)
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e}

Tableau tree:
 0. e: (p -> p) & (q | (~q))
    ├──  1. e: p -> p            [e-conjunction: 0]
    │   ├──  3. e: p             [e-implication: 1]
    │   └──  4. e: p             [e-implication: 1]
    └──  2. e: q | (~q)          [e-conjunction: 0]
        ├──  5. e: q             [e-disjunction: 2]
        └──  6. e: ~q            [e-disjunction: 2]
```
---

## Classical Valid Inferences

Standard inference patterns that remain valid

### Modus Ponens

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p, p -> q |- q
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (p & (p -> q)) & (~q)
    ├──  1. t: p & (p -> q)      [t-conjunction: 0]
    │   ├──  3. t: p  ×          [t-conjunction: 1]
    │   └──  4. t: p -> q        [t-conjunction: 1]
    │       ├──  6. f: p  ×      [t-implication: 4]
    │       └──  7. t: q  ×      [t-implication: 4]
    └──  2. t: ~q                [t-conjunction: 0]
        └──  5. f: q  ×          [t-negation: 2]
```
---

### Modus Tollens

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p -> q, ~q |- ~p
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((p -> q) & (~q)) & (~(~p))
    ├──  1. t: (p -> q) & (~q)         [t-conjunction: 0]
    │   ├──  3. t: p -> q              [t-conjunction: 1]
    │   │   ├──  8. f: p  ×            [t-implication: 3]
    │   │   └──  9. t: q  ×            [t-implication: 3]
    │   └──  4. t: ~q                  [t-conjunction: 1]
    │       └──  6. f: q  ×            [t-negation: 4]
    └──  2. t: ~(~p)                   [t-conjunction: 0]
        └──  5. f: ~p                  [t-negation: 2]
            └──  7. t: p  ×            [f-negation: 5]
```
---

### Hypothetical Syllogism

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p -> q, q -> r |- p -> r
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((p -> q) & (q -> r)) & (~(p -> r))
    ├──  1. t: (p -> q) & (q -> r)             [t-conjunction: 0]
    │   ├──  3. t: p -> q                      [t-conjunction: 1]
    │   │   ├──  8. f: p  ×                    [t-implication: 3]
    │   │   └──  9. t: q  ×                    [t-implication: 3]
    │   └──  4. t: q -> r                      [t-conjunction: 1]
    │       ├── 10. f: q  ×                    [t-implication: 4]
    │       └── 11. t: r  ×                    [t-implication: 4]
    └──  2. t: ~(p -> r)                       [t-conjunction: 0]
        └──  5. f: p -> r                      [t-negation: 2]
            ├──  6. t: p  ×                    [f-implication: 5]
            └──  7. f: r  ×                    [f-implication: 5]
```
---

### Disjunctive Syllogism

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p | q, ~p |- q
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((p | q) & (~p)) & (~q)
    ├──  1. t: (p | q) & (~p)      [t-conjunction: 0]
    │   ├──  3. t: p | q           [t-conjunction: 1]
    │   │   ├──  7. t: p  ×        [t-disjunction: 3]
    │   │   └──  8. t: q  ×        [t-disjunction: 3]
    │   └──  4. t: ~p              [t-conjunction: 1]
    │       └──  6. f: p  ×        [t-negation: 4]
    └──  2. t: ~q                  [t-conjunction: 0]
        └──  5. f: q  ×            [t-negation: 2]
```
---

### Simplification

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p & q |- p
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (p & q) & (~p)
    ├──  1. t: p & q      [t-conjunction: 0]
    │   ├──  3. t: p  ×   [t-conjunction: 1]
    │   └──  4. t: q  ×   [t-conjunction: 1]
    └──  2. t: ~p         [t-conjunction: 0]
        └──  5. f: p  ×   [t-negation: 2]
```
---

### Addition

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules p |- p | q
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: p & (~(p | q))
    ├──  1. t: p  ×         [t-conjunction: 0]
    └──  2. t: ~(p | q)     [t-conjunction: 0]
        └──  3. f: p | q    [t-negation: 2]
            └──  4. f: p  × [f-disjunction: 3]
```
---

### Contraposition

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules (p -> q) |- (~q -> ~p)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (p -> q) & (~((~q) -> (~p)))
    ├──  1. t: p -> q                   [t-conjunction: 0]
    │   ├──  8. f: p  ×                 [t-implication: 1]
    │   └──  9. t: q  ×                 [t-implication: 1]
    └──  2. t: ~((~q) -> (~p))          [t-conjunction: 0]
        └──  3. f: (~q) -> (~p)         [t-negation: 2]
            ├──  4. t: ~q               [f-implication: 3]
            │   └──  6. f: q  ×         [t-negation: 4]
            └──  5. f: ~p               [f-implication: 3]
                └──  7. t: p  ×         [f-negation: 5]
```
---

### Double Negation Elimination

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules ~~p |- p
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (~(~p)) & (~p)
    ├──  1. t: ~(~p)      [t-conjunction: 0]
    │   └──  3. f: ~p  ×  [t-negation: 1]
    └──  2. t: ~p  ×      [t-conjunction: 0]
```
---

## Classical Invalid Inferences

Standard fallacies that remain invalid

### Affirming the Consequent

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel p -> q, q |- p
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}

Tableau tree:
 0. t: ((p -> q) & q) & (~p)
    ├──  1. t: (p -> q) & q      [t-conjunction: 0]
    │   ├──  3. t: p -> q        [t-conjunction: 1]
    │   └──  4. t: q             [t-conjunction: 1]
    └──  2. t: ~p                [t-conjunction: 0]
        └──  5. f: p             [t-negation: 2]
```
---

### Denying the Antecedent

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel p -> q, ~p |- ~q
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}

Tableau tree:
 0. t: ((p -> q) & (~p)) & (~(~q))
    ├──  1. t: (p -> q) & (~p)         [t-conjunction: 0]
    │   ├──  3. t: p -> q              [t-conjunction: 1]
    │   └──  4. t: ~p                  [t-conjunction: 1]
    │       └──  6. f: p               [t-negation: 4]
    └──  2. t: ~(~q)                   [t-conjunction: 0]
        └──  5. f: ~q                  [t-negation: 2]
            └──  7. t: q               [f-negation: 5]
```
---

### Undistributed Middle

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {A(c_6)=t, B(c_6)=t, C(c_6)=f}

Tableau tree:
 0. t: ([∀X A(X)]B(X) & [∀Y C(Y)]B(Y)) & (~[∀Z A(Z)]C(Z))
    ├──  1. t: [∀X A(X)]B(X) & [∀Y C(Y)]B(Y)                  [t-conjunction: 0]
    │   ├──  3. t: [∀X A(X)]B(X)                              [t-conjunction: 1]
    │   │   ├──  8. f: A(c_6)                                 [t-restricted-forall: 3]
    │   │   └──  9. t: B(c_6)                                 [t-restricted-forall: 3]
    │   └──  4. t: [∀Y C(Y)]B(Y)                              [t-conjunction: 1]
    └──  2. t: ~[∀Z A(Z)]C(Z)                                 [t-conjunction: 0]
        └──  5. f: [∀Z A(Z)]C(Z)                              [t-negation: 2]
            ├──  6. t: A(c_6)                                 [f-restricted-forall: 5]
            └──  7. f: C(c_6)                                 [f-restricted-forall: 5]
```
---

## Restricted Quantification

The wKrQ restricted quantifier system

### Valid Universal Instantiation

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)
```

**Output:**
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

### Invalid Existential to Universal (THE BUG WE FIXED)

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)
```

**Output:**
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

### Valid Existential Introduction

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules P(a), Q(a) |- [exists X P(X)]Q(X)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (P(a) & Q(a)) & (~[∃X P(X)]Q(X))
    ├──  1. t: P(a) & Q(a)                  [t-conjunction: 0]
    │   ├──  3. t: P(a)  ×                  [t-conjunction: 1]
    │   └──  4. t: Q(a)  ×                  [t-conjunction: 1]
    └──  2. t: ~[∃X P(X)]Q(X)               [t-conjunction: 0]
        └──  5. f: [∃X P(X)]Q(X)            [t-negation: 2]
            ├──  6. m: P(c_6)  ×            [f-restricted-exists: 5]
            ├──  7. m: Q(c_6)  ×            [f-restricted-exists: 5]
            ├──  8. n: P(a)  ×              [f-restricted-exists: 5]
            ├──  9. m: P(c_6)  ×            [f-restricted-exists: 5]
            ├── 10. m: Q(c_6)  ×            [f-restricted-exists: 5]
            └── 11. n: Q(a)  ×              [f-restricted-exists: 5]
```
---

### Invalid Existential Elimination

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X P(X)]Q(X), P(a) |- Q(a)
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {P(a)=t, P(c_6)=t, Q(a)=f, Q(c_6)=t}

Tableau tree:
 0. t: ([∃X P(X)]Q(X) & P(a)) & (~Q(a))
    ├──  1. t: [∃X P(X)]Q(X) & P(a)         [t-conjunction: 0]
    │   ├──  3. t: [∃X P(X)]Q(X)            [t-conjunction: 1]
    │   │   ├──  6. t: P(c_6)               [t-restricted-exists: 3]
    │   │   └──  7. t: Q(c_6)               [t-restricted-exists: 3]
    │   └──  4. t: P(a)                     [t-conjunction: 1]
    └──  2. t: ~Q(a)                        [t-conjunction: 0]
        └──  5. f: Q(a)                     [t-negation: 2]
```
---

## Quantifier Scoping and Complex Cases

Edge cases for restricted quantification showing scoping and variable interactions

### Nested quantifier instantiation

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X P(X)]Q(X) & [forall Y R(Y)]S(Y)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: [∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)
    ├──  1. t: [∀X P(X)]Q(X)             [t-conjunction: 0]
    │   ├──  3. f: P(c_3)                [t-restricted-forall: 1]
    │   └──  4. t: Q(c_3)                [t-restricted-forall: 1]
    └──  2. t: [∀Y R(Y)]S(Y)             [t-conjunction: 0]
        ├──  5. f: R(c_3)                [t-restricted-forall: 2]
        ├──  6. t: S(c_3)                [t-restricted-forall: 2]
        ├──  7. f: R(c_3)                [t-restricted-forall: 2]
        └──  8. t: S(c_3)                [t-restricted-forall: 2]
```
---

### Mixed quantifier interaction

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X P(X)]Q(X) & [exists Y R(Y)]S(Y)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: [∀X P(X)]Q(X) & [∃Y R(Y)]S(Y)
    ├──  1. t: [∀X P(X)]Q(X)             [t-conjunction: 0]
    │   ├──  5. f: P(c_3)                [t-restricted-forall: 1]
    │   └──  6. t: Q(c_3)                [t-restricted-forall: 1]
    └──  2. t: [∃Y R(Y)]S(Y)             [t-conjunction: 0]
        ├──  3. t: R(c_3)                [t-restricted-exists: 2]
        └──  4. t: S(c_3)                [t-restricted-exists: 2]
```
---

### Universal with existential premise

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X Human(X)]Mortal(X) & [exists Y Human(Y)]Smart(Y)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: [∀X Human(X)]Mortal(X) & [∃Y Human(Y)]Smart(Y)
    ├──  1. t: [∀X Human(X)]Mortal(X)                     [t-conjunction: 0]
    │   ├──  5. f: Human(c_3)                             [t-restricted-forall: 1]
    │   └──  6. t: Mortal(c_3)                            [t-restricted-forall: 1]
    └──  2. t: [∃Y Human(Y)]Smart(Y)                      [t-conjunction: 0]
        ├──  3. t: Human(c_3)                             [t-restricted-exists: 2]
        └──  4. t: Smart(c_3)                             [t-restricted-exists: 2]
```
---

### Quantifier scope interaction

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [exists X P(X)]Q(X), [forall Y Q(Y)]R(Y) |- [exists Z P(Z)]R(Z)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∃X P(X)]Q(X) & [∀Y Q(Y)]R(Y)) & (~[∃Z P(Z)]R(Z))
    ├──  1. t: [∃X P(X)]Q(X) & [∀Y Q(Y)]R(Y)                  [t-conjunction: 0]
    │   ├──  3. t: [∃X P(X)]Q(X)                              [t-conjunction: 1]
    │   │   ├──  6. t: P(c_6)  ×                              [t-restricted-exists: 3]
    │   │   └──  7. t: Q(c_6)  ×                              [t-restricted-exists: 3]
    │   └──  4. t: [∀Y Q(Y)]R(Y)                              [t-conjunction: 1]
    │       ├──  8. f: Q(c_6)  ×                              [t-restricted-forall: 4]
    │       └──  9. t: R(c_6)  ×                              [t-restricted-forall: 4]
    └──  2. t: ~[∃Z P(Z)]R(Z)                                 [t-conjunction: 0]
        └──  5. f: [∃Z P(Z)]R(Z)                              [t-negation: 2]
            ├── 10. m: P(c_9)  ×                              [f-restricted-exists: 5]
            ├── 11. m: R(c_9)  ×                              [f-restricted-exists: 5]
            ├── 12. n: P(c_6)  ×                              [f-restricted-exists: 5]
            ├── 13. m: P(c_9)  ×                              [f-restricted-exists: 5]
            ├── 14. m: R(c_9)  ×                              [f-restricted-exists: 5]
            └── 15. n: R(c_6)  ×                              [f-restricted-exists: 5]
```
---

### Quantifier alternation valid

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X P(X)]Q(X) |- [forall Y P(Y)]Q(Y)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: [∀X P(X)]Q(X) & (~[∀Y P(Y)]Q(Y))
    ├──  1. t: [∀X P(X)]Q(X)                [t-conjunction: 0]
    │   ├──  6. f: P(c_4)  ×                [t-restricted-forall: 1]
    │   └──  7. t: Q(c_4)  ×                [t-restricted-forall: 1]
    └──  2. t: ~[∀Y P(Y)]Q(Y)               [t-conjunction: 0]
        └──  3. f: [∀Y P(Y)]Q(Y)            [t-negation: 2]
            ├──  4. t: P(c_4)  ×            [f-restricted-forall: 3]
            └──  5. f: Q(c_4)  ×            [f-restricted-forall: 3]
```
---

### Quantifier alternation invalid

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X P(X)]Q(X) |- [exists Y P(Y)]R(Y)
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {P(c_3)=t, P(c_6)=t, Q(c_3)=t, R(c_3)=f, R(c_6)=t}

Tableau tree:
 0. t: [∃X P(X)]Q(X) & (~[∃Y P(Y)]R(Y))
    ├──  1. t: [∃X P(X)]Q(X)                [t-conjunction: 0]
    │   ├──  3. t: P(c_3)                   [t-restricted-exists: 1]
    │   └──  4. t: Q(c_3)                   [t-restricted-exists: 1]
    └──  2. t: ~[∃Y P(Y)]R(Y)               [t-conjunction: 0]
        └──  5. f: [∃Y P(Y)]R(Y)            [t-negation: 2]
            ├──  6. m: P(c_6)               [f-restricted-exists: 5]
            ├──  7. m: R(c_6)               [f-restricted-exists: 5]
            ├──  8. n: P(c_3)               [f-restricted-exists: 5]
            ├──  9. m: P(c_6)               [f-restricted-exists: 5]
            ├── 10. m: R(c_6)               [f-restricted-exists: 5]
            └── 11. n: R(c_3)               [f-restricted-exists: 5]
```
---

### Complex restriction interaction

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X (P(X) & Q(X))]R(X), P(a) & Q(a) |- R(a)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X P(X) & Q(X)]R(X) & (P(a) & Q(a))) & (~R(a))
    ├──  1. t: [∀X P(X) & Q(X)]R(X) & (P(a) & Q(a))         [t-conjunction: 0]
    │   ├──  3. t: [∀X P(X) & Q(X)]R(X)                     [t-conjunction: 1]
    │   │   ├──  8. f: P(a) & Q(a)  ×                       [t-restricted-forall: 3]
    │   │   └──  9. t: R(a)  ×                              [t-restricted-forall: 3]
    │   └──  4. t: P(a) & Q(a)                              [t-conjunction: 1]
    │       ├──  6. t: P(a)  ×                              [t-conjunction: 4]
    │       └──  7. t: Q(a)  ×                              [t-conjunction: 4]
    └──  2. t: ~R(a)                                        [t-conjunction: 0]
        └──  5. f: R(a)  ×                                  [t-negation: 2]
```
---

### Vacuous quantification

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X P(X)]Q(X) |- [forall Y ~P(Y)](Q(Y) | ~Q(Y))
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: [∀X P(X)]Q(X) & (~[∀Y ~P(Y)]Q(Y) | (~Q(Y)))
    ├──  1. t: [∀X P(X)]Q(X)  ×                        [t-conjunction: 0]
    └──  2. t: ~[∀Y ~P(Y)]Q(Y) | (~Q(Y))               [t-conjunction: 0]
        └──  3. f: [∀Y ~P(Y)]Q(Y) | (~Q(Y))            [t-negation: 2]
            ├──  4. t: ~P(c_4)                         [f-restricted-forall: 3]
            │   └──  6. f: P(c_4)  ×                   [t-negation: 4]
            └──  5. f: Q(c_4) | (~Q(c_4))              [f-restricted-forall: 3]
                ├──  7. f: Q(c_4)  ×                   [f-disjunction: 5]
                └──  8. f: ~Q(c_4)                     [f-disjunction: 5]
                    └──  9. t: Q(c_4)  ×               [f-negation: 8]
```
---

## Constant Generation and Witness Management

Tests stressing the constant generation mechanism and witness management

### Multiple existential witnesses

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X P(X)]Q(X), [exists Y R(Y)]S(Y) |- [exists Z P(Z)](Q(Z) & [exists W R(W)]S(W))
```

**Output:**
```
ERROR: Error: RestrictedExistentialFormula.__init__() takes 4 positional arguments but 5 were given

```
---

### Fresh constant generation test

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X P(X)]Q(X) |- [forall Y P(Y)]Q(Y)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: [∀X P(X)]Q(X) & (~[∀Y P(Y)]Q(Y))
    ├──  1. t: [∀X P(X)]Q(X)                [t-conjunction: 0]
    │   ├──  6. f: P(c_4)  ×                [t-restricted-forall: 1]
    │   └──  7. t: Q(c_4)  ×                [t-restricted-forall: 1]
    └──  2. t: ~[∀Y P(Y)]Q(Y)               [t-conjunction: 0]
        └──  3. f: [∀Y P(Y)]Q(Y)            [t-negation: 2]
            ├──  4. t: P(c_4)  ×            [f-restricted-forall: 3]
            └──  5. f: Q(c_4)  ×            [f-restricted-forall: 3]
```
---

### Witness independence

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X A(X)]B(X), [exists Y A(Y)]C(Y) |- [exists Z A(Z)](B(Z) & C(Z))
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=f, B(c_6)=t, B(c_8)=f, C(c_10)=e, C(c_8)=t}
  2. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=f, B(c_6)=t, B(c_8)=e, C(c_10)=e, C(c_8)=t}
  3. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=e, B(c_6)=t, B(c_8)=f, C(c_10)=f, C(c_8)=t}
  4. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=e, B(c_6)=t, B(c_8)=e, C(c_10)=f, C(c_8)=t}
  5. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=t, B(c_6)=t, B(c_8)=f, C(c_10)=t, C(c_8)=t}
  6. {A(c_10)=t, A(c_6)=t, A(c_8)=t, B(c_10)=t, B(c_6)=t, B(c_8)=e, C(c_10)=t, C(c_8)=t}

Tableau tree:
 0. t: ([∃X A(X)]B(X) & [∃Y A(Y)]C(Y)) & (~[∃Z A(Z)]B(Z) & C(Z))
    ├──  1. t: [∃X A(X)]B(X) & [∃Y A(Y)]C(Y)                         [t-conjunction: 0]
    │   ├──  3. t: [∃X A(X)]B(X)                                     [t-conjunction: 1]
    │   │   ├──  6. t: A(c_6)                                        [t-restricted-exists: 3]
    │   │   └──  7. t: B(c_6)                                        [t-restricted-exists: 3]
    │   └──  4. t: [∃Y A(Y)]C(Y)                                     [t-conjunction: 1]
    │       ├──  8. t: A(c_8)                                        [t-restricted-exists: 4]
    │       └──  9. t: C(c_8)                                        [t-restricted-exists: 4]
    └──  2. t: ~[∃Z A(Z)]B(Z) & C(Z)                                 [t-conjunction: 0]
        └──  5. f: [∃Z A(Z)]B(Z) & C(Z)                              [t-negation: 2]
            ├── 10. m: A(c_10)                                       [f-restricted-exists: 5]
            ├── 11. m: B(c_10) & C(c_10)                             [f-restricted-exists: 5]
            ├── 12. n: A(c_8)                                        [f-restricted-exists: 5]
            ├── 13. m: A(c_10)                                       [f-restricted-exists: 5]
            ├── 14. m: B(c_10) & C(c_10)                             [f-restricted-exists: 5]
            │   ├── 16. t: B(c_10)                                   [m-conjunction: 14]
            │   ├── 17. t: C(c_10)                                   [m-conjunction: 14]
            │   ├── 18. f: B(c_10)                                   [m-conjunction: 14]
            │   └── 19. f: C(c_10)                                   [m-conjunction: 14]
            └── 15. n: B(c_8) & C(c_8)                               [f-restricted-exists: 5]
                ├── 20. f: B(c_8)                                    [n-conjunction: 15]
                ├── 21. f: C(c_8)                                    [n-conjunction: 15]
                ├── 22. e: B(c_8)                                    [n-conjunction: 15]
                ├── 23. e: C(c_8)                                    [n-conjunction: 15]
                ├── 24. f: B(c_8)                                    [n-conjunction: 15]
                ├── 25. f: C(c_8)                                    [n-conjunction: 15]
                ├── 26. e: B(c_8)                                    [n-conjunction: 15]
                ├── 27. e: C(c_8)                                    [n-conjunction: 15]
                ├── 28. f: B(c_8)                                    [n-conjunction: 15]
                ├── 29. f: C(c_8)                                    [n-conjunction: 15]
                ├── 30. e: B(c_8)                                    [n-conjunction: 15]
                └── 31. e: C(c_8)                                    [n-conjunction: 15]
```
---

### Multiple universal instantiation

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X P(X)]Q(X) & [forall Y R(Y)]S(Y) & P(a) & R(a)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (([∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)) & P(a)) & R(a)
    ├──  1. t: ([∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)) & P(a)      [t-conjunction: 0]
    │   ├──  3. t: [∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)           [t-conjunction: 1]
    │   │   ├──  5. t: [∀X P(X)]Q(X)                       [t-conjunction: 3]
    │   │   │   ├──  7. f: P(a)                            [t-restricted-forall: 5]
    │   │   │   └──  8. t: Q(a)                            [t-restricted-forall: 5]
    │   │   └──  6. t: [∀Y R(Y)]S(Y)                       [t-conjunction: 3]
    │   │       ├──  9. f: R(a)                            [t-restricted-forall: 6]
    │   │       └── 10. t: S(a)                            [t-restricted-forall: 6]
    │   └──  4. t: P(a)                                    [t-conjunction: 1]
    └──  2. t: R(a)                                        [t-conjunction: 0]
```
---

### Existential witness limit

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [exists X P(X)]Q(X) & [exists Y R(Y)]S(Y) & [exists Z T(Z)]U(Z)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ([∃X P(X)]Q(X) & [∃Y R(Y)]S(Y)) & [∃Z T(Z)]U(Z)
    ├──  1. t: [∃X P(X)]Q(X) & [∃Y R(Y)]S(Y)               [t-conjunction: 0]
    │   ├──  3. t: [∃X P(X)]Q(X)                           [t-conjunction: 1]
    │   │   ├──  7. t: P(c_7)                              [t-restricted-exists: 3]
    │   │   └──  8. t: Q(c_7)                              [t-restricted-exists: 3]
    │   └──  4. t: [∃Y R(Y)]S(Y)                           [t-conjunction: 1]
    │       ├──  9. t: R(c_9)                              [t-restricted-exists: 4]
    │       └── 10. t: S(c_9)                              [t-restricted-exists: 4]
    └──  2. t: [∃Z T(Z)]U(Z)                               [t-conjunction: 0]
        ├──  5. t: T(c_5)                                  [t-restricted-exists: 2]
        └──  6. t: U(c_5)                                  [t-restricted-exists: 2]
```
---

### Universal chain

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X P(X)]Q(X), [forall Y Q(Y)]R(Y), P(a) |- R(a)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (([∀X P(X)]Q(X) & [∀Y Q(Y)]R(Y)) & P(a)) & (~R(a))
    ├──  1. t: ([∀X P(X)]Q(X) & [∀Y Q(Y)]R(Y)) & P(a)         [t-conjunction: 0]
    │   ├──  3. t: [∀X P(X)]Q(X) & [∀Y Q(Y)]R(Y)              [t-conjunction: 1]
    │   │   ├──  6. t: [∀X P(X)]Q(X)                          [t-conjunction: 3]
    │   │   │   ├──  8. f: P(a)  ×                            [t-restricted-forall: 6]
    │   │   │   └──  9. t: Q(a)  ×                            [t-restricted-forall: 6]
    │   │   └──  7. t: [∀Y Q(Y)]R(Y)                          [t-conjunction: 3]
    │   │       ├── 10. f: Q(a)  ×                            [t-restricted-forall: 7]
    │   │       └── 11. t: R(a)  ×                            [t-restricted-forall: 7]
    │   └──  4. t: P(a)  ×                                    [t-conjunction: 1]
    └──  2. t: ~R(a)                                          [t-conjunction: 0]
        └──  5. f: R(a)  ×                                    [t-negation: 2]
```
---

## Aristotelian Syllogisms

Traditional syllogistic forms with restricted quantifiers

### Barbara: All M are P, All S are M ⊢ All S are P

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X M(X)]P(X) & [∀Y S(Y)]M(Y)) & (~[∀Z S(Z)]P(Z))
    ├──  1. t: [∀X M(X)]P(X) & [∀Y S(Y)]M(Y)                  [t-conjunction: 0]
    │   ├──  3. t: [∀X M(X)]P(X)                              [t-conjunction: 1]
    │   │   ├──  8. f: M(c_6)  ×                              [t-restricted-forall: 3]
    │   │   └──  9. t: P(c_6)  ×                              [t-restricted-forall: 3]
    │   └──  4. t: [∀Y S(Y)]M(Y)                              [t-conjunction: 1]
    │       ├── 10. f: S(c_6)  ×                              [t-restricted-forall: 4]
    │       └── 11. t: M(c_6)  ×                              [t-restricted-forall: 4]
    └──  2. t: ~[∀Z S(Z)]P(Z)                                 [t-conjunction: 0]
        └──  5. f: [∀Z S(Z)]P(Z)                              [t-negation: 2]
            ├──  6. t: S(c_6)  ×                              [f-restricted-forall: 5]
            └──  7. f: P(c_6)  ×                              [f-restricted-forall: 5]
```
---

### Celarent: No M are P, All S are M ⊢ No S are P

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X M(X)]~P(X) & [∀Y S(Y)]M(Y)) & (~[∀Z S(Z)]~P(Z))
    ├──  1. t: [∀X M(X)]~P(X) & [∀Y S(Y)]M(Y)                   [t-conjunction: 0]
    │   ├──  3. t: [∀X M(X)]~P(X)                               [t-conjunction: 1]
    │   │   ├──  9. f: M(c_6)  ×                                [t-restricted-forall: 3]
    │   │   └── 10. t: ~P(c_6)  ×                               [t-restricted-forall: 3]
    │   └──  4. t: [∀Y S(Y)]M(Y)                                [t-conjunction: 1]
    │       ├── 11. f: S(c_6)  ×                                [t-restricted-forall: 4]
    │       └── 12. t: M(c_6)  ×                                [t-restricted-forall: 4]
    └──  2. t: ~[∀Z S(Z)]~P(Z)                                  [t-conjunction: 0]
        └──  5. f: [∀Z S(Z)]~P(Z)                               [t-negation: 2]
            ├──  6. t: S(c_6)  ×                                [f-restricted-forall: 5]
            └──  7. f: ~P(c_6)                                  [f-restricted-forall: 5]
                └──  8. t: P(c_6)  ×                            [f-negation: 7]
```
---

### Darii: All M are P, Some S are M ⊢ Some S are P

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X M(X)]P(X), [exists Y S(Y)]M(Y) |- [exists Z S(Z)]P(Z)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X M(X)]P(X) & [∃Y S(Y)]M(Y)) & (~[∃Z S(Z)]P(Z))
    ├──  1. t: [∀X M(X)]P(X) & [∃Y S(Y)]M(Y)                  [t-conjunction: 0]
    │   ├──  3. t: [∀X M(X)]P(X)                              [t-conjunction: 1]
    │   │   ├──  8. f: M(c_6)  ×                              [t-restricted-forall: 3]
    │   │   └──  9. t: P(c_6)  ×                              [t-restricted-forall: 3]
    │   └──  4. t: [∃Y S(Y)]M(Y)                              [t-conjunction: 1]
    │       ├──  6. t: S(c_6)  ×                              [t-restricted-exists: 4]
    │       └──  7. t: M(c_6)  ×                              [t-restricted-exists: 4]
    └──  2. t: ~[∃Z S(Z)]P(Z)                                 [t-conjunction: 0]
        └──  5. f: [∃Z S(Z)]P(Z)                              [t-negation: 2]
            ├── 10. m: S(c_9)  ×                              [f-restricted-exists: 5]
            ├── 11. m: P(c_9)  ×                              [f-restricted-exists: 5]
            ├── 12. n: S(c_6)  ×                              [f-restricted-exists: 5]
            ├── 13. m: S(c_9)  ×                              [f-restricted-exists: 5]
            ├── 14. m: P(c_9)  ×                              [f-restricted-exists: 5]
            └── 15. n: P(c_6)  ×                              [f-restricted-exists: 5]
```
---

### Ferio: No M are P, Some S are M ⊢ Some S are not P

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules [forall X M(X)](~P(X)), [exists Y S(Y)]M(Y) |- [exists Z S(Z)](~P(Z))
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ([∀X M(X)]~P(X) & [∃Y S(Y)]M(Y)) & (~[∃Z S(Z)]~P(Z))
    ├──  1. t: [∀X M(X)]~P(X) & [∃Y S(Y)]M(Y)                   [t-conjunction: 0]
    │   ├──  3. t: [∀X M(X)]~P(X)                               [t-conjunction: 1]
    │   │   ├──  8. f: M(c_6)  ×                                [t-restricted-forall: 3]
    │   │   └──  9. t: ~P(c_6)                                  [t-restricted-forall: 3]
    │   │       └── 10. f: P(c_6)  ×                            [t-negation: 9]
    │   └──  4. t: [∃Y S(Y)]M(Y)                                [t-conjunction: 1]
    │       ├──  6. t: S(c_6)  ×                                [t-restricted-exists: 4]
    │       └──  7. t: M(c_6)  ×                                [t-restricted-exists: 4]
    └──  2. t: ~[∃Z S(Z)]~P(Z)                                  [t-conjunction: 0]
        └──  5. f: [∃Z S(Z)]~P(Z)                               [t-negation: 2]
            ├── 11. m: S(c_10)  ×                               [f-restricted-exists: 5]
            ├── 12. m: ~P(c_10)  ×                              [f-restricted-exists: 5]
            ├── 13. n: S(c_6)  ×                                [f-restricted-exists: 5]
            ├── 14. m: S(c_10)  ×                               [f-restricted-exists: 5]
            ├── 15. m: ~P(c_10)  ×                              [f-restricted-exists: 5]
            └── 16. n: ~P(c_6)  ×                               [f-restricted-exists: 5]
```
---

## De Morgan's Laws

De Morgan equivalences in weak Kleene logic

### ¬(p ∧ q) ⊢ ¬p ∨ ¬q

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules ~(p & q) |- (~p | ~q)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (~(p & q)) & (~((~p) | (~q)))
    ├──  1. t: ~(p & q)                  [t-conjunction: 0]
    │   └──  3. f: p & q                 [t-negation: 1]
    │       ├──  9. f: p  ×              [f-conjunction: 3]
    │       ├── 10. f: q  ×              [f-conjunction: 3]
    │       ├── 11. e: p  ×              [f-conjunction: 3]
    │       └── 12. e: q  ×              [f-conjunction: 3]
    └──  2. t: ~((~p) | (~q))            [t-conjunction: 0]
        └──  4. f: (~p) | (~q)           [t-negation: 2]
            ├──  5. f: ~p                [f-disjunction: 4]
            │   └──  7. t: p  ×          [f-negation: 5]
            └──  6. f: ~q                [f-disjunction: 4]
                └──  8. t: q  ×          [f-negation: 6]
```
---

### ¬p ∨ ¬q ⊢ ¬(p ∧ q)

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules (~p | ~q) |- ~(p & q)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((~p) | (~q)) & (~(~(p & q)))
    ├──  1. t: (~p) | (~q)               [t-conjunction: 0]
    │   ├──  7. t: ~p                    [t-disjunction: 1]
    │   │   └──  9. f: p  ×              [t-negation: 7]
    │   └──  8. t: ~q                    [t-disjunction: 1]
    │       └── 10. f: q  ×              [t-negation: 8]
    └──  2. t: ~(~(p & q))               [t-conjunction: 0]
        └──  3. f: ~(p & q)              [t-negation: 2]
            └──  4. t: p & q             [f-negation: 3]
                ├──  5. t: p  ×          [t-conjunction: 4]
                └──  6. t: q  ×          [t-conjunction: 4]
```
---

### ¬(p ∨ q) ⊢ ¬p ∧ ¬q

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules ~(p | q) |- (~p & ~q)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (~(p | q)) & (~((~p) & (~q)))
    ├──  1. t: ~(p | q)                  [t-conjunction: 0]
    │   └──  3. f: p | q                 [t-negation: 1]
    │       ├──  5. f: p  ×              [f-disjunction: 3]
    │       └──  6. f: q  ×              [f-disjunction: 3]
    └──  2. t: ~((~p) & (~q))            [t-conjunction: 0]
        └──  4. f: (~p) & (~q)           [t-negation: 2]
            ├──  7. f: ~p                [f-conjunction: 4]
            │   └── 11. t: p  ×          [f-negation: 7]
            ├──  8. f: ~q                [f-conjunction: 4]
            │   └── 12. t: q  ×          [f-negation: 8]
            ├──  9. e: ~p                [f-conjunction: 4]
            │   └── 13. e: p  ×          [e-negation: 9]
            └── 10. e: ~q                [f-conjunction: 4]
                └── 14. e: q  ×          [e-negation: 10]
```
---

### ¬p ∧ ¬q ⊢ ¬(p ∨ q)

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules (~p & ~q) |- ~(p | q)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((~p) & (~q)) & (~(~(p | q)))
    ├──  1. t: (~p) & (~q)               [t-conjunction: 0]
    │   ├──  3. t: ~p                    [t-conjunction: 1]
    │   │   └──  6. f: p  ×              [t-negation: 3]
    │   └──  4. t: ~q                    [t-conjunction: 1]
    │       └──  7. f: q  ×              [t-negation: 4]
    └──  2. t: ~(~(p | q))               [t-conjunction: 0]
        └──  5. f: ~(p | q)              [t-negation: 2]
            └──  8. t: p | q             [f-negation: 5]
                ├──  9. t: p  ×          [t-disjunction: 8]
                └── 10. t: q  ×          [t-disjunction: 8]
```
---

### Quantified De Morgan

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules ~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: (~[∀X Domain(X)]P(X)) & (~[∃Y Domain(Y)]~P(Y))
    ├──  1. t: ~[∀X Domain(X)]P(X)                        [t-conjunction: 0]
    │   └──  3. f: [∀X Domain(X)]P(X)                     [t-negation: 1]
    │       ├──  5. t: Domain(c_5)  ×                     [f-restricted-forall: 3]
    │       └──  6. f: P(c_5)  ×                          [f-restricted-forall: 3]
    └──  2. t: ~[∃Y Domain(Y)]~P(Y)                       [t-conjunction: 0]
        └──  4. f: [∃Y Domain(Y)]~P(Y)                    [t-negation: 2]
            ├──  7. m: Domain(c_7)  ×                     [f-restricted-exists: 4]
            ├──  8. m: ~P(c_7)  ×                         [f-restricted-exists: 4]
            ├──  9. n: Domain(c_5)  ×                     [f-restricted-exists: 4]
            ├── 10. m: Domain(c_7)  ×                     [f-restricted-exists: 4]
            ├── 11. m: ~P(c_7)                            [f-restricted-exists: 4]
            │   ├── 13. f: P(c_7)  ×                      [m-negation: 11]
            │   └── 14. t: P(c_7)  ×                      [m-negation: 11]
            └── 12. n: ~P(c_5)                            [f-restricted-exists: 4]
                ├── 15. t: P(c_5)  ×                      [n-negation: 12]
                ├── 16. e: P(c_5)  ×                      [n-negation: 12]
                ├── 17. t: P(c_5)  ×                      [n-negation: 12]
                └── 18. e: P(c_5)  ×                      [n-negation: 12]
```
---

## Tableau Rule Application and Proof Structure

Examples demonstrating rule application order and proof completeness

### Rule order independence for conjunction

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p & q) & (r & s)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (p & q) & (r & s)
    ├──  1. t: p & q         [t-conjunction: 0]
    │   ├──  3. t: p         [t-conjunction: 1]
    │   └──  4. t: q         [t-conjunction: 1]
    └──  2. t: r & s         [t-conjunction: 0]
        ├──  5. t: r         [t-conjunction: 2]
        └──  6. t: s         [t-conjunction: 2]
```
---

### Branching order for disjunction

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p | q) | (r | s)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (p | q) | (r | s)
    ├──  1. t: p | q         [t-disjunction: 0]
    │   ├──  3. t: p         [t-disjunction: 1]
    │   └──  4. t: q         [t-disjunction: 1]
    └──  2. t: r | s         [t-disjunction: 0]
        ├──  5. t: r         [t-disjunction: 2]
        └──  6. t: s         [t-disjunction: 2]
```
---

### Mixed connectives rule application

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p & q) | (r -> s)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (p & q) | (r -> s)
    ├──  1. t: p & q          [t-disjunction: 0]
    │   ├──  3. t: p          [t-conjunction: 1]
    │   └──  4. t: q          [t-conjunction: 1]
    └──  2. t: r -> s         [t-disjunction: 0]
        ├──  5. f: r          [t-implication: 2]
        └──  6. t: s          [t-implication: 2]
```
---

### Negation elimination timing

**CLI Command:**
```bash
python -m wkrq --tree --show-rules ~(~p & ~q)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ~((~p) & (~q))
    └──  1. f: (~p) & (~q) [t-negation: 0]
        ├──  2. f: ~p      [f-conjunction: 1]
        │   └──  6. t: p   [f-negation: 2]
        ├──  3. f: ~q      [f-conjunction: 1]
        │   └──  7. t: q   [f-negation: 3]
        ├──  4. e: ~p      [f-conjunction: 1]
        │   └──  8. e: p   [e-negation: 4]
        └──  5. e: ~q      [f-conjunction: 1]
            └──  9. e: q   [e-negation: 5]
```
---

### Quantifier instantiation order

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X P(X)]Q(X) & [forall Y R(Y)]S(Y) & P(a) & R(a)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (([∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)) & P(a)) & R(a)
    ├──  1. t: ([∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)) & P(a)      [t-conjunction: 0]
    │   ├──  3. t: [∀X P(X)]Q(X) & [∀Y R(Y)]S(Y)           [t-conjunction: 1]
    │   │   ├──  5. t: [∀X P(X)]Q(X)                       [t-conjunction: 3]
    │   │   │   ├──  7. f: P(a)                            [t-restricted-forall: 5]
    │   │   │   └──  8. t: Q(a)                            [t-restricted-forall: 5]
    │   │   └──  6. t: [∀Y R(Y)]S(Y)                       [t-conjunction: 3]
    │   │       ├──  9. f: R(a)                            [t-restricted-forall: 6]
    │   │       └── 10. t: S(a)                            [t-restricted-forall: 6]
    │   └──  4. t: P(a)                                    [t-conjunction: 1]
    └──  2. t: R(a)                                        [t-conjunction: 0]
```
---

### Multiple valid proof paths

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p -> q) & (q -> r) & p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ((p -> q) & (q -> r)) & p
    ├──  1. t: (p -> q) & (q -> r)   [t-conjunction: 0]
    │   ├──  3. t: p -> q            [t-conjunction: 1]
    │   │   ├──  5. f: p             [t-implication: 3]
    │   │   └──  6. t: q             [t-implication: 3]
    │   └──  4. t: q -> r            [t-conjunction: 1]
    │       ├──  7. f: q             [t-implication: 4]
    │       └──  8. t: r             [t-implication: 4]
    └──  2. t: p                     [t-conjunction: 0]
```
---

### Early vs late branching

**CLI Command:**
```bash
python -m wkrq --tree --show-rules ((p | q) -> r) & (p | q)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ((p | q) -> r) & (p | q)
    ├──  1. t: (p | q) -> r         [t-conjunction: 0]
    │   ├──  3. f: p | q            [t-implication: 1]
    │   └──  4. t: r                [t-implication: 1]
    └──  2. t: p | q                [t-conjunction: 0]
        ├──  5. t: p                [t-disjunction: 2]
        └──  6. t: q                [t-disjunction: 2]
```
---

## Three-Valued Model Construction

Examples showing model extraction with all three truth values

### Model with all three values

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models (p & q) | r
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {p=t, q=t, r=e}
  2. {p=e, q=e, r=t}

Tableau tree:
 0. t: (p & q) | r
    ├──  1. t: p & q   [t-disjunction: 0]
    │   ├──  3. t: p   [t-conjunction: 1]
    │   └──  4. t: q   [t-conjunction: 1]
    └──  2. t: r       [t-disjunction: 0]
```
---

### Models satisfying with undefined

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules --models p -> q
```

**Output:**
```
Satisfiable: True
Models (3):
  1. {p=f, q=e}
  2. {p=e, q=t}
  3. {p=t, q=f}

Tableau tree:
 0. m: p -> q
    ├──  1. f: p  [m-implication: 0]
    ├──  2. t: q  [m-implication: 0]
    ├──  3. t: p  [m-implication: 0]
    └──  4. f: q  [m-implication: 0]
```
---

### Undefined-only satisfaction

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models (p & ~p) | (q & ~q)
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p=e, q=e}

Tableau tree:
 0. e: (p & (~p)) | (q & (~q))
    ├──  1. e: p & (~p)            [e-disjunction: 0]
    │   ├──  3. e: p               [e-conjunction: 1]
    │   └──  4. e: ~p              [e-conjunction: 1]
    └──  2. e: q & (~q)            [e-disjunction: 0]
        ├──  5. e: q               [e-conjunction: 2]
        └──  6. e: ~q              [e-conjunction: 2]
```
---

### Mixed truth values in quantified formulas

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models [exists X P(X)](Q(X) | R(X))
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {P(c_1)=t, Q(c_1)=t, R(c_1)=e}
  2. {P(c_1)=t, Q(c_1)=e, R(c_1)=t}

Tableau tree:
 0. t: [∃X P(X)]Q(X) | R(X)
    ├──  1. t: P(c_1)           [t-restricted-exists: 0]
    └──  2. t: Q(c_1) | R(c_1)  [t-restricted-exists: 0]
        ├──  3. t: Q(c_1)       [t-disjunction: 2]
        └──  4. t: R(c_1)       [t-disjunction: 2]
```
---

### Model minimality demonstration

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models p | q | r
```

**Output:**
```
Satisfiable: True
Models (3):
  1. {p=e, q=e, r=t}
  2. {p=t, q=e, r=e}
  3. {p=e, q=t, r=e}

Tableau tree:
 0. t: (p | q) | r
    ├──  1. t: p | q   [t-disjunction: 0]
    │   ├──  3. t: p   [t-disjunction: 1]
    │   └──  4. t: q   [t-disjunction: 1]
    └──  2. t: r       [t-disjunction: 0]
```
---

### Witnesses with undefined predicates

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules --models [exists X P(X)](Q(X) & ~Q(X))
```

**Output:**
```
Satisfiable: True
Models (2):
  1. {P(c_1)=e}
  2. {Q(c_1)=e}

Tableau tree:
 0. e: [∃X P(X)]Q(X) & (~Q(X))
    ├──  1. e: P(c_1)              [e-restricted-exists: 0]
    └──  2. e: Q(c_1) & (~Q(c_1))  [e-restricted-exists: 0]
```
---

### Complex model with multiple witnesses

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [exists X P(X)]Q(X) & [exists Y R(Y)]S(Y)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: [∃X P(X)]Q(X) & [∃Y R(Y)]S(Y)
    ├──  1. t: [∃X P(X)]Q(X)             [t-conjunction: 0]
    │   ├──  3. t: P(c_3)                [t-restricted-exists: 1]
    │   └──  4. t: Q(c_3)                [t-restricted-exists: 1]
    └──  2. t: [∃Y R(Y)]S(Y)             [t-conjunction: 0]
        ├──  5. t: R(c_5)                [t-restricted-exists: 2]
        └──  6. t: S(c_5)                [t-restricted-exists: 2]
```
---

## Tableau System Properties

Branch closure and tableau construction

### Branch closes on t:p and f:p

**CLI Command:**
```bash
python -m wkrq --tree --show-rules p & ~p
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. t: p & (~p)
    ├──  1. t: p  ×     [t-conjunction: 0]
    └──  2. t: ~p       [t-conjunction: 0]
        └──  3. f: p  × [t-negation: 2]
```
---

### Branch closes on t:p and e:p

**CLI Command:**
```bash
python -m wkrq --sign=e --tree --show-rules p & ~p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. e: p & (~p)
    ├──  1. e: p    [e-conjunction: 0]
    └──  2. e: ~p   [e-conjunction: 0]
```
---

### Branch closes on f:p and e:p

**CLI Command:**
```bash
python -m wkrq --sign=f --tree --show-rules p | ~p
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. f: p | (~p)
    ├──  1. f: p  ×     [f-disjunction: 0]
    └──  2. f: ~p       [f-disjunction: 0]
        └──  3. t: p  × [f-negation: 2]
```
---

### M-sign creates meaningful branches

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: p
```
---

### N-sign creates non-true branches

**CLI Command:**
```bash
python -m wkrq --sign=n --tree --show-rules p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. n: p
```
---

## ACrQ Paraconsistent Logic

Bilateral predicates and paraconsistent reasoning

### Knowledge gluts don't explode

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --inference --tree --show-rules --countermodel P(a) & P*(a) |- Q(b)
```

**Output:**
```
ACrQ Inference (bilateral mode):
  Premises: P(a) & P*(a)
  Conclusion: Q(b)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t, Q(b)=f}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. f: Q(b)
    ├──  2. t: P(a)     [t-conjunction: 0]
    └──  3. t: P*(a)    [t-conjunction: 0]
```
---

### Local inconsistency preserved

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models P(a) & P*(a)
```

**Output:**
```
ACrQ Formula (bilateral mode): P(a) & P*(a)
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=t, P*(a)=t}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. t: P(a)     [t-conjunction: 0]
    └──  2. t: P*(a)    [t-conjunction: 0]
```
---

### Reasoning continues despite gluts

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --inference --tree --show-rules P(a) & P*(a), P(a) -> Q(a) |- Q(a)
```

**Output:**
```
ACrQ Inference (bilateral mode):
  Premises: P(a) & P*(a), P(a) -> Q(a)
  Conclusion: Q(a)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t, Q(a)=f}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. t: P(a) -> Q(a)
    ├──  2. f: Q(a)
    ├──  3. t: P(a)         [t-conjunction: 0]
    └──  4. t: P*(a)        [t-conjunction: 0]
```
---

### De Morgan with bilateral predicates

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --inference --tree --show-rules ~(P(a) & Q(a)) |- (~P(a) | ~Q(a))
```

**Output:**
```
ERROR: Parse error: Negated predicates are not allowed in bilateral mode. Use explicit star syntax: P* instead of ¬P

```
---

## ACrQ Glut and Gap Complex Interactions

Complex scenarios with knowledge gluts and gaps

### Glut propagation through conjunction

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models (P(a) & P*(a)) & Q(a)
```

**Output:**
```
ACrQ Formula (bilateral mode): (P(a) & P*(a)) & Q(a)
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=e, P*(a)=e, Q(a)=t}

Tableau tree:
 0. t: (P(a) & P*(a)) & Q(a)
    ├──  1. t: P(a) & P*(a)      [t-conjunction: 0]
    └──  2. t: Q(a)              [t-conjunction: 0]
```
---

### Gap handling in disjunction

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models P(a) | P*(a)
```

**Output:**
```
ACrQ Formula (bilateral mode): P(a) | P*(a)
Sign: t
Satisfiable: True

Models (3):
  1. {P(a)=t, P*(a)=t}
  2. {P(a)=e, P*(a)=t}
  3. {P(a)=t, P*(a)=e}

Tableau tree:
 0. t: P(a) | P*(a)
    ├──  1. t: P(a)     [t-disjunction: 0]
    ├──  2. t: P*(a)    [t-disjunction: 0]
    ├──  3. t: P*(a)    [t-disjunction: 0]
    ├──  4. t: P(a)     [t-disjunction: 0]
    ├──  5. t: P*(a)    [t-disjunction: 0]
    ├──  6. t: P(a)     [t-disjunction: 0]
    ├──  7. t: P*(a)    [t-disjunction: 0]
    ├──  8. t: P(a)     [t-disjunction: 0]
    ├──  9. t: P*(a)    [t-disjunction: 0]
    ├── 10. t: P(a)     [t-disjunction: 0]
    ├── 11. t: P*(a)    [t-disjunction: 0]
    ├── 12. t: P(a)     [t-disjunction: 0]
    ├── 13. t: P*(a)    [t-disjunction: 0]
    ├── 14. t: P(a)     [t-disjunction: 0]
    ├── 15. t: P*(a)    [t-disjunction: 0]
    ├── 16. t: P(a)     [t-disjunction: 0]
    ├── 17. t: P*(a)    [t-disjunction: 0]
    ├── 18. t: P(a)     [t-disjunction: 0]
    ├── 19. t: P*(a)    [t-disjunction: 0]
    ├── 20. t: P(a)     [t-disjunction: 0]
    ├── 21. t: P*(a)    [t-disjunction: 0]
    ├── 22. t: P(a)     [t-disjunction: 0]
    ├── 23. t: P*(a)    [t-disjunction: 0]
    ├── 24. t: P(a)     [t-disjunction: 0]
    ├── 25. t: P*(a)    [t-disjunction: 0]
    ├── 26. t: P(a)     [t-disjunction: 0]
    ├── 27. t: P*(a)    [t-disjunction: 0]
    ├── 28. t: P(a)     [t-disjunction: 0]
    ├── 29. t: P*(a)    [t-disjunction: 0]
    ├── 30. t: P(a)     [t-disjunction: 0]
    ├── 31. t: P*(a)    [t-disjunction: 0]
    ├── 32. t: P(a)     [t-disjunction: 0]
    ├── 33. t: P*(a)    [t-disjunction: 0]
    ├── 34. t: P(a)     [t-disjunction: 0]
    ├── 35. t: P*(a)    [t-disjunction: 0]
    ├── 36. t: P(a)     [t-disjunction: 0]
    ├── 37. t: P*(a)    [t-disjunction: 0]
    ├── 38. t: P(a)     [t-disjunction: 0]
    ├── 39. t: P*(a)    [t-disjunction: 0]
    ├── 40. t: P(a)     [t-disjunction: 0]
    ├── 41. t: P*(a)    [t-disjunction: 0]
    ├── 42. t: P(a)     [t-disjunction: 0]
    ├── 43. t: P*(a)    [t-disjunction: 0]
    ├── 44. t: P(a)     [t-disjunction: 0]
    ├── 45. t: P*(a)    [t-disjunction: 0]
    ├── 46. t: P(a)     [t-disjunction: 0]
    ├── 47. t: P*(a)    [t-disjunction: 0]
    ├── 48. t: P(a)     [t-disjunction: 0]
    ├── 49. t: P*(a)    [t-disjunction: 0]
    ├── 50. t: P(a)     [t-disjunction: 0]
    ├── 51. t: P*(a)    [t-disjunction: 0]
    ├── 52. t: P(a)     [t-disjunction: 0]
    ├── 53. t: P*(a)    [t-disjunction: 0]
    ├── 54. t: P(a)     [t-disjunction: 0]
    ├── 55. t: P*(a)    [t-disjunction: 0]
    ├── 56. t: P(a)     [t-disjunction: 0]
    ├── 57. t: P*(a)    [t-disjunction: 0]
    ├── 58. t: P(a)     [t-disjunction: 0]
    ├── 59. t: P*(a)    [t-disjunction: 0]
    ├── 60. t: P(a)     [t-disjunction: 0]
    ├── 61. t: P*(a)    [t-disjunction: 0]
    ├── 62. t: P(a)     [t-disjunction: 0]
    ├── 63. t: P*(a)    [t-disjunction: 0]
    ├── 64. t: P(a)     [t-disjunction: 0]
    ├── 65. t: P*(a)    [t-disjunction: 0]
    ├── 66. t: P(a)     [t-disjunction: 0]
    ├── 67. t: P*(a)    [t-disjunction: 0]
    ├── 68. t: P(a)     [t-disjunction: 0]
    ├── 69. t: P*(a)    [t-disjunction: 0]
    ├── 70. t: P(a)     [t-disjunction: 0]
    ├── 71. t: P*(a)    [t-disjunction: 0]
    ├── 72. t: P(a)     [t-disjunction: 0]
    ├── 73. t: P*(a)    [t-disjunction: 0]
    ├── 74. t: P(a)     [t-disjunction: 0]
    ├── 75. t: P*(a)    [t-disjunction: 0]
    ├── 76. t: P(a)     [t-disjunction: 0]
    ├── 77. t: P*(a)    [t-disjunction: 0]
    ├── 78. t: P(a)     [t-disjunction: 0]
    ├── 79. t: P*(a)    [t-disjunction: 0]
    ├── 80. t: P(a)     [t-disjunction: 0]
    ├── 81. t: P*(a)    [t-disjunction: 0]
    ├── 82. t: P(a)     [t-disjunction: 0]
    ├── 83. t: P*(a)    [t-disjunction: 0]
    ├── 84. t: P(a)     [t-disjunction: 0]
    ├── 85. t: P*(a)    [t-disjunction: 0]
    ├── 86. t: P(a)     [t-disjunction: 0]
    ├── 87. t: P*(a)    [t-disjunction: 0]
    ├── 88. t: P(a)     [t-disjunction: 0]
    ├── 89. t: P*(a)    [t-disjunction: 0]
    ├── 90. t: P(a)     [t-disjunction: 0]
    ├── 91. t: P*(a)    [t-disjunction: 0]
    ├── 92. t: P(a)     [t-disjunction: 0]
    ├── 93. t: P*(a)    [t-disjunction: 0]
    ├── 94. t: P(a)     [t-disjunction: 0]
    ├── 95. t: P*(a)    [t-disjunction: 0]
    ├── 96. t: P(a)     [t-disjunction: 0]
    ├── 97. t: P*(a)    [t-disjunction: 0]
    ├── 98. t: P(a)     [t-disjunction: 0]
    ├── 99. t: P*(a)    [t-disjunction: 0]
    ├── 100. t: P(a)    [t-disjunction: 0]
    ├── 101. t: P*(a)   [t-disjunction: 0]
    ├── 102. t: P(a)    [t-disjunction: 0]
    ├── 103. t: P*(a)   [t-disjunction: 0]
    ├── 104. t: P(a)    [t-disjunction: 0]
    ├── 105. t: P*(a)   [t-disjunction: 0]
    ├── 106. t: P(a)    [t-disjunction: 0]
    ├── 107. t: P*(a)   [t-disjunction: 0]
    ├── 108. t: P(a)    [t-disjunction: 0]
    ├── 109. t: P*(a)   [t-disjunction: 0]
    ├── 110. t: P(a)    [t-disjunction: 0]
    ├── 111. t: P*(a)   [t-disjunction: 0]
    ├── 112. t: P(a)    [t-disjunction: 0]
    ├── 113. t: P*(a)   [t-disjunction: 0]
    ├── 114. t: P(a)    [t-disjunction: 0]
    ├── 115. t: P*(a)   [t-disjunction: 0]
    ├── 116. t: P(a)    [t-disjunction: 0]
    ├── 117. t: P*(a)   [t-disjunction: 0]
    ├── 118. t: P(a)    [t-disjunction: 0]
    ├── 119. t: P*(a)   [t-disjunction: 0]
    ├── 120. t: P(a)    [t-disjunction: 0]
    ├── 121. t: P*(a)   [t-disjunction: 0]
    ├── 122. t: P(a)    [t-disjunction: 0]
    ├── 123. t: P*(a)   [t-disjunction: 0]
    ├── 124. t: P(a)    [t-disjunction: 0]
    ├── 125. t: P*(a)   [t-disjunction: 0]
    ├── 126. t: P(a)    [t-disjunction: 0]
    ├── 127. t: P*(a)   [t-disjunction: 0]
    ├── 128. t: P(a)    [t-disjunction: 0]
    ├── 129. t: P*(a)   [t-disjunction: 0]
    ├── 130. t: P(a)    [t-disjunction: 0]
    ├── 131. t: P*(a)   [t-disjunction: 0]
    ├── 132. t: P(a)    [t-disjunction: 0]
    ├── 133. t: P*(a)   [t-disjunction: 0]
    ├── 134. t: P(a)    [t-disjunction: 0]
    ├── 135. t: P*(a)   [t-disjunction: 0]
    ├── 136. t: P(a)    [t-disjunction: 0]
    ├── 137. t: P*(a)   [t-disjunction: 0]
    ├── 138. t: P(a)    [t-disjunction: 0]
    ├── 139. t: P*(a)   [t-disjunction: 0]
    ├── 140. t: P(a)    [t-disjunction: 0]
    ├── 141. t: P*(a)   [t-disjunction: 0]
    ├── 142. t: P(a)    [t-disjunction: 0]
    ├── 143. t: P*(a)   [t-disjunction: 0]
    ├── 144. t: P(a)    [t-disjunction: 0]
    ├── 145. t: P*(a)   [t-disjunction: 0]
    ├── 146. t: P(a)    [t-disjunction: 0]
    ├── 147. t: P*(a)   [t-disjunction: 0]
    ├── 148. t: P(a)    [t-disjunction: 0]
    ├── 149. t: P*(a)   [t-disjunction: 0]
    ├── 150. t: P(a)    [t-disjunction: 0]
    ├── 151. t: P*(a)   [t-disjunction: 0]
    ├── 152. t: P(a)    [t-disjunction: 0]
    ├── 153. t: P*(a)   [t-disjunction: 0]
    ├── 154. t: P(a)    [t-disjunction: 0]
    ├── 155. t: P*(a)   [t-disjunction: 0]
    ├── 156. t: P(a)    [t-disjunction: 0]
    ├── 157. t: P*(a)   [t-disjunction: 0]
    ├── 158. t: P(a)    [t-disjunction: 0]
    ├── 159. t: P*(a)   [t-disjunction: 0]
    ├── 160. t: P(a)    [t-disjunction: 0]
    ├── 161. t: P*(a)   [t-disjunction: 0]
    ├── 162. t: P(a)    [t-disjunction: 0]
    ├── 163. t: P*(a)   [t-disjunction: 0]
    ├── 164. t: P(a)    [t-disjunction: 0]
    ├── 165. t: P*(a)   [t-disjunction: 0]
    ├── 166. t: P(a)    [t-disjunction: 0]
    ├── 167. t: P*(a)   [t-disjunction: 0]
    ├── 168. t: P(a)    [t-disjunction: 0]
    ├── 169. t: P*(a)   [t-disjunction: 0]
    ├── 170. t: P(a)    [t-disjunction: 0]
    ├── 171. t: P*(a)   [t-disjunction: 0]
    ├── 172. t: P(a)    [t-disjunction: 0]
    ├── 173. t: P*(a)   [t-disjunction: 0]
    ├── 174. t: P(a)    [t-disjunction: 0]
    ├── 175. t: P*(a)   [t-disjunction: 0]
    ├── 176. t: P(a)    [t-disjunction: 0]
    ├── 177. t: P*(a)   [t-disjunction: 0]
    ├── 178. t: P(a)    [t-disjunction: 0]
    ├── 179. t: P*(a)   [t-disjunction: 0]
    ├── 180. t: P(a)    [t-disjunction: 0]
    ├── 181. t: P*(a)   [t-disjunction: 0]
    ├── 182. t: P(a)    [t-disjunction: 0]
    ├── 183. t: P*(a)   [t-disjunction: 0]
    ├── 184. t: P(a)    [t-disjunction: 0]
    ├── 185. t: P*(a)   [t-disjunction: 0]
    ├── 186. t: P(a)    [t-disjunction: 0]
    ├── 187. t: P*(a)   [t-disjunction: 0]
    ├── 188. t: P(a)    [t-disjunction: 0]
    ├── 189. t: P*(a)   [t-disjunction: 0]
    ├── 190. t: P(a)    [t-disjunction: 0]
    ├── 191. t: P*(a)   [t-disjunction: 0]
    ├── 192. t: P(a)    [t-disjunction: 0]
    ├── 193. t: P*(a)   [t-disjunction: 0]
    ├── 194. t: P(a)    [t-disjunction: 0]
    ├── 195. t: P*(a)   [t-disjunction: 0]
    ├── 196. t: P(a)    [t-disjunction: 0]
    ├── 197. t: P*(a)   [t-disjunction: 0]
    ├── 198. t: P(a)    [t-disjunction: 0]
    ├── 199. t: P*(a)   [t-disjunction: 0]
    ├── 200. t: P(a)    [t-disjunction: 0]
    ├── 201. t: P*(a)   [t-disjunction: 0]
    ├── 202. t: P(a)    [t-disjunction: 0]
    ├── 203. t: P*(a)   [t-disjunction: 0]
    ├── 204. t: P(a)    [t-disjunction: 0]
    ├── 205. t: P*(a)   [t-disjunction: 0]
    ├── 206. t: P(a)    [t-disjunction: 0]
    ├── 207. t: P*(a)   [t-disjunction: 0]
    ├── 208. t: P(a)    [t-disjunction: 0]
    ├── 209. t: P*(a)   [t-disjunction: 0]
    ├── 210. t: P(a)    [t-disjunction: 0]
    ├── 211. t: P*(a)   [t-disjunction: 0]
    ├── 212. t: P(a)    [t-disjunction: 0]
    ├── 213. t: P*(a)   [t-disjunction: 0]
    ├── 214. t: P(a)    [t-disjunction: 0]
    ├── 215. t: P*(a)   [t-disjunction: 0]
    ├── 216. t: P(a)    [t-disjunction: 0]
    ├── 217. t: P*(a)   [t-disjunction: 0]
    ├── 218. t: P(a)    [t-disjunction: 0]
    ├── 219. t: P*(a)   [t-disjunction: 0]
    ├── 220. t: P(a)    [t-disjunction: 0]
    ├── 221. t: P*(a)   [t-disjunction: 0]
    ├── 222. t: P(a)    [t-disjunction: 0]
    ├── 223. t: P*(a)   [t-disjunction: 0]
    ├── 224. t: P(a)    [t-disjunction: 0]
    ├── 225. t: P*(a)   [t-disjunction: 0]
    ├── 226. t: P(a)    [t-disjunction: 0]
    ├── 227. t: P*(a)   [t-disjunction: 0]
    ├── 228. t: P(a)    [t-disjunction: 0]
    ├── 229. t: P*(a)   [t-disjunction: 0]
    ├── 230. t: P(a)    [t-disjunction: 0]
    ├── 231. t: P*(a)   [t-disjunction: 0]
    ├── 232. t: P(a)    [t-disjunction: 0]
    ├── 233. t: P*(a)   [t-disjunction: 0]
    ├── 234. t: P(a)    [t-disjunction: 0]
    ├── 235. t: P*(a)   [t-disjunction: 0]
    ├── 236. t: P(a)    [t-disjunction: 0]
    ├── 237. t: P*(a)   [t-disjunction: 0]
    ├── 238. t: P(a)    [t-disjunction: 0]
    ├── 239. t: P*(a)   [t-disjunction: 0]
    ├── 240. t: P(a)    [t-disjunction: 0]
    ├── 241. t: P*(a)   [t-disjunction: 0]
    ├── 242. t: P(a)    [t-disjunction: 0]
    ├── 243. t: P*(a)   [t-disjunction: 0]
    ├── 244. t: P(a)    [t-disjunction: 0]
    ├── 245. t: P*(a)   [t-disjunction: 0]
    ├── 246. t: P(a)    [t-disjunction: 0]
    ├── 247. t: P*(a)   [t-disjunction: 0]
    ├── 248. t: P(a)    [t-disjunction: 0]
    ├── 249. t: P*(a)   [t-disjunction: 0]
    ├── 250. t: P(a)    [t-disjunction: 0]
    ├── 251. t: P*(a)   [t-disjunction: 0]
    ├── 252. t: P(a)    [t-disjunction: 0]
    ├── 253. t: P*(a)   [t-disjunction: 0]
    ├── 254. t: P(a)    [t-disjunction: 0]
    ├── 255. t: P*(a)   [t-disjunction: 0]
    ├── 256. t: P(a)    [t-disjunction: 0]
    ├── 257. t: P*(a)   [t-disjunction: 0]
    ├── 258. t: P(a)    [t-disjunction: 0]
    ├── 259. t: P*(a)   [t-disjunction: 0]
    ├── 260. t: P(a)    [t-disjunction: 0]
    ├── 261. t: P*(a)   [t-disjunction: 0]
    ├── 262. t: P(a)    [t-disjunction: 0]
    ├── 263. t: P*(a)   [t-disjunction: 0]
    ├── 264. t: P(a)    [t-disjunction: 0]
    ├── 265. t: P*(a)   [t-disjunction: 0]
    ├── 266. t: P(a)    [t-disjunction: 0]
    ├── 267. t: P*(a)   [t-disjunction: 0]
    ├── 268. t: P(a)    [t-disjunction: 0]
    ├── 269. t: P*(a)   [t-disjunction: 0]
    ├── 270. t: P(a)    [t-disjunction: 0]
    ├── 271. t: P*(a)   [t-disjunction: 0]
    ├── 272. t: P(a)    [t-disjunction: 0]
    ├── 273. t: P*(a)   [t-disjunction: 0]
    ├── 274. t: P(a)    [t-disjunction: 0]
    ├── 275. t: P*(a)   [t-disjunction: 0]
    ├── 276. t: P(a)    [t-disjunction: 0]
    ├── 277. t: P*(a)   [t-disjunction: 0]
    ├── 278. t: P(a)    [t-disjunction: 0]
    ├── 279. t: P*(a)   [t-disjunction: 0]
    ├── 280. t: P(a)    [t-disjunction: 0]
    ├── 281. t: P*(a)   [t-disjunction: 0]
    ├── 282. t: P(a)    [t-disjunction: 0]
    ├── 283. t: P*(a)   [t-disjunction: 0]
    ├── 284. t: P(a)    [t-disjunction: 0]
    ├── 285. t: P*(a)   [t-disjunction: 0]
    ├── 286. t: P(a)    [t-disjunction: 0]
    ├── 287. t: P*(a)   [t-disjunction: 0]
    ├── 288. t: P(a)    [t-disjunction: 0]
    ├── 289. t: P*(a)   [t-disjunction: 0]
    ├── 290. t: P(a)    [t-disjunction: 0]
    ├── 291. t: P*(a)   [t-disjunction: 0]
    ├── 292. t: P(a)    [t-disjunction: 0]
    ├── 293. t: P*(a)   [t-disjunction: 0]
    ├── 294. t: P(a)    [t-disjunction: 0]
    ├── 295. t: P*(a)   [t-disjunction: 0]
    ├── 296. t: P(a)    [t-disjunction: 0]
    ├── 297. t: P*(a)   [t-disjunction: 0]
    ├── 298. t: P(a)    [t-disjunction: 0]
    ├── 299. t: P*(a)   [t-disjunction: 0]
    ├── 300. t: P(a)    [t-disjunction: 0]
    ├── 301. t: P*(a)   [t-disjunction: 0]
    ├── 302. t: P(a)    [t-disjunction: 0]
    ├── 303. t: P*(a)   [t-disjunction: 0]
    ├── 304. t: P(a)    [t-disjunction: 0]
    ├── 305. t: P*(a)   [t-disjunction: 0]
    ├── 306. t: P(a)    [t-disjunction: 0]
    ├── 307. t: P*(a)   [t-disjunction: 0]
    ├── 308. t: P(a)    [t-disjunction: 0]
    ├── 309. t: P*(a)   [t-disjunction: 0]
    ├── 310. t: P(a)    [t-disjunction: 0]
    ├── 311. t: P*(a)   [t-disjunction: 0]
    ├── 312. t: P(a)    [t-disjunction: 0]
    ├── 313. t: P*(a)   [t-disjunction: 0]
    ├── 314. t: P(a)    [t-disjunction: 0]
    ├── 315. t: P*(a)   [t-disjunction: 0]
    ├── 316. t: P(a)    [t-disjunction: 0]
    ├── 317. t: P*(a)   [t-disjunction: 0]
    ├── 318. t: P(a)    [t-disjunction: 0]
    ├── 319. t: P*(a)   [t-disjunction: 0]
    ├── 320. t: P(a)    [t-disjunction: 0]
    ├── 321. t: P*(a)   [t-disjunction: 0]
    ├── 322. t: P(a)    [t-disjunction: 0]
    ├── 323. t: P*(a)   [t-disjunction: 0]
    ├── 324. t: P(a)    [t-disjunction: 0]
    ├── 325. t: P*(a)   [t-disjunction: 0]
    ├── 326. t: P(a)    [t-disjunction: 0]
    ├── 327. t: P*(a)   [t-disjunction: 0]
    ├── 328. t: P(a)    [t-disjunction: 0]
    ├── 329. t: P*(a)   [t-disjunction: 0]
    ├── 330. t: P(a)    [t-disjunction: 0]
    ├── 331. t: P*(a)   [t-disjunction: 0]
    ├── 332. t: P(a)    [t-disjunction: 0]
    ├── 333. t: P*(a)   [t-disjunction: 0]
    ├── 334. t: P(a)    [t-disjunction: 0]
    ├── 335. t: P*(a)   [t-disjunction: 0]
    ├── 336. t: P(a)    [t-disjunction: 0]
    ├── 337. t: P*(a)   [t-disjunction: 0]
    ├── 338. t: P(a)    [t-disjunction: 0]
    ├── 339. t: P*(a)   [t-disjunction: 0]
    ├── 340. t: P(a)    [t-disjunction: 0]
    ├── 341. t: P*(a)   [t-disjunction: 0]
    ├── 342. t: P(a)    [t-disjunction: 0]
    ├── 343. t: P*(a)   [t-disjunction: 0]
    ├── 344. t: P(a)    [t-disjunction: 0]
    ├── 345. t: P*(a)   [t-disjunction: 0]
    ├── 346. t: P(a)    [t-disjunction: 0]
    ├── 347. t: P*(a)   [t-disjunction: 0]
    ├── 348. t: P(a)    [t-disjunction: 0]
    ├── 349. t: P*(a)   [t-disjunction: 0]
    ├── 350. t: P(a)    [t-disjunction: 0]
    ├── 351. t: P*(a)   [t-disjunction: 0]
    ├── 352. t: P(a)    [t-disjunction: 0]
    ├── 353. t: P*(a)   [t-disjunction: 0]
    ├── 354. t: P(a)    [t-disjunction: 0]
    ├── 355. t: P*(a)   [t-disjunction: 0]
    ├── 356. t: P(a)    [t-disjunction: 0]
    ├── 357. t: P*(a)   [t-disjunction: 0]
    ├── 358. t: P(a)    [t-disjunction: 0]
    ├── 359. t: P*(a)   [t-disjunction: 0]
    ├── 360. t: P(a)    [t-disjunction: 0]
    ├── 361. t: P*(a)   [t-disjunction: 0]
    ├── 362. t: P(a)    [t-disjunction: 0]
    ├── 363. t: P*(a)   [t-disjunction: 0]
    ├── 364. t: P(a)    [t-disjunction: 0]
    ├── 365. t: P*(a)   [t-disjunction: 0]
    ├── 366. t: P(a)    [t-disjunction: 0]
    ├── 367. t: P*(a)   [t-disjunction: 0]
    ├── 368. t: P(a)    [t-disjunction: 0]
    ├── 369. t: P*(a)   [t-disjunction: 0]
    ├── 370. t: P(a)    [t-disjunction: 0]
    ├── 371. t: P*(a)   [t-disjunction: 0]
    ├── 372. t: P(a)    [t-disjunction: 0]
    ├── 373. t: P*(a)   [t-disjunction: 0]
    ├── 374. t: P(a)    [t-disjunction: 0]
    ├── 375. t: P*(a)   [t-disjunction: 0]
    ├── 376. t: P(a)    [t-disjunction: 0]
    ├── 377. t: P*(a)   [t-disjunction: 0]
    ├── 378. t: P(a)    [t-disjunction: 0]
    ├── 379. t: P*(a)   [t-disjunction: 0]
    ├── 380. t: P(a)    [t-disjunction: 0]
    ├── 381. t: P*(a)   [t-disjunction: 0]
    ├── 382. t: P(a)    [t-disjunction: 0]
    ├── 383. t: P*(a)   [t-disjunction: 0]
    ├── 384. t: P(a)    [t-disjunction: 0]
    ├── 385. t: P*(a)   [t-disjunction: 0]
    ├── 386. t: P(a)    [t-disjunction: 0]
    ├── 387. t: P*(a)   [t-disjunction: 0]
    ├── 388. t: P(a)    [t-disjunction: 0]
    ├── 389. t: P*(a)   [t-disjunction: 0]
    ├── 390. t: P(a)    [t-disjunction: 0]
    ├── 391. t: P*(a)   [t-disjunction: 0]
    ├── 392. t: P(a)    [t-disjunction: 0]
    ├── 393. t: P*(a)   [t-disjunction: 0]
    ├── 394. t: P(a)    [t-disjunction: 0]
    ├── 395. t: P*(a)   [t-disjunction: 0]
    ├── 396. t: P(a)    [t-disjunction: 0]
    ├── 397. t: P*(a)   [t-disjunction: 0]
    ├── 398. t: P(a)    [t-disjunction: 0]
    ├── 399. t: P*(a)   [t-disjunction: 0]
    ├── 400. t: P(a)    [t-disjunction: 0]
    ├── 401. t: P*(a)   [t-disjunction: 0]
    ├── 402. t: P(a)    [t-disjunction: 0]
    ├── 403. t: P*(a)   [t-disjunction: 0]
    ├── 404. t: P(a)    [t-disjunction: 0]
    ├── 405. t: P*(a)   [t-disjunction: 0]
    ├── 406. t: P(a)    [t-disjunction: 0]
    ├── 407. t: P*(a)   [t-disjunction: 0]
    ├── 408. t: P(a)    [t-disjunction: 0]
    ├── 409. t: P*(a)   [t-disjunction: 0]
    ├── 410. t: P(a)    [t-disjunction: 0]
    ├── 411. t: P*(a)   [t-disjunction: 0]
    ├── 412. t: P(a)    [t-disjunction: 0]
    ├── 413. t: P*(a)   [t-disjunction: 0]
    ├── 414. t: P(a)    [t-disjunction: 0]
    ├── 415. t: P*(a)   [t-disjunction: 0]
    ├── 416. t: P(a)    [t-disjunction: 0]
    ├── 417. t: P*(a)   [t-disjunction: 0]
    ├── 418. t: P(a)    [t-disjunction: 0]
    ├── 419. t: P*(a)   [t-disjunction: 0]
    ├── 420. t: P(a)    [t-disjunction: 0]
    ├── 421. t: P*(a)   [t-disjunction: 0]
    ├── 422. t: P(a)    [t-disjunction: 0]
    ├── 423. t: P*(a)   [t-disjunction: 0]
    ├── 424. t: P(a)    [t-disjunction: 0]
    ├── 425. t: P*(a)   [t-disjunction: 0]
    ├── 426. t: P(a)    [t-disjunction: 0]
    ├── 427. t: P*(a)   [t-disjunction: 0]
    ├── 428. t: P(a)    [t-disjunction: 0]
    ├── 429. t: P*(a)   [t-disjunction: 0]
    ├── 430. t: P(a)    [t-disjunction: 0]
    ├── 431. t: P*(a)   [t-disjunction: 0]
    ├── 432. t: P(a)    [t-disjunction: 0]
    ├── 433. t: P*(a)   [t-disjunction: 0]
    ├── 434. t: P(a)    [t-disjunction: 0]
    ├── 435. t: P*(a)   [t-disjunction: 0]
    ├── 436. t: P(a)    [t-disjunction: 0]
    ├── 437. t: P*(a)   [t-disjunction: 0]
    ├── 438. t: P(a)    [t-disjunction: 0]
    ├── 439. t: P*(a)   [t-disjunction: 0]
    ├── 440. t: P(a)    [t-disjunction: 0]
    ├── 441. t: P*(a)   [t-disjunction: 0]
    ├── 442. t: P(a)    [t-disjunction: 0]
    ├── 443. t: P*(a)   [t-disjunction: 0]
    ├── 444. t: P(a)    [t-disjunction: 0]
    ├── 445. t: P*(a)   [t-disjunction: 0]
    ├── 446. t: P(a)    [t-disjunction: 0]
    ├── 447. t: P*(a)   [t-disjunction: 0]
    ├── 448. t: P(a)    [t-disjunction: 0]
    ├── 449. t: P*(a)   [t-disjunction: 0]
    ├── 450. t: P(a)    [t-disjunction: 0]
    ├── 451. t: P*(a)   [t-disjunction: 0]
    ├── 452. t: P(a)    [t-disjunction: 0]
    ├── 453. t: P*(a)   [t-disjunction: 0]
    ├── 454. t: P(a)    [t-disjunction: 0]
    ├── 455. t: P*(a)   [t-disjunction: 0]
    ├── 456. t: P(a)    [t-disjunction: 0]
    ├── 457. t: P*(a)   [t-disjunction: 0]
    ├── 458. t: P(a)    [t-disjunction: 0]
    ├── 459. t: P*(a)   [t-disjunction: 0]
    ├── 460. t: P(a)    [t-disjunction: 0]
    ├── 461. t: P*(a)   [t-disjunction: 0]
    ├── 462. t: P(a)    [t-disjunction: 0]
    ├── 463. t: P*(a)   [t-disjunction: 0]
    ├── 464. t: P(a)    [t-disjunction: 0]
    ├── 465. t: P*(a)   [t-disjunction: 0]
    ├── 466. t: P(a)    [t-disjunction: 0]
    ├── 467. t: P*(a)   [t-disjunction: 0]
    ├── 468. t: P(a)    [t-disjunction: 0]
    ├── 469. t: P*(a)   [t-disjunction: 0]
    ├── 470. t: P(a)    [t-disjunction: 0]
    ├── 471. t: P*(a)   [t-disjunction: 0]
    ├── 472. t: P(a)    [t-disjunction: 0]
    ├── 473. t: P*(a)   [t-disjunction: 0]
    ├── 474. t: P(a)    [t-disjunction: 0]
    ├── 475. t: P*(a)   [t-disjunction: 0]
    ├── 476. t: P(a)    [t-disjunction: 0]
    ├── 477. t: P*(a)   [t-disjunction: 0]
    ├── 478. t: P(a)    [t-disjunction: 0]
    ├── 479. t: P*(a)   [t-disjunction: 0]
    ├── 480. t: P(a)    [t-disjunction: 0]
    ├── 481. t: P*(a)   [t-disjunction: 0]
    ├── 482. t: P(a)    [t-disjunction: 0]
    ├── 483. t: P*(a)   [t-disjunction: 0]
    ├── 484. t: P(a)    [t-disjunction: 0]
    ├── 485. t: P*(a)   [t-disjunction: 0]
    ├── 486. t: P(a)    [t-disjunction: 0]
    ├── 487. t: P*(a)   [t-disjunction: 0]
    ├── 488. t: P(a)    [t-disjunction: 0]
    ├── 489. t: P*(a)   [t-disjunction: 0]
    ├── 490. t: P(a)    [t-disjunction: 0]
    ├── 491. t: P*(a)   [t-disjunction: 0]
    ├── 492. t: P(a)    [t-disjunction: 0]
    ├── 493. t: P*(a)   [t-disjunction: 0]
    ├── 494. t: P(a)    [t-disjunction: 0]
    ├── 495. t: P*(a)   [t-disjunction: 0]
    ├── 496. t: P(a)    [t-disjunction: 0]
    ├── 497. t: P*(a)   [t-disjunction: 0]
    ├── 498. t: P(a)    [t-disjunction: 0]
    ├── 499. t: P*(a)   [t-disjunction: 0]
    ├── 500. t: P(a)    [t-disjunction: 0]
    └── 501. t: P*(a)   [t-disjunction: 0]
```
---

### Mixed gluts and gaps

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models (P(a) & P*(a)) | (Q(b) | Q*(b))
```

**Output:**
```
ACrQ Formula (bilateral mode): (P(a) & P*(a)) | (Q(b) | Q*(b))
Sign: t
Satisfiable: True

Models (2):
  1. {P(a)=t, P*(a)=t, Q(b)=e, Q*(b)=e}
  2. {P(a)=e, P*(a)=e, Q(b)=e, Q*(b)=e}

Tableau tree:
 0. t: (P(a) & P*(a)) | (Q(b) | Q*(b))
    ├──  1. t: P(a) & P*(a)                [t-disjunction: 0]
    │   ├──  3. t: P(a)                    [t-conjunction: 1]
    │   └──  4. t: P*(a)                   [t-conjunction: 1]
    ├──  2. t: Q(b) | Q*(b)                [t-disjunction: 0]
    ├──  5. t: P(a) & P*(a)                [t-disjunction: 0]
    ├──  6. t: P(a) & P*(a)                [t-disjunction: 0]
    ├──  7. t: P(a) & P*(a)                [t-disjunction: 0]
    ├──  8. t: P(a) & P*(a)                [t-disjunction: 0]
    ├──  9. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 10. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 11. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 12. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 13. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 14. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 15. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 16. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 17. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 18. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 19. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 20. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 21. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 22. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 23. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 24. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 25. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 26. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 27. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 28. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 29. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 30. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 31. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 32. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 33. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 34. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 35. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 36. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 37. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 38. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 39. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 40. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 41. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 42. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 43. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 44. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 45. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 46. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 47. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 48. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 49. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 50. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 51. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 52. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 53. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 54. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 55. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 56. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 57. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 58. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 59. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 60. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 61. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 62. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 63. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 64. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 65. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 66. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 67. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 68. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 69. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 70. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 71. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 72. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 73. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 74. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 75. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 76. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 77. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 78. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 79. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 80. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 81. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 82. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 83. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 84. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 85. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 86. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 87. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 88. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 89. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 90. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 91. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 92. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 93. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 94. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 95. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 96. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 97. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 98. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 99. t: P(a) & P*(a)                [t-disjunction: 0]
    ├── 100. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 101. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 102. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 103. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 104. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 105. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 106. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 107. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 108. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 109. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 110. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 111. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 112. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 113. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 114. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 115. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 116. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 117. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 118. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 119. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 120. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 121. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 122. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 123. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 124. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 125. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 126. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 127. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 128. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 129. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 130. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 131. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 132. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 133. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 134. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 135. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 136. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 137. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 138. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 139. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 140. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 141. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 142. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 143. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 144. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 145. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 146. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 147. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 148. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 149. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 150. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 151. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 152. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 153. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 154. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 155. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 156. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 157. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 158. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 159. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 160. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 161. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 162. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 163. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 164. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 165. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 166. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 167. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 168. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 169. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 170. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 171. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 172. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 173. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 174. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 175. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 176. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 177. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 178. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 179. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 180. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 181. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 182. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 183. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 184. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 185. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 186. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 187. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 188. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 189. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 190. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 191. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 192. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 193. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 194. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 195. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 196. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 197. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 198. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 199. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 200. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 201. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 202. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 203. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 204. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 205. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 206. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 207. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 208. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 209. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 210. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 211. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 212. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 213. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 214. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 215. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 216. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 217. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 218. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 219. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 220. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 221. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 222. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 223. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 224. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 225. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 226. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 227. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 228. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 229. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 230. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 231. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 232. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 233. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 234. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 235. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 236. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 237. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 238. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 239. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 240. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 241. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 242. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 243. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 244. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 245. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 246. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 247. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 248. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 249. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 250. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 251. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 252. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 253. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 254. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 255. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 256. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 257. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 258. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 259. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 260. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 261. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 262. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 263. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 264. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 265. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 266. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 267. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 268. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 269. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 270. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 271. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 272. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 273. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 274. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 275. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 276. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 277. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 278. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 279. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 280. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 281. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 282. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 283. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 284. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 285. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 286. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 287. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 288. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 289. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 290. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 291. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 292. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 293. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 294. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 295. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 296. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 297. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 298. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 299. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 300. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 301. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 302. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 303. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 304. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 305. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 306. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 307. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 308. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 309. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 310. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 311. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 312. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 313. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 314. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 315. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 316. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 317. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 318. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 319. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 320. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 321. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 322. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 323. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 324. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 325. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 326. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 327. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 328. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 329. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 330. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 331. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 332. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 333. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 334. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 335. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 336. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 337. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 338. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 339. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 340. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 341. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 342. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 343. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 344. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 345. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 346. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 347. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 348. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 349. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 350. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 351. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 352. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 353. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 354. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 355. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 356. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 357. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 358. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 359. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 360. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 361. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 362. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 363. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 364. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 365. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 366. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 367. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 368. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 369. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 370. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 371. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 372. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 373. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 374. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 375. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 376. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 377. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 378. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 379. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 380. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 381. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 382. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 383. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 384. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 385. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 386. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 387. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 388. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 389. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 390. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 391. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 392. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 393. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 394. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 395. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 396. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 397. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 398. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 399. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 400. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 401. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 402. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 403. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 404. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 405. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 406. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 407. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 408. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 409. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 410. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 411. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 412. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 413. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 414. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 415. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 416. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 417. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 418. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 419. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 420. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 421. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 422. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 423. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 424. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 425. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 426. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 427. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 428. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 429. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 430. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 431. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 432. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 433. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 434. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 435. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 436. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 437. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 438. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 439. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 440. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 441. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 442. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 443. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 444. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 445. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 446. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 447. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 448. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 449. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 450. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 451. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 452. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 453. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 454. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 455. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 456. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 457. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 458. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 459. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 460. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 461. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 462. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 463. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 464. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 465. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 466. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 467. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 468. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 469. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 470. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 471. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 472. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 473. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 474. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 475. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 476. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 477. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 478. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 479. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 480. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 481. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 482. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 483. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 484. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 485. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 486. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 487. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 488. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 489. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 490. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 491. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 492. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 493. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 494. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 495. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 496. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 497. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 498. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 499. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 500. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 501. t: P(a) & P*(a)               [t-disjunction: 0]
    ├── 502. t: P(a) & P*(a)               [t-disjunction: 0]
    └── 503. t: P(a) & P*(a)               [t-disjunction: 0]
```
---

### Glut in antecedent

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models (P(a) & P*(a)) -> Q(a)
```

**Output:**
```
ACrQ Formula (bilateral mode): (P(a) & P*(a)) -> Q(a)
Sign: t
Satisfiable: True

Models (2):
  1. {P(a)=e, P*(a)=e, Q(a)=t}
  2. {P(a)=e, P*(a)=e, Q(a)=e}

Tableau tree:
 0. t: (P(a) & P*(a)) -> Q(a)
    ├──  1. f: P(a) & P*(a)       [t-implication: 0]
    ├──  2. t: Q(a)               [t-implication: 0]
    ├──  3. t: Q(a)               [t-implication: 0]
    ├──  4. f: P(a) & P*(a)       [t-implication: 0]
    ├──  5. t: Q(a)               [t-implication: 0]
    ├──  6. f: P(a) & P*(a)       [t-implication: 0]
    ├──  7. t: Q(a)               [t-implication: 0]
    ├──  8. f: P(a) & P*(a)       [t-implication: 0]
    ├──  9. t: Q(a)               [t-implication: 0]
    ├── 10. f: P(a) & P*(a)       [t-implication: 0]
    ├── 11. t: Q(a)               [t-implication: 0]
    ├── 12. f: P(a) & P*(a)       [t-implication: 0]
    ├── 13. t: Q(a)               [t-implication: 0]
    ├── 14. f: P(a) & P*(a)       [t-implication: 0]
    ├── 15. t: Q(a)               [t-implication: 0]
    ├── 16. f: P(a) & P*(a)       [t-implication: 0]
    ├── 17. t: Q(a)               [t-implication: 0]
    ├── 18. f: P(a) & P*(a)       [t-implication: 0]
    ├── 19. t: Q(a)               [t-implication: 0]
    ├── 20. f: P(a) & P*(a)       [t-implication: 0]
    ├── 21. t: Q(a)               [t-implication: 0]
    ├── 22. f: P(a) & P*(a)       [t-implication: 0]
    ├── 23. t: Q(a)               [t-implication: 0]
    ├── 24. f: P(a) & P*(a)       [t-implication: 0]
    ├── 25. t: Q(a)               [t-implication: 0]
    ├── 26. f: P(a) & P*(a)       [t-implication: 0]
    ├── 27. t: Q(a)               [t-implication: 0]
    ├── 28. f: P(a) & P*(a)       [t-implication: 0]
    ├── 29. t: Q(a)               [t-implication: 0]
    ├── 30. f: P(a) & P*(a)       [t-implication: 0]
    ├── 31. t: Q(a)               [t-implication: 0]
    ├── 32. f: P(a) & P*(a)       [t-implication: 0]
    ├── 33. t: Q(a)               [t-implication: 0]
    ├── 34. f: P(a) & P*(a)       [t-implication: 0]
    ├── 35. t: Q(a)               [t-implication: 0]
    ├── 36. f: P(a) & P*(a)       [t-implication: 0]
    ├── 37. t: Q(a)               [t-implication: 0]
    ├── 38. f: P(a) & P*(a)       [t-implication: 0]
    ├── 39. t: Q(a)               [t-implication: 0]
    ├── 40. f: P(a) & P*(a)       [t-implication: 0]
    ├── 41. t: Q(a)               [t-implication: 0]
    ├── 42. f: P(a) & P*(a)       [t-implication: 0]
    ├── 43. t: Q(a)               [t-implication: 0]
    ├── 44. f: P(a) & P*(a)       [t-implication: 0]
    ├── 45. t: Q(a)               [t-implication: 0]
    ├── 46. f: P(a) & P*(a)       [t-implication: 0]
    ├── 47. t: Q(a)               [t-implication: 0]
    ├── 48. f: P(a) & P*(a)       [t-implication: 0]
    ├── 49. t: Q(a)               [t-implication: 0]
    ├── 50. f: P(a) & P*(a)       [t-implication: 0]
    ├── 51. t: Q(a)               [t-implication: 0]
    ├── 52. f: P(a) & P*(a)       [t-implication: 0]
    ├── 53. t: Q(a)               [t-implication: 0]
    ├── 54. f: P(a) & P*(a)       [t-implication: 0]
    ├── 55. t: Q(a)               [t-implication: 0]
    ├── 56. f: P(a) & P*(a)       [t-implication: 0]
    ├── 57. t: Q(a)               [t-implication: 0]
    ├── 58. f: P(a) & P*(a)       [t-implication: 0]
    ├── 59. t: Q(a)               [t-implication: 0]
    ├── 60. f: P(a) & P*(a)       [t-implication: 0]
    ├── 61. t: Q(a)               [t-implication: 0]
    ├── 62. f: P(a) & P*(a)       [t-implication: 0]
    ├── 63. t: Q(a)               [t-implication: 0]
    ├── 64. f: P(a) & P*(a)       [t-implication: 0]
    ├── 65. t: Q(a)               [t-implication: 0]
    ├── 66. f: P(a) & P*(a)       [t-implication: 0]
    ├── 67. t: Q(a)               [t-implication: 0]
    ├── 68. f: P(a) & P*(a)       [t-implication: 0]
    ├── 69. t: Q(a)               [t-implication: 0]
    ├── 70. f: P(a) & P*(a)       [t-implication: 0]
    ├── 71. t: Q(a)               [t-implication: 0]
    ├── 72. f: P(a) & P*(a)       [t-implication: 0]
    ├── 73. t: Q(a)               [t-implication: 0]
    ├── 74. f: P(a) & P*(a)       [t-implication: 0]
    ├── 75. t: Q(a)               [t-implication: 0]
    ├── 76. f: P(a) & P*(a)       [t-implication: 0]
    ├── 77. t: Q(a)               [t-implication: 0]
    ├── 78. f: P(a) & P*(a)       [t-implication: 0]
    ├── 79. t: Q(a)               [t-implication: 0]
    ├── 80. f: P(a) & P*(a)       [t-implication: 0]
    ├── 81. t: Q(a)               [t-implication: 0]
    ├── 82. f: P(a) & P*(a)       [t-implication: 0]
    ├── 83. t: Q(a)               [t-implication: 0]
    ├── 84. f: P(a) & P*(a)       [t-implication: 0]
    ├── 85. t: Q(a)               [t-implication: 0]
    ├── 86. f: P(a) & P*(a)       [t-implication: 0]
    ├── 87. t: Q(a)               [t-implication: 0]
    ├── 88. f: P(a) & P*(a)       [t-implication: 0]
    ├── 89. t: Q(a)               [t-implication: 0]
    ├── 90. f: P(a) & P*(a)       [t-implication: 0]
    ├── 91. t: Q(a)               [t-implication: 0]
    ├── 92. f: P(a) & P*(a)       [t-implication: 0]
    ├── 93. t: Q(a)               [t-implication: 0]
    ├── 94. f: P(a) & P*(a)       [t-implication: 0]
    ├── 95. t: Q(a)               [t-implication: 0]
    ├── 96. f: P(a) & P*(a)       [t-implication: 0]
    ├── 97. t: Q(a)               [t-implication: 0]
    ├── 98. f: P(a) & P*(a)       [t-implication: 0]
    ├── 99. t: Q(a)               [t-implication: 0]
    ├── 100. f: P(a) & P*(a)      [t-implication: 0]
    ├── 101. t: Q(a)              [t-implication: 0]
    ├── 102. f: P(a) & P*(a)      [t-implication: 0]
    ├── 103. t: Q(a)              [t-implication: 0]
    ├── 104. f: P(a) & P*(a)      [t-implication: 0]
    ├── 105. t: Q(a)              [t-implication: 0]
    ├── 106. f: P(a) & P*(a)      [t-implication: 0]
    ├── 107. t: Q(a)              [t-implication: 0]
    ├── 108. f: P(a) & P*(a)      [t-implication: 0]
    ├── 109. t: Q(a)              [t-implication: 0]
    ├── 110. f: P(a) & P*(a)      [t-implication: 0]
    ├── 111. t: Q(a)              [t-implication: 0]
    ├── 112. f: P(a) & P*(a)      [t-implication: 0]
    ├── 113. t: Q(a)              [t-implication: 0]
    ├── 114. f: P(a) & P*(a)      [t-implication: 0]
    ├── 115. t: Q(a)              [t-implication: 0]
    ├── 116. f: P(a) & P*(a)      [t-implication: 0]
    ├── 117. t: Q(a)              [t-implication: 0]
    ├── 118. f: P(a) & P*(a)      [t-implication: 0]
    ├── 119. t: Q(a)              [t-implication: 0]
    ├── 120. f: P(a) & P*(a)      [t-implication: 0]
    ├── 121. t: Q(a)              [t-implication: 0]
    ├── 122. f: P(a) & P*(a)      [t-implication: 0]
    ├── 123. t: Q(a)              [t-implication: 0]
    ├── 124. f: P(a) & P*(a)      [t-implication: 0]
    ├── 125. t: Q(a)              [t-implication: 0]
    ├── 126. f: P(a) & P*(a)      [t-implication: 0]
    ├── 127. t: Q(a)              [t-implication: 0]
    ├── 128. f: P(a) & P*(a)      [t-implication: 0]
    ├── 129. t: Q(a)              [t-implication: 0]
    ├── 130. f: P(a) & P*(a)      [t-implication: 0]
    ├── 131. t: Q(a)              [t-implication: 0]
    ├── 132. f: P(a) & P*(a)      [t-implication: 0]
    ├── 133. t: Q(a)              [t-implication: 0]
    ├── 134. f: P(a) & P*(a)      [t-implication: 0]
    ├── 135. t: Q(a)              [t-implication: 0]
    ├── 136. f: P(a) & P*(a)      [t-implication: 0]
    ├── 137. t: Q(a)              [t-implication: 0]
    ├── 138. f: P(a) & P*(a)      [t-implication: 0]
    ├── 139. t: Q(a)              [t-implication: 0]
    ├── 140. f: P(a) & P*(a)      [t-implication: 0]
    ├── 141. t: Q(a)              [t-implication: 0]
    ├── 142. f: P(a) & P*(a)      [t-implication: 0]
    ├── 143. t: Q(a)              [t-implication: 0]
    ├── 144. f: P(a) & P*(a)      [t-implication: 0]
    ├── 145. t: Q(a)              [t-implication: 0]
    ├── 146. f: P(a) & P*(a)      [t-implication: 0]
    ├── 147. t: Q(a)              [t-implication: 0]
    ├── 148. f: P(a) & P*(a)      [t-implication: 0]
    ├── 149. t: Q(a)              [t-implication: 0]
    ├── 150. f: P(a) & P*(a)      [t-implication: 0]
    ├── 151. t: Q(a)              [t-implication: 0]
    ├── 152. f: P(a) & P*(a)      [t-implication: 0]
    ├── 153. t: Q(a)              [t-implication: 0]
    ├── 154. f: P(a) & P*(a)      [t-implication: 0]
    ├── 155. t: Q(a)              [t-implication: 0]
    ├── 156. f: P(a) & P*(a)      [t-implication: 0]
    ├── 157. t: Q(a)              [t-implication: 0]
    ├── 158. f: P(a) & P*(a)      [t-implication: 0]
    ├── 159. t: Q(a)              [t-implication: 0]
    ├── 160. f: P(a) & P*(a)      [t-implication: 0]
    ├── 161. t: Q(a)              [t-implication: 0]
    ├── 162. f: P(a) & P*(a)      [t-implication: 0]
    ├── 163. t: Q(a)              [t-implication: 0]
    ├── 164. f: P(a) & P*(a)      [t-implication: 0]
    ├── 165. t: Q(a)              [t-implication: 0]
    ├── 166. f: P(a) & P*(a)      [t-implication: 0]
    ├── 167. t: Q(a)              [t-implication: 0]
    ├── 168. f: P(a) & P*(a)      [t-implication: 0]
    ├── 169. t: Q(a)              [t-implication: 0]
    ├── 170. f: P(a) & P*(a)      [t-implication: 0]
    ├── 171. t: Q(a)              [t-implication: 0]
    ├── 172. f: P(a) & P*(a)      [t-implication: 0]
    ├── 173. t: Q(a)              [t-implication: 0]
    ├── 174. f: P(a) & P*(a)      [t-implication: 0]
    ├── 175. t: Q(a)              [t-implication: 0]
    ├── 176. f: P(a) & P*(a)      [t-implication: 0]
    ├── 177. t: Q(a)              [t-implication: 0]
    ├── 178. f: P(a) & P*(a)      [t-implication: 0]
    ├── 179. t: Q(a)              [t-implication: 0]
    ├── 180. f: P(a) & P*(a)      [t-implication: 0]
    ├── 181. t: Q(a)              [t-implication: 0]
    ├── 182. f: P(a) & P*(a)      [t-implication: 0]
    ├── 183. t: Q(a)              [t-implication: 0]
    ├── 184. f: P(a) & P*(a)      [t-implication: 0]
    ├── 185. t: Q(a)              [t-implication: 0]
    ├── 186. f: P(a) & P*(a)      [t-implication: 0]
    ├── 187. t: Q(a)              [t-implication: 0]
    ├── 188. f: P(a) & P*(a)      [t-implication: 0]
    ├── 189. t: Q(a)              [t-implication: 0]
    ├── 190. f: P(a) & P*(a)      [t-implication: 0]
    ├── 191. t: Q(a)              [t-implication: 0]
    ├── 192. f: P(a) & P*(a)      [t-implication: 0]
    ├── 193. t: Q(a)              [t-implication: 0]
    ├── 194. f: P(a) & P*(a)      [t-implication: 0]
    ├── 195. t: Q(a)              [t-implication: 0]
    ├── 196. f: P(a) & P*(a)      [t-implication: 0]
    ├── 197. t: Q(a)              [t-implication: 0]
    ├── 198. f: P(a) & P*(a)      [t-implication: 0]
    ├── 199. t: Q(a)              [t-implication: 0]
    ├── 200. f: P(a) & P*(a)      [t-implication: 0]
    ├── 201. t: Q(a)              [t-implication: 0]
    ├── 202. f: P(a) & P*(a)      [t-implication: 0]
    ├── 203. t: Q(a)              [t-implication: 0]
    ├── 204. f: P(a) & P*(a)      [t-implication: 0]
    ├── 205. t: Q(a)              [t-implication: 0]
    ├── 206. f: P(a) & P*(a)      [t-implication: 0]
    ├── 207. t: Q(a)              [t-implication: 0]
    ├── 208. f: P(a) & P*(a)      [t-implication: 0]
    ├── 209. t: Q(a)              [t-implication: 0]
    ├── 210. f: P(a) & P*(a)      [t-implication: 0]
    ├── 211. t: Q(a)              [t-implication: 0]
    ├── 212. f: P(a) & P*(a)      [t-implication: 0]
    ├── 213. t: Q(a)              [t-implication: 0]
    ├── 214. f: P(a) & P*(a)      [t-implication: 0]
    ├── 215. t: Q(a)              [t-implication: 0]
    ├── 216. f: P(a) & P*(a)      [t-implication: 0]
    ├── 217. t: Q(a)              [t-implication: 0]
    ├── 218. f: P(a) & P*(a)      [t-implication: 0]
    ├── 219. t: Q(a)              [t-implication: 0]
    ├── 220. f: P(a) & P*(a)      [t-implication: 0]
    ├── 221. t: Q(a)              [t-implication: 0]
    ├── 222. f: P(a) & P*(a)      [t-implication: 0]
    ├── 223. t: Q(a)              [t-implication: 0]
    ├── 224. f: P(a) & P*(a)      [t-implication: 0]
    ├── 225. t: Q(a)              [t-implication: 0]
    ├── 226. f: P(a) & P*(a)      [t-implication: 0]
    ├── 227. t: Q(a)              [t-implication: 0]
    ├── 228. f: P(a) & P*(a)      [t-implication: 0]
    ├── 229. t: Q(a)              [t-implication: 0]
    ├── 230. f: P(a) & P*(a)      [t-implication: 0]
    ├── 231. t: Q(a)              [t-implication: 0]
    ├── 232. f: P(a) & P*(a)      [t-implication: 0]
    ├── 233. t: Q(a)              [t-implication: 0]
    ├── 234. f: P(a) & P*(a)      [t-implication: 0]
    ├── 235. t: Q(a)              [t-implication: 0]
    ├── 236. f: P(a) & P*(a)      [t-implication: 0]
    ├── 237. t: Q(a)              [t-implication: 0]
    ├── 238. f: P(a) & P*(a)      [t-implication: 0]
    ├── 239. t: Q(a)              [t-implication: 0]
    ├── 240. f: P(a) & P*(a)      [t-implication: 0]
    ├── 241. t: Q(a)              [t-implication: 0]
    ├── 242. f: P(a) & P*(a)      [t-implication: 0]
    ├── 243. t: Q(a)              [t-implication: 0]
    ├── 244. f: P(a) & P*(a)      [t-implication: 0]
    ├── 245. t: Q(a)              [t-implication: 0]
    ├── 246. f: P(a) & P*(a)      [t-implication: 0]
    ├── 247. t: Q(a)              [t-implication: 0]
    ├── 248. f: P(a) & P*(a)      [t-implication: 0]
    ├── 249. t: Q(a)              [t-implication: 0]
    ├── 250. f: P(a) & P*(a)      [t-implication: 0]
    ├── 251. t: Q(a)              [t-implication: 0]
    ├── 252. f: P(a) & P*(a)      [t-implication: 0]
    ├── 253. t: Q(a)              [t-implication: 0]
    ├── 254. f: P(a) & P*(a)      [t-implication: 0]
    ├── 255. t: Q(a)              [t-implication: 0]
    ├── 256. f: P(a) & P*(a)      [t-implication: 0]
    ├── 257. t: Q(a)              [t-implication: 0]
    ├── 258. f: P(a) & P*(a)      [t-implication: 0]
    ├── 259. t: Q(a)              [t-implication: 0]
    ├── 260. f: P(a) & P*(a)      [t-implication: 0]
    ├── 261. t: Q(a)              [t-implication: 0]
    ├── 262. f: P(a) & P*(a)      [t-implication: 0]
    ├── 263. t: Q(a)              [t-implication: 0]
    ├── 264. f: P(a) & P*(a)      [t-implication: 0]
    ├── 265. t: Q(a)              [t-implication: 0]
    ├── 266. f: P(a) & P*(a)      [t-implication: 0]
    ├── 267. t: Q(a)              [t-implication: 0]
    ├── 268. f: P(a) & P*(a)      [t-implication: 0]
    ├── 269. t: Q(a)              [t-implication: 0]
    ├── 270. f: P(a) & P*(a)      [t-implication: 0]
    ├── 271. t: Q(a)              [t-implication: 0]
    ├── 272. f: P(a) & P*(a)      [t-implication: 0]
    ├── 273. t: Q(a)              [t-implication: 0]
    ├── 274. f: P(a) & P*(a)      [t-implication: 0]
    ├── 275. t: Q(a)              [t-implication: 0]
    ├── 276. f: P(a) & P*(a)      [t-implication: 0]
    ├── 277. t: Q(a)              [t-implication: 0]
    ├── 278. f: P(a) & P*(a)      [t-implication: 0]
    ├── 279. t: Q(a)              [t-implication: 0]
    ├── 280. f: P(a) & P*(a)      [t-implication: 0]
    ├── 281. t: Q(a)              [t-implication: 0]
    ├── 282. f: P(a) & P*(a)      [t-implication: 0]
    ├── 283. t: Q(a)              [t-implication: 0]
    ├── 284. f: P(a) & P*(a)      [t-implication: 0]
    ├── 285. t: Q(a)              [t-implication: 0]
    ├── 286. f: P(a) & P*(a)      [t-implication: 0]
    ├── 287. t: Q(a)              [t-implication: 0]
    ├── 288. f: P(a) & P*(a)      [t-implication: 0]
    ├── 289. t: Q(a)              [t-implication: 0]
    ├── 290. f: P(a) & P*(a)      [t-implication: 0]
    ├── 291. t: Q(a)              [t-implication: 0]
    ├── 292. f: P(a) & P*(a)      [t-implication: 0]
    ├── 293. t: Q(a)              [t-implication: 0]
    ├── 294. f: P(a) & P*(a)      [t-implication: 0]
    ├── 295. t: Q(a)              [t-implication: 0]
    ├── 296. f: P(a) & P*(a)      [t-implication: 0]
    ├── 297. t: Q(a)              [t-implication: 0]
    ├── 298. f: P(a) & P*(a)      [t-implication: 0]
    ├── 299. t: Q(a)              [t-implication: 0]
    ├── 300. f: P(a) & P*(a)      [t-implication: 0]
    ├── 301. t: Q(a)              [t-implication: 0]
    ├── 302. f: P(a) & P*(a)      [t-implication: 0]
    ├── 303. t: Q(a)              [t-implication: 0]
    ├── 304. f: P(a) & P*(a)      [t-implication: 0]
    ├── 305. t: Q(a)              [t-implication: 0]
    ├── 306. f: P(a) & P*(a)      [t-implication: 0]
    ├── 307. t: Q(a)              [t-implication: 0]
    ├── 308. f: P(a) & P*(a)      [t-implication: 0]
    ├── 309. t: Q(a)              [t-implication: 0]
    ├── 310. f: P(a) & P*(a)      [t-implication: 0]
    ├── 311. t: Q(a)              [t-implication: 0]
    ├── 312. f: P(a) & P*(a)      [t-implication: 0]
    ├── 313. t: Q(a)              [t-implication: 0]
    ├── 314. f: P(a) & P*(a)      [t-implication: 0]
    ├── 315. t: Q(a)              [t-implication: 0]
    ├── 316. f: P(a) & P*(a)      [t-implication: 0]
    ├── 317. t: Q(a)              [t-implication: 0]
    ├── 318. f: P(a) & P*(a)      [t-implication: 0]
    ├── 319. t: Q(a)              [t-implication: 0]
    ├── 320. f: P(a) & P*(a)      [t-implication: 0]
    ├── 321. t: Q(a)              [t-implication: 0]
    ├── 322. f: P(a) & P*(a)      [t-implication: 0]
    ├── 323. t: Q(a)              [t-implication: 0]
    ├── 324. f: P(a) & P*(a)      [t-implication: 0]
    ├── 325. t: Q(a)              [t-implication: 0]
    ├── 326. f: P(a) & P*(a)      [t-implication: 0]
    ├── 327. t: Q(a)              [t-implication: 0]
    ├── 328. f: P(a) & P*(a)      [t-implication: 0]
    ├── 329. t: Q(a)              [t-implication: 0]
    ├── 330. f: P(a) & P*(a)      [t-implication: 0]
    ├── 331. t: Q(a)              [t-implication: 0]
    ├── 332. f: P(a) & P*(a)      [t-implication: 0]
    ├── 333. t: Q(a)              [t-implication: 0]
    ├── 334. f: P(a) & P*(a)      [t-implication: 0]
    ├── 335. t: Q(a)              [t-implication: 0]
    ├── 336. f: P(a) & P*(a)      [t-implication: 0]
    ├── 337. t: Q(a)              [t-implication: 0]
    ├── 338. f: P(a) & P*(a)      [t-implication: 0]
    ├── 339. t: Q(a)              [t-implication: 0]
    ├── 340. f: P(a) & P*(a)      [t-implication: 0]
    ├── 341. t: Q(a)              [t-implication: 0]
    ├── 342. f: P(a) & P*(a)      [t-implication: 0]
    ├── 343. t: Q(a)              [t-implication: 0]
    ├── 344. f: P(a) & P*(a)      [t-implication: 0]
    ├── 345. t: Q(a)              [t-implication: 0]
    ├── 346. f: P(a) & P*(a)      [t-implication: 0]
    ├── 347. t: Q(a)              [t-implication: 0]
    ├── 348. f: P(a) & P*(a)      [t-implication: 0]
    ├── 349. t: Q(a)              [t-implication: 0]
    ├── 350. f: P(a) & P*(a)      [t-implication: 0]
    ├── 351. t: Q(a)              [t-implication: 0]
    ├── 352. f: P(a) & P*(a)      [t-implication: 0]
    ├── 353. t: Q(a)              [t-implication: 0]
    ├── 354. f: P(a) & P*(a)      [t-implication: 0]
    ├── 355. t: Q(a)              [t-implication: 0]
    ├── 356. f: P(a) & P*(a)      [t-implication: 0]
    ├── 357. t: Q(a)              [t-implication: 0]
    ├── 358. f: P(a) & P*(a)      [t-implication: 0]
    ├── 359. t: Q(a)              [t-implication: 0]
    ├── 360. f: P(a) & P*(a)      [t-implication: 0]
    ├── 361. t: Q(a)              [t-implication: 0]
    ├── 362. f: P(a) & P*(a)      [t-implication: 0]
    ├── 363. t: Q(a)              [t-implication: 0]
    ├── 364. f: P(a) & P*(a)      [t-implication: 0]
    ├── 365. t: Q(a)              [t-implication: 0]
    ├── 366. f: P(a) & P*(a)      [t-implication: 0]
    ├── 367. t: Q(a)              [t-implication: 0]
    ├── 368. f: P(a) & P*(a)      [t-implication: 0]
    ├── 369. t: Q(a)              [t-implication: 0]
    ├── 370. f: P(a) & P*(a)      [t-implication: 0]
    ├── 371. t: Q(a)              [t-implication: 0]
    ├── 372. f: P(a) & P*(a)      [t-implication: 0]
    ├── 373. t: Q(a)              [t-implication: 0]
    ├── 374. f: P(a) & P*(a)      [t-implication: 0]
    ├── 375. t: Q(a)              [t-implication: 0]
    ├── 376. f: P(a) & P*(a)      [t-implication: 0]
    ├── 377. t: Q(a)              [t-implication: 0]
    ├── 378. f: P(a) & P*(a)      [t-implication: 0]
    ├── 379. t: Q(a)              [t-implication: 0]
    ├── 380. f: P(a) & P*(a)      [t-implication: 0]
    ├── 381. t: Q(a)              [t-implication: 0]
    ├── 382. f: P(a) & P*(a)      [t-implication: 0]
    ├── 383. t: Q(a)              [t-implication: 0]
    ├── 384. f: P(a) & P*(a)      [t-implication: 0]
    ├── 385. t: Q(a)              [t-implication: 0]
    ├── 386. f: P(a) & P*(a)      [t-implication: 0]
    ├── 387. t: Q(a)              [t-implication: 0]
    ├── 388. f: P(a) & P*(a)      [t-implication: 0]
    ├── 389. t: Q(a)              [t-implication: 0]
    ├── 390. f: P(a) & P*(a)      [t-implication: 0]
    ├── 391. t: Q(a)              [t-implication: 0]
    ├── 392. f: P(a) & P*(a)      [t-implication: 0]
    ├── 393. t: Q(a)              [t-implication: 0]
    ├── 394. f: P(a) & P*(a)      [t-implication: 0]
    ├── 395. t: Q(a)              [t-implication: 0]
    ├── 396. f: P(a) & P*(a)      [t-implication: 0]
    ├── 397. t: Q(a)              [t-implication: 0]
    ├── 398. f: P(a) & P*(a)      [t-implication: 0]
    ├── 399. t: Q(a)              [t-implication: 0]
    ├── 400. f: P(a) & P*(a)      [t-implication: 0]
    ├── 401. t: Q(a)              [t-implication: 0]
    ├── 402. f: P(a) & P*(a)      [t-implication: 0]
    ├── 403. t: Q(a)              [t-implication: 0]
    ├── 404. f: P(a) & P*(a)      [t-implication: 0]
    ├── 405. t: Q(a)              [t-implication: 0]
    ├── 406. f: P(a) & P*(a)      [t-implication: 0]
    ├── 407. t: Q(a)              [t-implication: 0]
    ├── 408. f: P(a) & P*(a)      [t-implication: 0]
    ├── 409. t: Q(a)              [t-implication: 0]
    ├── 410. f: P(a) & P*(a)      [t-implication: 0]
    ├── 411. t: Q(a)              [t-implication: 0]
    ├── 412. f: P(a) & P*(a)      [t-implication: 0]
    ├── 413. t: Q(a)              [t-implication: 0]
    ├── 414. f: P(a) & P*(a)      [t-implication: 0]
    ├── 415. t: Q(a)              [t-implication: 0]
    ├── 416. f: P(a) & P*(a)      [t-implication: 0]
    ├── 417. t: Q(a)              [t-implication: 0]
    ├── 418. f: P(a) & P*(a)      [t-implication: 0]
    ├── 419. t: Q(a)              [t-implication: 0]
    ├── 420. f: P(a) & P*(a)      [t-implication: 0]
    ├── 421. t: Q(a)              [t-implication: 0]
    ├── 422. f: P(a) & P*(a)      [t-implication: 0]
    ├── 423. t: Q(a)              [t-implication: 0]
    ├── 424. f: P(a) & P*(a)      [t-implication: 0]
    ├── 425. t: Q(a)              [t-implication: 0]
    ├── 426. f: P(a) & P*(a)      [t-implication: 0]
    ├── 427. t: Q(a)              [t-implication: 0]
    ├── 428. f: P(a) & P*(a)      [t-implication: 0]
    ├── 429. t: Q(a)              [t-implication: 0]
    ├── 430. f: P(a) & P*(a)      [t-implication: 0]
    ├── 431. t: Q(a)              [t-implication: 0]
    ├── 432. f: P(a) & P*(a)      [t-implication: 0]
    ├── 433. t: Q(a)              [t-implication: 0]
    ├── 434. f: P(a) & P*(a)      [t-implication: 0]
    ├── 435. t: Q(a)              [t-implication: 0]
    ├── 436. f: P(a) & P*(a)      [t-implication: 0]
    ├── 437. t: Q(a)              [t-implication: 0]
    ├── 438. f: P(a) & P*(a)      [t-implication: 0]
    ├── 439. t: Q(a)              [t-implication: 0]
    ├── 440. f: P(a) & P*(a)      [t-implication: 0]
    ├── 441. t: Q(a)              [t-implication: 0]
    ├── 442. f: P(a) & P*(a)      [t-implication: 0]
    ├── 443. t: Q(a)              [t-implication: 0]
    ├── 444. f: P(a) & P*(a)      [t-implication: 0]
    ├── 445. t: Q(a)              [t-implication: 0]
    ├── 446. f: P(a) & P*(a)      [t-implication: 0]
    ├── 447. t: Q(a)              [t-implication: 0]
    ├── 448. f: P(a) & P*(a)      [t-implication: 0]
    ├── 449. t: Q(a)              [t-implication: 0]
    ├── 450. f: P(a) & P*(a)      [t-implication: 0]
    ├── 451. t: Q(a)              [t-implication: 0]
    ├── 452. f: P(a) & P*(a)      [t-implication: 0]
    ├── 453. t: Q(a)              [t-implication: 0]
    ├── 454. f: P(a) & P*(a)      [t-implication: 0]
    ├── 455. t: Q(a)              [t-implication: 0]
    ├── 456. f: P(a) & P*(a)      [t-implication: 0]
    ├── 457. t: Q(a)              [t-implication: 0]
    ├── 458. f: P(a) & P*(a)      [t-implication: 0]
    ├── 459. t: Q(a)              [t-implication: 0]
    ├── 460. f: P(a) & P*(a)      [t-implication: 0]
    ├── 461. t: Q(a)              [t-implication: 0]
    ├── 462. f: P(a) & P*(a)      [t-implication: 0]
    ├── 463. t: Q(a)              [t-implication: 0]
    ├── 464. f: P(a) & P*(a)      [t-implication: 0]
    ├── 465. t: Q(a)              [t-implication: 0]
    ├── 466. f: P(a) & P*(a)      [t-implication: 0]
    ├── 467. t: Q(a)              [t-implication: 0]
    ├── 468. f: P(a) & P*(a)      [t-implication: 0]
    ├── 469. t: Q(a)              [t-implication: 0]
    ├── 470. f: P(a) & P*(a)      [t-implication: 0]
    ├── 471. t: Q(a)              [t-implication: 0]
    ├── 472. f: P(a) & P*(a)      [t-implication: 0]
    ├── 473. t: Q(a)              [t-implication: 0]
    ├── 474. f: P(a) & P*(a)      [t-implication: 0]
    ├── 475. t: Q(a)              [t-implication: 0]
    ├── 476. f: P(a) & P*(a)      [t-implication: 0]
    ├── 477. t: Q(a)              [t-implication: 0]
    ├── 478. f: P(a) & P*(a)      [t-implication: 0]
    ├── 479. t: Q(a)              [t-implication: 0]
    ├── 480. f: P(a) & P*(a)      [t-implication: 0]
    ├── 481. t: Q(a)              [t-implication: 0]
    ├── 482. f: P(a) & P*(a)      [t-implication: 0]
    ├── 483. t: Q(a)              [t-implication: 0]
    ├── 484. f: P(a) & P*(a)      [t-implication: 0]
    ├── 485. t: Q(a)              [t-implication: 0]
    ├── 486. f: P(a) & P*(a)      [t-implication: 0]
    ├── 487. t: Q(a)              [t-implication: 0]
    ├── 488. f: P(a) & P*(a)      [t-implication: 0]
    ├── 489. t: Q(a)              [t-implication: 0]
    ├── 490. f: P(a) & P*(a)      [t-implication: 0]
    ├── 491. t: Q(a)              [t-implication: 0]
    ├── 492. f: P(a) & P*(a)      [t-implication: 0]
    ├── 493. t: Q(a)              [t-implication: 0]
    ├── 494. f: P(a) & P*(a)      [t-implication: 0]
    ├── 495. t: Q(a)              [t-implication: 0]
    ├── 496. f: P(a) & P*(a)      [t-implication: 0]
    ├── 497. t: Q(a)              [t-implication: 0]
    ├── 498. f: P(a) & P*(a)      [t-implication: 0]
    ├── 499. t: Q(a)              [t-implication: 0]
    ├── 500. f: P(a) & P*(a)      [t-implication: 0]
    └── 501. t: Q(a)              [t-implication: 0]
```
---

### Chain reasoning through contradictions

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --inference --tree --show-rules P(a) & P*(a), P(a) -> Q(a), Q(a) -> R(a) |- R(a)
```

**Output:**
```
ACrQ Inference (bilateral mode):
  Premises: P(a) & P*(a), P(a) -> Q(a), Q(a) -> R(a)
  Conclusion: R(a)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t, Q(a)=e, R(a)=f}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. t: P(a) -> Q(a)
    ├──  2. t: Q(a) -> R(a)
    ├──  3. f: R(a)
    ├──  4. t: P(a)         [t-conjunction: 0]
    └──  5. t: P*(a)        [t-conjunction: 0]
```
---

### Multiple gluts interaction

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models (P(a) & P*(a)) & (Q(b) & Q*(b))
```

**Output:**
```
ACrQ Formula (bilateral mode): (P(a) & P*(a)) & (Q(b) & Q*(b))
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=e, P*(a)=e, Q(b)=e, Q*(b)=e}

Tableau tree:
 0. t: (P(a) & P*(a)) & (Q(b) & Q*(b))
    ├──  1. t: P(a) & P*(a)                [t-conjunction: 0]
    └──  2. t: Q(b) & Q*(b)                [t-conjunction: 0]
```
---

### Quantified gluts

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models [exists X (P(X) & P*(X))]Q(X)
```

**Output:**
```
ERROR: Parse error: Invalid character at position 9: '*'

```
---

## Countermodel Construction and Quality

Testing countermodel generation for various invalid inferences

### Minimal countermodel for simple invalid

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel p |- q
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {p=t, q=f}

Tableau tree:
 0. t: p & (~q)
    ├──  1. t: p     [t-conjunction: 0]
    └──  2. t: ~q    [t-conjunction: 0]
        └──  3. f: q [t-negation: 2]
```
---

### Countermodel with undefined values

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel p | ~p |- q
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {p=t, q=f}
  2. {p=e, q=f}

Tableau tree:
 0. t: (p | (~p)) & (~q)
    ├──  1. t: p | (~p)      [t-conjunction: 0]
    │   ├──  4. t: p         [t-disjunction: 1]
    │   └──  5. t: ~p        [t-disjunction: 1]
    └──  2. t: ~q            [t-conjunction: 0]
        └──  3. f: q         [t-negation: 2]
```
---

### Quantified countermodel structure

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X P(X)]Q(X) |- [forall Y P(Y)]Q(Y)
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {P(c_3)=t, P(c_6)=t, Q(c_3)=t, Q(c_6)=f}

Tableau tree:
 0. t: [∃X P(X)]Q(X) & (~[∀Y P(Y)]Q(Y))
    ├──  1. t: [∃X P(X)]Q(X)                [t-conjunction: 0]
    │   ├──  3. t: P(c_3)                   [t-restricted-exists: 1]
    │   └──  4. t: Q(c_3)                   [t-restricted-exists: 1]
    └──  2. t: ~[∀Y P(Y)]Q(Y)               [t-conjunction: 0]
        └──  5. f: [∀Y P(Y)]Q(Y)            [t-negation: 2]
            ├──  6. t: P(c_6)               [f-restricted-forall: 5]
            └──  7. f: Q(c_6)               [f-restricted-forall: 5]
```
---

### Multiple witness countermodel

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel [exists X P(X)]Q(X), [exists Y R(Y)]S(Y) |- [forall Z (P(Z) | R(Z))](Q(Z) & S(Z))
```

**Output:**
```
✗ Invalid inference
Countermodels:
  1. {P(c_10)=t, P(c_6)=t, Q(c_10)=f, Q(c_6)=t, R(c_10)=e, R(c_8)=t, S(c_10)=e, S(c_8)=t}
  2. {P(c_10)=t, P(c_6)=t, Q(c_10)=e, Q(c_6)=t, R(c_10)=e, R(c_8)=t, S(c_10)=f, S(c_8)=t}
  3. {P(c_10)=t, P(c_6)=t, Q(c_10)=e, Q(c_6)=t, R(c_10)=e, R(c_8)=t, S(c_10)=e, S(c_8)=t}
  4. {P(c_10)=e, P(c_6)=t, Q(c_10)=f, Q(c_6)=t, R(c_10)=t, R(c_8)=t, S(c_10)=e, S(c_8)=t}
  5. {P(c_10)=e, P(c_6)=t, Q(c_10)=e, Q(c_6)=t, R(c_10)=t, R(c_8)=t, S(c_10)=f, S(c_8)=t}
  6. {P(c_10)=e, P(c_6)=t, Q(c_10)=e, Q(c_6)=t, R(c_10)=t, R(c_8)=t, S(c_10)=e, S(c_8)=t}

Tableau tree:
 0. t: ([∃X P(X)]Q(X) & [∃Y R(Y)]S(Y)) & (~[∀Z P(Z) | R(Z)]Q(Z) & S(Z))
    ├──  1. t: [∃X P(X)]Q(X) & [∃Y R(Y)]S(Y)                                [t-conjunction: 0]
    │   ├──  3. t: [∃X P(X)]Q(X)                                            [t-conjunction: 1]
    │   │   ├──  6. t: P(c_6)                                               [t-restricted-exists: 3]
    │   │   └──  7. t: Q(c_6)                                               [t-restricted-exists: 3]
    │   └──  4. t: [∃Y R(Y)]S(Y)                                            [t-conjunction: 1]
    │       ├──  8. t: R(c_8)                                               [t-restricted-exists: 4]
    │       └──  9. t: S(c_8)                                               [t-restricted-exists: 4]
    └──  2. t: ~[∀Z P(Z) | R(Z)]Q(Z) & S(Z)                                 [t-conjunction: 0]
        └──  5. f: [∀Z P(Z) | R(Z)]Q(Z) & S(Z)                              [t-negation: 2]
            ├── 10. t: P(c_10) | R(c_10)                                    [f-restricted-forall: 5]
            │   ├── 12. t: P(c_10)                                          [t-disjunction: 10]
            │   └── 13. t: R(c_10)                                          [t-disjunction: 10]
            └── 11. f: Q(c_10) & S(c_10)                                    [f-restricted-forall: 5]
                ├── 14. f: Q(c_10)                                          [f-conjunction: 11]
                ├── 15. f: S(c_10)                                          [f-conjunction: 11]
                ├── 16. e: Q(c_10)                                          [f-conjunction: 11]
                ├── 17. e: S(c_10)                                          [f-conjunction: 11]
                ├── 18. f: Q(c_10)                                          [f-conjunction: 11]
                ├── 19. f: S(c_10)                                          [f-conjunction: 11]
                ├── 20. e: Q(c_10)                                          [f-conjunction: 11]
                └── 21. e: S(c_10)                                          [f-conjunction: 11]
```
---

### Countermodel for complex formula

**CLI Command:**
```bash
python -m wkrq --inference --tree --show-rules --countermodel (p -> q) & (r -> s) |- (p & r) -> (q & s)
```

**Output:**
```
✓ Valid inference

Tableau tree:
 0. t: ((p -> q) & (r -> s)) & (~((p & r) -> (q & s)))
    ├──  1. t: (p -> q) & (r -> s)                         [t-conjunction: 0]
    │   ├──  3. t: p -> q                                  [t-conjunction: 1]
    │   │   ├── 10. f: p  ×                                [t-implication: 3]
    │   │   └── 11. t: q  ×                                [t-implication: 3]
    │   └──  4. t: r -> s                                  [t-conjunction: 1]
    │       ├── 12. f: r  ×                                [t-implication: 4]
    │       └── 13. t: s  ×                                [t-implication: 4]
    └──  2. t: ~((p & r) -> (q & s))                       [t-conjunction: 0]
        └──  5. f: (p & r) -> (q & s)                      [t-negation: 2]
            ├──  6. t: p & r                               [f-implication: 5]
            │   ├──  8. t: p  ×                            [t-conjunction: 6]
            │   └──  9. t: r  ×                            [t-conjunction: 6]
            └──  7. f: q & s                               [f-implication: 5]
                ├── 14. f: q  ×                            [f-conjunction: 7]
                ├── 15. f: s  ×                            [f-conjunction: 7]
                ├── 16. e: q  ×                            [f-conjunction: 7]
                └── 17. e: s  ×                            [f-conjunction: 7]
```
---

### ACrQ countermodel with gluts

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --inference --tree --show-rules --countermodel P(a) & P*(a) |- [forall X Q(X)]R(X)
```

**Output:**
```
ACrQ Inference (bilateral mode):
  Premises: P(a) & P*(a)
  Conclusion: [∀X Q(X)]R(X)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. f: [∀X Q(X)]R(X)
    ├──  2. t: P(a)          [t-conjunction: 0]
    └──  3. t: P*(a)         [t-conjunction: 0]
```
---

## Performance and Complexity Boundaries

Tests at the edge of computational feasibility

### Deep nesting stress test

**CLI Command:**
```bash
python -m wkrq --tree --show-rules ((((p | q) & r) -> s) | t) & u
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ((((p | q) & r) -> s) | t) & u
    ├──  1. t: (((p | q) & r) -> s) | t   [t-conjunction: 0]
    │   ├──  3. t: ((p | q) & r) -> s     [t-disjunction: 1]
    │   └──  4. t: t                      [t-disjunction: 1]
    └──  2. t: u                          [t-conjunction: 0]
```
---

### Wide branching formula

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p1 | p2) & (q1 | q2) & (r1 | r2) & (s1 | s2)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (((p1 | p2) & (q1 | q2)) & (r1 | r2)) & (s1 | s2)
    ├──  1. t: ((p1 | p2) & (q1 | q2)) & (r1 | r2)           [t-conjunction: 0]
    │   ├──  3. t: (p1 | p2) & (q1 | q2)                     [t-conjunction: 1]
    │   │   ├──  5. t: p1 | p2                               [t-conjunction: 3]
    │   │   │   ├── 13. t: p1                                [t-disjunction: 5]
    │   │   │   ├── 14. t: p2                                [t-disjunction: 5]
    │   │   │   ├── 15. t: p1                                [t-disjunction: 5]
    │   │   │   ├── 16. t: p2                                [t-disjunction: 5]
    │   │   │   ├── 17. t: p1                                [t-disjunction: 5]
    │   │   │   ├── 18. t: p2                                [t-disjunction: 5]
    │   │   │   ├── 19. t: p1                                [t-disjunction: 5]
    │   │   │   └── 20. t: p2                                [t-disjunction: 5]
    │   │   └──  6. t: q1 | q2                               [t-conjunction: 3]
    │   │       ├── 21. t: q1                                [t-disjunction: 6]
    │   │       ├── 22. t: q2                                [t-disjunction: 6]
    │   │       ├── 23. t: q1                                [t-disjunction: 6]
    │   │       ├── 24. t: q2                                [t-disjunction: 6]
    │   │       ├── 25. t: q1                                [t-disjunction: 6]
    │   │       ├── 26. t: q2                                [t-disjunction: 6]
    │   │       ├── 27. t: q1                                [t-disjunction: 6]
    │   │       ├── 28. t: q2                                [t-disjunction: 6]
    │   │       ├── 29. t: q1                                [t-disjunction: 6]
    │   │       ├── 30. t: q2                                [t-disjunction: 6]
    │   │       ├── 31. t: q1                                [t-disjunction: 6]
    │   │       ├── 32. t: q2                                [t-disjunction: 6]
    │   │       ├── 33. t: q1                                [t-disjunction: 6]
    │   │       ├── 34. t: q2                                [t-disjunction: 6]
    │   │       ├── 35. t: q1                                [t-disjunction: 6]
    │   │       └── 36. t: q2                                [t-disjunction: 6]
    │   └──  4. t: r1 | r2                                   [t-conjunction: 1]
    │       ├──  9. t: r1                                    [t-disjunction: 4]
    │       ├── 10. t: r2                                    [t-disjunction: 4]
    │       ├── 11. t: r1                                    [t-disjunction: 4]
    │       └── 12. t: r2                                    [t-disjunction: 4]
    └──  2. t: s1 | s2                                       [t-conjunction: 0]
        ├──  7. t: s1                                        [t-disjunction: 2]
        └──  8. t: s2                                        [t-disjunction: 2]
```
---

### Quantifier chain complexity

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X P(X)]Q(X) & [exists Y Q(Y)]R(Y) & [forall Z R(Z)]S(Z)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ([∀X P(X)]Q(X) & [∃Y Q(Y)]R(Y)) & [∀Z R(Z)]S(Z)
    ├──  1. t: [∀X P(X)]Q(X) & [∃Y Q(Y)]R(Y)               [t-conjunction: 0]
    │   ├──  3. t: [∀X P(X)]Q(X)                           [t-conjunction: 1]
    │   │   └──  9. f: P(c_5)                              [t-restricted-forall: 3]
    │   └──  4. t: [∃Y Q(Y)]R(Y)                           [t-conjunction: 1]
    │       ├──  5. t: Q(c_5)                              [t-restricted-exists: 4]
    │       └──  6. t: R(c_5)                              [t-restricted-exists: 4]
    └──  2. t: [∀Z R(Z)]S(Z)                               [t-conjunction: 0]
        ├──  7. f: R(c_5)                                  [t-restricted-forall: 2]
        └──  8. t: S(c_5)                                  [t-restricted-forall: 2]
```
---

### Large conjunction chain

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models p1 & p2 & p3 & p4 & p5 & p6 & p7 & p8
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {p1=t, p2=t, p3=t, p4=t, p5=t, p6=t, p7=t, p8=t}

Tableau tree:
 0. t: ((((((p1 & p2) & p3) & p4) & p5) & p6) & p7) & p8
    ├──  1. t: (((((p1 & p2) & p3) & p4) & p5) & p6) & p7    [t-conjunction: 0]
    │   ├──  3. t: ((((p1 & p2) & p3) & p4) & p5) & p6       [t-conjunction: 1]
    │   │   ├──  5. t: (((p1 & p2) & p3) & p4) & p5          [t-conjunction: 3]
    │   │   │   ├──  7. t: ((p1 & p2) & p3) & p4             [t-conjunction: 5]
    │   │   │   │   ├──  9. t: (p1 & p2) & p3                [t-conjunction: 7]
    │   │   │   │   │   ├── 11. t: p1 & p2                   [t-conjunction: 9]
    │   │   │   │   │   │   ├── 13. t: p1                    [t-conjunction: 11]
    │   │   │   │   │   │   └── 14. t: p2                    [t-conjunction: 11]
    │   │   │   │   │   └── 12. t: p3                        [t-conjunction: 9]
    │   │   │   │   └── 10. t: p4                            [t-conjunction: 7]
    │   │   │   └──  8. t: p5                                [t-conjunction: 5]
    │   │   └──  6. t: p6                                    [t-conjunction: 3]
    │   └──  4. t: p7                                        [t-conjunction: 1]
    └──  2. t: p8                                            [t-conjunction: 0]
```
---

### Complex tautology check

**CLI Command:**
```bash
python -m wkrq --tree --show-rules ((p -> q) -> p) -> p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ((p -> q) -> p) -> p
    ├──  1. f: (p -> q) -> p    [t-implication: 0]
    └──  2. t: p                [t-implication: 0]
```
---

### Exponential branching control

**CLI Command:**
```bash
python -m wkrq --tree --show-rules ((p | q) & (r | s)) -> ((t | u) & (v | w))
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: ((p | q) & (r | s)) -> ((t | u) & (v | w))
    ├──  1. f: (p | q) & (r | s)                      [t-implication: 0]
    │   ├──  3. f: p | q                              [f-conjunction: 1]
    │   │   ├──  9. f: p                              [f-disjunction: 3]
    │   │   └── 10. f: q                              [f-disjunction: 3]
    │   ├──  4. f: r | s                              [f-conjunction: 1]
    │   │   ├── 11. f: r                              [f-disjunction: 4]
    │   │   └── 12. f: s                              [f-disjunction: 4]
    │   ├──  5. e: p | q                              [f-conjunction: 1]
    │   │   ├── 13. e: p                              [e-disjunction: 5]
    │   │   └── 14. e: q                              [e-disjunction: 5]
    │   └──  6. e: r | s                              [f-conjunction: 1]
    │       ├── 15. e: r                              [e-disjunction: 6]
    │       └── 16. e: s                              [e-disjunction: 6]
    └──  2. t: (t | u) & (v | w)                      [t-implication: 0]
        ├──  7. t: t | u                              [t-conjunction: 2]
        │   ├── 17. t: t                              [t-disjunction: 7]
        │   └── 18. t: u                              [t-disjunction: 7]
        └──  8. t: v | w                              [t-conjunction: 2]
```
---

## Ferguson (2021) Literature Examples

Direct examples from Ferguson (2021) to verify compliance

### Ferguson (2021) Example 3.2

**CLI Command:**
```bash
python -m wkrq --tree --show-rules [forall X Human(X)]Mortal(X)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: [∀X Human(X)]Mortal(X)
    ├──  1. f: Human(c_1)         [t-restricted-forall: 0]
    └──  2. t: Mortal(c_1)        [t-restricted-forall: 0]
```
---

### Branch closure example

**CLI Command:**
```bash
python -m wkrq --tree --show-rules p & ~p
```

**Output:**
```
Satisfiable: False

Tableau tree:
 0. t: p & (~p)
    ├──  1. t: p  ×     [t-conjunction: 0]
    └──  2. t: ~p       [t-conjunction: 0]
        └──  3. f: p  × [t-negation: 2]
```
---

### M-sign branching example

**CLI Command:**
```bash
python -m wkrq --sign=m --tree --show-rules p
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. m: p
```
---

### Quantifier restriction example

**CLI Command:**
```bash
python -m wkrq --tree --show-rules --models [exists X Student(X)]Smart(X)
```

**Output:**
```
Satisfiable: True
Models (1):
  1. {Smart(c_1)=t, Student(c_1)=t}

Tableau tree:
 0. t: [∃X Student(X)]Smart(X)
    ├──  1. t: Student(c_1)        [t-restricted-exists: 0]
    └──  2. t: Smart(c_1)          [t-restricted-exists: 0]
```
---

### ACrQ glut tolerance example

**Mode:** ACrQ

**CLI Command:**
```bash
python -m wkrq --mode=acrq --syntax=bilateral --tree --show-rules --models P(a) & P*(a)
```

**Output:**
```
ACrQ Formula (bilateral mode): P(a) & P*(a)
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=t, P*(a)=t}

Tableau tree:
 0. t: P(a) & P*(a)
    ├──  1. t: P(a)     [t-conjunction: 0]
    └──  2. t: P*(a)    [t-conjunction: 0]
```
---

### Tableau completeness example

**CLI Command:**
```bash
python -m wkrq --tree --show-rules (p -> q) | (q -> p)
```

**Output:**
```
Satisfiable: True

Tableau tree:
 0. t: (p -> q) | (q -> p)
    ├──  1. t: p -> q          [t-disjunction: 0]
    │   ├──  3. f: p           [t-implication: 1]
    │   └──  4. t: q           [t-implication: 1]
    └──  2. t: q -> p          [t-disjunction: 0]
        ├──  5. f: q           [t-implication: 2]
        └──  6. t: p           [t-implication: 2]
```
---

## Summary Statistics

- Total validation examples: 111
- Categories covered: 19
- Test suite: 480 automated tests
- Bug fixes validated: Quantifier instantiation bug fixed
