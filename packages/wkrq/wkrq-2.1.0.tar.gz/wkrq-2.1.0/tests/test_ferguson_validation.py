"""
Comprehensive Ferguson 2021 compliance tests based on examples/validation.py.

These tests validate that our wKrQ implementation exactly matches the tableau
system described in Ferguson (2021) "Tableaux and Restricted Quantification
for Systems Related to Weak Kleene Logic."
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

    def test_sign_t_constrains_to_true(self):
        """t sign constrains formula to truth value t."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=t}" in stdout

    def test_sign_f_constrains_to_false(self):
        """f sign constrains formula to truth value f."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=f}" in stdout

    def test_sign_e_constrains_to_undefined(self):
        """e sign constrains formula to truth value e (undefined)."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=e}" in stdout

    def test_sign_m_branches_for_meaningful(self):
        """m sign creates branches for both t and f (meaningful)."""
        stdout, _, _ = run_wkrq_command(["--sign=m", "--tree", "--show-rules", "p & q"])
        assert "m-conjunction: 0" in stdout
        assert "t: p" in stdout
        assert "f: p" in stdout

    def test_sign_n_branches_for_nontrue(self):
        """n sign creates branches for both f and e (nontrue)."""
        stdout, _, _ = run_wkrq_command(["--sign=n", "--tree", "--show-rules", "p & q"])
        assert "n-conjunction: 0" in stdout
        assert "f: p" in stdout
        assert "e: p" in stdout


class TestFergusonNegationRules:
    """Tests for Ferguson Definition 9 negation rules (v : ~φ → ~v : φ)."""

    def test_t_negation_rule(self):
        """t : ~φ → f : φ (where ~t = f)."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--tree", "--show-rules", "~p"])
        assert "t-negation: 0" in stdout
        assert "f: p" in stdout

    def test_f_negation_rule(self):
        """f : ~φ → t : φ (where ~f = t)."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "--show-rules", "~p"])
        assert "f-negation: 0" in stdout
        assert "t: p" in stdout

    def test_e_negation_rule(self):
        """e : ~φ → e : φ (where ~e = e)."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--tree", "--show-rules", "~p"])
        assert "e-negation: 0" in stdout
        assert "e: p" in stdout

    def test_m_negation_branching(self):
        """m : ~φ → (f : φ) + (t : φ) [branches for meaningful]."""
        stdout, _, _ = run_wkrq_command(["--sign=m", "--tree", "--show-rules", "~p"])
        assert "m-negation: 0" in stdout
        assert "f: p" in stdout
        assert "t: p" in stdout

    def test_n_negation_branching(self):
        """n : ~φ → (t : φ) + (e : φ) [branches for nontrue]."""
        stdout, _, _ = run_wkrq_command(["--sign=n", "--tree", "--show-rules", "~p"])
        assert "n-negation: 0" in stdout
        assert "t: p" in stdout
        assert "e: p" in stdout


class TestFergusonConjunctionRules:
    """Tests for Ferguson Definition 9 conjunction rules (v : φ ∧ ψ)."""

    def test_t_conjunction_rule(self):
        """t : (φ ∧ ψ) → t : φ ○ t : ψ [only t ∧ t = t]."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--tree", "--show-rules", "p & q"])
        assert "t-conjunction: 0" in stdout
        assert "t: p" in stdout
        assert "t: q" in stdout

    def test_f_conjunction_branching(self):
        """f : (φ ∧ ψ) → branches for all ways to get f."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "--show-rules", "p & q"])
        assert "f-conjunction: 0" in stdout
        # Should have branches for f:p, f:q, and e cases

    def test_e_conjunction_contagion(self):
        """e : (φ ∧ ψ) → (e : φ) + (e : ψ) [e is contagious]."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--tree", "--show-rules", "p & q"])
        assert "e-conjunction: 0" in stdout
        assert "e: p" in stdout or "e: q" in stdout

    def test_m_conjunction_complex_branching(self):
        """m : (φ ∧ ψ) → complex branching for t and f results."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=m", "--tree", "--show-rules", "--compact", "p & q"]
        )
        assert "m-conjunction: 0" in stdout
        # Should show branching for both t and f possibilities

    def test_n_conjunction_nontrue_branching(self):
        """n : (φ ∧ ψ) → branches for f and e results."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=n", "--tree", "--show-rules", "--compact", "p & q"]
        )
        assert "n-conjunction: 0" in stdout
        # Should show branching for f and e possibilities


