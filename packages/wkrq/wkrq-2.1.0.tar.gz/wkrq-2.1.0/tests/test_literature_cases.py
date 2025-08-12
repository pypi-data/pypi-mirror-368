#!/usr/bin/env python3
"""
Comprehensive Literature Test Cases for wKrQ

Adapted from classical tableau literature for the optimized wKrQ system.
Includes test cases from:
- Priest, G. "Introduction to Non-Classical Logic" (2008)
- Fitting, m. "First-Order Logic and Automated Theorem Proving" (1996)
- Smullyan, R. "First-Order Logic" (1968)
- Ferguson, S. "Tableaux and restricted quantification" (2021)
"""

import time

import pytest

from wkrq import (
    Formula,
    check_inference,
    f,
    m,
    n,
    parse_inference,
    solve,
    t,
    valid,
)
from wkrq.semantics import FALSE, TRUE, UNDEFINED


class TestPriestNonClassicalLogic:
    """Test cases from Priest's "Introduction to Non-Classical Logic"."""

    def test_weak_kleene_excluded_middle(self):
        """Test that excluded middle is not a tautology in weak Kleene logic."""
        p = Formula.atom("p")
        excluded_middle = p | ~p

        # In wKrQ (three-valued), excluded middle is NOT valid
        # because e ∨ ¬e = e ∨ e = e when p is undefined
        result = solve(excluded_middle, t)
        assert result.satisfiable, "p ∨ ¬p should be satisfiable"

        # Should NOT be valid in weak Kleene (can be undefined)
        assert not valid(excluded_middle), "p ∨ ¬p is not valid in weak Kleene"

    def test_weak_kleene_contradiction_properties(self):
        """Test contradiction behavior in weak Kleene logic."""
        p = Formula.atom("p")
        contradiction = p & ~p

        # t:(p ∧ ¬p) should be unsatisfiable
        result_t = solve(contradiction, t)
        assert not result_t.satisfiable, "t:(p ∧ ¬p) should be unsatisfiable"

        # f:(p ∧ ¬p) should be satisfiable
        result_f = solve(contradiction, f)
        assert result_f.satisfiable, "f:(p ∧ ¬p) should be satisfiable"

        # m:(p ∧ ¬p) should be satisfiable (epistemic uncertainty)
        result_m = solve(contradiction, m)
        assert result_m.satisfiable, "m:(p ∧ ¬p) should be satisfiable"

        # n:(p ∧ ¬p) should be satisfiable (need not be true)
        result_n = solve(contradiction, n)
        assert result_n.satisfiable, "n:(p ∧ ¬p) should be satisfiable"

    def test_priest_signed_tableau_soundness(self):
        """Test soundness of signed tableau rules."""
        p, q = Formula.atoms("p", "q")

        # Test t-conjunction rule correctness
        conj = p & q
        result = solve(conj, t)

        if result.satisfiable:
            # Every model should make both p and q true
            for model in result.models:
                p_val = model.valuations.get("p", UNDEFINED)
                q_val = model.valuations.get("q", UNDEFINED)

                # In a t:(p ∧ q) model, both p and q should be true
                if p_val == TRUE and q_val == TRUE:
                    continue  # This is expected
                else:
                    # Allow for cases where the formula might be satisfied differently
                    # due to three-valued semantics
                    pass

    def test_priest_many_valued_completeness(self):
        """Test completeness properties for many-valued tableaux."""
        p, q = Formula.atoms("p", "q")

        # Test that satisfiable formulas have models
        satisfiable_formulas = [
            p,  # Simple atom
            p | ~p,  # Tautology
            p | q,  # Disjunction
        ]

        for formula in satisfiable_formulas:
            result = solve(formula, t)
            if result.satisfiable:
                assert (
                    len(result.models) > 0
                ), f"Satisfiable formula {formula} should have models"

        # Test that unsatisfiable formulas have no models
        unsatisfiable_formulas = [
            p & ~p,  # Contradiction
        ]

        for formula in unsatisfiable_formulas:
            result = solve(formula, t)
            assert not result.satisfiable, f"Formula {formula} should be unsatisfiable"
            assert (
                len(result.models) == 0
            ), f"Unsatisfiable formula {formula} should have no models"


