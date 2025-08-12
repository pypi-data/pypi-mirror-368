#!/usr/bin/env python3
"""
Debug test for Pluto integrated proof issue.
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.cli import TableauTreeRenderer
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_pluto_llm_evaluator():
    """LLM evaluator with post-2006 Pluto knowledge"""
    
    knowledge = {
        "Planet(pluto)": BilateralTruthValue(positive=FALSE, negative=TRUE),
        "OrbitsSun(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
        "Spherical(pluto)": BilateralTruthValue(positive=TRUE, negative=FALSE),
    }
    
    def evaluate_formula(formula):
        key = str(formula)
        result = knowledge.get(key, BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED))
        print(f"    LLM evaluating {key} -> positive={result.positive}, negative={result.negative}")
        return result
    
    return evaluate_formula


def main():
    print("Debugging Pluto integrated proof...")
    
    # Set up the formal reasoning
    universal_rule = parse("[∀x OrbitsSun(x) & Spherical(x)] Planet(x)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    print(f"Initial formulas: {[str(sf) for sf in signed_formulas]}")
    
    # Create tableau with LLM evaluator
    llm_eval = create_pluto_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    
    # Check root
    print(f"\nRoot formula: {tableau.root.formula}")
    
    # Manually step through construction
    iteration = 0
    max_iterations = 10
    
    while tableau.open_branches and iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*50}")
        print(f"Iteration {iteration}:")
        
        # Get branch
        branch = tableau.open_branches[0]
        print(f"  Branch has {len(branch.nodes)} nodes")
        print(f"  Ground terms: {branch.ground_terms}")
        
        # Check if branch is complete
        is_complete = tableau._branch_is_complete(branch)
        print(f"  Branch is complete? {is_complete}")
        
        # Get applicable rules
        applicable_rules = tableau._get_prioritized_rules(branch)
        print(f"  Found {len(applicable_rules)} applicable rules")
        
        if applicable_rules:
            for node, rule in applicable_rules[:3]:  # Show first 3
                print(f"    - {rule.name} for {node.formula}")
            
            # Apply first rule
            node, rule_info = applicable_rules[0]
            print(f"\n  Applying: {rule_info.name} to node {node.id}: {node.formula}")
            tableau.apply_rule(node, branch, rule_info)
            
            # Show resulting nodes
            print(f"  After application: {len(branch.nodes)} nodes")
            for i, n in enumerate(branch.nodes[-3:] if len(branch.nodes) > 3 else branch.nodes):
                print(f"    Node {n.id}: {n.formula}")
        else:
            print("  No applicable rules - stopping")
            break
    
    print(f"\n{'='*50}")
    print("Final tableau:")
    
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(tableau)
    print(tree_str)
    
    print(f"\nResult: Satisfiable={tableau.construct().satisfiable}")


if __name__ == "__main__":
    main()