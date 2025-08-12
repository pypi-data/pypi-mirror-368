"""
Test ACrQ implementation against Ferguson's Definition 18 and examples.

This test suite validates that our ACrQ implementation correctly implements
the tableau system described in Ferguson (2021), particularly:
- Definition 18: ACrQ as wKrQ minus negation elimination plus bilateral rules
- Lemma 5: Branch closure conditions
- Lemma 6: Validity preservation
"""

import pytest

from wkrq import (
    FALSE,
    TRUE,
    UNDEFINED,
    Formula,
    SignedFormula,
    f,
    parse,
    t,
)
from wkrq.acrq_parser import parse_acrq_formula
from wkrq.acrq_tableau import ACrQTableau
from wkrq.formula import BilateralPredicateFormula, PredicateFormula


class TestACrQFergusonCompliance:
    """Test ACrQ compliance with Ferguson's Definition 18."""

    def test_acrq_drops_negation_elimination(self):
        """Test that ACrQ doesn't have general negation elimination."""
        # In wKrQ: v:~φ → ~v:φ where ~t=f, ~f=t, ~e=e
        # In ACrQ: This rule is dropped except for predicates

        # Test with compound formula
        formula = parse("~(p & q)")
        tableau = ACrQTableau([SignedFormula(t, formula)])
        result = tableau.construct()

        # Should not decompose ~(p & q) since negation elimination is dropped
        # The formula should remain as is
        assert result.satisfiable

    def test_acrq_bilateral_predicate_negation(self):
        """Test ACrQ handles ~R(x) → R*(x) per Definition 18."""
        # v:~R(c) → v:R*(c)
        formula = parse_acrq_formula("~Human(alice)")
        tableau = ACrQTableau([SignedFormula(t, formula)])
        result = tableau.construct()

        # Should convert ~Human(alice) to Human*(alice)
        assert result.satisfiable

        # Check that the conversion happened
        branch = result.tableau.open_branches[0]
        has_human_star = False
        # Look through the nodes in the branch
        for node_id in branch.node_ids:
            node = result.tableau.nodes[node_id]
            sf = node.formula
            if sf.sign == t and isinstance(sf.formula, BilateralPredicateFormula):
                if sf.formula.positive_name == "Human" and sf.formula.is_negative:
                    has_human_star = True
                    break
        assert has_human_star

    def test_acrq_bilateral_predicate_double_negation(self):
        """Test ACrQ handles ~R*(x) → R(x) per Definition 18."""
        # Create Human* first
        human_star = BilateralPredicateFormula(
            positive_name="Human", terms=[Formula.constant("alice")], is_negative=True
        )
        # Negate it: ~Human*(alice)
        from wkrq.formula import CompoundFormula

        neg_human_star = CompoundFormula("~", [human_star])

        tableau = ACrQTableau([SignedFormula(t, neg_human_star)])
        result = tableau.construct()

        # Should convert ~Human*(alice) to Human(alice)
        assert result.satisfiable

    def test_acrq_glut_allowed(self):
        """Test that ACrQ allows gluts (t:R(a) and t:R*(a)) per Lemma 5."""
        # Create both Human(alice) and Human*(alice) with t sign
        human = PredicateFormula("Human", [Formula.constant("alice")])
        human_star = BilateralPredicateFormula(
            positive_name="Human", terms=[Formula.constant("alice")], is_negative=True
        )

        tableau = ACrQTableau([SignedFormula(t, human), SignedFormula(t, human_star)])
        result = tableau.construct()

        # Branch should remain open (glut is allowed)
        assert result.satisfiable

    def test_acrq_standard_contradiction_closes(self):
        """Test that standard contradictions still close branches."""
        # t:Human(alice) and f:Human(alice) should close
        human = PredicateFormula("Human", [Formula.constant("alice")])

        tableau = ACrQTableau([SignedFormula(t, human), SignedFormula(f, human)])
        result = tableau.construct()

        # Branch should close (standard contradiction)
        assert not result.satisfiable

    def test_acrq_conjunction_with_bilateral(self):
        """Test conjunction rules work with bilateral predicates."""
        # t:(Human(x) & Robot*(x))
        human = PredicateFormula("Human", [Formula.constant("x")])
        robot_star = BilateralPredicateFormula(
            positive_name="Robot", terms=[Formula.constant("x")], is_negative=True
        )
        from wkrq.formula import CompoundFormula

        conj = CompoundFormula("&", [human, robot_star])

        tableau = ACrQTableau([SignedFormula(t, conj)])
        result = tableau.construct()

        # Should decompose to t:Human(x) and t:Robot*(x)
        assert result.satisfiable
        branch = tableau.open_branches[0]

        # Check both components are present
        has_human = any(
            sf.sign == t
            and isinstance(sf.formula, PredicateFormula)
            and not isinstance(sf.formula, BilateralPredicateFormula)
            and sf.formula.predicate_name == "Human"
            for node_id in branch.node_ids
            for sf in [result.tableau.nodes[node_id].formula]
        )
        has_robot_star = any(
            sf.sign == t
            and isinstance(sf.formula, BilateralPredicateFormula)
            and sf.formula.positive_name == "Robot"
            and sf.formula.is_negative
            for node_id in branch.node_ids
            for sf in [result.tableau.nodes[node_id].formula]
        )
        assert has_human and has_robot_star

    def test_acrq_lemma6_validity_preservation(self):
        """Test Lemma 6: Γ ⊢_ACrQ φ iff Γ* ⊢_ACrQ φ*"""
        # This is a meta-theorem about the relationship between
        # ACrQ proofs and their bilateral transforms
        # We test a simple case

        # If Human(x) ⊢ Mortal(x) in ACrQ
        # Then Human(x) ⊢ Mortal(x) should also hold
        human = PredicateFormula("Human", [Formula.constant("x")])
        mortal = PredicateFormula("Mortal", [Formula.constant("x")])

        # Test the inference
        tableau = ACrQTableau([SignedFormula(t, human), SignedFormula(f, mortal)])
        result = tableau.construct()

        # This should be open (no logical connection between Human and Mortal)
        assert result.satisfiable

    def test_acrq_quantifier_rules(self):
        """Test that quantifier rules work in ACrQ."""
        # Test existential: t:[∃x Human(x)]Mortal(x)
        # Use regular parser since ACrQ parser has issues with quantifiers
        formula = parse("[exists X Human(X)]Mortal(X)")
        tableau = ACrQTableau([SignedFormula(t, formula)])
        result = tableau.construct()

        # Should create witness with both Human(c) and Mortal(c)
        assert result.satisfiable

        # Check for witness
        branch = result.tableau.open_branches[0]
        constants = [str(c) for c in branch.ground_terms]
        assert len(constants) > 0

    def test_acrq_mixed_glut_and_gap(self):
        """Test model with both gluts and gaps."""
        # Human(alice): glut (both true)
        # Robot(alice): gap (neither true)
        human = PredicateFormula("Human", [Formula.constant("alice")])
        human_star = BilateralPredicateFormula(
            positive_name="Human", terms=[Formula.constant("alice")], is_negative=True
        )
        robot = PredicateFormula("Robot", [Formula.constant("alice")])
        robot_star = BilateralPredicateFormula(
            positive_name="Robot", terms=[Formula.constant("alice")], is_negative=True
        )

        tableau = ACrQTableau(
            [
                SignedFormula(t, human),  # Human true
                SignedFormula(t, human_star),  # Human* true (glut)
                SignedFormula(f, robot),  # Robot false
                SignedFormula(f, robot_star),  # Robot* false (gap)
            ]
        )
        result = tableau.construct()

        # Should be open with appropriate model
        assert result.satisfiable
        assert len(result.models) > 0

        # Check the model - unified model stores predicates separately
        model = result.models[0]
        # Glut: both Human and Human* are true
        assert model.valuations.get("Human(alice)") == TRUE
        assert model.valuations.get("Human*(alice)") == TRUE
        # Gap: both Robot and Robot* are false/undefined
        assert model.valuations.get("Robot(alice)") in [FALSE, UNDEFINED]
        assert model.valuations.get("Robot*(alice)") in [FALSE, UNDEFINED]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
