#!/usr/bin/env python3
"""
Debug why f: Planet*(sedna) isn't being added.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t, f, m
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, FALSE, TRUE, UNDEFINED

def create_sedna_llm_evaluator():
    """LLM evaluator with no knowledge about Planet(sedna) only"""
    
    def evaluate_formula(formula):
        formula_str = str(formula)
        
        # Return gap ONLY for Planet(sedna)
        if formula_str == "Planet(sedna)":
            print(f"LLM evaluating {formula}: returning gap (FALSE, FALSE)")
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
        
        # Return UNDEFINED for everything else (won't trigger evaluation)
        print(f"LLM not evaluating {formula}: returning UNDEFINED")
        return BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED)
    
    return evaluate_formula


def main():
    print("Debug: Sedna Gap Dual Formula Test V3")
    print("=" * 50)
    
    # Test with m: Planet(sedna) which branches
    planet_sedna = parse("Planet(sedna)")
    
    signed_formulas = [
        SignedFormula(m, planet_sedna),  # m branches to t or f
    ]
    
    print("\nInitial formula:")
    print("  m: Planet(sedna) [branches to t or f]")
    
    print("\nExpected behavior:")
    print("  Branch 1: t: Planet(sedna)")
    print("    → LLM eval returns gap (FALSE, FALSE)")
    print("    → Should add f: Planet(sedna) AND f: Planet*(sedna)")
    print("  Branch 2: f: Planet(sedna)")
    print("    → No LLM eval needed")
    
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
        formula_str = str(node.formula.formula)
        print(f"  Node {node_id}: {node.formula.sign}: {formula_str}")
        if hasattr(node.formula.formula, 'is_negative'):
            print(f"    is_negative: {node.formula.formula.is_negative}")
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")


if __name__ == "__main__":
    main()