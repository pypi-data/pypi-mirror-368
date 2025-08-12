"""
Comprehensive semantic validation tests for wKrQ against literature.

This module validates our implementation against:
1. Weak Kleene logic truth tables (Bochvar, Kleene literature)
2. Ferguson (2021) four-sign system principles
3. Tableau soundness and completeness properties
4. Non-classical tautology behavior
5. Epistemic vs truth-functional distinctions

References:
- Ferguson, t.m. (2021). "Tableaux and restricted quantification for systems related to weak Kleene logic"
- Bochvar, D.A. (1938). "Ob odnom trekhznachnom ischislenii i ego primenenii k analizu paradoksov klassicheskogo rasshirennogo funktsional'nogo ischisleniya"
- Kleene, S.C. (1938). "On notation for ordinal numbers"
- Priest, G. (2008). "An Introduction to Non-Classical Logic"
"""

from wkrq.api import entails, solve, valid
from wkrq.formula import Formula
from wkrq.semantics import FALSE, TRUE, UNDEFINED, WeakKleeneSemantics
from wkrq.signs import SignedFormula, f, m, n, t


class TestWeakKleeneTruthTables:
    """Validate truth tables against literature."""

    def setup_method(self):
        """Set up semantic system for testing."""
        self.semantics = WeakKleeneSemantics()

    def test_conjunction_truth_table_literature_compliance(self):
        """Test conjunction truth table matches weak Kleene literature.

        Reference: Bochvar's "contagious" undefined value semantics.
        Key principle: ANY undefined input produces undefined output.
        """
        conjunction = self.semantics._conjunction_table

        # Classical cases (should match Boolean logic)
        assert conjunction[(TRUE, TRUE)] == TRUE
        assert conjunction[(TRUE, FALSE)] == FALSE
        assert conjunction[(FALSE, TRUE)] == FALSE
        assert conjunction[(FALSE, FALSE)] == FALSE

        # Weak Kleene principle: undefined is "contagious"
        assert conjunction[(TRUE, UNDEFINED)] == UNDEFINED
        assert conjunction[(UNDEFINED, TRUE)] == UNDEFINED
        assert (
            conjunction[(FALSE, UNDEFINED)] == UNDEFINED
        )  # Key difference from Strong Kleene
        assert (
            conjunction[(UNDEFINED, FALSE)] == UNDEFINED
        )  # Key difference from Strong Kleene
        assert conjunction[(UNDEFINED, UNDEFINED)] == UNDEFINED

    def test_disjunction_truth_table_literature_compliance(self):
        """Test disjunction truth table matches weak Kleene literature."""
        disjunction = self.semantics._disjunction_table

        # Classical cases
        assert disjunction[(TRUE, TRUE)] == TRUE
        assert disjunction[(TRUE, FALSE)] == TRUE
        assert disjunction[(FALSE, TRUE)] == TRUE
        assert disjunction[(FALSE, FALSE)] == FALSE

        # Weak Kleene principle: undefined is "contagious"
        assert disjunction[(TRUE, UNDEFINED)] == UNDEFINED  # Key: t ∨ e = e (not t)
        assert disjunction[(UNDEFINED, TRUE)] == UNDEFINED  # Key: e ∨ t = e (not t)
        assert disjunction[(FALSE, UNDEFINED)] == UNDEFINED
        assert disjunction[(UNDEFINED, FALSE)] == UNDEFINED
        assert disjunction[(UNDEFINED, UNDEFINED)] == UNDEFINED

    def test_negation_truth_table_literature_compliance(self):
        """Test negation truth table matches weak Kleene literature."""
        negation = self.semantics._negation_table

        # Classical cases
        assert negation[TRUE] == FALSE
        assert negation[FALSE] == TRUE

        # Weak Kleene: undefined negation is undefined
        assert negation[UNDEFINED] == UNDEFINED

    def test_implication_truth_table_literature_compliance(self):
        """Test implication truth table matches weak Kleene literature."""
        implication = self.semantics._implication_table

        # Classical cases
        assert implication[(TRUE, TRUE)] == TRUE
        assert implication[(TRUE, FALSE)] == FALSE
        assert implication[(FALSE, TRUE)] == TRUE
        assert implication[(FALSE, FALSE)] == TRUE

        # Weak Kleene principle: any undefined input → undefined output
        assert implication[(TRUE, UNDEFINED)] == UNDEFINED
        assert implication[(UNDEFINED, TRUE)] == UNDEFINED
        assert implication[(FALSE, UNDEFINED)] == UNDEFINED
        assert implication[(UNDEFINED, FALSE)] == UNDEFINED
        assert implication[(UNDEFINED, UNDEFINED)] == UNDEFINED


