#!/usr/bin/env python3
"""
ACrQ + LLM Integration: Pluto Classification Proof

Shows how formal logical derivation conflicts with LLM knowledge.
The universal rule derives Planet(pluto), but LLM says it's false.
"""

from wkrq import parse, Tableau, ACrQTableau, SignedFormula, t
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
    """Show formal derivation vs LLM knowledge conflict"""
    
    print("ACrQ + LLM: Pluto Classification Proof")
    print("=" * 50)
    
    # Set up the formal reasoning
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    negated_planet = parse("~Planet(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact),
        SignedFormula(t, negated_planet)
    ]
    
    print("\nFormal Rules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  OrbitsSun(pluto)")
    print("  Spherical(pluto)")
    print("\nTesting: ~Planet(pluto)")
    
    # Show pure logical derivation
    print("\n" + "─" * 50)
    print("PURE LOGICAL DERIVATION:")
    print("─" * 50)
    
    tableau = Tableau(signed_formulas)
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result.satisfiable]}")
    print("The universal rule instantiates with pluto:")
    print("  • Line 5-6: t-restricted-forall rule")
    print("  • Line 6: t: Planet(pluto) [derived]")
    print("  • Line 4: f: Planet(pluto) [from ~Planet(pluto)]")
    print("  • Contradiction! (×)")
    
    # Now show with LLM evaluation - test the derived conclusion directly
    print("\n" + "─" * 50)
    print("WITH LLM EVALUATION (Testing derived Planet(pluto)):")
    print("─" * 50)
    
    # Directly test the derived conclusion
    planet_pluto = parse("Planet(pluto)")
    signed_planet = SignedFormula(t, planet_pluto)
    
    print("Query: t: Planet(pluto) [from formal derivation]")
    print()
    
    llm_eval = create_pluto_llm_evaluator()
    tableau_llm = ACrQTableau([signed_planet], llm_evaluator=llm_eval)
    result_llm = tableau_llm.construct()
    
    tree_str_llm = renderer.render_ascii(result_llm.tableau)
    print(tree_str_llm)
    
    print(f"\nResult: {['SATISFIABLE', 'UNSATISFIABLE'][not result_llm.satisfiable]}")
    print("✗ LLM refutes the formal derivation!")
    print("  Formal logic: Planet(pluto) = TRUE")
    print("  LLM knowledge: Planet(pluto) = FALSE")


if __name__ == "__main__":
    main()