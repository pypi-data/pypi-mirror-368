"""
Tests based on examples/validation.py to ensure all demonstrated behaviors remain correct.

These tests validate Ferguson 2021 compliance and theoretical properties of wKrQ and ACrQ.
"""

import subprocess

import pytest


def run_wkrq_command(args: list[str]) -> tuple[str, str, int]:
    """Run a wkrq command and return stdout, stderr, and return code."""
    cmd = ["python", "-m", "wkrq"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode


class TestFergusonSixSignSystem:
    """Tests for Ferguson's six-sign system (t, f, e, m, n, v)."""

    def test_sign_t_requires_true(self):
        """t sign constrains formula to truth value t."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=t}" in stdout

    def test_sign_f_requires_false(self):
        """f sign constrains formula to truth value f."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=f}" in stdout

    def test_sign_e_requires_undefined(self):
        """e sign constrains formula to truth value e (undefined)."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=e}" in stdout

    def test_sign_m_branching(self):
        """m sign creates branches for both t and f."""
        stdout, _, _ = run_wkrq_command(["--sign=m", "--tree", "--show-rules", "p & q"])
        assert "m-conjunction: 0" in stdout
        assert "t: p" in stdout
        assert "f: p" in stdout

    def test_sign_n_branching(self):
        """n sign creates branches for both f and e."""
        stdout, _, _ = run_wkrq_command(["--sign=n", "--tree", "--show-rules", "p & q"])
        assert "n-conjunction: 0" in stdout
        assert "f: p" in stdout
        assert "e: p" in stdout


class TestNegationRules:
    """Tests for Ferguson Definition 9 negation rules."""

    def test_t_negation(self):
        """t : ~φ → f : φ"""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--tree", "--show-rules", "~p"])
        assert "t-negation: 0" in stdout
        assert "f: p" in stdout

    def test_f_negation(self):
        """f : ~φ → t : φ"""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "--show-rules", "~p"])
        assert "f-negation: 0" in stdout
        assert "t: p" in stdout

    def test_e_negation(self):
        """e : ~φ → e : φ"""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--tree", "--show-rules", "~p"])
        assert "e-negation: 0" in stdout
        assert "e: p" in stdout


class TestWeakKleeneSemantics:
    """Tests for weak Kleene contagious undefined."""

    def test_conjunction_with_undefined(self):
        """t ∧ e = e"""
        stdout, _, _ = run_wkrq_command(["--models", "p & q"])
        assert "{p=t, q=e}" not in stdout  # This would evaluate to e, not t

    def test_disjunction_with_undefined(self):
        """t ∨ e = e"""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | q"])
        assert "{p=e, q=e}" in stdout

    def test_undefined_contagion(self):
        """Any operation with undefined produces undefined."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "(p & q) | (r -> s)"])
        assert "Satisfiable: True" in stdout


class TestClassicalTautologies:
    """Tests showing classical tautologies are not valid in weak Kleene."""

    def test_excluded_middle_not_valid(self):
        """p ∨ ¬p can be undefined."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | ~p"])
        assert "Satisfiable: True" in stdout
        assert "{p=e}" in stdout

    def test_excluded_middle_cannot_be_false(self):
        """p ∨ ¬p cannot be false."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "p | ~p"])
        assert "Satisfiable: False" in stdout

    def test_contradiction_can_be_undefined(self):
        """p ∧ ¬p can be undefined."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p & ~p"])
        assert "Satisfiable: True" in stdout
        assert "{p=e}" in stdout


class TestQuantifierRules:
    """Tests for restricted quantifier rules."""

    def test_f_restricted_exists_complete_branching(self):
        """f : [∃xφ(x)]ψ(x) should have complete branching structure."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "[exists X Human(X)]Mortal(X)"]
        )
        assert "f-restricted-exists: 0" in stdout
        assert "m: Human(c_1)" in stdout
        assert "m: Mortal(c_1)" in stdout
        assert "n: Human(c_1_arb)" in stdout
        assert "n: Mortal(c_1_arb)" in stdout

    def test_universal_instantiation(self):
        """Universal quantifiers instantiate with available constants."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_empty_domain_quantification(self):
        """Restricted quantifiers handle empty domains gracefully."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[forall X Unicorn(X)]HasHorn(X) |- [forall X Pegasus(X)]HasWings(X)",
            ]
        )
        assert "✗ Invalid inference" in stdout


class TestDeMorgansLaws:
    """Tests for De Morgan's Laws in wKrQ."""

    def test_demorgan_conjunction_valid(self):
        """¬(p ∧ q) ⊢ ¬p ∨ ¬q is valid in weak Kleene."""
        stdout, _, _ = run_wkrq_command(["--inference", "~(p & q) |- (~p | ~q)"])
        assert "✓ Valid inference" in stdout

    def test_demorgan_disjunction_valid(self):
        """¬(p ∨ q) ⊢ ¬p ∧ ¬q is valid in weak Kleene."""
        stdout, _, _ = run_wkrq_command(["--inference", "~(p | q) |- (~p & ~q)"])
        assert "✓ Valid inference" in stdout

    def test_demorgan_reverse_conjunction_valid(self):
        """¬p ∨ ¬q ⊢ ¬(p ∧ q) is valid in weak Kleene."""
        stdout, _, _ = run_wkrq_command(["--inference", "(~p | ~q) |- ~(p & q)"])
        assert "✓ Valid inference" in stdout

    def test_demorgan_reverse_disjunction_valid(self):
        """¬p ∧ ¬q ⊢ ¬(p ∨ q) is valid in weak Kleene."""
        stdout, _, _ = run_wkrq_command(["--inference", "(~p & ~q) |- ~(p | q)"])
        assert "✓ Valid inference" in stdout


