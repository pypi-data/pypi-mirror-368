#!/usr/bin/env python3
"""
Prototype: Show complete rule applications in tableau visualization.

This explores different ways to help users understand what rules produce,
even when branches close before all conclusions are added.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, FALSE
from wkrq.tableau import Tableau, TableauNode, RuleInfo


@dataclass
class RuleApplication:
    """Record of a rule application."""
    rule_name: str
    source_node_id: int
    source_formula: str
    conclusions: List[List[str]]  # What the rule produced
    nodes_added: List[int]  # Which nodes were actually added
    branch_closed_at: Optional[str] = None  # Which formula caused closure


class InstrumentedTableau(ACrQTableau):
    """Tableau that records complete rule applications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rule_applications: List[RuleApplication] = []
        self.complete_application_mode = True  # Add all conclusions even after closure
    
    def apply_rule(self, node: TableauNode, branch, rule_info: RuleInfo) -> None:
        """Apply a rule and record what it produces."""
        # Record the rule application
        application = RuleApplication(
            rule_name=rule_info.name,
            source_node_id=node.id,
            source_formula=str(node.formula),
            conclusions=[[str(sf) for sf in conclusion_set] 
                        for conclusion_set in rule_info.conclusions],
            nodes_added=[]
        )
        
        # Mark node as processed (original behavior)
        if rule_info.instantiation_constant:
            key = (node.id, str(node.formula.formula))
            if key not in branch.universal_instantiations:
                branch.universal_instantiations[key] = set()
            branch.universal_instantiations[key].add(rule_info.instantiation_constant)
        else:
            branch.processed_node_ids.add(node.id)
        
        conclusions = rule_info.conclusions
        
        if len(conclusions) == 1:
            # Non-branching rule
            branch_already_closed = branch.is_closed
            
            for i, signed_formula in enumerate(conclusions[0]):
                formula_key = (str(signed_formula.formula), signed_formula.sign)
                if (formula_key not in branch.formula_index or 
                    not branch.formula_index[formula_key]):
                    
                    # Create new node
                    new_node = self._create_node(signed_formula)
                    node.add_child(new_node, rule_info.name)
                    application.nodes_added.append(new_node.id)
                    
                    # Add to branch
                    closed = self._add_node_to_branch(new_node, branch)
                    
                    if closed and not branch_already_closed:
                        application.branch_closed_at = str(signed_formula)
                        branch_already_closed = True
                        
                        # In complete mode, continue adding nodes even after closure
                        if not self.complete_application_mode:
                            break
        else:
            # Branching rule - call parent implementation
            super().apply_rule(node, branch, rule_info)
            # Record which nodes were added (simplified for now)
            for child in node.children:
                if child.rule_applied == rule_info.name:
                    application.nodes_added.append(child.id)
        
        self.rule_applications.append(application)
    
    def print_rule_log(self):
        """Print a detailed log of all rule applications."""
        print("\n" + "=" * 60)
        print("COMPLETE RULE APPLICATION LOG")
        print("=" * 60)
        
        for i, app in enumerate(self.rule_applications, 1):
            print(f"\n{i}. {app.rule_name}")
            print(f"   Source: Node {app.source_node_id} - {app.source_formula}")
            print(f"   Produced:")
            
            for j, conclusion_set in enumerate(app.conclusions):
                if len(app.conclusions) > 1:
                    print(f"   Branch {j+1}:")
                for formula in conclusion_set:
                    added = any(self.nodes[nid].formula.__str__() == formula 
                               for nid in app.nodes_added)
                    status = "✓" if added else "✗"
                    if not added and app.branch_closed_at:
                        status += " (branch closed)"
                    print(f"     {status} {formula}")
            
            if app.branch_closed_at:
                print(f"   Note: Branch closed at {app.branch_closed_at}")


def create_sedna_llm_evaluator():
    """LLM evaluator with gap for Sedna."""
    def evaluate_formula(formula):
        if str(formula) == "Planet(sedna)":
            return BilateralTruthValue(positive=FALSE, negative=FALSE)
        return BilateralTruthValue(positive=FALSE, negative=FALSE)
    return evaluate_formula


def main():
    print("Tableau Visualization Prototype: Complete Rule Applications")
    print("=" * 60)
    
    # Test case: Sedna with universal rule
    universal_rule = parse("[∀X OrbitsSun(X) & Spherical(X)]Planet(X)")
    orbits_fact = parse("OrbitsSun(sedna)")
    spherical_fact = parse("Spherical(sedna)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print("\nInput formulas:")
    for sf in signed_formulas:
        print(f"  {sf}")
    
    # Create instrumented tableau
    llm_eval = create_sedna_llm_evaluator()
    tableau = InstrumentedTableau(signed_formulas, llm_evaluator=llm_eval)
    
    # First, try with normal mode (stops on closure)
    print("\n" + "-" * 60)
    print("STANDARD MODE (stops adding formulas when branch closes):")
    print("-" * 60)
    
    tableau.complete_application_mode = False
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    print("\n" + renderer.render_ascii(result.tableau))
    
    # Print rule log
    tableau.print_rule_log()
    
    # Now try with complete mode
    print("\n" + "=" * 60)
    print("COMPLETE MODE (adds all formulas even after closure):")
    print("=" * 60)
    
    tableau2 = InstrumentedTableau(signed_formulas, llm_evaluator=llm_eval)
    tableau2.complete_application_mode = True
    result2 = tableau2.construct()
    
    print("\n" + renderer.render_ascii(result2.tableau))
    
    # Print rule log
    tableau2.print_rule_log()
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print("In standard mode, we see:")
    print("  • LLM evaluation produces both f:Planet(sedna) and f:Planet*(sedna)")
    print("  • But only f:Planet(sedna) appears in the tree")
    print("  • Because it immediately contradicts t:Planet(sedna)")
    print("\nIn complete mode, we could show:")
    print("  • All formulas that each rule produces")
    print("  • Even those that don't get added due to closure")
    print("\nThe rule log shows the complete picture regardless of mode.")


if __name__ == "__main__":
    main()