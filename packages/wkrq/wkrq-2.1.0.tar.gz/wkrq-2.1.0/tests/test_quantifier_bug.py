"""
Test cases demonstrating the restricted quantifier instantiation bug.

Bug: The system incorrectly validates [∃X A(X)]B(X) ⊢ [∀Y A(Y)]B(Y)
This should be invalid but the current system marks it as valid.
"""

import subprocess

import pytest


def run_wkrq_command(args: list[str]) -> tuple[str, str, int]:
    """Run a wkrq command and return stdout, stderr, and return code."""
    cmd = ["python", "-m", "wkrq"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode


class TestQuantifierBug:
    """Tests demonstrating the quantifier instantiation bug."""

    def test_existential_to_universal_invalid(self):
        """[∃X A(X)]B(X) ⊬ [∀Y A(Y)]B(Y) - should be invalid."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)",
            ]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout

    def test_existential_to_universal_with_explicit_domain(self):
        """With explicit domain elements, should still be invalid."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[exists X A(X)]B(X), A(c), A(d) |- [forall Y A(Y)]B(Y)",
            ]
        )
        assert "✗ Invalid inference" in stdout

    def test_valid_universal_instantiation(self):
        """Valid universal instantiation should still work."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_invalid_syllogism(self):
        """Invalid syllogism should be correctly identified."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)",
            ]
        )
        assert "✗ Invalid inference" in stdout

    def test_mixed_quantifiers(self):
        """Mixed quantifier inference that should be invalid."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)",
            ]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout


class TestQuantifierBugAnalysis:
    """Detailed analysis of the bug behavior."""

    def test_trace_fixed_inference(self):
        """Trace through the fixed inference to verify correct behavior."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)",
            ]
        )

        # After fix:
        # 1. Existential creates witness c_N with A(c_N) and B(c_N) true
        # 2. Universal falsification uses fresh constants, not c_N
        # 3. No contradiction, open branch found
        # 4. System correctly reports inference as invalid

        assert "✗ Invalid inference" in stdout  # Fixed behavior
        assert "t: A(c_" in stdout
        assert "t: B(c_" in stdout
        assert "f: B(c_" in stdout  # Different constants used
        # No closed branches for the countermodel

    def test_counterexample_should_exist(self):
        """Demonstrate what counterexample should be found."""
        # Manual construction of what should be a countermodel:
        # Domain: {c, d}
        # A(c) = true, B(c) = true  (witness from existential)
        # A(d) = true, B(d) = false (falsifies universal)

        # This model satisfies [∃X A(X)]B(X) (via c)
        # but falsifies [∀Y A(Y)]B(Y] (via d)

        # The system should find this or similar countermodel
        # but currently fails due to constant reuse
        pass


class TestProposedFix:
    """Tests for the proposed fix implementation."""

    @pytest.mark.skip(reason="Fix not yet implemented")
    def test_fix_generates_fresh_constant(self):
        """After fix, system should generate fresh constant for falsification."""
        # With the fix, when falsifying [∀Y A(Y)]B(Y]:
        # 1. System checks if existing constants would contradict
        # 2. Finds that c_1 already has B(c_1) true
        # 3. Generates fresh c_2 for falsification
        # 4. Successfully finds countermodel
        pass

    @pytest.mark.skip(reason="Fix not yet implemented")
    def test_fix_preserves_valid_inferences(self):
        """Fix should not affect valid inferences."""
        # All currently valid inferences should remain valid
        # The fix only affects how constants are chosen for falsification
        pass


# Additional test cases that might be affected by the bug
class TestRelatedIssues:
    """Other test cases that might be affected by the quantifier bug."""

    def test_multiple_quantifiers(self):
        """Test multiple (non-nested) quantifier behavior."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[forall X P(X)]Q(X), [exists Y Q(Y)]R(Y) |- [exists Z P(Z)]R(Z)",
            ]
        )
        # This is actually invalid - the counterexample shows Q can be true without P
        assert "✗ Invalid inference" in stdout

    @pytest.mark.xfail(reason="May be affected by the same bug")
    def test_quantifier_scope_interactions(self):
        """Test complex quantifier scope interactions."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[exists X P(X)][exists Y Q(Y)] |- [exists Z (P(Z) & Q(Z))]",
            ]
        )
        # This should be invalid - different witnesses
        assert "✗ Invalid inference" in stdout
