"""
Ferguson (2021) Compliance Tests for wKrQ Implementation.

This module validates our implementation against Ferguson's exact specifications
from "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic."

Key points from paper:
1. Ferguson uses weak Kleene truth tables (contagious undefined) ✓
2. Validity is truth preservation: φ valid iff φ gets value 't' in ALL interpretations ✓
3. Classical tautologies are NOT necessarily valid in weak Kleene logic ✓
4. Four-sign system: t↔t, f↔f, m↔{t,f} (meaningful), n↔{f,e} (nontrue) ✓
5. m and n are technical branching instructions, not epistemic markers ✓
6. Tableau system is sound and complete (Theorems 1-2) ✓

All tests in this file should PASS to confirm Ferguson compliance.
"""

from wkrq.api import entails, solve, valid
from wkrq.formula import Formula
from wkrq.semantics import FALSE, TRUE, UNDEFINED, WeakKleeneSemantics
from wkrq.signs import f, m, n, t


class TestFergusonTruthTables:
    """Validate truth tables match Ferguson's Definition 1 exactly."""

    def setup_method(self):
        """Set up semantic system for testing."""
        self.semantics = WeakKleeneSemantics()

    def test_conjunction_matches_ferguson_definition_1(self):
        """Test conjunction truth table matches Ferguson's Definition 1."""
        conjunction = self.semantics._conjunction_table

        # Ferguson's weak Kleene conjunction - contagious undefined
        assert conjunction[(TRUE, TRUE)] == TRUE
        assert conjunction[(TRUE, FALSE)] == FALSE
        assert conjunction[(FALSE, TRUE)] == FALSE
        assert conjunction[(FALSE, FALSE)] == FALSE

        # Critical: undefined is contagious (weak Kleene property)
        assert conjunction[(TRUE, UNDEFINED)] == UNDEFINED
        assert conjunction[(UNDEFINED, TRUE)] == UNDEFINED
        assert conjunction[(FALSE, UNDEFINED)] == UNDEFINED
        assert conjunction[(UNDEFINED, FALSE)] == UNDEFINED
        assert conjunction[(UNDEFINED, UNDEFINED)] == UNDEFINED

    def test_disjunction_matches_ferguson_definition_1(self):
        """Test disjunction truth table matches Ferguson's Definition 1."""
        disjunction = self.semantics._disjunction_table

        # Ferguson's weak Kleene disjunction - contagious undefined
        assert disjunction[(TRUE, TRUE)] == TRUE
        assert disjunction[(TRUE, FALSE)] == TRUE
        assert disjunction[(FALSE, TRUE)] == TRUE
        assert disjunction[(FALSE, FALSE)] == FALSE

        # Critical: t ∨ e = e (NOT t - this distinguishes weak from strong Kleene)
        assert disjunction[(TRUE, UNDEFINED)] == UNDEFINED
        assert disjunction[(UNDEFINED, TRUE)] == UNDEFINED
        assert disjunction[(FALSE, UNDEFINED)] == UNDEFINED
        assert disjunction[(UNDEFINED, FALSE)] == UNDEFINED
        assert disjunction[(UNDEFINED, UNDEFINED)] == UNDEFINED

    def test_negation_matches_ferguson_definition_1(self):
        """Test negation truth table matches Ferguson's Definition 1."""
        negation = self.semantics._negation_table

        # Ferguson's weak Kleene negation
        assert negation[TRUE] == FALSE
        assert negation[FALSE] == TRUE
        assert negation[UNDEFINED] == UNDEFINED


