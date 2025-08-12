"""
Exact compliance tests for Ferguson's tableau system.

These tests verify that our implementation exactly matches
the tableau rules from Ferguson (2021) Definition 9.
"""

import os

# We need to import ferguson_rules directly since it's not in __init__.py
import sys

from wkrq.formula import Formula
from wkrq.signs import SignedFormula, e, f, m, n, t
from wkrq.tableau import solve

# Add src directory to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "wkrq"))
if os.path.exists(os.path.join(src_path, "wkrq_rules.py")):
    sys.path.insert(0, os.path.dirname(src_path))
    from wkrq.wkrq_rules import (
        get_conjunction_rule,
        get_disjunction_rule,
        get_implication_rule,
        get_negation_rule,
    )


class TestFergusonNegationRules:
    """Test negation rules from Definition 9."""

    def test_t_negation(self):
        """Test t : ~φ → f : φ"""
        p = Formula.atom("p")
        neg_p = ~p

        signed_formula = SignedFormula(t, neg_p)
        rule = get_negation_rule(signed_formula)

        assert rule is not None
        assert rule.name == "t-negation"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 1
        assert rule.conclusions[0][0] == SignedFormula(f, p)

    def test_f_negation(self):
        """Test f : ~φ → t : φ"""
        p = Formula.atom("p")
        neg_p = ~p

        signed_formula = SignedFormula(f, neg_p)
        rule = get_negation_rule(signed_formula)

        assert rule is not None
        assert rule.name == "f-negation"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 1
        assert rule.conclusions[0][0] == SignedFormula(t, p)

    def test_e_negation(self):
        """Test e : ~φ → e : φ"""
        p = Formula.atom("p")
        neg_p = ~p

        signed_formula = SignedFormula(e, neg_p)
        rule = get_negation_rule(signed_formula)

        assert rule is not None
        assert rule.name == "e-negation"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 1
        assert rule.conclusions[0][0] == SignedFormula(e, p)

    def test_m_negation(self):
        """Test m : ~φ → (f : φ) + (t : φ)"""
        p = Formula.atom("p")
        neg_p = ~p

        signed_formula = SignedFormula(m, neg_p)
        rule = get_negation_rule(signed_formula)

        assert rule is not None
        assert rule.name == "m-negation"
        assert len(rule.conclusions) == 2  # Branching
        assert rule.conclusions[0][0] == SignedFormula(f, p)
        assert rule.conclusions[1][0] == SignedFormula(t, p)

    def test_n_negation(self):
        """Test n : ~φ → (t : φ) + (e : φ)"""
        p = Formula.atom("p")
        neg_p = ~p

        signed_formula = SignedFormula(n, neg_p)
        rule = get_negation_rule(signed_formula)

        assert rule is not None
        assert rule.name == "n-negation"
        assert len(rule.conclusions) == 2  # Branching
        assert rule.conclusions[0][0] == SignedFormula(t, p)
        assert rule.conclusions[1][0] == SignedFormula(e, p)


class TestFergusonConjunctionRules:
    """Test conjunction rules from Definition 9."""

    def test_t_conjunction(self):
        """Test t : φ ∧ ψ → t : φ ○ t : ψ"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        conj = p & q

        signed_formula = SignedFormula(t, conj)
        rule = get_conjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "t-conjunction"
        assert len(rule.conclusions) == 1  # Non-branching
        assert len(rule.conclusions[0]) == 2
        assert rule.conclusions[0][0] == SignedFormula(t, p)
        assert rule.conclusions[0][1] == SignedFormula(t, q)

    def test_f_conjunction(self):
        """Test f : φ ∧ ψ → branches for all ways to get f"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        conj = p & q

        signed_formula = SignedFormula(f, conj)
        rule = get_conjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "f-conjunction"
        assert len(rule.conclusions) == 4  # Four branches
        # Should have branches for: f:p, f:q, e:p, e:q
        assert SignedFormula(f, p) in [c[0] for c in rule.conclusions]
        assert SignedFormula(f, q) in [c[0] for c in rule.conclusions]
        assert SignedFormula(e, p) in [c[0] for c in rule.conclusions]
        assert SignedFormula(e, q) in [c[0] for c in rule.conclusions]

    def test_e_conjunction(self):
        """Test e : φ ∧ ψ → (e : φ) + (e : ψ)"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        conj = p & q

        signed_formula = SignedFormula(e, conj)
        rule = get_conjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "e-conjunction"
        assert len(rule.conclusions) == 2  # Two branches
        assert rule.conclusions[0][0] == SignedFormula(e, p)
        assert rule.conclusions[1][0] == SignedFormula(e, q)


class TestFergusonDisjunctionRules:
    """Test disjunction rules from Definition 9."""

    def test_t_disjunction(self):
        """Test t : φ ∨ ψ → (t : φ) + (t : ψ)"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        disj = p | q

        signed_formula = SignedFormula(t, disj)
        rule = get_disjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "t-disjunction"
        assert len(rule.conclusions) == 2  # Branching
        assert rule.conclusions[0][0] == SignedFormula(t, p)
        assert rule.conclusions[1][0] == SignedFormula(t, q)

    def test_f_disjunction(self):
        """Test f : φ ∨ ψ → f : φ ○ f : ψ"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        disj = p | q

        signed_formula = SignedFormula(f, disj)
        rule = get_disjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "f-disjunction"
        assert len(rule.conclusions) == 1  # Non-branching
        assert len(rule.conclusions[0]) == 2
        assert rule.conclusions[0][0] == SignedFormula(f, p)
        assert rule.conclusions[0][1] == SignedFormula(f, q)

    def test_e_disjunction(self):
        """Test e : φ ∨ ψ → (e : φ) + (e : ψ)"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        disj = p | q

        signed_formula = SignedFormula(e, disj)
        rule = get_disjunction_rule(signed_formula)

        assert rule is not None
        assert rule.name == "e-disjunction"
        assert len(rule.conclusions) == 2  # Two branches
        assert rule.conclusions[0][0] == SignedFormula(e, p)
        assert rule.conclusions[1][0] == SignedFormula(e, q)