class TestFergusonDisjunctionRules:
    """Tests for Ferguson Definition 9 disjunction rules (v : φ ∨ ψ)."""

    def test_t_disjunction_branching(self):
        """t : (φ ∨ ψ) → (t : φ) + (t : ψ) [branches]."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--tree", "--show-rules", "p | q"])
        assert "t-disjunction: 0" in stdout
        assert "t: p" in stdout
        assert "t: q" in stdout

    def test_f_disjunction_rule(self):
        """f : (φ ∨ ψ) → f : φ ○ f : ψ [only f ∨ f = f]."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "--show-rules", "p | q"])
        assert "f-disjunction: 0" in stdout
        assert "f: p" in stdout
        assert "f: q" in stdout

    def test_e_disjunction_contagion(self):
        """e : (φ ∨ ψ) → (e : φ) + (e : ψ) [e is contagious]."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--tree", "--show-rules", "p | q"])
        assert "e-disjunction: 0" in stdout
        assert "e: p" in stdout or "e: q" in stdout


class TestFergusonImplicationRules:
    """Tests for Ferguson Definition 9 implication rules (φ → ψ as ~φ ∨ ψ)."""

    def test_t_implication_branching(self):
        """t : (φ → ψ) → (f : φ) + (t : ψ) [~φ = t means φ = f]."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--tree", "--show-rules", "p -> q"]
        )
        assert "t-implication: 0" in stdout
        assert "f: p" in stdout
        assert "t: q" in stdout

    def test_f_implication_rule(self):
        """f : (φ → ψ) → t : φ ○ f : ψ [~φ = f means φ = t]."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "p -> q"]
        )
        assert "f-implication: 0" in stdout
        assert "t: p" in stdout
        assert "f: q" in stdout

    def test_e_implication_contagion(self):
        """e : (φ → ψ) → (e : φ) + (e : ψ) [e propagates]."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=e", "--tree", "--show-rules", "p -> q"]
        )
        assert "e-implication: 0" in stdout
        assert "e: p" in stdout or "e: q" in stdout


class TestFergusonBranchClosure:
    """Tests for Ferguson Definition 10 branch closure conditions."""

    def test_branch_closure_t_f(self):
        """Branch closes when t:φ and f:φ appear (distinct v, u ∈ {t,f,e})."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--tree", "--show-rules", "p & ~p"]
        )
        assert "×" in stdout  # Closed branch marker

    def test_branch_closure_t_e(self):
        """Branch closes when t:φ and e:φ appear."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--tree", "--show-rules", "(p | ~p) & ~(p | ~p)"]
        )
        assert "×" in stdout

    def test_branch_closure_f_e(self):
        """Branch closes when f:φ and e:φ appear."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "(p & ~p) | ~(p & ~p)"]
        )
        assert "×" in stdout


class TestWeakKleeneSemantics:
    """Tests for weak Kleene contagious undefined semantics."""

    def test_disjunction_with_undefined_contagion(self):
        """t ∨ e = e (NOT t) - distinguishes weak from strong Kleene."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | q"])
        assert "Satisfiable: True" in stdout
        assert "{p=e, q=e}" in stdout

    def test_conjunction_with_undefined_contagion(self):
        """f ∧ e = e - undefined is contagious."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p & q"])
        assert "Satisfiable: True" in stdout
        # At least one must be undefined

    def test_classical_tautology_can_be_undefined(self):
        """Classical tautologies can be undefined (NOT valid)."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | ~p"])
        assert "Satisfiable: True" in stdout
        assert "{p=e}" in stdout

    def test_excluded_middle_cannot_be_false(self):
        """p ∨ ¬p is NOT valid (can be e) but cannot be false."""
        stdout, _, _ = run_wkrq_command(["--sign=f", "--tree", "p | ~p"])
        assert "Satisfiable: False" in stdout