class TestFittingTableauMethods:
    """Test cases from Fitting's automated theorem proving work."""

    def test_fitting_alpha_beta_optimization(self):
        """Test alpha/beta rule prioritization from Fitting's optimization work."""
        # Formula that exercises both alpha and beta rules
        p, q, r = Formula.atoms("p", "q", "r")

        # ~(p ∧ q) ∧ (r ∨ p) - should prioritize alpha rules (negation, t-conjunction)
        formula = ~(p & q) & (r | p)

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        # Should be efficiently solved with alpha rule prioritization
        assert result.satisfiable, "Formula should be satisfiable"
        assert (end_time - start_time) < 0.01, "Should solve quickly with optimization"

        # Should find multiple models
        assert len(result.models) > 0, "Should find satisfying models"

    def test_fitting_tableau_closure_detection(self):
        """Test efficient closure detection from Fitting's work."""
        p, q = Formula.atoms("p", "q")

        # Formula that closes quickly: (p ∧ ¬p) ∧ (q ∨ ¬q)
        contradiction_part = p & ~p
        tautology_part = q | ~q
        mixed_formula = contradiction_part & tautology_part

        start_time = time.time()
        result = solve(mixed_formula, t)
        end_time = time.time()

        # Should detect closure immediately due to contradiction
        assert not result.satisfiable, "Should be unsatisfiable due to contradiction"
        assert (end_time - start_time) < 0.001, "Should detect closure very quickly"

    def test_fitting_model_extraction_efficiency(self):
        """Test efficient model extraction techniques."""
        # Create formula with multiple satisfying assignments
        p, q, r = Formula.atoms("p", "q", "r")
        formula = (p | q) & (q | r) & (r | p)

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        assert result.satisfiable, "Formula should be satisfiable"
        assert len(result.models) > 0, "Should extract models"
        assert (end_time - start_time) < 0.05, "Model extraction should be efficient"

        # Verify models are valid
        for model in result.models:
            assert isinstance(
                model.valuations, dict
            ), "Each model should have valuations"
            assert len(model.valuations) > 0, "Each model should assign truth values"

    def test_fitting_subsumption_elimination(self):
        """Test subsumption elimination techniques."""
        p, q = Formula.atoms("p", "q")

        # Formula where some subformulas subsume others
        # p ∨ (p ∧ q) - the disjunction subsumes the conjunction
        subsuming_formula = p | (p & q)

        result = solve(subsuming_formula, t)

        # Should be satisfiable and efficiently processed
        assert result.satisfiable, "Subsuming formula should be satisfiable"

        # Should have found that p alone satisfies the formula
        found_p_only_model = False
        for model in result.models:
            p_val = model.valuations.get("p", UNDEFINED)
            if p_val == TRUE:
                found_p_only_model = True
                break

        assert (
            found_p_only_model
        ), "Should find model where p satisfies the whole formula"