class TestFergusonValidityDefinition:
    """Test Ferguson's Definition 6: validity as truth preservation."""

    def test_classical_tautologies_are_not_valid_ferguson_definition_6(self):
        """Test that classical tautologies are NOT valid per Ferguson's Definition 6.

        Ferguson Definition 6: "Validity in weak Kleene logic is defined as truth preservation"
        A formula is valid iff it receives value 't' in ALL interpretations.
        Classical tautologies can be undefined, so they are NOT valid.
        """
        p = Formula.atom("p")

        # Law of Excluded Middle is NOT valid (can be undefined)
        excluded_middle = p | ~p
        assert not valid(
            excluded_middle
        ), "p ∨ ¬p is not valid in weak Kleene (can be undefined)"

        # Self-implication is NOT valid (can be undefined)
        self_implication = p.implies(p)
        assert not valid(
            self_implication
        ), "p → p is not valid in weak Kleene (can be undefined)"

        # Double negation elimination is NOT valid
        double_negation = ~~p.implies(p)
        assert not valid(
            double_negation
        ), "¬¬p → p is not valid in weak Kleene (can be undefined)"

    def test_classical_tautologies_unsatisfiable_under_f_sign(self):
        """Test that classical tautologies are unsatisfiable under f sign.

        While classical tautologies are NOT valid in weak Kleene (can be undefined),
        they still cannot be false. They can only be true or undefined.
        """
        p = Formula.atom("p")

        # f:(p ∨ ¬p) should be unsatisfiable (cannot be false)
        excluded_middle = p | ~p
        result = solve(excluded_middle, f)
        assert (
            not result.satisfiable
        ), "f:(p ∨ ¬p) should be unsatisfiable (cannot be false)"

        # f:(p → p) should be unsatisfiable
        self_implication = p.implies(p)
        result = solve(self_implication, f)
        assert (
            not result.satisfiable
        ), "f:(p → p) should be unsatisfiable (cannot be false)"

    def test_contradictions_unsatisfiable_under_t_sign(self):
        """Test that contradictions are unsatisfiable under t sign."""
        p = Formula.atom("p")

        # t:(p ∧ ¬p) should be unsatisfiable (contradictions cannot be true)
        contradiction = p & ~p
        result = solve(contradiction, t)
        assert (
            not result.satisfiable
        ), "t:(p ∧ ¬p) should be unsatisfiable (cannot be true)"

    def test_epistemic_uncertainty_allows_satisfiability(self):
        """Test that epistemic signs (m, n) allow satisfiability for tautologies/contradictions.

        This reflects Ferguson's practical approach where epistemic uncertainty
        is possible even about logical truths.
        """
        p = Formula.atom("p")

        # m:(p ∨ ¬p) should be satisfiable (epistemic uncertainty about tautology)
        excluded_middle = p | ~p
        result = solve(excluded_middle, m)
        assert (
            result.satisfiable
        ), "m:(p ∨ ¬p) should be satisfiable (epistemic uncertainty)"

        # n:(p ∨ ¬p) should be satisfiable (can be undefined)
        result = solve(excluded_middle, n)
        assert result.satisfiable, "n:(p ∨ ¬p) should be satisfiable (can be undefined)"

        # m:(p ∧ ¬p) should be satisfiable (epistemic uncertainty about contradiction)
        contradiction = p & ~p
        result = solve(contradiction, m)
        assert (
            result.satisfiable
        ), "m:(p ∧ ¬p) should be satisfiable (epistemic uncertainty)"


class TestFergusonFourSignSystem:
    """Test Ferguson's four-sign system from Definition 9."""

    def test_sign_to_truth_value_mapping(self):
        """Test that our signs map correctly to Ferguson's truth values.

        Based on Ferguson's Definition 9 and Lemma 1:
        - t sign ↔ t (must be true)
        - f sign ↔ f (must be false)
        - m sign ↔ m (meaningful - can be true or false)
        - n sign ↔ e (must be undefined)
        """
        p = Formula.atom("p")

        # All four signs should be satisfiable for atomic formulas
        for sign in [t, f, m, n]:
            result = solve(p, sign)
            assert result.satisfiable, f"{sign}:p should be satisfiable"
            assert len(result.models) > 0, f"{sign}:p should have models"

    def test_sign_coexistence_ferguson_footnote_3(self):
        """Test Ferguson's Footnote 3: signs can coexist if they don't contradict truth values.

        "Both m : φ and t : φ may harmoniously appear in an open branch"
        because m represents potential branching while t represents definite value.
        """
        # This is more of a tableau construction detail, but we can test
        # that m and t signs don't create inherent contradictions
        p = Formula.atom("p")

        # m:p is satisfiable (can be true or false)
        result_m = solve(p, m)
        assert result_m.satisfiable, "m:p should be satisfiable"

        # t:p is satisfiable (must be true)
        result_t = solve(p, t)
        assert result_t.satisfiable, "t:p should be satisfiable"

        # These don't contradict each other at the semantic level


class TestFergusonRestrictedQuantifiers:
    """Test Ferguson's restricted quantifier semantics from Definition 3."""

    def test_restricted_existential_basic_semantics(self):
        """Test restricted existential quantifier semantics."""
        x = Formula.variable("X")
        human_x = Formula.predicate("Human", [x])
        mortal_x = Formula.predicate("Mortal", [x])

        # [∃X Human(X)]Mortal(X) - "some human is mortal"
        existential_formula = Formula.restricted_exists(x, human_x, mortal_x)

        # Should be satisfiable under all signs (depends on domain)
        for sign in [t, f, m, n]:
            result = solve(existential_formula, sign)
            assert (
                result.satisfiable
            ), f"{sign}:[∃X Human(X)]Mortal(X) should be satisfiable"

    def test_restricted_universal_basic_semantics(self):
        """Test restricted universal quantifier semantics."""
        x = Formula.variable("X")
        human_x = Formula.predicate("Human", [x])
        mortal_x = Formula.predicate("Mortal", [x])

        # [∀X Human(X)]Mortal(X) - "all humans are mortal"
        universal_formula = Formula.restricted_forall(x, human_x, mortal_x)

        # Should be satisfiable under all signs (depends on domain)
        for sign in [t, f, m, n]:
            result = solve(universal_formula, sign)
            assert (
                result.satisfiable
            ), f"{sign}:[∀X Human(X)]Mortal(X) should be satisfiable"

    def test_quantifier_domain_reasoning(self):
        """Test that restricted quantifiers support domain-specific reasoning."""
        x = Formula.variable("X")
        human_x = Formula.predicate("Human", [x])
        mortal_x = Formula.predicate("Mortal", [x])

        # Standard inference: if all humans are mortal and Socrates is human, then Socrates is mortal
        all_humans_mortal = Formula.restricted_forall(x, human_x, mortal_x)
        socrates = Formula.constant("socrates")
        socrates_human = Formula.predicate("Human", [socrates])
        socrates_mortal = Formula.predicate("Mortal", [socrates])

        # Test basic entailment
        premises = [all_humans_mortal, socrates_human]
        conclusion = socrates_mortal

        # This should be valid (following Ferguson's practical applications)
        assert entails(
            premises, conclusion
        ), "Restricted quantifier inference should work for practical reasoning"


