"""
wKrQ command-line interface.

Comprehensive CLI for wKrQ logic with tableau visualization and inference testing.
"""

import argparse
import json
import sys
from dataclasses import asdict
from typing import TYPE_CHECKING

from . import __version__
from .api import InferenceResult, check_inference
from .parser import ParseError, parse, parse_inference
from .signs import SignedFormula, f, sign_from_string, t
from .tableau import Tableau, TableauNode, TableauResult, solve

if TYPE_CHECKING:
    from .acrq_parser import SyntaxMode


class TableauTreeRenderer:
    """Render tableau trees in various formats."""

    def __init__(
        self,
        show_rules: bool = False,
        show_steps: bool = False,
        highlight_closures: bool = False,
        compact: bool = False,
    ):
        self.show_rules = show_rules
        self.show_steps = show_steps
        self.highlight_closures = highlight_closures
        self.compact = compact
        self.closed_leaf_nodes: set[int] = set()  # Track which nodes are closure points
        self.branch_map: dict[int, list[int]] = {}  # Map nodes to their branches
        self.max_formula_width: int = 0  # Track maximum formula width for alignment

    def render_ascii(self, tableau: Tableau) -> str:
        """Render tableau as ASCII art tree."""
        if not tableau.nodes:
            return "Empty tableau"

        # First, identify which leaf nodes are at the end of closed branches
        self._mark_closed_paths(tableau)

        # Calculate maximum formula width for alignment
        if self.show_rules:
            self.max_formula_width = 0  # Reset before calculating
            self._calculate_max_width(tableau.root, 0, is_unicode=False)

        lines: list[str] = []
        self._render_node_ascii(tableau.root, lines, "", True)
        return "\n".join(lines)

    def _calculate_max_width(
        self, node: "TableauNode", depth: int, is_unicode: bool = False
    ) -> None:
        """Calculate maximum formula width in the tree for alignment."""
        # Calculate the width of this node's display
        if is_unicode:
            prefix_width = (
                depth * 5
            )  # Unicode indentation is 5 chars ("│    " or "     ")
        else:
            prefix_width = depth * 4  # ASCII indentation is 4 chars ("│   " or "    ")

        node_width = len(f"{node.id:>2}. {node.formula}")
        if not node.children and node.id in self.closed_leaf_nodes:
            node_width += 3  # Add space for "  ×"

        total_width = prefix_width + node_width
        self.max_formula_width = max(self.max_formula_width, total_width)

        # Recurse for children
        for child in node.children:
            self._calculate_max_width(child, depth + 1, is_unicode)

    def _mark_closed_paths(self, tableau: Tableau) -> None:
        """Identify leaf nodes that represent closure points.

        Uses the unified representation to directly check
        which nodes caused closures.
        """
        self.closed_leaf_nodes = set()

        # Unified tableau - nodes have closure tracking
        for node_id, node in tableau.nodes.items():
            if node.causes_closure and not node.children:
                self.closed_leaf_nodes.add(node_id)

    def _render_node_ascii(
        self, node: TableauNode, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Recursively render node and children."""
        # Node representation with better formatting
        node_str = f"{node.id:>2}. {node.formula}"

        # Add × mark for closed leaf nodes before rule name
        if not node.children and node.id in self.closed_leaf_nodes:
            node_str += "  ×"

        # Add rule name inline if available and requested
        # Include the parent node ID that the rule was applied to
        if self.show_rules and node.rule_applied:
            # Calculate current width including prefix
            current_width = len(prefix)
            if prefix:
                current_width += 4  # Length of connector ("├── " or "└── ")
            current_width += len(node_str)

            # Calculate padding needed
            padding_needed = max(1, self.max_formula_width - current_width + 5)
            padding = " " * padding_needed

            if node.parent:
                node_str += f"{padding}[{node.rule_applied}: {node.parent.id}]"
            else:
                # Root node case
                node_str += f"{padding}[{node.rule_applied}]"

        # Add prefix
        if prefix:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + node_str)
        else:
            lines.append(node_str)

        # Handle children
        if node.children:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension

            for i, child in enumerate(node.children):
                is_child_last = i == len(node.children) - 1
                self._render_node_ascii(child, lines, new_prefix, is_child_last)

    def render_unicode(self, tableau: Tableau) -> str:
        """Render tableau with Unicode box drawing."""
        if not tableau.nodes:
            return "Empty tableau"

        # First, identify which leaf nodes are at the end of closed branches
        self._mark_closed_paths(tableau)

        # Calculate maximum formula width for alignment
        if self.show_rules:
            self.max_formula_width = 0  # Reset before calculating
            self._calculate_max_width(tableau.root, 0, is_unicode=True)

        lines: list[str] = []
        self._render_node_unicode(tableau.root, lines, "", True)
        return "\n".join(lines)

    def _render_node_unicode(
        self, node: TableauNode, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Recursively render node with Unicode characters."""
        # Node representation with better formatting
        node_str = f"{node.id:>2}. {node.formula}"

        # Add × mark for closed leaf nodes before rule name
        if not node.children and node.id in self.closed_leaf_nodes:
            node_str += "  ×"

        # Add rule name inline if available and requested
        # Include the parent node ID that the rule was applied to
        if self.show_rules and node.rule_applied:
            # Calculate current width including prefix
            current_width = len(prefix)
            if prefix:
                current_width += 5  # Length of Unicode connector ("├─── " or "└─── ")
            current_width += len(node_str)

            # Calculate padding needed
            padding_needed = max(1, self.max_formula_width - current_width + 5)
            padding = " " * padding_needed

            if node.parent:
                node_str += f"{padding}[{node.rule_applied}: {node.parent.id}]"
            else:
                # Root node case
                node_str += f"{padding}[{node.rule_applied}]"

        # Add prefix with Unicode
        if prefix:
            connector = "└─── " if is_last else "├─── "
            lines.append(prefix + connector + node_str)
        else:
            lines.append(node_str)

        # Handle children
        if node.children:
            extension = "     " if is_last else "│    "
            new_prefix = prefix + extension

            for i, child in enumerate(node.children):
                is_child_last = i == len(node.children) - 1
                self._render_node_unicode(child, lines, new_prefix, is_child_last)

    def render_latex(self, tableau: Tableau) -> str:
        """Generate LaTeX/TikZ code for tableau tree."""
        lines = [
            "\\begin{tikzpicture}[",
            "  node distance=1.5cm,",
            "  every node/.style={draw, rectangle, minimum width=2cm, text width=3cm, align=center}",
            "]",
        ]

        # Generate nodes
        node_positions = {}
        for i, (_node_id, node) in enumerate(tableau.nodes.items()):
            tikz_id = f"n{node.id}"
            node_positions[node.id] = tikz_id

            formula_str = str(node.formula).replace("&", "\\land").replace("|", "\\lor")
            formula_str = formula_str.replace("->", "\\rightarrow").replace(
                "~", "\\neg"
            )

            if i == 0:
                lines.append(f"  \\node ({tikz_id}) {{{node.id}. {formula_str}}};")
            else:
                # Position relative to parent
                if node.parent:
                    parent_id = f"n{node.parent.id}"
                    lines.append(
                        f"  \\node ({tikz_id}) [below of={parent_id}] {{{node.id}. {formula_str}}};"
                    )

        # Generate edges
        for _node_id, node in tableau.nodes.items():
            if node.parent:
                parent_id = f"n{node.parent.id}"
                tikz_id = f"n{node.id}"
                rule_label = node.rule_applied or ""
                lines.append(
                    f"  \\draw[->] ({parent_id}) -- node[right] {{{rule_label}}} ({tikz_id});"
                )

        lines.append("\\end{tikzpicture}")
        return "\n".join(lines)

    def render_json(self, tableau: Tableau) -> dict:
        """Generate JSON representation of tableau tree."""
        nodes = []
        for _node_id, node in tableau.nodes.items():
            node_data = {
                "id": node.id,
                "formula": str(node.formula),
                "rule": node.rule_applied,
                "closed": node.causes_closure,
                "closure_reason": (
                    f"Contradicts node {node.contradicts_with}"
                    if node.causes_closure
                    else None
                ),
                "children": [child.id for child in node.children],
            }
            if node.parent:
                node_data["parent"] = node.parent.id
            nodes.append(node_data)

        return {
            "nodes": nodes,
            "open_branches": len(tableau.open_branches),
            "closed_branches": len(tableau.closed_branches),
            "total_nodes": len(tableau.nodes),
        }


def display_result(
    result: TableauResult,
    show_models: bool = True,
    show_stats: bool = False,
    debug: bool = False,
) -> None:
    """Display tableau result."""
    print(f"Satisfiable: {result.satisfiable}")

    if show_models and result.models:
        print(f"Models ({len(result.models)}):")
        for i, model in enumerate(result.models, 1):
            print(f"  {i}. {model}")

    if show_stats:
        print("\nStatistics:")
        print(f"  Open branches: {result.open_branches}")
        print(f"  Closed branches: {result.closed_branches}")
        print(f"  Total nodes: {result.total_nodes}")

    if debug and result.tableau:
        print("\nDebug info:")
        print(f"  Branch details: {len(result.tableau.branches)} total branches")
        for i, branch in enumerate(result.tableau.branches):
            status = "CLOSED" if branch.is_closed else "OPEN"
            print(f"    Branch {i}: {status} ({len(branch.node_ids)} nodes)")


def display_inference_result(
    result: InferenceResult, explain: bool = False, show_countermodels: bool = True
) -> None:
    """Display inference test result."""
    if result.valid:
        print("✓ Valid inference")
    else:
        print("✗ Invalid inference")
        if result.countermodels and show_countermodels:
            print("Countermodels:")
            for i, model in enumerate(result.countermodels, 1):
                print(f"  {i}. {model}")

    if explain:
        print("\nExplanation:")
        print(f"Testing satisfiability of: {result.inference.to_formula()}")
        display_result(result.tableau_result, show_models=False, show_stats=True)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="wKrQ - Weak Kleene logic with restricted quantification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wkrq "p & ~p"                    # Test satisfiability
  wkrq --sign=M "p | ~p"           # Test with M sign
  wkrq "p, p -> q |- q"            # Test inference validity
  wkrq --inference "p, p -> q, q"  # Last item is conclusion when using --inference
  wkrq --tree "p & (q | r)"        # Show tableau tree
  wkrq --models "p | q"            # Show all models
  wkrq --tree --format=unicode "p -> q"  # Unicode tree display

  # ACrQ mode (bilateral predicates)
  wkrq --mode=acrq "Human(alice) & ¬Human(alice)"  # Transparent mode (default)
  wkrq --mode=acrq --syntax=bilateral "Human*(alice)"  # Bilateral mode
  wkrq --mode=acrq "Human(x) -> Nice(x), Human(alice) |- Nice(alice)"  # Inference
  wkrq --mode=acrq --inference "P(a), ~P(a), Q(b)"  # ACrQ inference with --inference flag
        """,
    )

    parser.add_argument("input", nargs="?", help="Formula or inference to evaluate")
    parser.add_argument("--version", action="version", version=f"wKrQ {__version__}")
    parser.add_argument(
        "--sign",
        default="t",
        choices=["t", "f", "e", "m", "n"],
        help="Sign to test (default: t)",
    )

    # Logic mode selection
    parser.add_argument(
        "--mode",
        choices=["wkrq", "acrq"],
        default="wkrq",
        help="Logic mode: wkrq (standard) or acrq (bilateral predicates)",
    )
    parser.add_argument(
        "--syntax",
        choices=["transparent", "bilateral", "mixed"],
        default="transparent",
        help="ACrQ syntax mode (only for --mode=acrq)",
    )
    parser.add_argument("--models", action="store_true", help="Show all models")
    parser.add_argument("--stats", action="store_true", help="Show tableau statistics")
    parser.add_argument("--debug", action="store_true", help="Show debug information")

    # Inference testing
    parser.add_argument(
        "--inference",
        action="store_true",
        help="Treat input as inference (premises |- conclusion)",
    )
    parser.add_argument(
        "--consequence",
        choices=["strong", "weak"],
        default="strong",
        help="Type of consequence relation",
    )
    parser.add_argument(
        "--explain", action="store_true", help="Explain inference result"
    )
    parser.add_argument(
        "--countermodel",
        action="store_true",
        help="Show countermodel for invalid inference (default: show only if invalid)",
    )

    # Tree visualization
    parser.add_argument("--tree", action="store_true", help="Display tableau tree")
    parser.add_argument(
        "--format",
        choices=["ascii", "unicode", "latex", "json"],
        default="ascii",
        help="Tree display format",
    )
    parser.add_argument(
        "--show-rules", action="store_true", help="Show rule names in tree"
    )
    parser.add_argument(
        "--show-steps", action="store_true", help="Show step numbers in tree"
    )
    parser.add_argument(
        "--highlight-closures", action="store_true", help="Highlight closed branches"
    )
    parser.add_argument("--compact", action="store_true", help="Compact tree display")
    parser.add_argument(
        "--interactive", action="store_true", help="Step-by-step tableau construction"
    )
    parser.add_argument(
        "--trace", action="store_true", help="Show complete construction trace"
    )
    parser.add_argument(
        "--trace-verbose", action="store_true", help="Show verbose construction trace"
    )

    # Output formats
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    return parser


def handle_acrq_mode(args: argparse.Namespace) -> None:
    """Handle ACrQ mode processing."""
    from .acrq_parser import SyntaxMode

    # Map syntax argument to enum
    syntax_map = {
        "transparent": SyntaxMode.TRANSPARENT,
        "bilateral": SyntaxMode.BILATERAL,
        "mixed": SyntaxMode.MIXED,
    }
    syntax_mode = syntax_map[args.syntax]

    if args.inference or "|-" in args.input:
        handle_acrq_inference(args, syntax_mode)
    else:
        handle_acrq_formula(args, syntax_mode)


def _split_premises(premises_str: str) -> list[str]:
    """Split premises by commas, respecting parentheses and brackets."""
    premises = []
    current_premise = ""
    depth = 0

    for char in premises_str:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == "," and depth == 0:
            # Found a top-level comma, complete current premise
            if current_premise.strip():
                premises.append(current_premise.strip())
            current_premise = ""
            continue

        current_premise += char

    # Don't forget the last premise
    if current_premise.strip():
        premises.append(current_premise.strip())

    return premises


def _parse_inference_input(input_str: str, use_inference_flag: bool) -> str:
    """Parse input to add |- separator if using --inference flag."""
    if use_inference_flag and "|-" not in input_str:
        # Parse more carefully to handle formulas with nested commas (like quantifiers)
        # Strategy: Find the last top-level comma by tracking bracket depth
        depth = 0
        last_comma_pos = -1

        for i, char in enumerate(input_str):
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                last_comma_pos = i

        if last_comma_pos > 0:
            premises = input_str[:last_comma_pos].strip()
            conclusion = input_str[last_comma_pos + 1 :].strip()
            return f"{premises} |- {conclusion}"
        else:
            raise ParseError(
                "Inference format requires premises and conclusion separated by comma"
            )
    return input_str


def handle_acrq_inference(args: argparse.Namespace, syntax_mode: "SyntaxMode") -> None:
    """Handle ACrQ inference processing."""
    from .acrq_parser import parse_acrq_formula
    from .acrq_tableau import ACrQTableau

    # Parse input to handle --inference flag
    input_str = _parse_inference_input(args.input, args.inference)

    # Parse premises and conclusion separately
    parts = input_str.split("|-")
    if len(parts) != 2:
        raise ParseError(f"Invalid inference format: {input_str}")

    # Parse premises
    premises = []
    if parts[0].strip():
        # Split premises properly, respecting parentheses and brackets
        premise_strings = _split_premises(parts[0].strip())
        for premise_str in premise_strings:
            premise = parse_acrq_formula(premise_str.strip(), syntax_mode)
            premises.append(premise)

    # Parse conclusion
    conclusion = parse_acrq_formula(parts[1].strip(), syntax_mode)

    # Create signed formulas for tableau
    initial_formulas = [SignedFormula(t, p) for p in premises]
    initial_formulas.append(SignedFormula(f, conclusion))

    # Construct ACrQ tableau
    tableau = ACrQTableau(initial_formulas)
    result = tableau.construct()

    # Display result
    is_valid = not result.satisfiable

    if args.json:
        output = {
            "type": "acrq_inference",
            "premises": [str(p) for p in premises],
            "conclusion": str(conclusion),
            "valid": is_valid,
            "syntax_mode": args.syntax,
        }
        if not is_valid and result.models:
            output["countermodels"] = [str(m) for m in result.models]
        print(json.dumps(output, indent=2))
    else:
        print(f"ACrQ Inference ({args.syntax} mode):")
        print(f"  Premises: {', '.join(str(p) for p in premises)}")
        print(f"  Conclusion: {conclusion}")

        if is_valid:
            print("  ✓ Valid inference")
        else:
            print("  ✗ Invalid inference")
            # Show countermodels only if invalid (default) or if --countermodel is specified
            if result.models and (not is_valid or args.countermodel):
                print("  Countermodels:")
                for i, model in enumerate(result.models, 1):
                    print(f"    {i}. {model}")

        if args.tree and result.tableau:
            print("\nTableau tree:")
            renderer = TableauTreeRenderer(
                args.show_rules,
                args.show_steps,
                args.highlight_closures,
                args.compact,
            )
            tree_str = getattr(renderer, f"render_{args.format}")(result.tableau)
            print(tree_str)


def handle_acrq_formula(args: argparse.Namespace, syntax_mode: "SyntaxMode") -> None:
    """Handle ACrQ single formula processing."""
    from .acrq_parser import parse_acrq_formula
    from .acrq_tableau import ACrQTableau

    # Single ACrQ formula
    formula = parse_acrq_formula(args.input, syntax_mode)
    sign = sign_from_string(args.sign)
    signed_formula = SignedFormula(sign, formula)

    # Construct ACrQ tableau
    tableau = ACrQTableau([signed_formula])
    result = tableau.construct()

    # Display result
    if args.json:
        output = {
            "type": "acrq_formula",
            "formula": str(formula),
            "sign": args.sign,
            "satisfiable": result.satisfiable,
            "syntax_mode": args.syntax,
        }
        if result.models and args.models:
            output["models"] = [str(m) for m in result.models]
        print(json.dumps(output, indent=2))
    else:
        print(f"ACrQ Formula ({args.syntax} mode): {formula}")
        print(f"Sign: {args.sign}")
        print(f"Satisfiable: {result.satisfiable}")

        if args.models and result.models:
            print(f"\nModels ({len(result.models)}):")
            for i, model in enumerate(result.models, 1):
                print(f"  {i}. {model}")

        if args.stats:
            print("\nStatistics:")
            print(f"  Total nodes: {result.total_nodes}")
            print(f"  Open branches: {result.open_branches}")
            print(f"  Closed branches: {result.closed_branches}")

        if args.tree and result.tableau:
            print("\nTableau tree:")
            renderer = TableauTreeRenderer(
                args.show_rules,
                args.show_steps,
                args.highlight_closures,
                args.compact,
            )
            tree_str = getattr(renderer, f"render_{args.format}")(result.tableau)
            print(tree_str)


def handle_wkrq_mode(args: argparse.Namespace) -> None:
    """Handle standard wKrQ mode processing."""
    if args.inference or "|-" in args.input:
        handle_wkrq_inference(args)
    else:
        handle_wkrq_formula(args)


def handle_wkrq_inference(args: argparse.Namespace) -> None:
    """Handle wKrQ inference processing."""
    # Parse input to handle --inference flag
    input_str = _parse_inference_input(args.input, args.inference)
    inference = parse_inference(input_str)

    # Enable tracing if requested
    trace = args.trace or args.trace_verbose
    inference_result = check_inference(inference, trace=trace)

    if args.json:
        output = {
            "type": "inference",
            "inference": str(inference),
            "valid": inference_result.valid,
            "countermodels": [asdict(m) for m in inference_result.countermodels],
        }
        print(json.dumps(output, indent=2))
    else:
        # Show countermodels only if invalid (default) or if --countermodel is specified
        show_countermodels = not inference_result.valid or args.countermodel
        display_inference_result(
            inference_result, args.explain or args.debug, show_countermodels
        )

        if args.tree and inference_result.tableau_result.tableau:
            print("\nTableau tree:")
            renderer = TableauTreeRenderer(
                args.show_rules,
                args.show_steps,
                args.highlight_closures,
                args.compact,
            )
            tree_str = render_tree(
                inference_result.tableau_result.tableau,
                args.format,
                renderer,
            )
            print(tree_str)

        # Show trace if requested
        if (
            args.trace or args.trace_verbose
        ) and inference_result.tableau_result.construction_trace:
            print("\n" + "=" * 70)
            print("CONSTRUCTION TRACE")
            print("=" * 70)
            inference_result.tableau_result.print_trace(verbose=args.trace_verbose)


def handle_wkrq_formula(args: argparse.Namespace) -> None:
    """Handle wKrQ single formula processing."""
    formula = parse(args.input)
    sign = sign_from_string(args.sign)

    # Enable tracing if requested
    trace = args.trace or args.trace_verbose
    tableau_result = solve(formula, sign, trace=trace)

    if args.json:
        output = {
            "type": "formula",
            "formula": str(formula),
            "sign": str(sign),
            "satisfiable": tableau_result.satisfiable,
            "models": [asdict(m) for m in tableau_result.models],
            "stats": {
                "open_branches": tableau_result.open_branches,
                "closed_branches": tableau_result.closed_branches,
                "total_nodes": tableau_result.total_nodes,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        display_result(tableau_result, args.models, args.stats, args.debug)

        if args.tree and tableau_result.tableau:
            print("\nTableau tree:")
            renderer = TableauTreeRenderer(
                args.show_rules,
                args.show_steps,
                args.highlight_closures,
                args.compact,
            )
            tree_str = render_tree(tableau_result.tableau, args.format, renderer)
            print(tree_str)

        # Show trace if requested
        if (args.trace or args.trace_verbose) and tableau_result.construction_trace:
            print("\n" + "=" * 70)
            print("CONSTRUCTION TRACE")
            print("=" * 70)
            tableau_result.print_trace(verbose=args.trace_verbose)


def main() -> None:
    """Main CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Interactive mode if no input
    if not args.input:
        interactive_mode()
        return

    try:
        # Parse input based on mode
        if args.mode == "acrq":
            handle_acrq_mode(args)
        else:
            handle_wkrq_mode(args)

    except ParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if args.debug:
            raise
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def render_tree(
    tableau: Tableau, format_type: str, renderer: TableauTreeRenderer
) -> str:
    """Render tableau tree in specified format."""
    if format_type == "ascii":
        return renderer.render_ascii(tableau)
    elif format_type == "unicode":
        return renderer.render_unicode(tableau)
    elif format_type == "latex":
        return renderer.render_latex(tableau)
    elif format_type == "json":
        json_data = renderer.render_json(tableau)
        return json.dumps(json_data, indent=2)
    else:
        raise ValueError(f"Unknown format: {format_type}")


def interactive_mode() -> None:
    """Interactive REPL mode."""
    print("wKrQ Interactive Mode")
    print("Commands: formula, inference (P |- Q), help, quit")
    print()

    while True:
        try:
            line = input("wkrq> ").strip()

            if not line:
                continue

            if line.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if line.lower() in ["help", "h"]:
                print("Commands:")
                print("  formula           - Enter a formula to test")
                print("  P, Q |- R         - Test inference")
                print("  help              - Show this help")
                print("  quit              - Exit")
                continue

            # Parse and evaluate
            if "|-" in line:
                inference = parse_inference(line)
                result = check_inference(inference)
                display_inference_result(result)
            else:
                formula = parse(line)
                tableau_result = solve(formula, t)
                display_result(tableau_result)

        except ParseError as e:
            print(f"Parse error: {e}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
