"""
wKrQ formula parser.

Parses string representations of wKrQ formulas including restricted quantifiers.
Supports turnstile notation for inference testing.
"""

import re
from dataclasses import dataclass
from typing import Optional, Union

from .formula import (
    Conjunction,
    Constant,
    Disjunction,
    Formula,
    Implication,
    Negation,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Term,
    Variable,
)


@dataclass
class Inference:
    """Represents an inference with premises and conclusion."""

    premises: list[Formula]
    conclusion: Formula

    def to_formula(self) -> Formula:
        """Convert inference to formula for satisfiability testing."""
        # Test if (P1 & P2 & ... & Pn) & ~Q is satisfiable
        if not self.premises:
            return Negation(self.conclusion)

        # Combine all premises
        combined = self.premises[0]
        for p in self.premises[1:]:
            combined = Conjunction(combined, p)

        # Return premises & ~conclusion
        return Conjunction(combined, Negation(self.conclusion))

    def __str__(self) -> str:
        premises_str = ", ".join(str(p) for p in self.premises)
        return f"{premises_str} |- {self.conclusion}"


class ParseError(Exception):
    """Error during formula parsing."""

    pass


class FormulaParser:
    """Parser for wKrQ formulas."""

    def __init__(self) -> None:
        self.tokens: list[str] = []
        self.pos: int = 0
        self.constants: set[str] = set()
        self.variables: set[str] = set()

    def parse(self, input_str: str) -> Union[Formula, Inference]:
        """Parse a formula or inference string."""
        # Check for turnstile notation
        if "|-" in input_str:
            return self.parse_inference(input_str)
        else:
            return self.parse_formula(input_str)

    def parse_inference(self, input_str: str) -> Inference:
        """Parse an inference in the form 'P1, P2, ..., Pn |- Q'."""
        parts = input_str.split("|-")
        if len(parts) != 2:
            raise ParseError(f"Invalid inference format: {input_str}")

        # Parse premises
        premises_str = parts[0].strip()
        premises = []
        if premises_str:
            # Split premises by commas, but respect bracket nesting
            premise_parts = self._split_by_top_level_commas(premises_str)
            for premise_str in premise_parts:
                premise = self.parse_formula(premise_str.strip())
                premises.append(premise)

        # Parse conclusion
        conclusion_str = parts[1].strip()
        conclusion = self.parse_formula(conclusion_str)

        return Inference(premises, conclusion)

    def _split_by_top_level_commas(self, input_str: str) -> list[str]:
        """Split a string by commas, but only at top level (not inside brackets)."""
        parts = []
        current_part = []
        depth = 0

        for char in input_str:
            if char in "([":
                depth += 1
                current_part.append(char)
            elif char in ")]":
                depth -= 1
                current_part.append(char)
            elif char == "," and depth == 0:
                parts.append("".join(current_part))
                current_part = []
            else:
                current_part.append(char)

        # Add the last part
        if current_part:
            parts.append("".join(current_part))

        return parts

    def parse_formula(self, input_str: str) -> Formula:
        """Parse a single formula."""
        self.tokens = self._tokenize(input_str)
        self.pos = 0

        if not self.tokens:
            raise ParseError("Empty formula")

        formula = self._parse_implication()

        if self.pos < len(self.tokens):
            raise ParseError(f"Unexpected token: {self.tokens[self.pos]}")

        return formula

    def _tokenize(self, input_str: str) -> list[str]:
        """Tokenize the input string."""
        # Token patterns - order matters! More specific patterns first
        patterns = [
            # Quantifiers must come first to match before individual brackets
            (r"\[∀\w+\s+[^\]]+\]", "FORALL"),  # Restricted universal (Unicode)
            (r"\[∃\w+\s+[^\]]+\]", "EXISTS"),  # Restricted existential (Unicode)
            (r"\[forall\s+\w+\s+[^\]]+\]", "FORALL"),  # ASCII forall
            (r"\[exists\s+\w+\s+[^\]]+\]", "EXISTS"),  # ASCII exists
            (r"->", "IMPLIES"),
            (r"→", "IMPLIES"),
            (r"&", "AND"),
            (r"∧", "AND"),
            (r"\|", "OR"),
            (r"∨", "OR"),
            (r"~", "NOT"),
            (r"¬", "NOT"),
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r"\[", "LBRACKET"),  # For cases where quantifier pattern doesn't match
            (r"\]", "RBRACKET"),  # For cases where quantifier pattern doesn't match
            (r"\w+\([^)]*\)", "PREDICATE"),  # Predicate with arguments
            (r"\w+", "ATOM"),  # Propositional atom or constant
            (r"\s+", None),  # Whitespace (ignored)
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

    def _current_token(self) -> Optional[str]:
        """Get current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume_token(self) -> str:
        """Consume and return current token."""
        if self.pos >= len(self.tokens):
            raise ParseError("Unexpected end of formula")
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _parse_implication(self) -> Formula:
        """Parse implication (lowest precedence)."""
        left = self._parse_disjunction()

        while self._current_token() in ["->", "→"]:
            self._consume_token()
            right = self._parse_implication()  # Right associative
            left = Implication(left, right)

        return left

    def _parse_disjunction(self) -> Formula:
        """Parse disjunction."""
        left = self._parse_conjunction()

        while self._current_token() in ["|", "∨", "("]:
            self._consume_token()
            right = self._parse_conjunction()
            left = Disjunction(left, right)

        return left

    def _parse_conjunction(self) -> Formula:
        """Parse conjunction."""
        left = self._parse_negation()

        while self._current_token() in ["&", "∧"]:
            self._consume_token()
            right = self._parse_negation()
            left = Conjunction(left, right)

        return left

    def _parse_negation(self) -> Formula:
        """Parse negation (highest precedence for operators)."""
        if self._current_token() in ["~", "¬"]:
            self._consume_token()
            formula = self._parse_negation()
            return Negation(formula)

        return self._parse_atomic()

    def _parse_atomic(self) -> Formula:
        """Parse atomic formula or parenthesized formula."""
        token = self._current_token()

        if not token:
            raise ParseError("Expected formula")

        # Parenthesized formula
        if token == "(":
            self._consume_token()
            formula = self._parse_implication()
            if self._consume_token() != ")":
                raise ParseError("Expected closing parenthesis")
            return formula

        # Restricted quantifiers
        if token.startswith("[∀") or token.startswith("[forall"):
            return self._parse_restricted_universal()

        if token.startswith("[∃") or token.startswith("[exists"):
            return self._parse_restricted_existential()

        # Predicate
        if "(" in token and token.endswith(")"):
            return self._parse_predicate()

        # Propositional atom
        atom_name = self._consume_token()
        return PropositionalAtom(atom_name)

    def _parse_predicate(self) -> PredicateFormula:
        """Parse a predicate formula like P(x) or R(a,b)."""
        token = self._consume_token()

        # Extract predicate name and arguments
        match = re.match(r"(\w+)\(([^)]*)\)", token)
        if not match:
            raise ParseError(f"Invalid predicate format: {token}")

        pred_name = match.group(1)
        args_str = match.group(2)

        # Parse arguments
        terms: list[Term] = []
        if args_str:
            for arg in args_str.split(","):
                arg = arg.strip()
                if arg.isupper() or arg in self.variables:
                    # Variable (uppercase or already seen)
                    self.variables.add(arg)
                    terms.append(Variable(arg))
                else:
                    # Constant (lowercase or already seen)
                    self.constants.add(arg)
                    terms.append(Constant(arg))

        return PredicateFormula(pred_name, terms)

    def _parse_restricted_universal(self) -> RestrictedUniversalFormula:
        """Parse [∀X P(X)]Q(X)."""
        token = self._consume_token()

        # Extract components using regex
        match = re.match(r"\[(?:∀|forall\s+)(\w+)\s+([^\]]+)\]", token)
        if not match:
            raise ParseError(f"Invalid restricted universal format: {token}")

        var_name = match.group(1)
        restriction_str = match.group(2)

        # Create variable
        var = Variable(var_name)
        self.variables.add(var_name)

        # Parse restriction
        temp_parser = FormulaParser()
        temp_parser.variables = self.variables.copy()
        temp_parser.constants = self.constants.copy()
        restriction = temp_parser.parse_formula(restriction_str)

        # Parse matrix (what follows the quantifier)
        matrix = self._parse_atomic()

        return RestrictedUniversalFormula(var, restriction, matrix)

    def _parse_restricted_existential(self) -> RestrictedExistentialFormula:
        """Parse [∃X P(X)]Q(X)."""
        token = self._consume_token()

        # Extract components using regex
        match = re.match(r"\[(?:∃|exists\s+)(\w+)\s+([^\]]+)\]", token)
        if not match:
            raise ParseError(f"Invalid restricted existential format: {token}")

        var_name = match.group(1)
        restriction_str = match.group(2)

        # Create variable
        var = Variable(var_name)
        self.variables.add(var_name)

        # Parse restriction
        temp_parser = FormulaParser()
        temp_parser.variables = self.variables.copy()
        temp_parser.constants = self.constants.copy()
        restriction = temp_parser.parse_formula(restriction_str)

        # Parse matrix
        matrix = self._parse_atomic()

        return RestrictedExistentialFormula(var, restriction, matrix)


# Convenience functions
def parse(input_str: str) -> Formula:
    """Parse a formula string."""
    parser = FormulaParser()
    result = parser.parse(input_str)
    if isinstance(result, Inference):
        raise ParseError(
            "Expected formula but got inference. Use parse_inference() instead."
        )
    return result


def parse_inference(input_str: str) -> Inference:
    """Parse an inference string."""
    parser = FormulaParser()
    result = parser.parse(input_str)
    if isinstance(result, Formula):
        raise ParseError("Expected inference but got formula. Use parse() instead.")
    return result
