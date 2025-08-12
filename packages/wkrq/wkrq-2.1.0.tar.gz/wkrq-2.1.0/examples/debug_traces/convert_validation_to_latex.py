#!/usr/bin/env python3
"""
Convert VALIDATION_COMPREHENSIVE.md to a LaTeX document with proper mathematical formatting.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


class ValidationToLatexConverter:
    """Convert validation markdown to LaTeX format."""
    
    def __init__(self):
        self.preamble = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{mathtools}
\usepackage{bussproofs}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage[margin=1in]{geometry}
\usepackage{tocloft}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{fancyvrb}

% Define colors for syntax highlighting
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.98,0.98,0.98}

% Code listing style
\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
    frame=single
}

\lstset{style=mystyle}

% Custom commands for logic symbols
\newcommand{\wkrq}{\textsc{wKrQ}}
\newcommand{\acrq}{\textsc{ACrQ}}
\newcommand{\tsign}[1]{\mathsf{#1}}
\newcommand{\inference}[2]{#1 \vdash #2}
\newcommand{\noinference}[2]{#1 \nvdash #2}
\newcommand{\restricteq}[2]{[\exists #1]\,#2}
\newcommand{\restrictaq}[2]{[\forall #1]\,#2}

% Theorem environments
\theoremstyle{definition}
\newtheorem{example}{Example}[section]
\newtheorem{definition}{Definition}[section]
\newtheorem{theorem}{Theorem}[section]

\title{wKrQ Comprehensive Validation Document}
\author{Generated from Test Suite}
\date{\today}

\begin{document}

\maketitle

\tableofcontents
\newpage

"""
        
        self.sign_map = {
            't': r'\tsign{t}',
            'f': r'\tsign{f}',
            'e': r'\tsign{e}',
            'm': r'\tsign{m}',
            'n': r'\tsign{n}',
            'v': r'\tsign{v}'
        }
        
    def convert_formula(self, formula: str) -> str:
        """Convert a formula string to LaTeX format."""
        # Start with the original formula
        latex = formula
        
        # Basic logical connectives
        latex = latex.replace('|-', r' \vdash ')
        latex = latex.replace('&', r' \land ')
        latex = latex.replace('|', r' \lor ')
        latex = latex.replace('~', r'\neg ')
        latex = latex.replace('->', r' \to ')
        latex = latex.replace('<->', r' \leftrightarrow ')
        
        # Quantifiers - handle restricted quantification
        # [forall X P(X)]Q(X) -> [\forall X : P(X)]\,Q(X)
        latex = re.sub(r'\[forall\s+(\w+)\s+([^]]+)\]', r'[\\forall \1 : \2]\\,', latex)
        latex = re.sub(r'\[exists\s+(\w+)\s+([^]]+)\]', r'[\\exists \1 : \2]\\,', latex)
        
        # Handle predicates and constants
        # P(x) -> P(x) (already good)
        # P*(x) -> P^*(x)
        latex = re.sub(r'(\w+)\*\(', r'\1^*\(', latex)
        
        # Ensure proper math spacing
        latex = latex.replace('(', r'\left(')
        latex = latex.replace(')', r'\right)')
        
        return latex
    
    def convert_tableau_tree(self, tree_text: str) -> str:
        """Convert tableau tree representation to LaTeX."""
        lines = tree_text.strip().split('\n')
        latex_lines = []
        
        latex_lines.append(r"\begin{Verbatim}[frame=single,fontsize=\small]")
        
        for line in lines:
            # Replace tree drawing characters with ASCII equivalents
            line = line.replace('├──', '|--')
            line = line.replace('└──', '`--')
            line = line.replace('│', '|')
            line = line.replace('×', 'X')
            
            # Escape special LaTeX characters
            line = line.replace('\\', r'\\')
            line = line.replace('{', r'\{')
            line = line.replace('}', r'\}')
            line = line.replace('$', r'\$')
            line = line.replace('&', r'\&')
            line = line.replace('%', r'\%')
            line = line.replace('#', r'\#')
            line = line.replace('_', r'\_')
            
            latex_lines.append(line)
        
        latex_lines.append(r"\end{Verbatim}")
        
        return '\n'.join(latex_lines)
    
    def convert_models(self, models_text: str) -> str:
        """Convert model representation to LaTeX."""
        # Replace problematic characters
        clean_text = models_text
        clean_text = clean_text.replace('✓', 'Valid')
        clean_text = clean_text.replace('✗', 'Invalid')
        clean_text = clean_text.replace('×', 'X')
        # Use verbatim for models to preserve formatting
        return f"\\begin{{Verbatim}}[frame=single,fontsize=\\small]\n{clean_text}\n\\end{{Verbatim}}"
    
    def convert_section(self, section_text: str) -> str:
        """Convert a section of the validation document."""
        lines = section_text.split('\n')
        latex_lines = []
        in_code_block = False
        code_block_content = []
        current_formula = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Handle code blocks
            if line.strip() == '```':
                if in_code_block:
                    # End of code block
                    content = '\n'.join(code_block_content)
                    if 'Tableau tree:' in content:
                        latex_lines.append(self.convert_tableau_tree(content))
                    elif 'Models' in content or 'Countermodels' in content:
                        latex_lines.append(self.convert_models(content))
                    else:
                        # Regular output
                        latex_lines.append(f"\\begin{{Verbatim}}[frame=single,fontsize=\\small]\n{content}\n\\end{{Verbatim}}")
                    code_block_content = []
                    in_code_block = False
                else:
                    in_code_block = True
                i += 1
                continue
            
            if in_code_block:
                code_block_content.append(line)
                i += 1
                continue
            
            # Handle headers
            if line.startswith('###'):
                title = line[3:].strip()
                latex_lines.append(f"\n\\subsubsection{{{title}}}")
            elif line.startswith('##'):
                title = line[2:].strip()
                latex_lines.append(f"\n\\subsection{{{title}}}")
            elif line.startswith('#'):
                title = line[1:].strip()
                latex_lines.append(f"\n\\section{{{title}}}")
            
            # Handle formula lines
            elif line.startswith('Formula:'):
                formula_match = re.search(r'Formula:\s*`([^`]+)`', line)
                if formula_match:
                    formula = formula_match.group(1)
                    current_formula = formula
                    latex_formula = self.convert_formula(formula)
                    latex_lines.append(f"\n\\textbf{{Formula:}} $${latex_formula}$$")
            
            # Handle other metadata
            elif line.startswith('Sign:'):
                sign = line.split(':')[1].strip()
                latex_lines.append(f"\\textbf{{Sign:}} {self.sign_map.get(sign, sign)}")
            elif line.startswith('Mode:'):
                mode = line.split(':')[1].strip()
                latex_lines.append(f"\\textbf{{Mode:}} \\{mode.lower()}")
            elif line.startswith('*Note:'):
                note = line[6:].strip().rstrip('*')
                latex_lines.append(f"\\textit{{Note: {note}}}")
            
            # Handle horizontal rules
            elif line.strip() == '---':
                latex_lines.append("\n\\vspace{0.5em}\\hrule\\vspace{0.5em}")
            
            # Handle regular text
            elif line.strip():
                # Check for inline code
                line = re.sub(r'`([^`]+)`', r'\\texttt{\1}', line)
                # Replace Unicode characters in regular text
                line = line.replace('∃', r'$\exists$')
                line = line.replace('∀', r'$\forall$')
                line = line.replace('⊢', r'$\vdash$')
                line = line.replace('×', r'$\times$')
                line = line.replace('→', r'$\to$')
                line = line.replace('∧', r'$\land$')
                line = line.replace('∨', r'$\lor$')
                line = line.replace('¬', r'$\neg$')
                line = line.replace('✓', r'$\checkmark$')
                line = line.replace('✗', r'$\times$')
                latex_lines.append(line)
            
            i += 1
        
        return '\n'.join(latex_lines)
    
    def convert_document(self, input_file: Path, output_file: Path):
        """Convert the entire validation document to LaTeX."""
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Split into sections
        sections = re.split(r'\n(?=##\s)', content)
        
        latex_content = [self.preamble]
        
        # Process introduction
        intro_section = sections[0]
        intro_lines = intro_section.split('\n')
        latex_lines = []
        
        skip_until = 0
        for i, line in enumerate(intro_lines):
            if i < skip_until:
                continue
                
            if line.startswith('# wKrQ'):
                continue  # Skip title (handled in preamble)
            elif line.startswith('Generated:'):
                continue  # Skip generation timestamp
            elif line.startswith('## Introduction'):
                latex_lines.append("\\section{Introduction}")
            elif line.startswith('### '):
                title = line[4:].strip()
                latex_lines.append(f"\\subsection{{{title}}}")
            elif line.strip() == '## Table of Contents':
                # Skip the table of contents section
                for j in range(i+1, len(intro_lines)):
                    if intro_lines[j].startswith('---'):
                        skip_until = j + 1
                        break
            elif line.strip():
                latex_lines.append(line)
        
        latex_content.append('\n'.join(latex_lines))
        
        # Process main sections
        for section in sections[1:]:
            if section.strip():
                latex_content.append(self.convert_section(section))
        
        # Add document end
        latex_content.append("\n\\end{document}")
        
        # Write output
        with open(output_file, 'w') as f:
            f.write('\n'.join(latex_content))
        
        print(f"LaTeX document generated: {output_file}")
        print(f"To compile: pdflatex {output_file.name}")


def main():
    parser = argparse.ArgumentParser(description='Convert validation document to LaTeX')
    parser.add_argument(
        '--input', 
        default='docs/VALIDATION_COMPREHENSIVE.md',
        help='Input markdown file'
    )
    parser.add_argument(
        '--output',
        default='docs/VALIDATION_COMPREHENSIVE.tex',
        help='Output LaTeX file'
    )
    
    args = parser.parse_args()
    
    converter = ValidationToLatexConverter()
    converter.convert_document(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()