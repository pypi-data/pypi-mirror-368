#!/usr/bin/env python3
"""
Debug closure marks in visualization
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE
from wkrq.cli import TableauTreeRenderer


def create_bilateral_llm_evaluator():
    """LLM evaluator"""
    def evaluate_formula(formula):
        formula_str = str(formula)
        if formula_str == "Planet(pluto)":
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        elif formula_str == "OrbitsSun(pluto)":
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        elif formula_str == "Spherical(pluto)":
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        else:
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
    return evaluate_formula


def main():
    universal_rule = parse("[∀x OrbitsSun(x) & Spherical(x)] Planet(x)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    llm_eval = create_bilateral_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    # Debug the renderer
    renderer = TableauTreeRenderer(show_rules=True)
    renderer._mark_closed_paths(tableau)
    
    print("Closed leaf nodes:", renderer.closed_leaf_nodes)
    print("\nBranches:")
    for i, branch in enumerate(tableau.branches):
        print(f"\nBranch {i}:")
        print(f"  Closed: {branch.is_closed}")
        print(f"  Closure reason: {branch.closure_reason}")
        if branch.is_closed:
            # Find contradicting formulas
            formula_counts = {}
            for node in branch.nodes:
                key = (str(node.formula.formula), str(node.formula.sign))
                if key not in formula_counts:
                    formula_counts[key] = []
                formula_counts[key].append(node.id)
            
            print("  Formula/sign combinations:")
            for (formula, sign), node_ids in formula_counts.items():
                if len(node_ids) > 1 or any((formula, other_sign) in formula_counts 
                                           for other_sign in ['t', 'f', 'e'] if other_sign != sign):
                    print(f"    {sign}: {formula} - nodes {node_ids}")
    
    print("\n" + "="*50)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)


if __name__ == "__main__":
    main()