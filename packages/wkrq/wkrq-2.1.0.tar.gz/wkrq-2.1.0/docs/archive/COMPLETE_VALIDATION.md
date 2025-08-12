# wKrQ Complete Validation Document

Generated: 2025-08-05 09:47:00

## Introduction

This document contains a complete validation of the wKrQ (weak Kleene logic with restricted Quantification) implementation. All examples are automatically extracted from the pytest test suite, ensuring perfect synchronization between tests and documentation.

### Critical Bug Fix Note

A critical bug in the restricted quantifier instantiation has been fixed. The bug caused the system to incorrectly validate inferences like `[∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)` by reusing existential witness constants when falsifying universal quantifiers. This created spurious contradictions that made invalid inferences appear valid. The fix ensures that fresh constants are generated for f-case universal quantifiers while preventing infinite constant generation.

### Statistics

- Total test cases: 96
- Total validation commands: 96
- Categories: 13

## Table of Contents

- [ACrQ Paraconsistent Logic](#acrq-paraconsistent-logic) (4 tests)
- [Aristotelian Syllogisms](#aristotelian-syllogisms) (4 tests)
- [Classical Logic Patterns](#classical-logic-patterns) (9 tests)
- [De Morgan's Laws](#de-morgans-laws) (10 tests)
- [Ferguson's Connective Rules](#fergusons-connective-rules) (8 tests)
- [Ferguson's Negation Rules](#fergusons-negation-rules) (5 tests)
- [Ferguson's Quantifier Rules](#fergusons-quantifier-rules) (4 tests)
- [Ferguson's Six-Sign System](#fergusons-six-sign-system) (5 tests)
- [Ferguson's Tableau System](#fergusons-tableau-system) (9 tests)
- [Miscellaneous Tests](#miscellaneous-tests) (23 tests)
- [Model Theory](#model-theory) (3 tests)
- [Quantifier Logic](#quantifier-logic) (8 tests)
- [Weak Kleene Semantics](#weak-kleene-semantics) (4 tests)

---

## ACrQ Paraconsistent Logic

### Four states demonstration: glut, classic true, classic false, gap.
*Test: TestACrQParaconsistentReasoning::test_four_states_demonstration*

Formula: `(P(a) & ~~P(a)) & (~Q(a) & ~~Q(a)) & (~R(a) & ~~~R(a)) & (S(a) & ~S(a))`
Mode: acrq

```
ACrQ Formula (transparent mode): (((P(a) & (~P*(a))) & (Q*(a) & (~Q*(a)))) & (R*(a) & (~(~R*(a))))) & (S(a) & S*(a))
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=e, P*(a)=e, Q*(a)=e, R*(a)=e, S(a)=e, S*(a)=e}

Tableau tree:
 0. t: (((P(a) & (~P*(a))) & (Q*(a) & (~Q*(a)))) & (R*(a) & (~(~R*(a))))) & (S(a) & S*(a))
    ├──  1. t: ((P(a) & (~P*(a))) & (Q*(a) & (~Q*(a)))) & (R*(a) & (~(~R*(a))))                [t-conjunction: 0]
    └──  2. t: S(a) & S*(a)                                                                    [t-conjunction: 0]
```

*Test expects:* Satisfiable: True

---

### Local Inconsistency: P(a) ∧ ~P(a) doesn't affect Q(b).
*Test: TestACrQParaconsistentReasoning::test_local_inconsistency*

Formula: `(P(a) & ~P(a)) & (Q(b) & ~~Q(b))`
Mode: acrq

```
ACrQ Formula (transparent mode): (P(a) & P*(a)) & (Q(b) & (~Q*(b)))
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=e, P*(a)=e, Q(b)=e, Q*(b)=e}

Tableau tree:
 0. t: (P(a) & P*(a)) & (Q(b) & (~Q*(b)))
    ├──  1. t: P(a) & P*(a)                   [t-conjunction: 0]
    └──  2. t: Q(b) & (~Q*(b))                [t-conjunction: 0]
```

*Test expects:* Satisfiable: True

---

### Non-explosion: P(a), ~P(a) ⊬ Q(b) (glut doesn't explode).
*Test: TestACrQParaconsistentReasoning::test_non_explosion*

Formula: `P(a), ~P(a) |- Q(b)`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: P(a), P*(a)
  Conclusion: Q(b)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t, Q(b)=f}
```

*Test expects:* ✗ Invalid inference

---

### Reasoning despite gluts: P(a) → Q(a), P(a), ~P(a) ⊢ Q(a).
*Test: TestACrQParaconsistentReasoning::test_reasoning_despite_gluts*

Formula: `(P(a) -> Q(a)), P(a), ~P(a) |- Q(a)`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: P(a) -> Q(a), P(a), P*(a)
  Conclusion: Q(a)
  ✓ Valid inference
```

*Test expects:* ✓ Valid inference

---

## Aristotelian Syllogisms

### Barbara: All M are P, All S are M ⊢ All S are P.
*Test: TestAristotelianSyllogisms::test_barbara_syllogism*

Formula: `[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)`

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

*Test expects:* ✓ Valid inference

---

### Celarent: No M are P, All S are M ⊢ No S are P.
*Test: TestAristotelianSyllogisms::test_celarent_syllogism*

Formula: `[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))`

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

*Test expects:* ✓ Valid inference

---

### Darii: All M are P, Some S are M ⊢ Some S are P.
*Test: TestAristotelianSyllogisms::test_darii_syllogism*

Formula: `[forall X M(X)]P(X), [exists Y S(Y)]M(Y) |- [exists Z S(Z)]P(Z)`

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

*Test expects:* ✓ Valid inference

---

### Ferio: No M are P, Some S are M ⊢ Some S are not P.
*Test: TestAristotelianSyllogisms::test_ferio_syllogism*

Formula: `[forall X M(X)](~P(X)), [exists Y S(Y)]M(Y) |- [exists Z S(Z)](~P(Z))`

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

*Test expects:* ✓ Valid inference

---

## Classical Logic Patterns

### Addition: p ⊢ p ∨ q.
*Test: TestClassicalInferences::test_addition*

Formula: `p |- (p | q)`

```
✓ Valid inference

Tableau tree:
 0. t: p & (~(p | q))
    ├──  1. t: p  ×         [t-conjunction: 0]
    └──  2. t: ~(p | q)     [t-conjunction: 0]
        └──  3. f: p | q    [t-negation: 2]
            └──  4. f: p  × [f-disjunction: 3]
```

*Test expects:* ✓ Valid inference

---

### Constructive Dilemma: (p → q) ∧ (r → s), p ∨ r ⊢ q ∨ s.
*Test: TestClassicalInferences::test_constructive_dilemma*

Formula: `((p -> q) & (r -> s)), (p | r) |- (q | s)`

```
✓ Valid inference

Tableau tree:
 0. t: (((p -> q) & (r -> s)) & (p | r)) & (~(q | s))
    ├──  1. t: ((p -> q) & (r -> s)) & (p | r)            [t-conjunction: 0]
    │   ├──  3. t: (p -> q) & (r -> s)                    [t-conjunction: 1]
    │   │   ├──  6. t: p -> q                             [t-conjunction: 3]
    │   │   │   ├── 12. f: p  ×                           [t-implication: 6]
    │   │   │   ├── 13. t: q  ×                           [t-implication: 6]
    │   │   │   ├── 14. f: p  ×                           [t-implication: 6]
    │   │   │   └── 15. t: q  ×                           [t-implication: 6]
    │   │   └──  7. t: r -> s                             [t-conjunction: 3]
    │   │       ├── 16. f: r  ×                           [t-implication: 7]
    │   │       └── 17. t: s  ×                           [t-implication: 7]
    │   └──  4. t: p | r                                  [t-conjunction: 1]
    │       ├── 10. t: p  ×                               [t-disjunction: 4]
    │       └── 11. t: r  ×                               [t-disjunction: 4]
    └──  2. t: ~(q | s)                                   [t-conjunction: 0]
        └──  5. f: q | s                                  [t-negation: 2]
            ├──  8. f: q  ×                               [f-disjunction: 5]
            └──  9. f: s  ×                               [f-disjunction: 5]
```

*Test expects:* ✓ Valid inference

---

### Contraposition: (p → q) ⊢ (¬q → ¬p) is valid in Ferguson's system.
*Test: TestClassicalInferences::test_contraposition_valid_in_ferguson*

Formula: `(p -> q) |- (~q -> ~p)`

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

*Test expects:* ✓ Valid inference

---

### Disjunctive Syllogism: p ∨ q, ¬p ⊢ q.
*Test: TestClassicalInferences::test_disjunctive_syllogism*

Formula: `(p | q), ~p |- q`

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

*Test expects:* ✓ Valid inference

---

### Double Negation Elimination: ¬¬p ⊢ p (VALID).
*Test: TestClassicalInferences::test_double_negation_elimination*

Formula: `~~p |- p`

```
✓ Valid inference

Tableau tree:
 0. t: (~(~p)) & (~p)
    ├──  1. t: ~(~p)      [t-conjunction: 0]
    │   └──  3. f: ~p  ×  [t-negation: 1]
    └──  2. t: ~p  ×      [t-conjunction: 0]
```

*Test expects:* ✓ Valid inference

---

### Hypothetical Syllogism: p → q, q → r ⊢ p → r.
*Test: TestClassicalInferences::test_hypothetical_syllogism*

Formula: `(p -> q), (q -> r) |- (p -> r)`

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

*Test expects:* ✓ Valid inference

---

### Modus Ponens: p, p → q ⊢ q.
*Test: TestClassicalInferences::test_modus_ponens*

Formula: `p, (p -> q) |- q`

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

*Test expects:* ✓ Valid inference

---

### Modus Tollens: ¬q, p → q ⊢ ¬p.
*Test: TestClassicalInferences::test_modus_tollens*

Formula: `~q, (p -> q) |- ~p`

```
✓ Valid inference

Tableau tree:
 0. t: ((~q) & (p -> q)) & (~(~p))
    ├──  1. t: (~q) & (p -> q)         [t-conjunction: 0]
    │   ├──  3. t: ~q                  [t-conjunction: 1]
    │   │   └──  6. f: q  ×            [t-negation: 3]
    │   └──  4. t: p -> q              [t-conjunction: 1]
    │       ├──  8. f: p  ×            [t-implication: 4]
    │       └──  9. t: q  ×            [t-implication: 4]
    └──  2. t: ~(~p)                   [t-conjunction: 0]
        └──  5. f: ~p                  [t-negation: 2]
            └──  7. t: p  ×            [f-negation: 5]
```

*Test expects:* ✓ Valid inference

---

### Simplification: p ∧ q ⊢ p.
*Test: TestClassicalInferences::test_simplification*

Formula: `(p & q) |- p`

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

*Test expects:* ✓ Valid inference

---

## De Morgan's Laws

### ACrQDeMorgansLaws Tests

### ACrQ De Morgan 1a: ¬(P(a) ∧ Q(a)) ⊬ ¬P(a) ∨ ¬Q(a) in ACrQ.
*Test: TestACrQDeMorgansLaws::test_acrq_demorgan_basic*

Formula: `~(P(a) & Q(a)) |- (~P(a) | ~Q(a))`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: ~(P(a) & Q(a))
  Conclusion: P*(a) | Q*(a)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=e, P*(a)=f, Q(a)=e, Q*(a)=f}
```

*Test expects:* ✗ Invalid inference

---

### ACrQ De Morgan with bilateral: ¬(P(a) ∧ Q(a)) becomes P*(a) ∨ Q*(a).
*Test: TestACrQDeMorgansLaws::test_acrq_demorgan_bilateral_conversion*

Formula: `~(P(a) & Q(a))`
Mode: acrq

```
ACrQ Formula (transparent mode): ~(P(a) & Q(a))
Sign: t
Satisfiable: True

Tableau tree:
 0. t: ~(P(a) & Q(a))
```

---

### ACrQ preserves De Morgan despite gluts.
*Test: TestACrQDeMorgansLaws::test_acrq_demorgan_preserves_despite_gluts*

Formula: `(P(a) & ~P(a)), ~(P(a) & Q(a)) |- (~P(a) | ~Q(a))`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: P(a) & P*(a), ~(P(a) & Q(a))
  Conclusion: P*(a) | Q*(a)
  ✗ Invalid inference
  Countermodels:
    1. {P(a)=t, P*(a)=t, Q(a)=e, Q*(a)=e}
```

*Test expects:* ✗ Invalid inference

---

### ACrQ De Morgan with glut: P(a) ∧ ~P(a) case.
*Test: TestACrQDeMorgansLaws::test_acrq_demorgan_with_glut*

Formula: `~((P(a) & ~P(a)) & Q(a))`
Mode: acrq

```
ACrQ Formula (transparent mode): ~((P(a) & P*(a)) & Q(a))
Sign: t
Satisfiable: True

Models (1):
  1. {P(a)=e, P*(a)=e, Q(a)=e}

Tableau tree:
 0. t: ~((P(a) & P*(a)) & Q(a))
```

*Test expects:* Satisfiable: True

---

### DeMorgansLaws Tests

### ¬p ∧ ¬q ⊢ ¬(p ∨ q) (VALID in weak Kleene).
*Test: TestDeMorgansLaws::test_demorgan_conjunction_negation*

Formula: `(~p & ~q) |- ~(p | q)`

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

*Test expects:* ✓ Valid inference

---

### ¬(p ∧ q) ⊢ ¬p ∨ ¬q (VALID in weak Kleene).
*Test: TestDeMorgansLaws::test_demorgan_conjunction_to_disjunction*

Formula: `~(p & q) |- (~p | ~q)`

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

*Test expects:* ✓ Valid inference

---

### ¬(p ∨ q) ⊢ ¬p ∧ ¬q (VALID in weak Kleene).
*Test: TestDeMorgansLaws::test_demorgan_disjunction_negation*

Formula: `~(p | q) |- (~p & ~q)`

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

*Test expects:* ✓ Valid inference

---

### ¬p ∨ ¬q ⊢ ¬(p ∧ q) (VALID in weak Kleene).
*Test: TestDeMorgansLaws::test_demorgan_disjunction_to_conjunction*

Formula: `(~p | ~q) |- ~(p & q)`

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

*Test expects:* ✓ Valid inference

---

### De Morgan with undefined: When p,q undefined, both sides undefined.
*Test: TestDeMorgansLaws::test_demorgan_with_undefined*

Formula: `~(p & q)`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e, q=e}
```

*Test expects:* Satisfiable: True

---

### Quantified De Morgan: ¬∀x P(x) ⊢ ∃x ¬P(x) (valid in Ferguson's system).
*Test: TestDeMorgansLaws::test_quantified_demorgan_valid*

Formula: `~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))`

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

*Test expects:* ✓ Valid inference

---

## Ferguson's Connective Rules

### ConjunctionRules Tests

### e : (φ ∧ ψ) → (e : φ) + (e : ψ) [e is contagious].
*Test: TestFergusonConjunctionRules::test_e_conjunction_contagion*

Formula: `p & q`
Sign: e

```
Satisfiable: True

Tableau tree:
 0. e: p & q
    ├──  1. e: p [e-conjunction: 0]
    └──  2. e: q [e-conjunction: 0]
```

---

### f : (φ ∧ ψ) → branches for all ways to get f.
*Test: TestFergusonConjunctionRules::test_f_conjunction_branching*

Formula: `p & q`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: p & q
    ├──  1. f: p [f-conjunction: 0]
    ├──  2. f: q [f-conjunction: 0]
    ├──  3. e: p [f-conjunction: 0]
    └──  4. e: q [f-conjunction: 0]
```

---

### m : (φ ∧ ψ) → complex branching for t and f results.
*Test: TestFergusonConjunctionRules::test_m_conjunction_complex_branching*

Formula: `p & q`
Sign: m

```
Satisfiable: True

Tableau tree:
 0. m: p & q
    ├──  1. t: p [m-conjunction: 0]
    ├──  2. t: q [m-conjunction: 0]
    ├──  3. f: p [m-conjunction: 0]
    └──  4. f: q [m-conjunction: 0]
```

---

### n : (φ ∧ ψ) → branches for f and e results.
*Test: TestFergusonConjunctionRules::test_n_conjunction_nontrue_branching*

Formula: `p & q`
Sign: n

```
Satisfiable: True

Tableau tree:
 0. n: p & q
    ├──  1. f: p [n-conjunction: 0]
    ├──  2. f: q [n-conjunction: 0]
    ├──  3. e: p [n-conjunction: 0]
    └──  4. e: q [n-conjunction: 0]
```

---

### t : (φ ∧ ψ) → t : φ ○ t : ψ [only t ∧ t = t].
*Test: TestFergusonConjunctionRules::test_t_conjunction_rule*

Formula: `p & q`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: p & q
    ├──  1. t: p [t-conjunction: 0]
    └──  2. t: q [t-conjunction: 0]
```

---

### DisjunctionRules Tests

### e : (φ ∨ ψ) → (e : φ) + (e : ψ) [e is contagious].
*Test: TestFergusonDisjunctionRules::test_e_disjunction_contagion*

Formula: `p | q`
Sign: e

```
Satisfiable: True

Tableau tree:
 0. e: p | q
    ├──  1. e: p [e-disjunction: 0]
    └──  2. e: q [e-disjunction: 0]
```

---

### f : (φ ∨ ψ) → f : φ ○ f : ψ [only f ∨ f = f].
*Test: TestFergusonDisjunctionRules::test_f_disjunction_rule*

Formula: `p | q`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: p | q
    ├──  1. f: p [f-disjunction: 0]
    └──  2. f: q [f-disjunction: 0]
```

---

### t : (φ ∨ ψ) → (t : φ) + (t : ψ) [branches].
*Test: TestFergusonDisjunctionRules::test_t_disjunction_branching*

Formula: `p | q`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: p | q
    ├──  1. t: p [t-disjunction: 0]
    └──  2. t: q [t-disjunction: 0]
```

---

## Ferguson's Negation Rules

### e : ~φ → e : φ (where ~e = e).
*Test: TestFergusonNegationRules::test_e_negation_rule*

Formula: `~p`
Sign: e

```
Satisfiable: True

Tableau tree:
 0. e: ~p
    └──  1. e: p [e-negation: 0]
```

---

### f : ~φ → t : φ (where ~f = t).
*Test: TestFergusonNegationRules::test_f_negation_rule*

Formula: `~p`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: ~p
    └──  1. t: p [f-negation: 0]
```

---

### m : ~φ → (f : φ) + (t : φ) [branches for meaningful].
*Test: TestFergusonNegationRules::test_m_negation_branching*

Formula: `~p`
Sign: m

```
Satisfiable: True

Tableau tree:
 0. m: ~p
    ├──  1. f: p [m-negation: 0]
    └──  2. t: p [m-negation: 0]
```

---

### n : ~φ → (t : φ) + (e : φ) [branches for nontrue].
*Test: TestFergusonNegationRules::test_n_negation_branching*

Formula: `~p`
Sign: n

```
Satisfiable: True

Tableau tree:
 0. n: ~p
    ├──  1. t: p [n-negation: 0]
    └──  2. e: p [n-negation: 0]
```

---

### t : ~φ → f : φ (where ~t = f).
*Test: TestFergusonNegationRules::test_t_negation_rule*

Formula: `~p`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: ~p
    └──  1. f: p [t-negation: 0]
```

---

## Ferguson's Quantifier Rules

### f : [∃x φ(x)]ψ(x) → complex branching with m and n.
*Test: TestFergusonRestrictedQuantifierRules::test_f_restricted_exists_complex_branching*

Formula: `[exists X Human(X)]Mortal(X)`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: [∃X Human(X)]Mortal(X)
    ├──  1. m: Human(c_1)         [f-restricted-exists: 0]
    ├──  2. m: Mortal(c_1)        [f-restricted-exists: 0]
    ├──  3. n: Human(c_1_arb)     [f-restricted-exists: 0]
    ├──  4. m: Human(c_1)         [f-restricted-exists: 0]
    ├──  5. m: Mortal(c_1)        [f-restricted-exists: 0]
    └──  6. n: Mortal(c_1_arb)    [f-restricted-exists: 0]
```

---

### f : [∀x φ(x)]ψ(x) → t : φ(c) ○ f : ψ(c) [counterexample].
*Test: TestFergusonRestrictedQuantifierRules::test_f_restricted_forall_counterexample*

Formula: `[forall X Human(X)]Mortal(X)`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: [∀X Human(X)]Mortal(X)
    ├──  1. t: Human(c_1)         [f-restricted-forall: 0]
    └──  2. f: Mortal(c_1)        [f-restricted-forall: 0]
```

---

### t : [∃x φ(x)]ψ(x) → t : φ(c) ○ t : ψ(c).
*Test: TestFergusonRestrictedQuantifierRules::test_t_restricted_exists_rule*

Formula: `[exists X Human(X)]Mortal(X)`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: [∃X Human(X)]Mortal(X)
    ├──  1. t: Human(c_1)         [t-restricted-exists: 0]
    └──  2. t: Mortal(c_1)        [t-restricted-exists: 0]
```

---

### t : [∀x φ(x)]ψ(x) → (f : φ(c)) + (t : ψ(c)).
*Test: TestFergusonRestrictedQuantifierRules::test_t_restricted_forall_branching*

Formula: `[forall X Human(X)]Mortal(X)`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: [∀X Human(X)]Mortal(X)
    ├──  1. f: Human(c_1)         [t-restricted-forall: 0]
    └──  2. t: Mortal(c_1)        [t-restricted-forall: 0]
```

---

## Ferguson's Six-Sign System

### e sign constrains formula to truth value e (undefined).
*Test: TestFergusonSixSignSystem::test_sign_e_constrains_to_undefined*

Formula: `p`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e}
```

*Test expects:* Satisfiable: True

---

### f sign constrains formula to truth value f.
*Test: TestFergusonSixSignSystem::test_sign_f_constrains_to_false*

Formula: `p`
Sign: f

```
Satisfiable: True
Models (1):
  1. {p=f}
```

*Test expects:* Satisfiable: True

---

### m sign creates branches for both t and f (meaningful).
*Test: TestFergusonSixSignSystem::test_sign_m_branches_for_meaningful*

Formula: `p & q`
Sign: m

```
Satisfiable: True

Tableau tree:
 0. m: p & q
    ├──  1. t: p [m-conjunction: 0]
    ├──  2. t: q [m-conjunction: 0]
    ├──  3. f: p [m-conjunction: 0]
    └──  4. f: q [m-conjunction: 0]
```

---

### n sign creates branches for both f and e (nontrue).
*Test: TestFergusonSixSignSystem::test_sign_n_branches_for_nontrue*

Formula: `p & q`
Sign: n

```
Satisfiable: True

Tableau tree:
 0. n: p & q
    ├──  1. f: p [n-conjunction: 0]
    ├──  2. f: q [n-conjunction: 0]
    ├──  3. e: p [n-conjunction: 0]
    └──  4. e: q [n-conjunction: 0]
```

---

### t sign constrains formula to truth value t.
*Test: TestFergusonSixSignSystem::test_sign_t_constrains_to_true*

Formula: `p`
Sign: t

```
Satisfiable: True
Models (1):
  1. {p=t}
```

*Test expects:* Satisfiable: True

---

## Ferguson's Tableau System

### ComplexExamples Tests

### Epistemic uncertainty about logical truth (m sign on tautology).
*Test: TestComplexFergusonExamples::test_epistemic_uncertainty_about_logical_truth*

Formula: `p | ~p`
Sign: m

```
Satisfiable: True

Tableau tree:
 0. m: p | (~p)
    ├──  1. t: p    [m-disjunction: 0]
    ├──  2. t: ~p   [m-disjunction: 0]
    ├──  3. f: p    [m-disjunction: 0]
    └──  4. f: ~p   [m-disjunction: 0]
```

---

### Knowledge gap representation (n sign).
*Test: TestComplexFergusonExamples::test_knowledge_gap_representation*

Formula: `Human(alice) -> Mortal(alice)`
Sign: n

```
Satisfiable: True

Tableau tree:
 0. n: Human(alice) -> Mortal(alice)
    ├──  1. t: Human(alice)              [n-implication: 0]
    ├──  2. f: Mortal(alice)             [n-implication: 0]
    ├──  3. e: Human(alice)              [n-implication: 0]
    └──  4. e: Mortal(alice)             [n-implication: 0]
```

---

### Interaction of quantifiers with three-valued logic.
*Test: TestComplexFergusonExamples::test_quantifiers_with_three_valued_logic*

Formula: `[forall X Human(X)]Mortal(X) & [exists Y ~Mortal(Y)]Robot(Y)`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: [∀X Human(X)]Mortal(X) & [∃Y ~Mortal(Y)]Robot(Y)
    ├──  1. t: [∀X Human(X)]Mortal(X)                       [t-conjunction: 0]
    │   ├──  6. f: Human(c_3)                               [t-restricted-forall: 1]
    │   └──  7. t: Mortal(c_3)                              [t-restricted-forall: 1]
    └──  2. t: [∃Y ~Mortal(Y)]Robot(Y)                      [t-conjunction: 0]
        ├──  3. t: ~Mortal(c_3)                             [t-restricted-exists: 2]
        │   └──  5. f: Mortal(c_3)                          [t-negation: 3]
        └──  4. t: Robot(c_3)                               [t-restricted-exists: 2]
```

---

### BranchClosure Tests

### Branch closes when f:φ and e:φ appear.
*Test: TestFergusonBranchClosure::test_branch_closure_f_e*

Formula: `(p & ~p) | ~(p & ~p)`
Sign: f

```
Satisfiable: False

Tableau tree:
 0. f: (p & (~p)) | (~(p & (~p)))
    ├──  1. f: p & (~p)  ×            [f-disjunction: 0]
    └──  2. f: ~(p & (~p))            [f-disjunction: 0]
        └──  3. t: p & (~p)  ×        [f-negation: 2]
```

---

### Branch closes when t:φ and e:φ appear.
*Test: TestFergusonBranchClosure::test_branch_closure_t_e*

Formula: `(p | ~p) & ~(p | ~p)`
Sign: t

```
Satisfiable: False

Tableau tree:
 0. t: (p | (~p)) & (~(p | (~p)))
    ├──  1. t: p | (~p)  ×            [t-conjunction: 0]
    └──  2. t: ~(p | (~p))            [t-conjunction: 0]
        └──  3. f: p | (~p)  ×        [t-negation: 2]
```

---

### Branch closes when t:φ and f:φ appear (distinct v, u ∈ {t,f,e}).
*Test: TestFergusonBranchClosure::test_branch_closure_t_f*

Formula: `p & ~p`
Sign: t

```
Satisfiable: False

Tableau tree:
 0. t: p & (~p)
    ├──  1. t: p  ×     [t-conjunction: 0]
    └──  2. t: ~p       [t-conjunction: 0]
        └──  3. f: p  × [t-negation: 2]
```

---

### ImplicationRules Tests

### e : (φ → ψ) → (e : φ) + (e : ψ) [e propagates].
*Test: TestFergusonImplicationRules::test_e_implication_contagion*

Formula: `p -> q`
Sign: e

```
Satisfiable: True

Tableau tree:
 0. e: p -> q
    ├──  1. e: p  [e-implication: 0]
    └──  2. e: q  [e-implication: 0]
```

---

### f : (φ → ψ) → t : φ ○ f : ψ [~φ = f means φ = t].
*Test: TestFergusonImplicationRules::test_f_implication_rule*

Formula: `p -> q`
Sign: f

```
Satisfiable: True

Tableau tree:
 0. f: p -> q
    ├──  1. t: p  [f-implication: 0]
    └──  2. f: q  [f-implication: 0]
```

---

### t : (φ → ψ) → (f : φ) + (t : ψ) [~φ = t means φ = f].
*Test: TestFergusonImplicationRules::test_t_implication_branching*

Formula: `p -> q`
Sign: t

```
Satisfiable: True

Tableau tree:
 0. t: p -> q
    ├──  1. f: p  [t-implication: 0]
    └──  2. t: q  [t-implication: 0]
```

---

## Miscellaneous Tests

### ComplexRealWorldScenarios Tests

### Database reconciliation with conflicts.
*Test: TestComplexRealWorldScenarios::test_database_reconciliation*

Formula: `(Age(person, 25) & Age(person, 26)) & (Age(person, 25) -> Eligible(person, youth_program))`
Mode: acrq

```
ACrQ Formula (transparent mode): (Age(person, 25) & Age(person, 26)) & (Age(person, 25) -> Eligible(person, youth_program))
Sign: t
Satisfiable: True

Models (1):
  1. {Age(person, 25)=e, Age(person, 26)=e, Eligible(person, youth_program)=e}

Tableau tree:
 0. t: (Age(person, 25) & Age(person, 26)) & (Age(person, 25) -> Eligible(person, youth_program))
    ├──  1. t: Age(person, 25) & Age(person, 26)                                                      [t-conjunction: 0]
    └──  2. t: Age(person, 25) -> Eligible(person, youth_program)                                     [t-conjunction: 0]
```

*Test expects:* Satisfiable: True

---

### Legal reasoning with conflicting testimony.
*Test: TestComplexRealWorldScenarios::test_legal_reasoning_with_conflicts*

Formula: `(Witness(john, alibi) & ~Witness(john, alibi)) & (Evidence(dna, present) -> Guilty(suspect))`
Mode: acrq

```
ACrQ Formula (transparent mode): (Witness(john, alibi) & Witness*(john, alibi)) & (Evidence(dna, present) -> Guilty(suspect))
Sign: t
Satisfiable: True

Models (1):
  1. {Evidence(dna, present)=e, Guilty(suspect)=e, Witness(john, alibi)=e, Witness*(john, alibi)=e}

Tableau tree:
 0. t: (Witness(john, alibi) & Witness*(john, alibi)) & (Evidence(dna, present) -> Guilty(suspect))
    ├──  1. t: Witness(john, alibi) & Witness*(john, alibi)                                             [t-conjunction: 0]
    └──  2. t: Evidence(dna, present) -> Guilty(suspect)                                                [t-conjunction: 0]
```

*Test expects:* Satisfiable: True

---

### Medical diagnosis with contradictory symptoms.
*Test: TestComplexRealWorldScenarios::test_medical_diagnosis_contradictory_symptoms*

Formula: `Symptom(patient, fever), ~Symptom(patient, fever), [forall X (Symptom(X, fever) & ~~Symptom(X, fever))]Flu(X) |- Flu(patient)`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: Symptom(patient, fever), Symptom*(patient, fever), [∀X Symptom(X, fever) & (~Symptom*(X, fever))]Flu(X)
  Conclusion: Flu(patient)
  ✗ Invalid inference
  Countermodels:
    1. {Flu(fever)=t, Flu(patient)=f, Symptom(patient, fever)=t, Symptom*(patient, fever)=t}
    2. {Flu(patient)=f, Symptom(fever, fever)=f, Symptom(patient, fever)=t, Symptom*(fever, fever)=e, Symptom*(patient, fever)=t}
    3. {Flu(patient)=f, Symptom(fever, fever)=e, Symptom(patient, fever)=t, Symptom*(fever, fever)=e, Symptom*(patient, fever)=t}
```

*Test expects:* ✗ Invalid inference

---

### Sensor fusion with noisy readings.
*Test: TestComplexRealWorldScenarios::test_sensor_fusion_noisy_readings*

Formula: `Temp(sensor1, high), ~Temp(sensor1, high), Temp(sensor2, high), (Temp(sensor2, high) -> Alert(fire)) |- Alert(fire)`
Mode: acrq

```
ACrQ Inference (transparent mode):
  Premises: Temp(sensor1, high), Temp*(sensor1, high), Temp(sensor2, high), Temp(sensor2, high) -> Alert(fire)
  Conclusion: Alert(fire)
  ✓ Valid inference
```

*Test expects:* ✓ Valid inference

---

### EdgeCasesAndStresss Tests

### Complex restricted quantifier inference.
*Test: TestEdgeCasesAndStressTests::test_complex_restricted_quantifier_inference*

Formula: `[forall X Person(X)]HasParent(X), [forall Y HasParent(Y)]NeedsCare(Y) |- [forall Z Person(Z)]NeedsCare(Z)`

```
✓ Valid inference

Tableau tree:
 0. t: ([∀X Person(X)]HasParent(X) & [∀Y HasParent(Y)]NeedsCare(Y)) & (~[∀Z Person(Z)]NeedsCare(Z))
    ├──  1. t: [∀X Person(X)]HasParent(X) & [∀Y HasParent(Y)]NeedsCare(Y)                               [t-conjunction: 0]
    │   ├──  3. t: [∀X Person(X)]HasParent(X)                                                           [t-conjunction: 1]
    │   │   ├──  8. f: Person(c_6)  ×                                                                   [t-restricted-forall: 3]
    │   │   └──  9. t: HasParent(c_6)  ×                                                                [t-restricted-forall: 3]
    │   └──  4. t: [∀Y HasParent(Y)]NeedsCare(Y)                                                        [t-conjunction: 1]
    │       ├── 10. f: HasParent(c_6)  ×                                                                [t-restricted-forall: 4]
    │       └── 11. t: NeedsCare(c_6)  ×                                                                [t-restricted-forall: 4]
    └──  2. t: ~[∀Z Person(Z)]NeedsCare(Z)                                                              [t-conjunction: 0]
        └──  5. f: [∀Z Person(Z)]NeedsCare(Z)                                                           [t-negation: 2]
            ├──  6. t: Person(c_6)  ×                                                                   [f-restricted-forall: 5]
            └──  7. f: NeedsCare(c_6)  ×                                                                [f-restricted-forall: 5]
```

*Test expects:* ✓ Valid inference

---

### Empty domain quantification.
*Test: TestEdgeCasesAndStressTests::test_empty_domain_quantification*

Formula: `[forall X Unicorn(X)]HasHorn(X), ~[exists Y True(Y)]Unicorn(Y) |- [forall Z False(Z)]True(Z)`

```
✗ Invalid inference
Countermodels:
  1. {False(c_7)=t, HasHorn(c_7)=t, True(c_10)=t, True(c_7)=f, Unicorn(c_10)=f, Unicorn(c_7)=f}
  2. {False(c_7)=t, HasHorn(c_10)=t, HasHorn(c_7)=t, True(c_10)=t, True(c_7)=f, Unicorn(c_10)=t, Unicorn(c_7)=f}

Tableau tree:
 0. t: ([∀X Unicorn(X)]HasHorn(X) & (~[∃Y True(Y)]Unicorn(Y))) & (~[∀Z False(Z)]True(Z))
    ├──  1. t: [∀X Unicorn(X)]HasHorn(X) & (~[∃Y True(Y)]Unicorn(Y))                         [t-conjunction: 0]
    │   ├──  3. t: [∀X Unicorn(X)]HasHorn(X)                                                 [t-conjunction: 1]
    │   │   ├──  9. f: Unicorn(c_7)                                                          [t-restricted-forall: 3]
    │   │   ├── 10. t: HasHorn(c_7)                                                          [t-restricted-forall: 3]
    │   │   ├── 23. f: Unicorn(c_10)                                                         [t-restricted-forall: 3]
    │   │   └── 24. t: HasHorn(c_10)                                                         [t-restricted-forall: 3]
    │   └──  4. t: ~[∃Y True(Y)]Unicorn(Y)                                                   [t-conjunction: 1]
    │       └──  6. f: [∃Y True(Y)]Unicorn(Y)                                                [t-negation: 4]
    │           ├── 11. m: True(c_10)                                                        [f-restricted-exists: 6]
    │           ├── 12. m: Unicorn(c_10)                                                     [f-restricted-exists: 6]
    │           ├── 13. n: True(c_7)                                                         [f-restricted-exists: 6]
    │           ├── 14. m: True(c_10)                                                        [f-restricted-exists: 6]
    │           ├── 15. m: Unicorn(c_10)                                                     [f-restricted-exists: 6]
    │           ├── 16. n: Unicorn(c_7)                                                      [f-restricted-exists: 6]
    │           ├── 17. m: True(c_10)                                                        [f-restricted-exists: 6]
    │           ├── 18. m: Unicorn(c_10)                                                     [f-restricted-exists: 6]
    │           ├── 19. n: True(c_7)                                                         [f-restricted-exists: 6]
    │           ├── 20. m: True(c_10)                                                        [f-restricted-exists: 6]
    │           ├── 21. m: Unicorn(c_10)                                                     [f-restricted-exists: 6]
    │           └── 22. n: Unicorn(c_7)                                                      [f-restricted-exists: 6]
    └──  2. t: ~[∀Z False(Z)]True(Z)                                                         [t-conjunction: 0]
        └──  5. f: [∀Z False(Z)]True(Z)                                                      [t-negation: 2]
            ├──  7. t: False(c_7)                                                            [f-restricted-forall: 5]
            └──  8. f: True(c_7)                                                             [f-restricted-forall: 5]
```

*Test expects:* ✗ Invalid inference

---

### Large disjunction satisfiability.
*Test: TestEdgeCasesAndStressTests::test_large_disjunction_satisfiability*

Formula: `p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10`
Sign: t

```
Satisfiable: True
Models (2):
  1. {p1=e, p10=e, p2=e, p3=e, p4=e, p5=e, p6=e, p7=e, p8=e, p9=e}
  2. {p1=e, p10=t, p2=e, p3=e, p4=e, p5=e, p6=e, p7=e, p8=e, p9=e}
```

*Test expects:* Satisfiable: True

---

### Maximum formula nesting.
*Test: TestEdgeCasesAndStressTests::test_maximum_formula_nesting*

Formula: `((((p -> q) -> r) -> s) -> t) -> u`

```
Satisfiable: True
Models (2):
  1. {p=e, q=e, r=e, s=e, t=e, u=e}
  2. {p=e, q=e, r=e, s=e, t=e, u=t}

Tableau tree:
 0. t: ((((p -> q) -> r) -> s) -> t) -> u
    ├──  1. f: (((p -> q) -> r) -> s) -> t    [t-implication: 0]
    └──  2. t: u                              [t-implication: 0]
```

*Test expects:* Satisfiable: True

---

### InvalidInferences Tests

### Affirming the Consequent: q, p → q ⊬ p.
*Test: TestInvalidInferences::test_affirming_the_consequent*

Formula: `q, (p -> q) |- p`

```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}

Tableau tree:
 0. t: (q & (p -> q)) & (~p)
    ├──  1. t: q & (p -> q)      [t-conjunction: 0]
    │   ├──  3. t: q             [t-conjunction: 1]
    │   └──  4. t: p -> q        [t-conjunction: 1]
    └──  2. t: ~p                [t-conjunction: 0]
        └──  5. f: p             [t-negation: 2]
```

*Test expects:* ✗ Invalid inference

---

### Denying the Antecedent: ¬p, p → q ⊬ ¬q.
*Test: TestInvalidInferences::test_denying_the_antecedent*

Formula: `~p, (p -> q) |- ~q`

```
✗ Invalid inference
Countermodels:
  1. {p=f, q=t}

Tableau tree:
 0. t: ((~p) & (p -> q)) & (~(~q))
    ├──  1. t: (~p) & (p -> q)         [t-conjunction: 0]
    │   ├──  3. t: ~p                  [t-conjunction: 1]
    │   │   └──  6. f: p               [t-negation: 3]
    │   └──  4. t: p -> q              [t-conjunction: 1]
    └──  2. t: ~(~q)                   [t-conjunction: 0]
        └──  5. f: ~q                  [t-negation: 2]
            └──  7. t: q               [f-negation: 5]
```

*Test expects:* ✗ Invalid inference

---

### Invalid Existential: Some A are B ⊬ All A are B.
*Test: TestInvalidInferences::test_invalid_existential_generalization*

Formula: `[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)`

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

*Test expects:* ✗ Invalid inference

---

### Fallacy of the Undistributed Middle: All A are B, All C are B ⊬ All A are C.
*Test: TestInvalidInferences::test_undistributed_middle*

Formula: `[forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)`

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

*Test expects:* ✗ Invalid inference

---

### MAndNBranchingBehavior Tests

### m creates branches exploring both t and f possibilities.
*Test: TestMAndNBranchingBehavior::test_m_creates_meaningful_branches*

Formula: `(p -> q) & (q -> r)`
Sign: m

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

### m on atomic formula (no rule to apply, model chooses value).
*Test: TestMAndNBranchingBehavior::test_m_on_atomic_formula*

Formula: `p`
Sign: m

```
Satisfiable: True
Models (1):
  1. {p=t}
```

*Test expects:* Satisfiable: True

---

### n creates branches exploring both f and e possibilities.
*Test: TestMAndNBranchingBehavior::test_n_creates_nontrue_branches*

Formula: `(p | q) -> r`
Sign: n

```
Satisfiable: True

Tableau tree:
 0. n: (p | q) -> r
    ├──  1. t: p | q    [n-implication: 0]
    ├──  2. f: r        [n-implication: 0]
    ├──  3. e: p | q    [n-implication: 0]
    │   ├──  5. e: p    [e-disjunction: 3]
    │   └──  6. e: q    [e-disjunction: 3]
    └──  4. e: r        [n-implication: 0]
```

---

### RelatedIssues Tests

### Test multiple (non-nested) quantifier behavior.
*Test: TestRelatedIssues::test_multiple_quantifiers*

Formula: `[forall X P(X)]Q(X), [exists Y Q(Y)]R(Y) |- [exists Z P(Z)]R(Z)`

```
✗ Invalid inference
Countermodels:
  1. {P(c_6)=f, P(c_8)=f, Q(c_6)=t, R(c_6)=t, R(c_8)=t}
  2. {P(c_6)=f, P(c_8)=t, Q(c_6)=t, Q(c_8)=t, R(c_6)=t, R(c_8)=t}
```

*Test expects:* ✗ Invalid inference

---

### Test complex quantifier scope interactions.
*Test: TestRelatedIssues::test_quantifier_scope_interactions*

Formula: `[exists X P(X)][exists Y Q(Y)] |- [exists Z (P(Z) & Q(Z))]`

```

```

*Test expects:* ✗ Invalid inference

---

### RelevanceLogicProperties Tests

### Ex falso quodlibet holds vacuously when premise is constrained true.
*Test: TestRelevanceLogicProperties::test_ex_falso_quodlibet_vacuous*

Formula: `(p & ~p) |- q`

```
✓ Valid inference

Tableau tree:
 0. t: (p & (~p)) & (~q)
    ├──  1. t: p & (~p)      [t-conjunction: 0]
    │   ├──  3. t: p  ×      [t-conjunction: 1]
    │   └──  4. t: ~p        [t-conjunction: 1]
    │       └──  6. f: p  ×  [t-negation: 4]
    └──  2. t: ~q            [t-conjunction: 0]
        └──  5. f: q  ×      [t-negation: 2]
```

*Test expects:* ✓ Valid inference

---

### Relevant Modus Ponens: p, p → q ⊢ q (shared variable).
*Test: TestRelevanceLogicProperties::test_relevant_modus_ponens*

Formula: `p, (p -> q) |- q`

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

*Test expects:* ✓ Valid inference

---

### Variable sharing fails in relevance logic but holds in wKrQ.
*Test: TestRelevanceLogicProperties::test_variable_sharing_principle_holds_classically*

Formula: `p |- (q -> q)`

```
✓ Valid inference

Tableau tree:
 0. t: p & (~(q -> q))
    ├──  1. t: p  ×         [t-conjunction: 0]
    └──  2. t: ~(q -> q)    [t-conjunction: 0]
        └──  3. f: q -> q   [t-negation: 2]
            ├──  4. t: q  × [f-implication: 3]
            └──  5. f: q  × [f-implication: 3]
```

*Test expects:* ✓ Valid inference

---

### SoundnessAndCompleteness Tests

### Complex valid inference.
*Test: TestSoundnessAndCompleteness::test_complex_valid_inference*

Formula: `(p -> q) & (q -> r), p | s, ~s |- r`

```
✓ Valid inference

Tableau tree:
 0. t: ((((p -> q) & (q -> r)) & (p | s)) & (~s)) & (~r)
    ├──  1. t: (((p -> q) & (q -> r)) & (p | s)) & (~s)      [t-conjunction: 0]
    │   ├──  3. t: ((p -> q) & (q -> r)) & (p | s)           [t-conjunction: 1]
    │   │   ├──  6. t: (p -> q) & (q -> r)                   [t-conjunction: 3]
    │   │   │   ├──  9. t: p -> q                            [t-conjunction: 6]
    │   │   │   │   ├── 13. f: p  ×                          [t-implication: 9]
    │   │   │   │   └── 14. t: q  ×                          [t-implication: 9]
    │   │   │   └── 10. t: q -> r                            [t-conjunction: 6]
    │   │   │       ├── 15. f: q  ×                          [t-implication: 10]
    │   │   │       └── 16. t: r  ×                          [t-implication: 10]
    │   │   └──  7. t: p | s                                 [t-conjunction: 3]
    │   │       ├── 11. t: p  ×                              [t-disjunction: 7]
    │   │       └── 12. t: s  ×                              [t-disjunction: 7]
    │   └──  4. t: ~s                                        [t-conjunction: 1]
    │       └──  8. f: s  ×                                  [t-negation: 4]
    └──  2. t: ~r                                            [t-conjunction: 0]
        └──  5. f: r  ×                                      [t-negation: 2]
```

*Test expects:* ✓ Valid inference

---

### Invalid inference correctly rejected.
*Test: TestSoundnessAndCompleteness::test_invalid_inference_rejected*

Formula: `p -> q |- q`

```
✗ Invalid inference
Countermodels:
  1. {p=f, q=f}

Tableau tree:
 0. t: (p -> q) & (~q)
    ├──  1. t: p -> q      [t-conjunction: 0]
    │   ├──  4. f: p       [t-implication: 1]
    │   └──  5. t: q       [t-implication: 1]
    └──  2. t: ~q          [t-conjunction: 0]
        └──  3. f: q       [t-negation: 2]
```

*Test expects:* ✗ Invalid inference

---

### Modus ponens is sound.
*Test: TestSoundnessAndCompleteness::test_modus_ponens_sound*

Formula: `p, p -> q |- q`

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

*Test expects:* ✓ Valid inference

---

## Model Theory

### Models for e sign show undefined values.
*Test: TestModelExtraction::test_models_for_e_sign*

Formula: `p | q`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e, q=e}
```

*Test expects:* Satisfiable: True

---

### Models for n sign show nontrue values (f or e).
*Test: TestModelExtraction::test_models_for_n_sign*

Formula: `p`
Sign: n

```
Satisfiable: True
Models (1):
  1. {p=f}
```

*Test expects:* Satisfiable: True

---

### Models reflect sign semantics (t:p produces p=true).
*Test: TestModelExtraction::test_models_reflect_sign_semantics*

Formula: `p & (q | r)`
Sign: t

```
Satisfiable: True
Models (2):
  1. {p=t, q=t, r=e}
  2. {p=t, q=e, r=t}
```

*Test expects:* Satisfiable: True

---

## Quantifier Logic

### QuantifierBug Tests

### [∃X A(X)]B(X) ⊬ [∀Y A(Y)]B(Y) - should be invalid.
*Test: TestQuantifierBug::test_existential_to_universal_invalid*

Formula: `[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)`

```
✗ Invalid inference
Countermodels:
  1. {A(c_3)=t, A(c_6)=t, B(c_3)=t, B(c_6)=f}
```

*Test expects:* ✗ Invalid inference

---

### With explicit domain elements, should still be invalid.
*Test: TestQuantifierBug::test_existential_to_universal_with_explicit_domain*

Formula: `[exists X A(X)]B(X), A(c), A(d) |- [forall Y A(Y)]B(Y)`

```
✗ Invalid inference
Countermodels:
  1. {A(c)=t, A(c_10)=t, A(c_8)=t, A(d)=t, B(c_10)=t, B(c_8)=f}
```

*Test expects:* ✗ Invalid inference

---

### Invalid syllogism should be correctly identified.
*Test: TestQuantifierBug::test_invalid_syllogism*

Formula: `[forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)`

```
✗ Invalid inference
Countermodels:
  1. {A(c_6)=t, B(c_6)=t, C(c_6)=f}
```

*Test expects:* ✗ Invalid inference

---

### Mixed quantifier inference that should be invalid.
*Test: TestQuantifierBug::test_mixed_quantifiers*

Formula: `[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)`

```
✗ Invalid inference
Countermodels:
  1. {Smart(alice)=f, Smart(c_6)=t, Student(alice)=t, Student(c_6)=t}
```

*Test expects:* ✗ Invalid inference

---

### Valid universal instantiation should still work.
*Test: TestQuantifierBug::test_valid_universal_instantiation*

Formula: `[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)`

```
✓ Valid inference
```

*Test expects:* ✓ Valid inference

---

### QuantifierBugAnalysis Tests

### Trace through the fixed inference to verify correct behavior.
*Test: TestQuantifierBugAnalysis::test_trace_fixed_inference*

Formula: `[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)`

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

*Test expects:* ✗ Invalid inference

---

### QuantifierInference Tests

### Some student smart, Alice student ⊬ Alice smart.
*Test: TestQuantifierInference::test_existential_witness_invalid*

Formula: `[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)`

```
✗ Invalid inference
Countermodels:
  1. {Smart(alice)=f, Smart(c_6)=t, Student(alice)=t, Student(c_6)=t}

Tableau tree:
 0. t: ([∃X Student(X)]Smart(X) & Student(alice)) & (~Smart(alice))
    ├──  1. t: [∃X Student(X)]Smart(X) & Student(alice)                 [t-conjunction: 0]
    │   ├──  3. t: [∃X Student(X)]Smart(X)                              [t-conjunction: 1]
    │   │   ├──  6. t: Student(c_6)                                     [t-restricted-exists: 3]
    │   │   └──  7. t: Smart(c_6)                                       [t-restricted-exists: 3]
    │   └──  4. t: Student(alice)                                       [t-conjunction: 1]
    └──  2. t: ~Smart(alice)                                            [t-conjunction: 0]
        └──  5. f: Smart(alice)                                         [t-negation: 2]
```

*Test expects:* ✗ Invalid inference

---

### All humans mortal, Socrates human ⊢ Socrates mortal.
*Test: TestQuantifierInference::test_standard_syllogism*

Formula: `[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)`

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

*Test expects:* ✓ Valid inference

---

## Weak Kleene Semantics

### Classical tautologies can be undefined (NOT valid).
*Test: TestWeakKleeneSemantics::test_classical_tautology_can_be_undefined*

Formula: `p | ~p`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e}
```

*Test expects:* Satisfiable: True

---

### f ∧ e = e - undefined is contagious.
*Test: TestWeakKleeneSemantics::test_conjunction_with_undefined_contagion*

Formula: `p & q`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e, q=e}
```

*Test expects:* Satisfiable: True

---

### t ∨ e = e (NOT t) - distinguishes weak from strong Kleene.
*Test: TestWeakKleeneSemantics::test_disjunction_with_undefined_contagion*

Formula: `p | q`
Sign: e

```
Satisfiable: True
Models (1):
  1. {p=e, q=e}
```

*Test expects:* Satisfiable: True

---

### p ∨ ¬p is NOT valid (can be e) but cannot be false.
*Test: TestWeakKleeneSemantics::test_excluded_middle_cannot_be_false*

Formula: `p | ~p`
Sign: f

```
Satisfiable: False

Tableau tree:
 0. f: p | (~p)
    ├──  1. f: p  ×
    └──  2. f: ~p
        └──  3. t: p  ×
```

*Test expects:* Satisfiable: False

---

