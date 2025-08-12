#!/usr/bin/env python3
"""
Debug branch closures in Pluto example
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
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
    # The formal rule and facts
    universal_rule = parse("[∀x OrbitsSun(x) & Spherical(x)] Planet(x)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    # Create tableau with bilateral LLM evaluator
    llm_eval = create_bilateral_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    print("Pluto Example Branch Analysis")
    print("="*50)
    
    # Check all branches
    for i, branch in enumerate(tableau.branches):
        print(f"\nBranch {i}:")
        print(f"  Closed: {branch.is_closed}")
        print(f"  Closure reason: {branch.closure_reason}")
        print(f"  Formulas in branch:")
        for sf in branch.formulas:
            print(f"    {sf}")
        
        # Check for contradictions manually
        print(f"  Checking for contradictions:")
        formulas_by_content = {}
        for sf in branch.formulas:
            key = str(sf.formula)
            if key not in formulas_by_content:
                formulas_by_content[key] = []
            formulas_by_content[key].append(str(sf.sign))
        
        for formula_str, signs in formulas_by_content.items():
            if len(signs) > 1:
                print(f"    {formula_str}: signs = {signs}")
    
    from wkrq.cli import TableauTreeRenderer
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print("\nTree visualization:")
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")


if __name__ == "__main__":
    main()