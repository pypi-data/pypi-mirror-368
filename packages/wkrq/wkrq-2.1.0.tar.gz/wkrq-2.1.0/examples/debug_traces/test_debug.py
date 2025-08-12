#!/usr/bin/env python3
"""Debug script to test the quantifier fix."""

from wkrq import parse, entails

# Test the basic case
premise = parse("[exists X A(X)]B(X)")
conclusion = parse("[forall Y A(Y)]B(Y)")

print("Testing: [∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)")
print("This should be invalid...")

try:
    result = entails([premise], conclusion)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()