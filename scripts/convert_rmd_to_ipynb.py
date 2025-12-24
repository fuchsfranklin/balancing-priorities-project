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

# Add title
nb["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# From Pure Indexing to Flirting with Factor Tilts\\n",
        "## Finding the Sweet Spot for International Equity\\n",
        "### Thinking about Index Inefficiencies and the Hunt for a VXUS Alternative"
    ]
})

print("Script created")