class TestFergusonRestrictedQuantifierRules:
    """Tests for Ferguson's restricted quantifier rules."""

    def test_t_restricted_exists_rule(self):
        """t : [∃x φ(x)]ψ(x) → t : φ(c) ○ t : ψ(c)."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--tree", "--show-rules", "[exists X Human(X)]Mortal(X)"]
        )
        assert "t-restricted-exists: 0" in stdout
        assert "t: Human(c_" in stdout
        assert "t: Mortal(c_" in stdout

    def test_f_restricted_exists_complex_branching(self):
        """f : [∃x φ(x)]ψ(x) → complex branching with m and n."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "[exists X Human(X)]Mortal(X)"]
        )
        assert "f-restricted-exists: 0" in stdout
        assert "m: Human(c_" in stdout
        assert "m: Mortal(c_" in stdout
        assert "n: Human(c_" in stdout
        assert "n: Mortal(c_" in stdout

    def test_t_restricted_forall_branching(self):
        """t : [∀x φ(x)]ψ(x) → (f : φ(c)) + (t : ψ(c))."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--tree", "--show-rules", "[forall X Human(X)]Mortal(X)"]
        )
        assert "t-restricted-forall: 0" in stdout
        assert "f: Human(c_" in stdout or "t: Mortal(c_" in stdout

    def test_f_restricted_forall_counterexample(self):
        """f : [∀x φ(x)]ψ(x) → t : φ(c) ○ f : ψ(c) [counterexample]."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "[forall X Human(X)]Mortal(X)"]
        )
        assert "f-restricted-forall: 0" in stdout
        assert "t: Human(c_" in stdout
        assert "f: Mortal(c_" in stdout


class TestQuantifierInference:
    """Tests for quantifier inference patterns."""

    def test_standard_syllogism(self):
        """All humans mortal, Socrates human ⊢ Socrates mortal."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_existential_witness_invalid(self):
        """Some student smart, Alice student ⊬ Alice smart."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "--countermodel",
                "[exists X Student(X)]Smart(X), Student(alice) |- Smart(alice)",
            ]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout


class TestMAndNBranchingBehavior:
    """Tests for m and n as branching instructions (not truth values)."""

    def test_m_creates_meaningful_branches(self):
        """m creates branches exploring both t and f possibilities."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=m", "--tree", "--show-rules", "(p -> q) & (q -> r)"]
        )
        assert "m-conjunction: 0" in stdout
        # Should see branching for t and f cases

    def test_n_creates_nontrue_branches(self):
        """n creates branches exploring both f and e possibilities."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=n", "--tree", "--show-rules", "(p | q) -> r"]
        )
        assert "n-implication: 0" in stdout
        # Should see branching for f and e cases

    def test_m_on_atomic_formula(self):
        """m on atomic formula (no rule to apply, model chooses value)."""
        stdout, _, _ = run_wkrq_command(["--sign=m", "--models", "p"])
        assert "Satisfiable: True" in stdout
        # Should have models with both p=t and p=f


