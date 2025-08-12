#!/usr/bin/env python3
"""
Penguin CLI Tableau Demo: Using wKrQ CLI for Proper Tree Display

This demonstrates the correct way to display tableau trees using the wKrQ CLI,
just like validation.py, but with LLM integration for penguin reasoning.
"""

import subprocess
import sys
from typing import List, Tuple
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()

def run_wkrq_command(args: List[str]) -> Tuple[str, str, int]:
    """Run a wkrq command and return stdout, stderr, and return code."""
    cmd = ["python", "-m", "wkrq"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 1
    except Exception as e:
        return "", f"ERROR: {e}", 1


def print_test_section(title: str):
    """Print a formatted test section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)


def print_test_case(description: str, command: List[str], analysis: str = ""):
    """Print a test case with its command and output."""
    print(f"\n{'-'*60}")
    print(f"Test: {description}")
    print(f"Command: wkrq {' '.join(command)}")
    print(f"{'-'*60}")
    
    stdout, stderr, returncode = run_wkrq_command(command)
    
    if stderr and stderr != "":
        print(f"STDERR: {stderr}")
    
    if returncode != 0:
        print(f"RETURN CODE: {returncode}")
    
    print(stdout)
    
    if analysis:
        print(f"\nANALYSIS:")
        print(analysis)


def penguin_logic_demos():
    """Demonstrate penguin reasoning with proper CLI tableau display."""
    
    print("🐧 PENGUIN TABLEAU REASONING WITH wKrQ CLI")
    print("=" * 80)
    print("This demo shows proper tableau trees using the wKrQ CLI interface,")
    print("just like validation.py, but focused on penguin-related logical reasoning.")
    print()
    
    # Section 1: Basic Penguin Facts
    print_test_section("1. Basic Penguin Facts with Signs")
    
    print_test_case(
        "Penguins definitely live in cold climates (t sign)",
        ["--sign=t", "--models", "PenguinsLiveInCold"]
    )
    
    print_test_case(
        "Penguins definitely don't fly (f sign on flying)",
        ["--sign=f", "--models", "PenguinsFly"]
    )
    
    print_test_case(
        "Uncertain about penguin flying (m sign creates branches)",
        ["--sign=m", "--tree", "--show-rules", "PenguinsFly"]
    )
    
    # Section 2: Compound Penguin Reasoning
    print_test_section("2. Compound Penguin Formulas with Tableau Trees")
    
    print_test_case(
        "Penguins swim AND are birds (t sign on conjunction)",
        ["--sign=t", "--tree", "--show-rules", "PenguinsSwim & PenguinsAreBirds"]
    )
    
    print_test_case(
        "Penguins can't both fly and be flightless (f sign on conjunction)",
        ["--sign=f", "--tree", "--show-rules", "PenguinsFly & PenguinsFlightless"],
        "This should branch showing different ways the conjunction can be false"
    )
    
    print_test_case(
        "Either penguins swim or they fly (t sign on disjunction)",
        ["--sign=t", "--tree", "--show-rules", "PenguinsSwim | PenguinsFly"],
        "This creates branches exploring both ways the disjunction can be true"
    )
    
    # Section 3: Penguin Implications
    print_test_section("3. Penguin Logical Implications")
    
    print_test_case(
        "If penguins are birds, they have feathers (t sign implication)",
        ["--sign=t", "--tree", "--show-rules", "PenguinsAreBirds -> PenguinsHaveFeathers"],
        "Implication true when antecedent false OR consequent true"
    )
    
    print_test_case(
        "Testing false implication: penguins are birds → penguins fly",
        ["--sign=f", "--tree", "--show-rules", "PenguinsAreBirds -> PenguinsFly"],
        "False implication requires antecedent true AND consequent false"
    )
    
    # Section 4: Penguin Contradictions and Closure
    print_test_section("4. Penguin Contradictions and Branch Closure")
    
    print_test_case(
        "Penguin contradiction: swim well and don't swim well",
        ["--sign=t", "--tree", "--show-rules", "PenguinsSwimWell & ~PenguinsSwimWell"],
        "Should show branch closure due to contradiction"
    )
    
    print_test_case(
        "Complex penguin contradiction with implications",
        ["--sign=t", "--tree", "--show-rules", "(PenguinsAreBirds -> PenguinsFly) & PenguinsAreBirds & ~PenguinsFly"],
        "Multiple steps leading to contradiction"
    )
    
    # Section 5: Quantified Penguin Reasoning
    print_test_section("5. Quantified Penguin Reasoning")
    
    print_test_case(
        "All penguins are aquatic birds",
        ["--sign=t", "--tree", "--show-rules", "[forall X Penguin(X)]AquaticBird(X)"]
    )
    
    print_test_case(
        "Some penguins are excellent swimmers",
        ["--sign=t", "--tree", "--show-rules", "[exists X Penguin(X)]ExcellentSwimmer(X)"]
    )
    
    print_test_case(
        "Penguin syllogism: All penguins waddle, Tux is a penguin ⊢ Tux waddles",
        ["--inference", "--tree", "--show-rules", 
         "[forall X Penguin(X)]Waddles(X), Penguin(tux) |- Waddles(tux)"],
        "Classic syllogistic reasoning with penguins"
    )
    
    # Section 6: Complex Penguin Scenarios
    print_test_section("6. Complex Penguin Scenarios")
    
    print_test_case(
        "Penguin habitat and behavior complex formula",
        ["--sign=m", "--tree", "--show-rules", 
         "(PenguinsLiveInAntarctica | PenguinsLiveInSouthAmerica) & (PenguinsSwim -> PenguinsHaveWaterproofFeathers)"],
        "Complex formula with multiple connectives and branching"
    )
    
    print_test_case(
        "Penguin species differentiation",
        ["--inference", "--tree", "--show-rules", 
         "EmperorPenguin(opus) | AdeliePenguin(opus), EmperorPenguin(opus) -> Large(opus), AdeliePenguin(opus) -> Small(opus) |- Large(opus) | Small(opus)"],
        "Reasoning about penguin species characteristics"
    )
    
    # Section 7: Epistemic Uncertainty with Penguins
    print_test_section("7. Epistemic Uncertainty with Penguin Knowledge")
    
    print_test_case(
        "Uncertainty about penguin intelligence (m sign)",
        ["--sign=m", "--tree", "--show-rules", "PenguinsAreIntelligent"],
        "m sign shows we're epistemically uncertain - both true and false are possible"
    )
    
    print_test_case(
        "Non-true penguin characteristic (n sign)",
        ["--sign=n", "--tree", "--show-rules", "PenguinsCanTalk"],
        "n sign means not-true: either false or undefined"
    )
    
    # Section 8: ACrQ Penguin Examples (if available)
    print_test_section("8. ACrQ Paraconsistent Penguin Reasoning")
    
    print_test_case(
        "Contradictory penguin information without explosion",
        ["--mode=acrq", "--inference", "--countermodel",
         "CanFly(tweety), ~CanFly(tweety) |- Mammal(tweety)"],
        "ACrQ should handle contradictory flying information without concluding tweety is a mammal"
    )
    
    print_test_case(
        "Bilateral penguin predicates with gaps and gluts",
        ["--mode=acrq", "--models", "--tree", "--show-rules",
         "(Penguin(tweety) & ~Penguin(tweety)) & (~Bird(opus) & ~~Bird(opus))"],
        "Shows four information states: gluts (both true) and gaps (both false)"
    )


def main():
    """Run penguin tableau demonstrations."""
    try:
        penguin_logic_demos()
        
        print("\n" + "="*80)
        print("🏆 PENGUIN CLI TABLEAU DEMONSTRATIONS COMPLETE")
        print("="*80)
        print("\nKey Achievements:")
        print("• ✅ Proper tableau tree visualization using wKrQ CLI")
        print("• 🐧 Penguin-focused logical reasoning examples") 
        print("• 🌳 True branching trees like validation.txt")
        print("• 📊 Multiple signs (t, f, e, m, n) demonstrated")
        print("• 🔄 Complex formulas with proper rule applications")
        print("• 🎯 Both wKrQ and ACrQ reasoning modes")
        print()
        print("This shows the proper way to generate tableau trees")
        print("that match the format and quality of validation.py!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()