# Ferguson Tableau System Alignment Plan

## Executive Summary

This plan outlines a complete overhaul of the wKrQ tableau system to exactly match Ferguson's 2021 paper specification. No backward compatibility will be maintained. All tests, documentation, and examples will be migrated to the new system.

## Current State vs Ferguson's Paper Analysis

### 1. Sign System Differences

**Ferguson's Paper (Definition 9):**
- Uses 6 signs: `v`, `t`, `f`, `m`, `n`, `e`
- `v` is any element of V₃ = {t, f, e}
- `e` represents the undefined/error value
- `m` (meaningful) decorates a formula when both `t : φ` and `f : φ` are available for branching
- `n` (nontrue) decorates a formula when both `f : φ` and `e : φ` are available

**Current Implementation:**
- Uses 4 signs: `t`, `f`, `m`, `n`
- No separate `v` or `e` signs
- `t` ↔ true (must be true)
- `f` ↔ false (must be false)
- `m` ↔ {true, false} (both/meaningful)
- `n` ↔ {undefined} (neither/need not be true)

**Key Difference:** Ferguson uses `e` as a distinct sign, while our implementation treats `n` as representing undefined directly.

### 2. Tableau Rules Comparison

#### 2.1 Negation Rules

**Ferguson's Rules:**
```
v : ~φ
-----
~v : φ
```
Where ~t = f, ~f = t, ~e = e

**Current Implementation:**
- t:~φ → f:φ (correct)
- f:~φ → t:φ (correct)
- m:~φ → m:φ (differs - Ferguson would branch)
- n:~φ → n:φ (differs - should use e sign)

**Issue:** Ferguson's system would have separate rules for m and n signs that branch, while ours doesn't.

#### 2.2 Conjunction Rules

**Ferguson's Rules:**
```
v : φ ∧ ψ
---------
+ {v₀ : φ ∘ v₁ : ψ} where v₀∧v₁=v
```

**Current Implementation:**
- t:(φ ∧ ψ) → t:φ, t:ψ (correct)
- f:(φ ∧ ψ) → f:φ | f:ψ (correct branching)
- m:(φ ∧ ψ) → m:φ | m:ψ (incorrect - should consider all combinations)
- n:(φ ∧ ψ) → n:φ | n:ψ (incorrect - should consider e combinations)

**Issue:** m and n rules don't properly enumerate all truth value combinations.

#### 2.3 Disjunction Rules

Similar issues as conjunction - our m and n rules are simplified and don't capture Ferguson's full branching structure.

#### 2.4 Quantifier Rules

**Ferguson's Restricted Existential:**
```
t : [∃x φ(x)]ψ(x)
-----------------
t : φ(c) ∘ t : ψ(c)

f : [∃x φ(x)]ψ(x)
-----------------
m : φ(c) ∘ m : ψ(c) ∘ (n : φ(a) + n : ψ(a))

e : [∃x φ(x)]ψ(x)
-----------------
e : φ(a) + e : ψ(a)
```

**Current Implementation:**
- t:[∃X P(X)]Q(X) → t:P(c) ∧ t:Q(c) (correct)
- f:[∃X P(X)]Q(X) → f:P(c) | f:Q(c) (simplified - missing m/n branching)
- m/n cases not handled properly

### 3. Missing Features

1. **No `e` sign**: Ferguson explicitly uses `e` for undefined values
2. **No `v` sign**: Used as a meta-variable in rules
3. **Incomplete m/n rules**: Don't enumerate all truth value combinations
4. **Missing branch closure rules**: Ferguson's Definition 10 specifies closure when `v : φ` and `u : φ` appear where v,u ∈ V₃ are distinct

### 4. Implementation Alignment Plan

#### Phase 1: Extend Sign System
1. Add `E` sign for explicit undefined representation
2. Add `V` as a meta-sign (optional, for rule specification)
3. Update Sign class to handle 6-sign system
4. Update contradiction checking for new signs

#### Phase 2: Update Tableau Rules
1. Implement proper m/n branching rules for connectives
2. Add rules for e sign interactions
3. Update quantifier rules to match Ferguson's exactly
4. Implement proper branch closure conditions

#### Phase 3: Refactor Rule Application
1. Create rule templates that match Ferguson's notation
2. Implement truth value combination enumeration
3. Add proper handling for m and n decomposition

#### Phase 4: Testing and Validation
1. Create test cases for each Ferguson rule
2. Validate against paper's examples
3. Ensure backward compatibility where possible

### 5. Specific Code Changes Needed

1. **signs.py**:
   - Add `E = Sign("E")` for undefined
   - Add `V = Sign("V")` as meta-sign (optional)
   - Update `SIGNS` set
   - Update contradiction logic

2. **tableau.py**:
   - Rewrite `_get_applicable_rule` to match Ferguson's rules
   - Add proper m/n branching logic
   - Update branch closure conditions
   - Add e-sign specific rules

3. **semantics.py**:
   - Ensure e-sign maps to UNDEFINED correctly
   - Update truth condition mappings

4. **New file: ferguson_rules.py**:
   - Create rule templates matching paper notation
   - Implement truth value enumeration logic
   - Provide rule generation functions

### 6. Implementation Sequence

#### Step 1: Core System Changes (~50 file edits)
- Update signs.py to add e sign and change to lowercase
- Rewrite tableau.py rules (major changes to _get_applicable_rule)
- Update formula.py string representations
- Modify semantics.py sign mappings

#### Step 2: Test Suite Migration (~200 test updates)
- Update all imports from t,f,m,n to t,f,e,m,n
- Rewrite m/n tests to handle branching behavior
- Add new Ferguson exact compliance tests
- Fix all test failures from system changes

#### Step 3: Documentation Updates (~30 files)
- Update all .md files with new notation
- Rewrite all code examples
- Update all docstrings
- Create comprehensive migration notes

#### Step 4: Example and CLI Updates (~20 changes)
- Update all example files
- Modify CLI to accept new signs
- Update parser to handle lowercase signs
- Test all examples end-to-end

### 7. Validation Checklist

- [ ] All Ferguson Definition 9 rules implemented exactly
- [ ] Branch closure per Definition 10
- [ ] All tests pass with new system
- [ ] Documentation uses consistent notation
- [ ] Examples run correctly
- [ ] Paper's examples reproduce exactly

### 8. Risk Mitigation

1. **Breaking Changes**: Tag current version as "legacy" before changes
2. **User Impact**: Announce major version change (2.0.0)
3. **Testing**: Create parallel test suite during migration
4. **Documentation**: Maintain clear mapping table (old → new)

### 9. Success Criteria

The implementation is successful when:
1. Every rule in Ferguson's Definition 9 is implemented exactly as specified
2. All examples from the paper produce identical tableaux
3. The test suite validates complete Ferguson compliance
4. Documentation consistently uses Ferguson's notation throughout

### 10. Estimated Scope

- **Total file changes**: ~300 files (including tests)
- **Lines of code affected**: ~5,000-7,000 lines
- **New code required**: ~1,000 lines (new rules, tests)
- **Documentation updates**: All user-facing docs
- **Breaking change**: Complete API change (major version bump)