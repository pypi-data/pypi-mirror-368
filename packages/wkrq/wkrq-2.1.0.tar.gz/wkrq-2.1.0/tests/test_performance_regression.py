#!/usr/bin/env python3
"""
Performance Regression Tests for wKrQ

Ensures that optimizations maintain industrial-grade performance benchmarks.
These tests fail if performance degrades below acceptable thresholds.
"""

import statistics
import time

import pytest

from wkrq import Formula, check_inference, parse_inference, solve, t


class TestBasicPerformanceBenchmarks:
    """Basic performance benchmarks that must be maintained."""

    def test_simple_atom_performance(self):
        """Simple atoms should solve in microseconds."""
        p = Formula.atom("p")

        # Run multiple times for statistical reliability
        times = []
        for _ in range(10):
            start = time.time()
            result = solve(p, t)
            end = time.time()
            times.append((end - start) * 1000)  # Convert to milliseconds

        avg_time = statistics.mean(times)
        max_time = max(times)

        assert result.satisfiable, "Simple atom should be satisfiable"
        assert avg_time < 1.0, f"Average time {avg_time:.3f}ms should be < 1ms"
        assert max_time < 5.0, f"Max time {max_time:.3f}ms should be < 5ms"

    def test_conjunction_performance(self):
        """Conjunctions should solve in sub-millisecond time."""
        p, q = Formula.atoms("p", "q")
        formula = p & q

        times = []
        for _ in range(10):
            start = time.time()
            result = solve(formula, t)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert result.satisfiable, "Conjunction should be satisfiable"
        assert avg_time < 2.0, f"Average time {avg_time:.3f}ms should be < 2ms"

    def test_disjunction_branching_performance(self):
        """Disjunctions should handle branching efficiently."""
        p, q = Formula.atoms("p", "q")
        formula = p | q

        times = []
        for _ in range(10):
            start = time.time()
            result = solve(formula, t)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert result.satisfiable, "Disjunction should be satisfiable"
        assert len(result.models) >= 2, "Should find multiple models"
        assert avg_time < 2.0, f"Average time {avg_time:.3f}ms should be < 2ms"

    def test_negation_alpha_rule_performance(self):
        """Negation (alpha rule) should be processed very quickly."""
        p = Formula.atom("p")
        formula = ~~p  # Double negation

        times = []
        for _ in range(10):
            start = time.time()
            result = solve(formula, t)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert result.satisfiable, "Double negation should be satisfiable"
        assert (
            avg_time < 1.0
        ), f"Average time {avg_time:.3f}ms should be < 1ms (alpha rule priority)"

    def test_contradiction_detection_performance(self):
        """Contradictions should be detected immediately."""
        p = Formula.atom("p")
        contradiction = p & ~p

        times = []
        for _ in range(10):
            start = time.time()
            result = solve(contradiction, t)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert not result.satisfiable, "Contradiction should be unsatisfiable"
        assert (
            avg_time < 1.0
        ), f"Average time {avg_time:.3f}ms should be < 1ms (fast closure)"


