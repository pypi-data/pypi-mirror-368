"""
Basic tests for wKrQ implementation.

Tests core functionality of the refactored wKrQ system.
"""

import pytest

from wkrq import (
    Formula,
    check_inference,
    entails,
    f,
    m,
    n,
    parse,
    parse_inference,
    solve,
    t,
    valid,
)
from wkrq.parser import ParseError
from wkrq.semantics import FALSE, TRUE, UNDEFINED, WeakKleeneSemantics


class TestBasicFormulas:
    """Test basic formula construction and evaluation."""

    def test_atom_creation(self):
        """Test propositional atom creation."""
        p = Formula.atom("p")
        assert str(p) == "p"
        assert p.is_atomic()
        assert p.get_atoms() == {"p"}

    def test_compound_formula_construction(self):
        """Test compound formula construction with operators."""
        p = Formula.atom("p")
        q = Formula.atom("q")

        # Conjunction
        conj = p & q
        assert str(conj) == "p & q"
        assert not conj.is_atomic()
        assert conj.get_atoms() == {"p", "q"}

        # Disjunction
        disj = p | q
        assert str(disj) == "p | q"

        # Negation
        neg = ~p
        assert str(neg) == "~p"

        # Implication
        impl = p.implies(q)
        assert str(impl) == "p -> q"

    def test_complex_formula(self):
        """Test complex formula construction."""
        p, q, r = Formula.atoms("p", "q", "r")
        formula = (p & q) | (~p & r)

        assert formula.get_atoms() == {"p", "q", "r"}
        assert formula.complexity() == 4  # 4 connectives


class TestSemantics:
    """Test weak Kleene semantics."""

    def test_truth_values(self):
        """Test truth value system."""
        semantics = WeakKleeneSemantics()

        assert TRUE in semantics.truth_values
        assert FALSE in semantics.truth_values
        assert UNDEFINED in semantics.truth_values
        assert semantics.is_designated(TRUE)
        assert not semantics.is_designated(FALSE)
        assert not semantics.is_designated(UNDEFINED)

    def test_conjunction_semantics(self):
        """Test weak Kleene conjunction."""
        semantics = WeakKleeneSemantics()

        # Standard cases
        assert semantics.conjunction(TRUE, TRUE) == TRUE
        assert semantics.conjunction(TRUE, FALSE) == FALSE
        assert semantics.conjunction(FALSE, TRUE) == FALSE
        assert semantics.conjunction(FALSE, FALSE) == FALSE

        # Undefined cases - Weak Kleene: any undefined input → undefined output
        assert semantics.conjunction(TRUE, UNDEFINED) == UNDEFINED
        assert semantics.conjunction(UNDEFINED, TRUE) == UNDEFINED
        assert semantics.conjunction(FALSE, UNDEFINED) == UNDEFINED
        assert semantics.conjunction(UNDEFINED, UNDEFINED) == UNDEFINED

    def test_disjunction_semantics(self):
        """Test weak Kleene disjunction."""
        semantics = WeakKleeneSemantics()

        # Standard cases
        assert semantics.disjunction(TRUE, TRUE) == TRUE
        assert semantics.disjunction(TRUE, FALSE) == TRUE
        assert semantics.disjunction(FALSE, TRUE) == TRUE
        assert semantics.disjunction(FALSE, FALSE) == FALSE

        # Undefined cases - Weak Kleene: any undefined input → undefined output
        assert semantics.disjunction(TRUE, UNDEFINED) == UNDEFINED
        assert semantics.disjunction(UNDEFINED, TRUE) == UNDEFINED
        assert semantics.disjunction(FALSE, UNDEFINED) == UNDEFINED
        assert semantics.disjunction(UNDEFINED, UNDEFINED) == UNDEFINED

    def test_negation_semantics(self):
        """Test weak Kleene negation."""
        semantics = WeakKleeneSemantics()

        assert semantics.negation(TRUE) == FALSE
        assert semantics.negation(FALSE) == TRUE
        assert semantics.negation(UNDEFINED) == UNDEFINED


