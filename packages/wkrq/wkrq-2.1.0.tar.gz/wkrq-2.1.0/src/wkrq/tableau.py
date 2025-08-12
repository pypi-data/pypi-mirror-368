"""
Unified tableau implementation for both wKrQ and ACrQ.

This module provides a single, coherent tableau system that eliminates
the synchronization issues between multiple representations.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from .tableau_trace import TableauConstructionTrace

from .formula import (
    CompoundFormula,
    Constant,
    Formula,
    PredicateFormula,
    RestrictedUniversalFormula,
)
from .semantics import FALSE, TRUE, UNDEFINED, TruthValue
from .signs import Sign, SignedFormula, e, f, m, n, t


class RuleType(Enum):
    """Types of tableau rules."""

    ALPHA = "alpha"  # Non-branching rules
    BETA = "beta"  # Branching rules
    LLM = "llm"  # LLM evaluation rules


@dataclass
class RuleInfo:
    """Information about a tableau rule."""

    name: str
    rule_type: RuleType
    priority: int
    conclusions: list[list[SignedFormula]]
    instantiation_constant: Optional[str] = None

    def __lt__(self, other: "RuleInfo") -> bool:
        """Compare rules for priority ordering."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return len(self.conclusions) < len(other.conclusions)


@dataclass
class TableauNode:
    """Unified node representation for the tableau tree.

    This is the single source of truth for all node information.
    """

    id: int
    formula: SignedFormula
    parent: Optional["TableauNode"] = None
    children: list["TableauNode"] = field(default_factory=list)
    rule_applied: Optional[str] = None
    depth: int = 0

    # Branch membership tracking
    branch_ids: set[int] = field(default_factory=set)

    # Closure tracking
    causes_closure: bool = False
    contradicts_with: Optional[int] = None  # ID of the node it contradicts with
    closure_branch_id: Optional[int] = None  # Which branch closed because of this node

    def add_child(self, child: "TableauNode", rule: Optional[str] = None) -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        child.rule_applied = rule
        self.children.append(child)
        # Child inherits parent's branch memberships initially
        child.branch_ids = self.branch_ids.copy()


@dataclass
class Branch:
    """Unified branch representation.

    References nodes by ID only - no duplication of node data.
    """

    id: int
    node_ids: set[int] = field(default_factory=set)
    is_closed: bool = False
    closure_reason: Optional[str] = None

    # Track which nodes caused closure
    closure_node_ids: Optional[tuple[int, int]] = None  # IDs of contradicting nodes

    # Formula index for O(1) contradiction checking
    # Maps (formula_str, sign) -> set of node IDs
    formula_index: dict[tuple[str, Sign], set[int]] = field(
        default_factory=lambda: defaultdict(set)
    )

    # Track processed node IDs to avoid reprocessing
    processed_node_ids: set[int] = field(default_factory=set)

    # Track ground terms for quantifier instantiation
    ground_terms: set[str] = field(default_factory=set)

    # Track universal instantiations: (node_id, formula) -> set of constants used
    universal_instantiations: dict[tuple[int, str], set[str]] = field(
        default_factory=dict
    )


@dataclass
class Model:
    """A model extracted from an open branch."""

    valuations: dict[str, TruthValue]
    constants: dict[str, set[Formula]]

    def __str__(self) -> str:
        val_str = ", ".join(f"{k}={v}" for k, v in sorted(self.valuations.items()))
        if self.constants:
            const_str = "; ".join(
                f"{c}: {', '.join(str(f) for f in fs)}"
                for c, fs in sorted(self.constants.items())
            )
            return f"{{valuations: {{{val_str}}}, constants: {{{const_str}}}}}"
        return f"{{{val_str}}}"


