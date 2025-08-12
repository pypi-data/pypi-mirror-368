#!/usr/bin/env python3
"""
Test the general tracing system for any tableau proof.
"""

from wkrq import parse, solve, valid, entails, check_inference, parse_inference
from wkrq.signs import t, f, e
from wkrq.cli import TableauTreeRenderer


def test_simple_contradiction():
    """Test tracing with a simple contradiction."""
    print("=" * 70)
    print("TEST 1: Simple Contradiction")
    print("=" * 70)
    
    formula = parse("P & ~P")
    print(f"\nFormula: {formula}")
    
    # Solve with tracing
    result = solve(formula, trace=True)
    
    # Print the trace
    result.print_trace()
    
    # Print the final tableau
    print("\n" + "=" * 70)
    print("FINAL TABLEAU")
    print("=" * 70)
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")


def test_quantifier_reasoning():
    """Test tracing with quantifier instantiation."""
    print("\n" + "=" * 70)
    print("TEST 2: Quantifier Reasoning")
    print("=" * 70)
    
    formula = parse("[∀X P(X)]Q(X) & P(a) & ~Q(a)")
    print(f"\nFormula: {formula}")
    
    # Solve with tracing
    result = solve(formula, trace=True)
    
    # Print step-by-step construction
    if result.construction_trace:
        result.construction_trace.print_step_by_step()
    
    # Print the final tableau
    print("\n" + "=" * 70)
    print("FINAL TABLEAU")
    print("=" * 70)
    renderer = TableauTreeRenderer(show_rules=True)
    print(renderer.render_ascii(result.tableau))
    
    print(f"\nResult: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")


def test_inference_tracing():
    """Test tracing with inference checking."""
    print("\n" + "=" * 70)
    print("TEST 3: Inference Checking with Trace")
    print("=" * 70)
    
    inference_str = "P → Q, Q → R ⊢ P → R"
    inference = parse_inference(inference_str)
    print(f"\nInference: {inference}")
    
    # Check inference with tracing
    result = check_inference(inference, trace=True)
    
    print(f"\n{result}")
    
    # Access the trace through the tableau result
    if result.tableau_result.construction_trace:
        print("\n" + "-" * 70)
        print("INFERENCE PROOF TRACE")
        print("-" * 70)
        # Get rule summary
        for line in result.tableau_result.construction_trace.get_rule_summary():
            print(line)


def test_complex_formula():
    """Test tracing with a complex formula."""
    print("\n" + "=" * 70)
    print("TEST 4: Complex Formula")
    print("=" * 70)
    
    formula = parse("(P ∨ Q) & (~P ∨ R) & (~Q ∨ S) & ~(R & S)")
    print(f"\nFormula: {formula}")
    
    # Solve with different signs
    for sign in [t, f]:
        print(f"\n--- Testing with sign {sign} ---")
        result = solve(formula, sign, trace=True)
        
        # Print summary only
        if result.construction_trace:
            print(f"Total steps: {len(result.construction_trace.rule_applications)}")
            print(f"Branches created: {result.construction_trace.total_branches}")
            print(f"Branches closed: {result.construction_trace.closed_branches}")
            print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
            
            # Show rules applied
            rule_counts = {}
            for app in result.construction_trace.rule_applications:
                rule_counts[app.rule_name] = rule_counts.get(app.rule_name, 0) + 1
            print("Rules applied:")
            for rule, count in sorted(rule_counts.items()):
                print(f"  {rule}: {count}x")


def test_entailment_tracing():
    """Test tracing with entailment checking."""
    print("\n" + "=" * 70)
    print("TEST 5: Entailment with Trace")
    print("=" * 70)
    
    premises = [parse("P → Q"), parse("Q → R")]
    conclusion = parse("P → R")
    
    print(f"\nPremises: {', '.join(str(p) for p in premises)}")
    print(f"Conclusion: {conclusion}")
    
    # We need to modify entails to support tracing
    # For now, let's construct it manually
    from wkrq.formula import Conjunction, Negation
    
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    
    result = solve(test_formula, t, trace=True)
    
    is_entailed = not result.satisfiable
    print(f"\nEntailment: {'VALID' if is_entailed else 'INVALID'}")
    
    if result.construction_trace:
        print(f"Proof required {len(result.construction_trace.rule_applications)} steps")
        if not is_entailed:
            print(f"Found {len(result.models)} countermodel(s)")


def main():
    """Run all tracing tests."""
    print("GENERAL TABLEAU TRACING SYSTEM")
    print("Demonstrating whiteboard-style explanations for any proof")
    print()
    
    test_simple_contradiction()
    test_quantifier_reasoning()
    test_inference_tracing()
    test_complex_formula()
    test_entailment_tracing()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("The tracing system provides:")
    print("  1. Complete rule application history")
    print("  2. What each rule produced (even if not added)")
    print("  3. Branch closure explanations")
    print("  4. Step-by-step construction narrative")
    print("  5. Statistical summaries")
    print("\nThis works for ANY formula or inference in wKrQ/ACrQ.")


if __name__ == "__main__":
    main()