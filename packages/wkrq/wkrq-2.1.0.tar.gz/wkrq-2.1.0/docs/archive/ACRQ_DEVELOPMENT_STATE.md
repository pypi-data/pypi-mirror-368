# ACrQ Development State - July 30, 2025

## Current Status

### ✅ Completed: Step 1 - Core Components (Bilateral Predicates)

### 🔄 In Progress: Step 2 - Parser Modes Implementation

#### Completed:
- Basic ACrQ parser with transparent mode support
- Simple formula translation (¬P(x) → P*(x))
- Basic tests passing

#### Still To Do:
- Full parser mode infrastructure (TransparentMode, BilateralMode, MixedMode classes)
- Mode-aware parsing with proper error handling
- Star syntax (*) parsing support
- Comprehensive test suite

1. **BilateralPredicateFormula** (`src/wkrq/formula.py`)
   - Full implementation with R/R* duality
   - Integration with Formula hierarchy
   - Methods: `get_dual()`, `to_standard_predicates()`

2. **BilateralTruthValue** (`src/wkrq/semantics.py`)
   - Four information states (true/false/gap/glut)
   - Helper methods for state detection
   - User-friendly display with `to_simple_value()`

3. **Test Suite** (`tests/test_bilateral_predicates.py`)
   - 16 comprehensive tests, all passing
   - Covers all functionality of both classes

4. **Package Integration**
   - Exported in `__init__.py`
   - Version updated to 1.0.9
   - All 209 tests passing

## Next Steps: Step 2 - Parser Modes

### 2.1 Create Parser Mode Infrastructure

**File**: `src/wkrq/acrq_parser.py` (new file)

```python
from abc import ABC, abstractmethod
from typing import Optional
from .formula import Formula, PredicateFormula, BilateralPredicateFormula, Term

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
    # Implementation as designed
    
class BilateralMode(ParserMode):
    """Explicit R/R* syntax only."""
    # Implementation as designed
    
class MixedMode(ParserMode):
    """Accepts both syntaxes."""
    # Implementation as designed
```

### 2.2 Extend Parser with Mode Awareness

**File**: `src/wkrq/acrq_parser.py` (continue)

```python
from .parser import Parser

class ACrQParser(Parser):
    """Parser that supports multiple syntax modes."""
    
    def __init__(self, input_string: str, mode: ParserMode):
        super().__init__(input_string)
        self.mode = mode
    
    def parse_atomic(self) -> Formula:
        """Parse atomic formula with mode awareness."""
        # Handle ¬P(x) based on mode
        # Handle P* based on mode
        
    def parse_predicate_with_star(self) -> Formula:
        """Parse predicate that might have * suffix."""
        # Check mode.can_parse_predicate_star()
        # Create BilateralPredicateFormula as appropriate
```

### 2.3 Create Translation Framework

**File**: `src/wkrq/acrq_translator.py` (new file)

```python
class TransparentTranslator:
    """Translates formulas to ACrQ using Ferguson's Definition 17."""
    
    def translate(self, formula: Formula) -> Formula:
        """Apply transparent translation."""
        # Implement Ferguson's translation
        # ¬R(x) → BilateralPredicateFormula(R, x, is_negative=True)
```

### 2.4 Parser Factory and Integration

**File**: `src/wkrq/acrq_parser.py` (continue)

```python
from enum import Enum

class SyntaxMode(Enum):
    TRANSPARENT = "transparent"
    BILATERAL = "bilateral"
    MIXED = "mixed"

def parse_acrq_formula(
    input_string: str, 
    syntax_mode: SyntaxMode = SyntaxMode.TRANSPARENT
) -> Formula:
    """Parse formula according to syntax mode."""
    mode_map = {
        SyntaxMode.TRANSPARENt: TransparentMode(),
        SyntaxMode.BILATERAL: BilateralMode(),
        SyntaxMode.MIXED: MixedMode()
    }
    
    mode = mode_map[syntax_mode]
    parser = ACrQParser(input_string, mode)
    formula = parser.parse()
    
    # Post-processing for transparent mode
    if syntax_mode == SyntaxMode.TRANSPARENt:
        translator = TransparentTranslator()
        formula = translator.translate(formula)
    
    return formula
```

