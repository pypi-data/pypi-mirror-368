"""
Tableau construction trace for debugging and education.

This module provides detailed tracing of tableau construction,
showing exactly what each rule produces and how the tableau evolves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .signs import SignedFormula
from .tableau import Branch, TableauNode


class TraceEvent(Enum):
    """Types of events in tableau construction."""

    RULE_APPLICATION = "rule_application"
    NODE_ADDED = "node_added"
    BRANCH_CLOSED = "branch_closed"
    BRANCH_CREATED = "branch_created"


@dataclass
class RuleApplicationTrace:
    """Complete trace of a rule application."""

    rule_name: str
    source_node: TableauNode
    source_branch: Branch

    # What the rule produced
    produced_formulas: list[list[SignedFormula]]

    # What actually happened
    nodes_created: list[TableauNode] = field(default_factory=list)
    branches_created: list[Branch] = field(default_factory=list)
    closures_caused: list[tuple[Branch, str]] = field(default_factory=list)

    # Timing
    step_number: int = 0

    def get_summary(self) -> str:
        """Get a human-readable summary."""
        lines = []
        lines.append(f"Step {self.step_number}: {self.rule_name}")
        lines.append(f"  Applied to: {self.source_node.formula}")

        if len(self.produced_formulas) == 1:
            lines.append("  Produced:")
            for sf in self.produced_formulas[0]:
                added = any(str(n.formula) == str(sf) for n in self.nodes_created)
                mark = "✓" if added else "✗"
                if not added and self.closures_caused:
                    mark += " (branch already closed)"
                lines.append(f"    {mark} {sf}")
        else:
            lines.append(f"  Created {len(self.produced_formulas)} branches:")
            for i, formula_set in enumerate(self.produced_formulas):
                lines.append(f"    Branch {i+1}:")
                for sf in formula_set:
                    lines.append(f"      {sf}")

        if self.closures_caused:
            for _branch, reason in self.closures_caused:
                lines.append(f"  ⚠ Caused closure: {reason}")

        return "\n".join(lines)


@dataclass
class TableauConstructionTrace:
    """Complete trace of tableau construction."""

    initial_formulas: list[SignedFormula]
    rule_applications: list[RuleApplicationTrace] = field(default_factory=list)

    # Statistics
    total_nodes: int = 0
    total_branches: int = 0
    closed_branches: int = 0

    def add_rule_application(self, trace: RuleApplicationTrace) -> None:
        """Add a rule application to the trace."""
        trace.step_number = len(self.rule_applications) + 1
        self.rule_applications.append(trace)

    def print_trace(self, verbose: bool = False) -> None:
        """Print the complete construction trace."""
        print("\n" + "=" * 70)
        print("TABLEAU CONSTRUCTION TRACE")
        print("=" * 70)

        print("\nInitial Formulas:")
        for i, sf in enumerate(self.initial_formulas, 1):
            print(f"  {i}. {sf}")

        print("\n" + "-" * 70)
        print("RULE APPLICATIONS")
        print("-" * 70)

        for trace in self.rule_applications:
            print(f"\n{trace.get_summary()}")

        print("\n" + "-" * 70)
        print("STATISTICS")
        print("-" * 70)
        print(f"Total steps: {len(self.rule_applications)}")
        print(f"Total nodes: {self.total_nodes}")
        print(f"Total branches: {self.total_branches}")
        print(f"Closed branches: {self.closed_branches}")

    def print_step_by_step(self) -> None:
        """Print trace in step-by-step format."""
        print("\n" + "=" * 70)
        print("STEP-BY-STEP TABLEAU CONSTRUCTION")
        print("=" * 70)

        print("\nInitial State:")
        for i, sf in enumerate(self.initial_formulas):
            print(f"  Node {i}: {sf}")

        for trace in self.rule_applications:
            print(f"\n{'-' * 70}")
            print(trace.get_summary())

            if trace.nodes_created:
                print("  New nodes added to tableau:")
                for node in trace.nodes_created:
                    print(f"    Node {node.id}: {node.formula}")

            if trace.branches_created:
                print(f"  Created {len(trace.branches_created)} new branches")

    def get_rule_summary(self) -> list[str]:
        """Get a summary of all rules applied."""
        summary = []

        # Group by rule type
        rule_counts: dict[str, int] = {}
        for trace in self.rule_applications:
            rule_counts[trace.rule_name] = rule_counts.get(trace.rule_name, 0) + 1

        summary.append("Rules Applied:")
        for rule, count in sorted(rule_counts.items()):
            summary.append(f"  {rule}: {count} time(s)")

        # Show LLM evaluations specifically
        llm_evals = [t for t in self.rule_applications if "LLM-Eval" in t.rule_name]
        if llm_evals:
            summary.append("\nLLM Evaluations:")
            for trace in llm_evals:
                formula = trace.source_node.formula.formula
                produced = trace.produced_formulas[0] if trace.produced_formulas else []

                # Determine what the LLM returned
                result = "unknown"
                if any(sf.sign.symbol == "t" for sf in produced):
                    if any("*" in str(sf.formula) for sf in produced):
                        result = "glut (both true)"
                    else:
                        result = "true"
                elif any(sf.sign.symbol == "f" for sf in produced):
                    if len([sf for sf in produced if sf.sign.symbol == "f"]) > 1:
                        result = "gap (no knowledge)"
                    else:
                        result = "false"
                elif any(sf.sign.symbol == "e" for sf in produced):
                    result = "undefined"

                summary.append(f"  {formula} → {result}")

        return summary
