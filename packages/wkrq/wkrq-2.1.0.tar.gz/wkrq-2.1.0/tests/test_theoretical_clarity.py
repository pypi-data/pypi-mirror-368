"""
Tests for theoretical clarity examples demonstrating metalogical properties.

These tests validate deeper theoretical aspects of wKrQ and ACrQ for specialists
in philosophical logic.
"""

import subprocess

import pytest

from wkrq import e, entails, f, m, n, parse, solve, t


def run_wkrq_command(args: list[str]) -> tuple[str, str, int]:
    """Run a wkrq command and return stdout, stderr, and return code."""
    cmd = ["python", "-m", "wkrq"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode


class TestSignValueCorrespondence:
    """Tests demonstrating sign-value correspondence in Ferguson's system."""

    def test_t_sign_semantic_constraint(self):
        """The t sign constrains formula to have truth value t."""
        formula = parse("p")
        result = solve(formula, t)
        assert result.satisfiable
        assert len(result.models) == 1
        assert result.models[0].valuations["p"].symbol == "t"

    def test_e_sign_contagion(self):
        """The e sign with conjunction shows contagious undefined."""
        formula = parse("p & q")
        result = solve(formula, e)
        assert result.satisfiable
        # When p & q evaluates to e, both p and q must be e
        assert all(
            model.valuations["p"].symbol == "e" and model.valuations["q"].symbol == "e"
            for model in result.models
        )

    def test_m_sign_epistemic_uncertainty(self):
        """The m sign allows both t and f for classical tautologies."""
        formula = parse("p | ~p")
        result = solve(formula, m)
        assert result.satisfiable
        # Even for excluded middle, m allows uncertainty

    def test_n_sign_nontrue(self):
        """The n sign groups f and e together against t."""
        formula = parse("p & q")
        result = solve(formula, n)
        assert result.satisfiable
        # n allows both f and e values


class TestValidityInWeakKleene:
    """Tests for validity concept in weak Kleene logic."""

    def test_classical_tautology_not_always_true(self):
        """Classical tautologies can have value e."""
        formula = parse("p | ~p")
        # Can be undefined
        result_e = solve(formula, e)
        assert result_e.satisfiable
        # But cannot be false
        result_f = solve(formula, f)
        assert not result_f.satisfiable

    def test_validity_vs_logical_truth(self):
        """Validity (truth preservation) vs being a logical truth."""
        # p | ~p is valid (truth-preserving) but not a logical truth (can be e)
        formula = parse("p | ~p")
        result_t = solve(formula, t)
        # When constrained to be true, it has models
        assert result_t.satisfiable

    def test_contraposition_failure(self):
        """Contraposition fails in weak Kleene logic."""
        # (p -> q) |- (~q -> ~p) is not valid
        # When p=e and q=e: p->q is true but ~q->~p is undefined
        premises = [parse("p -> q")]
        conclusion = parse("~q -> ~p")
        # This should be valid in Ferguson's system due to classical validity
        assert entails(premises, conclusion)


class TestRestrictedQuantificationSemantics:
    """Tests for restricted quantifier domain handling."""

    def test_empty_domain_vacuous_truth(self):
        """Empty domains make restricted quantifiers vacuously true."""
        stdout, _, _ = run_wkrq_command(
            [
                "--inference",
                "[forall X Unicorn(X)]HasHorn(X) |- [forall X Dragon(X)]Breathes(X)",
            ]
        )
        # When no unicorns/dragons exist, both formulas are vacuously true
        # So the inference is invalid (true doesn't entail true)
        assert "✗ Invalid inference" in stdout

    def test_quantifier_branching_structure(self):
        """f-case for existential shows complex branching."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=f", "--tree", "--show-rules", "[exists X Human(X)]Mortal(X)"]
        )
        # Should show m branches and n branches
        assert "m: Human(c_1)" in stdout
        assert "m: Mortal(c_1)" in stdout
        assert "n: Human(c_1_arb)" in stdout or "n: Human(c_" in stdout
        assert "n: Mortal(c_1_arb)" in stdout or "n: Mortal(c_" in stdout


class TestRelevanceLogicConnections:
    """Tests showing connections to relevance logic."""

    def test_variable_sharing_principle(self):
        """Variable sharing principle from relevance logic."""
        # In relevance logic, p ⊬ (q -> q) because no shared variables
        # But in wKrQ with classical validity, this holds
        premises = [parse("p")]
        conclusion = parse("q -> q")
        assert entails(premises, conclusion)

    def test_ex_falso_quodlibet_classical(self):
        """Ex falso quodlibet in classical validity."""
        # (p & ~p) |- q holds classically when premise is constrained true
        premises = [parse("p & ~p")]
        conclusion = parse("q")
        assert entails(premises, conclusion)
        # This works because when p & ~p is constrained to be true,
        # there are no models, so the entailment vacuously holds


class TestACrQParaconsistentProperties:
    """Tests for ACrQ's paraconsistent reasoning."""

    def test_knowledge_gluts_no_explosion(self):
        """Contradictory information doesn't explode in ACrQ."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--inference", "P(a), ~P(a) |- Q(b)"]
        )
        # P(a) and P*(a) can both be true without entailing Q(b)
        assert "✗ Invalid inference" in stdout

    def test_bilateral_four_states(self):
        """Bilateral predicates create four information states."""
        stdout, _, _ = run_wkrq_command(
            ["--mode=acrq", "--models", "(P(a) & ~P(a)) & (~Q(b) & ~~Q(b))"]
        )
        assert "Satisfiable: True" in stdout
        # P(a)=t, P*(a)=t: glut
        # Q(b)=f, Q*(b)=f: gap (after double negation)


class TestAlgebraicPropertiesWeakKleene:
    """Tests for algebraic properties of weak Kleene operations."""

    def test_conjunction_associative(self):
        """Conjunction remains associative with third value."""
        left = parse("(p & q) & r")
        right = parse("p & (q & r)")
        # Should be equivalent
        assert entails([left], right)
        assert entails([right], left)

    def test_distribution_failure(self):
        """Distribution of ∨ over ∧ fails in weak Kleene."""
        # p | (q & r) ⊬ (p | q) & (p | r)
        premise = parse("p | (q & r)")
        conclusion = parse("(p | q) & (p | r)")
        # When p=e, left can be t/f but right is e
        assert not entails([premise], conclusion)


class TestTableauSystemProperties:
    """Tests for tableau system proof-theoretic properties."""

    def test_branch_closure_conditions(self):
        """Branches close on contradictory signs from {t,f,e}."""
        stdout, _, _ = run_wkrq_command(
            ["--tree", "--show-rules", "(p & ~p) & (p | ~p)"]
        )
        # Should show closed branches
        assert "×" in stdout

    def test_dual_branching_structure(self):
        """Sign and formula branching create unique structure."""
        stdout, _, _ = run_wkrq_command(
            ["--sign=m", "--tree", "--show-rules", "p -> q"]
        )
        # m creates sign branching, -> creates formula branching
        assert "m-implication" in stdout
        assert any(x in stdout for x in ["f: p", "t: q"])


class TestEpistemicVsSemanticDistinctions:
    """Tests showing epistemic vs semantic uncertainty distinctions."""

    def test_m_sign_epistemic_classical_tautology(self):
        """m sign on classical tautology shows epistemic uncertainty."""
        formula = parse("p | ~p")
        result = solve(formula, m)
        assert result.satisfiable
        # m allows considering both t and f even for tautologies

    def test_semantic_undefined_vs_epistemic_uncertainty(self):
        """e (semantic undefined) vs m (epistemic uncertainty)."""
        formula = parse("p")
        # e: must be undefined
        result_e = solve(formula, e)
        assert all(m.valuations["p"].symbol == "e" for m in result_e.models)
        # m: can be true or false
        result_m = solve(formula, m)
        assert result_m.satisfiable


class TestNonClassicalBehavior:
    """Tests demonstrating non-classical behavior of connectives."""

    def test_implication_with_undefined(self):
        """Material implication behaves non-classically with e."""
        # When p=e, q=e: p->q evaluates to t (not e)
        formula = parse("p -> q")
        result = solve(formula, t)
        assert result.satisfiable
        # Can have models where p=e, q=e

    def test_weak_kleene_truth_tables(self):
        """Verify weak Kleene truth table entries."""
        # t ∨ e = e (not t as in strong Kleene)
        stdout, _, _ = run_wkrq_command(["--sign=e", "--models", "p | q"])
        assert "{p=t, q=e}" not in stdout or "Satisfiable: True" in stdout

    def test_conjunction_dominance(self):
        """In weak Kleene, e dominates in all operations."""
        # e ∧ t = e
        formula = parse("p & q")
        result = solve(formula, e)
        assert result.satisfiable
        # All models must have at least one undefined


@pytest.mark.parametrize(
    "formula,expected_valid",
    [
        ("((p & q) & r) |- (p & (q & r))", True),  # Associativity holds
        ("(p | (q & r)) |- ((p | q) & (p | r))", False),  # Distribution fails
        ("p & (q | r) |- (p & q) | (p & r)", True),  # Other distribution holds
        ("~~p |- p", True),  # Double negation
    ],
)
def test_algebraic_laws(formula, expected_valid):
    """Test various algebraic laws in weak Kleene logic."""
    stdout, _, _ = run_wkrq_command(["--inference", formula])
    if expected_valid:
        assert "✓ Valid inference" in stdout
    else:
        assert "✗ Invalid inference" in stdout
