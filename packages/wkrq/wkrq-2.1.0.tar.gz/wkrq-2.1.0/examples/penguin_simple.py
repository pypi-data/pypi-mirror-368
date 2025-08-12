#!/usr/bin/env python3
"""
Simplified Penguin Example: Demonstrating Paraconsistent Reasoning

Focus on the core contradiction:
"Penguins can fly" vs "Penguins cannot fly"
"""

import os
from dotenv import load_dotenv
load_dotenv()

from wkrq import ACrQTableau, PropositionalAtom, SignedFormula, t, f
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_evaluator():
    """Create bilateral-truth evaluator."""
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        # Determine evidence type
        if pos == TRUE and neg == FALSE:
            evidence = "✓ Strong positive evidence"
        elif pos == FALSE and neg == TRUE:
            evidence = "✗ Strong negative evidence"
        elif pos == TRUE and neg == TRUE:
            evidence = "⚡ Contradictory evidence (glut)"
        elif pos == FALSE and neg == FALSE:
            evidence = "? Insufficient evidence (gap)"
        else:
            evidence = "~ Mixed evidence"
            
        print(f"    LLM Assessment: '{formula}' → <{u},{v}> → {evidence}")
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


def main():
    print("=== Penguin Paraconsistent Reasoning Demo ===")
    print()
    print("The Classic Problem:")
    print("• General knowledge: 'Birds can fly'")
    print("• Specific knowledge: 'Penguins cannot fly'") 
    print("• Fact: 'Penguins are birds'")
    print("• Question: Can penguins fly?")
    print()
    print("Classical logic would derive contradiction and explode.")
    print("ACrQ handles this paraconsistently with LLM knowledge.")
    print()

    llm_eval = create_evaluator()

    # Test core statements
    test_cases = [
        ("Birds can fly", "General rule about birds"),
        ("Penguins can fly", "Specific case - should contradict general knowledge"),
        ("Penguins cannot fly", "Specific exception - should align with LLM knowledge"),
        ("Penguins are birds", "Taxonomic fact"),
    ]

    for statement, description in test_cases:
        print(f"Testing: {statement}")
        print(f"Context: {description}")
        
        atom = PropositionalAtom(statement)
        
        # Test positive assertion
        tableau_pos = ACrQTableau([SignedFormula(t, atom)], llm_evaluator=llm_eval)
        result_pos = tableau_pos.construct()
        
        print(f"    t:{statement} → {'Satisfiable' if result_pos.satisfiable else 'Unsatisfiable'}")
        print()

    # Now test the contradiction scenario
    print("=== Contradiction Test ===")
    print("Testing simultaneous assertions:")
    print("• t:'Penguins can fly' (positive)")
    print("• f:'Penguins can fly' (negative)")
    print()

    penguin_fly = PropositionalAtom("Penguins can fly")
    
    # Create tableau with contradictory assertions
    contradictory_formulas = [
        SignedFormula(t, penguin_fly),  # Penguins can fly
        SignedFormula(f, penguin_fly)   # Penguins cannot fly  
    ]

    print("LLM will evaluate 'Penguins can fly':")
    tableau_contradiction = ACrQTableau(contradictory_formulas, llm_evaluator=llm_eval)
    result_contradiction = tableau_contradiction.construct()

    print()
    print("Results:")
    print(f"  Satisfiable: {result_contradiction.satisfiable}")
    print(f"  Open branches: {result_contradiction.open_branches}")
    print(f"  Closed branches: {result_contradiction.closed_branches}")
    print(f"  Total nodes: {result_contradiction.total_nodes}")

    if result_contradiction.satisfiable:
        print("  ✓ ACrQ successfully handles the contradiction without explosion!")
    else:
        print("  ✗ Branch closed due to contradiction (as expected in some cases)")

    print()
    print("=== Key Insights ===")
    print("1. LLM provides nuanced bilateral evidence")
    print("2. ACrQ reasoning handles contradictions paraconsistently") 
    print("3. No logical explosion despite conflicting knowledge")
    print("4. Formal logical reasoning enhanced with world knowledge")


if __name__ == "__main__":
    main()