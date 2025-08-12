#!/usr/bin/env python3
"""
Debug test for conjunction root expansion issue.
"""

from wkrq import parse, Tableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer

def main():
    print("Testing conjunction root expansion...")
    
    # Simple test case with three formulas that should become a conjunction
    f1 = parse("P")
    f2 = parse("Q")
    f3 = parse("R")
    
    signed_formulas = [
        SignedFormula(t, f1),
        SignedFormula(t, f2),
        SignedFormula(t, f3)
    ]
    
    print(f"Initial formulas: {[str(sf) for sf in signed_formulas]}")
    
    # Create tableau
    tableau = Tableau(signed_formulas)
    
    # Check root
    print(f"\nRoot formula: {tableau.root.formula}")
    print(f"Root is compound? {isinstance(tableau.root.formula.formula, CompoundFormula)}")
    
    # Do one iteration manually
    branch = tableau.open_branches[0]
    print(f"\nBranch has {len(branch.nodes)} nodes")
    print(f"Branch formulas: {[str(sf) for sf in branch.formulas]}")
    print(f"Processed formulas: {getattr(branch, '_processed_formulas', set())}")
    
    # Get applicable rules
    print("\nChecking applicable rules for each node:")
    for i, node in enumerate(branch.nodes):
        rule = tableau._get_applicable_rule(node.formula, branch)
        if rule:
            print(f"  Node {i} ({node.formula}): {rule.name}")
        else:
            print(f"  Node {i} ({node.formula}): No rule applicable")
    
    # Apply first rule if any
    applicable_rules = tableau._get_prioritized_rules(branch)
    if applicable_rules:
        node, rule_info = applicable_rules[0]
        print(f"\nApplying rule: {rule_info.name} to {node.formula}")
        tableau.apply_rule(node, branch, rule_info)
        
        # Check state after application
        print(f"\nAfter applying rule:")
        print(f"  Branch has {len(branch.nodes)} nodes")
        print(f"  Branch formulas: {[str(sf) for sf in branch.formulas]}")
        print(f"  Processed formulas: {getattr(branch, '_processed_formulas', set())}")
        
        # Check for applicable rules again
        print("\nChecking applicable rules again:")
        for i, node in enumerate(branch.nodes):
            rule = tableau._get_applicable_rule(node.formula, branch)
            if rule:
                print(f"  Node {i} ({node.formula}): {rule.name}")
            else:
                print(f"  Node {i} ({node.formula}): No rule applicable")
    
    print("\n" + "="*50)
    print("Full tableau construction:")
    result = tableau.construct()
    
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)
    
    print(f"\nResult: Satisfiable={result.satisfiable}")
    print(f"Total nodes: {result.total_nodes}")


from wkrq.formula import CompoundFormula

if __name__ == "__main__":
    main()