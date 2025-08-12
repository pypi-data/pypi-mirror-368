"""
wKrQ - Weak Kleene logic with restricted quantification.

A three-valued logic system with restricted quantifiers for first-order reasoning.
Based on Ferguson (2021) semantics with tableau-based theorem proving.
"""

from .acrq_parser import SyntaxMode, parse_acrq_formula
from .acrq_tableau import ACrQTableau
from .api import Inference, check_inference
from .formula import (
    BilateralPredicateFormula,
    Constant,
    Formula,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Term,
    Variable,
)
from .parser import parse, parse_inference
from .semantics import (
    FALSE,
    TRUE,
    UNDEFINED,
    BilateralTruthValue,
    TruthValue,
    WeakKleeneSemantics,
)
from .signs import Sign, SignedFormula, e, f, m, n, t
from .tableau import Tableau, TableauResult, WKrQTableau, entails, solve, valid

__version__ = "2.1.0"

__all__ = [
    # Core types
    "Formula",
    "PropositionalAtom",
    "PredicateFormula",
    "BilateralPredicateFormula",
    "Variable",
    "Constant",
    "Term",
    "RestrictedExistentialFormula",
    "RestrictedUniversalFormula",
    # Semantics
    "WeakKleeneSemantics",
    "TruthValue",
    "BilateralTruthValue",
    "TRUE",
    "FALSE",
    "UNDEFINED",
    # Signs
    "Sign",
    "SignedFormula",
    "t",
    "f",
    "e",
    "m",
    "n",
    # Tableau
    "Tableau",
    "WKrQTableau",
    "ACrQTableau",
    "TableauResult",
    # Main functions
    "solve",
    "valid",
    "entails",
    "parse",
    "parse_inference",
    "check_inference",
    "Inference",
    # ACrQ parser (minimal)
    "parse_acrq_formula",
    "SyntaxMode",
]
