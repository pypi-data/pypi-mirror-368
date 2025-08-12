"""
Full ACrQ parser with complete mode support and star syntax.

This module provides a complete parser for ACrQ formulas with three syntax modes:
- Transparent: Standard syntax, ¬P(x) automatically becomes P*(x)
- Bilateral: Explicit R/R* syntax only, ¬P(x) is an error
- Mixed: Both syntaxes allowed
"""

import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Constant,
    Formula,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Term,
    Variable,
)
from .parser import ParseError


class ParserMode(ABC):
    """Abstract base class for parser modes."""

    @abstractmethod
    def can_parse_predicate_star(self) -> bool:
        """Whether P* syntax is allowed."""
        pass

    @abstractmethod
    def can_parse_negated_predicate(self) -> bool:
        """Whether ¬P(x) syntax is allowed."""
        pass

    @abstractmethod
    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        """How to handle ¬P(x) when encountered."""
        pass

    @abstractmethod
    def get_error_message(self, attempted_syntax: str) -> str:
        """Get helpful error message for invalid syntax."""
        pass


class TransparentMode(ParserMode):
    """Standard syntax mode, auto-translates ¬P(x) to P*(x)."""

    def can_parse_predicate_star(self) -> bool:
        return False  # P* not allowed in transparent mode

    def can_parse_negated_predicate(self) -> bool:
        return True  # ¬P(x) allowed and auto-translated

    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        """Convert ¬P(x) to BilateralPredicateFormula with is_negative=True."""
        return BilateralPredicateFormula(
            positive_name=pred.predicate_name, terms=pred.terms, is_negative=True
        )

    def get_error_message(self, attempted_syntax: str) -> str:
        if "*" in attempted_syntax:
            return (
                "Star syntax (P*) is not allowed in transparent mode. "
                "Use standard negation syntax: ¬P(x) or ~P(x)"
            )
        return f"Invalid syntax: {attempted_syntax}"


class BilateralMode(ParserMode):
    """Explicit R/R* syntax only mode."""

    def can_parse_predicate_star(self) -> bool:
        return True  # P* required for negative conditions

    def can_parse_negated_predicate(self) -> bool:
        return False  # ¬P(x) not allowed, must use P*

    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        """Should not be called in bilateral mode."""
        raise ParseError(
            f"Negated predicates (¬{pred.predicate_name}) are not allowed in "
            f"bilateral mode. Use explicit star syntax: {pred.predicate_name}*"
        )

    def get_error_message(self, attempted_syntax: str) -> str:
        if "¬" in attempted_syntax or "~" in attempted_syntax:
            pred_name = attempted_syntax.replace("¬", "").replace("~", "").strip()
            if "(" in pred_name:
                pred_name = pred_name.split("(")[0]
            return (
                f"Negated predicates are not allowed in bilateral mode. "
                f"Use explicit star syntax: {pred_name}* instead of ¬{pred_name}"
            )
        return f"Invalid syntax: {attempted_syntax}"


class MixedMode(ParserMode):
    """Both ¬P(x) and P* syntaxes allowed."""

    def can_parse_predicate_star(self) -> bool:
        return True  # P* allowed

    def can_parse_negated_predicate(self) -> bool:
        return True  # ¬P(x) also allowed

    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        """Convert ¬P(x) to BilateralPredicateFormula with is_negative=True."""
        return BilateralPredicateFormula(
            positive_name=pred.predicate_name, terms=pred.terms, is_negative=True
        )

    def get_error_message(self, attempted_syntax: str) -> str:
        return f"Invalid syntax: {attempted_syntax}"


class SyntaxMode(Enum):
    """Available syntax modes for ACrQ parser."""

    TRANSPARENT = "transparent"
    BILATERAL = "bilateral"
    MIXED = "mixed"


