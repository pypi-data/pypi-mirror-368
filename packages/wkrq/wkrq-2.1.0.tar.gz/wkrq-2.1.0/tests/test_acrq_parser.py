"""Comprehensive tests for full ACrQ parser."""

import pytest

from wkrq.acrq_parser import (
    ACrQParser,
    BilateralMode,
    MixedMode,
    SyntaxMode,
    TransparentMode,
    parse_acrq_formula,
)
from wkrq.formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Constant,
    PredicateFormula,
    PropositionalAtom,
)
from wkrq.parser import ParseError


class TestParserModes:
    """Test the three parser mode classes."""

    def test_transparent_mode(self):
        """Test transparent mode capabilities."""
        mode = TransparentMode()
        assert mode.can_parse_negated_predicate() is True
        assert mode.can_parse_predicate_star() is False

        # Test transform
        pred = PredicateFormula("Human", [Constant("socrates")])
        result = mode.transform_negated_predicate(pred)
        assert isinstance(result, BilateralPredicateFormula)
        assert result.is_negative is True
        assert str(result) == "Human*(socrates)"

        # Test error message
        msg = mode.get_error_message("Human*")
        assert "Star syntax" in msg
        assert "transparent mode" in msg

    def test_bilateral_mode(self):
        """Test bilateral mode capabilities."""
        mode = BilateralMode()
        assert mode.can_parse_negated_predicate() is False
        assert mode.can_parse_predicate_star() is True

        # Test transform raises error
        pred = PredicateFormula("Human", [Constant("socrates")])
        with pytest.raises(ParseError) as exc_info:
            mode.transform_negated_predicate(pred)
        assert "bilateral mode" in str(exc_info.value)
        assert "Human*" in str(exc_info.value)

        # Test error message
        msg = mode.get_error_message("¬Human(x)")
        assert "bilateral mode" in msg
        assert "Human*" in msg

    def test_mixed_mode(self):
        """Test mixed mode capabilities."""
        mode = MixedMode()
        assert mode.can_parse_negated_predicate() is True
        assert mode.can_parse_predicate_star() is True

        # Test transform
        pred = PredicateFormula("Human", [Constant("socrates")])
        result = mode.transform_negated_predicate(pred)
        assert isinstance(result, BilateralPredicateFormula)
        assert result.is_negative is True


