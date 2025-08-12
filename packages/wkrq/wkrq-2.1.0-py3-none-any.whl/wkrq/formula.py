"""
wKrQ formula representations.

Provides formula types for propositional and first-order wKrQ logic
with restricted quantifiers.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Formula(ABC):
    """Base class for all wKrQ formulas."""

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the formula."""
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Check equality with another formula."""
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        pass

    @abstractmethod
    def get_atoms(self) -> set[str]:
        """Get all atomic formulas in this formula."""
        pass

    @abstractmethod
    def substitute(self, mapping: dict[str, "Formula"]) -> "Formula":
        """Substitute atoms/terms according to mapping."""
        pass

    @abstractmethod
    def is_atomic(self) -> bool:
        """Check if this is an atomic formula."""
        pass

    def complexity(self) -> int:
        """Return the complexity (number of connectives) of the formula."""
        if self.is_atomic():
            return 0
        if isinstance(self, CompoundFormula):
            return 1 + sum(sub.complexity() for sub in self.subformulas)
        return 0

    # Operator overloading for natural formula construction
    def __and__(self, other: "Formula") -> "Formula":
        """Conjunction using & operator."""
        return Conjunction(self, other)

    def __or__(self, other: "Formula") -> "Formula":
        """Disjunction using | operator."""
        return Disjunction(self, other)

    def __invert__(self) -> "Formula":
        """Negation using ~ operator."""
        return Negation(self)

    def implies(self, other: "Formula") -> "Formula":
        """Implication using method call."""
        return Implication(self, other)

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Formula":
        """Substitute terms in the formula."""
        # Default implementation - override in subclasses that contain terms
        return self

    # Static constructors
    @staticmethod
    def atom(name: str) -> "PropositionalAtom":
        """Create a propositional atom."""
        return PropositionalAtom(name)

    @staticmethod
    def atoms(*names: str) -> list["PropositionalAtom"]:
        """Create multiple propositional atoms."""
        return [PropositionalAtom(name) for name in names]

    @staticmethod
    def variable(name: str) -> "Variable":
        """Create a first-order variable."""
        return Variable(name)

    @staticmethod
    def constant(name: str) -> "Constant":
        """Create a first-order constant."""
        return Constant(name)

    @staticmethod
    def predicate(name: str, terms: list["Term"]) -> "PredicateFormula":
        """Create a predicate formula."""
        return PredicateFormula(name, terms)

    @staticmethod
    def restricted_exists(
        variable: "Variable", restriction: "Formula", matrix: "Formula"
    ) -> "RestrictedExistentialFormula":
        """Create a restricted existential quantifier: [∃X P(X)]Q(X)"""
        return RestrictedExistentialFormula(variable, restriction, matrix)

    @staticmethod
    def restricted_forall(
        variable: "Variable", restriction: "Formula", matrix: "Formula"
    ) -> "RestrictedUniversalFormula":
        """Create a restricted universal quantifier: [∀X P(X)]Q(X)"""
        return RestrictedUniversalFormula(variable, restriction, matrix)


class PropositionalAtom(Formula):
    """A propositional atom (variable)."""

    def __init__(self, name: str):
        if not name:
            raise ValueError("Atom name cannot be empty")
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, PropositionalAtom) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("atom", self.name))

    def get_atoms(self) -> set[str]:
        return {self.name}

    def substitute(self, mapping: dict[str, Formula]) -> Formula:
        return mapping.get(self.name, self)

    def is_atomic(self) -> bool:
        return True


class Term(ABC):
    """Base class for first-order terms."""

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def substitute_term(self, mapping: dict[str, "Term"]) -> "Term":
        """Substitute terms according to mapping."""
        pass


class Constant(Term):
    """A constant term."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Constant) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("constant", self.name))

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Term":
        return mapping.get(self.name, self)


