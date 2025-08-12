# ACrQ Development Quick Start

## 🚀 Quick Resume Commands

```bash
# 1. Check current state
cd /Users/bradleyallen/Documents/GitHub/wkrq
git status
pytest tests/test_bilateral_predicates.py -v  # Should show 16 passing tests

# 2. Create parser files
touch src/wkrq/acrq_parser.py
touch src/wkrq/acrq_translator.py
touch tests/test_acrq_parser.py
```

## 📋 Next Task: Parser Modes Implementation

### Step 1: Create ParserMode Classes
Start with `src/wkrq/acrq_parser.py`:

```python
from abc import ABC, abstractmethod

class ParserMode(ABC):
    @abstractmethod
    def can_parse_predicate_star(self) -> bool:
        pass
    
    @abstractmethod
    def can_parse_negated_predicate(self) -> bool:
        pass
```

### Step 2: Implement Three Modes
1. **TransparentMode**: ¬P(x) → P*(x) automatically
2. **BilateralMode**: Must use P*(x) explicitly  
3. **MixedMode**: Both syntaxes allowed

### Step 3: Extend Parser
Create `ACrQParser(Parser)` that uses the mode to decide how to parse.

## ✅ What's Already Done

- ✅ BilateralPredicateFormula class
- ✅ BilateralTruthValue class  
- ✅ 16 tests for bilateral predicates
- ✅ Package exports updated
- ✅ Version 1.0.9

## 📚 Key Files to Reference

1. **Design Doc**: `docs/ACrQ_IMPLEMENTATION_GUIDE.md` (lines 516-681 for parser design)
2. **Existing Parser**: `src/wkrq/parser.py` (to understand extension pattern)
3. **Bilateral Classes**: `src/wkrq/formula.py` (lines 245-338)
4. **Full State**: `ACRQ_DEVELOPMENT_STATE.md`

## 🎯 Success Criteria

When Step 2 is complete:
- `parse_acrq_formula("¬P(x)")` returns BilateralPredicateFormula with is_negative=True
- `parse_acrq_formula("P*(x)", mode=BILATERAL)` works
- `parse_acrq_formula("¬P(x)", mode=BILATERAL)` raises helpful error
- All existing tests still pass

## 💡 Quick Design Reminders

- Ferguson's translation: ¬R(x) → R*(x)
- Transparent mode is default (user-friendly)
- Parser modes control syntax acceptance
- Translation happens post-parsing in transparent mode
- Error messages should guide users to correct syntax for their mode