#!/usr/bin/env python3
"""
Simple usage example: Using bilateral-truth with ACrQ tableau.

This shows the minimal code needed to integrate bilateral-truth 
with wKrQ's ACrQ tableau system.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from wkrq import ACrQTableau, PropositionalAtom, SignedFormula, t
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_llm_tableau_evaluator():
    """Create evaluator function for ACrQ tableau."""
    # Create bilateral-truth LLM evaluator
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        """Convert wKrQ formula to bilateral-truth format and evaluate."""
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        # Map bilateral-truth <u,v> to ACrQ BilateralTruthValue
        from bilateral_truth.truth_values import TruthValueComponent
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


# Example usage
if __name__ == "__main__":
    # Create LLM evaluator
    llm_eval = create_llm_tableau_evaluator()
    
    # Test a factual claim
    claim = PropositionalAtom("Paris is the capital of France")
    
    # Create ACrQ tableau with LLM integration
    tableau = ACrQTableau([SignedFormula(t, claim)], llm_evaluator=llm_eval)
    
    # Run tableau
    result = tableau.construct()
    
    print(f"Claim: {claim}")
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models: {len(result.models)}")