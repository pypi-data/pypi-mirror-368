#!/usr/bin/env python3
"""
Integration example: bilateral-truth package with wKrQ ACrQ tableau.

This example shows how to integrate the bilateral-truth package's zeta_c
function with the ACrQ tableau to provide LLM-based bilateral factuality
evaluation for atomic formulas during tableau construction.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from wkrq import (
    ACrQTableau,
    BilateralTruthValue, 
    PredicateFormula,
    PropositionalAtom,
    Constant,
    SignedFormula,
    t, f
)
from wkrq.semantics import TRUE, FALSE, UNDEFINED

try:
    from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
    BILATERAL_TRUTH_AVAILABLE = True
except ImportError:
    BILATERAL_TRUTH_AVAILABLE = False
    print("Error: bilateral-truth package not found.")
    print("Install with: pip install bilateral-truth[openai]")
    exit(1)


def create_bilateral_truth_evaluator(llm_provider='openai', model='gpt-4o-mini', **kwargs):
    """
    Create an LLM evaluator function compatible with ACrQ tableau.
    
    Args:
        llm_provider: LLM provider ('openai', 'anthropic', etc.)
        model: Model name
        **kwargs: Additional arguments for create_llm_evaluator
        
    Returns:
        Function that takes a Formula and returns BilateralTruthValue
    """
    # Create the bilateral-truth evaluator
    evaluator = create_llm_evaluator(llm_provider, model=model, **kwargs)
    
    def formula_evaluator(formula):
        """
        Evaluate a wKrQ Formula using bilateral-truth package.
        
        Args:
            formula: A wKrQ Formula object (atomic)
            
        Returns:
            BilateralTruthValue mapping from bilateral-truth <u,v> format
        """
        # Convert wKrQ formula to bilateral-truth Assertion
        formula_text = str(formula)
        assertion = Assertion(formula_text)
        
        # Call bilateral-truth zeta_c function
        try:
            generalized_truth_value = zeta_c(assertion, evaluator.evaluate_bilateral)
            
            # Extract u (verifiability) and v (refutability) components
            u, v = generalized_truth_value.u, generalized_truth_value.v
            
            # Convert to wKrQ BilateralTruthValue
            # u (verifiability) maps to positive evidence (R)
            # v (refutability) maps to negative evidence (R*)
            positive_value = _convert_truth_component(u)
            negative_value = _convert_truth_component(v)
            
            return BilateralTruthValue(
                positive=positive_value,
                negative=negative_value
            )
            
        except Exception as e:
            print(f"Warning: bilateral-truth evaluation failed for {formula_text}: {e}")
            # Return knowledge gap on error
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
    
    return formula_evaluator


def _convert_truth_component(component):
    """
    Convert bilateral-truth truth component to wKrQ TruthValue.
    
    Args:
        component: Truth component from bilateral-truth TruthValueComponent enum
        
    Returns:
        wKrQ TruthValue (TRUE, UNDEFINED, FALSE)
    """
    from bilateral_truth.truth_values import TruthValueComponent
    
    if component == TruthValueComponent.TRUE:
        return TRUE
    elif component == TruthValueComponent.UNDEFINED: 
        return UNDEFINED
    elif component == TruthValueComponent.FALSE:
        return FALSE
    else:
        # Unknown component, default to undefined
        return UNDEFINED


def run_bilateral_truth_example():
    """Demonstrate bilateral-truth integration with ACrQ tableau."""
    
    if not BILATERAL_TRUTH_AVAILABLE:
        print("bilateral-truth package not available. Skipping example.")
        return
    
    # Create the bilateral-truth evaluator
    print("Creating bilateral-truth evaluator...")
    llm_evaluator = create_bilateral_truth_evaluator()
    
    # Create some test formulas
    socrates = Constant("socrates")
    human_socrates = PredicateFormula("Human", [socrates])
    
    # Propositional examples
    earth_round = PropositionalAtom("The Earth is round")
    paris_capital = PropositionalAtom("Paris is the capital of France")
    
    print("=== Bilateral-Truth + ACrQ Tableau Integration ===\n")
    
    # Example 1: Well-known factual assertion
    print("Example 1: Testing t:Paris is the capital of France")
    print("Expected: LLM should provide strong positive evidence")
    
    tableau1 = ACrQTableau(
        [SignedFormula(t, paris_capital)], 
        llm_evaluator=llm_evaluator
    )
    result1 = tableau1.construct()
    
    print(f"Satisfiable: {result1.satisfiable}")
    if result1.models and hasattr(result1.models[0], 'bilateral_valuations'):
        print(f"Bilateral valuations: {result1.models[0].bilateral_valuations}")
    print()
    
    # Example 2: Test contradiction
    print("Example 2: Testing f:The Earth is round")
    print("Expected: Should be unsatisfiable (LLM knows Earth is round)")
    
    tableau2 = ACrQTableau(
        [SignedFormula(f, earth_round)], 
        llm_evaluator=llm_evaluator
    )
    result2 = tableau2.construct()
    
    print(f"Satisfiable: {result2.satisfiable}")
    print(f"Closed branches: {result2.closed_branches}")
    print()
    
    # Example 3: Predicate logic
    print("Example 3: Testing t:Human(socrates)")
    print("Expected: LLM should recognize Socrates as human")
    
    tableau3 = ACrQTableau(
        [SignedFormula(t, human_socrates)], 
        llm_evaluator=llm_evaluator
    )
    result3 = tableau3.construct()
    
    print(f"Satisfiable: {result3.satisfiable}")
    if result3.models:
        print(f"Models found: {len(result3.models)}")
        if hasattr(result3.models[0], 'bilateral_valuations'):
            print(f"Bilateral valuations: {result3.models[0].bilateral_valuations}")
    print()


def demonstrate_truth_value_mapping():
    """Show how bilateral-truth <u,v> maps to ACrQ BilateralTruthValue."""
    
    print("=== Truth Value Mapping ===")
    print("bilateral-truth <u,v> → ACrQ BilateralTruthValue(positive, negative)")
    print()
    
    test_cases = [
        ('t', 'f'),  # Definitely true (verified, not refutable)
        ('f', 't'),  # Definitely false (not verified, refutable)  
        ('t', 't'),  # Contradictory (both verified and refutable - glut)
        ('f', 'f'),  # Uncertain (neither verified nor refutable - gap)
        ('e', 'f'),  # Undefined verifiability, not refutable
        ('t', 'e'),  # Verified, undefined refutability
    ]
    
    for u, v in test_cases:
        pos = _convert_truth_component(u)
        neg = _convert_truth_component(v)
        btv = BilateralTruthValue(positive=pos, negative=neg)
        
        # Determine the information state
        if btv.is_determinate():
            if btv.positive == TRUE:
                state = "definitely true"
            else:
                state = "definitely false"
        elif btv.is_glut():
            state = "contradictory (glut)"
        elif btv.is_gap():
            state = "uncertain (gap)"
        else:
            state = "complex"
            
        print(f"<{u},{v}> → BilateralTruthValue({pos}, {neg}) → {state}")


if __name__ == "__main__":
    demonstrate_truth_value_mapping()
    print()
    run_bilateral_truth_example()
    
    print("\n=== Integration Summary ===")
    print("1. bilateral-truth zeta_c() returns <u,v> generalized truth values")
    print("2. u (verifiability) maps to positive evidence in ACrQ")  
    print("3. v (refutability) maps to negative evidence in ACrQ")
    print("4. ACrQ tableau handles gluts and gaps paraconsistently")
    print("5. LLM evaluation becomes a formal tableau rule")