class ACrQParser:
    """Complete ACrQ parser with mode-aware parsing."""

    def __init__(self, input_string: str, mode: ParserMode):
        """Initialize parser with input and mode."""
        self.input_string = input_string
        self.mode = mode
        self.tokens: list[str] = []
        self.pos = 0
        self.current_token: Optional[str] = None

    def parse(self) -> Formula:
        """Parse the input string into a Formula."""
        self.tokens = self._tokenize(self.input_string)
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

        if not self.tokens:
            raise ParseError("Empty formula")

        formula = self._parse_implication()

        if self.pos < len(self.tokens):
            raise ParseError(f"Unexpected token: {self.tokens[self.pos]}")

        return formula

    def _tokenize(self, input_str: str) -> list[str]:
        """Tokenize the input string with ACrQ-aware patterns."""
        # Enhanced token patterns including star syntax
        patterns = [
            # Restricted quantifiers
            (r"\[∀\w+\s+[^\]]+\]", "FORALL"),
            (r"\[∃\w+\s+[^\]]+\]", "EXISTS"),
            (r"\[forall\s+\w+\s+[^\]]+\]", "FORALL"),  # ASCII alternative
            (r"\[exists\s+\w+\s+[^\]]+\]", "EXISTS"),  # ASCII alternative
            # Connectives
            (r"->", "IMPLIES"),
            (r"→", "IMPLIES"),
            (r"&", "AND"),
            (r"∧", "AND"),
            (r"\|", "OR"),
            (r"∨", "OR"),
            (r"~", "NOT"),
            (r"¬", "NOT"),
            # Parentheses
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            # Predicates with star
            (r"\w+\*\([^)]*\)", "PREDICATE_STAR"),  # P*(x)
            (r"\w+\*", "PREDICATE_STAR"),  # P* without args
            # Regular predicates
            (r"\w+\([^)]*\)", "PREDICATE"),  # P(x)
            # Atoms
            (r"\w+", "ATOM"),  # p or P
            # Whitespace
            (r"\s+", None),
        ]

        tokens = []
        i = 0
        while i < len(input_str):
            matched = False
            for pattern, token_type in patterns:
                regex = re.match(pattern, input_str[i:])
                if regex:
                    if token_type:  # Skip whitespace
                        tokens.append(regex.group(0))
                    i += regex.end()
                    matched = True
                    break

            if not matched:
                raise ParseError(f"Invalid character at position {i}: '{input_str[i]}'")

        return tokens

    def _advance(self) -> None:
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _parse_implication(self) -> Formula:
        """Parse implication (lowest precedence)."""
        left = self._parse_disjunction()

        while self.current_token in ["->", "→"]:
            self._advance()
            right = self._parse_implication()  # Right associative
            left = CompoundFormula("->", [left, right])

        return left

    def _parse_disjunction(self) -> Formula:
        """Parse disjunction."""
        left = self._parse_conjunction()

        while self.current_token in ["|", "∨"]:
            self._advance()
            right = self._parse_conjunction()
            left = CompoundFormula("|", [left, right])

        return left

    def _parse_conjunction(self) -> Formula:
        """Parse conjunction."""
        left = self._parse_negation()

        while self.current_token in ["&", "∧"]:
            self._advance()
            right = self._parse_negation()
            left = CompoundFormula("&", [left, right])

        return left

    def _parse_negation(self) -> Formula:
        """Parse negation."""
        if self.current_token in ["~", "¬"]:
            self._advance()

            # Check if next token is a predicate (not another negation)
            if (
                self.current_token
                and self._is_predicate_token(self.current_token)
                and self.current_token not in ["~", "¬"]
            ):
                # Parse the predicate
                pred = self._parse_predicate_as_standard()

                # Check if mode allows negated predicates
                if not self.mode.can_parse_negated_predicate():
                    raise ParseError(
                        self.mode.get_error_message(f"¬{pred.predicate_name}")
                    )

                # Transform according to mode
                return self.mode.transform_negated_predicate(pred)
            else:
                # Regular negation (including nested negations)
                inner = self._parse_negation()  # Allow nested negations
                return CompoundFormula("~", [inner])

        return self._parse_atomic()

    def _parse_atomic(self) -> Formula:
        """Parse atomic formula."""
        if not self.current_token:
            raise ParseError("Unexpected end of formula")

        # Parenthesized expression
        if self.current_token == "(":
            self._advance()
            formula = self._parse_implication()
            if self.current_token != ")":
                raise ParseError(f"Expected ')', got '{self.current_token}'")
            self._advance()
            return formula

        # Restricted quantifier
        if self.current_token.startswith("["):
            return self._parse_restricted_quantifier()

        # Predicate with star
        if self._is_predicate_star_token(self.current_token):
            if not self.mode.can_parse_predicate_star():
                # Extract predicate name for error message
                pred_name = self.current_token.split("*")[0]
                raise ParseError(self.mode.get_error_message(f"{pred_name}*"))
            return self._parse_predicate_star()

        # Regular predicate
        if self._is_predicate_token(self.current_token):
            pred = self._parse_predicate_as_standard()
            # Convert to bilateral in ACrQ mode
            return BilateralPredicateFormula(
                positive_name=pred.predicate_name, terms=pred.terms, is_negative=False
            )

        # Propositional atom
        if self.current_token and self.current_token[0].islower():
            atom = self.current_token
            self._advance()
            return PropositionalAtom(atom)

        raise ParseError(f"Unexpected token: {self.current_token}")

    def _is_predicate_token(self, token: str) -> bool:
        """Check if token is a predicate (with or without arguments)."""
        if not token:
            return False
        # Predicate starts with uppercase and may have parentheses
        return token[0].isupper()

    def _is_predicate_star_token(self, token: str) -> bool:
        """Check if token is a star predicate."""
        return bool(token and "*" in token)

    def _parse_predicate_as_standard(self) -> PredicateFormula:
        """Parse a predicate as a standard PredicateFormula."""
        token = self.current_token
        if not token:
            raise ParseError("Expected predicate")

        if "(" in token:
            # Predicate with arguments
            parts = token.split("(", 1)
            pred_name = parts[0]
            args_str = parts[1].rstrip(")")

            # Parse arguments
            terms: list[Term] = []
            if args_str:
                arg_tokens = [arg.strip() for arg in args_str.split(",")]
                for arg in arg_tokens:
                    if arg[0].isupper():
                        terms.append(Variable(arg))
                    else:
                        terms.append(Constant(arg))

            self._advance()
            return PredicateFormula(pred_name, terms)
        else:
            # Predicate without arguments
            pred_name = token
            self._advance()
            return PredicateFormula(pred_name, [])

    def _parse_predicate_star(self) -> BilateralPredicateFormula:
        """Parse a star predicate P* or P*(x)."""
        token = self.current_token
        if not token:
            raise ParseError("Expected predicate")

        if "(" in token:
            # P*(x) format
            parts = token.split("*", 1)
            pred_name = parts[0]
            args_part = parts[1]  # Should be (x)

            # Parse arguments
            args_str = args_part.strip("()")
            terms: list[Term] = []
            if args_str:
                arg_tokens = [arg.strip() for arg in args_str.split(",")]
                for arg in arg_tokens:
                    if arg[0].isupper():
                        terms.append(Variable(arg))
                    else:
                        terms.append(Constant(arg))

            self._advance()
            return BilateralPredicateFormula(
                positive_name=pred_name, terms=terms, is_negative=True
            )
        else:
            # P* format (no arguments)
            pred_name = token.rstrip("*")
            self._advance()
            return BilateralPredicateFormula(
                positive_name=pred_name, terms=[], is_negative=True
            )

    def _parse_restricted_quantifier(self) -> Formula:
        """Parse restricted quantifier [∀X P(X)]Q(X) or [∃X P(X)]Q(X)."""
        token = self.current_token
        if not token:
            raise ParseError("Expected quantifier")

        # Extract variable and restriction from quantifier token
        import re

        # Try different patterns
        patterns = [
            (r"\[(?:∀|forall\s+)(\w+)\s+([^\]]+)\]", "forall"),
            (r"\[(?:∃|exists\s+)(\w+)\s+([^\]]+)\]", "exists"),
        ]

        match = None
        quantifier_type = None
        for pattern, qtype in patterns:
            match = re.match(pattern, token)
            if match:
                quantifier_type = qtype
                break

        if not match:
            raise ParseError(f"Invalid quantifier format: {token}")

        var_name = match.group(1)
        restriction_str = match.group(2)

        # Create variable
        var = Variable(var_name)

        # Parse restriction using temporary parser
        from .parser import FormulaParser

        temp_parser = FormulaParser()
        restriction = temp_parser.parse_formula(restriction_str)

        # Advance past the quantifier token
        self._advance()

        # Parse the matrix (what follows the quantifier)
        matrix = self._parse_negation()  # This allows negation in the matrix

        # Convert to bilateral if needed
        restriction = self._convert_to_bilateral(restriction)
        matrix = self._convert_to_bilateral(matrix)

        # Create the appropriate quantifier formula
        if quantifier_type == "forall":
            return RestrictedUniversalFormula(var, restriction, matrix)
        else:
            return RestrictedExistentialFormula(var, restriction, matrix)

    def _convert_to_bilateral(self, formula: Formula) -> Formula:
        """Convert predicates in a formula to bilateral form."""
        if isinstance(formula, PredicateFormula):
            return BilateralPredicateFormula(
                positive_name=formula.predicate_name,
                terms=formula.terms,
                is_negative=False,
            )
        elif isinstance(formula, CompoundFormula):
            # Special handling for negated predicates
            if formula.connective == "~" and len(formula.subformulas) == 1:
                sub = formula.subformulas[0]
                if isinstance(sub, PredicateFormula):
                    # Convert ~P(x) to P*(x) in transparent mode
                    if self.mode.can_parse_negated_predicate():
                        return self.mode.transform_negated_predicate(sub)
                    else:
                        # In bilateral mode, this would be an error
                        raise ParseError(
                            self.mode.get_error_message(f"~{sub.predicate_name}")
                        )
            # Regular compound formula conversion
            converted_subs = [
                self._convert_to_bilateral(sub) for sub in formula.subformulas
            ]
            return CompoundFormula(formula.connective, converted_subs)
        elif isinstance(
            formula, (RestrictedExistentialFormula, RestrictedUniversalFormula)
        ):
            converted_restriction = self._convert_to_bilateral(formula.restriction)
            converted_matrix = self._convert_to_bilateral(formula.matrix)
            if isinstance(formula, RestrictedExistentialFormula):
                return RestrictedExistentialFormula(
                    formula.var, converted_restriction, converted_matrix
                )
            else:
                return RestrictedUniversalFormula(
                    formula.var, converted_restriction, converted_matrix
                )
        else:
            # Already bilateral or propositional
            return formula


def parse_acrq_formula(
    input_string: str, syntax_mode: SyntaxMode = SyntaxMode.TRANSPARENT
) -> Formula:
    """Parse formula according to syntax mode.

    Args:
        input_string: The formula string to parse
        syntax_mode: The syntax mode to use (default: TRANSPARENT)

    Returns:
        The parsed Formula object

    Raises:
        ParseError: If the formula is invalid for the given mode
    """
    # Create mode instance
    mode_map = {
        SyntaxMode.TRANSPARENT: TransparentMode(),
        SyntaxMode.BILATERAL: BilateralMode(),
        SyntaxMode.MIXED: MixedMode(),
    }

    mode = mode_map[syntax_mode]
    parser = ACrQParser(input_string, mode)
    formula = parser.parse()

    return formula