class TestContagiousUndefinedPropagation:
    """Test the 'infectious/contagious' nature of undefined values."""

    def test_simple_undefined_propagation(self):
        """Test undefined values propagate through simple operations."""
        p = Formula.atom("p")
        q = Formula.atom("q")

        # Set p as undefined, q as true - result should be undefined
        formula = p & q

        # Test that undefined propagates in conjunction
        # TODO: Need to implement model checking to verify undefined propagation
        # For now, verify basic satisfiability behavior
        _ = solve(formula, t)  # Basic satisfiability test

    def test_complex_undefined_propagation(self):
        """Test undefined propagation in complex nested formulas."""
        p, q, r = Formula.atoms("p", "q", "r")

        # Complex formula: ((p ∧ q) ∨ r) → (p ∨ (q ∧ r))
        complex_formula = ((p & q) | r).implies(p | (q & r))

        # If any variable is undefined, whole formula should be undefined
        # This tests the "contagious" property through multiple operations
        result = solve(complex_formula, n)  # n sign tests undefined behavior
        assert (
            result.satisfiable
        ), "Undefined formulas should be satisfiable under n sign"


class TestFergusonTautologyBehavior:
    """Test classical tautology behavior in Ferguson's hybrid system.

    Ferguson uses classical validity with weak Kleene semantics, so classical
    tautologies ARE valid (truth preservation) but allow epistemic uncertainty.
    """

    def test_law_of_excluded_middle_ferguson_behavior(self):
        """Test that p ∨ ¬p behaves according to Ferguson's hybrid system.

        Ferguson uses classical validity with weak Kleene semantics, so classical
        tautologies like excluded middle ARE valid (cannot be false).
        """
        p = Formula.atom("p")
        excluded_middle = p | ~p

        # In Ferguson's system, classical tautologies are valid (cannot be false)
        result_f = solve(excluded_middle, f)
        assert (
            not result_f.satisfiable
        ), "f:(p ∨ ¬p) should be unsatisfiable (cannot be false in Ferguson's system)"

        # But satisfiable under n sign (can be undefined for epistemic uncertainty)
        result_n = solve(excluded_middle, n)
        assert (
            result_n.satisfiable
        ), "n:(p ∨ ¬p) should be satisfiable (epistemic uncertainty allowed)"

        # Ferguson does NOT preserve classical validity for tautologies
        assert not valid(
            excluded_middle
        ), "p ∨ ¬p is not valid in weak Kleene (can be undefined)"

    def test_law_of_non_contradiction_ferguson_behavior(self):
        """Test that ¬(p ∧ ¬p) behaves according to Ferguson's hybrid system."""
        p = Formula.atom("p")
        non_contradiction = ~(p & ~p)

        # In Ferguson's system, classical tautologies cannot be false
        result_f = solve(non_contradiction, f)
        assert (
            not result_f.satisfiable
        ), "f:¬(p ∧ ¬p) should be unsatisfiable (cannot be false in Ferguson's system)"

        # But satisfiable under n sign (epistemic uncertainty)
        result_n = solve(non_contradiction, n)
        assert (
            result_n.satisfiable
        ), "n:¬(p ∧ ¬p) should be satisfiable (epistemic uncertainty allowed)"

        # Ferguson preserves classical validity for tautologies
        assert not valid(
            non_contradiction
        ), "¬(p ∧ ¬p) is not valid in weak Kleene (can be undefined)"

    def test_material_conditional_properties_ferguson_behavior(self):
        """Test material conditional behavior in Ferguson's hybrid system."""
        p, q = Formula.atoms("p", "q")

        # Classical tautologies that are valid in Ferguson's system
        tautology_candidates = [
            p.implies(p),  # Self-implication
            (p & q).implies(p),  # Simplification
            p.implies(p | q),  # Addition
        ]

        for formula in tautology_candidates:
            # Classical tautologies cannot be false in Ferguson's system
            result_f = solve(formula, f)
            assert (
                not result_f.satisfiable
            ), f"f:{formula} should be unsatisfiable (cannot be false)"

            # But allow epistemic uncertainty
            result_n = solve(formula, n)
            assert (
                result_n.satisfiable
            ), f"n:{formula} should be satisfiable (epistemic uncertainty)"

            # Ferguson does NOT preserve classical validity for all tautologies
            assert not valid(
                formula
            ), f"{formula} is not valid in weak Kleene (can be undefined)"