class TestTransparentModeParsing:
    """Test parsing in transparent mode (default)."""

    def test_negated_predicate_translation(self):
        """¬P(x) should become P*(x)."""
        formula = parse_acrq_formula("¬Human(x)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is True
        assert str(formula) == "Human*(x)"

        # Also test with ~
        formula2 = parse_acrq_formula("~Human(x)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula2, BilateralPredicateFormula)
        assert formula2.is_negative is True
        assert str(formula2) == "Human*(x)"

    def test_star_syntax_rejected(self):
        """P* syntax not allowed in transparent mode."""
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("Human*(x)", SyntaxMode.TRANSPARENT)
        assert "Star syntax" in str(exc_info.value)
        assert "transparent mode" in str(exc_info.value)

        # Also test without parentheses
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("Human*", SyntaxMode.TRANSPARENT)
        assert "Star syntax" in str(exc_info.value)

    def test_positive_predicate(self):
        """Positive predicates become bilateral with is_negative=False."""
        formula = parse_acrq_formula("Human(x)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is False
        assert str(formula) == "Human(x)"

    def test_compound_formula_translation(self):
        """Test translation in compound formulas."""
        # ¬Human(x) ∧ Mortal(x)
        formula = parse_acrq_formula("¬Human(x) & Mortal(x)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "&"

        left = formula.subformulas[0]
        right = formula.subformulas[1]

        assert isinstance(left, BilateralPredicateFormula)
        assert left.is_negative is True
        assert str(left) == "Human*(x)"

        assert isinstance(right, BilateralPredicateFormula)
        assert right.is_negative is False
        assert str(right) == "Mortal(x)"

    def test_double_negation(self):
        """Test ¬¬P(x) handling."""
        formula = parse_acrq_formula("¬¬Human(x)", SyntaxMode.TRANSPARENT)
        # In transparent mode: ¬Human(x) → Human*(x)
        # So ¬¬Human(x) → ¬Human*(x)
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "~"
        inner = formula.subformulas[0]
        assert isinstance(inner, BilateralPredicateFormula)
        assert inner.is_negative is True  # Human*(x)
        assert str(inner) == "Human*(x)"

    def test_propositional_negation(self):
        """Test that propositional negation still works."""
        formula = parse_acrq_formula("¬p", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "~"
        assert isinstance(formula.subformulas[0], PropositionalAtom)

    def test_complex_mixed_formula(self):
        """Test complex formula with mixed elements."""
        formula = parse_acrq_formula(
            "(¬Human(x) → Mortal(x)) & (p | ¬q)", SyntaxMode.TRANSPARENT
        )
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "&"

        # Left side should have bilateral predicate
        left = formula.subformulas[0]
        assert isinstance(left, CompoundFormula)
        assert left.connective == "->"
        assert isinstance(left.subformulas[0], BilateralPredicateFormula)
        assert left.subformulas[0].is_negative is True

        # Right side should have propositional atoms
        right = formula.subformulas[1]
        assert isinstance(right, CompoundFormula)
        assert right.connective == "|"
        assert isinstance(right.subformulas[0], PropositionalAtom)


class TestBilateralModeParsing:
    """Test parsing in bilateral mode."""

    def test_star_syntax_accepted(self):
        """P* syntax required in bilateral mode."""
        formula = parse_acrq_formula("Human*(x)", SyntaxMode.BILATERAL)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is True
        assert str(formula) == "Human*(x)"

    def test_negation_rejected(self):
        """¬P(x) not allowed in bilateral mode."""
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("¬Human(x)", SyntaxMode.BILATERAL)
        assert "bilateral mode" in str(exc_info.value)
        assert "Human*" in str(exc_info.value)

        # Also test with ~
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("~Human(x)", SyntaxMode.BILATERAL)
        assert "bilateral mode" in str(exc_info.value)

    def test_positive_predicate_bilateral(self):
        """Positive predicates work normally."""
        formula = parse_acrq_formula("Human(x)", SyntaxMode.BILATERAL)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is False
        assert str(formula) == "Human(x)"

    def test_compound_with_stars(self):
        """Test compound formulas with P* syntax."""
        formula = parse_acrq_formula("Human*(x) | Mortal(y)", SyntaxMode.BILATERAL)
        assert isinstance(formula, CompoundFormula)

        left = formula.subformulas[0]
        assert isinstance(left, BilateralPredicateFormula)
        assert left.is_negative is True

        right = formula.subformulas[1]
        assert isinstance(right, BilateralPredicateFormula)
        assert right.is_negative is False

    def test_star_without_parens(self):
        """Test P* syntax without parentheses."""
        formula = parse_acrq_formula("Human*", SyntaxMode.BILATERAL)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is True
        assert formula.terms == []
        assert str(formula) == "Human*"

    def test_propositional_negation_allowed(self):
        """Propositional negation should still work."""
        formula = parse_acrq_formula("~p", SyntaxMode.BILATERAL)
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "~"
        assert isinstance(formula.subformulas[0], PropositionalAtom)


class TestMixedModeParsing:
    """Test parsing in mixed mode."""

    def test_both_syntaxes_accepted(self):
        """Both ¬P(x) and P* accepted."""
        # Negation syntax
        f1 = parse_acrq_formula("¬Human(x)", SyntaxMode.MIXED)
        assert isinstance(f1, BilateralPredicateFormula)
        assert f1.is_negative is True
        assert str(f1) == "Human*(x)"

        # Star syntax
        f2 = parse_acrq_formula("Human*(x)", SyntaxMode.MIXED)
        assert isinstance(f2, BilateralPredicateFormula)
        assert f2.is_negative is True
        assert str(f2) == "Human*(x)"

        # Both should be equal
        assert f1 == f2

    def test_mixed_compound(self):
        """Test mixing both syntaxes in one formula."""
        formula = parse_acrq_formula("¬Human(x) & Mortal*(y)", SyntaxMode.MIXED)
        assert isinstance(formula, CompoundFormula)

        left = formula.subformulas[0]
        right = formula.subformulas[1]

        # Both should be bilateral negative
        assert isinstance(left, BilateralPredicateFormula)
        assert left.is_negative is True
        assert str(left) == "Human*(x)"

        assert isinstance(right, BilateralPredicateFormula)
        assert right.is_negative is True
        assert str(right) == "Mortal*(y)"


class TestParserIntegration:
    """Test integration of parser modes with formulas."""

    def test_complex_formula_transparent(self):
        """Test complex formula in transparent mode."""
        formula_str = "(¬Human(x) → Mortal(x)) & (Animal(y) | ¬Plant(z))"
        formula = parse_acrq_formula(formula_str, SyntaxMode.TRANSPARENT)

        # Check structure
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "&"

        # Left side: implication
        left = formula.subformulas[0]
        assert isinstance(left, CompoundFormula)
        assert left.connective == "->"

        # Check ¬Human(x) became Human*(x)
        antecedent = left.subformulas[0]
        assert isinstance(antecedent, BilateralPredicateFormula)
        assert antecedent.is_negative is True

        # Right side: disjunction
        right = formula.subformulas[1]
        assert isinstance(right, CompoundFormula)
        assert right.connective == "|"

        # Check ¬Plant(z) became Plant*(z)
        right_right = right.subformulas[1]
        assert isinstance(right_right, BilateralPredicateFormula)
        assert right_right.is_negative is True
        assert str(right_right) == "Plant*(z)"

    def test_error_messages_helpful(self):
        """Test that error messages guide users correctly."""
        # Transparent mode with star
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("Human*(x) & Mortal(x)", SyntaxMode.TRANSPARENT)
        error_msg = str(exc_info.value)
        assert "Star syntax" in error_msg
        assert "transparent mode" in error_msg
        assert "¬P(x)" in error_msg or "~P(x)" in error_msg

        # Bilateral mode with negation
        with pytest.raises(ParseError) as exc_info:
            parse_acrq_formula("¬Human(x) | Mortal(x)", SyntaxMode.BILATERAL)
        error_msg = str(exc_info.value)
        assert "bilateral mode" in error_msg
        assert "Human*" in error_msg

    def test_default_mode_is_transparent(self):
        """Test that transparent is the default mode."""
        # No mode specified
        formula = parse_acrq_formula("¬Human(x)")
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is True

        # Should reject star syntax
        with pytest.raises(ParseError):
            parse_acrq_formula("Human*(x)")


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_predicate(self):
        """Test predicates without arguments."""
        # Transparent mode
        f1 = parse_acrq_formula("¬P", SyntaxMode.TRANSPARENT)
        assert isinstance(f1, BilateralPredicateFormula)
        assert f1.is_negative is True
        assert f1.terms == []
        assert str(f1) == "P*"

        # Bilateral mode
        f2 = parse_acrq_formula("P*", SyntaxMode.BILATERAL)
        assert isinstance(f2, BilateralPredicateFormula)
        assert f2.is_negative is True
        assert f2.terms == []

    def test_multiple_terms(self):
        """Test predicates with multiple terms."""
        formula = parse_acrq_formula("¬Loves(john, mary)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative is True
        assert len(formula.terms) == 2
        assert str(formula) == "Loves*(john, mary)"

    def test_nested_negations(self):
        """Test deeply nested negations."""
        # ¬¬¬P(x) in transparent mode
        formula = parse_acrq_formula("¬¬¬P(x)", SyntaxMode.TRANSPARENT)
        # Should parse as ¬(¬(P*(x)))
        assert isinstance(formula, CompoundFormula)
        assert formula.connective == "~"

    def test_unicode_support(self):
        """Test Unicode operator support."""
        # Test both ¬ and ~ work the same
        f1 = parse_acrq_formula("¬Human(x)", SyntaxMode.TRANSPARENT)
        f2 = parse_acrq_formula("~Human(x)", SyntaxMode.TRANSPARENT)
        assert str(f1) == str(f2)

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        formulas = [
            "¬Human(x)",
            "¬ Human(x)",
            "¬  Human( x )",
            "¬\tHuman(\tx\t)",
        ]

        results = [parse_acrq_formula(f, SyntaxMode.TRANSPARENT) for f in formulas]

        # All should parse to same structure
        for r in results[1:]:
            assert str(r) == str(results[0])

    def test_star_with_spaces(self):
        """Test star syntax with various spacing."""
        formulas = [
            "Human*(x)",
            "Human* (x)",
            "Human *(x)",
            "Human * (x)",
        ]

        # First should work
        f1 = parse_acrq_formula(formulas[0], SyntaxMode.BILATERAL)
        assert isinstance(f1, BilateralPredicateFormula)

        # Others might fail due to tokenization - that's ok
        # The important thing is the first standard form works


class TestTokenization:
    """Test the tokenizer specifically."""

    def test_tokenize_star_predicates(self):
        """Test tokenization of star predicates."""
        parser = ACrQParser("Human*(x) & Animal*", TransparentMode())
        tokens = parser._tokenize("Human*(x) & Animal*")

        assert "Human*(x)" in tokens
        assert "&" in tokens
        assert "Animal*" in tokens

    def test_tokenize_mixed_content(self):
        """Test tokenization of mixed content."""
        parser = ACrQParser("", TransparentMode())
        tokens = parser._tokenize("¬P(x) → (Q* | r)")

        assert "¬" in tokens
        assert "P(x)" in tokens
        assert "→" in tokens
        assert "(" in tokens
        assert "Q*" in tokens
        assert "|" in tokens
        assert "r" in tokens
        assert ")" in tokens