class TestScalabilityBenchmarks:
    """Test scalability with increasingly complex formulas."""

    def test_wide_conjunction_scaling(self):
        """Wide conjunctions should scale linearly."""
        sizes = [5, 10, 15, 20]
        times = []

        for size in sizes:
            atoms = [Formula.atom(f"p{i}") for i in range(size)]
            formula = atoms[0]
            for atom in atoms[1:]:
                formula = formula & atom

            start = time.time()
            result = solve(formula, t)
            end = time.time()

            elapsed = (end - start) * 1000
            times.append(elapsed)

            assert (
                result.satisfiable
            ), f"Conjunction of {size} atoms should be satisfiable"

        # Check that time growth is reasonable (not exponential)
        for i in range(1, len(times)):
            ratio = times[i] / times[i - 1]
            assert (
                ratio < 7.0
            ), f"Time ratio {ratio:.2f} should not exceed 7x for reasonable scaling"

        # Final size should still be fast
        assert (
            times[-1] < 50.0
        ), f"Large conjunction time {times[-1]:.3f}ms should be < 50ms"

    def test_deep_nesting_performance(self):
        """Deeply nested formulas should be handled efficiently."""
        p, q = Formula.atoms("p", "q")

        # Build deeply nested implication
        formula = p
        for _i in range(10):
            formula = p.implies(formula)

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "Deep nesting should be satisfiable"
        assert elapsed < 100.0, f"Deep nesting time {elapsed:.3f}ms should be < 100ms"

    def test_cnf_formula_performance(self):
        """CNF formulas should benefit from optimization."""
        # Create 3-SAT style formula: (p1 ∨ p2 ∨ p3) ∧ (¬p1 ∨ p4 ∨ p5) ∧ ...
        atoms = [Formula.atom(f"p{i}") for i in range(15)]

        clauses = [
            atoms[0] | atoms[1] | atoms[2],
            ~atoms[0] | atoms[3] | atoms[4],
            atoms[1] | ~atoms[2] | atoms[5],
            ~atoms[3] | atoms[6] | atoms[7],
            atoms[4] | atoms[8] | ~atoms[5],
        ]

        formula = clauses[0]
        for clause in clauses[1:]:
            formula = formula & clause

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "CNF formula should be satisfiable"
        assert elapsed < 200.0, f"CNF formula time {elapsed:.3f}ms should be < 200ms"
        assert (
            result.total_nodes < 200
        ), f"Node count {result.total_nodes} should be reasonable"

    def test_branching_factor_control(self):
        """Ensure branching factor doesn't explode exponentially."""
        # Formula that could cause exponential branching: (p1 ∨ q1) ∧ (p2 ∨ q2) ∧ ...
        pairs = [(Formula.atom(f"p{i}"), Formula.atom(f"q{i}")) for i in range(8)]

        clauses = [p | q for p, q in pairs]
        formula = clauses[0]
        for clause in clauses[1:]:
            formula = formula & clause

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "Branching formula should be satisfiable"
        assert (
            elapsed < 5000.0
        ), f"Branching formula time {elapsed:.3f}ms should be < 5000ms"
        assert (
            result.total_nodes < 600
        ), f"Node count {result.total_nodes} should be controlled"


class TestInferencePerformanceBenchmarks:
    """Performance benchmarks for inference testing."""

    def test_simple_inference_performance(self):
        """Simple inferences should be very fast."""
        inference = parse_inference("p |- p")

        times = []
        for _ in range(10):
            start = time.time()
            result = check_inference(inference)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert result.valid, "Simple inference should be valid"
        assert avg_time < 1.0, f"Average time {avg_time:.3f}ms should be < 1ms"

    def test_modus_ponens_performance(self):
        """Modus ponens should be solved very efficiently."""
        inference = parse_inference("p, p -> q |- q")

        times = []
        for _ in range(10):
            start = time.time()
            result = check_inference(inference)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert result.valid, "Modus ponens should be valid"
        assert avg_time < 2.0, f"Average time {avg_time:.3f}ms should be < 2ms"

    def test_complex_inference_performance(self):
        """Complex inferences should still be reasonably fast."""
        # Chain of reasoning
        inference = parse_inference("p -> q, q -> r, r -> s, p |- s")

        start = time.time()
        result = check_inference(inference)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.valid, "Complex inference should be valid"
        assert (
            elapsed < 100.0
        ), f"Complex inference time {elapsed:.3f}ms should be < 100ms"

    def test_invalid_inference_performance(self):
        """Invalid inferences should be detected quickly with countermodels."""
        inference = parse_inference("p |- q")

        times = []
        for _ in range(10):
            start = time.time()
            result = check_inference(inference)
            end = time.time()
            times.append((end - start) * 1000)

        avg_time = statistics.mean(times)

        assert not result.valid, "Inference should be invalid"
        assert len(result.countermodels) > 0, "Should provide countermodels"
        assert avg_time < 2.0, f"Average time {avg_time:.3f}ms should be < 2ms"


