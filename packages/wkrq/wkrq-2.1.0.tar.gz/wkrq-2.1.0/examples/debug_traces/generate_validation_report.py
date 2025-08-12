#!/usr/bin/env python3
"""
Generate a validation report similar to examples/validation.txt from pytest tests.
This creates a human-readable document for philosophical logic experts.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json


class ValidationExample:
    """Represents a validation example with formula and results."""
    def __init__(self, category: str, description: str, formula: str, 
                 mode: str = "wkrq", show_tree: bool = False, show_models: bool = False):
        self.category = category
        self.description = description
        self.formula = formula
        self.mode = mode
        self.show_tree = show_tree
        self.show_models = show_models
        self.result = None
        self.output = None


def extract_examples_from_tests() -> List[ValidationExample]:
    """Extract validation examples from test files."""
    examples = []
    
    # Key examples from Ferguson validation tests
    ferguson_examples = [
        # Basic sign system
        ValidationExample(
            "Ferguson Six-Sign System",
            "Sign t constrains to true",
            "p",
            show_models=True
        ),
        ValidationExample(
            "Ferguson Six-Sign System", 
            "Sign m allows both true and false",
            "p | ~p",
            show_models=True
        ),
        
        # Negation rules
        ValidationExample(
            "Ferguson Negation Rules",
            "t-negation: t:¬φ leads to f:φ",
            "~p |- q",
            show_tree=True
        ),
        
        # Weak Kleene semantics
        ValidationExample(
            "Weak Kleene Semantics",
            "Undefined is contagious in disjunction",
            "(p | q)",
            show_models=True
        ),
        ValidationExample(
            "Weak Kleene Semantics",
            "Classical tautology can be undefined",
            "p | ~p",
            show_models=True
        ),
        
        # Quantifier rules
        ValidationExample(
            "Restricted Quantifiers",
            "Universal instantiation (valid)",
            "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)",
            show_tree=True
        ),
        ValidationExample(
            "Restricted Quantifiers",
            "Existential to universal (invalid) - THE BUG WE FIXED",
            "[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)",
            show_tree=True,
            show_models=True
        ),
        
        # Classical inferences
        ValidationExample(
            "Classical Inferences",
            "Modus Ponens",
            "p, p -> q |- q"
        ),
        ValidationExample(
            "Classical Inferences",
            "Modus Tollens", 
            "p -> q, ~q |- ~p"
        ),
        ValidationExample(
            "Classical Inferences",
            "Hypothetical Syllogism",
            "p -> q, q -> r |- p -> r"
        ),
        
        # Invalid inferences
        ValidationExample(
            "Invalid Inferences",
            "Affirming the Consequent",
            "p -> q, q |- p",
            show_models=True
        ),
        ValidationExample(
            "Invalid Inferences",
            "Denying the Antecedent",
            "p -> q, ~p |- ~q",
            show_models=True
        ),
        
        # Aristotelian Syllogisms
        ValidationExample(
            "Aristotelian Syllogisms",
            "Barbara: All M are P, All S are M ⊢ All S are P",
            "[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)"
        ),
        ValidationExample(
            "Aristotelian Syllogisms",
            "Celarent: No M are P, All S are M ⊢ No S are P",
            "[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))"
        ),
        
        # De Morgan's Laws
        ValidationExample(
            "De Morgan's Laws",
            "¬(p ∧ q) ⊢ ¬p ∨ ¬q",
            "~(p & q) |- (~p | ~q)"
        ),
        ValidationExample(
            "De Morgan's Laws",
            "Quantified De Morgan (now valid after our fix)",
            "~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))"
        ),
        
        # ACrQ examples
        ValidationExample(
            "ACrQ Paraconsistent Reasoning",
            "Knowledge gluts don't explode",
            "Symptom(patient, fever) & ~Symptom(patient, fever) |- Unrelated(claim)",
            mode="acrq",
            show_models=True
        ),
        ValidationExample(
            "ACrQ Paraconsistent Reasoning",
            "Local inconsistency preserved",
            "P(a) & P*(a)",
            mode="acrq",
            show_models=True
        ),
    ]
    
    return ferguson_examples


def run_wkrq_command(formula: str, mode: str = "wkrq", 
                     show_tree: bool = False, show_models: bool = False) -> Dict:
    """Run wkrq command and capture output."""
    cmd = ["python", "-m", "wkrq"]
    
    if mode == "acrq":
        cmd.extend(["--mode=acrq"])
    
    # Check if it's an inference
    if " |- " in formula:
        cmd.extend(["--inference"])
        if show_models:
            cmd.extend(["--countermodel"])
    
    if show_tree:
        cmd.extend(["--tree", "--show-rules"])
    elif show_models:
        cmd.extend(["--models"])
    
    cmd.append(formula)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "TIMEOUT: Formula took too long to evaluate",
            "stderr": "",
            "returncode": -1
        }


def format_example(example: ValidationExample) -> str:
    """Format a single example for the report."""
    lines = []
    
    # Header
    lines.append(f"### {example.description}")
    lines.append("")
    
    # Formula
    lines.append(f"**Formula**: `{example.formula}`")
    if example.mode != "wkrq":
        lines.append(f"**Mode**: {example.mode.upper()}")
    lines.append("")
    
    # Run the command
    result = run_wkrq_command(example.formula, example.mode, 
                            example.show_tree, example.show_models)
    
    # Output
    lines.append("**Result**:")
    lines.append("```")
    lines.append(result["stdout"].strip())
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def generate_validation_report(output_file: Path):
    """Generate the validation report."""
    examples = extract_examples_from_tests()
    
    # Group by category
    categories = {}
    for ex in examples:
        if ex.category not in categories:
            categories[ex.category] = []
        categories[ex.category].append(ex)
    
    # Generate report
    with open(output_file, 'w') as f:
        f.write("# wKrQ Validation Report\n\n")
        f.write("This report demonstrates the behavior of the wKrQ system through ")
        f.write("examples extracted from the test suite. Generated for review by ")
        f.write("experts in philosophical logic.\n\n")
        
        # Note about the bug fix
        f.write("## Important Note\n\n")
        f.write("This report was generated after fixing a critical bug in the ")
        f.write("restricted quantifier instantiation. The bug caused invalid ")
        f.write("inferences like `[∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)` to be ")
        f.write("incorrectly marked as valid. This has been fixed.\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for category in categories:
            anchor = category.lower().replace(" ", "-").replace("'", "")
            f.write(f"- [{category}](#{anchor})\n")
        f.write("\n---\n\n")
        
        # Examples by category
        for category, examples in categories.items():
            anchor = category.lower().replace(" ", "-").replace("'", "")
            f.write(f"## {category}\n\n")
            
            for example in examples:
                f.write(format_example(example))
                f.write("---\n\n")


def generate_compact_reference(output_file: Path):
    """Generate a compact reference of all test formulas."""
    examples = extract_examples_from_tests()
    
    with open(output_file, 'w') as f:
        f.write("# wKrQ Test Formulas Quick Reference\n\n")
        
        current_category = None
        for ex in examples:
            if ex.category != current_category:
                current_category = ex.category
                f.write(f"\n## {current_category}\n\n")
            
            # Determine validity
            result = run_wkrq_command(ex.formula, ex.mode)
            validity = "?"
            if "✓ Valid" in result["stdout"]:
                validity = "✓"
            elif "✗ Invalid" in result["stdout"]:
                validity = "✗"
            elif "Satisfiable: True" in result["stdout"]:
                validity = "SAT"
            elif "Satisfiable: False" in result["stdout"]:
                validity = "UNSAT"
            
            f.write(f"- [{validity}] `{ex.formula}` - {ex.description}\n")


def main():
    """Main entry point."""
    import sys
    
    if "--compact" in sys.argv:
        output_file = Path("docs/test_formulas_reference.md")
        print("Generating compact reference...")
        generate_compact_reference(output_file)
    else:
        output_file = Path("docs/validation_report.md")
        print("Generating validation report...")
        generate_validation_report(output_file)
    
    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    main()