"""
wKrQ API for inference testing and formula evaluation.

Provides high-level interface for working with wKrQ logic.
"""

from dataclasses import dataclass
from typing import Optional

from .formula import Formula
from .parser import Inference, parse, parse_inference
from .signs import Sign, sign_from_string, t
from .tableau import Model, TableauResult, entails, solve, valid


@dataclass
class InferenceResult:
    """Result of testing an inference."""

    valid: bool
    inference: Inference
    countermodels: list[Model]
    tableau_result: TableauResult

    def __str__(self) -> str:
        if self.valid:
            return f"✓ Valid inference: {self.inference}"
        else:
            countermodel_str = ", ".join(str(m) for m in self.countermodels)
            return f"✗ Invalid inference: {self.inference}\nCountermodels: {countermodel_str}"


def check_inference(
    inference: Inference, consequence: str = "strong", trace: bool = False
) -> InferenceResult:
    """
    Test the validity of an inference.

    Args:
        inference: The inference to test
        consequence: Type of consequence relation ("strong" or "weak")
        trace: Whether to enable construction tracing

    Returns:
        InferenceResult with validity information and optional trace
    """
    # Convert inference to formula for tableau testing
    test_formula = inference.to_formula()

    # Test satisfiability
    result = solve(test_formula, t, trace=trace)

    # Inference is valid if test formula is unsatisfiable
    is_valid = not result.satisfiable
    countermodels = result.models if not is_valid else []

    return InferenceResult(
        valid=is_valid,
        inference=inference,
        countermodels=countermodels,
        tableau_result=result,
    )


def evaluate_formula(
    formula: Formula, sign: Sign = t, track_steps: bool = False
) -> TableauResult:
    """
    Evaluate a formula with the given sign.

    Args:
        formula: The formula to evaluate
        sign: The sign to test (t, f, e, m, or n)
        track_steps: Whether to track tableau construction steps

    Returns:
        TableauResult with satisfiability information
    """
    return solve(formula, sign)


def check_validity(formula: Formula) -> bool:
    """Check if a formula is valid (true in all models)."""
    return valid(formula)


def check_entailment(premises: list[Formula], conclusion: Formula) -> bool:
    """Check if premises entail conclusion."""
    return entails(premises, conclusion)


def find_models(
    formula: Formula, sign: Sign = t, limit: Optional[int] = None
) -> list[Model]:
    """
    Find models that satisfy the formula with the given sign.

    Args:
        formula: The formula to find models for
        sign: The sign to test
        limit: Maximum number of models to return (None for all)

    Returns:
        List of models
    """
    result = solve(formula, sign)
    models = result.models

    if limit is not None:
        models = models[:limit]

    return models


class WkrqLogic:
    """Main interface for wKrQ logic operations."""

    def __init__(self) -> None:
        self.name = "wkrq"
        self.description = "Weak Kleene logic with restricted quantification"

    def parse(self, input_str: str) -> Formula:
        """Parse a formula string."""
        return parse(input_str)

    def parse_inference(self, input_str: str) -> Inference:
        """Parse an inference string."""
        return parse_inference(input_str)

    def solve(self, formula: Formula, sign: str = "t") -> TableauResult:
        """Solve a formula with the given sign."""
        sign_obj = sign_from_string(sign)
        return solve(formula, sign_obj)

    def valid(self, formula: Formula) -> bool:
        """Check if formula is valid."""
        return valid(formula)

    def entails(self, premises: list[Formula], conclusion: Formula) -> bool:
        """Check entailment."""
        return entails(premises, conclusion)

    def check_inference(self, inference: Inference) -> InferenceResult:
        """Test inference validity."""
        return check_inference(inference)

    def atom(self, name: str) -> Formula:
        """Create a propositional atom."""
        return Formula.atom(name)

    def atoms(self, *names: str) -> list[Formula]:
        """Create multiple propositional atoms."""
        return list(Formula.atoms(*names))

    def models(
        self, formula: Formula, sign: str = "t", limit: Optional[int] = None
    ) -> list[Model]:
        """Find models for a formula."""
        sign_obj = sign_from_string(sign)
        return find_models(formula, sign_obj, limit)


# Global instance for convenient access
wkrq = WkrqLogic()
