#!/usr/bin/env python3
"""
Generate a complete validation document from pytest test files.
This creates a single comprehensive document for philosophical logic experts.
"""

import subprocess
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict


class TestCase:
    """Represents a test case extracted from pytest files."""
    def __init__(self, test_class: str, test_method: str, description: str,
                 commands: List[Dict], file_path: str):
        self.test_class = test_class
        self.test_method = test_method
        self.description = description
        self.commands = commands  # List of wkrq commands with their assertions
        self.file_path = file_path
        
    def __repr__(self):
        return f"TestCase({self.test_class}::{self.test_method})"


class TestExtractor(ast.NodeVisitor):
    """Extract test cases from pytest test files."""
    
    def __init__(self, file_path: str):
        self.test_cases: List[TestCase] = []
        self.current_class = None
        self.file_path = file_path
        
    def visit_ClassDef(self, node):
        """Track current test class."""
        if node.name.startswith("Test"):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class
            
    def visit_FunctionDef(self, node):
        """Extract test information from test methods."""
        if not node.name.startswith("test_") or not self.current_class:
            return
            
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Find all wkrq commands in this test
        commands = []
        
        # Walk through the function body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                cmd_info = self._extract_wkrq_command(child)
                if cmd_info:
                    # Find assertions related to this command
                    assertions = self._find_assertions_after(node, child)
                    cmd_info['assertions'] = assertions
                    commands.append(cmd_info)
        
        if commands:
            test_case = TestCase(
                test_class=self.current_class,
                test_method=node.name,
                description=docstring.strip(),
                commands=commands,
                file_path=self.file_path
            )
            self.test_cases.append(test_case)
    
    def _extract_wkrq_command(self, call_node) -> Optional[Dict]:
        """Extract wkrq command details from a function call."""
        # Check if this is run_wkrq_command
        if isinstance(call_node.func, ast.Name) and call_node.func.id == "run_wkrq_command":
            if call_node.args and isinstance(call_node.args[0], ast.List):
                args = []
                for elt in call_node.args[0].elts:
                    if isinstance(elt, ast.Constant):
                        args.append(elt.value)
                    elif isinstance(elt, ast.Str):  # Python 3.7 compatibility
                        args.append(elt.s)
                
                # Parse the arguments
                cmd_info = self._parse_wkrq_args(args)
                if cmd_info:
                    return cmd_info
        
        return None
    
    def _parse_wkrq_args(self, args: List[str]) -> Optional[Dict]:
        """Parse wkrq command arguments."""
        info = {
            'mode': 'wkrq',
            'sign': None,
            'formula': None,
            'inference': False,
            'tree': False,
            'models': False,
            'countermodel': False,
            'show_rules': False,
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--mode=acrq":
                info['mode'] = 'acrq'
            elif arg.startswith("--sign="):
                info['sign'] = arg.split('=')[1]
            elif arg == "--inference":
                info['inference'] = True
            elif arg == "--tree":
                info['tree'] = True
            elif arg == "--models":
                info['models'] = True
            elif arg == "--countermodel":
                info['countermodel'] = True
            elif arg == "--show-rules":
                info['show_rules'] = True
            elif not arg.startswith("--"):
                # This should be the formula
                info['formula'] = arg
            i += 1
        
        return info if info['formula'] else None
    
    def _find_assertions_after(self, func_node, call_node) -> List[str]:
        """Find assertions that check the result of a command."""
        assertions = []
        
        # This is simplified - in reality we'd need more sophisticated AST analysis
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert) and isinstance(node.test, ast.Compare):
                for comparator in node.test.comparators:
                    if isinstance(node.test.left, ast.Constant):
                        assertion_text = node.test.left.value
                        if any(marker in assertion_text for marker in 
                               ["✓ Valid", "✗ Invalid", "Satisfiable:", "Models"]):
                            assertions.append(assertion_text)
                    elif isinstance(node.test.left, ast.Str):  # Python 3.7
                        assertion_text = node.test.left.s
                        if any(marker in assertion_text for marker in 
                               ["✓ Valid", "✗ Invalid", "Satisfiable:", "Models"]):
                            assertions.append(assertion_text)
        
        return assertions


