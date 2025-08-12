#!/usr/bin/env python3
"""
Penguin Detailed Tableau Trace: Complete Step-by-Step Reasoning

This shows the complete tableau construction process with all intermediate steps,
including LLM evaluations, rule applications, and branch management.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from wkrq import ACrQTableau, PropositionalAtom, PredicateFormula, Constant, SignedFormula, t, f
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


def create_verbose_evaluator():
    """Create LLM evaluator with verbose output."""
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        print(f"    🤖 LLM EVALUATION:")
        print(f"       Query: '{formula}'")
        
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        # Determine evidence type
        if pos == TRUE and neg == FALSE:
            evidence = "STRONG POSITIVE (definitely true)"
        elif pos == FALSE and neg == TRUE:
            evidence = "STRONG NEGATIVE (definitely false)"
        elif pos == TRUE and neg == TRUE:
            evidence = "CONTRADICTORY (glut - both true and false evidence)"
        elif pos == FALSE and neg == FALSE:
            evidence = "INSUFFICIENT (gap - no clear evidence either way)"
        else:
            evidence = "MIXED (complex evidence pattern)"
        
        print(f"       Response: <{u},{v}>")
        print(f"       Evidence: {evidence}")
        print(f"       Bilateral Value: positive={pos}, negative={neg}")
        
        return BilateralTruthValue(positive=pos, negative=neg)
    
    return evaluate_formula


def manual_tableau_construction(initial_formulas, llm_evaluator):
    """Manually construct tableau with detailed tracing."""
    
    print("🏗️  MANUAL TABLEAU CONSTRUCTION")
    print("=" * 50)
    
    # Create tableau
    tableau = ACrQTableau(initial_formulas, llm_evaluator=llm_evaluator)
    
    print("📋 INITIAL STATE:")
    print(f"   Branches: {len(tableau.branches)}")
    print(f"   Open branches: {len(tableau.open_branches)}")
    print(f"   Formulas in initial branch:")
    
    initial_branch = tableau.branches[0]
    i = 0
    for (formula_str, sign), node_ids in initial_branch.formula_index.items():
        if node_ids:
            i += 1
            print(f"     {i}. {sign}: {formula_str}")
    print()
    
    step = 0
    while tableau.open_branches and step < 10:  # Limit steps for demo
        step += 1
        print(f"📋 STEP {step}: Rule Application")
        print("-" * 30)
        
        # Select branch to work on
        branch = tableau.open_branches[0]
        print(f"🎯 Working on branch {branch.id}")
        
        # Look for applicable rules
        rules_found = []
        for node_id in branch.node_ids:
            node = tableau.nodes[node_id]
            rule_info = tableau._get_applicable_rule(node, branch)
            if rule_info:
                rules_found.append((node, rule_info))
        
        if not rules_found:
            print("✅ No more applicable rules - branch complete")
            break
            
        print(f"📜 Found {len(rules_found)} applicable rule(s):")
        for i, (node, rule_info) in enumerate(rules_found):
            print(f"   {i+1}. {rule_info.name} on {node.formula}")
        
        # Apply first rule
        node, rule_info = rules_found[0]
        print(f"\n⚡ APPLYING: {rule_info.name}")
        print(f"   On formula: {node.formula}")
        print(f"   Rule type: {rule_info.rule_type.value}")
        
        # Show rule conclusions before application
        if rule_info.conclusions:
            print(f"   Will add {len(rule_info.conclusions)} conclusion set(s):")
            for i, conclusion_set in enumerate(rule_info.conclusions):
                if len(rule_info.conclusions) > 1:
                    print(f"     Set {i+1} (new branch):")
                else:
                    print(f"     Conclusions:")
                for sf in conclusion_set:
                    print(f"       • {sf}")
        
        # Apply the rule
        old_branch_count = len(tableau.branches)
        old_node_count = len(tableau.nodes)
        
        tableau.apply_rule(node, branch, rule_info)
        
        # Show what changed
        new_branch_count = len(tableau.branches)
        new_node_count = len(tableau.nodes)
        
        print(f"\n📈 CHANGES AFTER RULE APPLICATION:")
        print(f"   Branches: {old_branch_count} → {new_branch_count}")
        print(f"   Nodes: {old_node_count} → {new_node_count}")
        print(f"   Open branches: {len(tableau.open_branches)}")
        print(f"   Closed branches: {len(tableau.closed_branches)}")
        
        # Show current branch contents
        print(f"\n🌳 CURRENT BRANCH STATES:")
        for i, br in enumerate(tableau.branches):
            status = "CLOSED" if br.is_closed else "OPEN"
            print(f"   Branch {i}: {status} ({len(br.formulas)} formulas)")
            if len(br.formulas) <= 5:  # Only show details for small branches
                for j, sf in enumerate(br.formulas):
                    print(f"     {j+1}. {sf}")
            if br.is_closed:
                print(f"     Closure reason: {br.closure_reason}")
        print()
    
    # Construct final result
    result = tableau.construct()
    
    print("🏁 FINAL RESULTS:")
    print("=" * 50)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models: {len(result.models)}")
    print(f"Total steps: {step}")
    
    # Display complete tableau tree
    print("\n🌳 COMPLETE TABLEAU TREE:")
    print("=" * 50)
    display_tableau_tree(tableau)
    
    # Display detailed branch analysis
    display_detailed_branch_analysis(tableau)
    
    if result.models:
        print("\n📊 MODELS:")
        for i, model in enumerate(result.models):
            print(f"   Model {i+1}:")
            for atom, value in sorted(model.valuations.items()):
                print(f"     {atom} = {value}")
            
            # Show bilateral valuations if available
            if hasattr(model, 'bilateral_valuations') and model.bilateral_valuations:
                print(f"   Bilateral valuations:")
                for atom, btv in sorted(model.bilateral_valuations.items()):
                    state = ("gap" if btv.is_gap() else 
                           "glut" if btv.is_glut() else 
                           "determinate")
                    print(f"     {atom}: {btv} ({state})")
    
    return result


def display_tableau_tree(tableau):
    """Display the complete tableau tree structure."""
    
    print("Tree structure:")
    print("• Each node shows: [ID] sign:formula (rule applied)")
    print("• Branches are marked as OPEN or CLOSED")
    print("• Parent-child relationships shown with tree lines")
    print()
    
    if not tableau.nodes:
        print("   (Empty tableau)")
        return
    
    # Build parent-child relationships
    children_map = {}
    for node_id, node in tableau.nodes.items():
        children_map[node.id] = []
    
    for node_id, node in tableau.nodes.items():
        if node.parent:
            children_map[node.parent.id].append(node)
    
    # Display tree starting from root
    root = tableau.root
    _display_node_tree(root, children_map, "", True, tableau)
    
    print("\n📋 BRANCH SUMMARY:")
    for i, branch in enumerate(tableau.branches):
        status = "CLOSED" if branch.is_closed else "OPEN"
        node_count = len(branch.node_ids)
        formula_count = len(branch.formula_index)
        
        print(f"   Branch {i}: {status} ({node_count} nodes, {formula_count} formulas)")
        
        if branch.is_closed:
            print(f"      Closure: {branch.closure_reason}")
        
        # Show all formulas in branch
        if formula_count <= 8:  # Only show details for reasonable-sized branches
            print(f"      Formulas:")
            j = 0
            for (formula_str, sign), node_ids in branch.formula_index.items():
                if node_ids:
                    j += 1
                    print(f"        {j}. {sign}: {formula_str}")
        else:
            print(f"      (Too many formulas to display: {formula_count})")


def _display_node_tree(node, children_map, prefix, is_last, tableau):
    """Recursively display tree structure."""
    
    # Determine tree drawing characters
    current_prefix = "└── " if is_last else "├── "
    child_prefix = "    " if is_last else "│   "
    
    # Format node information
    rule_info = f" (via {node.rule_applied})" if node.rule_applied else ""
    node_info = f"[{node.id}] {node.formula}{rule_info}"
    
    print(f"{prefix}{current_prefix}{node_info}")
    
    # Display children
    children = children_map.get(node.id, [])
    for i, child in enumerate(children):
        is_child_last = (i == len(children) - 1)
        _display_node_tree(child, children_map, prefix + child_prefix, is_child_last, tableau)
    
    # If this is a leaf node, show which branch(es) it belongs to
    if not children:
        # Find which branches contain this node
        containing_branches = []
        for i, branch in enumerate(tableau.branches):
            if node.id in branch.node_ids:
                status = "CLOSED" if branch.is_closed else "OPEN"
                containing_branches.append(f"Branch {i} ({status})")
        
        if containing_branches:
            branch_info = ", ".join(containing_branches)
            print(f"{prefix}{'    ' if is_last else '│   '}    ➤ {branch_info}")


def display_detailed_branch_analysis(tableau):
    """Show detailed analysis of each branch."""
    
    print("\n🔍 DETAILED BRANCH ANALYSIS:")
    print("=" * 50)
    
    for i, branch in enumerate(tableau.branches):
        print(f"📁 BRANCH {i}:")
        print(f"   Status: {'CLOSED' if branch.is_closed else 'OPEN'}")
        print(f"   Nodes: {len(branch.node_ids)}")
        print(f"   Formulas: {len(branch.formula_index)}")
        
        if branch.is_closed:
            print(f"   Closure reason: {branch.closure_reason}")
        
        print(f"   Node sequence:")
        for j, node_id in enumerate(branch.node_ids):
            branch_node = tableau.nodes[node_id]
            rule_text = f" (via {branch_node.rule_applied})" if branch_node.rule_applied else " (initial)"
            print(f"     {j+1}. [{branch_node.id}] {branch_node.formula}{rule_text}")
        
        print(f"   Formula set:")
        j = 0
        for (formula_str, sign), node_ids in branch.formula_index.items():
            if node_ids:
                j += 1
                print(f"     {j}. {sign}: {formula_str}")
        
        # Show formula index for debugging
        if hasattr(branch, 'formula_index'):
            print(f"   Formula index summary:")
            sign_counts = {}
            for (formula_str, sign), node_ids in branch.formula_index.items():
                if node_ids:
                    sign_counts[sign] = sign_counts.get(sign, 0) + 1
            for sign, count in sign_counts.items():
                print(f"     {sign}: {count} distinct formulas")
        
        print()


def demonstrate_simple_penguin_fact():
    """Demonstrate with a simple penguin fact."""
    
    print("🐧 DEMONSTRATION 1: Simple Penguin Fact")
    print("=" * 60)
    print()
    print("Testing: t:'Penguins live in cold climates'")
    print("This should trigger LLM evaluation and show the reasoning process.")
    print()
    
    llm_eval = create_verbose_evaluator()
    penguin_fact = PropositionalAtom("Penguins live in cold climates")
    initial_formula = SignedFormula(t, penguin_fact)
    
    result = manual_tableau_construction([initial_formula], llm_eval)
    
    print("\n🎓 What we learned:")
    print("• LLM evaluated the penguin fact")
    print("• Tableau integrated LLM evidence formally") 
    print("• Result shows satisfiability with LLM-grounded knowledge")
    
    return result


def demonstrate_penguin_contradiction():
    """Demonstrate contradiction with penguins."""
    
    print("\n\n🔥 DEMONSTRATION 2: Penguin Contradiction")
    print("=" * 60)
    print()
    print("Testing contradictory assertions:")
    print("• t:'Penguins are tropical birds'")
    print("• f:'Penguins are tropical birds'")
    print()
    
    llm_eval = create_verbose_evaluator()
    penguin_tropical = PropositionalAtom("Penguins are tropical birds")
    
    contradictory_formulas = [
        SignedFormula(t, penguin_tropical),  # Positive assertion
        SignedFormula(f, penguin_tropical)   # Negative assertion
    ]
    
    result = manual_tableau_construction(contradictory_formulas, llm_eval)
    
    print("\n🎓 What we learned:")
    if result.satisfiable:
        print("• ACrQ handled contradiction paraconsistently")
        print("• No logical explosion occurred")
    else:
        print("• Branch closed due to formal contradiction")
        print("• LLM evidence conflicted with assertions")
    
    return result


def demonstrate_predicate_reasoning():
    """Demonstrate with predicate logic."""
    
    print("\n\n🧠 DEMONSTRATION 3: Predicate Logic Reasoning")
    print("=" * 60)
    print()
    print("Testing: t:SwimWell(penguin)")
    print("Using first-order predicate with LLM evaluation.")
    print()
    
    llm_eval = create_verbose_evaluator()
    penguin = Constant("penguin")
    swim_well = PredicateFormula("SwimWell", [penguin])
    initial_formula = SignedFormula(t, swim_well)
    
    result = manual_tableau_construction([initial_formula], llm_eval)
    
    print("\n🎓 What we learned:")
    print("• LLM evaluated predicate formula")
    print("• ACrQ handled first-order reasoning with LLM knowledge")
    print("• Bilateral truth values applied to predicates")
    
    return result


if __name__ == "__main__":
    try:
        print("🎭 PENGUIN TABLEAU REASONING DEMONSTRATIONS")
        print("=" * 80)
        print()
        print("This demo shows detailed tableau construction with LLM integration")
        print("for penguin-related reasoning scenarios.")
        print()
        
        demonstrate_simple_penguin_fact()
        demonstrate_penguin_contradiction()  
        demonstrate_predicate_reasoning()
        
        print("\n" + "🏆 ALL DEMONSTRATIONS COMPLETE" + "\n" + "=" * 80)
        print("Key insights:")
        print("1. 🤖 LLM evaluation becomes formal tableau rule")
        print("2. 📊 Bilateral evidence integrates seamlessly") 
        print("3. 🛡️  Paraconsistent reasoning handles contradictions")
        print("4. 🧠 Works for both propositional and predicate logic")
        print("5. 📋 Every step is formally justified and traceable")
        print()
        print("This demonstrates the paper's theoretical framework in action!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()