class TestComplexFergusonExamples:
    """Complex examples demonstrating full Ferguson system."""

    def test_epistemic_uncertainty_about_logical_truth(self):
        """Epistemic uncertainty about logical truth (m sign on tautology)."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=m", "--tree", "--show-rules", "p | ~p"]
        )
        assert "m-disjunction: 0" in stdout
        # m allows considering both t and f even for tautologies

    def test_knowledge_gap_representation(self):
        """Knowledge gap representation (n sign)."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=n", "--tree", "--show-rules", "Human(alice) -> Mortal(alice)"]
        )
        assert "n-implication: 0" in stdout
        # n allows both f and e (nontrue)

    def test_quantifiers_with_three_valued_logic(self):
        """Interaction of quantifiers with three-valued logic."""
        stdout, _, _ = run_wkrq_command(
            [
                "--sign=t",
                "--tree",
                "--show-rules",
                "[forall X Human(X)]Mortal(X) & [exists Y ~Mortal(Y)]Robot(Y)",
            ]
        )
        assert "t-conjunction: 0" in stdout


class TestSoundnessAndCompleteness:
    """Tests for soundness and completeness (Ferguson Theorems 1-2)."""

    def test_modus_ponens_sound(self):
        """Modus ponens is sound."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "p, p -> q |- q"]
        )
        assert "✓ Valid inference" in stdout

    def test_invalid_inference_rejected(self):
        """Invalid inference correctly rejected."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "--countermodel", "p -> q |- q"]
        )
        assert "✗ Invalid inference" in stdout

    def test_complex_valid_inference(self):
        """Complex valid inference."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "(p -> q) & (q -> r), p | s, ~s |- r",
            ]
        )
        assert "✓ Valid inference" in stdout


class TestModelExtraction:
    """Tests for model extraction from open branches (Ferguson Definition 12)."""

    def test_models_reflect_sign_semantics(self):
        """Models reflect sign semantics (t:p produces p=true)."""
        stdout, _, _ = run_wkrq_command(["--sign=t", "--models", "p & (q | r)"])
        assert "Satisfiable: True" in stdout
        assert "{p=t" in stdout

    def test_models_for_e_sign(self):
        """Models for e sign show undefined values."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | q"])
        assert "Satisfiable: True" in stdout
        assert "=e}" in stdout

    def test_models_for_n_sign(self):
        """Models for n sign show nontrue values (f or e)."""
        stdout, _, _ = run_wkrq_command(["--sign=n", "--models", "p"])
        assert "Satisfiable: True" in stdout
        assert "{p=f}" in stdout or "{p=e}" in stdout


class TestDeMorgansLaws:
    """Tests for De Morgan's Laws in weak Kleene logic."""

    def test_demorgan_conjunction_to_disjunction(self):
        """¬(p ∧ q) ⊢ ¬p ∨ ¬q (VALID in weak Kleene)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "~(p & q) |- (~p | ~q)"]
        )
        assert "✓ Valid inference" in stdout

    def test_demorgan_disjunction_to_conjunction(self):
        """¬p ∨ ¬q ⊢ ¬(p ∧ q) (VALID in weak Kleene)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(~p | ~q) |- ~(p & q)"]
        )
        assert "✓ Valid inference" in stdout

    def test_demorgan_disjunction_negation(self):
        """¬(p ∨ q) ⊢ ¬p ∧ ¬q (VALID in weak Kleene)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "~(p | q) |- (~p & ~q)"]
        )
        assert "✓ Valid inference" in stdout

    def test_demorgan_conjunction_negation(self):
        """¬p ∧ ¬q ⊢ ¬(p ∨ q) (VALID in weak Kleene)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(~p & ~q) |- ~(p | q)"]
        )
        assert "✓ Valid inference" in stdout

    def test_demorgan_with_undefined(self):
        """De Morgan with undefined: When p,q undefined, both sides undefined."""
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "~(p & q)"])
        assert "Satisfiable: True" in stdout
        assert "{p=e, q=e}" in stdout

    def test_quantified_demorgan_valid(self):
        """Quantified De Morgan: ¬∀x P(x) ⊢ ∃x ¬P(x) (valid in Ferguson's system)."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "~([forall X Domain(X)]P(X)) |- [exists Y Domain(Y)](~P(Y))",
            ]
        )
        assert "✓ Valid inference" in stdout


class TestACrQDeMorgansLaws:
    """Tests for De Morgan's Laws in ACrQ (paraconsistent system)."""

    def test_acrq_demorgan_basic(self):
        """ACrQ De Morgan 1a: ¬(P(a) ∧ Q(a)) ⊬ ¬P(a) ∨ ¬Q(a) in ACrQ."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--inference", "~(P(a) & Q(a)) |- (~P(a) | ~Q(a))"]
        )
        assert "✗ Invalid inference" in stdout
        # In ACrQ, when P and Q are undefined, the inference fails

    def test_acrq_demorgan_bilateral_conversion(self):
        """ACrQ De Morgan with bilateral: ¬(P(a) ∧ Q(a)) becomes P*(a) ∨ Q*(a)."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--tree", "--show-rules", "~(P(a) & Q(a))"]
        )
        assert "ACrQ Formula" in stdout

    def test_acrq_demorgan_with_glut(self):
        """ACrQ De Morgan with glut: P(a) ∧ ~P(a) case."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--models",
                "--tree",
                "--show-rules",
                "~((P(a) & ~P(a)) & Q(a))",
            ]
        )
        assert "Satisfiable: True" in stdout

    def test_acrq_demorgan_preserves_despite_gluts(self):
        """ACrQ preserves De Morgan despite gluts."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--inference",
                "(P(a) & ~P(a)), ~(P(a) & Q(a)) |- (~P(a) | ~Q(a))",
            ]
        )
        assert "✓ Valid inference" in stdout
        # With gluts, this De Morgan inference is actually valid in ACrQ


