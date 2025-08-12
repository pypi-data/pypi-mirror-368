# wKrQ Test Formulas Quick Reference


## Ferguson Six-Sign System

- [SAT] `p` - Sign t constrains to true
- [SAT] `p | ~p` - Sign m allows both true and false

## Ferguson Negation Rules

- [✗] `~p |- q` - t-negation: t:¬φ leads to f:φ

## Weak Kleene Semantics

- [SAT] `(p | q)` - Undefined is contagious in disjunction
- [SAT] `p | ~p` - Classical tautology can be undefined

## Restricted Quantifiers

- [✓] `[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)` - Universal instantiation (valid)
- [✗] `[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)` - Existential to universal (invalid) - THE BUG WE FIXED

## Classical Inferences

- [✓] `p, p -> q |- q` - Modus Ponens
- [✓] `p -> q, ~q |- ~p` - Modus Tollens
- [✓] `p -> q, q -> r |- p -> r` - Hypothetical Syllogism

## Invalid Inferences

- [✗] `p -> q, q |- p` - Affirming the Consequent
- [✗] `p -> q, ~p |- ~q` - Denying the Antecedent

## Aristotelian Syllogisms

- [✓] `[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)` - Barbara: All M are P, All S are M ⊢ All S are P
- [✓] `[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))` - Celarent: No M are P, All S are M ⊢ No S are P

## De Morgan's Laws

- [✓] `~(p & q) |- (~p | ~q)` - ¬(p ∧ q) ⊢ ¬p ∨ ¬q
- [✓] `~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))` - Quantified De Morgan (now valid after our fix)

## ACrQ Paraconsistent Reasoning

- [✗] `Symptom(patient, fever) & ~Symptom(patient, fever) |- Unrelated(claim)` - Knowledge gluts don't explode
- [?] `P(a) & P*(a)` - Local inconsistency preserved