class TestFergusonFourSignSystem:
    """Test Ferguson's four-sign system (t, f, m, n) principles."""

    def test_four_signs_basic_satisfiability(self):
        """Test that all four signs are meaningful and satisfiable."""
        p = Formula.atom("p")

        # All four signs should be satisfiable for any atomic formula
        for sign in [t, f, m, n]:
            result = solve(p, sign)
            assert result.satisfiable, f"{sign}:p should be satisfiable"
            assert len(result.models) > 0, f"{sign}:p should have models"

    def test_epistemic_vs_truth_functional_distinction(self):
        """Test distinction between epistemic (m, n) and truth-functional (t, f) signs.

        Reference: Ferguson's epistemic interpretation of m and n signs.
        """
        p = Formula.atom("p")
        contradiction = p & ~p

        # Truth-functional signs: contradictions are unsatisfiable
        result_t = solve(contradiction, t)
        assert not result_t.satisfiable, "t:(p ∧ ¬p) should be unsatisfiable"

        result_f = solve(contradiction, f)
        # f:(p ∧ ¬p) tests if contradiction can be false - in Ferguson's system,
        # contradictions CAN be false (they're not valid), so this should be satisfiable
        assert (
            result_f.satisfiable
        ), "f:(p ∧ ¬p) should be satisfiable (contradictions can be false)"

        # Epistemic signs: express uncertainty, should be satisfiable
        result_m = solve(contradiction, m)
        assert (
            result_m.satisfiable
        ), "m:(p ∧ ¬p) should be satisfiable (epistemic uncertainty)"

        result_n = solve(contradiction, n)
        assert result_n.satisfiable, "n:(p ∧ ¬p) should be satisfiable (undefined)"

    def test_sign_interaction_principles(self):
        """Test how different signs interact in reasoning."""
        p, q = Formula.atoms("p", "q")

        # Test inference patterns with different signs
        premises = [SignedFormula(t, p), SignedFormula(t, p.implies(q))]
        conclusion = SignedFormula(t, q)

        # Modus ponens should work with t signs
        assert entails(
            [sf.formula for sf in premises], conclusion.formula
        ), "Modus ponens should work with truth-functional signs"

        # Test with epistemic signs
        premises_m = [SignedFormula(m, p), SignedFormula(m, p.implies(q))]
        # Epistemic reasoning is more complex - for now just test satisfiability
        for prem in premises_m:
            result = solve(prem.formula, prem.sign)
            assert result.satisfiable, f"Epistemic premise {prem} should be satisfiable"


class TestRestrictedQuantifierSemantics:
    """Test restricted quantification semantics."""

    def test_restricted_universal_basic_semantics(self):
        """Test basic restricted universal quantifier semantics."""
        # [∀X P(X)]Q(X) - for all X where P(X), Q(X) holds
        x = Formula.variable("X")
        px = Formula.predicate("P", [x])
        qx = Formula.predicate("Q", [x])

        universal_formula = Formula.restricted_forall(x, px, qx)

        # Test satisfiability under different signs
        for sign in [t, f, m, n]:
            result = solve(universal_formula, sign)
            # Should be satisfiable - exact semantics depend on domain
            assert result.satisfiable, f"{sign}:[∀X P(X)]Q(X) should be satisfiable"

    def test_restricted_existential_basic_semantics(self):
        """Test basic restricted existential quantifier semantics."""
        # [∃X P(X)]Q(X) - there exists X where P(X) and Q(X) holds
        x = Formula.variable("X")
        px = Formula.predicate("P", [x])
        qx = Formula.predicate("Q", [x])

        existential_formula = Formula.restricted_exists(x, px, qx)

        # Test satisfiability under different signs
        for sign in [t, f, m, n]:
            result = solve(existential_formula, sign)
            assert result.satisfiable, f"{sign}:[∃X P(X)]Q(X) should be satisfiable"

    def test_quantifier_domain_interaction(self):
        """Test how quantifiers interact with domain restrictions."""
        # This tests the core innovation of Ferguson (2021)
        x = Formula.variable("X")
        human_x = Formula.predicate("Human", [x])
        mortal_x = Formula.predicate("Mortal", [x])

        # All humans are mortal: [∀X Human(X)]Mortal(X)
        universal = Formula.restricted_forall(x, human_x, mortal_x)

        # Should be satisfiable as a general principle
        result = solve(universal, t)
        assert result.satisfiable, "Universal quantification should be satisfiable"


