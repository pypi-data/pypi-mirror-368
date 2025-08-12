#!/usr/bin/env python3
"""
Example: Integrating LLM evaluation with ACrQ tableau procedure.

This example shows how to integrate an external LLM-based evaluation function
with the ACrQ tableau to provide truth values for atomic formulas during 
tableau construction.
"""

from wkrq import (
    ACrQTableau,
    BilateralTruthValue, 
    TRUE, FALSE, UNDEFINED,
    PredicateFormula,
    Constant,
    SignedFormula,
    t, f
)


def example_llm_evaluator(formula):
    """
    Example LLM evaluator function.
    
    In practice, this would call your Python package that interfaces with an LLM.
    For this example, we'll simulate some knowledge:
    - Human(socrates) is definitely true
    - Mortal(socrates) is definitely true  
    - Flying(socrates) has conflicting evidence (glut)
    - Unknown predicates return gaps
    """
    formula_str = str(formula)
    
    # Simulate LLM knowledge
    if formula_str == "Human(socrates)":
        return BilateralTruthValue(positive=TRUE, negative=FALSE)
    elif formula_str == "Mortal(socrates)":
        return BilateralTruthValue(positive=TRUE, negative=FALSE)
    elif formula_str == "Flying(socrates)":
        # Conflicting evidence - both positive and negative are true (glut)
        return BilateralTruthValue(positive=TRUE, negative=TRUE)
    elif formula_str == "Robot(socrates)":
        return BilateralTruthValue(positive=FALSE, negative=TRUE)
    else:
        # Unknown - knowledge gap
        return BilateralTruthValue(positive=FALSE, negative=FALSE)


def run_example():
    """Demonstrate LLM integration with ACrQ tableau."""
    
    # Create some atomic formulas
    socrates = Constant("socrates")
    human_socrates = PredicateFormula("Human", [socrates])
    mortal_socrates = PredicateFormula("Mortal", [socrates])
    flying_socrates = PredicateFormula("Flying", [socrates])
    
    print("=== LLM Integration with ACrQ Tableau ===\n")
    
    # Example 1: Test satisfiability of Human(socrates)
    print("Example 1: Testing t:Human(socrates)")
    print("Expected: LLM should provide positive evidence for Human(socrates)")
    
    tableau1 = ACrQTableau(
        [SignedFormula(t, human_socrates)], 
        llm_evaluator=example_llm_evaluator
    )
    result1 = tableau1.construct()
    
    print(f"Satisfiable: {result1.satisfiable}")
    print(f"Models: {len(result1.models)}")
    if result1.models:
        print(f"First model: {result1.models[0]}")
    print()
    
    # Example 2: Test a contradiction - trying to prove something false that LLM knows is true
    print("Example 2: Testing f:Human(socrates)")
    print("Expected: Should be unsatisfiable since LLM knows Human(socrates) is true")
    
    tableau2 = ACrQTableau(
        [SignedFormula(f, human_socrates)], 
        llm_evaluator=example_llm_evaluator
    )
    result2 = tableau2.construct()
    
    print(f"Satisfiable: {result2.satisfiable}")
    print(f"Closed branches: {result2.closed_branches}")
    print()
    
    # Example 3: Test a glut case - Flying(socrates) has conflicting evidence
    print("Example 3: Testing t:Flying(socrates)")
    print("Expected: Should be satisfiable despite conflicting evidence (ACrQ allows gluts)")
    
    tableau3 = ACrQTableau(
        [SignedFormula(t, flying_socrates)], 
        llm_evaluator=example_llm_evaluator
    )
    result3 = tableau3.construct()
    
    print(f"Satisfiable: {result3.satisfiable}")
    print(f"Models: {len(result3.models)}")
    if result3.models:
        print(f"First model valuations: {result3.models[0].valuations}")
    print()
    
    # Example 4: Test knowledge gap
    print("Example 4: Testing t:Unknown(socrates)")  
    print("Expected: Should be satisfiable with undefined/gap information")
    
    unknown_socrates = PredicateFormula("Unknown", [socrates])
    tableau4 = ACrQTableau(
        [SignedFormula(t, unknown_socrates)], 
        llm_evaluator=example_llm_evaluator
    )
    result4 = tableau4.construct()
    
    print(f"Satisfiable: {result4.satisfiable}")
    print(f"Models: {len(result4.models)}")
    print()


def real_llm_integration_template():
    """
    Template for integrating with a real LLM package.
    
    Replace this with calls to your actual LLM evaluation package.
    """
    
    def real_llm_evaluator(formula):
        """
        Template for real LLM evaluator.
        
        Args:
            formula: An atomic Formula object (PredicateFormula, PropositionalAtom, etc.)
            
        Returns:
            BilateralTruthValue representing the LLM's assessment
        """
        
        # Convert formula to string or extract relevant information
        formula_text = str(formula)
        
        # TODO: Call your LLM package here
        # Example:
        # from your_llm_package import evaluate_assertion
        # llm_response = evaluate_assertion(formula_text)
        
        # TODO: Convert LLM response to BilateralTruthValue
        # The LLM might return something like:
        # {
        #   "positive_evidence": 0.9,    # confidence that R is true
        #   "negative_evidence": 0.1,    # confidence that R* (negation) is true  
        #   "uncertainty": 0.2           # overall uncertainty
        # }
        
        # Convert to discrete truth values based on thresholds
        # pos_val = TRUE if llm_response["positive_evidence"] > 0.7 else FALSE
        # neg_val = TRUE if llm_response["negative_evidence"] > 0.7 else FALSE
        
        # For now, return a placeholder
        return BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED)
    
    return real_llm_evaluator


if __name__ == "__main__":
    run_example()
    
    print("\n=== Integration Template ===")
    print("See real_llm_integration_template() function for guidance on")
    print("integrating with your actual LLM evaluation package.")