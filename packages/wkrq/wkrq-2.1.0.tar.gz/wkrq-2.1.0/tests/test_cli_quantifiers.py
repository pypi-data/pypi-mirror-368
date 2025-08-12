"""
Comprehensive CLI tests for first-order quantifier inference checking.

Tests command-line interface functionality for quantifier reasoning including
parsing, inference validation, output formatting, and error handling.
"""

import json
import subprocess
import sys

import pytest


class CLITestHelper:
    """Helper class for CLI testing."""

    @staticmethod
    def run_cli(args: list[str], input_text: str = None) -> subprocess.CompletedProcess:
        """Run wkrq CLI with given arguments."""
        cmd = [sys.executable, "-m", "wkrq"] + args
        return subprocess.run(
            cmd, input=input_text, text=True, capture_output=True, timeout=30
        )

    @staticmethod
    def assert_valid_inference(output: str) -> None:
        """Assert that CLI output indicates valid inference."""
        assert "✓ Valid inference" in output, f"Expected valid inference, got: {output}"

    @staticmethod
    def assert_invalid_inference(output: str) -> None:
        """Assert that CLI output indicates invalid inference."""
        assert (
            "✗ Invalid inference" in output
        ), f"Expected invalid inference, got: {output}"

    @staticmethod
    def assert_countermodel_shown(output: str) -> None:
        """Assert that countermodel is displayed."""
        assert (
            "Countermodels:" in output
        ), f"Expected countermodel output, got: {output}"


