"""
ACrQ semantic evaluator for bilateral predicates.

This module provides semantic evaluation for ACrQ formulas using weak Kleene
semantics with bilateral predicates.
"""

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Formula,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedQuantifierFormula,
    RestrictedUniversalFormula,
)
from .semantics import FALSE, TRUE, UNDEFINED, BilateralTruthValue, TruthValue


class ACrQInterpretation:
    """An interpretation for ACrQ with bilateral predicates."""

    def __init__(self) -> None:
        """Initialize empty interpretation."""
        self.propositional_values: dict[str, TruthValue] = {}
        self.bilateral_values: dict[str, BilateralTruthValue] = {}
        self.domain: set[str] = set()  # Domain of individuals

    def set_propositional(self, atom: str, value: TruthValue) -> None:
        """Set the value of a propositional atom."""
        self.propositional_values[atom] = value

    def set_bilateral(
        self,
        predicate: str,
        args: tuple[str, ...],
        positive: TruthValue,
        negative: TruthValue,
    ) -> None:
        """Set bilateral values for a predicate with arguments."""
        # Validate bilateral consistency
        if positive == TRUE and negative == TRUE:
            raise ValueError(
                f"Bilateral inconsistency: {predicate}{args} cannot be both true and false"
            )

        key = f"{predicate}{args}"
        self.bilateral_values[key] = BilateralTruthValue(
            positive=positive, negative=negative
        )

        # Add individuals to domain
        for arg in args:
            self.domain.add(arg)

    def get_bilateral(
        self, predicate: str, args: tuple[str, ...]
    ) -> BilateralTruthValue:
        """Get bilateral value for a predicate with arguments."""
        key = f"{predicate}{args}"
        if key in self.bilateral_values:
            return self.bilateral_values[key]
        # Default to gap (no information)
        return BilateralTruthValue(positive=FALSE, negative=FALSE)


