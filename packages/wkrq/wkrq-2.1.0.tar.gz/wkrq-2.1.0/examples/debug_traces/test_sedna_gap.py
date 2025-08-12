#!/usr/bin/env python3
"""
Test case specifically for Sedna knowledge gap with new semantics.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE

def create_sedna_llm_evaluator():
    """LLM evaluator with no knowledge about Sedna"""
    
    knowledge = {
        "OrbitsSun(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        # No knowledge about Planet(sedna) - returns gap (FALSE, FALSE)
    }
    
    def evaluate_formula(formula):
        key = str(formula)
        if key in knowledge:
            return knowledge[key]
        # Return gap (explicit uncertainty) for unknown predicates
        return BilateralTruthValue(positive=FALSE, negative=FALSE)
    
    return evaluate_formula


def main():
    print("ACrQ + LLM: Sedna Knowledge Gap Test")
    print("=" * 50)
    
    # The formal rule and facts
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(sedna)")
    spherical_fact = parse("Spherical(sedna)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nFormal Rules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  OrbitsSun(sedna)")
    print("  Spherical(sedna)")
    
    print("\nLLM Knowledge:")
    print("  OrbitsSun(sedna): (TRUE, FALSE) - has positive evidence")
    print("  Spherical(sedna): (TRUE, FALSE) - has positive evidence")
    print("  Planet(sedna): (FALSE, FALSE) - knowledge gap (no evidence)")
    
    print("\nNew Gap Semantics:")
    print("  • Gap (FALSE, FALSE) is an explicit uncertainty speech act")
    print("  • LLM states: 'I cannot verify AND I cannot refute'")
    print("  • This adds both f: Planet(sedna) and f: Planet*(sedna)")
    print("  • The f: Planet(sedna) contradicts the derived t: Planet(sedna)")
    
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
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    print("\nConclusion:")
    if not result.satisfiable:
        print("  ✓ UNSATISFIABLE: LLM's explicit uncertainty contradicts formal derivation")
        print("  • Formal logic derives: t: Planet(sedna)")
        print("  • LLM gap produces: f: Planet(sedna) [cannot verify]")
        print("  • Contradiction causes branch closure")
    else:
        print("  ✗ SATISFIABLE: Old behavior - gap was treated as silence")
        print("  • This should not happen with new semantics")


if __name__ == "__main__":
    main()