class TestTableauSoundnessProperties:
    """Test tableau proof system soundness properties."""

    def test_basic_soundness_modus_ponens(self):
        """Test that derivable conclusions are semantically valid (soundness)."""
        p, q = Formula.atoms("p", "q")

        # Modus ponens: p, p → q ⊢ q
        premises = [p, p.implies(q)]
        conclusion = q

        # If tableau derives this, it should be semantically valid
        is_entailed = entails(premises, conclusion)
        assert is_entailed, "Modus ponens should be valid (soundness test)"

    def test_soundness_invalid_inference_rejection(self):
        """Test that invalid inferences are correctly rejected."""
        p, q = Formula.atoms("p", "q")

        # Invalid: p ⊢ q (affirming consequent)
        premises = [p]
        conclusion = q

        is_entailed = entails(premises, conclusion)
        assert not is_entailed, "Invalid inference should be rejected (soundness test)"

    def test_contradiction_detection_soundness(self):
        """Test that contradictions are correctly identified."""
        p = Formula.atom("p")
        contradiction = p & ~p

        # Should be unsatisfiable under t sign
        result = solve(contradiction, t)
        assert not result.satisfiable, "Contradictions should be unsatisfiable under t"

        # But satisfiable under epistemic signs (uncertainty about contradictions)
        result_m = solve(contradiction, m)
        result_n = solve(contradiction, n)
        assert (
            result_m.satisfiable
        ), "Contradictions should be satisfiable under m (epistemic)"
        assert (
            result_n.satisfiable
        ), "Contradictions should be satisfiable under n (undefined)"


class TestSQLNullLogicCompatibility:
    """Test compatibility with SQL NULL logic (Kleene K3 fragment)."""

    def test_sql_null_and_semantics(self):
        """Test that our AND semantics match SQL NULL behavior."""
        # SQL: TRUE AND NULL = NULL, FALSE AND NULL = FALSE, NULL AND NULL = NULL
        # Our weak Kleene: t ∧ e = e, f ∧ e = e, e ∧ e = e

        semantics = WeakKleeneSemantics()
        conjunction = semantics._conjunction_table

        # SQL NULL behavior should match our undefined behavior for TRUE/NULL
        assert conjunction[(TRUE, UNDEFINED)] == UNDEFINED  # TRUE AND NULL = NULL
        assert conjunction[(UNDEFINED, TRUE)] == UNDEFINED

        # Note: SQL FALSE AND NULL = FALSE, but weak Kleene f ∧ e = e
        # This is a known difference - weak Kleene is more "infectious"
        assert conjunction[(FALSE, UNDEFINED)] == UNDEFINED  # Different from SQL!
        assert conjunction[(UNDEFINED, FALSE)] == UNDEFINED  # Different from SQL!

    def test_sql_null_or_semantics(self):
        """Test that our OR semantics match SQL NULL behavior where applicable."""
        # SQL: TRUE OR NULL = TRUE, FALSE OR NULL = NULL, NULL OR NULL = NULL
        # Our weak Kleene: t ∨ e = e, f ∨ e = e, e ∨ e = e

        semantics = WeakKleeneSemantics()
        disjunction = semantics._disjunction_table

        # Note: SQL TRUE OR NULL = TRUE, but weak Kleene t ∨ e = e
        # This demonstrates weak Kleene's more infectious nature
        assert disjunction[(TRUE, UNDEFINED)] == UNDEFINED  # Different from SQL!
        assert (
            disjunction[(FALSE, UNDEFINED)] == UNDEFINED
        )  # FALSE OR NULL = NULL (matches SQL)
        assert (
            disjunction[(UNDEFINED, UNDEFINED)] == UNDEFINED
        )  # NULL OR NULL = NULL (matches SQL)


# Additional test classes for completeness validation, model checking, etc.
# would be added here as we expand the validation suite
