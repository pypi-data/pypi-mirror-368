#!/usr/bin/env python3
"""
Penguin Tableau Trace: Step-by-Step Reasoning Visualization

This example shows the detailed step-by-step construction of the ACrQ tableau
for penguin reasoning, including LLM evaluations and rule applications.
Perfect for demonstrating the formal reasoning process to others.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from wkrq import ACrQTableau, PropositionalAtom, PredicateFormula, Constant, SignedFormula, t, f
from bilateral_truth import zeta_c, create_llm_evaluator, Assertion
from bilateral_truth.truth_values import TruthValueComponent
from wkrq.semantics import BilateralTruthValue, TRUE, FALSE, UNDEFINED


class TracingACrQTableau(ACrQTableau):
    """Extended ACrQ tableau that traces its construction step-by-step."""
    
    def __init__(self, initial_formulas, llm_evaluator=None):
        print("🏗️  INITIALIZING TABLEAU")
        print("=" * 50)
        super().__init__(initial_formulas, llm_evaluator)
        self.step_counter = 0
        self.trace_enabled = True
        
        print("Initial formulas:")
        for i, sf in enumerate(initial_formulas):
            print(f"  {i+1}. {sf}")
        print()
    
    def construct(self):
        """Construct tableau with detailed tracing."""
        print("🚀 STARTING TABLEAU CONSTRUCTION")
        print("=" * 50)
        print()
        
        max_iterations = 1000
        iteration = 0
        
        while (
            self.open_branches
            and not self.is_complete()
            and iteration < max_iterations
            and len(self.branches) < self.max_branching_factor
        ):
            iteration += 1
            self.step_counter += 1
            
            print(f"📋 STEP {self.step_counter}: Iteration {iteration}")
            print("-" * 30)
            
            # Show current branch status
            print(f"Current status:")
            print(f"  • Open branches: {len(self.open_branches)}")
            print(f"  • Closed branches: {len(self.closed_branches)}")
            print(f"  • Total nodes: {len(self.nodes)}")
            print()
            
            # Select branch
            selected_branch = self._select_optimal_branch()
            if not selected_branch:
                print("❌ No branch available for processing")
                break
                
            print(f"🎯 Selected branch {selected_branch.id} for processing")
            self._trace_branch_state(selected_branch)
            
            # Get applicable rules
            applicable_rules = self._get_prioritized_rules(selected_branch)
            if not applicable_rules:
                print("✅ No more rules applicable - branch complete")
                break
                
            # Show applicable rules
            print(f"📜 Found {len(applicable_rules)} applicable rule(s):")
            for i, (node, rule_info) in enumerate(applicable_rules):
                priority = "HIGH" if rule_info.priority <= 5 else "MEDIUM" if rule_info.priority <= 10 else "LOW"
                print(f"  {i+1}. {rule_info.name} on {node.formula} (Priority: {priority})")
            print()
            
            # Apply highest priority rule
            best_rule = applicable_rules[0]
            node, rule_info = best_rule
            
            print(f"⚡ APPLYING RULE: {rule_info.name}")
            print(f"   Formula: {node.formula}")
            print(f"   Type: {rule_info.rule_type.value}")
            
            if "LLM-Eval" in rule_info.name:
                print("   🤖 LLM EVALUATION:")
                
            # Apply the rule
            self.apply_rule(node, selected_branch, rule_info)
            
            # Show rule conclusions
            if rule_info.conclusions:
                print(f"   Conclusions ({len(rule_info.conclusions)} sets):")
                for i, conclusion_set in enumerate(rule_info.conclusions):
                    if len(rule_info.conclusions) > 1:
                        print(f"     Branch {i+1}:")
                    for j, sf in enumerate(conclusion_set):
                        print(f"     {'  ' if len(rule_info.conclusions) > 1 else ''}• {sf}")
            
            # Check for branch closure
            closed_this_step = []
            for branch in self.branches:
                if branch.is_closed and branch not in self.closed_branches:
                    closed_this_step.append(branch)
                    
            if closed_this_step:
                print(f"   🚫 Branch(es) closed: {[b.id for b in closed_this_step]}")
                for branch in closed_this_step:
                    print(f"      Reason: {branch.closure_reason}")
            
            print()
            
            # Show updated branch states
            self._trace_all_branches()
            print()
            
        # Final results
        return self._construct_final_result()
    
    def _trace_branch_state(self, branch):
        """Show detailed state of a branch."""
        print(f"   📁 Branch {branch.id} contents ({len(branch.formulas)} formulas):")
        for i, sf in enumerate(branch.formulas):
            print(f"      {i+1}. {sf}")
        print()
    
    def _trace_all_branches(self):
        """Show state of all branches."""
        print("🌳 CURRENT TABLEAU STATE:")
        for branch in self.branches:
            status = "CLOSED" if branch.is_closed else "OPEN"
            print(f"   Branch {branch.id}: {status} ({len(branch.formulas)} formulas)")
            if branch.is_closed:
                print(f"      Closure: {branch.closure_reason}")
    
    def _construct_final_result(self):
        """Construct final result with summary."""
        result = super().construct()
        
        print("🏁 TABLEAU CONSTRUCTION COMPLETE")
        print("=" * 50)
        print(f"Final Results:")
        print(f"  • Satisfiable: {result.satisfiable}")
        print(f"  • Models found: {len(result.models)}")
        print(f"  • Open branches: {result.open_branches}")
        print(f"  • Closed branches: {result.closed_branches}")
        print(f"  • Total nodes: {result.total_nodes}")
        print()
        
        if result.models:
            print("📊 MODELS FOUND:")
            for i, model in enumerate(result.models):
                print(f"   Model {i+1}:")
                for atom, value in sorted(model.valuations.items()):
                    print(f"     {atom} = {value}")
                
                if hasattr(model, 'bilateral_valuations') and model.bilateral_valuations:
                    print(f"   Bilateral valuations:")
                    for atom, btv in sorted(model.bilateral_valuations.items()):
                        state = ("gap" if btv.is_gap() else 
                               "glut" if btv.is_glut() else 
                               "determinate")
                        print(f"     {atom}: {btv} ({state})")
        
        return result
    
    def _create_llm_evaluation_rule(self, signed_formula, branch):
        """Create LLM rule with tracing."""
        rule_info = super()._create_llm_evaluation_rule(signed_formula, branch)
        
        if rule_info and self.trace_enabled:
            # Show LLM evaluation details
            if hasattr(self, '_last_llm_evaluation'):
                btv = self._last_llm_evaluation
                evidence_type = ("Strong positive" if btv.positive == TRUE and btv.negative == FALSE else
                               "Strong negative" if btv.positive == FALSE and btv.negative == TRUE else
                               "Contradictory (glut)" if btv.positive == TRUE and btv.negative == TRUE else
                               "Insufficient (gap)" if btv.positive == FALSE and btv.negative == FALSE else
                               "Mixed")
                print(f"      Evidence: {evidence_type}")
                print(f"      Bilateral value: {btv}")
        
        return rule_info


def create_tracing_evaluator():
    """Create LLM evaluator that shows its reasoning."""
    evaluator = create_llm_evaluator('openai', model='gpt-4o-mini')
    
    def evaluate_formula(formula):
        print(f"      🤖 Querying LLM about: '{formula}'")
        
        assertion = Assertion(str(formula))
        result = zeta_c(assertion, evaluator.evaluate_bilateral)
        u, v = result.u, result.v
        
        pos = TRUE if u == TruthValueComponent.TRUE else (UNDEFINED if u == TruthValueComponent.UNDEFINED else FALSE)
        neg = TRUE if v == TruthValueComponent.TRUE else (UNDEFINED if v == TruthValueComponent.UNDEFINED else FALSE)
        
        print(f"      📊 LLM response: <{u},{v}> → BilateralTruthValue({pos}, {neg})")
        
        btv = BilateralTruthValue(positive=pos, negative=neg)
        return btv
    
    return evaluate_formula


def demonstrate_penguin_tableau_trace():
    """Run detailed tableau trace for penguin reasoning."""
    
    print("🐧 PENGUIN REASONING: DETAILED TABLEAU TRACE")
    print("=" * 60)
    print()
    print("This demo shows step-by-step how ACrQ + bilateral-truth")
    print("constructs a formal reasoning tableau for penguin knowledge.")
    print()
    print("Scenario: Testing if we can assert 'Penguins are excellent swimmers'")
    print("The LLM will evaluate this claim and provide bilateral evidence.")
    print()
    
    # Create tracing evaluator
    llm_eval = create_tracing_evaluator()
    
    # Simple test case
    penguin_swimmers = PropositionalAtom("Penguins are excellent swimmers")
    initial_formula = SignedFormula(t, penguin_swimmers)
    
    print("🎯 TEST FORMULA:")
    print(f"   {initial_formula}")
    print()
    
    # Create tracing tableau
    tableau = TracingACrQTableau([initial_formula], llm_evaluator=llm_eval)
    
    # Run construction with tracing
    result = tableau.construct()
    
    print()
    print("🎓 EDUCATIONAL SUMMARY:")
    print("=" * 50)
    print("This tableau trace demonstrates:")
    print("1. 🏗️  Tableau initialization with signed formulas")
    print("2. 🔄 Iterative rule application process")
    print("3. 🤖 LLM evaluation as a formal tableau rule")
    print("4. 📊 Bilateral evidence integration")
    print("5. ✅ Model extraction from open branches")
    print()
    print("Key insight: LLM knowledge becomes part of formal logical reasoning!")


def demonstrate_contradiction_trace():
    """Show detailed trace of contradiction handling."""
    
    print("\n" + "🔥 CONTRADICTION HANDLING TRACE" + "\n" + "=" * 60)
    print()
    print("Testing how ACrQ handles contradictory penguin assertions:")
    print("• t:'Penguins can fly' (positive assertion)")  
    print("• f:'Penguins can fly' (negative assertion)")
    print()
    print("Classical logic: EXPLOSION 💥")
    print("ACrQ: Paraconsistent handling 🛡️")
    print()
    
    llm_eval = create_tracing_evaluator()
    
    # Contradictory formulas
    penguin_fly = PropositionalAtom("Penguins can fly")
    contradictory_formulas = [
        SignedFormula(t, penguin_fly),  # Penguins can fly
        SignedFormula(f, penguin_fly)   # Penguins cannot fly
    ]
    
    print("🎯 TEST FORMULAS:")
    for i, sf in enumerate(contradictory_formulas):
        print(f"   {i+1}. {sf}")
    print()
    
    # Create tracing tableau for contradiction
    tableau = TracingACrQTableau(contradictory_formulas, llm_evaluator=llm_eval)
    result = tableau.construct()
    
    print()
    print("🎓 CONTRADICTION ANALYSIS:")
    print("=" * 50)
    if result.satisfiable:
        print("✅ ACrQ successfully handled the contradiction!")
        print("   • No logical explosion occurred")
        print("   • Paraconsistent reasoning preserved")
    else:
        print("🚫 Branch closed due to formal contradiction")
        print("   • LLM evidence created contradiction")
        print("   • Tableau correctly detected inconsistency")


if __name__ == "__main__":
    try:
        demonstrate_penguin_tableau_trace()
        demonstrate_contradiction_trace()
        
        print("\n" + "🏆 DEMO COMPLETE" + "\n" + "=" * 60)
        print("You now have a detailed view of ACrQ tableau construction")
        print("with LLM integration for paraconsistent reasoning!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure bilateral-truth is installed and API keys are set.")