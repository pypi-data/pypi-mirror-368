#!/usr/bin/env python3
"""
Generate a human-readable report of all test cases from pytest tests.
This extracts the logical formulas and their expected results for expert review.
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional
import subprocess
import sys


class TestCase:
    """Represents a single test case with its formula and expected result."""
    def __init__(self, test_class: str, test_method: str, description: str, 
                 formula: str, expected: str, mode: str = "wkrq"):
        self.test_class = test_class
        self.test_method = test_method
        self.description = description
        self.formula = formula
        self.expected = expected
        self.mode = mode


class TestExtractor(ast.NodeVisitor):
    """Extract test cases from pytest test files."""
    
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.current_class = None
        
    def visit_ClassDef(self, node):
        """Track current test class."""
        if node.name.startswith("Test"):
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = None
            
    def visit_FunctionDef(self, node):
        """Extract test information from test methods."""
        if not node.name.startswith("test_"):
            return
            
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Look for run_wkrq_command calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_wkrq_command_call(child):
                    test_info = self._extract_test_info(child, docstring)
                    if test_info:
                        formula, mode = test_info
                        # Look for assertion
                        expected = self._find_expected_result(node)
                        if expected and formula:
                            test_case = TestCase(
                                self.current_class or "Unknown",
                                node.name,
                                docstring.strip(),
                                formula,
                                expected,
                                mode
                            )
                            self.test_cases.append(test_case)
                            break
    
    def _is_wkrq_command_call(self, node):
        """Check if this is a call to run_wkrq_command."""
        if isinstance(node.func, ast.Name) and node.func.id == "run_wkrq_command":
            return True
        return False
    
    def _extract_test_info(self, call_node, docstring) -> Optional[Tuple[str, str]]:
        """Extract formula and mode from run_wkrq_command call."""
        if not call_node.args:
            return None
            
        # First argument should be a list
        if not isinstance(call_node.args[0], ast.List):
            return None
            
        args = []
        for elt in call_node.args[0].elts:
            if isinstance(elt, ast.Constant):
                args.append(elt.value)
        
        # Extract formula and mode
        formula = None
        mode = "wkrq"
        
        for i, arg in enumerate(args):
            if arg == "--inference" and i + 1 < len(args):
                formula = args[i + 1]
            elif arg == "--mode=acrq":
                mode = "acrq"
            elif not arg.startswith("--") and i > 0 and args[i-1] not in ["--inference"]:
                formula = arg
                
        return (formula, mode) if formula else None
    
    def _find_expected_result(self, func_node) -> Optional[str]:
        """Find the expected result from assertions."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                # Look for string comparisons
                if isinstance(node.test, ast.Compare):
                    for op, comparator in zip(node.test.ops, node.test.comparators):
                        if isinstance(op, ast.In) and isinstance(comparator, ast.Name):
                            if isinstance(node.test.left, ast.Constant):
                                if "✓ Valid" in node.test.left.value:
                                    return "Valid"
                                elif "✗ Invalid" in node.test.left.value:
                                    return "Invalid"
                                elif "Satisfiable: True" in node.test.left.value:
                                    return "Satisfiable"
                                elif "Satisfiable: False" in node.test.left.value:
                                    return "Unsatisfiable"
        return None


def extract_tests_from_file(filepath: Path) -> List[TestCase]:
    """Extract test cases from a single test file."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    extractor = TestExtractor()
    extractor.visit(tree)
    return extractor.test_cases


def format_test_case(tc: TestCase) -> str:
    """Format a test case for display."""
    lines = []
    
    # Clean up description
    desc = tc.description
    if not desc:
        # Generate description from test method name
        desc = tc.test_method.replace("test_", "").replace("_", " ").title()
    
    lines.append(f"## {desc}")
    if tc.mode != "wkrq":
        lines.append(f"Mode: {tc.mode.upper()}")
    lines.append(f"Formula: {tc.formula}")
    lines.append(f"Expected: {tc.expected}")
    
    return "\n".join(lines)


def group_tests_by_category(test_cases: List[TestCase]) -> dict:
    """Group test cases by their test class."""
    grouped = {}
    for tc in test_cases:
        if tc.test_class not in grouped:
            grouped[tc.test_class] = []
        grouped[tc.test_class].append(tc)
    return grouped


def clean_class_name(class_name: str) -> str:
    """Convert TestClassName to readable format."""
    # Remove Test prefix
    if class_name.startswith("Test"):
        class_name = class_name[4:]
    
    # Add spaces before capitals
    result = ""
    for i, char in enumerate(class_name):
        if i > 0 and char.isupper() and class_name[i-1].islower():
            result += " "
        result += char
    
    return result


def generate_report(test_files: List[Path], output_file: Path):
    """Generate the full report from all test files."""
    all_tests = []
    
    # Extract tests from each file
    for test_file in test_files:
        if test_file.exists():
            tests = extract_tests_from_file(test_file)
            all_tests.extend(tests)
    
    # Group by category
    grouped = group_tests_by_category(all_tests)
    
    # Generate report
    with open(output_file, 'w') as f:
        f.write("# wKrQ Test Cases Report\n\n")
        f.write("This report contains all test cases extracted from the pytest test suite.\n")
        f.write("Generated for expert review in philosophical logic.\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for class_name in sorted(grouped.keys()):
            clean_name = clean_class_name(class_name)
            f.write(f"- [{clean_name}](#{class_name.lower()})\n")
        f.write("\n---\n\n")
        
        # Test cases by category
        for class_name in sorted(grouped.keys()):
            clean_name = clean_class_name(class_name)
            f.write(f"# {clean_name}\n\n")
            
            for tc in grouped[class_name]:
                f.write(format_test_case(tc))
                f.write("\n\n")
            
            f.write("---\n\n")


def run_validation_tests(output_file: Path):
    """Run a subset of tests and capture their actual output for validation."""
    print("Running validation tests to capture actual outputs...")
    
    # Run specific test files that contain the most important logical examples
    test_files = [
        "tests/test_ferguson_validation.py",
        "tests/test_quantifier_bug.py",
        "tests/test_wkrq_basic.py"
    ]
    
    with open(output_file, 'a') as f:
        f.write("\n\n# Actual Test Execution Results\n\n")
        f.write("The following section shows actual execution of key test cases:\n\n")
        
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"Running {test_file}...")
                result = subprocess.run(
                    ["pytest", test_file, "-v", "--tb=no"],
                    capture_output=True,
                    text=True
                )
                
                f.write(f"## {test_file}\n\n")
                f.write("```\n")
                f.write(result.stdout)
                f.write("```\n\n")


def main():
    """Main entry point."""
    # Define test files to scan
    test_files = [
        Path("tests/test_ferguson_validation.py"),
        Path("tests/test_ferguson_compliance.py"),
        Path("tests/test_quantifier_bug.py"),
        Path("tests/test_wkrq_basic.py"),
        Path("tests/test_first_order.py"),
        Path("tests/test_cli_quantifiers.py"),
        Path("tests/test_acrq_integration.py"),
    ]
    
    output_file = Path("docs/test_cases_report.md")
    
    print("Extracting test cases from pytest files...")
    generate_report(test_files, output_file)
    
    # Optionally run tests to show actual results
    if "--run-tests" in sys.argv:
        run_validation_tests(output_file)
    
    print(f"Report generated: {output_file}")
    print("\nTo generate report with actual test execution:")
    print("  python generate_test_report.py --run-tests")


if __name__ == "__main__":
    main()