def extract_all_tests() -> Dict[str, List[TestCase]]:
    """Extract all test cases from test files."""
    test_files = [
        "tests/test_ferguson_validation.py",
        "tests/test_ferguson_compliance.py", 
        "tests/test_ferguson_exact.py",
        "tests/test_quantifier_bug.py",
        "tests/test_wkrq_basic.py",
        "tests/test_first_order.py",
        "tests/test_cli_quantifiers.py",
        "tests/test_acrq_integration.py",
        "tests/test_acrq_ferguson.py",
        "tests/test_bilateral_predicates.py",
    ]
    
    all_tests = defaultdict(list)
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"Extracting from {test_file}...")
            with open(test_file, 'r') as f:
                try:
                    tree = ast.parse(f.read())
                    extractor = TestExtractor(test_file)
                    extractor.visit(tree)
                    
                    for test_case in extractor.test_cases:
                        category = categorize_test(test_case)
                        all_tests[category].append(test_case)
                except Exception as e:
                    print(f"  Error parsing {test_file}: {e}")
    
    return dict(all_tests)


def categorize_test(test_case: TestCase) -> str:
    """Categorize a test based on its class name and content."""
    class_name = test_case.test_class
    
    # Map test classes to categories
    if "Ferguson" in class_name:
        if "SixSign" in class_name:
            return "Ferguson's Six-Sign System"
        elif "Negation" in class_name:
            return "Ferguson's Negation Rules"
        elif "Conjunction" in class_name or "Disjunction" in class_name:
            return "Ferguson's Connective Rules"
        elif "Quantifier" in class_name:
            return "Ferguson's Quantifier Rules"
        else:
            return "Ferguson's Tableau System"
    elif "Kleene" in class_name:
        return "Weak Kleene Semantics"
    elif "Classical" in class_name:
        return "Classical Logic Patterns"
    elif "Quantifier" in class_name:
        return "Quantifier Logic"
    elif "Syllogism" in class_name:
        return "Aristotelian Syllogisms"
    elif "Morgan" in class_name:
        return "De Morgan's Laws"
    elif "ACrQ" in class_name or "Bilateral" in class_name:
        return "ACrQ Paraconsistent Logic"
    elif "Model" in class_name:
        return "Model Theory"
    elif "Tableau" in class_name:
        return "Tableau Construction"
    else:
        return "Miscellaneous Tests"