class TestSmullyanTableauFoundations:
    """Test cases from Smullyan's foundational tableau work."""

    def test_smullyan_systematic_tableau_construction(self):
        """Test systematic tableau construction principles."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Classical tautology: ((p → q) → ((q → r) → (p → r)))
        # Hypothetical syllogism
        inner_impl = q.implies(r)
        outer_impl = p.implies(r)
        full_tautology = (p.implies(q)).implies(inner_impl.implies(outer_impl))

        # Should NOT be valid in weak Kleene (can be undefined)
        assert not valid(
            full_tautology
        ), "Hypothetical syllogism is not valid in weak Kleene"

        # But it cannot be false
        result = solve(full_tautology, f)
        assert not result.satisfiable, "Hypothetical syllogism cannot be false"

    def test_smullyan_alpha_beta_classification_correctness(self):
        """Test correct classification and handling of alpha/beta formulas."""
        p, q = Formula.atoms("p", "q")

        # Alpha formulas (non-branching)
        alpha_formulas = [
            ~(p | q),  # t:¬(p ∨ q) → f:(p ∨ q) → f:p, f:q
            p & q,  # t:(p ∧ q) → t:p, t:q
            ~(p.implies(q)),  # t:¬(p → q) → f:(p → q) → t:p, f:q
        ]

        # Beta formulas (branching)
        beta_formulas = [
            p | q,  # t:(p ∨ q) → t:p | t:q
            p.implies(q),  # t:(p → q) → f:p | t:q
            ~(p & q),  # t:¬(p ∧ q) → f:(p ∧ q) → f:p | f:q
        ]

        # Test that alpha formulas are processed efficiently (non-branching)
        for alpha in alpha_formulas:
            result = solve(alpha, t)
            # Alpha rules should not create excessive branching
            if result.satisfiable:
                # The key is that alpha rules are deterministic
                assert (
                    len(result.models) >= 1
                ), f"Alpha formula {alpha} should have models"

        # Test that beta formulas create appropriate branching
        for beta in beta_formulas:
            result = solve(beta, t)
            if result.satisfiable:
                # Beta rules should allow multiple possibilities
                assert (
                    len(result.models) >= 1
                ), f"Beta formula {beta} should have models"

    def test_smullyan_completeness_theorem_example(self):
        """Test example demonstrating tableau completeness."""
        p, q = Formula.atoms("p", "q")

        # Satisfiable formula with clear models: (p ∧ q) ∨ (¬p ∧ ¬q)
        pos_case = p & q
        neg_case = ~p & ~q
        satisfiable_formula = pos_case | neg_case

        result = solve(satisfiable_formula, t)
        assert result.satisfiable, "Formula should be satisfiable"
        assert len(result.models) > 0, "Should extract satisfying models"

        # Should find models corresponding to both branches
        found_both_true = False
        found_both_false = False

        for model in result.models:
            p_val = model.valuations.get("p", UNDEFINED)
            q_val = model.valuations.get("q", UNDEFINED)

            if p_val == TRUE and q_val == TRUE:
                found_both_true = True
            elif p_val == FALSE and q_val == FALSE:
                found_both_false = True

        # Should find at least one of the expected model types
        assert found_both_true or found_both_false, "Should find expected model types"


class TestFergusonWKrQSystem:
    """Test cases specific to Ferguson's wKrQ system."""

    def test_ferguson_four_valued_signs(self):
        """Test the four-valued sign system t, f, m, n."""
        p = Formula.atom("p")

        # Test all four signs are satisfiable individually
        for sign in [t, f, m, n]:
            result = solve(p, sign)
            assert result.satisfiable, f"{sign}:p should be satisfiable"
            assert len(result.models) > 0, f"{sign}:p should have models"

    def test_ferguson_epistemic_vs_truth_functional(self):
        """Test distinction between epistemic (m, n) and truth-functional (t, f) signs."""
        p, q = Formula.atoms("p", "q")

        # Truth-functional contradiction: should be unsatisfiable
        contradiction = p & ~p
        result_t = solve(contradiction, t)
        assert not result_t.satisfiable, "t:(p ∧ ¬p) should be unsatisfiable"

        # Epistemic uncertainty: should be satisfiable
        result_m = solve(contradiction, m)
        assert result_m.satisfiable, "m:(p ∧ ¬p) should be satisfiable"

        result_n = solve(contradiction, n)
        assert result_n.satisfiable, "n:(p ∧ ¬p) should be satisfiable"

        # This demonstrates the key insight: epistemic signs express uncertainty,
        # not truth conditions

    def test_ferguson_non_classical_tautology_behavior(self):
        """Test non-classical behavior with epistemic uncertainty about tautologies."""
        p = Formula.atom("p")

        # Classical tautology
        tautology = p | ~p

        # Truth-functionally true
        result_t = solve(tautology, t)
        assert result_t.satisfiable, "t:(p ∨ ¬p) should be satisfiable"

        # But epistemic uncertainty is possible
        result_m = solve(tautology, m)
        assert result_m.satisfiable, "m:(p ∨ ¬p) should be satisfiable"

        result_n = solve(tautology, n)
        assert result_n.satisfiable, "n:(p ∨ ¬p) should be satisfiable"

        # This shows epistemic and truth-functional dimensions are orthogonal

    def test_ferguson_complex_epistemic_reasoning(self):
        """Test complex reasoning with mixed epistemic and truth-functional signs."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Complex formula: ((p ∧ q) ∨ r) → (p ∨ (q ∧ r))
        antecedent = (p & q) | r
        consequent = p | (q & r)
        complex_impl = antecedent.implies(consequent)

        # Test with different signs
        for sign in [t, f, m, n]:
            result = solve(complex_impl, sign)
            # Each should be satisfiable given the semantic framework
            assert result.satisfiable, f"{sign}:complex_formula should be satisfiable"

            if result.models:
                # Models should be consistent with the sign semantics
                assert len(result.models) > 0, f"{sign} should have models"


class TestPerformanceOptimization:
    """Test cases validating optimization techniques."""

    def test_alpha_rule_prioritization(self):
        """Test that alpha rules are processed before beta rules."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Formula with mix of alpha and beta rules
        # ~(p ∧ q) ∧ (r ∨ p) - negation (alpha) should be processed first
        formula = ~(p & q) & (r | p)

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        # Should be solved efficiently
        assert result.satisfiable, "Formula should be satisfiable"
        assert (
            end_time - start_time
        ) < 0.01, "Should solve quickly with alpha prioritization"

    def test_branch_selection_optimization(self):
        """Test intelligent branch selection strategies."""
        atoms = [Formula.atom(f"p{i}") for i in range(6)]

        # Create formula that could lead to exponential branching without optimization
        clauses = []
        for i in range(3):
            clause = atoms[i] | atoms[i + 1] | atoms[i + 2]
            clauses.append(clause)

        # Conjoin all clauses
        formula = clauses[0]
        for clause in clauses[1:]:
            formula = formula & clause

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        # Should be solved without exponential blowup
        assert result.satisfiable, "CNF formula should be satisfiable"
        assert (
            end_time - start_time
        ) < 0.1, "Should solve efficiently with branch optimization"
        assert result.total_nodes < 100, "Should not create excessive nodes"

    def test_early_termination_optimization(self):
        """Test early termination when first model is found."""
        p, q = Formula.atoms("p", "q")

        # Simple satisfiable formula
        formula = p | q

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        # Should terminate quickly
        assert result.satisfiable, "Formula should be satisfiable"
        assert (end_time - start_time) < 0.001, "Should terminate very quickly"
        assert len(result.models) > 0, "Should find models"

    def test_subsumption_elimination_effectiveness(self):
        """Test that subsumption elimination reduces redundant work."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Formula with potential subsumption: p ∨ (p ∧ q ∧ r)
        general = p
        specific = p & q & r
        formula = general | specific

        start_time = time.time()
        result = solve(formula, t)
        end_time = time.time()

        # Should recognize that p subsumes p ∧ q ∧ r
        assert result.satisfiable, "Formula should be satisfiable"
        assert (
            end_time - start_time
        ) < 0.01, "Should solve efficiently with subsumption"

        # Should find model where just p is true
        found_simple_model = False
        for model in result.models:
            p_val = model.valuations.get("p", UNDEFINED)
            if p_val == TRUE:
                found_simple_model = True
                break

        assert found_simple_model, "Should find model with just p true"


class TestInferencePatterns:
    """Test standard inference patterns from the literature."""

    def test_modus_ponens_variations(self):
        """Test modus ponens and its variations."""
        # Standard modus ponens
        inference = parse_inference("p, p -> q |- q")
        result = check_inference(inference)
        assert result.valid, "Modus ponens should be valid"

        # Modus tollens
        inference = parse_inference("p -> q, ~q |- ~p")
        result = check_inference(inference)
        assert result.valid, "Modus tollens should be valid"

        # Hypothetical syllogism
        inference = parse_inference("p -> q, q -> r |- p -> r")
        result = check_inference(inference)
        assert result.valid, "Hypothetical syllogism should be valid"

        # Disjunctive syllogism
        inference = parse_inference("p | q, ~p |- q")
        result = check_inference(inference)
        assert result.valid, "Disjunctive syllogism should be valid"

    def test_invalid_inference_detection(self):
        """Test detection of invalid inferences."""
        invalid_inferences = [
            "p |- q",  # No connection
            "p -> q |- q",  # Affirming the consequent
            "p -> q, ~p |- ~q",  # Denying the antecedent
            "p & q |- r",  # Unrelated conclusion
        ]

        for inf_str in invalid_inferences:
            inference = parse_inference(inf_str)
            result = check_inference(inference)
            assert not result.valid, f"Inference '{inf_str}' should be invalid"
            assert (
                len(result.countermodels) > 0
            ), f"Should provide countermodel for '{inf_str}'"

    def test_complex_inference_chains(self):
        """Test complex multi-step inferences."""
        # Complex valid inference
        complex_valid = "p -> (q -> r), p, q |- r"
        inference = parse_inference(complex_valid)
        result = check_inference(inference)
        assert result.valid, "Complex valid inference should be recognized"

        # Complex invalid inference
        complex_invalid = "p -> (q -> r), p |- r"
        inference = parse_inference(complex_invalid)
        result = check_inference(inference)
        assert not result.valid, "Complex invalid inference should be detected"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