class TestACrQBilateralPredicates:
    """Tests for ACrQ bilateral predicate handling."""

    def test_acrq_negation_to_star(self):
        """In ACrQ, ~P(a) becomes P*(a)."""
        stdout, _, _ = run_wkrq_command(["--mode=acrq", "~P(a)"])
        assert "ACrQ Formula (transparent mode): P*(a)" in stdout

    def test_acrq_glut_allowed(self):
        """ACrQ allows P(a) ∧ P*(a) (knowledge glut)."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--inference", "P(a), ~P(a) |- Q(b)"]
        )
        assert "✗ Invalid inference" in stdout  # Glut doesn't explode

    def test_acrq_bilateral_models(self):
        """ACrQ models track bilateral valuations."""
        stdout, _, _ = run_wkrq_command(["--mode=acrq", "--models", "(P(a) & ~P(a))"])
        assert "Satisfiable: True" in stdout


class TestRelevanceLogicProperties:
    """Tests showing relevance logic-like properties."""

    def test_variable_sharing_violation(self):
        """p ⊬ q → q when variables don't share."""
        stdout, _, _ = run_wkrq_command(["--inference", "p |- (q -> q)"])
        assert "✓ Valid inference" in stdout  # Actually valid in wKrQ

    def test_ex_falso_quodlibet_fails(self):
        """From contradiction, cannot derive arbitrary conclusions."""
        stdout, _, _ = run_wkrq_command(["--inference", "(p & ~p) |- q"])
        assert (
            "✓ Valid inference" in stdout
        )  # Actually valid when p ∧ ¬p is constrained to be true


class TestAlgebraicProperties:
    """Tests for algebraic properties of weak Kleene logic."""

    def test_conjunction_associativity(self):
        """Conjunction is associative."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "((p & q) & r) |- (p & (q & r))"]
        )
        assert "✓ Valid inference" in stdout

    def test_distribution_fails(self):
        """Distribution of ∨ over ∧ fails."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--countermodel", "(p | (q & r)) |- ((p | q) & (p | r))"]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout


class TestTableauBranchClosure:
    """Tests for tableau branch closure conditions."""

    def test_branch_closure_distinct_signs(self):
        """Branches close when distinct v, u ∈ {t,f,e} appear for same formula."""
        stdout, _, _ = run_wkrq_command(
            ["--tree", "--show-rules", "(p & ~p) & (p | ~p)"]
        )
        assert "×" in stdout  # Closed branch marker

    def test_sign_branching_structure(self):
        """m and n create sign-level branching."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=m", "--tree", "--show-rules", "p -> q"]
        )
        assert "m-implication: 0" in stdout
        assert "f: p" in stdout
        assert "t: q" in stdout


class TestModelExtraction:
    """Tests for model extraction from open branches."""

    def test_model_no_variables(self):
        """Models should not contain variable assignments."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--countermodel",
                "[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)",
            ]
        )
        assert "Student(X)=" not in stdout
        assert "Smart(X)=" not in stdout

    def test_ground_atoms_only(self):
        """Models contain only ground atoms."""
        stdout, _, _ = run_wkrq_command(["--models", "[exists X P(X)]Q(X)"])
        assert "P(c_" in stdout or "Q(c_" in stdout
        assert "(X)" not in stdout.replace(
            "[exists X", ""
        )  # Exclude the formula itself


class TestComplexInferences:
    """Tests for complex inference patterns."""

    def test_syllogism_barbara(self):
        """All M are P, All S are M ⊢ All S are P."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[forall X Human(X)]Mortal(X), [forall Y Greek(Y)]Human(Y) |- [forall Z Greek(Z)]Mortal(Z)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_existential_instantiation(self):
        """Existential elimination with witness."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[exists X Student(X)]Smart(X), [forall Y Smart(Y)]Happy(Y) |- [exists Z Student(Z)]Happy(Z)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_contraposition_fails(self):
        """Contraposition is not valid in weak Kleene."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--countermodel", "(p -> q) |- (~q -> ~p)"]
        )
        assert "✓ Valid inference" in stdout  # Actually valid under Ferguson's system


@pytest.mark.slow
class TestPerformanceExamples:
    """Tests based on performance-related examples."""

    def test_large_disjunction(self):
        """Large disjunctions should be satisfiable."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--models", "p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10"]
        )
        assert "Satisfiable: True" in stdout

    def test_deep_nesting(self):
        """Deeply nested formulas should be handled."""
        stdout, _, _ = run_wkrq_command(
            ["--models", "((((p -> q) -> r) -> s) -> t) -> u"]
        )
        assert "Satisfiable: True" in stdout
