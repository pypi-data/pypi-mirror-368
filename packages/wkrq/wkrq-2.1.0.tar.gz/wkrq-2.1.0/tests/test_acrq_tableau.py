"""Tests for ACrQ-specific tableau functionality."""

from wkrq.acrq_parser import SyntaxMode, parse_acrq_formula
from wkrq.acrq_tableau import ACrQTableau, Model
from wkrq.formula import (
    BilateralPredicateFormula,
    Conjunction,
    Constant,
    Negation,
    PredicateFormula,
)
from wkrq.parser import parse
from wkrq.semantics import FALSE, TRUE, UNDEFINED
from wkrq.signs import SignedFormula, f, m, n, t


class TestACrQTableau:
    """Test ACrQ-specific tableau functionality."""

    def test_bilateral_predicate_initialization(self):
        """Test that ACrQTableau correctly initializes bilateral predicates."""
        # Create formulas with bilateral predicates
        human = BilateralPredicateFormula("Human", [Constant("alice")])
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        initial = [SignedFormula(t, human), SignedFormula(f, human_star)]
        tableau = ACrQTableau(initial)

        # Check bilateral pairs are identified
        assert "Human" in tableau.bilateral_pairs
        assert tableau.bilateral_pairs["Human"] == "Human*"
        assert "Human*" in tableau.bilateral_pairs
        assert tableau.bilateral_pairs["Human*"] == "Human"

    def test_glut_allowed(self):
        """Test that t:R(a) and t:R*(a) can coexist (glut)."""
        # Create both t:Human(alice) and t:Human*(alice)
        human_pos = PredicateFormula("Human", [Constant("alice")])
        human_neg = PredicateFormula("Human*", [Constant("alice")])

        initial = [SignedFormula(t, human_pos), SignedFormula(t, human_neg)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be satisfiable (glut allowed)
        assert result.satisfiable
        assert len(result.models) > 0

        # Check model contains both
        model = result.models[0]
        assert model.valuations["Human(alice)"] == TRUE
        assert model.valuations["Human*(alice)"] == TRUE

    def test_standard_contradiction_closes(self):
        """Test that standard contradictions still close branches."""
        # t:Human(alice) and f:Human(alice) should close
        human = PredicateFormula("Human", [Constant("alice")])

        initial = [SignedFormula(t, human), SignedFormula(f, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be unsatisfiable
        assert not result.satisfiable

    def test_t_r_rule(self):
        """Test that t:R works correctly in tableau."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        # Test that t:R is satisfiable
        initial = [SignedFormula(t, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that model has Human(alice) = true
        assert len(result.models) > 0
        model = result.models[0]
        assert "Human(alice)" in model.valuations
        assert model.valuations["Human(alice)"] == TRUE

    def test_t_r_star_rule(self):
        """Test that t:R* works correctly in tableau."""
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        # Test that t:R* is satisfiable
        initial = [SignedFormula(t, human_star)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that model has Human*(alice) = true
        assert len(result.models) > 0
        model = result.models[0]
        assert "Human*(alice)" in model.valuations
        assert model.valuations["Human*(alice)"] == TRUE

    def test_f_r_rule(self):
        """Test that f:R works correctly in tableau."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        # Test that f:R is satisfiable
        initial = [SignedFormula(f, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that model has Human(alice) = false
        assert len(result.models) > 0
        model = result.models[0]
        assert "Human(alice)" in model.valuations
        assert model.valuations["Human(alice)"] == FALSE

    def test_m_r_rule(self):
        """Test that m:R works correctly (can be either true or false)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        # Test that m:R is satisfiable
        initial = [SignedFormula(m, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that models exist with different values
        assert len(result.models) > 0
        # At least one model should have Human(alice) assigned
        values = [model.valuations.get("Human(alice)") for model in result.models]
        assert any(v in [TRUE, FALSE] for v in values)

    def test_n_r_rule(self):
        """Test that n:R works correctly (can be false or undefined)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        # Test that n:R is satisfiable
        initial = [SignedFormula(n, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that models exist with appropriate values
        assert len(result.models) > 0
        # At least one model should have Human(alice) as false or undefined
        values = [model.valuations.get("Human(alice)") for model in result.models]
        assert any(v in [FALSE, UNDEFINED] for v in values)

    def test_bilateral_negation_rule(self):
        """Test ~R → R* transformation works correctly."""
        # Test ~R → R*
        neg_human = parse_acrq_formula("~Human(alice)", SyntaxMode.TRANSPARENT)
        initial = [SignedFormula(t, neg_human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Check that model has Human*(alice) = true
        assert len(result.models) > 0
        model = result.models[0]
        # The negation should be converted to Human*(alice)
        assert "Human*(alice)" in model.valuations
        assert model.valuations["Human*(alice)"] == TRUE

    def test_glut_with_compound_formulas(self):
        """Test gluts in context of compound formulas."""
        # (Human(alice) & Human*(alice)) should be satisfiable
        human_pos = PredicateFormula("Human", [Constant("alice")])
        human_neg = PredicateFormula("Human*", [Constant("alice")])
        conjunction = Conjunction(human_pos, human_neg)

        initial = [SignedFormula(t, conjunction)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be satisfiable (glut allowed)
        assert result.satisfiable

    def test_model_extraction_bilateral(self):
        """Test ACrQModel extracts bilateral valuations correctly."""
        # Create a scenario with bilateral predicates
        human_pos = PredicateFormula("Human", [Constant("alice")])
        human_neg = PredicateFormula("Human*", [Constant("alice")])
        nice_pos = PredicateFormula("Nice", [Constant("alice")])

        initial = [
            SignedFormula(t, human_pos),
            SignedFormula(f, human_neg),
            SignedFormula(t, nice_pos),
        ]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        model = result.models[0]
        assert isinstance(model, Model)

        # Check valuations - in unified model, bilateral predicates are stored separately
        assert "Human(alice)" in model.valuations
        assert model.valuations["Human(alice)"] == TRUE
        assert "Human*(alice)" in model.valuations
        assert model.valuations["Human*(alice)"] == FALSE

    def test_no_general_negation_elimination(self):
        """Test that ACrQ doesn't eliminate negation on compound formulas."""
        # ~(p & q) should not be decomposed
        formula = Negation(Conjunction(parse("p"), parse("q")))
        initial = [SignedFormula(t, formula)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be satisfiable with the negation intact
        assert result.satisfiable
        # The formula should remain as ~(p & q) in the model
        assert len(result.models) > 0

    def test_valid_bilateral_inference(self):
        """Test a valid inference with bilateral predicates."""
        # [∀X Human(X)]Nice(X), Human(alice) |- Nice(alice)
        formula1 = parse_acrq_formula("[∀X Human(X)]Nice(X)", SyntaxMode.TRANSPARENT)
        formula2 = parse_acrq_formula("Human(alice)", SyntaxMode.TRANSPARENT)
        conclusion = parse_acrq_formula("Nice(alice)", SyntaxMode.TRANSPARENT)

        # Test by negating: should be unsatisfiable
        initial = [
            SignedFormula(t, formula1),
            SignedFormula(t, formula2),
            SignedFormula(f, conclusion),
        ]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be unsatisfiable (valid inference)
        assert not result.satisfiable

    def test_bilateral_with_quantifiers(self):
        """Test bilateral predicates with quantifiers."""
        # [∃X Human(X)](~Human(X)) - someone is both human and not human
        # In transparent mode, ~Human(X) gets converted to Human*(X)
        formula = parse_acrq_formula("[∃X Human(X)](~Human(X))", SyntaxMode.TRANSPARENT)
        initial = [SignedFormula(t, formula)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be satisfiable in ACrQ (gluts allowed)
        assert result.satisfiable
