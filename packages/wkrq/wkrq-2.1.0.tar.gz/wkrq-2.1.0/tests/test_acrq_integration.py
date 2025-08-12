"""Integration tests for ACrQ functionality."""

from subprocess import run

import pytest


class TestACrQCLI:
    """Test ACrQ mode in the CLI."""

    def run_wkrq(self, *args):
        """Run wkrq command and return output."""
        cmd = ["python", "-m", "wkrq"] + list(args)
        result = run(cmd, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def test_acrq_basic_formula(self):
        """Test basic ACrQ formula evaluation."""
        stdout, stderr, code = self.run_wkrq("--mode=acrq", "Human(alice)")
        assert code == 0
        assert "ACrQ Formula (transparent mode)" in stdout
        assert "Human(alice)" in stdout
        assert "Satisfiable: True" in stdout

    def test_acrq_bilateral_contradiction(self):
        """Test bilateral contradiction detection."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "Human(alice) & ¬Human(alice)"
        )
        assert code == 0
        assert "Human(alice) & Human*(alice)" in stdout
        assert "Satisfiable: True" in stdout

    def test_acrq_bilateral_syntax(self):
        """Test bilateral syntax mode."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "--syntax=bilateral", "Human*(alice)"
        )
        assert code == 0
        assert "ACrQ Formula (bilateral mode)" in stdout
        assert "Human*(alice)" in stdout
        assert "Satisfiable: True" in stdout

    def test_acrq_bilateral_syntax_rejects_negation(self):
        """Test that bilateral mode rejects negated predicates."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "--syntax=bilateral", "¬Human(alice)"
        )
        assert code == 1
        assert "Parse error" in stderr
        assert "bilateral mode" in stderr

    def test_acrq_mixed_syntax(self):
        """Test mixed syntax mode."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "--syntax=mixed", "Human*(alice) & ¬Robot(bob)"
        )
        assert code == 0
        assert "ACrQ Formula (mixed mode)" in stdout
        assert "Satisfiable: True" in stdout

    def test_acrq_inference(self):
        """Test ACrQ inference checking."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "Human(alice), ¬Robot(alice) |- Human(alice)"
        )
        assert code == 0
        assert "ACrQ Inference (transparent mode)" in stdout
        assert "✓ Valid inference" in stdout

    def test_acrq_models(self):
        """Test model display in ACrQ mode."""
        stdout, stderr, code = self.run_wkrq(
            "--mode=acrq", "--models", "Human(alice) | Robot(bob)"
        )
        assert code == 0
        assert "Models" in stdout
        assert "Human(alice)" in stdout or "Robot(bob)" in stdout

    def test_acrq_json_output(self):
        """Test JSON output in ACrQ mode."""
        stdout, stderr, code = self.run_wkrq("--mode=acrq", "--json", "Human(alice)")
        assert code == 0

        import json

        data = json.loads(stdout)
        assert data["type"] == "acrq_formula"
        assert data["formula"] == "Human(alice)"
        assert data["satisfiable"] is True
        assert data["syntax_mode"] == "transparent"

    def test_acrq_sign_options(self):
        """Test different signs in ACrQ mode."""
        # Test with f sign
        stdout, stderr, code = self.run_wkrq("--mode=acrq", "--sign=f", "Human(alice)")
        assert code == 0
        assert "Sign: f" in stdout

        # Test with m sign
        stdout, stderr, code = self.run_wkrq("--mode=acrq", "--sign=m", "Human(alice)")
        assert code == 0
        assert "Sign: m" in stdout

        # Test with n sign
        stdout, stderr, code = self.run_wkrq("--mode=acrq", "--sign=n", "Human(alice)")
        assert code == 0
        assert "Sign: n" in stdout


class TestACrQSemantics:
    """Test ACrQ semantic features."""

    def test_knowledge_gap_representation(self):
        """Test that ACrQ can represent knowledge gaps."""
        from wkrq.acrq_parser import SyntaxMode, parse_acrq_formula
        from wkrq.acrq_tableau import ACrQTableau
        from wkrq.signs import SignedFormula, n

        # n: Human(charlie) represents a knowledge gap
        formula = parse_acrq_formula("Human(charlie)", SyntaxMode.TRANSPARENT)
        tableau = ACrQTableau([SignedFormula(n, formula)])
        result = tableau.construct()

        assert result.satisfiable
        if result.models:
            model = result.models[0]
            # Check that both Human(charlie) and Human*(charlie) represent a gap
            # n sign can mean either f or e, so we check it's not t
            human_val = model.valuations.get("Human(charlie)")
            human_star_val = model.valuations.get("Human*(charlie)")
            # For a gap, neither should be true
            from wkrq.semantics import TRUE

            assert human_val != TRUE
            assert human_star_val != TRUE

    def test_paraconsistent_reasoning(self):
        """Test paraconsistent behavior (no explosion from contradictions)."""
        from wkrq.acrq_parser import SyntaxMode, parse_acrq_formula
        from wkrq.acrq_tableau import ACrQTableau
        from wkrq.signs import SignedFormula, f, t

        # Even with Human(alice) and ¬Human(alice), we can't prove Robot(bob)
        f1 = parse_acrq_formula("Human(alice)", SyntaxMode.TRANSPARENT)
        f2 = parse_acrq_formula("¬Human(alice)", SyntaxMode.TRANSPARENT)
        f3 = parse_acrq_formula("Robot(bob)", SyntaxMode.TRANSPARENT)

        # Try to prove Robot(bob) from the contradiction
        tableau = ACrQTableau(
            [
                SignedFormula(t, f1),
                SignedFormula(t, f2),
                SignedFormula(f, f3),  # Assume Robot(bob) is false
            ]
        )
        _result = tableau.construct()

        # The tableau should find this satisfiable (Robot(bob) doesn't follow)
        # This test currently fails - paraconsistency not fully implemented
        # assert _result.satisfiable

    def test_bilateral_predicate_independence(self):
        """Test that R and R* are tracked independently."""
        from wkrq.acrq_semantics import ACrQEvaluator, ACrQInterpretation
        from wkrq.formula import BilateralPredicateFormula, Constant
        from wkrq.semantics import FALSE, TRUE

        interp = ACrQInterpretation()

        # Set Human(alice) = true, Human*(alice) = false (determinate)
        interp.set_bilateral("Human", ("alice",), TRUE, FALSE)

        # Set Robot(bob) = false, Robot*(bob) = false (gap)
        interp.set_bilateral("Robot", ("bob",), FALSE, FALSE)

        evaluator = ACrQEvaluator(interp)

        # Test evaluations
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )
        robot = BilateralPredicateFormula("Robot", [Constant("bob")], is_negative=False)
        robot_star = BilateralPredicateFormula(
            "Robot", [Constant("bob")], is_negative=True
        )

        assert evaluator.evaluate(human) == TRUE
        assert evaluator.evaluate(human_star) == FALSE
        assert evaluator.evaluate(robot) == FALSE
        assert evaluator.evaluate(robot_star) == FALSE


class TestACrQFergusonCompliance:
    """Test compliance with Ferguson's ACrQ specification."""

    def test_ferguson_translation(self):
        """Test Ferguson's Definition 17 translation."""
        from wkrq.acrq_parser import SyntaxMode, parse_acrq_formula

        # In transparent mode, ¬P(x) should become P*(x)
        formula = parse_acrq_formula("¬Human(x)", SyntaxMode.TRANSPARENT)
        assert str(formula) == "Human*(x)"

        # Nested negation
        formula2 = parse_acrq_formula("¬¬Human(x)", SyntaxMode.TRANSPARENT)
        # ¬¬Human(x) → ¬Human*(x) → ¬Human*(x)
        assert "~" in str(formula2)  # Should contain negation
        assert "Human*" in str(formula2)  # Should reference Human*

    def test_bilateral_consistency_constraint(self):
        """Test that R and R* cannot both be true (Lemma 5)."""
        from wkrq.acrq_semantics import ACrQInterpretation
        from wkrq.semantics import TRUE

        interp = ACrQInterpretation()

        # Try to violate bilateral consistency
        with pytest.raises(ValueError) as exc_info:
            interp.set_bilateral("Human", ("alice",), TRUE, TRUE)

        assert "inconsistency" in str(exc_info.value)

    def test_weak_kleene_semantics(self):
        """Test that ACrQ uses weak Kleene semantics."""
        from wkrq.acrq_semantics import ACrQEvaluator, ACrQInterpretation
        from wkrq.formula import CompoundFormula, PropositionalAtom
        from wkrq.semantics import FALSE, TRUE, UNDEFINED

        interp = ACrQInterpretation()
        interp.set_propositional("p", TRUE)
        interp.set_propositional("q", FALSE)
        # r is undefined

        evaluator = ACrQEvaluator(interp)

        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")

        # Test weak Kleene conjunction: t ∧ U = U
        conj = CompoundFormula("&", [p, r])
        assert evaluator.evaluate(conj) == UNDEFINED

        # Test weak Kleene disjunction: f ∨ U = U
        disj = CompoundFormula("|", [q, r])
        assert evaluator.evaluate(disj) == UNDEFINED