@dataclass
class TableauResult:
    """Result of tableau construction."""

    satisfiable: bool
    models: list[Model]
    closed_branches: int
    open_branches: int
    total_nodes: int
    tableau: Optional["Tableau"] = None
    construction_trace: Optional["TableauConstructionTrace"] = None

    @property
    def valid(self) -> bool:
        """Check if the original formula is valid (no countermodels)."""
        return not self.satisfiable

    def print_trace(self, verbose: bool = False) -> None:
        """Print the construction trace if available."""
        if self.construction_trace:
            self.construction_trace.print_trace(verbose=verbose)
        else:
            print("No trace available. Re-run with trace=True")


class Tableau:
    """Base tableau implementation for both wKrQ and ACrQ.

    This class provides all shared tableau mechanics.
    Subclasses only override rule selection and contradiction checking.
    """

    def __init__(self, initial_formulas: list[SignedFormula], trace: bool = False):
        """Initialize the tableau.

        Args:
            initial_formulas: Initial signed formulas for the tableau
            trace: Whether to enable construction tracing
        """
        if not initial_formulas:
            raise ValueError("Cannot create tableau with empty formula list")

        # All nodes stored by ID
        self.nodes: dict[int, TableauNode] = {}
        self.node_counter = 0

        # All branches
        self.branches: list[Branch] = []
        self.open_branches: list[Branch] = []
        self.closed_branches: list[Branch] = []
        self.branch_counter = 0

        # Global tracking
        self.constants: set[str] = set()

        # Tracing
        self.trace_enabled = trace
        self.construction_trace = None
        if trace:
            from .tableau_trace import TableauConstructionTrace

            self.construction_trace = TableauConstructionTrace(initial_formulas)

        # Create initial branch
        initial_branch = self._create_branch()
        self.branches.append(initial_branch)
        self.open_branches.append(initial_branch)

        # Add all initial formulas as separate nodes
        for i, signed_formula in enumerate(initial_formulas):
            node = self._create_node(signed_formula)
            if i == 0:
                self.root = node  # First node is the root

            # Check for closure when adding each initial formula
            if self._add_node_to_branch(node, initial_branch):
                break  # Branch closed

    def _create_node(self, signed_formula: SignedFormula) -> TableauNode:
        """Create a new tableau node."""
        node = TableauNode(self.node_counter, signed_formula)
        self.nodes[self.node_counter] = node
        self.node_counter += 1
        return node

    def _create_branch(self) -> Branch:
        """Create a new branch."""
        branch = Branch(self.branch_counter)
        self.branch_counter += 1
        return branch

    def _register_node_with_branch(self, node: TableauNode, branch: Branch) -> None:
        """Register a node with a branch."""
        node.branch_ids.add(branch.id)
        branch.node_ids.add(node.id)

        # Update formula index
        formula_key = (str(node.formula.formula), node.formula.sign)
        branch.formula_index[formula_key].add(node.id)

    def _extract_ground_terms_from_node(
        self, node: TableauNode, branch: Branch
    ) -> None:
        """Extract ground terms from a node's formula."""
        formula = node.formula.formula

        def extract_from_formula(f: Formula) -> None:
            if isinstance(f, PredicateFormula):
                for term in f.terms:
                    if isinstance(term, Constant):
                        branch.ground_terms.add(term.name)
                        self.constants.add(term.name)
            elif isinstance(f, CompoundFormula):
                for sub in f.subformulas:
                    extract_from_formula(sub)
            elif hasattr(f, "restriction") and hasattr(f, "matrix"):
                extract_from_formula(f.restriction)
                extract_from_formula(f.matrix)

        extract_from_formula(formula)

    def _check_contradiction(
        self, node: TableauNode, branch: Branch
    ) -> tuple[bool, Optional[int]]:
        """Check if a node causes a contradiction in the branch.

        Returns:
            (closes, contradicting_node_id)
        """
        # Check for contradicting signs
        for other_sign in [t, f, e]:
            if other_sign != node.formula.sign:
                other_key = (str(node.formula.formula), other_sign)
                if other_key in branch.formula_index:
                    # Found contradiction
                    other_node_ids = branch.formula_index[other_key]
                    if other_node_ids:
                        other_node_id = next(iter(other_node_ids))
                        return True, other_node_id

        return False, None

    def _add_node_to_branch(self, node: TableauNode, branch: Branch) -> bool:
        """Add a node to a branch and check for closure.

        Returns:
            True if branch closes
        """
        # Check for contradiction
        closes, contradicting_node_id = self._check_contradiction(node, branch)

        if closes:
            # Mark branch as closed
            branch.is_closed = True
            if contradicting_node_id is not None:
                branch.closure_node_ids = (node.id, contradicting_node_id)
            if contradicting_node_id is not None:
                branch.closure_reason = f"{node.formula} contradicts {self.nodes[contradicting_node_id].formula}"

                # Mark nodes as causing closure
                node.causes_closure = True
                node.contradicts_with = contradicting_node_id
                node.closure_branch_id = branch.id

                other_node = self.nodes[contradicting_node_id]
                other_node.causes_closure = True
                other_node.contradicts_with = node.id
                other_node.closure_branch_id = branch.id

            # Move branch to closed list
            if branch in self.open_branches:
                self.open_branches.remove(branch)
                self.closed_branches.append(branch)

            return True

        # No contradiction - register the node
        self._register_node_with_branch(node, branch)
        self._extract_ground_terms_from_node(node, branch)

        return False

    def _get_applicable_rule(
        self, node: TableauNode, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get the next applicable rule for a node.

        Subclasses override this to use different rule systems.
        """
        # Default implementation uses wKrQ rules
        from .wkrq_rules import get_applicable_rule

        # Check if already processed
        if node.id in branch.processed_node_ids:
            # Allow reprocessing of universals for new constants
            if not isinstance(node.formula.formula, RestrictedUniversalFormula):
                return None

        # Get existing and used constants for universals
        used_constants = None
        if isinstance(node.formula.formula, RestrictedUniversalFormula):
            key = (node.id, str(node.formula.formula))
            used_constants = branch.universal_instantiations.get(key, set())

        # Create fresh constant generator
        def fresh_constant_generator() -> Constant:
            return Constant(f"c_{self.node_counter}")

        # Get the rule
        rule = get_applicable_rule(
            node.formula,
            fresh_constant_generator,
            list(branch.ground_terms) if branch.ground_terms else None,
            used_constants,
        )

        if not rule:
            return None

        # Convert to RuleInfo
        rule_type = RuleType.ALPHA if not rule.is_branching() else RuleType.BETA
        priority = 10 if rule_type == RuleType.ALPHA else 20

        return RuleInfo(
            name=rule.name,
            rule_type=rule_type,
            priority=priority,
            conclusions=rule.conclusions,
            instantiation_constant=rule.instantiation_constant,
        )

    def apply_rule(
        self, node: TableauNode, branch: Branch, rule_info: RuleInfo
    ) -> None:
        """Apply a tableau rule."""
        # Create trace for this application if tracing is enabled
        if self.trace_enabled and self.construction_trace:
            from .tableau_trace import RuleApplicationTrace

            trace = RuleApplicationTrace(
                rule_name=rule_info.name,
                source_node=node,
                source_branch=branch,
                produced_formulas=rule_info.conclusions,
            )
            initial_closed_count = len(self.closed_branches)
            initial_branch_count = len(self.branches)

        # Mark node as processed
        if rule_info.instantiation_constant:
            # Universal quantifier - track instantiation
            key = (node.id, str(node.formula.formula))
            if key not in branch.universal_instantiations:
                branch.universal_instantiations[key] = set()
            branch.universal_instantiations[key].add(rule_info.instantiation_constant)
        else:
            # Regular processing
            branch.processed_node_ids.add(node.id)

        conclusions = rule_info.conclusions

        if len(conclusions) == 1:
            # Non-branching rule
            for signed_formula in conclusions[0]:
                # Check if formula already exists in branch
                formula_key = (str(signed_formula.formula), signed_formula.sign)
                if (
                    formula_key not in branch.formula_index
                    or not branch.formula_index[formula_key]
                ):
                    # Create new node
                    new_node = self._create_node(signed_formula)
                    node.add_child(new_node, rule_info.name)

                    # Add to branch
                    if self._add_node_to_branch(new_node, branch):
                        return  # Branch closed
        else:
            # Branching rule
            if branch in self.open_branches:
                self.open_branches.remove(branch)

            for conclusion_set in conclusions:
                # Create new branch
                new_branch = self._create_branch()
                self.branches.append(new_branch)

                # Copy existing nodes to new branch
                for node_id in branch.node_ids:
                    existing_node = self.nodes[node_id]
                    self._register_node_with_branch(existing_node, new_branch)

                # Copy branch state
                new_branch.ground_terms = branch.ground_terms.copy()
                new_branch.processed_node_ids = branch.processed_node_ids.copy()
                new_branch.universal_instantiations = {
                    k: v.copy() for k, v in branch.universal_instantiations.items()
                }

                # Add new formulas
                branch_closed = False
                for signed_formula in conclusion_set:
                    formula_key = (str(signed_formula.formula), signed_formula.sign)
                    if (
                        formula_key not in new_branch.formula_index
                        or not new_branch.formula_index[formula_key]
                    ):
                        new_node = self._create_node(signed_formula)
                        node.add_child(new_node, rule_info.name)

                        if self._add_node_to_branch(new_node, new_branch):
                            branch_closed = True
                            break

                if not branch_closed:
                    self.open_branches.append(new_branch)

        # Complete the trace if enabled
        if self.trace_enabled and self.construction_trace:
            # Record nodes created
            for child in node.children:
                if child.rule_applied == rule_info.name:
                    trace.nodes_created.append(child)

            # Record branches created
            if len(self.branches) > initial_branch_count:
                new_branches = self.branches[initial_branch_count:]
                trace.branches_created.extend(new_branches)

            # Record closures
            if len(self.closed_branches) > initial_closed_count:
                for closed_branch in self.closed_branches[initial_closed_count:]:
                    if closed_branch.closure_reason:
                        trace.closures_caused.append(
                            (closed_branch, closed_branch.closure_reason)
                        )

            # Add trace to construction history
            self.construction_trace.add_rule_application(trace)
            self.construction_trace.total_nodes = len(self.nodes)
            self.construction_trace.total_branches = len(self.branches)
            self.construction_trace.closed_branches = len(self.closed_branches)

    def is_complete(self) -> bool:
        """Check if tableau construction is complete."""
        if not self.open_branches:
            return True

        for branch in self.open_branches:
            for node_id in branch.node_ids:
                if node_id not in branch.processed_node_ids:
                    node = self.nodes[node_id]
                    if self._get_applicable_rule(node, branch):
                        return False

        return True

    def construct(self) -> TableauResult:
        """Construct the tableau."""
        max_iterations = 1000
        iteration = 0

        while (
            self.open_branches and not self.is_complete() and iteration < max_iterations
        ):
            iteration += 1

            # Select branch to process
            branch = self.open_branches[0]

            # Get applicable rules
            applicable_rules = []
            for node_id in branch.node_ids:
                if node_id not in branch.processed_node_ids:
                    node = self.nodes[node_id]
                    rule = self._get_applicable_rule(node, branch)
                    if rule:
                        applicable_rules.append((node, rule))

            if not applicable_rules:
                break

            # Sort by priority
            applicable_rules.sort(key=lambda x: x[1])

            # Apply best rule
            node, rule_info = applicable_rules[0]
            self.apply_rule(node, branch, rule_info)

        # Extract models from open branches
        models = []
        for branch in self.open_branches:
            model = self._extract_model(branch)
            if model:
                models.append(model)

        return TableauResult(
            satisfiable=len(models) > 0,
            models=models,
            closed_branches=len(self.closed_branches),
            open_branches=len(self.open_branches),
            total_nodes=len(self.nodes),
            tableau=self,
        )

    def _extract_model(self, branch: Branch) -> Optional[Model]:
        """Extract a model from an open branch."""
        # Get all atoms
        atoms = set()
        for node_id in branch.node_ids:
            node = self.nodes[node_id]
            atoms.update(node.formula.formula.get_atoms())

        # Build valuation
        valuations = {}
        for atom in atoms:
            # Check what signs appear for this atom (keys are string, sign)
            has_t = (atom, t) in branch.formula_index and branch.formula_index[
                (atom, t)
            ]
            has_f = (atom, f) in branch.formula_index and branch.formula_index[
                (atom, f)
            ]
            has_e = (atom, e) in branch.formula_index and branch.formula_index[
                (atom, e)
            ]
            has_m = (atom, m) in branch.formula_index and branch.formula_index[
                (atom, m)
            ]
            has_n = (atom, n) in branch.formula_index and branch.formula_index[
                (atom, n)
            ]

            if has_t:
                valuations[atom] = TRUE
            elif has_f:
                valuations[atom] = FALSE
            elif has_e:
                valuations[atom] = UNDEFINED
            elif has_m:
                # m means meaningful - can be either true or false
                valuations[atom] = TRUE  # Choose true (could also be FALSE)
            elif has_n:
                # n means nontrue - can be either false or undefined
                valuations[atom] = FALSE  # Choose false (could also be UNDEFINED)
            else:
                valuations[atom] = UNDEFINED

        return Model(valuations, {})


class WKrQTableau(Tableau):
    """wKrQ-specific tableau."""

    def __init__(self, initial_formulas: list[SignedFormula], trace: bool = False):
        super().__init__(initial_formulas, trace=trace)

    # Uses default _get_applicable_rule which uses wKrQ rules
    # Uses default _check_contradiction which doesn't allow gluts


class ACrQTableau(Tableau):
    """ACrQ-specific tableau with bilateral predicate support."""

    def __init__(
        self,
        initial_formulas: list[SignedFormula],
        llm_evaluator: Optional[Callable] = None,
        trace: bool = False,
    ):
        super().__init__(initial_formulas, trace=trace)
        self.llm_evaluator = llm_evaluator
        self.bilateral_pairs: dict[str, str] = {}

        # Identify bilateral predicates
        self._identify_bilateral_predicates(initial_formulas)

    def _identify_bilateral_predicates(self, formulas: list[SignedFormula]) -> None:
        """Identify and register bilateral predicate pairs."""

        for sf in formulas:
            self._extract_bilateral_pairs(sf.formula)

    def _extract_bilateral_pairs(self, formula: Formula) -> None:
        """Extract bilateral predicate pairs from a formula."""
        from .formula import BilateralPredicateFormula

        if isinstance(formula, BilateralPredicateFormula):
            pos_name = formula.positive_name
            neg_name = f"{formula.positive_name}*"
            self.bilateral_pairs[pos_name] = neg_name
            self.bilateral_pairs[neg_name] = pos_name
        elif isinstance(formula, CompoundFormula):
            for sub in formula.subformulas:
                self._extract_bilateral_pairs(sub)
        elif hasattr(formula, "restriction") and hasattr(formula, "matrix"):
            self._extract_bilateral_pairs(formula.restriction)
            self._extract_bilateral_pairs(formula.matrix)

    def _check_contradiction(
        self, node: TableauNode, branch: Branch
    ) -> tuple[bool, Optional[int]]:
        """Check for contradictions in ACrQ (allows gluts)."""
        # Check if this is a bilateral glut case
        if self._is_bilateral_glut(node, branch):
            return False, None  # Gluts are allowed

        # Otherwise use standard contradiction checking
        return super()._check_contradiction(node, branch)

    def _is_bilateral_glut(self, node: TableauNode, branch: Branch) -> bool:
        """Check if this node forms a bilateral glut with existing formulas."""
        from .formula import BilateralPredicateFormula

        formula = node.formula.formula
        sign = node.formula.sign

        # Only check for gluts with t sign
        if sign != t:
            return False

        # Check if this is a bilateral predicate
        if not isinstance(formula, (PredicateFormula, BilateralPredicateFormula)):
            return False

        # Get base name
        if isinstance(formula, BilateralPredicateFormula):
            base_name = formula.get_base_name()
            is_negative = formula.is_negative
        else:
            pred_name = formula.predicate_name
            if pred_name.endswith("*"):
                base_name = pred_name[:-1]
                is_negative = True
            else:
                base_name = pred_name
                is_negative = False

        # Look for the dual with same sign (glut)
        for other_node_id in branch.node_ids:
            other_node = self.nodes[other_node_id]
            if other_node.formula.sign != t:
                continue

            other_formula = other_node.formula.formula
            if not isinstance(
                other_formula, (PredicateFormula, BilateralPredicateFormula)
            ):
                continue

            # Check if it's the dual
            if isinstance(other_formula, BilateralPredicateFormula):
                other_base = other_formula.get_base_name()
                other_negative = other_formula.is_negative
            else:
                other_pred = other_formula.predicate_name
                if other_pred.endswith("*"):
                    other_base = other_pred[:-1]
                    other_negative = True
                else:
                    other_base = other_pred
                    other_negative = False

            # If same base but different polarity with same args, it's a glut
            if (
                base_name == other_base
                and is_negative != other_negative
                and str(formula.terms) == str(other_formula.terms)
            ):
                return True

        return False

    def _get_applicable_rule(
        self, node: TableauNode, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get applicable rule using ACrQ rules."""
        from .acrq_rules import get_acrq_rule

        # Check if already processed
        if node.id in branch.processed_node_ids:
            if not isinstance(node.formula.formula, RestrictedUniversalFormula):
                # Check for LLM evaluation if atomic
                if self.llm_evaluator and node.formula.formula.is_atomic():
                    return self._create_llm_evaluation_rule(node, branch)
                return None

        # Get existing and used constants
        used_constants = None
        if isinstance(node.formula.formula, RestrictedUniversalFormula):
            key = (node.id, str(node.formula.formula))
            used_constants = branch.universal_instantiations.get(key, set())

        # Create fresh constant generator
        def fresh_constant_generator() -> Constant:
            return Constant(f"c_{self.node_counter}")

        # Get ACrQ rule
        rule = get_acrq_rule(
            node.formula,
            fresh_constant_generator,
            list(branch.ground_terms) if branch.ground_terms else None,
            used_constants,
        )

        if rule:
            # Convert to RuleInfo
            rule_type = RuleType.BETA if rule.is_branching() else RuleType.ALPHA
            priority = 10 if rule_type == RuleType.ALPHA else 20

            return RuleInfo(
                name=rule.name,
                rule_type=rule_type,
                priority=priority,
                conclusions=rule.conclusions,
                instantiation_constant=rule.instantiation_constant,
            )

        # Try LLM evaluation for atomic formulas
        if self.llm_evaluator and node.formula.formula.is_atomic():
            return self._create_llm_evaluation_rule(node, branch)

        return None

    def _create_llm_evaluation_rule(
        self, node: TableauNode, branch: Branch
    ) -> Optional[RuleInfo]:
        """Create an LLM evaluation rule."""
        # Check if already evaluated
        eval_key = f"llm_eval_{node.id}"
        if eval_key in branch.processed_node_ids:
            return None

        # Call LLM evaluator
        if self.llm_evaluator is None:
            return None
        try:
            bilateral_value = self.llm_evaluator(node.formula.formula)
        except Exception:
            return None

        # Convert to signed formulas

        conclusions = []
        conclusion_set = []

        # Determine what to add based on bilateral value
        if bilateral_value.positive == TRUE and bilateral_value.negative == FALSE:
            # Clear positive evidence
            conclusion_set.append(SignedFormula(t, node.formula.formula))
        elif bilateral_value.positive == FALSE and bilateral_value.negative == TRUE:
            # Clear negative evidence
            conclusion_set.append(SignedFormula(f, node.formula.formula))
        elif bilateral_value.positive == TRUE and bilateral_value.negative == TRUE:
            # Glut - add both
            conclusion_set.append(SignedFormula(t, node.formula.formula))
            # Also add dual for bilateral predicates
            from .formula import BilateralPredicateFormula

            if isinstance(
                node.formula.formula, (PredicateFormula, BilateralPredicateFormula)
            ):
                if isinstance(node.formula.formula, BilateralPredicateFormula):
                    dual = node.formula.formula.get_dual()
                else:
                    dual = BilateralPredicateFormula(
                        positive_name=node.formula.formula.predicate_name,
                        terms=node.formula.formula.terms,
                        is_negative=True,
                    )
                conclusion_set.append(SignedFormula(t, dual))
        elif bilateral_value.positive == FALSE and bilateral_value.negative == FALSE:
            # Gap - explicit uncertainty: cannot verify AND cannot refute
            # This is a speech act stating the limits of knowledge
            conclusion_set.append(SignedFormula(f, node.formula.formula))

            # Also add f: P*(x) for bilateral predicates
            from .formula import BilateralPredicateFormula

            if isinstance(
                node.formula.formula, (PredicateFormula, BilateralPredicateFormula)
            ):
                if isinstance(node.formula.formula, BilateralPredicateFormula):
                    dual = node.formula.formula.get_dual()
                else:
                    dual = BilateralPredicateFormula(
                        positive_name=node.formula.formula.predicate_name,
                        terms=node.formula.formula.terms,
                        is_negative=True,
                    )
                conclusion_set.append(SignedFormula(f, dual))
        elif (
            bilateral_value.positive == UNDEFINED
            or bilateral_value.negative == UNDEFINED
        ):
            # Error
            conclusion_set.append(SignedFormula(e, node.formula.formula))

        if conclusion_set:
            conclusions.append(conclusion_set)

            return RuleInfo(
                name=f"LLM-Eval({node.formula.formula})",
                rule_type=RuleType.LLM,
                priority=30,  # Lower priority than logical rules
                conclusions=conclusions,
            )

        return None


def solve(formula: Formula, sign: Sign = t, trace: bool = False) -> TableauResult:
    """Solve a formula with the given sign.

    Args:
        formula: The formula to solve
        sign: The sign to assign (default: t)
        trace: Whether to enable construction tracing

    Returns:
        TableauResult with optional construction_trace attribute
    """
    signed_formula = SignedFormula(sign, formula)
    tableau = WKrQTableau([signed_formula], trace=trace)
    result = tableau.construct()
    if trace and tableau.construction_trace:
        result.construction_trace = tableau.construction_trace
    return result


def valid(formula: Formula) -> bool:
    """Check if a formula is valid (true in all models).

    A formula is valid iff it cannot be false or undefined.
    """
    # Check if formula can be false
    result_f = solve(formula, f)
    if result_f.satisfiable:
        return False

    # Check if formula can be undefined
    result_e = solve(formula, e)
    if result_e.satisfiable:
        return False

    # Cannot be false or undefined, must be valid
    return True


def entails(premises: list[Formula], conclusion: Formula) -> bool:
    """Check if premises entail conclusion."""
    from .formula import Conjunction, Negation

    if not premises:
        # Empty premises, check if conclusion is valid
        return valid(conclusion)

    # Combine premises
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)

    # Test satisfiability of premises & ~conclusion
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    result = solve(test_formula, t)

    return not result.satisfiable
