#!/usr/bin/env python3
"""
Debug why LLM evaluation isn't happening for Planet(pluto)
"""

from wkrq import parse, ACrQTableau, SignedFormula, t
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_debug_llm_evaluator():
    """Debug LLM evaluator"""
    
    def evaluate_formula(formula):
        print(f"      [LLM] Asked to evaluate: {formula}")
        if str(formula) == "Planet(pluto)":
            print(f"      [LLM] Returning FALSE for Planet(pluto)")
            return BilateralTruthValue(positive=FALSE, negative=TRUE)
        print(f"      [LLM] Returning UNDEFINED for {formula}")
        return BilateralTruthValue(positive=UNDEFINED, negative=UNDEFINED)
    
    return evaluate_formula


def main():
    print("Debugging LLM evaluation...")
    
    # The formal rule and facts
    universal_rule = parse("[∀x OrbitsSun(x) & Spherical(x)] Planet(x)")
    orbits_fact = parse("OrbitsSun(pluto)")
    spherical_fact = parse("Spherical(pluto)")
    
    signed_formulas = [
        SignedFormula(t, universal_rule),
        SignedFormula(t, orbits_fact),
        SignedFormula(t, spherical_fact)
    ]
    
    # Create tableau with debug evaluator
    llm_eval = create_debug_llm_evaluator()
    tableau = ACrQTableau(signed_formulas, llm_evaluator=llm_eval)
    
    # Manually step through
    iteration = 0
    max_iterations = 15
    
    while tableau.open_branches and iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*50}")
        print(f"Iteration {iteration}:")
        
        branch = tableau.open_branches[0] if tableau.open_branches else None
        if not branch:
            print("  No open branches")
            break
            
        print(f"  Branch has {len(branch.nodes)} nodes")
        
        # Show all nodes
        for node in branch.nodes:
            print(f"    Node {node.id}: {node.formula} (atomic: {node.formula.formula.is_atomic()})")
        
        # Get applicable rules
        applicable_rules = tableau._get_prioritized_rules(branch)
        print(f"\n  Found {len(applicable_rules)} applicable rules:")
        
        if applicable_rules:
            for node, rule in applicable_rules:
                print(f"    {rule.priority}: {rule.name} for node {node.id}: {node.formula}")
            
            # Apply first rule
            node, rule_info = applicable_rules[0]
            print(f"\n  Applying: {rule_info.name} to node {node.id}")
            tableau.apply_rule(node, branch, rule_info)
        else:
            print("  No applicable rules")
            break
    
    print("\n" + "="*50)
    print("Final tree:")
    from wkrq.cli import TableauTreeRenderer
    renderer = TableauTreeRenderer(show_rules=True)
    tree_str = renderer.render_ascii(tableau)
    print(tree_str)


if __name__ == "__main__":
    main()