### 2.5 Create Comprehensive Tests

**File**: `tests/test_acrq_parser.py` (new file)

```python
import pytest
from wkrq.acrq_parser import parse_acrq_formula, SyntaxMode, ParseError

class TestTransparentMode:
    def test_negated_predicate_translation(self):
        """¬P(x) should become P*(x)"""
        formula = parse_acrq_formula("¬Human(x)", SyntaxMode.TRANSPARENT)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative
        
    def test_star_syntax_rejected(self):
        """P* syntax not allowed in transparent mode"""
        with pytest.raises(ParseError):
            parse_acrq_formula("Human*(x)", SyntaxMode.TRANSPARENT)

class TestBilateralMode:
    def test_star_syntax_accepted(self):
        """P* syntax required in bilateral mode"""
        formula = parse_acrq_formula("Human*(x)", SyntaxMode.BILATERAL)
        assert isinstance(formula, BilateralPredicateFormula)
        assert formula.is_negative
        
    def test_negation_rejected(self):
        """¬P(x) not allowed in bilateral mode"""
        with pytest.raises(ParseError):
            parse_acrq_formula("¬Human(x)", SyntaxMode.BILATERAL)

class TestMixedMode:
    def test_both_syntaxes_accepted(self):
        """Both ¬P(x) and P* accepted"""
        f1 = parse_acrq_formula("¬Human(x)", SyntaxMode.MIXED)
        f2 = parse_acrq_formula("Human*(x)", SyntaxMode.MIXED)
        # Both should result in same internal representation
```

## Implementation Order

1. **Create `acrq_parser.py`**
   - Start with ParserMode classes
   - Implement ACrQParser extending existing Parser
   - Add mode-specific parsing logic

2. **Create `acrq_translator.py`**
   - Implement Ferguson's Definition 17 translation
   - Handle all formula types recursively

3. **Integration**
   - Factory function for creating parsers
   - Post-processing pipeline

4. **Testing**
   - Unit tests for each mode
   - Integration tests for complex formulas
   - Error handling tests

## Key Technical Challenges

1. **Parser Extension**: Need to carefully extend existing parser without breaking it
2. **Recursive Translation**: Must handle nested formulas correctly
3. **Error Messages**: Mode-specific error messages must be helpful
4. **Unicode Support**: Handle both ¬ and ~ for negation

## File Structure After Step 2

```
src/wkrq/
├── __init__.py          (updated exports)
├── formula.py           (has BilateralPredicateFormula)
├── semantics.py         (has BilateralTruthValue)
├── parser.py            (existing parser - unchanged)
├── acrq_parser.py       (NEW - mode-aware parser)
├── acrq_translator.py   (NEW - Ferguson translation)
└── ...

tests/
├── test_bilateral_predicates.py  (completed)
├── test_acrq_parser.py          (NEW - parser tests)
└── ...
```

## Commands to Resume Development

```bash
# 1. Activate development environment
cd /Users/bradleyallen/Documents/GitHub/wkrq

# 2. Verify current state
pytest tests/test_bilateral_predicates.py -v

# 3. Create new parser files
touch src/wkrq/acrq_parser.py
touch src/wkrq/acrq_translator.py
touch tests/test_acrq_parser.py

# 4. Start implementing ParserMode classes
```

## Design Decisions Already Made

1. **Three Parser Modes**: Transparent (default), Bilateral, Mixed
2. **Transparent Mode**: User writes ¬P(x), system uses P*(x) internally
3. **Error Handling**: Mode-specific helpful error messages
4. **Post-Processing**: Translation happens after parsing in transparent mode
5. **Default Behavior**: Transparent mode is default for user-friendliness

## References

- ACrQ Implementation Guide: `docs/ACrQ_IMPLEMENTATION_GUIDE.md`
- Ferguson (2021) Definition 17 for translation rules
- Existing parser in `src/wkrq/parser.py` for extension pattern

## Next Session Starting Point

Begin with creating `src/wkrq/acrq_parser.py` and implementing the three ParserMode classes. The infrastructure is ready, and all dependencies (BilateralPredicateFormula, etc.) are in place.