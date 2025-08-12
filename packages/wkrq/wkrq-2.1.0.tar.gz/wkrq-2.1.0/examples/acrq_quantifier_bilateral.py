#!/usr/bin/env python3
"""
ACrQ Quantifiers with Bilateral Predicates

Demonstrates proper ACrQ syntax where negated predicates become bilateral predicates.
In ACrQ:
- ~P(x) automatically becomes P*(x) in transparent mode
- Quantified formulas properly handle bilateral predicates
"""

from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t, f
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE


def test_quantified_negation():
    """Test: Universal quantifier with negated consequent"""
    print("\n" + "=" * 60)
    print("TEST 1: Universal with Negated Consequent")
    print("=" * 60)
    
    # In ACrQ, ~Mortal(X) becomes Mortal*(X)
    formula_str = "[∀X Human(X)]~Mortal(X)"
    formula = parse_acrq_formula(formula_str)
    
    print(f"\nInput:  {formula_str}")
    print(f"ACrQ:   {formula}")
    print("\nMeaning: All humans have negative evidence of mortality")
    
    formulas = [
        SignedFormula(t, formula),
        SignedFormula(t, parse_acrq_formula("Human(socrates)")),
    ]
    
    tableau = ACrQTableau(formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Derives Mortal*(socrates) - negative evidence of mortality")


def test_negated_restriction():
    """Test: Universal with negated restriction"""
    print("\n" + "=" * 60)
    print("TEST 2: Universal with Negated Restriction")
    print("=" * 60)
    
    # In ACrQ, ~Robot(X) becomes Robot*(X)
    formula_str = "[∀X ~Robot(X)]HasEmotions(X)"
    formula = parse_acrq_formula(formula_str)
    
    print(f"\nInput:  {formula_str}")
    print(f"ACrQ:   {formula}")
    print("\nMeaning: Everything with negative evidence of being a robot has emotions")
    
    formulas = [
        SignedFormula(t, formula),
        SignedFormula(t, parse_acrq_formula("~Robot(c3po)")),  # Becomes Robot*(c3po)
    ]
    
    tableau = ACrQTableau(formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Robot*(c3po) satisfies restriction, derives HasEmotions(c3po)")


def test_existential_with_negation():
    """Test: Existential with negated matrix"""
    print("\n" + "=" * 60)
    print("TEST 3: Existential with Negation")
    print("=" * 60)
    
    # In ACrQ, ~Flies(X) becomes Flies*(X)
    formula_str = "[∃X Penguin(X)]~Flies(X)"
    formula = parse_acrq_formula(formula_str)
    
    print(f"\nInput:  {formula_str}")
    print(f"ACrQ:   {formula}")
    print("\nMeaning: There exists a penguin with negative evidence of flying")
    
    formulas = [
        SignedFormula(t, formula),
    ]
    
    tableau = ACrQTableau(formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Creates witness with Penguin(c_1) ∧ Flies*(c_1)")


def test_complex_bilateral_quantifier():
    """Test: Complex formula with multiple negations"""
    print("\n" + "=" * 60)
    print("TEST 4: Complex Bilateral Quantifiers")
    print("=" * 60)
    
    # Multiple negations in quantified formula
    formula_str = "[∀X ~Villain(X) & ~Robot(X)]~Evil(X)"
    formula = parse_acrq_formula(formula_str)
    
    print(f"\nInput:  {formula_str}")
    print(f"ACrQ:   {formula}")
    print("\nMeaning: Everything with negative evidence of being a villain")
    print("         and negative evidence of being a robot")
    print("         has negative evidence of being evil")
    
    formulas = [
        SignedFormula(t, formula),
        SignedFormula(t, parse_acrq_formula("~Villain(batman)")),
        SignedFormula(t, parse_acrq_formula("~Robot(batman)")),
    ]
    
    tableau = ACrQTableau(formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Derives Evil*(batman) from Villain*(batman) ∧ Robot*(batman)")


def test_quantifier_duality():
    """Test: De Morgan's laws for quantifiers in ACrQ"""
    print("\n" + "=" * 60)
    print("TEST 5: Quantifier Duality in ACrQ")
    print("=" * 60)
    
    # Testing ~∀X P(X) vs ∃X ~P(X) in ACrQ
    formula1_str = "~[∀X Human(X)]Mortal(X)"
    formula2_str = "[∃X Human(X)]~Mortal(X)"
    
    formula1 = parse_acrq_formula(formula1_str)
    formula2 = parse_acrq_formula(formula2_str)
    
    print(f"\nFormula 1: {formula1_str}")
    print(f"ACrQ:      {formula1}")
    print(f"\nFormula 2: {formula2_str}")
    print(f"ACrQ:      {formula2}")
    print("\nTesting if negated universal implies existential with bilateral predicate")
    
    # Test if formula1 entails formula2
    formulas = [
        SignedFormula(t, formula1),
        SignedFormula(f, formula2),
    ]
    
    tableau = ACrQTableau(formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'VALID' if not result.satisfiable else 'INVALID'}")
    print("Analysis: In ACrQ, quantifier duality works with bilateral predicates")


def test_llm_with_bilateral_quantifiers():
    """Test: LLM evaluation with bilateral quantified formulas"""
    print("\n" + "=" * 60)
    print("TEST 6: LLM + Bilateral Quantifiers")
    print("=" * 60)
    
    def llm_evaluator(formula):
        """LLM that knows about fictional characters"""
        knowledge = {
            "Wizard(gandalf)": BilateralTruthValue(positive=TRUE, negative=FALSE),
            "Wizard*(gandalf)": BilateralTruthValue(positive=FALSE, negative=TRUE),
            "Mortal(gandalf)": BilateralTruthValue(positive=TRUE, negative=FALSE),
            "Mortal*(gandalf)": BilateralTruthValue(positive=FALSE, negative=TRUE),
            "Human(gandalf)": BilateralTruthValue(positive=FALSE, negative=TRUE),
            "Human*(gandalf)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        }
        return knowledge.get(str(formula), BilateralTruthValue(positive=FALSE, negative=FALSE))
    
    # Wizards who are not human are not mortal (but Gandalf is special)
    formula_str = "[∀X Wizard(X) & ~Human(X)]~Mortal(X)"
    formula = parse_acrq_formula(formula_str)
    
    print(f"\nRule:   {formula_str}")
    print(f"ACrQ:   {formula}")
    print("\nTesting with Gandalf (wizard, not human, but actually mortal)")
    
    formulas = [
        SignedFormula(t, formula),
        SignedFormula(t, parse_acrq_formula("Wizard(gandalf)")),
        SignedFormula(t, parse_acrq_formula("~Human(gandalf)")),
    ]
    
    tableau = ACrQTableau(formulas, llm_evaluator=llm_evaluator)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Rule derives Mortal*(gandalf), but LLM knows Gandalf is mortal")
    print("         This creates a conflict between formal rule and LLM knowledge")


def main():
    print("ACrQ Quantifiers with Bilateral Predicates")
    print("=" * 60)
    print("\nIn ACrQ transparent mode:")
    print("  • ~P(x) automatically becomes P*(x)")
    print("  • Quantified formulas work with bilateral predicates")
    print("  • Negation creates bilateral (negative evidence) predicates")
    
    test_quantified_negation()
    test_negated_restriction()
    test_existential_with_negation()
    test_complex_bilateral_quantifier()
    test_quantifier_duality()
    test_llm_with_bilateral_quantifiers()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("• ACrQ properly handles negation in quantified formulas")
    print("• Negated predicates become bilateral predicates (P*)")
    print("• Quantifier rules work correctly with bilateral predicates")
    print("• LLM integration can detect conflicts with formal rules")


if __name__ == "__main__":
    main()