#!/usr/bin/env python3
"""
Debug why f: Planet*(sedna) isn't showing in the tableau.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, FALSE

def create_sedna_llm_evaluator():
    """LLM evaluator with no knowledge about Sedna"""
    
    def evaluate_formula(formula):
        # Return gap for Planet(sedna)
        if str(formula) == "Planet(sedna)":
            print(f"LLM evaluating {formula}: returning gap (FALSE, FALSE)")
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
        # Don't evaluate anything else
        return BilateralTruthValue(positive=FALSE, negative=FALSE)
    
    return evaluate_formula


def main():
    print("Debug: Sedna Gap Dual Formula Test")
    print("=" * 50)
    
    # Simple test with just Planet(sedna)
    planet_sedna = parse("Planet(sedna)")
    
    signed_formulas = [
        SignedFormula(t, planet_sedna),
    ]
    
    print("\nInitial formula:")
    print("  t: Planet(sedna)")
    
    print("\nExpected LLM evaluation:")
    print("  Gap (FALSE, FALSE) should produce:")
    print("  1. f: Planet(sedna)")
    print("  2. f: Planet*(sedna)")
    
    # Create tableau with LLM evaluator
    llm_eval = create_sedna_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    # Render the proof tree
    print("\n" + "─" * 50)
    print("PROOF TREE:")
    print("─" * 50)
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print("\nDEBUG: Checking all nodes in tableau:")
    for node_id, node in tableau.nodes.items():
        print(f"  Node {node_id}: {node.formula.sign}: {node.formula.formula}")
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")


if __name__ == "__main__":
    main()