class TestClassicalInferences:
    """Tests for classical logic inference patterns."""

    def test_modus_ponens(self):
        """Modus Ponens: p, p → q ⊢ q."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "p, (p -> q) |- q"]
        )
        assert "✓ Valid inference" in stdout

    def test_modus_tollens(self):
        """Modus Tollens: ¬q, p → q ⊢ ¬p."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "~q, (p -> q) |- ~p"]
        )
        assert "✓ Valid inference" in stdout

    def test_hypothetical_syllogism(self):
        """Hypothetical Syllogism: p → q, q → r ⊢ p → r."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(p -> q), (q -> r) |- (p -> r)"]
        )
        assert "✓ Valid inference" in stdout

    def test_disjunctive_syllogism(self):
        """Disjunctive Syllogism: p ∨ q, ¬p ⊢ q."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(p | q), ~p |- q"]
        )
        assert "✓ Valid inference" in stdout

    def test_constructive_dilemma(self):
        """Constructive Dilemma: (p → q) ∧ (r → s), p ∨ r ⊢ q ∨ s."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "((p -> q) & (r -> s)), (p | r) |- (q | s)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_simplification(self):
        """Simplification: p ∧ q ⊢ p."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(p & q) |- p"]
        )
        assert "✓ Valid inference" in stdout

    def test_addition(self):
        """Addition: p ⊢ p ∨ q."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "p |- (p | q)"]
        )
        assert "✓ Valid inference" in stdout

    def test_contraposition_valid_in_ferguson(self):
        """Contraposition: (p → q) ⊢ (¬q → ¬p) is valid in Ferguson's system."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(p -> q) |- (~q -> ~p)"]
        )
        assert "✓ Valid inference" in stdout

    def test_double_negation_elimination(self):
        """Double Negation Elimination: ¬¬p ⊢ p (VALID)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "~~p |- p"]
        )
        assert "✓ Valid inference" in stdout


class TestInvalidInferences:
    """Tests for invalid inferences with countermodels."""

    def test_affirming_the_consequent(self):
        """Affirming the Consequent: q, p → q ⊬ p."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "--countermodel",
                "q, (p -> q) |- p",
            ]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout

    def test_denying_the_antecedent(self):
        """Denying the Antecedent: ¬p, p → q ⊬ ¬q."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "--countermodel",
                "~p, (p -> q) |- ~q",
            ]
        )
        assert "✗ Invalid inference" in stdout
        assert "Countermodels:" in stdout

    def test_undistributed_middle(self):
        """Fallacy of the Undistributed Middle: All A are B, All C are B ⊬ All A are C."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "--countermodel",
                "[forall X A(X)]B(X), [forall Y C(Y)]B(Y) |- [forall Z A(Z)]C(Z)",
            ]
        )
        assert "✗ Invalid inference" in stdout

    def test_invalid_existential_generalization(self):
        """Invalid Existential: Some A are B ⊬ All A are B."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "--countermodel",
                "[exists X A(X)]B(X) |- [forall Y A(Y)]B(Y)",
            ]
        )
        assert "✗ Invalid inference" in stdout


class TestAristotelianSyllogisms:
    """Tests for Aristotelian syllogistic reasoning."""

    def test_barbara_syllogism(self):
        """Barbara: All M are P, All S are M ⊢ All S are P."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X M(X)]P(X), [forall Y S(Y)]M(Y) |- [forall Z S(Z)]P(Z)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_celarent_syllogism(self):
        """Celarent: No M are P, All S are M ⊢ No S are P."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X M(X)](~P(X)), [forall Y S(Y)]M(Y) |- [forall Z S(Z)](~P(Z))",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_darii_syllogism(self):
        """Darii: All M are P, Some S are M ⊢ Some S are P."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X M(X)]P(X), [exists Y S(Y)]M(Y) |- [exists Z S(Z)]P(Z)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_ferio_syllogism(self):
        """Ferio: No M are P, Some S are M ⊢ Some S are not P."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X M(X)](~P(X)), [exists Y S(Y)]M(Y) |- [exists Z S(Z)](~P(Z))",
            ]
        )
        assert "✓ Valid inference" in stdout


class TestRelevanceLogicProperties:
    """Tests showing relevance logic-like properties."""

    def test_variable_sharing_principle_holds_classically(self):
        """Variable sharing fails in relevance logic but holds in wKrQ."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "p |- (q -> q)"]
        )
        assert "✓ Valid inference" in stdout  # Valid due to classical validity

    def test_ex_falso_quodlibet_vacuous(self):
        """Ex falso quodlibet holds vacuously when premise is constrained true."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "(p & ~p) |- q"]
        )
        assert "✓ Valid inference" in stdout  # Valid because p ∧ ¬p can't be true

    def test_relevant_modus_ponens(self):
        """Relevant Modus Ponens: p, p → q ⊢ q (shared variable)."""
        stdout, _, _ = run_wkrq_command(
            ["--inference", "--tree", "--show-rules", "p, (p -> q) |- q"]
        )
        assert "✓ Valid inference" in stdout


class TestACrQParaconsistentReasoning:
    """Tests for ACrQ paraconsistent properties."""

    def test_non_explosion(self):
        """Non-explosion: P(a), ~P(a) ⊬ Q(b) (glut doesn't explode)."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--inference", "--countermodel", "P(a), ~P(a) |- Q(b)"]
        )
        assert "✗ Invalid inference" in stdout

    def test_local_inconsistency(self):
        """Local Inconsistency: P(a) ∧ ~P(a) doesn't affect Q(b)."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--models",
                "--tree",
                "--show-rules",
                "(P(a) & ~P(a)) & (Q(b) & ~~Q(b))",
            ]
        )
        assert "Satisfiable: True" in stdout

    def test_reasoning_despite_gluts(self):
        """Reasoning despite gluts: P(a) → Q(a), P(a), ~P(a) ⊢ Q(a)."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--inference", "(P(a) -> Q(a)), P(a), ~P(a) |- Q(a)"]
        )
        assert "✓ Valid inference" in stdout

    def test_four_states_demonstration(self):
        """Four states demonstration: glut, classic true, classic false, gap."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--models",
                "--tree",
                "--show-rules",
                "(P(a) & ~~P(a)) & (~Q(a) & ~~Q(a)) & (~R(a) & ~~~R(a)) & (S(a) & ~S(a))",
            ]
        )
        assert "Satisfiable: True" in stdout


class TestComplexRealWorldScenarios:
    """Tests for complex real-world application scenarios."""

    def test_legal_reasoning_with_conflicts(self):
        """Legal reasoning with conflicting testimony."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--models",
                "--tree",
                "--show-rules",
                "(Witness(john, alibi) & ~Witness(john, alibi)) & (Evidence(dna, present) -> Guilty(suspect))",
            ]
        )
        assert "Satisfiable: True" in stdout

    def test_medical_diagnosis_contradictory_symptoms(self):
        """Medical diagnosis with contradictory symptoms."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--inference",
                "Symptom(patient, fever), ~Symptom(patient, fever), [forall X (Symptom(X, fever) & ~~Symptom(X, fever))]Flu(X) |- Flu(patient)",
            ]
        )
        assert "✓ Valid inference" in stdout
        # The universal instantiation actually makes this valid despite the glut

    def test_database_reconciliation(self):
        """Database reconciliation with conflicts."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--models",
                "--tree",
                "--show-rules",
                "(Age(person, 25) & Age(person, 26)) & (Age(person, 25) -> Eligible(person, youth_program))",
            ]
        )
        assert "Satisfiable: True" in stdout

    def test_sensor_fusion_noisy_readings(self):
        """Sensor fusion with noisy readings."""
        stdout, _, _ = run_wkrq_command(
            [
                "--mode=acrq",
                "--inference",
                "Temp(sensor1, high), ~Temp(sensor1, high), Temp(sensor2, high), (Temp(sensor2, high) -> Alert(fire)) |- Alert(fire)",
            ]
        )
        assert "✓ Valid inference" in stdout


