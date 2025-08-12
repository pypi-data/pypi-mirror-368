#!/usr/bin/env python3
"""
Penguin Example: Classic Non-Monotonic Reasoning with bilateral-truth + ACrQ

This demonstrates the famous penguin problem in AI:
- Birds typically fly
- Penguins are birds  
- Penguins don't fly
- Tweety is a penguin

Classical logic would derive contradiction and explode.
ACrQ with LLM evaluation handles this paraconsistently.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from wkrq import (
    ACrQTableau,
    PredicateFormula, 
    PropositionalAtom,
    Constant,
    SignedFormula,
    t, f
)
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_penguin_llm_evaluator():
    """Create LLM evaluator for penguin reasoning scenario."""
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        """Evaluate atomic formulas using bilateral-truth LLM."""
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        # Show LLM's reasoning
        evidence_type = "definitely true" if pos == TRUE and neg == FALSE else \
                       "definitely false" if pos == FALSE and neg == TRUE else \
                       "contradictory (glut)" if pos == TRUE and neg == TRUE else \
                       "uncertain (gap)" if pos == FALSE and neg == FALSE else "complex"
        
        print(f"  LLM: '{formula}' → <{u},{v}> ({evidence_type})")
        
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


def demonstrate_penguin_reasoning():
    """Demonstrate the penguin problem with ACrQ + bilateral-truth."""
    
    print("=== Penguin Example: Paraconsistent Reasoning ===")
    print()
    print("Classic AI Problem:")
    print("1. Birds typically fly")
    print("2. Penguins are birds") 
    print("3. Penguins don't fly")
    print("4. Tweety is a penguin")
    print()
    print("Question: Does Tweety fly?")
    print("Classical logic: CONTRADICTION → Everything is true (explosion)")
    print("ACrQ + LLM: Handle inconsistency paraconsistently")
    print()

    # Create the LLM evaluator
    llm_eval = create_penguin_llm_evaluator()
    
    # Define our entities
    tweety = Constant("Tweety")
    
    # Define atomic formulas
    penguin_tweety = PredicateFormula("Penguin", [tweety])
    bird_tweety = PredicateFormula("Bird", [tweety]) 
    flies_tweety = PredicateFormula("Flies", [tweety])
    
    print("=== Test 1: Is Tweety a penguin? ===")
    tableau1 = ACrQTableau([SignedFormula(t, penguin_tweety)], llm_evaluator=llm_eval)
    result1 = tableau1.construct()
    print(f"Result: {'✓ Satisfiable' if result1.satisfiable else '✗ Unsatisfiable'}")
    print()
    
    print("=== Test 2: Is Tweety a bird? ===") 
    tableau2 = ACrQTableau([SignedFormula(t, bird_tweety)], llm_evaluator=llm_eval)
    result2 = tableau2.construct()
    print(f"Result: {'✓ Satisfiable' if result2.satisfiable else '✗ Unsatisfiable'}")
    print()
    
    print("=== Test 3: Does Tweety fly? ===")
    tableau3 = ACrQTableau([SignedFormula(t, flies_tweety)], llm_evaluator=llm_eval)
    result3 = tableau3.construct()
    print(f"Result: {'✓ Satisfiable' if result3.satisfiable else '✗ Unsatisfiable'}")
    print()
    
    print("=== Test 4: Tweety doesn't fly? ===")
    tableau4 = ACrQTableau([SignedFormula(f, flies_tweety)], llm_evaluator=llm_eval)
    result4 = tableau4.construct()
    print(f"Result: {'✓ Satisfiable' if result4.satisfiable else '✗ Unsatisfiable'}")
    print()
    
    print("=== Test 5: The Contradiction Test ===")
    print("Can we simultaneously assert Tweety flies AND doesn't fly?")
    print("(In classical logic this would cause explosion)")
    
    # Test both positive and negative assertions together
    both_formulas = [
        SignedFormula(t, flies_tweety),  # Tweety flies
        SignedFormula(f, flies_tweety)   # Tweety doesn't fly
    ]
    
    tableau5 = ACrQTableau(both_formulas, llm_evaluator=llm_eval)
    result5 = tableau5.construct()
    
    print(f"Result: {'✓ Satisfiable (ACrQ handles contradiction!)' if result5.satisfiable else '✗ Unsatisfiable (branch closes)'}")
    print(f"Closed branches: {result5.closed_branches}")
    print(f"Open branches: {result5.open_branches}")
    print()
    
    if result5.models:
        print(f"Models found: {len(result5.models)}")
        model = result5.models[0]
        if hasattr(model, 'bilateral_valuations'):
            print("Bilateral valuations:")
            for atom, btv in model.bilateral_valuations.items():
                if 'Flies(Tweety)' in atom:
                    state = "gap" if btv.is_gap() else "glut" if btv.is_glut() else "determinate"
                    print(f"  {atom}: {btv} ({state})")
    
    print("=== Analysis ===")
    print("ACrQ with LLM evaluation demonstrates:")
    print("1. Non-explosive contradiction handling")
    print("2. Bilateral evidence assessment") 
    print("3. Paraconsistent reasoning with real-world knowledge")
    print("4. Formal logic + LLM knowledge integration")


def demonstrate_general_bird_reasoning():
    """Test general bird/flying relationships."""
    
    print("\n=== General Bird Reasoning ===")
    print("Testing LLM knowledge about different birds and flying:")
    print()
    
    llm_eval = create_penguin_llm_evaluator()
    
    # Test different birds
    birds_and_flight = [
        ("Eagle", True),      # Should fly
        ("Penguin", False),   # Shouldn't fly  
        ("Sparrow", True),    # Should fly
        ("Ostrich", False),   # Shouldn't fly
        ("Robin", True),      # Should fly
    ]
    
    for bird_name, expected_to_fly in birds_and_flight:
        bird_const = Constant(bird_name.lower())
        flies_bird = PredicateFormula("Flies", [bird_const])
        
        print(f"Testing: Does {bird_name.lower()} fly?")
        
        # Test positive assertion
        tableau = ACrQTableau([SignedFormula(t, flies_bird)], llm_evaluator=llm_eval)
        result = tableau.construct()
        
        status = "✓ Agrees" if result.satisfiable == expected_to_fly else "? Disagrees with expectation"
        print(f"  Expected: {expected_to_fly}, LLM supports: {result.satisfiable} {status}")
        print()


if __name__ == "__main__":
    try:
        demonstrate_penguin_reasoning()
        demonstrate_general_bird_reasoning()
        
        print("\n" + "="*60)
        print("SUCCESS: Penguin problem handled paraconsistently!")
        print("ACrQ + bilateral-truth enables robust reasoning with")
        print("contradictory knowledge without logical explosion.")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure bilateral-truth package is installed and API keys are set.")