#!/usr/bin/env python3
"""
ACrQ + LLM: Comprehensive Pluto Example

Demonstrates:
1. Formal derivation vs LLM knowledge
2. Knowledge gaps (unknown objects)
3. Gluts (contradictory information)
4. Multiple celestial objects
"""

from wkrq import parse_acrq_formula, ACrQTableau, SignedFormula, t, f
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_comprehensive_llm_evaluator():
    """LLM with knowledge about various celestial objects"""
    
    knowledge = {
        # Pluto - controversial status
        "Planet(pluto)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "DwarfPlanet(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "OrbitsSun(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "ClearedOrbit(pluto)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        
        # Earth - uncontroversial planet
        "Planet(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "OrbitsSun(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "ClearedOrbit(earth)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        
        # Ceres - dwarf planet in asteroid belt
        "Planet(ceres)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "DwarfPlanet(ceres)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "OrbitsSun(ceres)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(ceres)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "ClearedOrbit(ceres)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        
        # Sedna - distant object, classification unclear
        "OrbitsSun(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(sedna)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        # Planet and DwarfPlanet status unknown - will return gap
        
        # Moon - not a planet
        "Planet(moon)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "OrbitsSun(moon)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "Spherical(moon)": BilateralTruthValue(positive=TRUE, negative=FALSE),
    }
    
    def evaluate_formula(formula):
        key = str(formula)
        # Return knowledge if known, otherwise gap (no information)
        return knowledge.get(key, BilateralTruthValue(positive=FALSE, negative=FALSE))
    
    return evaluate_formula


def test_classic_planet_definition():
    """Test: Classic definition (orbits sun + spherical = planet)"""
    print("\n" + "=" * 60)
    print("TEST 1: Classic Planet Definition")
    print("=" * 60)
    
    # Pre-2006 definition
    formulas = [
        SignedFormula(t, parse_acrq_formula("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto)")),
        SignedFormula(t, parse_acrq_formula("Spherical(pluto)")),
    ]
    
    print("\nRules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  OrbitsSun(pluto)")
    print("  Spherical(pluto)")
    
    tableau = ACrQTableau(formulas, llm_evaluator=create_comprehensive_llm_evaluator())
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Formal logic derives Planet(pluto), but LLM knows it's false → contradiction")


def test_modern_planet_definition():
    """Test: Modern definition (includes cleared orbit requirement)"""
    print("\n" + "=" * 60)
    print("TEST 2: Modern Planet Definition (IAU 2006)")
    print("=" * 60)
    
    # Post-2006 IAU definition
    formulas = [
        SignedFormula(t, parse_acrq_formula(
            "[∀X OrbitsSun(X) & Spherical(X) & ClearedOrbit(X)]Planet(X)"
        )),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto)")),
        SignedFormula(t, parse_acrq_formula("Spherical(pluto)")),
        SignedFormula(t, parse_acrq_formula("~ClearedOrbit(pluto)")),  # Becomes ClearedOrbit*(pluto)
    ]
    
    print("\nRules:")
    print("  [∀X OrbitsSun(X) & Spherical(X) & ClearedOrbit(X)]Planet(X)")
    print("  OrbitsSun(pluto)")
    print("  Spherical(pluto)")
    print("  ~ClearedOrbit(pluto)  [ACrQ: ClearedOrbit*(pluto)]")
    
    tableau = ACrQTableau(formulas, llm_evaluator=create_comprehensive_llm_evaluator())
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Modern definition correctly doesn't derive Planet(pluto)")


def test_knowledge_gap():
    """Test: Object with unknown classification (Sedna)"""
    print("\n" + "=" * 60)
    print("TEST 3: Knowledge Gap - Unknown Classification")
    print("=" * 60)
    
    formulas = [
        SignedFormula(t, parse_acrq_formula("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")),
        SignedFormula(t, parse_acrq_formula("OrbitsSun(sedna)")),
        SignedFormula(t, parse_acrq_formula("Spherical(sedna)")),
    ]
    
    print("\nRules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  OrbitsSun(sedna)")
    print("  Spherical(sedna)")
    print("\nNote: LLM has no knowledge about Planet(sedna) status")
    
    tableau = ACrQTableau(formulas, llm_evaluator=create_comprehensive_llm_evaluator())
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Formal logic derives Planet(sedna), LLM's uncertainty contradicts → unsatisfiable")


def test_multiple_objects():
    """Test: Compare Earth, Pluto, and Ceres"""
    print("\n" + "=" * 60)
    print("TEST 4: Multiple Objects Comparison")
    print("=" * 60)
    
    # Test if all three satisfy the classic definition
    formulas = [
        SignedFormula(t, parse_acrq_formula("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")),
        # Earth
        SignedFormula(t, parse_acrq_formula("OrbitsSun(earth) & Spherical(earth)")),
        # Pluto
        SignedFormula(t, parse_acrq_formula("OrbitsSun(pluto) & Spherical(pluto)")),
        # Ceres
        SignedFormula(t, parse_acrq_formula("OrbitsSun(ceres) & Spherical(ceres)")),
    ]
    
    print("\nRules:")
    print("  [∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    print("  Earth: OrbitsSun ∧ Spherical")
    print("  Pluto: OrbitsSun ∧ Spherical")
    print("  Ceres: OrbitsSun ∧ Spherical")
    
    tableau = ACrQTableau(formulas, llm_evaluator=create_comprehensive_llm_evaluator())
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True, compact=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    print("Analysis: Earth is correctly a planet, but Pluto and Ceres aren't → contradictions")


def main():
    print("ACrQ + LLM: Comprehensive Celestial Classification")
    print("Combining formal astronomical rules with modern knowledge")
    
    test_classic_planet_definition()
    test_modern_planet_definition()
    test_knowledge_gap()
    test_multiple_objects()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("• Classic definition conflicts with modern knowledge")
    print("• Modern IAU definition correctly classifies objects")
    print("• Knowledge gaps now cause unsatisfiability (explicit uncertainty)")
    print("• Multiple objects reveal systematic classification issues")


if __name__ == "__main__":
    main()