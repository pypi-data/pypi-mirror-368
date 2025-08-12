"""
Tests for first-order wKrQ features.

Tests restricted quantifiers and first-order reasoning.
"""

from wkrq import (
    Constant,
    Formula,
    PredicateFormula,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Variable,
    solve,
    t,
)
from wkrq.parser import parse


class TestFirstOrderFormulas:
    """Test first-order formula construction."""

    def test_variables_and_constants(self):
        """Test variable and constant creation."""
        x = Formula.variable("X")
        a = Formula.constant("a")

        assert str(x) == "X"
        assert str(a) == "a"
        assert isinstance(x, Variable)
        assert isinstance(a, Constant)

    def test_predicate_formulas(self):
        """Test predicate formula creation."""
        x = Formula.variable("X")
        a = Formula.constant("a")

        # Unary predicate
        p_x = Formula.predicate("P", [x])
        assert str(p_x) == "P(X)"

        # Binary predicate
        r_xa = Formula.predicate("R", [x, a])
        assert str(r_xa) == "R(X, a)"

        # Nullary predicate
        q = Formula.predicate("Q", [])
        assert str(q) == "Q"

    def test_restricted_quantifiers(self):
        """Test restricted quantifier creation."""
        x = Formula.variable("X")
        student_x = Formula.predicate("Student", [x])
        human_x = Formula.predicate("Human", [x])

        # Restricted existential
        exists = Formula.restricted_exists(x, student_x, human_x)
        assert str(exists) == "[∃X Student(X)]Human(X)"
        assert isinstance(exists, RestrictedExistentialFormula)

        # Restricted universal
        forall = Formula.restricted_forall(x, student_x, human_x)
        assert str(forall) == "[∀X Student(X)]Human(X)"
        assert isinstance(forall, RestrictedUniversalFormula)

    def test_complex_first_order_formulas(self):
        """Test complex first-order formula construction."""
        x = Formula.variable("X")
        a = Formula.constant("a")

        # Create predicates
        p_x = Formula.predicate("P", [x])
        q_x = Formula.predicate("Q", [x])
        p_a = Formula.predicate("P", [a])

        # Combine with propositional operators
        formula = p_a & Formula.restricted_exists(x, p_x, q_x)

        assert "P(a)" in str(formula)
        assert "[∃X P(X)]Q(X)" in str(formula)


class TestFirstOrderParsing:
    """Test parsing of first-order formulas."""

    def test_predicate_parsing(self):
        """Test predicate parsing."""
        # Simple predicate
        formula = parse("P(x)")
        assert isinstance(formula, PredicateFormula)
        assert str(formula) == "P(x)"

        # Multiple arguments
        formula = parse("R(x, y, z)")
        assert str(formula) == "R(x, y, z)"

    def test_complex_first_order_parsing(self):
        """Test complex first-order formula parsing."""
        # Predicate with propositional operators
        formula = parse("P(x) & Q(y)")
        assert "P(x)" in str(formula)
        assert "Q(y)" in str(formula)

        # Implication with predicates
        formula = parse("P(x) -> Q(x)")
        assert str(formula) == "P(x) -> Q(x)"


class TestFirstOrderSemantics:
    """Test first-order semantics and tableau reasoning."""

    def test_predicate_satisfiability(self):
        """Test basic predicate satisfiability."""
        x = Formula.constant("a")  # Use constant for now
        p_a = Formula.predicate("P", [x])

        result = solve(p_a, t)
        assert result.satisfiable
        assert len(result.models) > 0

    def test_predicate_contradiction(self):
        """Test predicate contradiction."""
        a = Formula.constant("a")
        p_a = Formula.predicate("P", [a])

        # P(a) & ~P(a) should be unsatisfiable
        contradiction = p_a & ~p_a
        result = solve(contradiction, t)
        assert not result.satisfiable

    def test_predicate_reasoning(self):
        """Test basic predicate reasoning patterns."""
        a = Formula.constant("a")
        p_a = Formula.predicate("P", [a])
        q_a = Formula.predicate("Q", [a])

        # Simple predicate implication
        formula = p_a.implies(q_a)
        result = solve(formula, t)
        assert (
            result.satisfiable
        )  # Should have models where P(a) is false or Q(a) is true


class TestRestrictedQuantifiers:
    """Test restricted quantifier reasoning (placeholder for future implementation)."""

    def test_restricted_quantifier_construction(self):
        """Test that restricted quantifiers can be constructed."""
        x = Formula.variable("X")
        student_x = Formula.predicate("Student", [x])
        human_x = Formula.predicate("Human", [x])

        # This should not raise an error
        exists = Formula.restricted_exists(x, student_x, human_x)
        forall = Formula.restricted_forall(x, student_x, human_x)

        assert exists is not None
        assert forall is not None

    def test_restricted_existential_reasoning(self):
        """Test restricted existential reasoning."""
        x = Formula.variable("X")
        a = Formula.constant("a")

        student_x = Formula.predicate("Student", [x])
        human_x = Formula.predicate("Human", [x])
        student_a = Formula.predicate("Student", [a])

        # Test basic satisfiability of restricted existential
        premise1 = Formula.restricted_exists(x, student_x, human_x)
        result = solve(premise1, t)
        assert result.satisfiable, "[∃X Student(X)]Human(X) should be satisfiable"

        # Test that we can construct complex formulas with restricted quantifiers
        complex_formula = premise1 & student_a
        result = solve(complex_formula, t)
        assert (
            result.satisfiable
        ), "Complex formula with restricted existential should be satisfiable"

    def test_restricted_universal_reasoning(self):
        """Test restricted universal reasoning."""
        x = Formula.variable("X")
        a = Formula.constant("a")

        student_x = Formula.predicate("Student", [x])
        human_x = Formula.predicate("Human", [x])
        student_a = Formula.predicate("Student", [a])

        # Test basic satisfiability of restricted universal
        premise1 = Formula.restricted_forall(x, student_x, human_x)
        result = solve(premise1, t)
        assert result.satisfiable, "[∀X Student(X)]Human(X) should be satisfiable"

        # Test that we can construct complex formulas with restricted quantifiers
        complex_formula = premise1 & student_a
        result = solve(complex_formula, t)
        assert (
            result.satisfiable
        ), "Complex formula with restricted universal should be satisfiable"