class TestEdgeCasesAndStressTests:
    """Tests for edge cases and boundary conditions."""

    def test_empty_domain_quantification(self):
        """Empty domain quantification."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X Unicorn(X)]HasHorn(X), ~[exists Y True(Y)]Unicorn(Y) |- [forall Z False(Z)]True(Z)",
            ]
        )
        assert "✗ Invalid inference" in stdout

    def test_complex_restricted_quantifier_inference(self):
        """Complex restricted quantifier inference."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "--tree",
                "--show-rules",
                "[forall X Person(X)]HasParent(X), [forall Y HasParent(Y)]NeedsCare(Y) |- [forall Z Person(Z)]NeedsCare(Z)",
            ]
        )
        assert "✓ Valid inference" in stdout

    def test_maximum_formula_nesting(self):
        """Maximum formula nesting."""
        stdout, _, _ = run_wkrq_command(
            ["--models", "--tree", "--show-rules", "((((p -> q) -> r) -> s) -> t) -> u"]
        )
        assert "Satisfiable: True" in stdout

    def test_large_disjunction_satisfiability(self):
        """Large disjunction satisfiability."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=t", "--models", "p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10"]
        )
        assert "Satisfiable: True" in stdout


@pytest.mark.parametrize(
    "formula,expected",
    [
        ("((p & q) & r) |- (p & (q & r))", True),  # Associativity holds
        ("(p | (q & r)) |- ((p | q) & (p | r))", False),  # Distribution fails
        ("p & (q | r) |- (p & q) | (p & r)", True),  # Other distribution holds
        ("~~p |- p", True),  # Double negation
        ("(p -> q) |- (~q -> ~p)", True),  # Contraposition holds in Ferguson's system
        ("p |- (q -> q)", True),  # Tautology introduction holds classically
        ("(p & ~p) |- q", True),  # Ex falso holds vacuously
    ],
)
def test_logical_laws(formula, expected):
    """Test various logical laws in weak Kleene logic."""
    stdout, _, _ = run_wkrq_command(["--inference", formula])
    if expected:
        assert "✓ Valid inference" in stdout
    else:
        assert "✗ Invalid inference" in stdout