class Variable(Term):
    """A variable term."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("variable", self.name))

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Term":
        return mapping.get(self.name, self)


class PredicateFormula(Formula):
    """A predicate applied to terms."""

    def __init__(self, predicate_name: str, terms: list[Term]):
        self.predicate_name = predicate_name
        self.terms = terms

    def __str__(self) -> str:
        if not self.terms:
            return self.predicate_name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{self.predicate_name}({term_str})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PredicateFormula)
            and self.predicate_name == other.predicate_name
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("predicate", self.predicate_name, tuple(self.terms)))

    def get_atoms(self) -> set[str]:
        # Only return this as an atom if all terms are constants (ground atom)
        # Don't include predicates with variables in the model
        if all(isinstance(term, Constant) for term in self.terms):
            return {str(self)}
        return set()

    def substitute(self, mapping: dict[str, Formula]) -> Formula:
        # For predicates, we might substitute the whole predicate
        return mapping.get(str(self), self)

    def substitute_terms(self, mapping: dict[str, "Term"]) -> "PredicateFormula":
        """Substitute terms in the predicate."""
        new_terms = [t.substitute_term(mapping) for t in self.terms]
        return PredicateFormula(self.predicate_name, new_terms)

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Formula":
        """Substitute terms in the predicate formula."""
        return self.substitute_terms(mapping)

    def is_atomic(self) -> bool:
        return True


class BilateralPredicateFormula(PredicateFormula):
    """A bilateral predicate R/R* for ACrQ.

    In ACrQ, each predicate R has a dual R* for tracking falsity.
    This creates four possible information states:
    - R(a)=t, R*(a)=f: Positive evidence only (clearly true)
    - R(a)=f, R*(a)=t: Negative evidence only (clearly false)
    - R(a)=f, R*(a)=f: No evidence either way (knowledge gap)
    - R(a)=t, R*(a)=t: Conflicting evidence (knowledge glut)
    """

    def __init__(
        self,
        positive_name: str,
        terms: list[Term],
        negative_name: Optional[str] = None,
        is_negative: bool = False,
    ):
        """Initialize a bilateral predicate.

        Args:
            positive_name: The base predicate name (R)
            terms: The terms applied to the predicate
            negative_name: The negative predicate name (R*), auto-generated if None
            is_negative: Whether this instance represents R* (True) or R (False)
        """
        # Call parent constructor with the appropriate name
        name = negative_name or f"{positive_name}*" if is_negative else positive_name
        super().__init__(name, terms)

        self.positive_name = positive_name
        self.negative_name = negative_name or f"{positive_name}*"
        self.is_negative = is_negative

    def __str__(self) -> str:
        name = self.negative_name if self.is_negative else self.positive_name
        if not self.terms:
            return name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{name}({term_str})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, BilateralPredicateFormula)
            and self.positive_name == other.positive_name
            and self.negative_name == other.negative_name
            and self.terms == other.terms
            and self.is_negative == other.is_negative
        )

    def __hash__(self) -> int:
        return hash(
            (
                "bilateral",
                self.positive_name,
                self.negative_name,
                tuple(self.terms),
                self.is_negative,
            )
        )

    def get_atoms(self) -> set[str]:
        # Only return this as an atom if all terms are constants (ground atom)
        # Don't include predicates with variables in the model
        if all(isinstance(term, Constant) for term in self.terms):
            return {str(self)}
        return set()

    def substitute(self, mapping: dict[str, Formula]) -> Formula:
        # For bilateral predicates, we might substitute the whole predicate
        return mapping.get(str(self), self)

    def substitute_terms(self, mapping: dict[str, Term]) -> "BilateralPredicateFormula":
        """Substitute terms in the bilateral predicate."""
        new_terms = [t.substitute_term(mapping) for t in self.terms]
        return BilateralPredicateFormula(
            self.positive_name, new_terms, self.negative_name, self.is_negative
        )

    def substitute_term(self, mapping: dict[str, Term]) -> Formula:
        """Substitute terms in the bilateral predicate formula."""
        return self.substitute_terms(mapping)

    def is_atomic(self) -> bool:
        return True

    def get_dual(self) -> "BilateralPredicateFormula":
        """Return the dual predicate (R ↔ R*)."""
        return BilateralPredicateFormula(
            positive_name=self.positive_name,
            terms=self.terms,
            negative_name=self.negative_name,
            is_negative=not self.is_negative,
        )

    def to_standard_predicates(self) -> tuple[PredicateFormula, PredicateFormula]:
        """Convert to pair of standard predicates (R, R*)."""
        pos = PredicateFormula(self.positive_name, self.terms)
        neg = PredicateFormula(self.negative_name, self.terms)
        return (pos, neg)

    def get_base_name(self) -> str:
        """Get the base predicate name (without *)."""
        return self.positive_name


class CompoundFormula(Formula):
    """A compound formula with a connective."""

    def __init__(self, connective: str, subformulas: list[Formula]):
        self.connective = connective
        self.subformulas = subformulas

    def __str__(self) -> str:
        if self.connective == "~" and len(self.subformulas) == 1:
            subformula = self.subformulas[0]
            if isinstance(subformula, CompoundFormula):
                return f"~({subformula})"
            else:
                return f"~{subformula}"
        elif len(self.subformulas) == 2:
            left, right = self.subformulas
            # Add parentheses for clarity
            left_str = f"({left})" if isinstance(left, CompoundFormula) else str(left)
            right_str = (
                f"({right})" if isinstance(right, CompoundFormula) else str(right)
            )
            return f"{left_str} {self.connective} {right_str}"
        else:
            raise ValueError(
                f"Invalid compound formula: {self.connective} with {len(self.subformulas)} subformulas"
            )

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, CompoundFormula)
            and self.connective == other.connective
            and self.subformulas == other.subformulas
        )

    def __hash__(self) -> int:
        return hash((self.connective, tuple(self.subformulas)))

    def get_atoms(self) -> set[str]:
        atoms = set()
        for sub in self.subformulas:
            atoms.update(sub.get_atoms())
        return atoms

    def substitute(self, mapping: dict[str, Formula]) -> Formula:
        new_subs = [sub.substitute(mapping) for sub in self.subformulas]
        return CompoundFormula(self.connective, new_subs)

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Formula":
        """Substitute terms in compound formula."""
        new_subs = [sub.substitute_term(mapping) for sub in self.subformulas]
        return CompoundFormula(self.connective, new_subs)

    def is_atomic(self) -> bool:
        return False


class RestrictedQuantifierFormula(Formula):
    """Base class for restricted quantifier formulas."""

    def __init__(
        self, quantifier: str, variable: Variable, restriction: Formula, matrix: Formula
    ):
        self.quantifier = quantifier
        self.var = variable
        self.restriction = restriction
        self.matrix = matrix

    def __str__(self) -> str:
        return f"[{self.quantifier}{self.var} {self.restriction}]{self.matrix}"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, RestrictedQuantifierFormula)
            and self.quantifier == other.quantifier
            and self.var == other.var
            and self.restriction == other.restriction
            and self.matrix == other.matrix
        )

    def __hash__(self) -> int:
        return hash(
            (
                "restricted_quantifier",
                self.quantifier,
                self.var,
                self.restriction,
                self.matrix,
            )
        )

    def get_atoms(self) -> set[str]:
        atoms = set()
        atoms.update(self.restriction.get_atoms())
        atoms.update(self.matrix.get_atoms())
        return atoms

    def substitute(self, mapping: dict[str, Formula]) -> Formula:
        # Don't substitute the bound variable
        filtered_mapping = {k: v for k, v in mapping.items() if k != str(self.var)}
        new_restriction = self.restriction.substitute(filtered_mapping)
        new_matrix = self.matrix.substitute(filtered_mapping)
        return self.__class__(self.quantifier, self.var, new_restriction, new_matrix)

    def substitute_term(self, mapping: dict[str, "Term"]) -> "Formula":
        """Substitute terms in restricted quantifier formula."""
        # Don't substitute the bound variable
        filtered_mapping = {k: v for k, v in mapping.items() if k != str(self.var)}
        new_restriction = self.restriction.substitute_term(filtered_mapping)
        new_matrix = self.matrix.substitute_term(filtered_mapping)
        return self.__class__(self.quantifier, self.var, new_restriction, new_matrix)

    def is_atomic(self) -> bool:
        return False

    def complexity(self) -> int:
        return 1 + self.restriction.complexity() + self.matrix.complexity()


class RestrictedExistentialFormula(RestrictedQuantifierFormula):
    """Restricted existential quantifier: [∃X P(X)]Q(X)"""

    def __init__(self, variable: Variable, restriction: Formula, matrix: Formula):
        super().__init__("∃", variable, restriction, matrix)


class RestrictedUniversalFormula(RestrictedQuantifierFormula):
    """Restricted universal quantifier: [∀X P(X)]Q(X)"""

    def __init__(self, variable: Variable, restriction: Formula, matrix: Formula):
        super().__init__("∀", variable, restriction, matrix)


# Convenience functions for formula construction
def negation(formula: Formula) -> CompoundFormula:  # noqa: N802
    """Create a negation."""
    return CompoundFormula("~", [formula])


def conjunction(left: Formula, right: Formula) -> CompoundFormula:  # noqa: N802
    """Create a conjunction."""
    return CompoundFormula("&", [left, right])


def disjunction(left: Formula, right: Formula) -> CompoundFormula:  # noqa: N802
    """Create a disjunction."""
    return CompoundFormula("|", [left, right])


def implication(left: Formula, right: Formula) -> CompoundFormula:  # noqa: N802
    """Create an implication."""
    return CompoundFormula("->", [left, right])


# Keep uppercase versions for backwards compatibility
Negation = negation
Conjunction = conjunction
Disjunction = disjunction
Implication = implication