class TestCLIQuantifierParsing:
    """Test CLI parsing of quantifier syntax."""

    def test_universal_quantifier_unicode(self):
        """Test parsing universal quantifier with Unicode symbols."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_existential_quantifier_unicode(self):
        """Test parsing existential quantifier with Unicode symbols."""
        result = CLITestHelper.run_cli(["[∃X Human(X)]Mortal(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Satisfiable: True" in result.stdout

    def test_mixed_quantifiers(self):
        """Test parsing mixed universal and existential quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), [∃Y God(Y)]Immortal(Y), Human(socrates) |- Mortal(socrates)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_complex_quantifier_expressions(self):
        """Test parsing complex quantifier expressions."""
        result = CLITestHelper.run_cli(["[∀X (Human(X) & Rational(X))]Mortal(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Satisfiable: True" in result.stdout

    def test_nested_quantifier_predicates(self):
        """Test parsing nested predicates in quantifiers."""
        result = CLITestHelper.run_cli(["[∀X Student(X)](Studies(X) & Smart(X))"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Satisfiable: True" in result.stdout


class TestCLIUniversalQuantifierInference:
    """Test CLI inference checking with universal quantifiers."""

    def test_basic_universal_inference(self):
        """Test basic universal quantifier inference."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_universal_with_multiple_constants(self):
        """Test universal quantifier with multiple constants."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), Human(socrates), Human(plato), Human(aristotle) |- "
                "Mortal(socrates) & Mortal(plato) & Mortal(aristotle)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_universal_chain_reasoning(self):
        """Test chained universal quantifier reasoning."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Animal(X), [∀Y Animal(Y)]Living(Y), Human(darwin) |- Living(darwin)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_universal_contrapositive(self):
        """Test contrapositive reasoning with universal quantifiers."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)]Mortal(X), ~Mortal(superman) |- ~Human(superman)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_universal_invalid_inference(self):
        """Test invalid universal quantifier inference."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)]Mortal(X), Dog(lassie) |- Mortal(lassie)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_invalid_inference(result.stdout)
        CLITestHelper.assert_countermodel_shown(result.stdout)

    def test_universal_with_negation(self):
        """Test universal quantifier with negated predicates."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)](~Immortal(X)), Human(achilles) |- ~Immortal(achilles)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)


class TestCLIExistentialQuantifierInference:
    """Test CLI inference checking with existential quantifiers."""

    def test_basic_existential_satisfiability(self):
        """Test basic existential quantifier satisfiability."""
        result = CLITestHelper.run_cli(["[∃X Human(X)]Wise(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Satisfiable: True" in result.stdout

    def test_existential_invalid_specific_inference(self):
        """Test that existential doesn't imply specific instance."""
        result = CLITestHelper.run_cli(
            ["[∃X Human(X)]Wise(X), Human(socrates) |- Wise(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_invalid_inference(result.stdout)

    def test_existential_with_unrelated_constant(self):
        """Test existential with unrelated constant."""
        result = CLITestHelper.run_cli(
            ["[∃X Human(X)]Mortal(X), Dog(rover) |- Mortal(rover)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_invalid_inference(result.stdout)

    def test_existential_contradiction(self):
        """Test contradictory existential statements."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)](~Mortal(X)), [∃Y Human(Y)]Mortal(Y) |- False"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        # This should be valid due to contradiction in premises
        CLITestHelper.assert_valid_inference(result.stdout)


class TestCLIMixedQuantifierScenarios:
    """Test CLI with mixed quantifier scenarios."""

    def test_universal_and_existential_combination(self):
        """Test combination of universal and existential quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), [∃Y Human(Y)]Wise(Y), Human(plato) |- Mortal(plato)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_different_variable_names(self):
        """Test quantifiers with different variable names."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Rational(X), [∀Y Rational(Y)]Thinking(Y), Human(descartes) |- Thinking(descartes)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_quantifier_variable_scoping(self):
        """Test proper variable scoping in quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), [∃X God(X)]Immortal(X), Human(socrates) |- Mortal(socrates)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)


class TestCLIQuantifierOutputFormats:
    """Test CLI output formatting for quantifier results."""

    def test_json_output_valid_inference(self):
        """Test JSON output for valid quantifier inference."""
        result = CLITestHelper.run_cli(
            ["--json", "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Parse and validate JSON
        data = json.loads(result.stdout)
        assert data["type"] == "inference"
        assert data["valid"] is True
        assert (
            data["inference"]
            == "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
        )
        assert data["countermodels"] == []

    def test_json_output_invalid_inference(self):
        """Test JSON output for invalid quantifier inference."""
        result = CLITestHelper.run_cli(
            ["--json", "[∀X Human(X)]Mortal(X), Dog(fido) |- Mortal(fido)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        data = json.loads(result.stdout)
        assert data["type"] == "inference"
        assert data["valid"] is False
        assert len(data["countermodels"]) > 0

    def test_json_output_quantifier_formula(self):
        """Test JSON output for quantifier formula satisfiability."""
        result = CLITestHelper.run_cli(["--json", "[∀X Human(X)]Mortal(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        data = json.loads(result.stdout)
        assert data["type"] == "formula"
        assert data["satisfiable"] is True
        assert data["formula"] == "[∀X Human(X)]Mortal(X)"
        assert "stats" in data

    def test_explain_option_with_quantifiers(self):
        """Test --explain option with quantifier inference."""
        result = CLITestHelper.run_cli(
            ["--explain", "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "✓ Valid inference" in result.stdout
        assert "Explanation:" in result.stdout
        assert "Testing satisfiability of:" in result.stdout

    def test_models_option_with_quantifiers(self):
        """Test --models option with quantifier formulas."""
        result = CLITestHelper.run_cli(["--models", "[∃X Human(X)]Wise(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "Satisfiable: True" in result.stdout
        assert "Models" in result.stdout

    def test_stats_option_with_quantifiers(self):
        """Test --stats option with quantifier reasoning."""
        result = CLITestHelper.run_cli(["--stats", "[∀X Human(X)]Mortal(X)"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "Statistics:" in result.stdout
        assert "Open branches:" in result.stdout
        assert "Closed branches:" in result.stdout
        assert "Total nodes:" in result.stdout


class TestCLIQuantifierTreeVisualization:
    """Test CLI tree visualization for quantifier reasoning."""

    def test_ascii_tree_universal_quantifier(self):
        """Test ASCII tree display for universal quantifier."""
        result = CLITestHelper.run_cli(
            ["--tree", "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "✓ Valid inference" in result.stdout
        assert "Tableau tree:" in result.stdout
        # Should contain tree structure characters
        assert any(char in result.stdout for char in ["├", "└", "│"])

    def test_unicode_tree_quantifier(self):
        """Test Unicode tree display for quantifiers."""
        result = CLITestHelper.run_cli(
            ["--tree", "--format=unicode", "[∀X Human(X)]Mortal(X)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "Tableau tree:" in result.stdout
        # Should contain Unicode box drawing characters
        assert any(char in result.stdout for char in ["├", "└", "┌", "─"])

    def test_tree_with_rules_quantifier(self):
        """Test tree display with rules for quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "--tree",
                "--show-rules",
                "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)",
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "Tableau tree:" in result.stdout
        # Should show rule names
        assert any(
            rule in result.stdout
            for rule in ["t-conjunction", "t-negation", "t-restricted-forall"]
        )

    def test_json_tree_quantifier(self):
        """Test JSON tree format for quantifiers."""
        result = CLITestHelper.run_cli(
            ["--tree", "--format=json", "[∀X Human(X)]Mortal(X)"]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        assert "Tableau tree:" in result.stdout
        # Should contain JSON structure
        assert "nodes" in result.stdout
        assert "open_branches" in result.stdout


class TestCLIQuantifierErrorHandling:
    """Test CLI error handling for quantifier syntax."""

    def test_malformed_quantifier_syntax(self):
        """Test error handling for truly malformed quantifier syntax."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X Mortal(X)"]
        )  # Missing closing bracket entirely
        assert result.returncode != 0
        assert "Parse error" in result.stderr

    def test_invalid_variable_in_quantifier(self):
        """Test error handling for invalid variable usage."""
        result = CLITestHelper.run_cli(["[∀ Human(X)]Mortal(X)"])  # Missing variable
        assert result.returncode != 0
        assert "Parse error" in result.stderr

    def test_mixed_variable_confusion(self):
        """Test handling of variable confusion in quantifiers."""
        # This should parse but might have unexpected semantics
        result = CLITestHelper.run_cli(["[∀X Human(Y)]Mortal(X)"])  # Y not bound
        # Depending on parser implementation, this might succeed with a warning
        # or fail - the test documents the behavior
        if result.returncode != 0:
            assert "Parse error" in result.stderr

    def test_complex_syntax_error_reporting(self):
        """Test detailed error reporting for complex syntax errors."""
        result = CLITestHelper.run_cli(
            ["[∀X Human(X)]Mortal(X), Human(socrates) |--| Mortal(socrates)"]
        )  # Invalid inference operator
        assert result.returncode != 0
        assert "Parse error" in result.stderr

    def test_debug_mode_error_handling(self):
        """Test debug mode error handling."""
        result = CLITestHelper.run_cli(
            ["--debug", "[∀X Human(X Mortal(X)"]  # Truly malformed
        )
        assert result.returncode != 0
        # In debug mode, should get more detailed error information


class TestCLIQuantifierPerformance:
    """Test CLI performance with quantifiers."""

    def test_multiple_quantifiers_performance(self):
        """Test CLI performance with multiple quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), [∀Y Animal(Y)]Living(Y), [∃Z God(Z)]Immortal(Z), "
                "Human(socrates), Animal(fido) |- Mortal(socrates) & Living(fido)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_many_constants_performance(self):
        """Test CLI performance with many constants."""
        constants = ["human" + str(i) for i in range(1, 11)]  # 10 constants
        premises = "[∀X Human(X)]Mortal(X)"
        for const in constants:
            premises += f", Human({const})"

        conclusion = " & ".join(f"Mortal({const})" for const in constants)
        inference = f"{premises} |- {conclusion}"

        result = CLITestHelper.run_cli([inference])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_complex_quantifier_nesting_performance(self):
        """Test performance with complex quantifier expressions."""
        result = CLITestHelper.run_cli(
            [
                "[∀X (Human(X) & Rational(X))]Thinking(X), "
                "[∀Y Thinking(Y)]Conscious(Y), "
                "Human(descartes) & Rational(descartes) |- Conscious(descartes)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)


class TestCLIQuantifierInteractiveMode:
    """Test interactive mode with quantifiers."""

    def test_interactive_quantifier_formula(self):
        """Test interactive mode with quantifier formula."""
        result = CLITestHelper.run_cli([], input_text="[∀X Human(X)]Mortal(X)\nquit\n")
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "wKrQ Interactive Mode" in result.stdout
        assert "Satisfiable: True" in result.stdout

    def test_interactive_quantifier_inference(self):
        """Test interactive mode with quantifier inference."""
        result = CLITestHelper.run_cli(
            [],
            input_text="[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)\nquit\n",
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "✓ Valid inference" in result.stdout

    def test_interactive_help_command(self):
        """Test help command in interactive mode."""
        result = CLITestHelper.run_cli([], input_text="help\nquit\n")
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Commands:" in result.stdout
        assert "formula" in result.stdout
        assert "inference" in result.stdout

    def test_interactive_parse_error_recovery(self):
        """Test error recovery in interactive mode."""
        result = CLITestHelper.run_cli(
            [], input_text="[∀X Human(X Mortal(X)\n[∀X Human(X)]Mortal(X)\nquit\n"
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        # First command should fail, second should work
        # Output contains both error and success messages
        # Should contain both error and success
        output_text = result.stdout
        assert "Parse error" in output_text or "Error" in output_text
        assert "Satisfiable: True" in output_text  # Second command should work


class TestCLIQuantifierIntegration:
    """Integration tests for CLI quantifier functionality."""

    def test_real_world_philosophy_example(self):
        """Test real-world philosophical reasoning example."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Human(X)]Mortal(X), [∀Y Mortal(Y)]Finite(Y), Human(socrates) |- Finite(socrates)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_mathematical_reasoning_example(self):
        """Test mathematical reasoning with quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Number(X)]Real(X), [∀Y Real(Y)]Measurable(Y), Number(pi) |- Measurable(pi)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_scientific_reasoning_example(self):
        """Test scientific reasoning with quantifiers."""
        result = CLITestHelper.run_cli(
            [
                "[∀X Organism(X)]Carbon(X), [∃Y Element(Y)]Essential(Y), Organism(bacteria) |- Carbon(bacteria)"
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        CLITestHelper.assert_valid_inference(result.stdout)

    def test_combined_output_options(self):
        """Test combination of multiple CLI options."""
        result = CLITestHelper.run_cli(
            [
                "--stats",
                "--explain",
                "--models",
                "[∀X Human(X)]Rational(X), Human(aristotle) |- Rational(aristotle)",
            ]
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Should contain all expected sections
        assert "✓ Valid inference" in result.stdout
        assert "Explanation:" in result.stdout
        assert "Statistics:" in result.stdout

    def test_version_option(self):
        """Test --version option works correctly."""
        result = CLITestHelper.run_cli(["--version"])
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "wKrQ" in result.stdout
        # Should contain version number
        assert any(char.isdigit() for char in result.stdout)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
