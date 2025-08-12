"""
wKrQ sign system for tableau construction (Ferguson 2021).

Signs: t (true), f (false), e (error/undefined), m (meaningful), n (nontrue), v (variable)
Following Ferguson's Definition 9 exactly.
"""

from dataclasses import dataclass

from .formula import Formula
from .semantics import FALSE, TRUE, UNDEFINED, TruthValue


@dataclass(frozen=True)
class Sign:
    """A sign in the Ferguson wKrQ tableau system."""

    symbol: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"Sign({self.symbol})"

    def is_contradictory_with(self, other: "Sign") -> bool:
        """Check if this sign contradicts another sign.

        Per Ferguson Definition 10: A branch closes if there is a sentence φ
        and distinct v, u ∈ V₃ such that both v : φ and u : φ appear on B.
        """
        # Two signs contradict if they are different members of {t, f, e}
        if self.symbol in {"t", "f", "e"} and other.symbol in {"t", "f", "e"}:
            return self.symbol != other.symbol
        return False

    def truth_conditions(self) -> set[TruthValue]:
        """Get the set of truth values this sign represents.

        Note: m and n are branching instructions, not truth values.
        """
        if self.symbol == "t":
            return {TRUE}
        elif self.symbol == "f":
            return {FALSE}
        elif self.symbol == "e":
            return {UNDEFINED}
        elif self.symbol == "m":
            # m is a branching instruction: both t and f possible
            return {TRUE, FALSE}
        elif self.symbol == "n":
            # n is a branching instruction: both f and e possible
            return {FALSE, UNDEFINED}
        elif self.symbol == "v":
            # v is a meta-variable representing any of {t, f, e}
            return {TRUE, FALSE, UNDEFINED}
        else:
            raise ValueError(f"Unknown sign: {self.symbol}")


# Ferguson's signs from Definition 9
t = Sign("t")  # True
f = Sign("f")  # False
e = Sign("e")  # Error/undefined
m = Sign("m")  # Meaningful (branching: t or f)
n = Sign("n")  # Nontrue (branching: f or e)
v = Sign("v")  # Variable (meta-sign for any of t, f, e)

# All valid signs (v is meta, not used directly in formulas)
SIGNS = {t, f, e, m, n}

# For backward compatibility during migration
T = t
F = f
M = m
N = n


@dataclass(frozen=True)
class SignedFormula:
    """A formula with a sign attached."""

    sign: Sign
    formula: Formula

    def __str__(self) -> str:
        return f"{self.sign}: {self.formula}"

    def __repr__(self) -> str:
        return f"SignedFormula({self.sign}, {self.formula})"

    def contradicts(self, other: "SignedFormula") -> bool:
        """Check if this signed formula contradicts another."""
        return self.formula == other.formula and self.sign.is_contradictory_with(
            other.sign
        )


def sign_from_string(s: str) -> Sign:
    """Convert a string to a sign."""
    s = s.lower()  # Ferguson uses lowercase
    if s == "t":
        return t
    elif s == "f":
        return f
    elif s == "e":
        return e
    elif s == "m":
        return m
    elif s == "n":
        return n
    elif s == "v":
        return v
    else:
        raise ValueError(f"Invalid sign: {s}. Must be t, f, e, m, n, or v.")
