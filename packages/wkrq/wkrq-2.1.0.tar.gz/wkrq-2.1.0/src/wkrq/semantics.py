"""
wKrQ three-valued weak Kleene semantics.

Implements the truth value system and semantic operations for wKrQ logic.
Truth values: t (true), e (undefined), f (false)
"""

from collections.abc import Generator
from dataclasses import dataclass


@dataclass(frozen=True)
class TruthValue:
    """A truth value in weak Kleene logic."""

    symbol: str
    name: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"TruthValue({self.symbol}, {self.name})"


# The three truth values of weak Kleene logic
TRUE = TruthValue("t", "true")
UNDEFINED = TruthValue("e", "undefined")
FALSE = TruthValue("f", "false")


@dataclass
class BilateralTruthValue:
    """Truth value for bilateral predicates in ACrQ.

    Each bilateral predicate has two independent truth values:
    - positive: The truth value of R
    - negative: The truth value of R*

    This creates four possible information states:
    - positive=TRUE, negative=FALSE: Standard true (determinate)
    - positive=FALSE, negative=TRUE: Standard false (determinate)
    - positive=FALSE, negative=FALSE: Knowledge gap (no information)
    - positive=TRUE, negative=TRUE: Knowledge glut (conflicting information)

    Note: The last case (both TRUE) violates consistency but is handled
    paraconsistently in ACrQ.
    """

    positive: TruthValue  # Value for R
    negative: TruthValue  # Value for R*

    def __post_init__(self) -> None:
        """Validate the bilateral truth value."""
        # We don't enforce consistency here to allow paraconsistent reasoning
        # but we could add a warning or flag
        pass

    def is_consistent(self) -> bool:
        """Check if the bilateral value is consistent.

        A bilateral value is inconsistent (a glut) when both R and R* are true.
        """
        return not (self.positive == TRUE and self.negative == TRUE)

    def is_gap(self) -> bool:
        """Check if neither R nor R* is true (truth value gap)."""
        return self.positive == FALSE and self.negative == FALSE

    def is_glut(self) -> bool:
        """Check if both R and R* are true (knowledge glut)."""
        return self.positive == TRUE and self.negative == TRUE

    def is_determinate(self) -> bool:
        """Check if exactly one of R or R* is true (classical behavior)."""
        return (self.positive == TRUE and self.negative == FALSE) or (
            self.positive == FALSE and self.negative == TRUE
        )

    def to_simple_value(self) -> str:
        """Convert to a simple string representation for user display."""
        if self.positive == TRUE and self.negative == FALSE:
            return "true"
        elif self.positive == FALSE and self.negative == TRUE:
            return "false"
        elif self.positive == UNDEFINED or self.negative == UNDEFINED:
            return "undefined"
        elif self.is_gap():
            return "undefined (gap)"
        elif self.is_glut():
            return "both (glut)"
        else:
            return f"complex({self.positive}/{self.negative})"

    def __str__(self) -> str:
        return f"BilateralTruthValue(pos={self.positive}, neg={self.negative})"

    def __repr__(self) -> str:
        return self.__str__()


class WeakKleeneSemantics:
    """Three-valued weak Kleene semantic system."""

    def __init__(self) -> None:
        self.truth_values = {TRUE, UNDEFINED, FALSE}
        self.designated_values = {TRUE}

        # Truth tables for connectives
        self._conjunction_table = self._build_conjunction_table()
        self._disjunction_table = self._build_disjunction_table()
        self._negation_table = self._build_negation_table()
        self._implication_table = self._build_implication_table()

    def _build_conjunction_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene conjunction truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): FALSE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): FALSE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): FALSE,
        }

    def _build_disjunction_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene disjunction truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): TRUE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): TRUE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): FALSE,
        }

    def _build_negation_table(self) -> dict[TruthValue, TruthValue]:
        """Build weak Kleene negation truth table."""
        return {TRUE: FALSE, UNDEFINED: UNDEFINED, FALSE: TRUE}

    def _build_implication_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene implication truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): FALSE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): TRUE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): TRUE,
        }

    def conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute conjunction of two truth values."""
        return self._conjunction_table[(a, b)]

    def disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute disjunction of two truth values."""
        return self._disjunction_table[(a, b)]

    def negation(self, a: TruthValue) -> TruthValue:
        """Compute negation of a truth value."""
        return self._negation_table[a]

    def implication(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute implication of two truth values."""
        return self._implication_table[(a, b)]

    def evaluate_connective(self, connective: str, *args: TruthValue) -> TruthValue:
        """Evaluate a connective with given truth value arguments."""
        if connective in ["&", "'", "∧"]:
            return self.conjunction(args[0], args[1])
        elif connective in ["|", "(", "∨"]:
            return self.disjunction(args[0], args[1])
        elif connective in ["~", "¬"]:
            return self.negation(args[0])
        elif connective in ["->", "→"]:
            return self.implication(args[0], args[1])
        else:
            raise ValueError(f"Unknown connective: {connective}")

    def is_designated(self, value: TruthValue) -> bool:
        """Check if a truth value is designated (true)."""
        return value in self.designated_values

    def all_valuations(
        self, atoms: set[str]
    ) -> Generator[dict[str, TruthValue], None, None]:
        """Generate all possible truth valuations for a set of atoms."""
        import itertools

        atoms_list = sorted(list(atoms))
        for values in itertools.product(self.truth_values, repeat=len(atoms_list)):
            yield dict(zip(atoms_list, values))
