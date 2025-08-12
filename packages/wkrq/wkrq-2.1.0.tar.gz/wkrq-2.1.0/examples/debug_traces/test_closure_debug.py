#!/usr/bin/env python3
"""
Debug why branches are incorrectly marked as closed
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE


def create_test_evaluator():
    """Test evaluator"""
    def evaluate_formula(formula):
        if str(formula) == "OrbitsSun(pluto)":
            # LLM agrees it's true
            return BilateralTruthValue(positive=TRUE, negative=FALSE)
        return BilateralTruthValue(positive=FALSE, negative=FALSE)
    return evaluate_formula


def main():
    # Simple test: just one fact
    orbits_fact = parse("OrbitsSun(pluto)")
    signed_formulas = [SignedFormula(t, orbits_fact)]
    
    llm_eval = create_test_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    print("Test: OrbitsSun(pluto) with LLM agreeing it's true")
    print("="*50)
    
    # Check branch status
    for i, branch in enumerate(tableau.branches):
        print(f"\nBranch {i}:")
        print(f"  Closed: {branch.is_closed}")
        print(f"  Closure reason: {branch.closure_reason}")
        print(f"  Nodes:")
        for node in branch.nodes:
            print(f"    {node.id}: {node.formula} (closed: {node.is_closed})")
    
    from wkrq.cli import TableauTreeRenderer
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print("\nTree visualization:")
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")


if __name__ == "__main__":
    main()