def run_wkrq_command(cmd_info: Dict) -> str:
    """Run a wkrq command and return the output."""
    cmd = ["python", "-m", "wkrq"]
    
    # Build command line
    if cmd_info['mode'] == 'acrq':
        cmd.append("--mode=acrq")
    
    if cmd_info['sign']:
        cmd.append(f"--sign={cmd_info['sign']}")
    
    if cmd_info['inference']:
        cmd.append("--inference")
    
    if cmd_info['tree']:
        cmd.append("--tree")
    
    if cmd_info['show_rules']:
        cmd.append("--show-rules")
    
    if cmd_info['models']:
        cmd.append("--models")
    
    if cmd_info['countermodel']:
        cmd.append("--countermodel")
    
    cmd.append(cmd_info['formula'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Command execution exceeded 5 seconds"
    except Exception as e:
        return f"ERROR: {str(e)}"


def format_test_case(test_case: TestCase) -> str:
    """Format a test case for the validation document."""
    lines = []
    
    # Test header
    clean_name = test_case.test_method.replace("test_", "").replace("_", " ").title()
    if test_case.description:
        lines.append(f"### {test_case.description}")
    else:
        lines.append(f"### {clean_name}")
    
    lines.append(f"*Test: {test_case.test_class}::{test_case.test_method}*")
    lines.append("")
    
    # Process each command in the test
    for i, cmd_info in enumerate(test_case.commands):
        if len(test_case.commands) > 1:
            lines.append(f"**Command {i+1}:**")
        
        # Show the formula
        formula = cmd_info['formula']
        lines.append(f"Formula: `{formula}`")
        
        # Show options if any
        options = []
        if cmd_info['mode'] != 'wkrq':
            options.append(f"Mode: {cmd_info['mode']}")
        if cmd_info['sign']:
            options.append(f"Sign: {cmd_info['sign']}")
        if options:
            lines.append(" | ".join(options))
        
        lines.append("")
        
        # Run the command and show output
        output = run_wkrq_command(cmd_info)
        lines.append("```")
        lines.append(output)
        lines.append("```")
        
        # Show what the test expects
        if cmd_info['assertions']:
            lines.append("")
            lines.append("*Test expects:* " + ", ".join(cmd_info['assertions']))
        
        lines.append("")
    
    return "\n".join(lines)


def generate_complete_validation_document():
    """Generate the complete validation document."""
    print("Extracting all test cases...")
    all_tests = extract_all_tests()
    
    output_file = Path("docs/COMPLETE_VALIDATION.md")
    
    with open(output_file, 'w') as f:
        # Header
        f.write("# wKrQ Complete Validation Document\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Introduction
        f.write("## Introduction\n\n")
        f.write("This document contains a complete validation of the wKrQ (weak Kleene ")
        f.write("logic with restricted Quantification) implementation. All examples are ")
        f.write("automatically extracted from the pytest test suite, ensuring perfect ")
        f.write("synchronization between tests and documentation.\n\n")
        
        # Bug fix note
        f.write("### Critical Bug Fix Note\n\n")
        f.write("A critical bug in the restricted quantifier instantiation has been fixed. ")
        f.write("The bug caused the system to incorrectly validate inferences like ")
        f.write("`[∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)` by reusing existential witness ")
        f.write("constants when falsifying universal quantifiers. This created spurious ")
        f.write("contradictions that made invalid inferences appear valid. The fix ensures ")
        f.write("that fresh constants are generated for f-case universal quantifiers while ")
        f.write("preventing infinite constant generation.\n\n")
        
        # Statistics
        total_tests = sum(len(tests) for tests in all_tests.values())
        total_commands = sum(len(test.commands) for tests in all_tests.values() 
                           for test in tests)
        
        f.write("### Statistics\n\n")
        f.write(f"- Total test cases: {total_tests}\n")
        f.write(f"- Total validation commands: {total_commands}\n")
        f.write(f"- Categories: {len(all_tests)}\n")
        f.write("\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for category in sorted(all_tests.keys()):
            anchor = category.lower().replace(" ", "-").replace("'", "")
            f.write(f"- [{category}](#{anchor}) ({len(all_tests[category])} tests)\n")
        f.write("\n---\n\n")
        
        # Main content
        for category in sorted(all_tests.keys()):
            f.write(f"## {category}\n\n")
            
            # Group similar tests
            test_groups = defaultdict(list)
            for test in all_tests[category]:
                # Group by test class
                test_groups[test.test_class].append(test)
            
            for test_class, tests in sorted(test_groups.items()):
                if len(test_groups) > 1:
                    clean_class = test_class.replace("Test", "").replace("Ferguson", "")
                    f.write(f"### {clean_class} Tests\n\n")
                
                for test in sorted(tests, key=lambda t: t.test_method):
                    f.write(format_test_case(test))
                    f.write("\n---\n\n")
    
    print(f"\nGenerated: {output_file}")
    print(f"Total test cases processed: {total_tests}")
    print(f"Total validation commands: {total_commands}")


def main():
    """Main entry point."""
    generate_complete_validation_document()


if __name__ == "__main__":
    main()