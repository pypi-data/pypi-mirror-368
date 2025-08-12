#!/usr/bin/env python3
"""
Debug branch structure
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE


def create_bilateral_llm_evaluator():
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
    
    print("Branch structure analysis:")
    print("="*50)
    
    for i, branch in enumerate(tableau.branches):
        print(f"\nBranch {i}: {'CLOSED' if branch.is_closed else 'OPEN'}")
        if branch.closure_reason:
            print(f"  Closure: {branch.closure_reason}")
        
        print(f"  Nodes in branch (total: {len(branch.nodes)}):")
        for j, node in enumerate(branch.nodes):
            print(f"    [{j}] ID={node.id}: {node.formula}")
            
    print("\nTableau nodes tree structure:")
    print("="*50)
    
    def print_tree(node, indent=0):
        print("  " * indent + f"ID={node.id}: {node.formula}")
        for child in node.children:
            print_tree(child, indent + 1)
    
    if tableau.nodes:
        print_tree(tableau.nodes[0])


if __name__ == "__main__":
    main()