class ACrQEvaluator:
    """Evaluator for ACrQ formulas under an interpretation."""

    def __init__(self, interpretation: ACrQInterpretation) -> None:
        """Initialize with an interpretation."""
        self.interpretation = interpretation

    def evaluate(self, formula: Formula) -> TruthValue:
        """Evaluate a formula under the interpretation."""
        if isinstance(formula, PropositionalAtom):
            return self._eval_atom(formula)
        elif isinstance(formula, BilateralPredicateFormula):
            return self._eval_bilateral_predicate(formula)
        elif isinstance(formula, PredicateFormula):
            return self._eval_standard_predicate(formula)
        elif isinstance(formula, CompoundFormula):
            return self._eval_compound(formula)
        elif isinstance(
            formula, (RestrictedExistentialFormula, RestrictedUniversalFormula)
        ):
            return self._eval_quantified(formula)
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")

    def _eval_atom(self, atom: PropositionalAtom) -> TruthValue:
        """Evaluate a propositional atom."""
        if atom.name in self.interpretation.propositional_values:
            return self.interpretation.propositional_values[atom.name]
        return UNDEFINED  # Unknown atoms are undefined

    def _eval_bilateral_predicate(self, pred: BilateralPredicateFormula) -> TruthValue:
        """Evaluate a bilateral predicate."""
        # Get arguments as strings
        args = tuple(str(term) for term in pred.terms)

        # Get bilateral value
        btv = self.interpretation.get_bilateral(pred.positive_name, args)

        # Return appropriate component
        if pred.is_negative:
            return btv.negative  # R* returns negative component
        else:
            return btv.positive  # R returns positive component

    def _eval_standard_predicate(self, pred: PredicateFormula) -> TruthValue:
        """Evaluate a standard predicate (convert to bilateral)."""
        # Standard predicates are treated as positive bilateral predicates
        args = tuple(str(term) for term in pred.terms)

        # Check if this is a star predicate
        if pred.predicate_name.endswith("*"):
            base_name = pred.predicate_name[:-1]
            btv = self.interpretation.get_bilateral(base_name, args)
            return btv.negative
        else:
            btv = self.interpretation.get_bilateral(pred.predicate_name, args)
            return btv.positive

    def _eval_compound(self, formula: CompoundFormula) -> TruthValue:
        """Evaluate a compound formula using weak Kleene semantics."""
        connective = formula.connective

        if connective == "~":
            return self._eval_negation(formula)
        elif connective == "&":
            return self._eval_conjunction(formula)
        elif connective == "|":
            return self._eval_disjunction(formula)
        elif connective == "->":
            return self._eval_implication(formula)
        else:
            raise ValueError(f"Unknown connective: {connective}")

    def _eval_negation(self, formula: CompoundFormula) -> TruthValue:
        """Evaluate negation using weak Kleene semantics."""
        sub_val = self.evaluate(formula.subformulas[0])
        if sub_val == TRUE:
            return FALSE
        elif sub_val == FALSE:
            return TRUE
        else:
            return UNDEFINED

    def _eval_conjunction(self, formula: CompoundFormula) -> TruthValue:
        """Evaluate conjunction using weak Kleene semantics."""
        left_val = self.evaluate(formula.subformulas[0])
        right_val = self.evaluate(formula.subformulas[1])

        # Weak Kleene: any undefined makes result undefined
        if left_val == UNDEFINED or right_val == UNDEFINED:
            return UNDEFINED
        elif left_val == TRUE and right_val == TRUE:
            return TRUE
        else:
            return FALSE

    def _eval_disjunction(self, formula: CompoundFormula) -> TruthValue:
        """Evaluate disjunction using weak Kleene semantics."""
        left_val = self.evaluate(formula.subformulas[0])
        right_val = self.evaluate(formula.subformulas[1])

        # Weak Kleene: any undefined makes result undefined
        if left_val == UNDEFINED or right_val == UNDEFINED:
            return UNDEFINED
        elif left_val == TRUE or right_val == TRUE:
            return TRUE
        else:
            return FALSE

    def _eval_implication(self, formula: CompoundFormula) -> TruthValue:
        """Evaluate implication using weak Kleene semantics."""
        ant_val = self.evaluate(formula.subformulas[0])
        cons_val = self.evaluate(formula.subformulas[1])

        # Weak Kleene: any undefined makes result undefined
        if ant_val == UNDEFINED or cons_val == UNDEFINED:
            return UNDEFINED
        elif ant_val == FALSE or cons_val == TRUE:
            return TRUE
        else:
            return FALSE

    def _eval_quantified(self, formula: RestrictedQuantifierFormula) -> TruthValue:
        """Evaluate a restricted quantified formula."""
        # This is a simplified evaluation - full implementation would need
        # to handle variable substitution properly

        if isinstance(formula, RestrictedExistentialFormula):
            # [∃X P(X)]Q(X) - exists x such that P(x) and Q(x)
            # Check all individuals in domain
            for individual in self.interpretation.domain:
                # Substitute variable with individual
                restriction_val = self._eval_with_substitution(
                    formula.restriction, {formula.var.name: individual}
                )
                matrix_val = self._eval_with_substitution(
                    formula.matrix, {formula.var.name: individual}
                )

                # If both are true for some individual, formula is true
                if restriction_val == TRUE and matrix_val == TRUE:
                    return TRUE
                # If either is undefined, we can't be sure
                elif restriction_val == UNDEFINED or matrix_val == UNDEFINED:
                    # Continue checking other individuals
                    continue

            # No witness found
            return FALSE

        elif isinstance(formula, RestrictedUniversalFormula):
            # [∀X P(X)]Q(X) - for all x, if P(x) then Q(x)
            has_undefined = False

            for individual in self.interpretation.domain:
                restriction_val = self._eval_with_substitution(
                    formula.restriction, {formula.var.name: individual}
                )
                matrix_val = self._eval_with_substitution(
                    formula.matrix, {formula.var.name: individual}
                )

                # Check implication P(x) → Q(x)
                if restriction_val == TRUE and matrix_val == FALSE:
                    return FALSE  # Counterexample found
                elif restriction_val == UNDEFINED or matrix_val == UNDEFINED:
                    has_undefined = True

            # No counterexample found
            return UNDEFINED if has_undefined else TRUE

        else:
            raise ValueError(f"Unknown quantifier type: {type(formula)}")

    def _eval_with_substitution(
        self, formula: Formula, substitution: dict[str, str]
    ) -> TruthValue:
        """Evaluate formula with variable substitution."""
        # This is a simplified implementation
        # A full implementation would properly handle variable substitution
        # For now, just evaluate the formula as-is
        return self.evaluate(formula)


def evaluate_acrq(formula: Formula, interpretation: ACrQInterpretation) -> TruthValue:
    """Evaluate an ACrQ formula under an interpretation."""
    evaluator = ACrQEvaluator(interpretation)
    return evaluator.evaluate(formula)
