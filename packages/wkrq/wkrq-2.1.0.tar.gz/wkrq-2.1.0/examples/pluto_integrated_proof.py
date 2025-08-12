#!/usr/bin/env python3
"""
ACrQ + LLM Integration: Complete Pluto Proof

Shows the full tableau with quantifier instantiation followed by LLM evaluation.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_pluto_llm_evaluator():
    """LLM evaluator with post-2006 Pluto knowledge"""
    
    knowledge = {
        "Planet(pluto)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "OrbitsSun(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
    }
    
    def evaluate_formula(formula):
        key = str(formula)
        result = knowledge.get(key, BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED))
        return result
    
    return evaluate_formula


def main():
    """Show complete integrated proof with quantifier instantiation and LLM evaluation"""
    
    print("ACrQ + LLM: Complete Integrated Proof")
    print("=" * 50)
    
    # Set up the formal reasoning
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nFormal Rules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  OrbitsSun(pluto)")
    print("  Spherical(pluto)")
    print("\nExpected: Derive Planet(pluto), then LLM refutes it")
    
    # Run with LLM evaluator
    print("\n" + "─" * 50)
    print("INTEGRATED PROOF (Quantifier + LLM):")
    print("─" * 50)
    
    llm_eval = create_pluto_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    print("\nAnalysis:")
    print("  • Universal rule should instantiate with pluto")
    print("  • This derives Planet(pluto)")
    print("  • LLM-Eval then evaluates Planet(pluto) → FALSE")
    print("  • Conflict shows formal vs contemporary knowledge")


if __name__ == "__main__":
    main()