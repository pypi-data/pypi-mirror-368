#!/usr/bin/env python3
"""
Convert VALIDATION_COMPREHENSIVE.md to a better formatted LaTeX document.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


class ValidationToLatexConverterV2:
    """Convert validation markdown to better formatted LaTeX."""
    
    def __init__(self):
        self.preamble = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{mathtools}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage[margin=0.8in]{geometry}
\usepackage{fancyvrb}
\usepackage{tabularx}
\usepackage{array}
\usepackage{graphicx}

% Better verbatim settings
\fvset{
    fontsize=\footnotesize,
    xleftmargin=0.5em,
    numbers=none,
    framesep=2mm,
    breaklines=true,
    breakanywhere=true
}

% Define colors
\definecolor{formulabg}{rgb}{0.95,0.95,0.98}
\definecolor{treebg}{rgb}{0.98,0.98,0.95}
\definecolor{outputbg}{rgb}{0.95,0.98,0.95}

% Custom commands for logic
\newcommand{\wkrq}{\textsc{wKrQ}}
\newcommand{\acrq}{\textsc{ACrQ}}
\newcommand{\tsign}[1]{\mathsf{#1}}

% Better spacing
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}

% Reduce section spacing
\usepackage{titlesec}
\titlespacing*{\section}{0pt}{1em}{0.5em}
\titlespacing*{\subsection}{0pt}{0.8em}{0.3em}
\titlespacing*{\subsubsection}{0pt}{0.5em}{0.2em}

\title{\Large\textbf{wKrQ Comprehensive Validation Document}}
\author{Generated from Test Suite}
\date{\today}

\begin{document}

\maketitle

\section*{Abstract}
This document provides comprehensive validation of the wKrQ (weak Kleene logic with restricted Quantification) 
and ACrQ (Analytic Containment with restricted Quantification) implementations. All examples are automatically 
generated from the test suite, showing tableau trees, models, and countermodels.

\tableofcontents
\newpage

"""
        
    def escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        # Order matters - do backslash first
        text = text.replace('\\', r'\textbackslash{}')
        text = text.replace('&', r'\&')
        text = text.replace('%', r'\%')
        text = text.replace('$', r'\$')
        text = text.replace('#', r'\#')
        text = text.replace('_', r'\_')
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        text = text.replace('~', r'\textasciitilde{}')
        text = text.replace('^', r'\textasciicircum{}')
        return text
    
    def convert_formula_display(self, formula: str) -> str:
        """Convert a formula for display in math mode."""
        # Basic replacements
        formula = formula.replace('|-', r' \vdash ')
        formula = formula.replace('&', r' \land ')
        formula = formula.replace('|', r' \lor ')
        formula = formula.replace('~', r' \neg ')
        formula = formula.replace('->', r' \to ')
        
        # Quantifiers
        formula = re.sub(r'\[forall\s+(\w+)\s+([^\]]+)\]', r'[\\forall \1 : \2]', formula)
        formula = re.sub(r'\[exists\s+(\w+)\s+([^\]]+)\]', r'[\\exists \1 : \2]', formula)
        
        # Handle star predicates
        formula = re.sub(r'(\w+)\*\(', r'\1^*\(', formula)
        
        return formula
    
    def format_example(self, example_data: Dict) -> str:
        """Format a single example."""
        lines = []
        
        # Extract components
        title = example_data.get('title', '')
        formula = example_data.get('formula', '')
        sign = example_data.get('sign', '')
        mode = example_data.get('mode', '')
        note = example_data.get('note', '')
        output = example_data.get('output', '')
        
        # Start example box
        lines.append(r'\noindent\fbox{\parbox{\textwidth}{')
        
        # Title
        lines.append(f'\\textbf{{{title}}}\\\\[0.3em]')
        
        # Formula in a colored box
        if formula:
            display_formula = self.convert_formula_display(formula)
            lines.append(f'\\colorbox{{formulabg}}{{\\parbox{{\\dimexpr\\textwidth-2\\fboxsep\\relax}}{{')
            lines.append(f'\\textbf{{Formula:}} $\\displaystyle {display_formula}$')
            lines.append('}}\\\\[0.3em]')
        
        # Metadata
        if sign:
            lines.append(f'\\textbf{{Sign:}} $\\tsign{{{sign}}}$ ')
        if mode:
            lines.append(f'\\textbf{{Mode:}} \\{mode.lower()} ')
        if note:
            lines.append(f'\\\\[0.2em]\\textit{{{note}}}')
        
        if sign or mode or note:
            lines.append('\\\\[0.3em]')
        
        # Output handling
        if output:
            if 'Tableau tree:' in output:
                lines.append(self.format_tableau_output(output))
            elif any(x in output for x in ['Models', 'Countermodels', 'Valid', 'Invalid']):
                lines.append(self.format_model_output(output))
            else:
                lines.append(self.format_generic_output(output))
        
        # Close example box
        lines.append('}}')
        
        return '\n'.join(lines)
    
    def format_tableau_output(self, output: str) -> str:
        """Format tableau tree output."""
        lines = output.split('\n')
        result = []
        
        # Find where the tree starts
        tree_start = 0
        for i, line in enumerate(lines):
            if re.match(r'^\s*\d+\.', line):
                tree_start = i
                break
        
        # Add header info
        for i in range(tree_start):
            if lines[i].strip():
                result.append(lines[i].strip() + '\\\\')
        
        # Format the tree
        result.append('\\begin{Verbatim}[frame=single,bgcolor=treebg]')
        
        for i in range(tree_start, len(lines)):
            line = lines[i]
            if line.strip():
                # Replace tree characters
                line = line.replace('├──', '|--')
                line = line.replace('└──', '`--')
                line = line.replace('│', '|')
                line = line.replace('×', 'X')
                # Escape LaTeX special chars
                line = self.escape_latex(line)
                result.append(line)
        
        result.append('\\end{Verbatim}')
        
        return '\n'.join(result)
    
    def format_model_output(self, output: str) -> str:
        """Format model/countermodel output."""
        lines = output.split('\n')
        result = []
        
        in_models = False
        for line in lines:
            if line.strip():
                if any(marker in line for marker in ['✓ Valid', '✗ Invalid', 'Satisfiable:']):
                    # Status line
                    clean_line = line.replace('✓', 'VALID:')
                    clean_line = clean_line.replace('✗', 'INVALID:')
                    result.append(f'\\textbf{{{clean_line}}}\\\\')
                elif 'Models' in line or 'Countermodels' in line:
                    result.append(f'\\textbf{{{line}}}')
                    result.append('\\begin{Verbatim}[frame=single,bgcolor=outputbg]')
                    in_models = True
                elif in_models and line.strip().startswith(tuple('0123456789')):
                    # Model line
                    result.append(self.escape_latex(line))
                elif 'Tableau tree:' in line:
                    # Switch to tableau mode
                    if in_models:
                        result.append('\\end{Verbatim}')
                        in_models = False
                    result.append('\\\\[0.3em]')
                    # Return and let tableau handler take over
                    remaining = '\n'.join(lines[lines.index(line):])
                    result.append(self.format_tableau_output(remaining))
                    break
                elif line.strip() and not line.startswith(' '):
                    if in_models:
                        result.append('\\end{Verbatim}')
                        in_models = False
                    result.append(line + '\\\\')
        
        if in_models:
            result.append('\\end{Verbatim}')
        
        return '\n'.join(result)
    
    def format_generic_output(self, output: str) -> str:
        """Format generic output."""
        clean_output = output.replace('✓', 'Valid')
        clean_output = clean_output.replace('✗', 'Invalid')
        clean_output = self.escape_latex(clean_output)
        
        return f'''\\begin{{Verbatim}}[frame=single,bgcolor=outputbg]
{clean_output}
\\end{{Verbatim}}'''
    
    def parse_markdown_example(self, text: str) -> Dict:
        """Parse a markdown example into components."""
        lines = text.strip().split('\n')
        example = {
            'title': '',
            'formula': '',
            'sign': '',
            'mode': '',
            'note': '',
            'output': ''
        }
        
        # Extract title
        for line in lines:
            if line.startswith('### '):
                example['title'] = line[4:].strip()
                break
        
        # Extract other components
        in_code = False
        code_lines = []
        
        for line in lines:
            if line.strip() == '```':
                if in_code:
                    example['output'] = '\n'.join(code_lines)
                    code_lines = []
                in_code = not in_code
            elif in_code:
                code_lines.append(line)
            elif line.startswith('Formula:'):
                match = re.search(r'`([^`]+)`', line)
                if match:
                    example['formula'] = match.group(1)
            elif line.startswith('Sign:'):
                example['sign'] = line.split(':')[1].strip()
            elif line.startswith('Mode:'):
                example['mode'] = line.split(':')[1].strip()
            elif line.startswith('*Note:'):
                example['note'] = line[6:].strip('* ')
        
        return example
    
    def convert_document(self, input_file: Path, output_file: Path):
        """Convert the entire validation document to LaTeX."""
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Split into sections
        sections = re.split(r'\n(?=## )', content)
        
        latex_content = [self.preamble]
        
        # Skip the header section and process main content
        for section in sections[1:]:
            if not section.strip():
                continue
                
            lines = section.split('\n')
            section_title = ''
            
            # Find section title
            for line in lines:
                if line.startswith('## '):
                    section_title = line[3:].strip()
                    latex_content.append(f'\n\\section{{{section_title}}}')
                    
                    # Find and add description
                    for i, desc_line in enumerate(lines):
                        if i > 0 and desc_line.strip() and not desc_line.startswith('#'):
                            latex_content.append(f'{desc_line.strip()}\n')
                            break
                    break
            
            # Split into examples
            example_texts = re.split(r'\n(?=### )', section)
            
            for example_text in example_texts[1:]:  # Skip section header
                if example_text.strip():
                    example = self.parse_markdown_example(example_text)
                    if example['title']:
                        latex_content.append(self.format_example(example))
                        latex_content.append('\n\\vspace{0.5em}\n')
        
        # Close document
        latex_content.append('\n\\end{document}')
        
        # Write output
        with open(output_file, 'w') as f:
            f.write('\n'.join(latex_content))
        
        print(f"LaTeX document generated: {output_file}")
        print(f"To compile: pdflatex {output_file.name}")


def main():
    parser = argparse.ArgumentParser(description='Convert validation document to better LaTeX')
    parser.add_argument(
        '--input', 
        default='docs/VALIDATION_COMPREHENSIVE.md',
        help='Input markdown file'
    )
    parser.add_argument(
        '--output',
        default='docs/VALIDATION_COMPREHENSIVE_V2.tex',
        help='Output LaTeX file'
    )
    
    args = parser.parse_args()
    
    converter = ValidationToLatexConverterV2()
    converter.convert_document(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()