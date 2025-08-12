#!/usr/bin/env python3
"""
Convert validation document to clean, compilable LaTeX.
"""

import re
from pathlib import Path
import argparse


def clean_text_for_latex(text):
    """Clean text for safe LaTeX inclusion."""
    # Replace Unicode symbols
    text = text.replace('∀', 'forall')
    text = text.replace('∃', 'exists')
    text = text.replace('⊢', '|-')
    text = text.replace('×', 'X')
    text = text.replace('→', '->')
    text = text.replace('∧', '&')
    text = text.replace('∨', '|')
    text = text.replace('¬', '~')
    text = text.replace('✓', '[VALID]')
    text = text.replace('✗', '[INVALID]')
    
    # Tree drawing chars
    text = text.replace('├──', '|--')
    text = text.replace('└──', '`--')
    text = text.replace('│', '|')
    
    return text


def convert_validation_to_latex(input_file, output_file):
    """Convert validation markdown to clean LaTeX."""
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Clean all Unicode first
    content = clean_text_for_latex(content)
    
    # LaTeX header
    latex = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amssymb}
\usepackage[margin=0.75in]{geometry}
\usepackage{listings}
\usepackage{hyperref}

% Code listing settings
\lstset{
    basicstyle=\scriptsize\ttfamily,
    breaklines=true,
    frame=single,
    xleftmargin=0pt,
    xrightmargin=0pt,
    breakatwhitespace=false,
    columns=fixed,
    keepspaces=true,
    escapeinside={(*@}{@*)},
    literate={~}{{\textasciitilde}}1
}

\title{wKrQ Comprehensive Validation Document}
\author{Generated from Test Suite}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\newpage

"""
    
    # Split content into sections
    sections = re.split(r'\n(?=## )', content)
    
    # Process each section
    for section in sections[1:]:  # Skip header
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        
        # Get section title
        if lines[0].startswith('## '):
            section_title = lines[0][3:].strip()
            latex += f"\\section{{{section_title}}}\n\n"
            
            # Add description if present
            if len(lines) > 2 and lines[2].strip() and not lines[2].startswith('#'):
                latex += f"{lines[2].strip()}\n\n"
        
        # Find examples
        current_example = []
        in_example = False
        
        for line in lines:
            if line.startswith('### '):
                # Process previous example if any
                if current_example:
                    latex += process_example(current_example)
                    current_example = []
                
                # Start new example
                in_example = True
                current_example = [line]
            elif line.strip() == '---':
                # End of example
                if current_example:
                    latex += process_example(current_example)
                    current_example = []
                in_example = False
            elif in_example:
                current_example.append(line)
        
        # Process last example if any
        if current_example:
            latex += process_example(current_example)
    
    # Close document
    latex += "\\end{document}\n"
    
    # Write output
    with open(output_file, 'w') as f:
        f.write(latex)
    
    print(f"Generated: {output_file}")


def process_example(lines):
    """Process a single example."""
    output = ""
    
    # Get title
    title = ""
    for line in lines:
        if line.startswith('### '):
            title = line[4:].strip()
            break
    
    if title:
        output += f"\\subsection{{{title}}}\n\n"
    
    # Extract components
    formula = ""
    sign = ""
    mode = ""
    note = ""
    code_block = []
    in_code = False
    
    for line in lines:
        if line.strip() == '```':
            in_code = not in_code
            if not in_code and code_block:
                # End of code block - format it
                output += "\\begin{lstlisting}\n"
                output += '\n'.join(code_block)
                output += "\n\\end{lstlisting}\n\n"
                code_block = []
        elif in_code:
            code_block.append(line)
        elif line.startswith('Formula:'):
            match = re.search(r'`([^`]+)`', line)
            if match:
                formula = match.group(1)
                # Convert formula to math mode
                math_formula = formula.replace('|-', r' \vdash ')
                math_formula = math_formula.replace('->', r' \to ')
                math_formula = re.sub(r'\[forall\s+(\w+)\s+([^\]]+)\]', r'[\\forall \1 : \2]', math_formula)
                math_formula = re.sub(r'\[exists\s+(\w+)\s+([^\]]+)\]', r'[\\exists \1 : \2]', math_formula)
                output += f"\\textbf{{Formula:}} $${math_formula}$$\n\n"
        elif line.startswith('Sign:'):
            sign = line.split(':', 1)[1].strip()
            output += f"\\textbf{{Sign:}} {sign}\n\n"
        elif line.startswith('Mode:'):
            mode = line.split(':', 1)[1].strip()
            output += f"\\textbf{{Mode:}} {mode}\n\n"
        elif line.startswith('*Note:'):
            note = line[6:].strip('* ')
            output += f"\\textit{{Note: {note}}}\n\n"
    
    output += "\\vspace{0.5em}\n\n"
    return output


def main():
    parser = argparse.ArgumentParser(description='Convert validation to clean LaTeX')
    parser.add_argument('--input', default='docs/VALIDATION_COMPREHENSIVE.md')
    parser.add_argument('--output', default='docs/VALIDATION_CLEAN.tex')
    
    args = parser.parse_args()
    convert_validation_to_latex(args.input, args.output)


if __name__ == '__main__':
    main()