class TestFergusonImplicationRules:
    """Test implication rules (as ~φ ∨ ψ)."""

    def test_t_implication(self):
        """Test t : φ → ψ as t : ~φ ∨ ψ"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        impl = p.implies(q)

        signed_formula = SignedFormula(t, impl)
        rule = get_implication_rule(signed_formula)

        assert rule is not None
        assert rule.name == "t-implication"
        assert len(rule.conclusions) == 2  # Branching
        assert rule.conclusions[0][0] == SignedFormula(f, p)  # ~φ = t means φ = f
        assert rule.conclusions[1][0] == SignedFormula(t, q)

    def test_f_implication(self):
        """Test f : φ → ψ as f : ~φ ∨ ψ"""
        p = Formula.atom("p")
        q = Formula.atom("q")
        impl = p.implies(q)

        signed_formula = SignedFormula(f, impl)
        rule = get_implication_rule(signed_formula)

        assert rule is not None
        assert rule.name == "f-implication"
        assert len(rule.conclusions) == 1  # Non-branching
        assert len(rule.conclusions[0]) == 2
        assert rule.conclusions[0][0] == SignedFormula(t, p)  # ~φ = f means φ = t
        assert rule.conclusions[0][1] == SignedFormula(f, q)


class TestFergusonTableauBehavior:
    """Test complete tableau behavior with Ferguson rules."""

    def test_classical_tautology_not_valid(self):
        """Test that p ∨ ¬p is not valid (can be undefined)."""
        p = Formula.atom("p")
        excluded_middle = p | ~p

        # Check if it can be false
        result_f = solve(excluded_middle, f)
        assert not result_f.satisfiable  # Cannot be false

        # Check if it can be undefined
        result_e = solve(excluded_middle, e)
        assert result_e.satisfiable  # Can be undefined!

        # Therefore not valid in weak Kleene

    def test_contradiction_behavior(self):
        """Test that p ∧ ¬p behaves correctly."""
        p = Formula.atom("p")
        contradiction = p & ~p

        # Cannot be true
        result_t = solve(contradiction, t)
        assert not result_t.satisfiable

        # Can be false
        result_f = solve(contradiction, f)
        assert result_f.satisfiable

        # Can be undefined
        result_e = solve(contradiction, e)
        assert result_e.satisfiable

    def test_branch_closure(self):
        """Test that branches close correctly per Definition 10."""
        p = Formula.atom("p")

        # A branch with both t:p and f:p should close
        # This is tested indirectly through tableau construction

        # Formula that forces contradiction: p ∧ ¬p under t
        formula = p & ~p
        result = solve(formula, t)
        assert not result.satisfiable
        assert result.closed_branches > 0

    def test_m_sign_branching(self):
        """Test that m sign creates proper branches for compound formulas."""
        p = Formula.atom("p")
        q = Formula.atom("q")

        # m:(p ∧ q) should create branches
        conj = p & q
        result = solve(conj, m)
        assert result.satisfiable
        assert len(result.models) > 0

        # For atomic formulas, m doesn't create branches but allows both values
        result_atomic = solve(p, m)
        assert result_atomic.satisfiable
        # Model extraction chooses one value (implementation detail)

    def test_n_sign_branching(self):
        """Test that n sign creates proper branches for compound formulas."""
        p = Formula.atom("p")
        q = Formula.atom("q")

        # n:(p ∧ q) should create branches
        conj = p & q
        result = solve(conj, n)
        assert result.satisfiable
        assert len(result.models) > 0

        # For atomic formulas, n doesn't create branches but allows f or e
        result_atomic = solve(p, n)
        assert result_atomic.satisfiable
        # Model extraction chooses one value (implementation detail)


class TestFergusonQuantifierRules:
    """Test restricted quantifier rules from Definition 9."""

    def test_t_restricted_exists_basic(self):
        """Test t:[∃x P(x)]Q(x) → t:P(c) ○ t:Q(c)"""
        x = Formula.variable("X")
        p_x = Formula.predicate("P", [x])
        q_x = Formula.predicate("Q", [x])

        exists_formula = Formula.restricted_exists(x, p_x, q_x)
        result = solve(exists_formula, t)

        # Should be satisfiable
        assert result.satisfiable

        # Should introduce a constant and assert both P(c) and Q(c)
        # This is tested through the tableau construction

    def test_f_restricted_forall_basic(self):
        """Test f:[∀x P(x)]Q(x) → t:P(c) ○ f:Q(c)"""
        x = Formula.variable("X")
        p_x = Formula.predicate("P", [x])
        q_x = Formula.predicate("Q", [x])

        forall_formula = Formula.restricted_forall(x, p_x, q_x)
        result = solve(forall_formula, f)

        # Should be satisfiable
        assert result.satisfiable

        # Should find a counterexample with P(c) true and Q(c) false
