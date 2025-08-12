#!/usr/bin/env python3
"""
ACrQ Tableau with LLM Integration: Penguin Reasoning Examples

This example demonstrates the integration of large language model evaluation
with ACrQ tableau construction. Compound formulas trigger ACrQ tableau rules
while atomic formulas undergo LLM evaluation, creating a hybrid reasoning system
that combines formal logic with neural language model knowledge.
"""

import subprocess
import sys
from typing import List, Tuple
import os
from dotenv import load_dotenv
load_dotenv()

# Import LLM integration components
from wkrq import ACrQTableau, PropositionalAtom, SignedFormula, t, f
from wkrq.formula import CompoundFormula
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED
from wkrq.cli import TableauTreeRenderer


def run_wkrq_command(args: List[str]) -> Tuple[str, str, int]:
    """Run a wkrq command and return stdout, stderr, and return code."""
    cmd = ["python", "-m", "wkrq"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 1
    except Exception as e:
        return "", f"ERROR: {e}", 1


def print_test_section(title: str):
    """Print a formatted test section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)


def create_penguin_llm_evaluator():
    """Create LLM evaluator with feedback for penguin examples."""
    bilateral_evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, bilateral_evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        print(f"    🤖 '{formula}' → <{u},{v}> → BilateralTruthValue({pos}, {neg})")
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


def print_test_case_with_llm(description: str, signed_formula: SignedFormula, analysis: str = ""):
    """Print a test case with LLM integration showing LLM-Eval rules."""
    print(f"\n{'-'*60}")
    print(f"Test: {description}")
    print(f"Formula: {signed_formula}")
    print(f"{'-'*60}")
    
    # Create LLM evaluator
    llm_eval = create_penguin_llm_evaluator()
    
    # Create tableau with LLM integration
    print("🏗️  CONSTRUCTING TABLEAU WITH LLM INTEGRATION...")
    tableau = ACrQTableau([signed_formula], llm_evaluator=llm_eval)
    result = tableau.construct()
    
    print(f"\n🏁 RESULTS:")
    print(f"   Satisfiable: {result.satisfiable}")
    print(f"   Total branches: {len(tableau.branches)}")
    print(f"   Total nodes: {result.total_nodes}")
    
    # Display tableau tree using CLI renderer
    print(f"\n🌳 TABLEAU TREE WITH LLM-EVAL RULES:")
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    if analysis:
        print(f"\n📋 ANALYSIS:")
        print(analysis)


def print_test_case(description: str, command: List[str], analysis: str = ""):
    """Print a regular CLI test case (for comparison)."""
    print(f"\n{'-'*60}")
    print(f"Test: {description} (CLI Only)")
    print(f"Command: wkrq {' '.join(command)}")
    print(f"{'-'*60}")
    
    stdout, stderr, returncode = run_wkrq_command(command)
    
    if stderr and stderr != "":
        print(f"STDERR: {stderr}")
    
    if returncode != 0:
        print(f"RETURN CODE: {returncode}")
    
    print(stdout)
    
    if analysis:
        print(f"\n📋 ANALYSIS:")
        print(analysis)


def demonstrate_disjunction_branching():
    """Demonstrate disjunction branching with LLM evaluation."""
    
    print_test_section("ACrQ Disjunction with LLM Integration")
    print()
    print("Testing: f:(Penguins can fly) ∨ (Penguins are mammals)")
    print()
    print("The f-disjunction rule creates branches for f:A and f:B.")
    print("LLM evaluation then assesses the atomic formulas at branch endpoints.")
    
    # Create disjunction formula
    can_fly = PropositionalAtom("Penguins can fly")
    are_mammals = PropositionalAtom("Penguins are mammals")
    disjunction = CompoundFormula("|", [can_fly, are_mammals])
    signed_formula = SignedFormula(f, disjunction)
    
    print_test_case_with_llm(
        "Disjunction with LLM evaluation",
        signed_formula,
        "Demonstrates how LLM knowledge can validate logical branching outcomes"
    )
    
    # Show comparison with standard tableau
    print_test_case(
        "Standard ACrQ tableau (no LLM)",
        ["--sign=f", "--tree", "--show-rules", "PenguinsCanFly | PenguinsAreMammals"],
        "Shows the baseline formal reasoning without external knowledge integration"
    )


def demonstrate_conjunction_branching():
    """Demonstrate conjunction branching with LLM evaluation."""
    
    print_test_section("ACrQ Conjunction with LLM Integration")
    print()
    print("Testing: f:(Penguins swim well) ∧ (Penguins are birds)")
    print()
    print("The f-conjunction rule creates multiple branches:")
    print("f:A (first conjunct false), f:B (second conjunct false),")
    print("e:A (first conjunct undefined), e:B (second conjunct undefined)")
    print()
    print("LLM evaluation determines truth values for atomic formulas on each branch.")
    
    # Create conjunction formula
    swim_well = PropositionalAtom("Penguins swim well")
    are_birds = PropositionalAtom("Penguins are birds")
    conjunction = CompoundFormula("&", [swim_well, are_birds])
    signed_formula = SignedFormula(f, conjunction)
    
    print_test_case_with_llm(
        "Conjunction with LLM evaluation",
        signed_formula,
        "Shows how LLM knowledge can contradict formal assumptions, leading to branch closure"
    )


def demonstrate_implication_branching():
    """Demonstrate implication branching with LLM evaluation."""
    
    print_test_section("ACrQ Implication with LLM Integration")
    print()
    print("Testing: f:(Penguins are birds) → (Penguins can fly)")
    print()
    print("The f-implication rule creates branches t:A and f:B,")
    print("representing the conditions needed for the implication to be false:")
    print("antecedent must be true AND consequent must be false.")
    print()
    print("LLM evaluation provides empirical assessment of both conditions.")
    
    # Create implication formula
    are_birds = PropositionalAtom("Penguins are birds")
    can_fly = PropositionalAtom("Penguins can fly")
    implication = CompoundFormula("->", [are_birds, can_fly])
    signed_formula = SignedFormula(f, implication)
    
    print_test_case_with_llm(
        "Implication with LLM evaluation",
        signed_formula,
        "Demonstrates empirical validation of logical conditions in formal reasoning"
    )


def demonstrate_nested_formula_branching():
    """Demonstrate nested formula with multi-level LLM integration."""
    
    print_test_section("ACrQ Nested Formula with LLM Integration")
    print()
    print("Testing: t:((Penguins swim) ∨ (Penguins fly)) ∧ (Penguins are birds)")
    print()
    print("This demonstrates multi-level tableau expansion:")
    print("1. t-conjunction rule expands the outer conjunction")
    print("2. Further rules may expand inner formulas")
    print("3. LLM evaluation occurs at atomic formula endpoints")
    
    # Create nested formula: ((A ∨ B) ∧ C)
    swim = PropositionalAtom("Penguins swim")
    fly = PropositionalAtom("Penguins fly")
    are_birds = PropositionalAtom("Penguins are birds")
    
    # Inner disjunction: (A ∨ B)
    inner_disj = CompoundFormula("|", [swim, fly])
    
    # Outer conjunction: (A ∨ B) ∧ C
    outer_conj = CompoundFormula("&", [inner_disj, are_birds])
    signed_formula = SignedFormula(t, outer_conj)
    
    print_test_case_with_llm(
        "Nested formula with LLM evaluation",
        signed_formula,
        "Shows hierarchical application of tableau rules and LLM evaluation"
    )


def demonstrate_atomic_evaluation():
    """Demonstrate direct LLM evaluation of atomic formulas."""
    
    print_test_section("Direct LLM Evaluation of Atomic Formulas")
    print()
    print("Testing atomic formulas to demonstrate LLM evaluation integration.")
    
    # Test simple atomic formula
    atomic_formula = PropositionalAtom("Penguins are birds")
    atomic_signed = SignedFormula(t, atomic_formula)
    
    print_test_case_with_llm(
        "Atomic formula evaluation",
        atomic_signed,
        "Shows direct integration of LLM knowledge into tableau construction"
    )


def demonstrate_contradiction_detection():
    """Demonstrate LLM-based contradiction detection."""
    
    print_test_section("LLM-Based Contradiction Detection")
    print()
    print("Testing formulas where LLM knowledge contradicts logical assumptions.")
    
    # Test atomic formula that LLM will disagree with
    fly_formula = PropositionalAtom("Penguins can fly")
    fly_signed_true = SignedFormula(t, fly_formula)
    
    print_test_case_with_llm(
        "Formula contradicting LLM knowledge",
        fly_signed_true,
        "Demonstrates how LLM evaluation can detect and resolve logical contradictions"
    )
    
    # Test logical contradiction that requires LLM evaluation to detect
    penguin_fly = PropositionalAtom("Penguins can fly")
    not_fly = CompoundFormula("~", [penguin_fly])
    contradiction = CompoundFormula("&", [penguin_fly, not_fly])
    contradiction_signed = SignedFormula(t, contradiction)
    
    print_test_case_with_llm(
        "Logical contradiction with LLM evaluation",
        contradiction_signed,
        "Shows LLM evaluation within formal contradiction detection"
    )


def main():
    """Run ACrQ tableau demonstrations with LLM integration."""
    try:
        print("ACrQ TABLEAU WITH LLM INTEGRATION")
        print("=" * 60)
        print("Demonstration of hybrid reasoning system combining formal logic")
        print("with large language model evaluation capabilities.")
        print()
        print("System components:")
        print("• ACrQ tableau rules for formal logical inference")
        print("• LLM-Eval rules for atomic formula assessment")
        print("• Bilateral truth values for paraconsistent reasoning")
        print("• Integrated contradiction detection and branch closure")
        print()
        
        # Run integrated demonstrations
        demonstrate_disjunction_branching()
        demonstrate_conjunction_branching()
        demonstrate_implication_branching()
        demonstrate_nested_formula_branching()
        demonstrate_atomic_evaluation()
        demonstrate_contradiction_detection()
        
        print("\n" + "DEMONSTRATION COMPLETE")
        print("=" * 40)
        print()
        print("Summary of capabilities demonstrated:")
        print("• Multi-branch tableau construction with ACrQ rules")
        print("• LLM evaluation integrated as formal tableau rules")
        print("• Contradiction detection through LLM knowledge")
        print("• Hierarchical rule application in complex formulas")
        print("• Empirical validation of logical assumptions")
        print()
        print("This system enables formal reasoning augmented with")
        print("empirical knowledge from large language models.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()