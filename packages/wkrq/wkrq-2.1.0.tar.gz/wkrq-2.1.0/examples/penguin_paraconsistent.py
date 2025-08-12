#!/usr/bin/env python3
"""
Penguin Example: True Paraconsistent Behavior

This example demonstrates how ACrQ + bilateral-truth can handle 
contradictory information without logical explosion, unlike classical logic.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from wkrq import ACrQTableau, PropositionalAtom, SignedFormula, t, f
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_evaluator():
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


def demonstrate_paraconsistency():
    """Show paraconsistent reasoning with contradictory penguin knowledge."""
    
    print("=== Paraconsistent Penguin Reasoning ===")
    print()
    print("Scenario: We have contradictory information about a specific penguin")
    print("• Some evidence suggests this penguin flies (maybe it's a cartoon penguin)")
    print("• Other evidence suggests penguins don't fly (biological fact)")
    print()
    
    llm_eval = create_evaluator()
    
    # Create two different penguin propositions that might yield different evidence
    penguin_flies = PropositionalAtom("The penguin Opus from Bloom County can fly")
    penguin_no_fly = PropositionalAtom("Penguins are flightless birds")
    something_else = PropositionalAtom("Penguins live in Antarctica")
    
    print("=== Individual Evaluations ===")
    
    # Test each individually
    test_cases = [
        (penguin_flies, "Specific fictional penguin"),
        (penguin_no_fly, "General biological fact"),  
        (something_else, "Unrelated penguin fact")
    ]
    
    for atom, description in test_cases:
        print(f"Testing: {atom}")
        print(f"Context: {description}")
        
        tableau = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=llm_eval)
        result = tableau.construct()
        
        print(f"Result: {'✓ Satisfiable' if result.satisfiable else '✗ Unsatisfiable'}")
        if result.models and hasattr(result.models[0], 'bilateral_valuations'):
            for formula_str, btv in result.models[0].bilateral_valuations.items():
                if str(atom) in formula_str:
                    state = ("gap" if btv.is_gap() else 
                           "glut" if btv.is_glut() else 
                           "determinate")
                    print(f"  Evidence: {btv} ({state})")
        print()
    
    print("=== Paraconsistent Test: Multiple Penguin Facts ===")
    print("Can we reason with multiple penguin-related facts simultaneously?")
    print("(In classical logic, any contradiction would make everything provable)")
    print()
    
    # Combine multiple potentially conflicting facts
    combined_facts = [
        SignedFormula(t, penguin_no_fly),     # Penguins don't fly (biological)
        SignedFormula(t, something_else),     # Penguins in Antarctica
        SignedFormula(t, PropositionalAtom("Some cartoon penguins appear to fly")),  # Fiction
    ]
    
    print("Testing combined knowledge base:")
    for sf in combined_facts:
        print(f"  {sf}")
    
    tableau_combined = ACrQTableau(combined_facts, llm_evaluator=llm_eval)
    result_combined = tableau_combined.construct()
    
    print()
    print("Results:")
    print(f"  Satisfiable: {'✓ YES' if result_combined.satisfiable else '✗ NO'}")
    print(f"  Models found: {len(result_combined.models)}")
    print(f"  Closed branches: {result_combined.closed_branches}")
    print(f"  Open branches: {result_combined.open_branches}")
    
    if result_combined.satisfiable:
        print("  ✓ SUCCESS: ACrQ handled potentially contradictory penguin knowledge!")
        print("    No logical explosion despite mixed information.")
        
        if result_combined.models:
            print("\\n  Model details:")
            model = result_combined.models[0]
            if hasattr(model, 'bilateral_valuations'):
                for atom, btv in model.bilateral_valuations.items():
                    info_state = ("knowledge gap" if btv.is_gap() else
                                "knowledge glut" if btv.is_glut() else  
                                "determinate knowledge")
                    print(f"    {atom}: {info_state}")
    else:
        print("  Branch closed - formal contradiction detected")
    
    print()
    print("=== Comparison with Classical Logic ===")
    print("Classical Logic:")
    print("  • Any contradiction → everything is provable (explosion)")
    print("  • Cannot distinguish between different types of inconsistency")
    print()
    print("ACrQ + bilateral-truth:")
    print("  • Contradictions handled locally without explosion")
    print("  • Different evidence types (gaps vs gluts) distinguished")
    print("  • Real-world knowledge integrated formally")
    print("  • Paraconsistent reasoning maintains useful inferences")


if __name__ == "__main__":
    demonstrate_paraconsistency()