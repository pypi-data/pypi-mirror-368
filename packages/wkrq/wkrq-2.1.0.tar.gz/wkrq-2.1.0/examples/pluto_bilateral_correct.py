#!/usr/bin/env python3
"""
ACrQ + LLM: Correct Bilateral Semantics

Uses proper bilateral-truth semantics where:
- <t,f> = true (positive evidence only)
- <f,t> = false (negative evidence only)
- <f,f> = gap (no evidence)
- <t,t> = glut (contradictory evidence)
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE


def create_bilateral_llm_evaluator():
    """LLM evaluator using correct bilateral semantics"""
    
    def evaluate_formula(formula):
        formula_str = str(formula)
        
        # Planet(pluto): LLM knows it's false (negative evidence only)
        if formula_str == "Planet(pluto)":
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        
        # OrbitsSun(pluto): LLM knows it's true (positive evidence only)
        elif formula_str == "OrbitsSun(pluto)":
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        
        # Spherical(pluto): LLM knows it's true (positive evidence only)
        elif formula_str == "Spherical(pluto)":
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        
        # For anything else: knowledge gap (no evidence either way)
        else:
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
    
    return evaluate_formula


def main():
    print("ACrQ + LLM: Bilateral Truth Semantics")
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
    
    print("\nFormal Knowledge:")
    print("  1. [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  2. OrbitsSun(pluto)")
    print("  3. Spherical(pluto)")
    
    print("\nLLM Knowledge (bilateral truth values):")
    print("  Planet(pluto): <f,t> (false - negative evidence)")
    print("  OrbitsSun(pluto): <t,f> (true - positive evidence)")
    print("  Spherical(pluto): <t,f> (true - positive evidence)")
    
    # Create tableau with bilateral LLM evaluator
    llm_eval = create_bilateral_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    # Render the proof tree
    print("\n" + "─" * 50)
    print("PROOF TREE:")
    print("─" * 50)
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    print("\nAnalysis:")
    print("  • Universal rule derives t: Planet(pluto)")
    print("  • LLM provides t: Planet*(pluto) (negative evidence)")
    print("  • Formal derivation conflicts with LLM knowledge")


if __name__ == "__main__":
    main()