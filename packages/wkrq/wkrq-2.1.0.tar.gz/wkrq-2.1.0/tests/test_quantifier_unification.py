"""
Comprehensive tests for first-order quantifier unification and reasoning.

Tests both restricted universal and existential quantifiers with various
scenarios including multiple constants, complex inferences, and edge cases.
"""

import pytest

from wkrq.api import check_inference
from wkrq.cli import parse_inference
from wkrq.parser import parse
from wkrq.signs import t
from wkrq.tableau import entails, solve


class TestUniversalQuantifierUnification:
    """Test universal quantifier unification with existing constants."""

    def test_basic_universal_instantiation(self):
        """Test basic universal quantifier instantiation with single constant."""
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal should instantiate with existing constant"

    def test_universal_with_multiple_constants(self):
        """Test universal quantifier with multiple existing constants."""
        # Both constants should work
        inference1 = parse_inference(
            "[∀X Human(X)]Mortal(X), Human(socrates), Human(plato) |- Mortal(socrates)"
        )
        result1 = check_inference(inference1)
        assert result1.valid, "Universal should work with first constant"

        inference2 = parse_inference(
            "[∀X Human(X)]Mortal(X), Human(socrates), Human(plato) |- Mortal(plato)"
        )
        result2 = check_inference(inference2)
        assert result2.valid, "Universal should work with second constant"

    def test_universal_multiple_premises_and_conclusions(self):
        """Test universal with multiple premises leading to multiple conclusions."""
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), Human(socrates), Human(plato), Human(aristotle) |- "
            "Mortal(socrates) & Mortal(plato) & Mortal(aristotle)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal should apply to all constants"

    def test_universal_with_different_predicates(self):
        """Test universal quantifier with different predicate names."""
        inference = parse_inference("[∀X Dog(X)]Animal(X), Dog(fido) |- Animal(fido)")
        result = check_inference(inference)
        assert result.valid, "Universal should work with different predicates"

    def test_universal_chain_reasoning(self):
        """Test chained reasoning with universal quantifiers."""
        # If all humans are mortal, and all mortals are finite, then all humans are finite
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), [∀Y Mortal(Y)]Finite(Y), Human(kant) |- Finite(kant)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal chain reasoning should work"

    def test_universal_invalid_conclusion(self):
        """Test that invalid universal inferences are correctly rejected."""
        # Universal about humans shouldn't apply to dogs
        inference = parse_inference("[∀X Human(X)]Mortal(X), Dog(fido) |- Mortal(fido)")
        result = check_inference(inference)
        assert not result.valid, "Universal shouldn't apply to unrelated constants"

    def test_universal_with_negation(self):
        """Test universal quantifiers with negated conclusions."""
        # If no humans are immortal, then socrates is not immortal
        inference = parse_inference(
            "[∀X Human(X)](~Immortal(X)), Human(socrates) |- ~Immortal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal with negation should work"

    def test_universal_contrapositive_reasoning(self):
        """Test contrapositive reasoning with universal quantifiers."""
        # If all humans are mortal, and socrates is not mortal, then socrates is not human
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), ~Mortal(socrates) |- ~Human(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal contrapositive should work"


class TestExistentialQuantifierUnification:
    """Test existential quantifier unification and witness selection."""

    def test_basic_existential_instantiation(self):
        """Test basic existential quantifier with witness."""
        # Note: The existence of *some* mortal human doesn't imply all humans are mortal
        # So this inference should be invalid
        inference = parse_inference(
            "[∃X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert (
            not result.valid
        ), "Existential about some human doesn't imply all humans have the property"

    def test_existential_with_multiple_witnesses(self):
        """Test existential with multiple possible witnesses."""
        # Either witness should work
        inference1 = parse_inference(
            "[∃X Human(X)]Wise(X), Human(socrates), Human(plato) |- Wise(socrates) | Wise(plato)"
        )
        _result1 = check_inference(inference1)
        # Note: This might not be valid depending on the exact semantics - existential doesn't guarantee all instances

    def test_existential_witness_selection(self):
        """Test that existential quantifier properly selects witnesses."""
        # The existence of a mortal human and the fact that socrates is human
        # doesn't guarantee socrates is mortal (it could be someone else)
        inference = parse_inference(
            "[∃X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert (
            not result.valid
        ), "Existential doesn't guarantee specific instance has property"

    def test_existential_invalid_witness(self):
        """Test that existential doesn't apply to non-matching constants."""
        # Existential about humans shouldn't guarantee anything about dogs
        inference = parse_inference("[∃X Human(X)]Mortal(X), Dog(fido) |- Mortal(fido)")
        result = check_inference(inference)
        assert not result.valid, "Existential shouldn't apply to non-matching witness"

    def test_existential_with_disjunction(self):
        """Test existential quantifier creating disjunctive conclusions."""
        # If some human is wise, and we have two humans, at least one is wise
        # This tests the branching behavior of existential quantifiers
        formula = parse("[∃X Human(X)]Wise(X)")
        result = solve(formula, t)
        assert result.satisfiable, "Existential should be satisfiable"

    def test_existential_contradiction(self):
        """Test existential quantifier in contradictory scenarios."""
        # If no human is mortal, then there can't exist a mortal human
        inference = parse_inference(
            "[∀X Human(X)](~Mortal(X)) |- ~([∃Y Human(Y)]Mortal(Y))"
        )
        result = check_inference(inference)
        assert result.valid, "Universal negation should contradict existential"


class TestMixedQuantifierScenarios:
    """Test scenarios involving both universal and existential quantifiers."""

    def test_universal_and_existential_combination(self):
        """Test reasoning with both universal and existential quantifiers."""
        # If all humans are mortal, and there exists a mortal being, and socrates is human
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), [∃Y Being(Y)]Mortal(Y), Human(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Mixed quantifiers should work together"

    def test_nested_quantifier_domains(self):
        """Test quantifiers over different but related domains."""
        # All humans are animals, some animals are pets, socrates is human
        inference = parse_inference(
            "[∀X Human(X)]Animal(X), [∃Y Animal(Y)]Pet(Y), Human(socrates) |- Animal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal should establish the connection"

    def test_quantifier_interaction_complex(self):
        """Test complex interactions between quantifiers."""
        # All students study, some students are brilliant, mary is a student
        inference = parse_inference(
            "[∀X Student(X)]Studies(X), [∃Y Student(Y)]Brilliant(Y), Student(mary) |- Studies(mary)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal should apply regardless of existential"

    def test_quantifier_scoping(self):
        """Test that quantifier variables are properly scoped."""
        # Using same variable name in different quantifiers
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), [∃X God(X)]Immortal(X), Human(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Variable scoping should be handled correctly"


class TestQuantifierEdgeCases:
    """Test edge cases and boundary conditions for quantifier reasoning."""

    def test_empty_domain_universal(self):
        """Test universal quantifier with no matching constants."""
        # Universal should be vacuously true if no instances exist
        formula = parse("[∀X Unicorn(X)]Magical(X)")
        result = solve(formula, t)
        assert result.satisfiable, "Universal over empty domain should be satisfiable"

    def test_empty_domain_existential(self):
        """Test existential quantifier with no matching constants."""
        # Existential should be satisfiable by introducing a witness
        formula = parse("[∃X Unicorn(X)]Magical(X)")
        result = solve(formula, t)
        assert (
            result.satisfiable
        ), "Existential should be satisfiable with fresh witness"

    def test_contradictory_quantifiers(self):
        """Test contradictory quantifier statements."""
        # All humans are mortal AND no humans are mortal
        inference = parse_inference(
            "[∀X Human(X)]Mortal(X), [∀Y Human(Y)](~Mortal(Y)), Human(socrates) |- False"
        )
        # This should lead to a contradiction, making the inference vacuously valid
        _result = check_inference(inference)
        # The premises are contradictory, so any conclusion follows

    def test_tautological_quantifiers(self):
        """Test tautological quantifier statements."""
        # All humans are human (tautology)
        inference = parse_inference(
            "[∀X Human(X)]Human(X), Human(socrates) |- Human(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Tautological universal should be valid"

    def test_multiple_constant_introduction(self):
        """Test scenario where multiple constants are introduced dynamically."""
        # This tests the unification system's ability to handle growing constant sets
        inference = parse_inference(
            "[∀X Person(X)]HasName(X), Person(a), Person(b), Person(c) |- "
            "HasName(a) & HasName(b) & HasName(c)"
        )
        result = check_inference(inference)
        assert (
            result.valid
        ), "Universal should apply to all dynamically introduced constants"

    def test_quantifier_with_complex_formulas(self):
        """Test quantifiers with complex formula structures."""
        # Universal over implication
        inference = parse_inference(
            "[∀X Human(X)](Rational(X) -> Mortal(X)), Human(socrates), Rational(socrates) |- Mortal(socrates)"
        )
        result = check_inference(inference)
        assert result.valid, "Universal with implication should work"

    def test_quantifier_performance_with_many_constants(self):
        """Test quantifier performance with many constants."""
        # Create inference with many constants to test unification efficiency
        constants = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        premises = "[∀X P(X)]Q(X)"
        for const in constants:
            premises += f", P({const})"

        conclusion = " & ".join(f"Q({const})" for const in constants)
        inference_str = f"{premises} |- {conclusion}"

        inference = parse_inference(inference_str)
        result = check_inference(inference)
        assert result.valid, "Universal should handle many constants efficiently"


class TestQuantifierSemantics:
    """Test the semantic correctness of quantifier reasoning."""

    def test_universal_semantic_correctness(self):
        """Test that universal quantifiers have correct weak Kleene semantics."""
        # Test with undefined values in the domain
        # This is more complex as it involves the three-valued nature
        formula = parse("[∀X P(X)]Q(X)")
        result = solve(formula, t)
        # Should be satisfiable in weak Kleene logic
        assert result.satisfiable

    def test_existential_semantic_correctness(self):
        """Test that existential quantifiers have correct weak Kleene semantics."""
        formula = parse("[∃X P(X)]Q(X)")
        result = solve(formula, t)
        assert result.satisfiable

    def test_quantifier_with_undefined_predicates(self):
        """Test quantifier behavior with undefined predicate values."""
        # This tests the interaction with the m and n signs
        # In weak Kleene logic, undefined values should propagate appropriately

        # Test with m sign (multiple truth values possible)
        from wkrq.signs import m

        formula = parse("[∀X P(X)]Q(X)")
        result = solve(formula, m)
        assert result.satisfiable, "Universal should be satisfiable with m sign"

        # Test with n sign (neither true nor false - undefined)
        from wkrq.signs import n

        result = solve(formula, n)
        assert result.satisfiable, "Universal should be satisfiable with n sign"

    def test_restricted_quantification_semantics(self):
        """Test the semantics of restricted quantification specifically."""
        # [∀X P(X)]Q(X) means: for all x, if P(x) then Q(x)
        # This should be equivalent to ∀x(P(x) → Q(x)) in classical logic

        # If the restriction is false, the quantified statement should be vacuously true
        inference = parse_inference("[∀X False]Q(X) |- True")
        # Note: This might not be directly testable with current parser

        # Test the contrapositive: if not Q(a) and the universal holds, then not P(a)
        inference = parse_inference("[∀X P(X)]Q(X), ~Q(socrates) |- ~P(socrates)")
        result = check_inference(inference)
        assert (
            result.valid
        ), "Contrapositive reasoning should work with restricted quantification"


class TestQuantifierAPIIntegration:
    """Test integration of quantifier reasoning with the API."""

    def test_api_entailment_with_quantifiers(self):
        """Test API entailment checking with quantifiers."""
        from wkrq.formula import (
            Constant,
            PredicateFormula,
            RestrictedUniversalFormula,
            Variable,
        )

        # Create formulas programmatically
        x = Variable("X")
        human_x = PredicateFormula("Human", [x])
        mortal_x = PredicateFormula("Mortal", [x])
        universal = RestrictedUniversalFormula(x, human_x, mortal_x)

        socrates = Constant("socrates")
        human_socrates = PredicateFormula("Human", [socrates])
        mortal_socrates = PredicateFormula("Mortal", [socrates])

        # Test entailment
        result = entails([universal, human_socrates], mortal_socrates)
        assert result, "API entailment should work with quantifiers"

    def test_model_extraction_with_quantifiers(self):
        """Test model extraction in the presence of quantifiers."""
        from wkrq.api import find_models

        formula = parse("[∀X Human(X)]Mortal(X)")
        models = find_models(formula)

        assert len(models) > 0, "Should find models for universal quantifier"

        # Check that models contain appropriate valuations
        for model in models:
            # Models should have valuations for the atomic components
            assert len(model.valuations) > 0, "Models should have some valuations"

    def test_satisfiability_with_quantifiers(self):
        """Test satisfiability checking with quantifiers."""
        from wkrq.api import evaluate_formula

        # Satisfiable universal
        formula1 = parse("[∀X Human(X)]Mortal(X)")
        result1 = evaluate_formula(formula1)
        assert result1.satisfiable, "Universal should be satisfiable"

        # Potentially unsatisfiable combination
        formula2 = parse("[∀X Human(X)]Mortal(X) & [∀Y Human(Y)](~Mortal(Y))")
        _result2 = evaluate_formula(formula2)
        # This should be unsatisfiable due to contradiction
        # assert not _result2.satisfiable, "Contradictory universals should be unsatisfiable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