class TestSigns:
    """Test sign system."""

    def test_sign_contradictions(self):
        """Test sign contradiction detection."""
        assert t.is_contradictory_with(f)
        assert f.is_contradictory_with(t)
        assert not t.is_contradictory_with(m)
        assert not t.is_contradictory_with(n)
        assert not m.is_contradictory_with(n)

    def test_sign_truth_conditions(self):
        """Test sign truth conditions."""
        assert t.truth_conditions() == {TRUE}
        assert f.truth_conditions() == {FALSE}
        assert m.truth_conditions() == {TRUE, FALSE}
        assert n.truth_conditions() == {
            FALSE,
            UNDEFINED,
        }  # n means "nontrue" - can be f or e


class TestTableauConstruction:
    """Test tableau construction."""

    def test_satisfiable_formula(self):
        """Test satisfiable formula."""
        p = Formula.atom("p")
        result = solve(p, t)

        assert result.satisfiable
        assert len(result.models) > 0
        assert result.total_nodes >= 1

    def test_unsatisfiable_formula(self):
        """Test unsatisfiable formula."""
        p = Formula.atom("p")
        contradiction = p & ~p
        result = solve(contradiction, t)

        assert not result.satisfiable
        assert len(result.models) == 0

    def test_tautology_detection(self):
        """Test tautology detection."""
        p = Formula.atom("p")
        tautology = p | ~p

        # In weak Kleene, p | ~p is NOT a tautology (can be undefined)
        assert not valid(tautology)

    def test_classical_inference(self):
        """Test classical inference patterns."""
        p, q = Formula.atoms("p", "q")

        # Modus ponens
        premises = [p, p.implies(q)]
        assert entails(premises, q)

        # Modus tollens
        premises = [p.implies(q), ~q]
        assert entails(premises, ~p)

        # Invalid inference
        assert not entails([p], q)


class TestParser:
    """Test formula parsing."""

    def test_basic_parsing(self):
        """Test basic formula parsing."""
        p = parse("p")
        assert str(p) == "p"

        conj = parse("p & q")
        assert str(conj) == "p & q"

        impl = parse("p -> q")
        assert str(impl) == "p -> q"

    def test_complex_parsing(self):
        """Test complex formula parsing."""
        formula = parse("(p & q) | (~p & r)")
        assert formula.get_atoms() == {"p", "q", "r"}

    def test_inference_parsing(self):
        """Test inference parsing."""
        inference = parse_inference("p, p -> q |- q")

        assert len(inference.premises) == 2
        assert str(inference.premises[0]) == "p"
        assert str(inference.conclusion) == "q"

    def test_parse_errors(self):
        """Test parse error handling."""
        with pytest.raises(ParseError):
            parse("p &")  # Incomplete formula

        with pytest.raises(ParseError):
            parse("p q")  # Invalid syntax


class TestInferenceTesting:
    """Test inference validity testing."""

    def test_valid_inference(self):
        """Test valid inference detection."""
        inference = parse_inference("p, p -> q |- q")
        result = check_inference(inference)

        assert result.valid
        assert len(result.countermodels) == 0

    def test_invalid_inference(self):
        """Test invalid inference detection."""
        inference = parse_inference("p |- q")
        result = check_inference(inference)

        assert not result.valid
        assert len(result.countermodels) > 0

    def test_complex_inference(self):
        """Test complex inference patterns."""
        # Disjunctive syllogism
        inference = parse_inference("p | q, ~p |- q")
        result = check_inference(inference)
        assert result.valid

        # Hypothetical syllogism
        inference = parse_inference("p -> q, q -> r |- p -> r")
        result = check_inference(inference)
        assert result.valid


class TestAPI:
    """Test high-level API."""

    def test_formula_creation(self):
        """Test API formula creation."""
        from wkrq.api import wkrq

        p = wkrq.atom("p")
        assert str(p) == "p"

        p, q = wkrq.atoms("p", "q")
        assert str(p) == "p"
        assert str(q) == "q"

    def test_formula_solving(self):
        """Test API formula solving."""
        from wkrq.api import wkrq

        p = wkrq.atom("p")
        result = wkrq.solve(p)

        assert result.satisfiable
        assert len(result.models) > 0

    def test_validity_checking(self):
        """Test API validity checking."""
        from wkrq.api import wkrq

        p = wkrq.atom("p")
        tautology = p | ~p

        assert not wkrq.valid(tautology)

    def test_model_finding(self):
        """Test API model finding."""
        from wkrq.api import wkrq

        p, q = wkrq.atoms("p", "q")
        formula = p | q

        models = wkrq.models(formula)
        assert len(models) > 0
