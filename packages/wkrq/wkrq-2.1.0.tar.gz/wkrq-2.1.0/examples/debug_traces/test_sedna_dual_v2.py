#!/usr/bin/env python3
"""
Debug why f: Planet*(sedna) isn't being added.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t, f
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
    print("Debug: Sedna Gap Dual Formula Test V2")
    print("=" * 50)
    
    # Test with a formula that won't immediately close
    orbits_sedna = parse("OrbitsSun(sedna)")
    planet_sedna = parse("Planet(sedna)")
    
    signed_formulas = [
        SignedFormula(t, orbits_sedna),  # This won't contradict
        SignedFormula(t, planet_sedna),
    ]
    
    print("\nInitial formulas:")
    print("  t: OrbitsSun(sedna)")
    print("  t: Planet(sedna)")
    
    print("\nExpected LLM evaluation of Planet(sedna):")
    print("  Gap (FALSE, FALSE) should produce:")
    print("  1. f: Planet(sedna) [contradicts t: Planet(sedna)]")
    print("  2. f: Planet*(sedna) [should also be added]")
    
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
        print(f"    Type: {type(node.formula.formula).__name__}")
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    
    # Let's also test if we start with something that won't contradict
    print("\n" + "=" * 50)
    print("Test 2: Without initial t: Planet(sedna)")
    print("=" * 50)
    
    signed_formulas2 = [
        SignedFormula(t, orbits_sedna),
        SignedFormula(f, planet_sedna),  # f instead of t
    ]
    
    print("\nInitial formulas:")
    print("  t: OrbitsSun(sedna)")
    print("  f: Planet(sedna)")
    
    tableau2 = ACrQTableau(signed_formulas2, llm_evaluator=llm_eval)
    result2 = tableau2.construct()
    
    print("\n" + "─" * 50)
    print("PROOF TREE:")
    print("─" * 50)
    tree_str2 = renderer.render_ascii(result2.tableau)
    print(tree_str2)
    
    print("\nDEBUG: Checking all nodes in tableau 2:")
    for node_id, node in tableau2.nodes.items():
        print(f"  Node {node_id}: {node.formula.sign}: {node.formula.formula}")
        print(f"    Type: {type(node.formula.formula).__name__}")


if __name__ == "__main__":
    main()