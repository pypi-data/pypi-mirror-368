"""Tests for ACrQ bilateral predicate functionality."""

from wkrq.formula import (
    BilateralPredicateFormula,
    Constant,
    PredicateFormula,
    Variable,
)
from wkrq.semantics import FALSE, TRUE, UNDEFINED, BilateralTruthValue


class TestBilateralPredicateFormula:
    """Test bilateral predicate formula functionality."""

    def test_bilateral_creation_basic(self):
        """Test creating basic bilateral predicates."""
        # Create R(a)
        pred = BilateralPredicateFormula("R", [Constant("a")])
        assert str(pred) == "R(a)"
        assert pred.positive_name == "R"
        assert pred.negative_name == "R*"
        assert not pred.is_negative

        # Create R*(a)
        pred_star = BilateralPredicateFormula("R", [Constant("a")], is_negative=True)
        assert str(pred_star) == "R*(a)"
        assert pred_star.is_negative

    def test_bilateral_creation_custom_negative_name(self):
        """Test creating bilateral predicates with custom negative name."""
        pred = BilateralPredicateFormula(
            "Human", [Constant("socrates")], negative_name="NotHuman"
        )
        assert pred.positive_name == "Human"
        assert pred.negative_name == "NotHuman"
        assert str(pred) == "Human(socrates)"

        # Get dual with custom name
        dual = pred.get_dual()
        assert str(dual) == "NotHuman(socrates)"

    def test_bilateral_with_multiple_terms(self):
        """Test bilateral predicates with multiple terms."""
        pred = BilateralPredicateFormula("Loves", [Constant("john"), Constant("mary")])
        assert str(pred) == "Loves(john, mary)"

        dual = pred.get_dual()
        assert str(dual) == "Loves*(john, mary)"

    def test_bilateral_without_terms(self):
        """Test bilateral predicates without terms (propositional)."""
        pred = BilateralPredicateFormula("P", [])
        assert str(pred) == "P"

        dual = pred.get_dual()
        assert str(dual) == "P*"

    def test_get_dual(self):
        """Test getting the dual predicate (R ↔ R*)."""
        pred = BilateralPredicateFormula("R", [Constant("a")])
        dual = pred.get_dual()

        assert str(pred) == "R(a)"
        assert str(dual) == "R*(a)"
        assert not pred.is_negative
        assert dual.is_negative

        # Dual of dual should be original
        dual_dual = dual.get_dual()
        assert str(dual_dual) == "R(a)"
        assert not dual_dual.is_negative

    def test_to_standard_predicates(self):
        """Test conversion to standard predicate pair."""
        pred = BilateralPredicateFormula("Human", [Constant("socrates")])
        pos, neg = pred.to_standard_predicates()

        assert isinstance(pos, PredicateFormula)
        assert isinstance(neg, PredicateFormula)
        assert str(pos) == "Human(socrates)"
        assert str(neg) == "Human*(socrates)"
        assert pos.predicate_name == "Human"
        assert neg.predicate_name == "Human*"

    def test_equality(self):
        """Test equality comparison of bilateral predicates."""
        pred1 = BilateralPredicateFormula("R", [Constant("a")])
        pred2 = BilateralPredicateFormula("R", [Constant("a")])
        pred3 = BilateralPredicateFormula("R", [Constant("a")], is_negative=True)
        pred4 = BilateralPredicateFormula("S", [Constant("a")])

        assert pred1 == pred2
        assert pred1 != pred3  # Different polarity
        assert pred1 != pred4  # Different predicate name
        assert pred3 != pred4

    def test_hashing(self):
        """Test that bilateral predicates can be hashed and used in sets."""
        pred1 = BilateralPredicateFormula("R", [Constant("a")])
        pred2 = BilateralPredicateFormula("R", [Constant("a")])
        pred3 = BilateralPredicateFormula("R", [Constant("a")], is_negative=True)

        # Same predicates should have same hash
        assert hash(pred1) == hash(pred2)

        # Different predicates should (usually) have different hashes
        assert hash(pred1) != hash(pred3)

        # Should work in sets
        pred_set = {pred1, pred2, pred3}
        assert len(pred_set) == 2  # pred1 and pred2 are equal

    def test_term_substitution(self):
        """Test substituting terms in bilateral predicates."""
        pred = BilateralPredicateFormula("R", [Variable("X"), Constant("a")])

        # Substitute X with b
        mapping = {str(Variable("X")): Constant("b")}
        new_pred = pred.substitute_term(mapping)

        assert str(new_pred) == "R(b, a)"
        assert new_pred.is_negative == pred.is_negative
        assert new_pred.positive_name == pred.positive_name
        assert new_pred.negative_name == pred.negative_name

    def test_is_atomic(self):
        """Test that bilateral predicates are atomic."""
        pred = BilateralPredicateFormula("R", [Constant("a")])
        assert pred.is_atomic()

        pred_star = pred.get_dual()
        assert pred_star.is_atomic()

    def test_get_atoms(self):
        """Test getting atoms from bilateral predicates."""
        pred = BilateralPredicateFormula("R", [Constant("a")])
        atoms = pred.get_atoms()
        assert atoms == {"R(a)"}

        pred_star = pred.get_dual()
        atoms_star = pred_star.get_atoms()
        assert atoms_star == {"R*(a)"}


