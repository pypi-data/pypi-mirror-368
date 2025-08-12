"""ACrQ parser - simple implementation."""

from enum import Enum

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Formula,
    PredicateFormula,
)


class SyntaxMode(Enum):
    """Available syntax modes."""

    TRANSPARENT = "transparent"
    BILATERAL = "bilateral"
    MIXED = "mixed"


def parse_acrq_formula(
    input_string: str, syntax_mode: SyntaxMode = SyntaxMode.TRANSPARENT
) -> Formula:
    """Parse ACrQ formula with transparent mode support."""
    # Use the convenience function that ensures we get a Formula
    from .parser import parse

    formula = parse(input_string)

    # In transparent mode, convert negated predicates
    if syntax_mode == SyntaxMode.TRANSPARENT:
        formula = _apply_transparent_translation(formula)

    return formula


def _apply_transparent_translation(formula: Formula) -> Formula:
    """Apply Ferguson's translation: ¬P(x) → P*(x)."""
    if isinstance(formula, CompoundFormula):
        if formula.connective in ["~", "¬"]:
            inner = formula.subformulas[0]
            if isinstance(inner, PredicateFormula):
                # Convert ¬P(x) to P*(x)
                return BilateralPredicateFormula(
                    positive_name=inner.predicate_name,
                    terms=inner.terms,
                    is_negative=True,
                )
        # Recursively translate subformulas
        translated_subs = [
            _apply_transparent_translation(sub) for sub in formula.subformulas
        ]
        return CompoundFormula(formula.connective, translated_subs)

    # Convert regular predicates to bilateral
    if isinstance(formula, PredicateFormula):
        return BilateralPredicateFormula(
            positive_name=formula.predicate_name, terms=formula.terms, is_negative=False
        )

    return formula
