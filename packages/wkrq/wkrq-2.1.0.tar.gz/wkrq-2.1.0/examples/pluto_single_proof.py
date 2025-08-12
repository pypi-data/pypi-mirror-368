#!/usr/bin/env python3
"""
ACrQ + LLM: Single Integrated Proof Tree

Shows one complete proof tree with:
1. Universal quantifier instantiation deriving Planet(pluto)
2. LLM evaluation refuting Planet(pluto)
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_selective_llm_evaluator():
    """LLM evaluator that only evaluates Planet(pluto), not the premises"""
    
    def evaluate_formula(formula):
        # Only evaluate Planet(pluto), leave other formulas undefined
        # This prevents cluttering the tree with evaluations of the premises
        if str(formula) == "Planet(pluto)":
            # Post-2006 knowledge: Pluto is not a planet
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        # Don't evaluate anything else
        return BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED)
    
    return evaluate_formula


def main():
    print("ACrQ + LLM: Single Integrated Proof")
    print("=" * 50)
    
    # The formal rule and facts
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nAssumptions:")
    print("  1. [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  2. OrbitsSun(pluto)")
    print("  3. Spherical(pluto)")
    print("\nExpected derivation:")
    print("  → Planet(pluto) [by universal instantiation]")
    print("  → LLM refutes with contemporary knowledge")
    
    # Create tableau with selective LLM evaluator
    llm_eval = create_selective_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    # Render the single proof tree
    print("\n" + "─" * 50)
    print("PROOF TREE:")
    print("─" * 50)
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    print("\nKey steps:")
    print("  • Node 6: Universal rule derives Planet(pluto)")
    print("  • Node 11: LLM evaluation refutes Planet(pluto)")
    print("  • Branch closes due to contradiction (×)")


if __name__ == "__main__":
    main()