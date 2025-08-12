# ACrQ Implementation Guide: Extending wKrQ with Analytic Containment

**Version**: 1.1.2  
**Date**: August 2025  
**Based on**: Ferguson, t.m. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic"

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Theoretical Foundation](#theoretical-foundation)
3. [Architecture Overview](#architecture-overview)
4. [Implementation Strategy](#implementation-strategy)
5. [Detailed Component Design](#detailed-component-design)
6. [Tableau Rules for ACrQ](#tableau-rules-for-acrq)
7. [External System Integration](#external-system-integration)
8. [Migration Path](#migration-path)
9. [Testing Strategy](#testing-strategy)
10. [Future Considerations](#future-considerations)

## Executive Summary

ACrQ (Analytic Containment with restricted Quantification) extends our existing wKrQ implementation with **bilateral predicates** to support paraconsistent and paracomplete reasoning. The key innovation is that each predicate R gets a corresponding R* for independent tracking of positive and negative conditions, enabling effective reasoning in the presence of knowledge gluts (conflicting information) and knowledge gaps (missing information).

### Key Features of ACrQ

1. **Bilateral Predicates**: Every predicate R has a dual R* for tracking falsity
2. **Generalized Truth Values**: Richer truth value space through R/R* combinations
3. **Bilateral Reasoning**: Enables paraconsistent handling of gluts and paracomplete handling of gaps
4. **Ferguson's Translation**: Systematic translation from wKrQ to ACrQ (Definition 17)
5. **Extended Tableau System**: New rules for bilateral predicate reasoning

### Benefits Over Pure wKrQ

- **Paraconsistent Reasoning**: Handle contradictory information (knowledge gluts) without system explosion
- **Paracomplete Reasoning**: Handle incomplete information (knowledge gaps) without assuming classical completeness
- **Fine-grained Information States**: Distinguishes between positive evidence (R), negative evidence (R*), gaps (neither), and gluts (both)
- **Robust Knowledge Representation**: Better models real-world scenarios with conflicting or incomplete data
- **Backward Compatibility**: ACrQ includes wKrQ as a special case

## Theoretical Foundation

### Bilateral Interpretation (Ferguson's Framework)

In ACrQ, each predicate symbol R gets two interpretations:

- **R**: The positive extension (when R holds)
- **R***: The negative extension (when R explicitly fails)

This creates four possible information states for any predicate instance R(a):

1. **R(a)=t, R*(a)=f**: Positive evidence only (clearly true)
2. **R(a)=f, R*(a)=t**: Negative evidence only (clearly false)
3. **R(a)=f, R*(a)=f**: No evidence either way (knowledge gap)
4. **R(a)=t, R*(a)=t**: Conflicting evidence (knowledge glut) - *paraconsistent handling required*

### Translation from wKrQ to ACrQ (Definition 17)

Ferguson provides a systematic translation τ:

```text
τ(p) = p                           (atoms unchanged)
τ(¬φ) = ¬τ(φ)                     (negation preserved)
τ(φ ∧ ψ) = τ(φ) ∧ τ(ψ)            (conjunction preserved)
τ(φ ∨ ψ) = τ(φ) ∨ τ(ψ)            (disjunction preserved)
τ(R(t₁,...,tₙ)) = R(t₁,...,tₙ)    (positive predicates unchanged)
τ(¬R(t₁,...,tₙ)) = R*(t₁,...,tₙ)  (negated predicates become R*)
```

### Transparent Translation Approach

The key innovation in our implementation is that this translation can be completely transparent to users. The system applies Ferguson's translation automatically, allowing users to:

1. **Write formulas using familiar syntax**: Users continue to write `¬Human(x)` without knowing about `Human*(x)`
2. **Get paraconsistent behavior automatically**: Knowledge gluts (`Human(x) ∧ ¬Human(x)`) are handled gracefully
3. **See intuitive results**: Models show "both (glut)" or "undefined (gap)" rather than bilateral details
4. **Access bilateral details when needed**: Advanced users can use `--show-bilateral` or direct API access

This transparency is achieved through:
- **Mode-aware parsing**: The parser translates `¬P(x)` to `P*(x)` in transparent mode
- **Dual-view results**: Results can show either user-friendly or bilateral representations
- **Progressive disclosure**: Complexity is available but not required

### Semantic Conditions

ACrQ models must satisfy:

- **Consistency**: For no R and tuple ā, both R(ā)=t and R*(ā)=t
- **Exhaustiveness** (optional): For each R and ā, either R(ā)=t or R*(ā)=t or both=f

### Tableau Closure (Lemma 5)

A branch closes in ACrQ when:

1. **Standard contradiction**: t:φ and f:φ appear
2. **Bilateral contradiction**: t:R(ā) and t:R*(ā) appear
3. **Other sign conflicts**: As in wKrQ

## Architecture Overview

### System Layers

```text
ACrQ System Architecture
├── Core Layer (Shared with wKrQ)
│   ├── Basic Formula Types
│   ├── Three-valued Semantics
│   ├── Sign System (t, f, m, n)
│   └── Core Tableau Engine
├── ACrQ Extension Layer
│   ├── Bilateral Predicate Types
│   ├── Extended Truth Values
│   ├── Translation Framework
│   └── ACrQ-specific Rules
├── CLI Layer
│   ├── Separate 'acrq' command
│   ├── Mode-aware parser (transparent/bilateral/mixed)
│   ├── Shared CLI utilities
│   └── Result formatting
└── API Layer
    ├── High-level API (transparent mode)
    ├── Low-level API (direct bilateral access)
    ├── Builder patterns
    └── Migration utilities
```text

### Component Relationships

```python
# Core components extended for ACrQ
Formula (ABC)
├── PropositionalAtom
├── CompoundFormula
├── PredicateFormula
├── BilateralPredicateFormula (NEW)
├── RestrictedExistentialFormula
└── RestrictedUniversalFormula

# Truth value system
TruthValue
├── Standard: TRUE, FALSE, UNDEFINED
└── Bilateral: BilateralTruthValue (NEW)

# Tableau system
Tableau
├── StandardTableau (wKrQ)
└── ACrQTableau (NEW)
    ├── Bilateral rule handling
    ├── Extended closure detection
    └── ACrQ model extraction
```text

## Implementation Strategy

### Phase 1: Foundation (Core Data Structures)

#### 1.1 Bilateral Predicate Formula

```python
@dataclass
class BilateralPredicateFormula(Formula):
    """A bilateral predicate R/R* for ACrQ."""
    
    positive_name: str      # R
    negative_name: str      # R*
    terms: List[Term]
    is_negative: bool = False  # True if this represents R*
    
    def __post_init__(self):
        if not self.negative_name:
            self.negative_name = f"{self.positive_name}*"
    
    def __str__(self) -> str:
        name = self.negative_name if self.is_negative else self.positive_name
        if not self.terms:
            return name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{name}({term_str})"
    
    def get_dual(self) -> "BilateralPredicateFormula":
        """Return the dual predicate (R ↔ R*)."""
        return BilateralPredicateFormula(
            positive_name=self.positive_name,
            negative_name=self.negative_name,
            terms=self.terms,
            is_negative=not self.is_negative
        )
    
    def to_standard_predicates(self) -> Tuple[PredicateFormula, PredicateFormula]:
        """Convert to pair of standard predicates (R, R*)."""
        pos = PredicateFormula(self.positive_name, self.terms)
        neg = PredicateFormula(self.negative_name, self.terms)
        return (pos, neg)
```text

#### 1.2 Bilateral Truth Value

```python
@dataclass
class BilateralTruthValue:
    """Truth value for bilateral predicates in ACrQ."""
    
    positive: TruthValue  # Value for R
    negative: TruthValue  # Value for R*
    
    def __post_init__(self):
        # Enforce consistency constraint
        if self.positive == TRUE and self.negative == TRUE:
            raise ValueError("Bilateral inconsistency: R and R* cannot both be true")
    
    def is_consistent(self) -> bool:
        """Check if the bilateral value is consistent."""
        return not (self.positive == TRUE and self.negative == TRUE)
    
    def is_gap(self) -> bool:
        """Check if neither R nor R* is true (truth value gap)."""
        return self.positive == FALSE and self.negative == FALSE
    
    def is_determinate(self) -> bool:
        """Check if exactly one of R or R* is true."""
        return (self.positive == TRUE and self.negative == FALSE) or \
               (self.positive == FALSE and self.negative == TRUE)
```text

### Phase 2: Translation Framework

#### 2.1 Formula Translator

```python
class ACrQTranslator:
    """Translates between wKrQ and ACrQ formulas."""
    
    def translate_to_acrq(self, formula: Formula) -> Formula:
        """Translate wKrQ formula to ACrQ using Ferguson's Definition 17."""
        
        if isinstance(formula, PropositionalAtom):
            # Atoms unchanged
            return formula
            
        elif isinstance(formula, CompoundFormula):
            if formula.connective == "~":
                # Handle negation of predicates specially
                sub = formula.subformulas[0]
                if isinstance(sub, PredicateFormula):
                    # ¬R(x) becomes R*(x)
                    return BilateralPredicateFormula(
                        positive_name=sub.predicate_name,
                        negative_name=f"{sub.predicate_name}*",
                        terms=sub.terms,
                        is_negative=True
                    )
                else:
                    # Recursively translate subformula
                    return Negation(self.translate_to_acrq(sub))
                    
            else:
                # Other connectives: translate subformulas
                new_subs = [self.translate_to_acrq(sub) for sub in formula.subformulas]
                return CompoundFormula(formula.connective, new_subs)
                
        elif isinstance(formula, PredicateFormula):
            # Positive predicates become bilateral with is_negative=False
            return BilateralPredicateFormula(
                positive_name=formula.predicate_name,
                negative_name=f"{formula.predicate_name}*",
                terms=formula.terms,
                is_negative=False
            )
            
        elif isinstance(formula, RestrictedQuantifierFormula):
            # Translate restriction and matrix
            new_restriction = self.translate_to_acrq(formula.restriction)
            new_matrix = self.translate_to_acrq(formula.matrix)
            return formula.__class__(formula.var, new_restriction, new_matrix)
            
        else:
            return formula
    
    def translate_from_acrq(self, formula: Formula) -> Formula:
        """Translate ACrQ formula back to wKrQ (when possible)."""
        
        if isinstance(formula, BilateralPredicateFormula):
            if formula.is_negative:
                # R*(x) becomes ¬R(x)
                pred = PredicateFormula(formula.positive_name, formula.terms)
                return Negation(pred)
            else:
                # R(x) becomes R(x)
                return PredicateFormula(formula.positive_name, formula.terms)
                
        elif isinstance(formula, CompoundFormula):
            # Recursively translate subformulas
            new_subs = [self.translate_from_acrq(sub) for sub in formula.subformulas]
            return CompoundFormula(formula.connective, new_subs)
            
        else:
            return formula
```text

### Phase 3: Extended Tableau Engine

#### 3.1 ACrQ-Specific Tableau

```python
class ACrQTableau(Tableau):
    """Extended tableau for ACrQ with bilateral predicate support."""
    
    def __init__(self, initial_formulas: List[SignedFormula]):
        super().__init__(initial_formulas)
        self.logic_system = "ACrQ"
        self.bilateral_pairs: Dict[str, str] = {}  # Maps R to R*
        
        # Identify bilateral predicates in initial formulas
        self._identify_bilateral_predicates(initial_formulas)
    
    def _identify_bilateral_predicates(self, formulas: List[SignedFormula]):
        """Identify and register bilateral predicate pairs."""
        for sf in formulas:
            self._extract_bilateral_pairs(sf.formula)
    
    def _extract_bilateral_pairs(self, formula: Formula):
        """Extract bilateral predicate pairs from a formula."""
        if isinstance(formula, BilateralPredicateFormula):
            self.bilateral_pairs[formula.positive_name] = formula.negative_name
            self.bilateral_pairs[formula.negative_name] = formula.positive_name
        elif isinstance(formula, CompoundFormula):
            for sub in formula.subformulas:
                self._extract_bilateral_pairs(sub)
        elif hasattr(formula, 'restriction') and hasattr(formula, 'matrix'):
            self._extract_bilateral_pairs(formula.restriction)
            self._extract_bilateral_pairs(formula.matrix)
    
    def _check_bilateral_contradiction(self, branch: Branch, new_formula: SignedFormula) -> bool:
        """Check for bilateral contradictions (Lemma 5)."""
        
        # Standard contradiction check
        if super()._check_contradiction(new_formula):
            return True
        
        # Check for bilateral contradiction: t:R(a) and t:R*(a)
        if new_formula.sign == t and isinstance(new_formula.formula, PredicateFormula):
            pred_name = new_formula.formula.predicate_name
            
            # Check if this is part of a bilateral pair
            if pred_name in self.bilateral_pairs:
                dual_name = self.bilateral_pairs[pred_name]
                
                # Look for t:R*(a) if we have t:R(a) (or vice versa)
                for node in branch.nodes:
                    if (node.formula.sign == t and 
                        isinstance(node.formula.formula, PredicateFormula) and
                        node.formula.formula.predicate_name == dual_name and
                        node.formula.formula.terms == new_formula.formula.terms):
                        
                        branch.closure_reason = f"Bilateral contradiction: {pred_name} and {dual_name}"
                        return True
        
        return False
```text

#### 3.2 ACrQ-Specific Rules

```python
def _get_acrq_rules(self, signed_formula: SignedFormula, branch: Branch) -> Optional[RuleInfo]:
    """Get ACrQ-specific tableau rules."""
    
    formula = signed_formula.formula
    sign = signed_formula.sign
    
    # Handle bilateral predicates
    if isinstance(formula, BilateralPredicateFormula):
        pos_pred, neg_pred = formula.to_standard_predicates()
        
        if sign == t:
            if formula.is_negative:
                # t: R*(x) means R(x) is false and R*(x) is true
                conclusions = [
                    [SignedFormula(f, pos_pred), SignedFormula(t, neg_pred)]
                ]
                return RuleInfo("t-BilateralNeg", RuleType.ALPHA, 1, 2, conclusions)
            else:
                # t: R(x) means R(x) is true and R*(x) is false
                conclusions = [
                    [SignedFormula(t, pos_pred), SignedFormula(f, neg_pred)]
                ]
                return RuleInfo("t-BilateralPos", RuleType.ALPHA, 1, 2, conclusions)
                
        elif sign == f:
            if formula.is_negative:
                # f: R*(x) branches: either R(x) is true or both undefined
                conclusions = [
                    [SignedFormula(t, pos_pred)],
                    [SignedFormula(n, pos_pred), SignedFormula(n, neg_pred)]
                ]
                return RuleInfo("f-BilateralNeg", RuleType.BETA, 10, 3, conclusions)
            else:
                # f: R(x) branches: either R*(x) is true or both undefined
                conclusions = [
                    [SignedFormula(t, neg_pred)],
                    [SignedFormula(n, pos_pred), SignedFormula(n, neg_pred)]
                ]
                return RuleInfo("f-BilateralPos", RuleType.BETA, 10, 3, conclusions)
                
        elif sign == m:
            # m: R(x) means R(x) can be true or false (but not undefined)
            # This requires considering R* appropriately
            if formula.is_negative:
                conclusions = [
                    [SignedFormula(m, neg_pred)],
                    [SignedFormula(f, pos_pred), SignedFormula(f, neg_pred)]
                ]
            else:
                conclusions = [
                    [SignedFormula(m, pos_pred)],
                    [SignedFormula(f, pos_pred), SignedFormula(f, neg_pred)]
                ]
            return RuleInfo(f"m-Bilateral{'Neg' if formula.is_negative else 'Pos'}", 
                          RuleType.BETA, 20, 3, conclusions)
                          
        elif sign == n:
            # n: R(x) means R(x) is undefined
            # In bilateral interpretation, this typically means gap (both false)
            conclusions = [
                [SignedFormula(f, pos_pred), SignedFormula(f, neg_pred)]
            ]
            return RuleInfo(f"n-Bilateral{'Neg' if formula.is_negative else 'Pos'}", 
                          RuleType.ALPHA, 5, 2, conclusions)
    
    # Handle negation of bilateral predicates
    elif isinstance(formula, CompoundFormula) and formula.connective == "~":
        sub = formula.subformulas[0]
        if isinstance(sub, BilateralPredicateFormula):
            # Negation swaps the bilateral predicate
            dual = sub.get_dual()
            conclusions = [[SignedFormula(sign, dual)]]
            return RuleInfo("Bilateral-Negation", RuleType.ALPHA, 0, 1, conclusions)
    
    return None
```text

### Phase 4: Model Extraction

#### 4.1 ACrQ Model Structure

```python
@dataclass
class ACrQModel(Model):
    """Model for ACrQ with bilateral predicate support."""
    
    bilateral_valuations: Dict[str, BilateralTruthValue]
    
    def __init__(self, branch: Branch, bilateral_pairs: Dict[str, str]):
        """Extract model from an open branch."""
        
        # Group predicates by their base name
        predicate_groups: Dict[str, Dict[str, TruthValue]] = defaultdict(dict)
        
        for node in branch.nodes:
            if isinstance(node.formula.formula, PredicateFormula):
                pred = node.formula.formula
                key = str(pred)
                
                # Determine truth value from sign
                if node.formula.sign == t:
                    value = TRUE
                elif node.formula.sign == f:
                    value = FALSE
                elif node.formula.sign == n:
                    value = UNDEFINED
                else:  # m sign
                    value = TRUE  # Could also be FALSE
                
                predicate_groups[pred.predicate_name][key] = value
        
        # Build bilateral valuations
        self.bilateral_valuations = {}
        processed = set()
        
        for pred_name, values in predicate_groups.items():
            if pred_name in processed:
                continue
                
            # Find the bilateral pair
            if pred_name in bilateral_pairs:
                dual_name = bilateral_pairs[pred_name]
                processed.add(pred_name)
                processed.add(dual_name)
                
                # Get values for both predicates
                for pred_instance in values:
                    # Extract the terms from the predicate instance
                    base_key = pred_instance.replace(pred_name, "").strip("()")
                    
                    pos_val = values.get(f"{pred_name}({base_key})", UNDEFINED)
                    neg_val = predicate_groups.get(dual_name, {}).get(f"{dual_name}({base_key})", UNDEFINED)
                    
                    # Create bilateral truth value
                    try:
                        bilateral_val = BilateralTruthValue(pos_val, neg_val)
                        self.bilateral_valuations[f"{pred_name}({base_key})"] = bilateral_val
                    except ValueError:
                        # Inconsistent - this shouldn't happen in an open branch
                        pass
        
        # Create standard valuations for compatibility
        standard_vals = {}
        for key, bilateral_val in self.bilateral_valuations.items():
            standard_vals[key] = bilateral_val.positive
            # Also add R* valuations
            base = key.split("(")[0]
            if base in bilateral_pairs:
                dual_key = key.replace(base, bilateral_pairs[base])
                standard_vals[dual_key] = bilateral_val.negative
        
        super().__init__(standard_vals, {})
```text

### Phase 5: CLI and API Integration

#### 5.1 Separate CLI Command

The ACrQ implementation will have its own `acrq` command-line tool, separate from `wkrq`:

```toml
# pyproject.toml
[project.scripts]
wkrq = "wkrq.cli:main"
acrq = "wkrq.acrq_cli:main"  # New separate command
```

#### CLI Architecture

```python
# src/wkrq/acrq_cli.py
from enum import Enum
import argparse
from .cli_common import add_common_arguments, format_result

class SyntaxMode(Enum):
    TRANSPARENT = "transparent"  # Default: ¬P(x) syntax
    BILATERAL = "bilateral"      # Explicit: P*(x) syntax  
    MIXED = "mixed"             # Both syntaxes allowed

def main():
    parser = argparse.ArgumentParser(
        description='ACrQ: Analytic Containment with restricted Quantification'
    )
    
    # Global syntax mode flag
    parser.add_argument(
        '--mode', 
        type=SyntaxMode,
        choices=list(SyntaxMode),
        default=SyntaxMode.TRANSPARENT,
        help='Formula syntax mode (default: transparent)'
    )
    
    parser.add_argument(
        '--show-bilateral',
        action='store_true',
        help='Show bilateral valuations in output (regardless of input mode)'
    )
    
    # Common arguments
    add_common_arguments(parser)
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command')
    
    # Satisfiability
    sat_parser = subparsers.add_parser('satisfiable')
    sat_parser.add_argument('formula', help='Formula to check')
    
    args = parser.parse_args()
    
    # Parse based on mode
    formula = parse_formula_with_mode(args.formula, args.mode)
    # ... rest of implementation
```

#### Usage Examples by Mode

**Transparent Mode (Default)**:
```bash
# Users write standard formulas - no R/R* visible
$ acrq satisfiable "Human(x) ∧ ¬Human(x)"
Formula is satisfiable
Model:
  Human(x) = both (glut)

# System internally translates ¬Human(x) to Human*(x)
```

**Bilateral Mode**:
```bash
# Users must write R/R* explicitly
$ acrq --mode bilateral satisfiable "Human(x) ∧ Human*(x)"
Formula is satisfiable
Bilateral Model:
  Human(x): pos=true, neg=true

# Negation not allowed in bilateral mode
$ acrq --mode bilateral satisfiable "¬Human(x)"
Error: Negation of predicates not allowed in bilateral mode. Use Human*(x) instead.
```

**Mixed Mode**:
```bash
# Accepts both syntaxes
$ acrq --mode mixed satisfiable "Human(x) ∧ ¬Robot(x) ∧ Alien*(x)"
Formula is satisfiable
Model:
  Human(x) = true
  Robot(x) = false  
  Alien(x) = false
```

#### 5.2 Mode-Aware Parser

The parser must handle different syntax modes appropriately:

```python
# src/wkrq/acrq_parser.py
from abc import ABC, abstractmethod

class ParserMode(ABC):
    """Abstract base for parser modes."""
    
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

class TransparentMode(ParserMode):
    """Standard syntax, auto-translates ¬P(x) to P*(x)."""
    
    def can_parse_predicate_star(self) -> bool:
        return False  # P* not allowed in transparent mode
    
    def can_parse_negated_predicate(self) -> bool:
        return True  # ¬P(x) is allowed and auto-translated
    
    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        # Auto-translate to bilateral
        return BilateralPredicateFormula(
            positive_name=pred.predicate_name,
            negative_name=f"{pred.predicate_name}*",
            terms=pred.terms,
            is_negative=True
        )

class BilateralMode(ParserMode):
    """Explicit R/R* syntax only."""
    
    def can_parse_predicate_star(self) -> bool:
        return True  # P* is required
    
    def can_parse_negated_predicate(self) -> bool:
        return False  # ¬P(x) not allowed - must use P*(x)
    
    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        raise ParseError(
            f"Negation of predicates not allowed in bilateral mode. "
            f"Use {pred.predicate_name}*(...) instead of ¬{pred.predicate_name}(...)"
        )

class MixedMode(ParserMode):
    """Accepts both syntaxes."""
    
    def can_parse_predicate_star(self) -> bool:
        return True  # P* allowed
    
    def can_parse_negated_predicate(self) -> bool:
        return True  # ¬P(x) also allowed
    
    def transform_negated_predicate(self, pred: PredicateFormula) -> Formula:
        # Same as transparent mode
        return BilateralPredicateFormula(
            positive_name=pred.predicate_name,
            negative_name=f"{pred.predicate_name}*",
            terms=pred.terms,
            is_negative=True
        )
```

#### Extended Parser Implementation

```python
class ACrQParser(Parser):
    """Parser that supports multiple syntax modes."""
    
    def __init__(self, input_string: str, mode: ParserMode):
        super().__init__(input_string)
        self.mode = mode
        
    def parse_atomic(self) -> Formula:
        """Parse atomic formula with mode awareness."""
        
        if self.current_token == '~' or self.current_token == '¬':
            # Negation
            self.consume_any(['~', '¬'])
            
            # Peek ahead to see if it's a predicate
            if self.is_predicate_start():
                if not self.mode.can_parse_negated_predicate():
                    predicate_name = self.peek_predicate_name()
                    raise ParseError(
                        f"Negation of predicate '{predicate_name}' not allowed "
                        f"in {self.mode.__class__.__name__}. "
                        f"Use {predicate_name}*(...) instead."
                    )
                
                # Parse the predicate
                pred = self.parse_predicate_formula()
                
                # Transform according to mode
                return self.mode.transform_negated_predicate(pred)
            else:
                # Negation of complex formula
                sub = self.parse_atomic()
                return Negation(sub)
                
        elif self.is_predicate_start():
            return self.parse_predicate_with_star()
            
        # ... other cases
    
    def parse_predicate_with_star(self) -> Formula:
        """Parse predicate that might have * suffix."""
        
        name = self.parse_identifier()
        
        # Check for star
        has_star = False
        if self.current_token == '*':
            if not self.mode.can_parse_predicate_star():
                raise ParseError(
                    f"Bilateral predicate syntax '{name}*' not allowed "
                    f"in {self.mode.__class__.__name__}. "
                    f"Use ¬{name}(...) instead."
                )
            self.consume('*')
            has_star = True
        
        # Parse terms
        terms = self.parse_terms() if self.current_token == '(' else []
        
        # Create appropriate formula based on mode
        if has_star:
            # Explicit bilateral negative
            return BilateralPredicateFormula(
                positive_name=name,
                negative_name=f"{name}*",
                terms=terms,
                is_negative=True
            )
        else:
            # In transparent mode, return standard predicate for later translation
            if isinstance(self.mode, TransparentMode):
                return PredicateFormula(name, terms)
            else:
                # In other modes, create bilateral predicate
                return BilateralPredicateFormula(
                    positive_name=name,
                    negative_name=f"{name}*",
                    terms=terms,
                    is_negative=False
                )
```

#### 5.3 Dual-Mode Programmatic API

The programmatic API supports both transparent usage (hiding R/R* complexity) and direct bilateral access:

##### High-Level API (Transparent Mode)

```python
# src/wkrq/acrq/api.py
from wkrq import parse
from wkrq.acrq import solve, entails, valid

# Users write standard formulas - no R/R* visible
formula = parse("Human(socrates) ∧ ¬Human(socrates)")

# ACrQ handles gluts gracefully
result = solve(formula)
print(result.satisfiable)  # True (not contradiction in ACrQ!)
print(result.model)  # {"Human(socrates)": "both (glut)"}

# Paraconsistent behavior - no explosion
entails(
    ["P(a)", "¬P(a)"],  # Contradictory premises
    "Q(b)"              # Unrelated conclusion
)  # Returns False (no explosion)
```

##### Low-Level API (Direct Bilateral Access)

```python
from wkrq.acrq.formula import BilateralPredicateFormula, Conjunction
from wkrq.acrq.tableau import ACrQTableau
from wkrq.acrq.semantics import BilateralTruthValue, TRUE, FALSE

# Direct bilateral predicate construction
human_pos = BilateralPredicateFormula(
    positive_name="Human",
    negative_name="Human*", 
    terms=[Constant("socrates")],
    is_negative=False
)

human_neg = BilateralPredicateFormula(
    positive_name="Human",
    negative_name="Human*",
    terms=[Constant("socrates")],
    is_negative=True  
)

# Create glut directly
glut = Conjunction(human_pos, human_neg)

# Direct tableau construction
tableau = ACrQTableau([SignedFormula(t, glut)])
result = tableau.construct()

# Access bilateral valuations directly
for pred, bilateral_val in result.model.bilateral_valuations.items():
    print(f"{pred}: pos={bilateral_val.positive}, neg={bilateral_val.negative}")
```

##### API Functions with Mode Support

```python
def solve(formula: Union[str, Formula], 
         show_bilateral: bool = False) -> ACrQResult:
    """Solve using ACrQ with transparent translation."""
    if isinstance(formula, str):
        formula = parse(formula)
    
    # Automatic translation happens here
    acrq_formula = TransparentTranslator().translate(formula)
    
    # Use bilateral machinery internally
    tableau = ACrQTableau([SignedFormula(t, acrq_formula)])
    result = tableau.construct()
    
    # Return user-friendly result by default
    if not show_bilateral:
        return UserFriendlyACrQResult(result)
    else:
        return result  # Full bilateral details

# Direct bilateral access
class BilateralAPI:
    """Low-level API for direct bilateral predicate manipulation."""
    
    @staticmethod
    def create_glut(predicate: str, *terms) -> Formula:
        """Create P(terms) ∧ P*(terms)."""
        
    @staticmethod  
    def create_gap(predicate: str, *terms) -> Formula:
        """Create ¬P(terms) ∧ ¬P*(terms)."""
        
    @staticmethod
    def from_bilateral_valuation(
        predicate: str, 
        terms: List[Term],
        positive: TruthValue,
        negative: TruthValue
    ) -> Formula:
        """Create formula from explicit bilateral valuation."""
```

##### Result Objects with Dual Views

```python
@dataclass
class ACrQResult:
    """Result that supports both transparent and bilateral views."""
    
    satisfiable: bool
    _bilateral_model: Optional[ACrQModel]
    
    @property
    def model(self) -> Dict[str, str]:
        """User-friendly model (transparent view)."""
        if not self._bilateral_model:
            return {}
            
        result = {}
        for pred, bilateral in self._bilateral_model.bilateral_valuations.items():
            if pred.endswith('*'):
                continue
                
            if bilateral.positive == TRUE and bilateral.negative == FALSE:
                result[pred] = "true"
            elif bilateral.positive == FALSE and bilateral.negative == TRUE:
                result[pred] = "false"
            elif bilateral.is_gap():
                result[pred] = "undefined (gap)"
            elif bilateral.positive == TRUE and bilateral.negative == TRUE:
                result[pred] = "both (glut)"
                
        return result
    
    @property
    def bilateral_model(self) -> Optional[ACrQModel]:
        """Direct access to bilateral valuations."""
        return self._bilateral_model
```

```python
def solve_acrq(formula: Formula, sign: Sign = t, 
               system: Optional[LogicalSystem] = None) -> TableauResult:
    """Solve a formula using the appropriate logical system."""
    
    # Auto-detect system if not specified
    if system is None:
        system = SystemSelector.detect_system([formula])
    
    # Translate if needed
    if system == LogicalSystem.ACRQ:
        translator = ACrQTranslator()
        formula = translator.translate_to_acrq(formula)
        
        # Use ACrQ tableau
        signed_formula = SignedFormula(sign, formula)
        tableau = ACrQTableau([signed_formula])
    else:
        # Use standard wKrQ tableau
        signed_formula = SignedFormula(sign, formula)
        tableau = Tableau([signed_formula])
    
    return tableau.construct()

def entails_acrq(premises: List[Formula], conclusion: Formula,
                 system: Optional[LogicalSystem] = None) -> bool:
    """Check entailment in the appropriate logical system."""
    
    all_formulas = premises + [conclusion]
    
    # Auto-detect system
    if system is None:
        system = SystemSelector.detect_system(all_formulas)
    
    # Translate if needed
    if system == LogicalSystem.ACRQ:
        translator = ACrQTranslator()
        premises = [translator.translate_to_acrq(p) for p in premises]
        conclusion = translator.translate_to_acrq(conclusion)
    
    # Standard entailment check
    from .formula import Conjunction, Negation
    
    if not premises:
        return valid(conclusion)
    
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)
    
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    result = solve_acrq(test_formula, t, system)
    
    return not result.satisfiable
```text

## Tableau Rules for ACrQ

### Bilateral Predicate Rules

#### True Sign Rules

```text
t: R(a)                     t: R*(a)
───────                     ────────
t: R(a)                     f: R(a)
f: R*(a)                    t: R*(a)
```text

#### False Sign Rules

```text
f: R(a)                     f: R*(a)
───────────────             ───────────────
t: R*(a) │ n: R(a)         t: R(a) │ n: R(a)
         │ n: R*(a)                │ n: R*(a)
```text

#### m Sign Rules (Meaningful)

```text
m: R(a)
─────────────────
m: R(a) │ f: R(a)
        │ f: R*(a)
```text

#### n Sign Rules (Neither/Undefined)

```text
n: R(a)
───────
f: R(a)
f: R*(a)
```text

### Negation with Bilateral Predicates

```text
t: ¬R(a)        f: ¬R(a)        m: ¬R(a)        n: ¬R(a)
────────        ────────        ────────        ────────
t: R*(a)        f: R*(a)        m: R*(a)        n: R*(a)
```text

### Closure Conditions (Extended)

A branch closes when:

1. **Standard contradiction**: `t: φ` and `f: φ` appear
2. **Bilateral contradiction**: `t: R(a)` and `t: R*(a)` appear
3. **Sign contradiction**: Any formula appears with incompatible signs

## External System Integration

The ACrQ tableau system supports integration with external systems that provide bilateral valuations for ground predicate expressions. When the tableau adds a node with a signed atomic formula to a branch, it can query external systems to discover additional bilateral information about the predicates involved.

### Integration Architecture

#### Hook Points in Tableau Construction

When the tableau adds a node with a **signed atomic formula** (like `t:Human(socrates)` or `f:Mortal*(john)`), the system:

1. **Detects Ground Atomic Formula**: Checks if the formula is a ground predicate (no variables)
2. **Queries External Systems**: Calls registered bilateral valuation providers
3. **Integrates Results**: Adds discovered bilateral information as new nodes to the branch
4. **Continues Tableau**: Proceeds with normal rule application

#### External System Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Set
from enum import Enum

class QueryStatus(Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class BilateralQueryResult:
    predicate_name: str
    terms: List[str]
    positive_evidence: Optional[TruthValue] = None
    negative_evidence: Optional[TruthValue] = None
    confidence: float = 1.0
    source: str = "unknown"
    status: QueryStatus = QueryStatus.SUCCESS
    metadata: Dict[str, any] = None
    
    def is_consistent(self) -> bool:
        """Check if bilateral valuation is consistent (not both TRUE)."""
        return not (self.positive_evidence == TRUE and self.negative_evidence == TRUE)
    
    def get_signed_formulas(self) -> List[SignedFormula]:
        """Convert result to signed formulas for tableau integration."""
        formulas = []
        pred = PredicateFormula(self.predicate_name, [Constant(t) for t in self.terms])
        pred_star = PredicateFormula(f"{self.predicate_name}*", [Constant(t) for t in self.terms])
        
        if self.positive_evidence == TRUE:
            formulas.append(SignedFormula(t, pred))
        elif self.positive_evidence == FALSE:
            formulas.append(SignedFormula(f, pred))
        elif self.positive_evidence == UNDEFINED:
            formulas.append(SignedFormula(n, pred))
            
        if self.negative_evidence == TRUE:
            formulas.append(SignedFormula(t, pred_star))
        elif self.negative_evidence == FALSE:
            formulas.append(SignedFormula(f, pred_star))
        elif self.negative_evidence == UNDEFINED:
            formulas.append(SignedFormula(n, pred_star))
            
        return formulas

class BilateralValuationProvider(ABC):
    """Abstract interface for external bilateral valuation systems."""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority  # Lower numbers = higher priority
        self.enabled = True
        
    @abstractmethod
    def query_bilateral(self, predicate_name: str, terms: List[str]) -> BilateralQueryResult:
        """Query external system for bilateral valuation."""
        pass
    
    @abstractmethod
    def can_handle(self, predicate_name: str) -> bool:
        """Check if this provider can handle the given predicate."""
        pass
    
    def get_supported_predicates(self) -> Set[str]:
        """Return set of predicates this provider supports."""
        return set()
    
    def initialize(self) -> bool:
        """Initialize the external system connection."""
        return True
    
    def cleanup(self) -> None:
        """Clean up external system resources."""
        pass
```text

### Provider Registry and Management

```python
class BilateralProviderRegistry:
    """Registry for managing bilateral valuation providers."""
    
    def __init__(self):
        self.providers: List[BilateralValuationProvider] = []
        self.cache: Dict[str, BilateralQueryResult] = {}
        self.cache_timeout: int = 300  # 5 minutes
        self.cache_timestamps: Dict[str, float] = {}
        
    def register(self, provider: BilateralValuationProvider) -> None:
        """Register a bilateral valuation provider."""
        if provider.initialize():
            self.providers.append(provider)
            # Sort by priority (lower numbers first)
            self.providers.sort(key=lambda p: p.priority)
        else:
            raise RuntimeError(f"Failed to initialize provider: {provider.name}")
    
    def query(self, predicate_name: str, terms: List[str]) -> Optional[BilateralQueryResult]:
        """Query all applicable providers for bilateral valuation."""
        cache_key = f"{predicate_name}({','.join(terms)})"
        
        # Check cache first
        if self._is_cached_valid(cache_key):
            return self.cache[cache_key]
        
        # Query providers in priority order
        for provider in self.providers:
            if not provider.enabled or not provider.can_handle(predicate_name):
                continue
                
            try:
                result = provider.query_bilateral(predicate_name, terms)
                if result.status == QueryStatus.SUCCESS:
                    # Cache successful results
                    self.cache[cache_key] = result
                    self.cache_timestamps[cache_key] = time.time()
                    return result
            except Exception as e:
                # Log error but continue with other providers
                continue
        
        return None
```text

### ACrQ Tableau Integration

```python
class ExternalIntegratedACrQTableau(ACrQTableau):
    """ACrQ tableau with external bilateral valuation integration."""
    
    def __init__(self, initial_formulas: List[SignedFormula]):
        super().__init__(initial_formulas)
        self.provider_registry = BilateralProviderRegistry()
        self.queried_predicates: Set[str] = set()  # Track what we've queried
        self.external_discoveries: List[SignedFormula] = []  # Track external additions
        
    def register_provider(self, provider: BilateralValuationProvider) -> None:
        """Register an external bilateral valuation provider."""
        self.provider_registry.register(provider)
    
    def _add_node_to_branch(self, branch: Branch, signed_formula: SignedFormula) -> bool:
        """Override to integrate external queries when adding ground atomic formulas."""
        
        # Add the node normally first
        node_added = super()._add_node_to_branch(branch, signed_formula)
        
        if not node_added:
            return False
        
        # Check if this is a ground atomic formula we should query about
        if self._should_query_external(signed_formula):
            external_results = self._query_external_systems(signed_formula)
            
            # Add discovered bilateral information to the branch
            for external_formula in external_results:
                if not self._formula_already_on_branch(branch, external_formula):
                    # Recursively add external discoveries
                    self._add_node_to_branch(branch, external_formula)
                    self.external_discoveries.append(external_formula)
        
        return True
    
    def _should_query_external(self, signed_formula: SignedFormula) -> bool:
        """Determine if we should query external systems for this formula."""
        formula = signed_formula.formula
        
        # Only query ground atomic predicates
        if not isinstance(formula, PredicateFormula):
            return False
        
        # Check if all terms are constants (ground)
        if not all(isinstance(term, Constant) for term in formula.terms):
            return False
        
        # Don't query bilateral predicates (R*) - they're handled by positive queries
        if formula.predicate_name.endswith('*'):
            return False
        
        # Don't query the same predicate instance twice
        predicate_key = f"{formula.predicate_name}({','.join(str(t) for t in formula.terms)})"
        if predicate_key in self.queried_predicates:
            return False
        
        return True
    
    def _query_external_systems(self, signed_formula: SignedFormula) -> List[SignedFormula]:
        """Query external systems and return signed formulas to add."""
        formula = signed_formula.formula
        predicate_name = formula.predicate_name
        terms = [str(term) for term in formula.terms]
        
        # Mark as queried
        predicate_key = f"{predicate_name}({','.join(terms)})"
        self.queried_predicates.add(predicate_key)
        
        # Query external systems
        result = self.provider_registry.query(predicate_name, terms)
        
        if result is None or result.status != QueryStatus.SUCCESS:
            return []
        
        # Convert result to signed formulas
        external_formulas = result.get_signed_formulas()
        
        # Filter out formulas that contradict existing knowledge
        filtered_formulas = []
        for ext_formula in external_formulas:
            if not self._contradicts_existing_knowledge(ext_formula):
                filtered_formulas.append(ext_formula)
        
        return filtered_formulas
```text

### Concrete Provider Examples

#### Database Provider

```python
class DatabaseBilateralProvider(BilateralValuationProvider):
    """Provider that queries a database for bilateral valuations."""
    
    def __init__(self, connection_string: str, priority: int = 50):
        super().__init__("database", priority)
        self.connection_string = connection_string
        self.connection = None
        
    def initialize(self) -> bool:
        try:
            # Initialize database connection
            # self.connection = create_connection(self.connection_string)
            return True
        except Exception:
            return False
    
    def can_handle(self, predicate_name: str) -> bool:
        # Check if predicate exists in database schema
        return True  # Simplified for example
    
    def query_bilateral(self, predicate_name: str, terms: List[str]) -> BilateralQueryResult:
        try:
            # Query database for positive and negative evidence
            # Example queries:
            # positive_result = self.connection.execute(
            #     f"SELECT value FROM {predicate_name} WHERE terms = ?", terms)
            # negative_result = self.connection.execute(
            #     f"SELECT value FROM {predicate_name}_neg WHERE terms = ?", terms)
            
            return BilateralQueryResult(
                predicate_name=predicate_name,
                terms=terms,
                positive_evidence=TRUE,
                negative_evidence=FALSE,
                confidence=0.9,
                source="database"
            )
        except Exception as e:
            return BilateralQueryResult(
                predicate_name=predicate_name,
                terms=terms,
                status=QueryStatus.ERROR,
                source="database",
                metadata={"error": str(e)}
            )
```text

#### Web API Provider

```python
class WebAPIBilateralProvider(BilateralValuationProvider):
    """Provider that queries a web API for bilateral valuations."""
    
    def __init__(self, api_endpoint: str, api_key: str = None, priority: int = 75):
        super().__init__("web_api", priority)
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.session = None
        
    def initialize(self) -> bool:
        try:
            import requests
            self.session = requests.Session()
            if self.api_key:
                self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
            return True
        except ImportError:
            return False
    
    def can_handle(self, predicate_name: str) -> bool:
        # Could check API capabilities endpoint
        return True
    
    def query_bilateral(self, predicate_name: str, terms: List[str]) -> BilateralQueryResult:
        try:
            response = self.session.post(
                f"{self.api_endpoint}/bilateral_query",
                json={
                    "predicate": predicate_name,
                    "terms": terms
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return BilateralQueryResult(
                    predicate_name=predicate_name,
                    terms=terms,
                    positive_evidence=self._parse_truth_value(data.get("positive")),
                    negative_evidence=self._parse_truth_value(data.get("negative")),
                    confidence=data.get("confidence", 1.0),
                    source="web_api"
                )
            else:
                return BilateralQueryResult(
                    predicate_name=predicate_name,
                    terms=terms,
                    status=QueryStatus.ERROR,
                    source="web_api"
                )
        except Exception as e:
            return BilateralQueryResult(
                predicate_name=predicate_name,
                terms=terms,
                status=QueryStatus.TIMEOUT if "timeout" in str(e).lower() else QueryStatus.ERROR,
                source="web_api"
            )
    
    def _parse_truth_value(self, value: str) -> Optional[TruthValue]:
        mapping = {"true": TRUE, "false": FALSE, "undefined": UNDEFINED}
        return mapping.get(value.lower()) if value else None
```text

### Usage Example

```python
def example_external_integration():
    """Example of using ACrQ with external bilateral valuation providers."""
    
    # Create tableau with external integration
    tableau = ExternalIntegratedACrQTableau([])
    
    # Register external providers
    db_provider = DatabaseBilateralProvider("sqlite:///knowledge.db", priority=10)
    api_provider = WebAPIBilateralProvider("https://api.example.com", priority=20)
    
    tableau.register_provider(db_provider)
    tableau.register_provider(api_provider)
    
    # Solve with external integration
    human_socrates = SignedFormula(t, PredicateFormula("Human", [Constant("socrates")]))
    result = tableau.solve([human_socrates])
    
    # External systems might have provided additional information:
    # - Human(socrates) = TRUE, Human*(socrates) = FALSE
    # - Mortal(socrates) = TRUE (if Human implies Mortal in external system)
    # - etc.
    
    print(f"External discoveries: {len(tableau.external_discoveries)}")
    return result
```text

### Key Design Features

1. **Pluggable Architecture**: Easy to add new external system types
2. **Priority-Based Querying**: Higher priority systems are queried first
3. **Caching**: Avoids repeated queries for the same predicates
4. **Error Handling**: Graceful fallback when external systems fail
5. **Conflict Resolution**: Framework for handling contradictory external information
6. **Performance**: Queries are triggered only for ground atomic formulas
7. **Integration Transparency**: External discoveries are tracked separately

This external integration capability significantly enhances ACrQ's practical utility by allowing it to leverage existing knowledge bases, APIs, and databases to provide bilateral valuations for predicates during tableau construction.

## Migration Path

### Phase 1: Non-Breaking Extension (Current wKrQ Preserved)

1. Add bilateral predicate classes alongside existing predicates
2. Extend formula hierarchy without modifying existing classes
3. Create ACrQTableau as subclass of Tableau
4. Add new API functions (solve_acrq, entails_acrq) without changing existing ones

### Phase 2: Unified System

1. Add system parameter to existing API functions
2. Auto-detect when ACrQ is needed based on formula content
3. Provide translation utilities for converting between systems
4. Update documentation with ACrQ examples

### Phase 3: Full Integration

1. Refactor Tableau to support pluggable rule systems
2. Create unified model extraction supporting both systems
3. Optimize shared components for both wKrQ and ACrQ
4. Add configuration for default system selection

## Testing Strategy

### Unit Tests

```python
class TestBilateralPredicates:
    """Test bilateral predicate functionality."""
    
    def test_bilateral_creation(self):
        """Test creating bilateral predicates."""
        pred = BilateralPredicateFormula("R", "R*", [Constant("a")])
        assert str(pred) == "R(a)"
        assert str(pred.get_dual()) == "R*(a)"
    
    def test_bilateral_consistency(self):
        """Test bilateral truth value consistency."""
        # This should raise an error
        with pytest.raises(ValueError):
            BilateralTruthValue(TRUE, TRUE)
    
    def test_bilateral_contradiction_detection(self):
        """Test that t:R(a) and t:R*(a) close a branch."""
        r_a = PredicateFormula("R", [Constant("a")])
        r_star_a = PredicateFormula("R*", [Constant("a")])
        
        tableau = ACrQTableau([
            SignedFormula(t, r_a),
            SignedFormula(t, r_star_a)
        ])
        
        result = tableau.construct()
        assert not result.satisfiable
```text

### Integration Tests

```python
class TestACrQReasoning:
    """Test ACrQ reasoning capabilities."""
    
    def test_paraconsistent_reasoning(self):
        """Test reasoning with knowledge gluts."""
        # Test that the system can handle conflicting information
        # without explosion (paraconsistent behavior)
        pass
    
    def test_paracomplete_reasoning(self):
        """Test reasoning with knowledge gaps."""
        # Test that the system can handle missing information
        # without assuming classical completeness
        pass
    
    def test_translation_round_trip(self):
        """Test translating between wKrQ and ACrQ."""
        translator = ACrQTranslator()
        
        # Original wKrQ formula: ¬R(a)
        original = Negation(PredicateFormula("R", [Constant("a")]))
        
        # Translate to ACrQ: R*(a)
        acrq = translator.translate_to_acrq(original)
        assert isinstance(acrq, BilateralPredicateFormula)
        assert acrq.is_negative
        
        # Translate back: ¬R(a)
        back = translator.translate_from_acrq(acrq)
        assert back == original
```text

### Validation Tests

```python
class TestFergusonACrQExamples:
    """Test examples from Ferguson 2021 paper."""
    
    def test_definition_17_translation(self):
        """Test Ferguson's Definition 17 translation examples."""
        # Test specific examples from the paper
        pass
    
    def test_lemma_5_closure(self):
        """Test Lemma 5 closure conditions."""
        # Test that branches close appropriately
        pass
    
    def test_lemma_6_reduction(self):
        """Test Lemma 6 showing ACrQ reduces to AC."""
        # Test the reduction property
        pass
```text

## Future Considerations

### Performance Optimizations

1. **Bilateral Index**: Maintain index of R/R* pairs for O(1) contradiction detection
2. **Rule Caching**: Cache applicable rules for bilateral predicates
3. **Lazy Translation**: Only translate formulas when needed
4. **Parallel Branches**: Process bilateral branches in parallel

### Extensions

1. **SrQ Support**: Add system for S¹ᵢₐ with intentional contexts
2. **Hybrid Reasoning**: Allow mixing wKrQ and ACrQ in same proof
3. **Glut/Gap Analysis**: Analyze information conflicts and gaps in knowledge bases
4. **Explanation Generation**: Explain reasoning paths through incomplete or conflicting information

### Research Applications

1. **Belief Revision**: Model belief systems with conflicting or incomplete information
2. **Knowledge Representation**: Handle real-world data with gaps and inconsistencies
3. **Natural Language**: Model uncertain or contradictory linguistic information
4. **AI Safety**: Reason robustly when facing incomplete or conflicting evidence

## Conclusion

The ACrQ extension provides a principled way to add paraconsistent and paracomplete reasoning to our wKrQ implementation while maintaining backward compatibility. The bilateral predicate approach elegantly handles both knowledge gluts and gaps, enabling robust reasoning in real-world scenarios with incomplete or conflicting information while preserving the computational efficiency of our tableau system.

### Key Implementation Decisions

1. **Separate CLI Command**: The `acrq` command is distinct from `wkrq`, following Unix philosophy and avoiding confusion
2. **Transparent Translation**: Users can write familiar syntax while getting ACrQ's advanced reasoning capabilities
3. **Mode Flexibility**: Three syntax modes (transparent/bilateral/mixed) accommodate different user expertise levels
4. **Dual-API Design**: Both high-level (transparent) and low-level (bilateral) programmatic interfaces
5. **Progressive Disclosure**: Complexity is available when needed but hidden by default

### Benefits of This Approach

- **Zero Learning Curve**: Users can start using ACrQ immediately with existing formula syntax
- **Gradual Adoption**: Organizations can migrate from wKrQ to ACrQ incrementally
- **Research Friendly**: Direct bilateral access supports academic work and experimentation
- **Production Ready**: Transparent mode provides a clean, intuitive interface for applications
- **Future Proof**: Architecture supports additional logical systems (SrQ, etc.)

The phased implementation strategy ensures we can incrementally add ACrQ features without disrupting existing functionality, making this a low-risk, high-reward enhancement to the wKrQ system.
