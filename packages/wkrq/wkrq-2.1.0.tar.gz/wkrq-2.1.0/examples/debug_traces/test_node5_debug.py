#!/usr/bin/env python3
"""
Debug why node 5 isn't marked as closing
"""

from wkrq import parse, Tableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer


def main():
    # Simpler test to understand node 5
    universal_rule = parse("[∀x OrbitsSun(x) & Spherical(x)] Planet(x)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    # Use regular Tableau (no LLM) to see the structure
    tableau = Tableau(signed_formulas)
    result = tableau.construct()
    
    print("Tree structure:")
    def print_tree(node, indent=0):
        print("  " * indent + f"ID={node.id}: {node.formula} (leaf: {not bool(node.children)})")
        for child in node.children:
            print_tree(child, indent + 1)
    
    if tableau.nodes:
        print_tree(tableau.nodes[0])
    
    print("\n" + "="*50)
    print("Path analysis for node 5:")
    
    # Find node 5
    node5 = None
    for node in tableau.nodes:
        if node.id == 5:
            node5 = node
            break
    
    if node5:
        print(f"Node 5: {node5.formula}")
        print(f"Is leaf: {not bool(node5.children)}")
        
        # Check path from root to node 5
        print("\nPath from root to node 5:")
        path = []
        current = node5
        while current:
            path.append(f"ID={current.id}: {current.formula}")
            current = current.parent
        
        for p in reversed(path):
            print(f"  {p}")
    
    print("\n" + "="*50)
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(result.tableau)
    print(tree_str)


if __name__ == "__main__":
    main()