"""
ACrQ-specific tableau rules from Ferguson's Definition 18.

This module implements the ACrQ tableau calculus which modifies wKrQ by:
1. Dropping the negation elimination rule (~ rule)
2. Adding special rules for bilateral predicates (R*)
3. Maintaining all other wKrQ rules unchanged

Based on Ferguson (2021) Definition 18.
"""

from typing import Callable, Optional

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Constant,
    PredicateFormula,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
)
from .signs import SignedFormula
from .wkrq_rules import (
    FergusonRule,
    get_conjunction_rule,
    get_disjunction_rule,
    get_implication_rule,
    get_restricted_existential_rule,
    get_restricted_universal_rule,
)


def get_acrq_negation_rule(signed_formula: SignedFormula) -> Optional[FergusonRule]:
    """Get ACrQ negation rule per Definition 18.

    ACrQ drops the general negation elimination rule from wKrQ.
    Only handles specific bilateral predicate cases:

    v : ~R(c₀,...,cₙ₋₁)
    -------------------
    v : R*(c₀,...,cₙ₋₁)

    v : ~R*(c₀,...,cₙ₋₁)
    --------------------
    v : R(c₀,...,cₙ₋₁)

    Also handles: v : ~~φ → v : φ
    """
    sign = signed_formula.sign
    formula = signed_formula.formula

    if not (isinstance(formula, CompoundFormula) and formula.connective == "~"):
        return None

    subformula = formula.subformulas[0]

    # Handle double negation: v : ~~φ → v : φ
    if isinstance(subformula, CompoundFormula) and subformula.connective == "~":
        return FergusonRule(
            name=f"{sign.symbol}-double-negation",
            premise=signed_formula,
            conclusions=[[SignedFormula(sign, subformula.subformulas[0])]],
        )

    # Handle negated predicates: convert to bilateral form
    if isinstance(subformula, PredicateFormula) and not isinstance(
        subformula, BilateralPredicateFormula
    ):
        # Create R* from ~R
        bilateral = BilateralPredicateFormula(
            positive_name=subformula.predicate_name,
            terms=subformula.terms,
            is_negative=True,
        )
        return FergusonRule(
            name=f"{sign.symbol}-negated-predicate-to-bilateral",
            premise=signed_formula,
            conclusions=[[SignedFormula(sign, bilateral)]],
        )

    # Handle negated bilateral predicates: ~R* → R
    if isinstance(subformula, BilateralPredicateFormula):
        if subformula.is_negative:
            # ~R* → R
            positive = PredicateFormula(
                predicate_name=subformula.positive_name, terms=subformula.terms
            )
            return FergusonRule(
                name=f"{sign.symbol}-negated-bilateral-to-positive",
                premise=signed_formula,
                conclusions=[[SignedFormula(sign, positive)]],
            )
        else:
            # ~R → R* (shouldn't happen in well-formed ACrQ)
            negative = BilateralPredicateFormula(
                positive_name=subformula.positive_name,
                terms=subformula.terms,
                is_negative=True,
            )
            return FergusonRule(
                name=f"{sign.symbol}-negated-positive-to-bilateral",
                premise=signed_formula,
                conclusions=[[SignedFormula(sign, negative)]],
            )

    # For compound formulas other than predicates, we don't eliminate negation
    # This is the key difference from wKrQ - no general negation elimination
    return None


def _get_acrq_compound_rule(signed_formula: SignedFormula) -> Optional[FergusonRule]:
    """Get rule for compound formulas in ACrQ."""
    formula = signed_formula.formula
    if not isinstance(formula, CompoundFormula):
        return None

    # ACrQ has special negation handling
    if formula.connective == "~":
        return get_acrq_negation_rule(signed_formula)

    # Other connectives use standard wKrQ rules
    connective_rules = {
        "&": get_conjunction_rule,
        "|": get_disjunction_rule,
        "->": get_implication_rule,
    }

    rule_func = connective_rules.get(formula.connective)
    return rule_func(signed_formula) if rule_func else None


def _get_acrq_universal_constant(
    existing_constants: Optional[list[str]],
    used_constants: Optional[set[str]],
    fresh_constant_generator: Callable[[], Constant],
) -> Optional[Constant]:
    """Get the appropriate constant for universal instantiation in ACrQ."""
    if existing_constants and used_constants is not None:
        # Find first unused constant
        for const_name in existing_constants:
            if const_name not in used_constants:
                return Constant(const_name)
        # All existing constants have been used
        return None
    elif existing_constants:
        # No tracking, use first constant
        return Constant(existing_constants[0])
    else:
        # No existing constants, generate fresh one
        return fresh_constant_generator()


def get_acrq_rule(
    signed_formula: SignedFormula,
    fresh_constant_generator,  # type: Callable[[], Constant]
    existing_constants: Optional[list[str]] = None,
    used_constants: Optional[set[str]] = None,
) -> Optional[FergusonRule]:
    """Get applicable ACrQ rule for a signed formula.

    ACrQ uses all wKrQ rules except for negation elimination,
    plus special handling for bilateral predicates.
    """
    formula = signed_formula.formula

    # Handle bilateral predicates - they are atomic
    if isinstance(formula, BilateralPredicateFormula):
        return None

    # Try compound formula rules
    if isinstance(formula, CompoundFormula):
        return _get_acrq_compound_rule(signed_formula)

    # Handle existential quantifier
    if isinstance(formula, RestrictedExistentialFormula):
        fresh_const = fresh_constant_generator()
        existing_const = None
        if existing_constants and len(existing_constants) > 0:
            existing_const = Constant(existing_constants[0])
        return get_restricted_existential_rule(
            signed_formula, fresh_const, existing_const
        )

    # Handle universal quantifier
    if isinstance(formula, RestrictedUniversalFormula):
        const = _get_acrq_universal_constant(
            existing_constants, used_constants, fresh_constant_generator
        )
        if const is None:
            return None
        return get_restricted_universal_rule(signed_formula, const)

    return None