class TestOptimizationEffectiveness:
    """Test that specific optimizations are working."""

    def test_alpha_beta_prioritization_effectiveness(self):
        """Alpha rules should be processed before beta rules."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Formula with both alpha and beta: ~(p ∧ q) ∧ (r ∨ p)
        # Negation should be processed first (alpha), then disjunction (beta)
        formula = ~(p & q) & (r | p)

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "Mixed formula should be satisfiable"
        assert (
            elapsed < 50.0
        ), f"Alpha/beta prioritization time {elapsed:.3f}ms should be < 50ms"

        # Should have processed efficiently (low node count indicates good prioritization)
        assert (
            result.total_nodes < 50
        ), f"Node count {result.total_nodes} should be low with prioritization"

    def test_early_termination_effectiveness(self):
        """Early termination should stop at first satisfying model."""
        p = Formula.atom("p")

        # Simple satisfiable formula that could have multiple models
        formula = p | ~p  # Tautology - satisfiable immediately

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "Tautology should be satisfiable"
        assert elapsed < 5.0, f"Early termination time {elapsed:.3f}ms should be < 5ms"

    def test_contradiction_detection_effectiveness(self):
        """O(1) contradiction detection should be very fast."""
        atoms = [Formula.atom(f"p{i}") for i in range(20)]

        # Create formula with contradiction: p1 ∧ p2 ∧ ... ∧ p20 ∧ ¬p10
        formula = atoms[0]
        for atom in atoms[1:]:
            formula = formula & atom

        # Add contradiction
        formula = formula & ~atoms[10]

        start = time.time()
        result = solve(formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert not result.satisfiable, "Contradiction should be unsatisfiable"
        assert (
            elapsed < 50.0
        ), f"Fast contradiction detection time {elapsed:.3f}ms should be < 50ms"

    def test_subsumption_elimination_effectiveness(self):
        """Subsumption should eliminate redundant formulas."""
        p, q, r = Formula.atoms("p", "q", "r")

        # p ∨ (p ∧ q ∧ r) - p subsumes the conjunction
        subsuming_formula = p | (p & q & r)

        start = time.time()
        result = solve(subsuming_formula, t)
        end = time.time()

        elapsed = (end - start) * 1000

        assert result.satisfiable, "Subsuming formula should be satisfiable"
        assert (
            elapsed < 50.0
        ), f"Subsumption elimination time {elapsed:.3f}ms should be < 50ms"

        # Should recognize that p alone satisfies the formula
        found_simple_model = False
        for model in result.models:
            p_val = model.valuations.get("p")
            if str(p_val) == "t":  # True value
                found_simple_model = True
                break

        assert found_simple_model, "Should find model with subsumption optimization"


class TestMemoryEfficiency:
    """Test memory usage and efficiency."""

    def test_node_count_efficiency(self):
        """Node count should not explode with complex formulas."""
        # Create moderately complex formula
        atoms = [Formula.atom(f"p{i}") for i in range(8)]

        # Build balanced tree: ((p1 ∨ p2) ∧ (p3 ∨ p4)) ∨ ((p5 ∨ p6) ∧ (p7 ∨ p8))
        left_part = (atoms[0] | atoms[1]) & (atoms[2] | atoms[3])
        right_part = (atoms[4] | atoms[5]) & (atoms[6] | atoms[7])
        formula = left_part | right_part

        result = solve(formula, t)

        assert result.satisfiable, "Complex formula should be satisfiable"
        assert (
            result.total_nodes < 100
        ), f"Node count {result.total_nodes} should be efficient"
        assert (
            result.open_branches + result.closed_branches < 20
        ), "Branch count should be reasonable"

    def test_model_extraction_efficiency(self):
        """Model extraction should not be memory-intensive."""
        # Formula with multiple models
        p, q, r = Formula.atoms("p", "q", "r")
        formula = (p | q) & (q | r)

        result = solve(formula, t)

        assert result.satisfiable, "Formula should be satisfiable"
        assert len(result.models) > 0, "Should extract models"
        assert len(result.models) < 20, "Should not extract excessive models"

        # Each model should be compact
        for model in result.models:
            assert len(model.valuations) <= 3, "Each model should be compact"
            assert (
                len(model.constants) == 0
            ), "No constants needed for propositional logic"


class TestRegressionPrevention:
    """Tests to prevent performance regressions."""

    def test_baseline_performance_maintained(self):
        """Ensure baseline performance benchmarks are maintained."""
        test_cases = [
            ("simple_atom", Formula.atom("p"), 0.5),
            ("conjunction", Formula.atom("p") & Formula.atom("q"), 1.0),
            ("disjunction", Formula.atom("p") | Formula.atom("q"), 1.5),
            ("negation", ~Formula.atom("p"), 0.5),
            ("implication", Formula.atom("p").implies(Formula.atom("q")), 1.0),
            ("contradiction", Formula.atom("p") & ~Formula.atom("p"), 0.5),
        ]

        for name, formula, max_time_ms in test_cases:
            start = time.time()
            solve(formula, t)  # We don't need the result
            end = time.time()

            elapsed = (end - start) * 1000

            assert (
                elapsed < max_time_ms
            ), f"{name} regression: {elapsed:.3f}ms > {max_time_ms}ms"

    def test_optimization_flags_working(self):
        """Verify that optimization settings are active."""
        p, q = Formula.atoms("p", "q")
        formula = (p & q) | (~p & ~q)

        result = solve(formula, t)

        # With optimizations, should be reasonably efficient
        assert result.total_nodes < 50, "Optimization should limit node explosion"
        assert result.satisfiable, "Formula should be satisfiable"

        # Should find multiple models efficiently
        assert len(result.models) >= 1, "Should find models with optimization"


if __name__ == "__main__":
    # Run with strict timing requirements
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # Stop on first failure