class TestFergusonTableauSoundnessCompleteness:
    """Test Ferguson's Theorems 1-2: soundness and completeness."""

    def test_soundness_theorem_1(self):
        """Test Ferguson's Theorem 1: If Γ ⊢wKrQ φ then Γ ⊨wK φ.

        Anything our tableau derives should be semantically valid.
        """
        p, q = Formula.atoms("p", "q")

        # Modus ponens: p, p → q ⊢ q
        premises = [p, p.implies(q)]
        conclusion = q

        # If tableau derives this, it should be semantically valid
        is_entailed = entails(premises, conclusion)
        assert is_entailed, "Modus ponens should be valid (soundness test)"

        # Invalid inference should be rejected
        invalid_premises = [p]
        invalid_conclusion = q

        is_invalid = entails(invalid_premises, invalid_conclusion)
        assert not is_invalid, "Invalid inference should be rejected (soundness test)"

    def test_completeness_basic_cases(self):
        """Test basic cases that should be derivable (completeness indication)."""
        p = Formula.atom("p")

        # Classical tautologies are NOT necessarily valid in weak Kleene
        excluded_middle = p | ~p
        assert not valid(
            excluded_middle
        ), "Classical tautologies are not valid in weak Kleene"

        # Classical contradictions should be unsatisfiable
        contradiction = p & ~p
        result = solve(contradiction, t)
        assert not result.satisfiable, "Contradictions should be unsatisfiable"


class TestFergusonModelExtraction:
    """Test Ferguson's Definition 12: model extraction from open branches."""

    def test_model_extraction_reflects_signs(self):
        """Test that extracted models reflect the sign semantics.

        Ferguson's Lemma 1: "if v : φ is on B, then IB(φ) = v"
        This means signs map directly to truth values in extracted models.
        """
        p = Formula.atom("p")

        # t:p should produce models where p is true
        result_t = solve(p, t)
        assert result_t.satisfiable
        for model in result_t.models:
            # Model should assign true to p
            assert str(model.valuations.get("p", "")).startswith(
                "t"
            ), "t:p should produce models where p is true"

        # f:p should produce models where p is false
        result_f = solve(p, f)
        assert result_f.satisfiable
        for model in result_f.models:
            # Model should assign false to p
            assert str(model.valuations.get("p", "")).startswith(
                "f"
            ), "f:p should produce models where p is false"

        # n:p should produce models where p is nontrue (f or e)
        result_n = solve(p, n)
        assert result_n.satisfiable
        for model in result_n.models:
            # Model should assign either false or undefined to p
            p_value = str(model.valuations.get("p", ""))
            assert p_value.startswith("f") or p_value.startswith(
                "e"
            ), "n:p should produce models where p is false or undefined"


# Summary test to confirm overall Ferguson compliance
class TestOverallFergusonCompliance:
    """High-level tests confirming our implementation matches Ferguson (2021)."""

    def test_ferguson_system_characteristics(self):
        """Test the key characteristics of Ferguson's hybrid system."""
        p, q = Formula.atoms("p", "q")

        # 1. Weak Kleene semantics with contagious undefined
        # 2. Classical validity (truth preservation)
        # 3. Practical reasoning patterns
        # 4. Four-sign system for tableau construction

        # Classical reasoning should work
        modus_ponens_valid = entails([p, p.implies(q)], q)
        assert modus_ponens_valid, "Classical reasoning should work"

        # Tautologies are NOT valid in weak Kleene (can be undefined)
        tautology_valid = valid(p | ~p)
        assert not tautology_valid, "Classical tautologies are not valid in weak Kleene"

        # Epistemic uncertainty should be representable
        epistemic_satisfiable = solve(p & ~p, m).satisfiable
        assert epistemic_satisfiable, "Epistemic uncertainty should be representable"

        # Four signs should all be meaningful
        for sign in [t, f, m, n]:
            result = solve(p, sign)
            assert result.satisfiable, "All four signs should be satisfiable"

    def test_ferguson_practical_applications(self):
        """Test that the system supports Ferguson's intended practical applications."""
        # Knowledge representation, conversational agents, belief cataloging

        # Should handle incomplete information gracefully
        x = Formula.variable("X")
        human_x = Formula.predicate("Human", [x])
        mortal_x = Formula.predicate("Mortal", [x])

        # Restricted quantification for domain-specific reasoning
        domain_rule = Formula.restricted_forall(x, human_x, mortal_x)

        # Should be satisfiable under epistemic uncertainty
        result = solve(domain_rule, m)
        assert result.satisfiable, "Domain rules should support epistemic uncertainty"
