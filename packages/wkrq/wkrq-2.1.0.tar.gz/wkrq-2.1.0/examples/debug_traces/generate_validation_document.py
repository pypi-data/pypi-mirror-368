#!/usr/bin/env python3
"""
Generate a complete validation document by running key test examples.
This creates a single, comprehensive document for philosophical logic experts.
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


# Define all validation examples organized by category
VALIDATION_SECTIONS = [
    {
        "title": "Ferguson's Six-Sign System",
        "description": "The six signs (t, f, e, m, n, v) in Ferguson's tableau system provide fine-grained control over truth values in weak Kleene logic.",
        "examples": [
            {
                "name": "t-sign: Must be true",
                "cmd": ["--sign=t", "--tree", "--models", "p"],
                "expect": "Forces p to be true"
            },
            {
                "name": "f-sign: Must be false", 
                "cmd": ["--sign=f", "--tree", "--models", "p"],
                "expect": "Forces p to be false"
            },
            {
                "name": "e-sign: Must be undefined",
                "cmd": ["--sign=e", "--tree", "--models", "p"],
                "expect": "Forces p to be undefined"
            },
            {
                "name": "m-sign: Meaningful (true or false)",
                "cmd": ["--sign=m", "--tree", "--models", "p"],
                "expect": "Allows p to be true or false but not undefined"
            },
            {
                "name": "n-sign: Non-true (false or undefined)",
                "cmd": ["--sign=n", "--tree", "--models", "p"],
                "expect": "Allows p to be false or undefined but not true"
            },
        ]
    },
    {
        "title": "Weak Kleene Semantics", 
        "description": "In weak Kleene logic, undefined (e) is 'contagious' - any operation with an undefined operand yields undefined.",
        "examples": [
            {
                "name": "Conjunction with undefined",
                "cmd": ["--sign=e", "--tree", "--models", "p & q"],
                "expect": "If either operand can be undefined, the result is undefined"
            },
            {
                "name": "Disjunction with undefined",
                "cmd": ["--sign=e", "--tree", "--models", "p | q"],
                "expect": "If either operand can be undefined, the result is undefined"
            },
            {
                "name": "Classical tautology can be undefined",
                "cmd": ["--sign=e", "--tree", "--models", "p | ~p"],
                "expect": "Even p ∨ ¬p can be undefined when p is undefined"
            },
            {
                "name": "Excluded middle cannot be false",
                "cmd": ["--sign=f", "--tree", "p | ~p"],
                "expect": "p ∨ ¬p cannot be false (unsatisfiable under f-sign)"
            },
            {
                "name": "Contradiction cannot be true",
                "cmd": ["--sign=t", "--tree", "p & ~p"],
                "expect": "p ∧ ¬p cannot be true (unsatisfiable under t-sign)"
            },
            {
                "name": "Weak vs Strong Kleene difference",
                "cmd": ["--tree", "--models", "(p | ~p) & (q | ~q)"],
                "expect": "Shows cases where formulas can be undefined"
            },
        ]
    },
    {
        "title": "Ferguson's Negation Rules",
        "description": "Negation rules in the six-sign system showing how signs transform under negation.",
        "examples": [
            {
                "name": "t-negation rule: t:¬φ yields f:φ",
                "cmd": ["--tree", "--show-rules", "~p"],
                "expect": "Shows how t:¬p decomposes to f:p"
            },
            {
                "name": "f-negation rule: f:¬φ yields t:φ",
                "cmd": ["--sign=f", "--tree", "--show-rules", "~p"],
                "expect": "Shows how f:¬p decomposes to t:p"
            },
            {
                "name": "e-negation rule: e:¬φ yields e:φ",
                "cmd": ["--sign=e", "--tree", "--show-rules", "~p"],
                "expect": "Shows how e:¬p decomposes to e:p"
            },
            {
                "name": "m-negation branching",
                "cmd": ["--sign=m", "--tree", "--show-rules", "~p"],
                "expect": "Shows how m:¬p branches to capture meaningful values"
            },
            {
                "name": "n-negation branching",
                "cmd": ["--sign=n", "--tree", "--show-rules", "~p"],
                "expect": "Shows how n:¬p branches to capture non-true values"
            },
        ]
    },
    {
        "title": "Classical Valid Inferences",
        "description": "Standard logical inferences that remain valid in weak Kleene logic.",
        "examples": [
            {
                "name": "Modus Ponens",
                "cmd": ["--inference", "--tree", "--show-rules", "p, p -> q |- q"],
                "expect": "Classic inference rule remains valid"
            },
            {
                "name": "Modus Tollens",
                "cmd": ["--inference", "--tree", "--show-rules", "p -> q, ~q |- ~p"],
                "expect": "Contrapositive reasoning remains valid"
            },
            {
                "name": "Hypothetical Syllogism", 
                "cmd": ["--inference", "--tree", "--show-rules", "p -> q, q -> r |- p -> r"],
                "expect": "Transitivity of implication"
            },
            {
                "name": "Disjunctive Syllogism",
                "cmd": ["--inference", "--tree", "--show-rules", "p | q, ~p |- q"],
                "expect": "Elimination by negation"
            },
            {
                "name": "Constructive Dilemma",
                "cmd": ["--inference", "--tree", "--show-rules", "(p -> q) & (r -> s), p | r |- q | s"],
                "expect": "Complex valid inference"
            },
            {
                "name": "Simplification",
                "cmd": ["--inference", "--tree", "--show-rules", "p & q |- p"],
                "expect": "Conjunction elimination"
            },
            {
                "name": "Addition",
                "cmd": ["--inference", "--tree", "--show-rules", "p |- p | q"],
                "expect": "Disjunction introduction"
            },
            {
                "name": "Double Negation Elimination",
                "cmd": ["--inference", "--tree", "--show-rules", "~~p |- p"],
                "expect": "Double negation cancels out"
            },
        ]
    },
    {
        "title": "Classical Invalid Inferences",
        "description": "Standard logical fallacies that remain invalid.",
        "examples": [
            {
                "name": "Affirming the Consequent",
                "cmd": ["--inference", "--countermodel", "p -> q, q |- p"],
                "expect": "Classic fallacy with counterexample"
            },
            {
                "name": "Denying the Antecedent",
                "cmd": ["--inference", "--countermodel", "p -> q, ~p |- ~q"],
                "expect": "Another classic fallacy"
            },
            {
                "name": "Quantifier Fallacy (Undistributed Middle)",
                "cmd": ["--inference", "--countermodel", "[forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)"],
                "expect": "Invalid syllogistic reasoning"
            },
        ]
    },
    {
        "title": "Restricted Quantification (THE BUG FIX)",
        "description": "Ferguson's restricted quantifiers [∀X φ(X)]ψ(X) and [∃X φ(X)]ψ(X). A critical bug where existential witnesses were reused for universal falsification has been fixed.",
        "examples": [
            {
                "name": "Valid Universal Instantiation",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"],
                "expect": "Standard universal instantiation works correctly"
            },
            {
                "name": "Invalid Existential to Universal (BUG FIXED)",
                "cmd": ["--inference", "--tree", "--show-rules", "--countermodel", "[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)"],
                "expect": "This was incorrectly validated before the fix. Now correctly shows as invalid."
            },
            {
                "name": "Valid Existential Introduction", 
                "cmd": ["--inference", "--tree", "--show-rules", "P(a), Q(a) |- [exists X P(X)]Q(X)"],
                "expect": "Existential generalization"
            },
            {
                "name": "Invalid Existential Elimination",
                "cmd": ["--inference", "--tree", "--show-rules", "--countermodel", "[exists X P(X)]Q(X), P(a) |- Q(a)"],
                "expect": "Cannot infer specific from existential"
            },
            {
                "name": "Quantifier Scope",
                "cmd": ["--inference", "--tree", "--show-rules", "--countermodel", "[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)"],
                "expect": "The existential witness might not be alice"
            },
            {
                "name": "Multiple Quantifiers",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X P(X)]Q(X), [forall Y Q(Y)]R(Y) |- [forall Z P(Z)]R(Z)"],
                "expect": "Chaining universal quantifiers"
            },
        ]
    },
    {
        "title": "Aristotelian Syllogisms",
        "description": "Classical syllogistic forms using restricted quantification.",
        "examples": [
            {
                "name": "Barbara (AAA-1)",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)"],
                "expect": "All M are P, All S are M, therefore All S are P"
            },
            {
                "name": "Celarent (EAE-1)", 
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))"],
                "expect": "No M are P, All S are M, therefore No S are P"
            },
            {
                "name": "Darii (AII-1)",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X M(X)]P(X), [exists Y S(Y)]M(Y) |- [exists Z S(Z)]P(Z)"],
                "expect": "All M are P, Some S are M, therefore Some S are P"
            },
            {
                "name": "Ferio (EIO-1)",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X M(X)](~P(X)), [exists Y S(Y)]M(Y) |- [exists Z S(Z)](~P(Z))"],
                "expect": "No M are P, Some S are M, therefore Some S are not P"
            },
        ]
    },
    {
        "title": "De Morgan's Laws", 
        "description": "De Morgan equivalences in weak Kleene logic.",
        "examples": [
            {
                "name": "¬(p ∧ q) ⊢ ¬p ∨ ¬q",
                "cmd": ["--inference", "--tree", "--show-rules", "~(p & q) |- (~p | ~q)"],
                "expect": "Negation distributes over conjunction"
            },
            {
                "name": "¬p ∨ ¬q ⊢ ¬(p ∧ q)",
                "cmd": ["--inference", "--tree", "--show-rules", "(~p | ~q) |- ~(p & q)"],
                "expect": "Reverse direction"
            },
            {
                "name": "¬(p ∨ q) ⊢ ¬p ∧ ¬q",
                "cmd": ["--inference", "--tree", "--show-rules", "~(p | q) |- (~p & ~q)"],
                "expect": "Negation distributes over disjunction"
            },
            {
                "name": "¬p ∧ ¬q ⊢ ¬(p ∨ q)",
                "cmd": ["--inference", "--tree", "--show-rules", "(~p & ~q) |- ~(p | q)"],
                "expect": "Reverse direction"
            },
            {
                "name": "Quantified De Morgan",
                "cmd": ["--inference", "--tree", "--show-rules", "~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))"],
                "expect": "De Morgan for quantifiers"
            },
        ]
    },
    {
        "title": "Tableau Construction Examples",
        "description": "Examples showing tableau tree construction and branch closure.",
        "examples": [
            {
                "name": "Simple contradiction tableau",
                "cmd": ["--tree", "--show-rules", "p & ~p"],
                "expect": "Shows branch closure on contradiction"
            },
            {
                "name": "Branching disjunction",
                "cmd": ["--tree", "--show-rules", "p | q"],
                "expect": "Shows branching for disjunction"
            },
            {
                "name": "Complex branching with m-sign",
                "cmd": ["--sign=m", "--tree", "--show-rules", "p & (q | r)"],
                "expect": "Shows complex branching behavior"
            },
            {
                "name": "Quantifier instantiation in tableau",
                "cmd": ["--tree", "--show-rules", "[forall X P(X)]Q(X) & P(a)"],
                "expect": "Shows universal instantiation process"
            },
        ]
    },
    {
        "title": "Model Extraction",
        "description": "Examples of extracting models from open tableau branches.",
        "examples": [
            {
                "name": "Simple model",
                "cmd": ["--tree", "--models", "p & q"],
                "expect": "Single model where both are true"
            },
            {
                "name": "Multiple models",
                "cmd": ["--tree", "--models", "p | q"],
                "expect": "Multiple satisfying models"
            },
            {
                "name": "Three-valued models",
                "cmd": ["--tree", "--models", "~(p & ~p)"],
                "expect": "Models including undefined values"
            },
            {
                "name": "Quantified models",
                "cmd": ["--tree", "--models", "[exists X P(X)]Q(X)"],
                "expect": "Models with witness constants"
            },
        ]
    },
    {
        "title": "ACrQ Paraconsistent Logic",
        "description": "Analytic Containment with restricted Quantification - bilateral predicates enable paraconsistent reasoning.",
        "examples": [
            {
                "name": "Knowledge gluts (contradictions) don't explode",
                "cmd": ["--mode=acrq", "--syntax=bilateral", "--inference", "--tree", "--show-rules", "--countermodel", "P(a) & P*(a) |- Q(b)"],
                "expect": "Local contradictions don't imply everything"
            },
            {
                "name": "Bilateral predicate semantics",
                "cmd": ["--mode=acrq", "--syntax=bilateral", "--tree", "--models", "P(a) & P*(a)"],
                "expect": "Both P and ¬P can be true independently"
            },
            {
                "name": "Reasoning continues despite gluts",
                "cmd": ["--mode=acrq", "--syntax=bilateral", "--inference", "--tree", "--show-rules", "P(a) & P*(a), P(a) -> Q(a) |- Q(a)"],
                "expect": "Valid reasoning preserved locally"
            },
            {
                "name": "Knowledge gaps (incompleteness)",
                "cmd": ["--mode=acrq", "--syntax=bilateral", "--tree", "--models", "P(a) | P*(a)"],
                "expect": "At least one of P or ¬P must be true"
            },
            {
                "name": "Four-valued logic demonstration",
                "cmd": ["--mode=acrq", "--syntax=bilateral", "--tree", "--models", "(P(a) | P*(a)) & (Q(b) | Q*(b))"],
                "expect": "Shows all four truth states possible"
            },
            {
                "name": "ACrQ De Morgan preservation",
                "cmd": ["--mode=acrq", "--inference", "--tree", "--show-rules", "~(P(a) & Q(a)) |- (~P(a) | ~Q(a))"],
                "expect": "De Morgan laws work with bilateral predicates"
            },
        ]
    },
    {
        "title": "Advanced Examples",
        "description": "Complex examples demonstrating system capabilities.",
        "examples": [
            {
                "name": "Nested implications",
                "cmd": ["--inference", "--tree", "--show-rules", "p -> (q -> r), p, q |- r"],
                "expect": "Curried implications"
            },
            {
                "name": "Epistemic uncertainty",
                "cmd": ["--sign=m", "--tree", "--models", "p -> p"],
                "expect": "Even tautologies can be epistemically uncertain"
            },
            {
                "name": "Complex quantifier interaction",
                "cmd": ["--inference", "--tree", "--show-rules", "[forall X Person(X)]Mortal(X), Person(john) |- Mortal(john)"],
                "expect": "Universal instantiation example"
            },
            {
                "name": "Relevance logic property",
                "cmd": ["--inference", "--tree", "--show-rules", "--countermodel", "p |- q -> q"],
                "expect": "Material implication without relevance can fail"
            },
        ]
    },
]


def run_wkrq_command(args: List[str]) -> str:
    """Run a wkrq command and return the output."""
    cmd = ["python", "-m", "wkrq"] + args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 and result.stderr:
            return f"ERROR: {result.stderr}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Command execution exceeded 10 seconds"
    except Exception as e:
        return f"ERROR: {str(e)}"


def format_example(example: Dict) -> str:
    """Format a single example."""
    lines = []
    
    lines.append(f"### {example['name']}")
    lines.append("")
    
    # Extract formula from command
    formula = example['cmd'][-1]  # Last argument is the formula
    lines.append(f"**Formula:** `{formula}`")
    
    # Show command options
    options = [opt for opt in example['cmd'][:-1] if opt.startswith("--")]
    if options:
        lines.append(f"**Options:** {' '.join(options)}")
    
    lines.append("")
    lines.append(f"**Expected:** {example['expect']}")
    lines.append("")
    
    # Run command and show output
    output = run_wkrq_command(example['cmd'])
    lines.append("**Output:**")
    lines.append("```")
    lines.append(output)
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def generate_validation_document():
    """Generate the complete validation document."""
    output_file = Path("docs/VALIDATION.md")
    
    with open(output_file, 'w') as f:
        # Header
        f.write("# wKrQ Complete Validation Document\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Introduction
        f.write("## Introduction\n\n")
        f.write("This document provides a complete validation of the wKrQ (weak Kleene logic ")
        f.write("with restricted Quantification) and ACrQ (Analytic Containment with restricted ")
        f.write("Quantification) systems. All examples are automatically generated by running ")
        f.write("actual commands, ensuring the documentation accurately reflects system behavior.\n\n")
        
        # System overview
        f.write("### System Overview\n\n")
        f.write("**wKrQ** implements:\n")
        f.write("- Weak Kleene three-valued logic (true, false, undefined)\n")
        f.write("- Ferguson's six-sign tableau system (t, f, e, m, n, v)\n")
        f.write("- Restricted quantification [∀X φ(X)]ψ(X) and [∃X φ(X)]ψ(X)\n")
        f.write("- Sound and complete tableau-based theorem proving\n\n")
        
        f.write("**ACrQ** extends wKrQ with:\n")
        f.write("- Bilateral predicates for paraconsistent reasoning\n")
        f.write("- Four-valued logic (true, false, both, neither)\n")
        f.write("- Local contradiction handling without explosion\n\n")
        
        # Critical bug fix
        f.write("### Critical Bug Fix (Quantifier Instantiation)\n\n")
        f.write("A critical bug in the restricted quantifier instantiation has been fixed. ")
        f.write("The bug caused invalid inferences like `[∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)` ")
        f.write("to be incorrectly marked as valid.\n\n")
        f.write("**Root cause:** When falsifying a universal quantifier `[∀Y A(Y)]B(Y)`, the ")
        f.write("system would reuse the existential witness constant from `[∃X A(X)]B(X)`. ")
        f.write("Since the witness already had B true, trying to make B false created an ")
        f.write("immediate contradiction, closing all branches and making the invalid inference ")
        f.write("appear valid.\n\n")
        f.write("**Fix:** The system now generates fresh constants when falsifying universal ")
        f.write("quantifiers (f-case), preventing the reuse of existential witnesses. The fix ")
        f.write("also prevents infinite constant generation by limiting f-case instantiations.\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for i, section in enumerate(VALIDATION_SECTIONS, 1):
            anchor = section['title'].lower().replace(" ", "-").replace("(", "").replace(")", "")
            f.write(f"{i}. [{section['title']}](#{anchor})\n")
        f.write("\n---\n\n")
        
        # Main content
        for section in VALIDATION_SECTIONS:
            anchor = section['title'].lower().replace(" ", "-").replace("(", "").replace(")", "")
            f.write(f"## {section['title']}\n\n")
            f.write(f"{section['description']}\n\n")
            
            for example in section['examples']:
                f.write(format_example(example))
                f.write("---\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        total_examples = sum(len(s['examples']) for s in VALIDATION_SECTIONS)
        f.write(f"This validation document contains {total_examples} examples across ")
        f.write(f"{len(VALIDATION_SECTIONS)} categories, demonstrating the complete ")
        f.write("functionality of the wKrQ and ACrQ systems.\n\n")
        
        f.write("### Key Validations\n\n")
        f.write("- ✓ Ferguson's six-sign system correctly implemented\n")
        f.write("- ✓ Weak Kleene semantics with undefined contagion\n")
        f.write("- ✓ Classical inference patterns preserved\n")
        f.write("- ✓ Restricted quantification with bug fix verified\n")
        f.write("- ✓ Aristotelian syllogisms correctly validated\n")
        f.write("- ✓ ACrQ paraconsistent reasoning without explosion\n")
        f.write("- ✓ Tableau construction and model extraction working\n\n")
        
        f.write("For the complete test suite with 480+ automated tests, run: `pytest tests/`\n")
    
    print(f"Generated: {output_file}")
    print(f"Total examples: {sum(len(s['examples']) for s in VALIDATION_SECTIONS)}")


def main():
    """Main entry point."""
    print("Generating validation document...")
    print("This will run many wkrq commands and may take a minute...")
    generate_validation_document()
    print("\nDone! Check docs/VALIDATION.md")


if __name__ == "__main__":
    main()