#!/usr/bin/env python3
"""
ACrQ (Analytic Containment with restricted Quantification) Demo

This demonstrates the ACrQ tableau system from Ferguson (2021) Definition 18.
ACrQ extends wKrQ with bilateral predicates for paraconsistent reasoning.
"""

from wkrq import (
    Formula,
    PredicateFormula,
    SignedFormula,
    parse,
    parse_acrq_formula,
    t,
    f,
    e,
)
from wkrq.acrq_tableau import ACrQTableau
from wkrq.formula import BilateralPredicateFormula


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def demonstrate_acrq():
    """Demonstrate key features of ACrQ."""
    
    print("ACrQ DEMONSTRATION")
    print("Based on Ferguson (2021) Definition 18")
    
    # 1. Negation elimination is dropped
    print_section("1. ACrQ drops general negation elimination")
    
    # In wKrQ, ~(p & q) would be decomposed by negation elimination
    # In ACrQ, it remains as is
    formula = parse("~(p & q)")
    tableau = ACrQTableau([SignedFormula(t, formula)])
    result = tableau.construct()
    
    print(f"Formula: {formula}")
    print(f"Satisfiable: {result.satisfiable}")
    print("Note: In ACrQ, compound negations are not eliminated")
    
    # 2. Bilateral predicates
    print_section("2. Bilateral predicates: ~R(x) → R*(x)")
    
    # ACrQ converts ~Human(alice) to Human*(alice)
    formula = parse_acrq_formula("~Human(alice)")
    tableau = ACrQTableau([SignedFormula(t, formula)])
    result = tableau.construct()
    
    print(f"Original: ~Human(alice)")
    print(f"Converted to: Human*(alice)")
    print(f"Satisfiable: {result.satisfiable}")
    
    # 3. Gluts are allowed
    print_section("3. Paraconsistent: Gluts (R ∧ R*) are allowed")
    
    # Both Human(alice) and Human*(alice) can be true (glut)
    human = PredicateFormula("Human", [Formula.constant("alice")])
    human_star = BilateralPredicateFormula(
        positive_name="Human",
        terms=[Formula.constant("alice")],
        is_negative=True
    )
    
    tableau = ACrQTableau([
        SignedFormula(t, human),
        SignedFormula(t, human_star)
    ])
    result = tableau.construct()
    
    print("t: Human(alice)")
    print("t: Human*(alice)")
    print(f"Satisfiable: {result.satisfiable} (Glut allowed!)")
    
    if result.models:
        model = result.models[0]
        print(f"Model: {model.valuations}")
    
    # 4. Standard contradictions still close
    print_section("4. Standard contradictions still close branches")
    
    # t:Human(alice) and f:Human(alice) is a contradiction
    tableau = ACrQTableau([
        SignedFormula(t, human),
        SignedFormula(f, human)
    ])
    result = tableau.construct()
    
    print("t: Human(alice)")
    print("f: Human(alice)")
    print(f"Satisfiable: {result.satisfiable} (Standard contradiction)")
    
    # 5. Knowledge gaps
    print_section("5. Knowledge gaps (neither R nor R*)")
    
    # Both false = gap
    robot = PredicateFormula("Robot", [Formula.constant("alice")])
    robot_star = BilateralPredicateFormula(
        positive_name="Robot",
        terms=[Formula.constant("alice")],
        is_negative=True
    )
    
    tableau = ACrQTableau([
        SignedFormula(f, robot),
        SignedFormula(f, robot_star)
    ])
    result = tableau.construct()
    
    print("f: Robot(alice)")
    print("f: Robot*(alice)")
    print(f"Satisfiable: {result.satisfiable} (Gap allowed)")
    
    # 6. Complex reasoning
    print_section("6. Complex ACrQ reasoning")
    
    # Human(x) ∧ ¬Human(x) is satisfiable in ACrQ!
    from wkrq.formula import CompoundFormula
    conj = CompoundFormula("&", [
        human,
        CompoundFormula("~", [human])
    ])
    
    tableau = ACrQTableau([SignedFormula(t, conj)])
    result = tableau.construct()
    
    print(f"Formula: Human(alice) & ~Human(alice)")
    print(f"Satisfiable: {result.satisfiable}")
    print("This would explode in classical logic, but ACrQ handles it!")
    
    # Summary
    print_section("Summary: ACrQ vs wKrQ")
    print("1. ACrQ drops general negation elimination")
    print("2. Negated predicates become bilateral: ~R(x) → R*(x)")
    print("3. Gluts allowed: R(x) ∧ R*(x) is satisfiable")
    print("4. Gaps allowed: ¬R(x) ∧ ¬R*(x) is satisfiable")
    print("5. Paraconsistent: contradictions don't explode")
    print("6. Based on Ferguson (2021) Definition 18")


if __name__ == "__main__":
    demonstrate_acrq()