class TestBilateralTruthValue:
    """Test bilateral truth value functionality."""

    def test_bilateral_truth_value_creation(self):
        """Test creating bilateral truth values."""
        # Standard true
        btv_true = BilateralTruthValue(TRUE, FALSE)
        assert btv_true.positive == TRUE
        assert btv_true.negative == FALSE
        assert btv_true.is_consistent()
        assert btv_true.is_determinate()
        assert not btv_true.is_gap()
        assert not btv_true.is_glut()

        # Standard false
        btv_false = BilateralTruthValue(FALSE, TRUE)
        assert btv_false.is_consistent()
        assert btv_false.is_determinate()

        # Knowledge gap
        btv_gap = BilateralTruthValue(FALSE, FALSE)
        assert btv_gap.is_consistent()
        assert btv_gap.is_gap()
        assert not btv_gap.is_determinate()
        assert not btv_gap.is_glut()

        # Knowledge glut
        btv_glut = BilateralTruthValue(TRUE, TRUE)
        assert not btv_glut.is_consistent()
        assert btv_glut.is_glut()
        assert not btv_glut.is_determinate()
        assert not btv_glut.is_gap()

    def test_bilateral_with_undefined(self):
        """Test bilateral truth values involving undefined."""
        # Undefined positive
        btv1 = BilateralTruthValue(UNDEFINED, FALSE)
        assert btv1.is_consistent()
        assert not btv1.is_determinate()
        assert not btv1.is_gap()
        assert not btv1.is_glut()

        # Undefined negative
        btv2 = BilateralTruthValue(FALSE, UNDEFINED)
        assert btv2.is_consistent()

        # Both undefined
        btv3 = BilateralTruthValue(UNDEFINED, UNDEFINED)
        assert btv3.is_consistent()
        assert not btv3.is_gap()  # Gap requires both FALSE
        assert not btv3.is_glut()  # Glut requires both TRUE

    def test_to_simple_value(self):
        """Test conversion to simple string representation."""
        # Standard cases
        assert BilateralTruthValue(TRUE, FALSE).to_simple_value() == "true"
        assert BilateralTruthValue(FALSE, TRUE).to_simple_value() == "false"

        # Gap and glut
        assert BilateralTruthValue(FALSE, FALSE).to_simple_value() == "undefined (gap)"
        assert BilateralTruthValue(TRUE, TRUE).to_simple_value() == "both (glut)"

        # Undefined cases
        assert BilateralTruthValue(UNDEFINED, FALSE).to_simple_value() == "undefined"
        assert BilateralTruthValue(FALSE, UNDEFINED).to_simple_value() == "undefined"
        assert (
            BilateralTruthValue(UNDEFINED, UNDEFINED).to_simple_value() == "undefined"
        )

        # Complex case (shouldn't normally occur)
        # If we had other truth values, this would trigger

    def test_string_representation(self):
        """Test string representations of bilateral truth values."""
        btv = BilateralTruthValue(TRUE, FALSE)
        assert str(btv) == "BilateralTruthValue(pos=t, neg=f)"
        assert repr(btv) == "BilateralTruthValue(pos=t, neg=f)"

    def test_consistency_allows_paraconsistent_reasoning(self):
        """Test that we allow inconsistent values for paraconsistent reasoning."""
        # This should NOT raise an exception
        btv_glut = BilateralTruthValue(TRUE, TRUE)
        assert btv_glut.positive == TRUE
        assert btv_glut.negative == TRUE
        assert btv_glut.is_glut()
        assert not btv_glut.is_consistent()

        # We can work with gluts
        assert btv_glut.to_simple_value() == "both (glut)"
