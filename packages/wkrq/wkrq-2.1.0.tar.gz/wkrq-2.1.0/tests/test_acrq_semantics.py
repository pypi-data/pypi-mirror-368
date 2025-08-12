"""Tests for ACrQ semantic evaluator."""

import pytest

from wkrq.acrq_semantics import ACrQEvaluator, ACrQInterpretation, evaluate_acrq
from wkrq.formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Constant,
    PredicateFormula,
    PropositionalAtom,
)
from wkrq.semantics import FALSE, TRUE, UNDEFINED


class TestACrQInterpretation:
    """Test ACrQ interpretation management."""

    def test_bilateral_value_setting(self):
        """Test setting and getting bilateral values."""
        interp = ACrQInterpretation()

        # Set bilateral value
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)

        # Get the value
        btv = interp.get_bilateral("Human", ("alice",))
        assert btv.positive == TRUE
        assert btv.negative == FALSE
        assert btv.is_determinate()

    def test_bilateral_consistency_check(self):
        """Test that bilateral inconsistency is rejected."""
        interp = ACrQInterpretation()

        # Try to set both R and R* to true (inconsistent)
        with pytest.raises(ValueError) as exc_info:
            interp.set_bilateral("Human", ("alice",), TRUE, TRUE)
        assert "inconsistency" in str(exc_info.value)

    def test_knowledge_gap(self):
        """Test knowledge gap representation."""
        interp = ACrQInterpretation()

        # Set a gap (no information)
        interp.set_bilateral("Human", ("charlie",), FALSE, FALSE)

        btv = interp.get_bilateral("Human", ("charlie",))
        assert btv.is_gap()

    def test_default_gap(self):
        """Test that unknown predicates default to gap."""
        interp = ACrQInterpretation()

        # Get value for unknown predicate
        btv = interp.get_bilateral("Unknown", ("x",))
        assert btv.positive == FALSE
        assert btv.negative == FALSE
        assert btv.is_gap()

    def test_domain_tracking(self):
        """Test that domain tracks individuals."""
        interp = ACrQInterpretation()

        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)
        interp.set_bilateral("Robot", ("bob", "charlie"), FALSE, TRUE)

        assert interp.domain == {"alice", "bob", "charlie"}


