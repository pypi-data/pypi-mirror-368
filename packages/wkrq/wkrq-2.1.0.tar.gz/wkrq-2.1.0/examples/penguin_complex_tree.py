#!/usr/bin/env python3
"""
Complex Penguin Tableau Tree: Multi-Branch Reasoning

This example demonstrates complex tableau trees with multiple branches,
showing how ACrQ handles more sophisticated reasoning scenarios with LLM integration.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from wkrq import (
    ACrQTableau, 
    PropositionalAtom, 
    PredicateFormula, 
    Constant, 
    SignedFormula,
    t, f
)
from wkrq.formula import CompoundFormula
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED

# Import the tree display functions from the other file
import sys
sys.path.append('.')
from penguin_detailed_trace import display_tableau_tree, display_detailed_branch_analysis, create_verbose_evaluator


def demonstrate_complex_penguin_reasoning():
    """Show complex reasoning with disjunctions and multiple branches."""
    
    print("🐧 COMPLEX PENGUIN REASONING: Multi-Branch Tree")
    print("=" * 70)
    print()
    print("Scenario: Testing a complex logical structure:")
    print("t:(Penguins swim well) ∨ (Penguins are good runners)")
    print()
    print("This will create branching in the tableau, demonstrating")
    print("how LLM evaluation works across multiple reasoning paths.")
    print()
    
    llm_eval = create_verbose_evaluator()
    
    # Create complex formula with disjunction
    swim_well = PropositionalAtom("Penguins swim well")
    good_runners = PropositionalAtom("Penguins are good runners") 
    
    # Create disjunction manually (since we need compound formula)
    disjunction = CompoundFormula("|", [swim_well, good_runners])
    initial_formula = SignedFormula(t, disjunction)
    
    print("🎯 INITIAL FORMULA:")
    print(f"   {initial_formula}")
    print()
    
    # Create tableau
    print("🏗️  CONSTRUCTING TABLEAU...")
    tableau = ACrQTableau([initial_formula], llm_evaluator=llm_eval)
    
    # Run construction
    result = tableau.construct()
    
    print("\n🏁 CONSTRUCTION COMPLETE")
    print("=" * 50)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models found: {len(result.models)}")
    print(f"Total nodes: {result.total_nodes}")
    print(f"Open branches: {result.open_branches}")
    print(f"Closed branches: {result.closed_branches}")
    
    # Show complete tree
    print("\n🌳 COMPLETE TABLEAU TREE:")
    print("=" * 50)
    display_tableau_tree(tableau)
    
    # Show detailed analysis
    display_detailed_branch_analysis(tableau)
    
    # Show models
    if result.models:
        print("📊 MODELS FOUND:")
        for i, model in enumerate(result.models):
            print(f"   Model {i+1}:")
            for atom, value in sorted(model.valuations.items()):
                print(f"     {atom} = {value}")
    
    return result


def demonstrate_multilevel_reasoning():
    """Show multiple levels of reasoning with nested implications."""
    
    print("\n\n🧠 MULTI-LEVEL PENGUIN REASONING")
    print("=" * 70) 
    print()
    print("Scenario: Testing nested logical structure:")
    print("f:(Penguins are tropical) → (Penguins like heat)")
    print()
    print("This tests implication handling with LLM evaluation")
    print("across multiple reasoning levels.")
    print()
    
    llm_eval = create_verbose_evaluator()
    
    # Create nested implication
    tropical = PropositionalAtom("Penguins are tropical")
    like_heat = PropositionalAtom("Penguins like heat")
    
    implication = CompoundFormula("->", [tropical, like_heat])
    initial_formula = SignedFormula(f, implication)  # Trying to falsify the implication
    
    print("🎯 INITIAL FORMULA:")
    print(f"   {initial_formula}")
    print()
    
    # Create tableau
    print("🏗️  CONSTRUCTING TABLEAU...")
    tableau = ACrQTableau([initial_formula], llm_evaluator=llm_eval)
    
    # Run construction
    result = tableau.construct()
    
    print("\n🏁 CONSTRUCTION COMPLETE")
    print("=" * 50)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models found: {len(result.models)}")
    print(f"Total nodes: {result.total_nodes}")
    print(f"Branches: {len(tableau.branches)}")
    
    # Show complete tree
    print("\n🌳 COMPLETE TABLEAU TREE:")
    print("=" * 50)
    display_tableau_tree(tableau)
    
    # Show detailed analysis
    display_detailed_branch_analysis(tableau)
    
    return result


def demonstrate_predicate_bilateral_reasoning():
    """Show bilateral predicate reasoning with multiple constants."""
    
    print("\n\n🔬 BILATERAL PREDICATE REASONING")
    print("=" * 70)
    print()
    print("Scenario: Testing bilateral predicates with multiple entities:")
    print("t:CanFly(emperor_penguin)")
    print()
    print("This will demonstrate bilateral predicate creation (R/R*)")
    print("and LLM evaluation of specific penguin species.")
    print()
    
    llm_eval = create_verbose_evaluator()
    
    # Create predicate with specific penguin species
    emperor = Constant("emperor_penguin")
    can_fly = PredicateFormula("CanFly", [emperor])
    initial_formula = SignedFormula(t, can_fly)
    
    print("🎯 INITIAL FORMULA:")
    print(f"   {initial_formula}")
    print()
    
    # Create tableau
    print("🏗️  CONSTRUCTING TABLEAU...")
    tableau = ACrQTableau([initial_formula], llm_evaluator=llm_eval)
    
    # Run construction  
    result = tableau.construct()
    
    print("\n🏁 CONSTRUCTION COMPLETE")
    print("=" * 50)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models found: {len(result.models)}")
    print(f"Total nodes: {result.total_nodes}")
    
    # Show complete tree
    print("\n🌳 COMPLETE TABLEAU TREE:")
    print("=" * 50)
    display_tableau_tree(tableau)
    
    # Show detailed analysis
    display_detailed_branch_analysis(tableau)
    
    # Show bilateral valuations specifically
    if result.models:
        print("📊 MODELS WITH BILATERAL VALUATIONS:")
        for i, model in enumerate(result.models):
            print(f"   Model {i+1}:")
            
            # Standard valuations
            for atom, value in sorted(model.valuations.items()):
                print(f"     {atom} = {value}")
            
            # Bilateral valuations  
            if hasattr(model, 'bilateral_valuations') and model.bilateral_valuations:
                print(f"   Bilateral evidence:")
                for atom, btv in sorted(model.bilateral_valuations.items()):
                    state = ("knowledge gap" if btv.is_gap() else
                           "knowledge glut" if btv.is_glut() else  
                           "determinate evidence")
                    print(f"     {atom}: positive={btv.positive}, negative={btv.negative} ({state})")
    
    return result


if __name__ == "__main__":
    try:
        print("🎭 COMPLEX PENGUIN TABLEAU DEMONSTRATIONS")
        print("=" * 80)
        print()
        print("These examples show sophisticated tableau trees with:")
        print("• Multiple branches from logical connectives")
        print("• LLM evaluation at different tree levels") 
        print("• Bilateral predicate reasoning")
        print("• Complete tree structure visualization")
        print()
        
        # Run demonstrations
        demonstrate_complex_penguin_reasoning()
        demonstrate_multilevel_reasoning()
        demonstrate_predicate_bilateral_reasoning()
        
        print("\n" + "🏆 ALL COMPLEX DEMONSTRATIONS COMPLETE" + "\n" + "=" * 80)
        print("🎓 Key Educational Points:")
        print("1. 🌳 Tableau trees show complete reasoning structure")
        print("2. 🤖 LLM evaluation integrates at any tree level")
        print("3. 🔄 Multiple branches explore different reasoning paths")
        print("4. 📊 Bilateral predicates handle positive/negative evidence")
        print("5. 🛡️  Paraconsistent logic manages contradictions gracefully")
        print("6. 📋 Every inference step is formally justified")
        print()
        print("Perfect for teaching formal reasoning with AI integration!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()