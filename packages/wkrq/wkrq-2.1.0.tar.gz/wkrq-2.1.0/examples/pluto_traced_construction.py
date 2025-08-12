#!/usr/bin/env python3
"""
ACrQ + LLM: Traced Tableau Construction

Shows the complete sequence of rule applications and what they produce,
even when branches close before all formulas are added.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE


def create_comprehensive_llm_evaluator():
    """LLM evaluator with varied knowledge."""
    
    knowledge = {
        # Pluto: knows it's not a planet
        "Planet(pluto)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "OrbitsSun(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        
        # Sedna: no knowledge (gap)
        "Planet(sedna)": BilateralTruthValue(positive=FALSE, negative=FALSE),
        "OrbitsSun(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        
        # Earth: knows it's a planet
        "Planet(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "OrbitsSun(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
    }
    
    def evaluate_formula(formula):
        key = str(formula)
        # Return gap for unknowns
        return knowledge.get(key, BilateralTruthValue(positive=FALSE, negative=FALSE))
    
    return evaluate_formula


def test_sedna_with_trace():
    """Test Sedna case with detailed tracing."""
    
    print("=" * 70)
    print("TEST: Sedna Classification with Knowledge Gap")
    print("=" * 70)
    
    # Create formulas
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(sedna)")
    spherical_fact = parse("Spherical(sedna)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nSetup:")
    print("  Universal rule: [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  Facts: OrbitsSun(sedna), Spherical(sedna)")
    print("  LLM knowledge: No information about Planet(sedna)")
    
    # Create tableau with tracing enabled
    llm_eval = create_comprehensive_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval, trace=True)
    result = tableau.construct()
    
    # Print the trace
    if tableau.construction_trace:
        tableau.construction_trace.print_trace()
    
    # Print rule summary
    print("\n" + "-" * 70)
    print("RULE SUMMARY")
    print("-" * 70)
    if tableau.construction_trace:
        for line in tableau.construction_trace.get_rule_summary():
            print(line)
    
    # Print final tableau
    print("\n" + "=" * 70)
    print("FINAL TABLEAU")
    print("=" * 70)
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    
    print("\n" + "-" * 70)
    print("KEY INSIGHT")
    print("-" * 70)
    print("The LLM evaluation of Planet(sedna) produces TWO formulas:")
    print("  1. f: Planet(sedna) - 'I cannot verify it's true'")
    print("  2. f: Planet*(sedna) - 'I cannot verify it's false'")
    print("\nHowever, only the first appears in the tree because:")
    print("  • f: Planet(sedna) immediately contradicts t: Planet(sedna)")
    print("  • The branch closes before f: Planet*(sedna) can be added")
    print("\nThe trace shows both formulas were produced by the rule.")


def test_pluto_with_trace():
    """Test Pluto case with detailed tracing."""
    
    print("\n" + "=" * 70)
    print("TEST: Pluto Classification with LLM Knowledge")
    print("=" * 70)
    
    # Create formulas
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nSetup:")
    print("  Universal rule: [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  Facts: OrbitsSun(pluto), Spherical(pluto)")
    print("  LLM knowledge: Planet(pluto) is FALSE")
    
    # Create tableau with tracing enabled
    llm_eval = create_comprehensive_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval, trace=True)
    result = tableau.construct()
    
    # Print step-by-step
    if tableau.construction_trace:
        tableau.construction_trace.print_step_by_step()
    
    # Print final tableau
    print("\n" + "=" * 70)
    print("FINAL TABLEAU")
    print("=" * 70)
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")


def main():
    """Run traced tableau construction examples."""
    
    print("TRACED TABLEAU CONSTRUCTION")
    print("Showing complete rule applications and construction sequence")
    print()
    
    test_sedna_with_trace()
    test_pluto_with_trace()
    
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("The trace shows:")
    print("  1. Exactly what each rule produces")
    print("  2. Which formulas get added to the tableau")
    print("  3. When and why branches close")
    print("  4. The complete sequence of construction")
    print("\nThis helps users understand both the logical rules")
    print("and how the tableau algorithm applies them.")


if __name__ == "__main__":
    main()