class TestACrQEvaluator:
    """Test ACrQ formula evaluation."""

    def test_bilateral_predicate_evaluation(self):
        """Test evaluation of bilateral predicates."""
        interp = ACrQInterpretation()
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)

        evaluator = ACrQEvaluator(interp)

        # Test positive predicate
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        assert evaluator.evaluate(human) == TRUE

        # Test negative predicate
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )
        assert evaluator.evaluate(human_star) == FALSE

    def test_standard_predicate_evaluation(self):
        """Test evaluation of standard predicates."""
        interp = ACrQInterpretation()
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)

        evaluator = ACrQEvaluator(interp)

        # Standard predicate
        human = PredicateFormula("Human", [Constant("alice")])
        assert evaluator.evaluate(human) == TRUE

        # Star predicate
        human_star = PredicateFormula("Human*", [Constant("alice")])
        assert evaluator.evaluate(human_star) == FALSE

    def test_knowledge_gap_evaluation(self):
        """Test evaluation with knowledge gaps."""
        interp = ACrQInterpretation()
        interp.set_bilateral("Human", ("charlie",), FALSE, FALSE)  # Gap

        evaluator = ACrQEvaluator(interp)

        # Both should evaluate to FALSE (no evidence)
        human = BilateralPredicateFormula(
            "Human", [Constant("charlie")], is_negative=False
        )
        assert evaluator.evaluate(human) == FALSE

        human_star = BilateralPredicateFormula(
            "Human", [Constant("charlie")], is_negative=True
        )
        assert evaluator.evaluate(human_star) == FALSE

    def test_propositional_evaluation(self):
        """Test evaluation of propositional atoms."""
        interp = ACrQInterpretation()
        interp.set_propositional("p", TRUE)
        interp.set_propositional("q", FALSE)

        evaluator = ACrQEvaluator(interp)

        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")  # Unknown

        assert evaluator.evaluate(p) == TRUE
        assert evaluator.evaluate(q) == FALSE
        assert evaluator.evaluate(r) == UNDEFINED

    def test_negation_evaluation(self):
        """Test negation under weak Kleene semantics."""
        interp = ACrQInterpretation()
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)

        evaluator = ACrQEvaluator(interp)

        # ¬Human(alice) where Human(alice) is true
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        neg_human = CompoundFormula("~", [human])

        assert evaluator.evaluate(neg_human) == FALSE

        # Negation of undefined
        unknown = PropositionalAtom("unknown")
        neg_unknown = CompoundFormula("~", [unknown])

        assert evaluator.evaluate(neg_unknown) == UNDEFINED

    def test_conjunction_weak_kleene(self):
        """Test conjunction under weak Kleene semantics."""
        interp = ACrQInterpretation()
        interp.set_propositional("p", TRUE)
        interp.set_propositional("q", FALSE)
        # r is undefined

        evaluator = ACrQEvaluator(interp)

        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")

        # t ∧ t = t
        conj1 = CompoundFormula("&", [p, p])
        assert evaluator.evaluate(conj1) == TRUE

        # t ∧ f = f
        conj2 = CompoundFormula("&", [p, q])
        assert evaluator.evaluate(conj2) == FALSE

        # t ∧ U = U (weak Kleene)
        conj3 = CompoundFormula("&", [p, r])
        assert evaluator.evaluate(conj3) == UNDEFINED

        # f ∧ U = U (weak Kleene)
        conj4 = CompoundFormula("&", [q, r])
        assert evaluator.evaluate(conj4) == UNDEFINED

    def test_disjunction_weak_kleene(self):
        """Test disjunction under weak Kleene semantics."""
        interp = ACrQInterpretation()
        interp.set_propositional("p", TRUE)
        interp.set_propositional("q", FALSE)

        evaluator = ACrQEvaluator(interp)

        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")  # Undefined

        # t ∨ f = t
        disj1 = CompoundFormula("|", [p, q])
        assert evaluator.evaluate(disj1) == TRUE

        # f ∨ f = f
        disj2 = CompoundFormula("|", [q, q])
        assert evaluator.evaluate(disj2) == FALSE

        # t ∨ U = U (weak Kleene)
        disj3 = CompoundFormula("|", [p, r])
        assert evaluator.evaluate(disj3) == UNDEFINED

        # f ∨ U = U (weak Kleene)
        disj4 = CompoundFormula("|", [q, r])
        assert evaluator.evaluate(disj4) == UNDEFINED

    def test_implication_weak_kleene(self):
        """Test implication under weak Kleene semantics."""
        interp = ACrQInterpretation()
        interp.set_propositional("p", TRUE)
        interp.set_propositional("q", FALSE)

        evaluator = ACrQEvaluator(interp)

        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")  # Undefined

        # t → t = t
        impl1 = CompoundFormula("->", [p, p])
        assert evaluator.evaluate(impl1) == TRUE

        # t → f = f
        impl2 = CompoundFormula("->", [p, q])
        assert evaluator.evaluate(impl2) == FALSE

        # f → X = t (for any X)
        impl3 = CompoundFormula("->", [q, p])
        assert evaluator.evaluate(impl3) == TRUE

        # t → U = U (weak Kleene)
        impl4 = CompoundFormula("->", [p, r])
        assert evaluator.evaluate(impl4) == UNDEFINED

        # U → t = U (weak Kleene)
        impl5 = CompoundFormula("->", [r, p])
        assert evaluator.evaluate(impl5) == UNDEFINED

    def test_bilateral_contradiction_handling(self):
        """Test handling of bilateral contradictions (gluts)."""
        interp = ACrQInterpretation()

        # Can't set both to true (would be inconsistent)
        # But we can have other combinations
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)  # Determinate true
        interp.set_bilateral("Human", ("bob",), FALSE, TRUE)  # Determinate false
        interp.set_bilateral("Human", ("charlie",), FALSE, FALSE)  # Gap

        evaluator = ACrQEvaluator(interp)

        # Test Alice (determinate true)
        alice_human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        alice_human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        assert evaluator.evaluate(alice_human) == TRUE
        assert evaluator.evaluate(alice_human_star) == FALSE

        # Test conjunction Human(alice) ∧ Human*(alice)
        conj = CompoundFormula("&", [alice_human, alice_human_star])
        assert evaluator.evaluate(conj) == FALSE  # t ∧ f = f

    def test_evaluate_acrq_function(self):
        """Test the convenience function."""
        interp = ACrQInterpretation()
        interp.set_bilateral("Robot", ("r2d2",), FALSE, TRUE)

        robot = BilateralPredicateFormula(
            "Robot", [Constant("r2d2")], is_negative=False
        )
        robot_star = BilateralPredicateFormula(
            "Robot", [Constant("r2d2")], is_negative=True
        )

        assert evaluate_acrq(robot, interp) == FALSE
        assert evaluate_acrq(robot_star, interp) == TRUE
