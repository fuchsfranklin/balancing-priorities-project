import json
import re

# Read R Markdown
with open("blog/international-equity-factor-tilts.Rmd", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Initialize notebook
nb = {
    "cells": [],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "nbformat": 4,
    "nbformat_minor": 4
}

# Add title cell
nb["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# From Pure Indexing to Flirting with Factor Tilts\n",
        "## Finding the Sweet Spot for International Equity\n",
        "### Thinking about Index Inefficiencies and the Hunt for a VXUS Alternative"
    ]
})

# Split content by code chunks
parts = re.split(r'```\{r[^}]*\}|```', content)

# Process each part
in_code = False
for i, part in enumerate(parts):
    part = part.strip()
    if not part:
        continue
    
    # Skip YAML header
    if i == 0 and part.startswith('---'):
        continue
    
    # Alternate between markdown and code
    if in_code:
        # Code cell - convert R to Python comments
        lines = part.split('\n')
        python_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                python_lines.append(line)
            elif 'library(' in line:
                python_lines.append('# ' + line + ' # R code - use pandas, yfinance in Python')
            else:
                python_lines.append('# ' + line)
        
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": python_lines
        })
        in_code = False
    else:
        # Markdown cell
        if part and not part.startswith('---'):
            # Clean up null characters
            part = part.replace('\x00', '')
            nb["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": part.split('\n')
            })
        in_code = True

# Save notebook
with open("blog/international-equity-factor-tilts.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("Jupyter notebook created successfully!")
