import re

# Read with error handling
with open('../blog/international-equity-factor-tilts.Rmd', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find code blocks that need chunk wrapping
# Pattern: lines starting with library(), symbols <-, # Get, etc.
code_patterns = [
    (r'(library\(tidyquant\).*?(?=\n[A-Z]|\n#|$))', 'vti-vxus-comparison'),
    (r'(# Compare VTI and DFUS.*?(?=\(The above|\n[A-Z]|\n#|$))', 'dfus-vti-performance'),
    (r'(# Get DFAX vs VXUS.*?(?=\(Above|\n[A-Z]|\n#|$))', 'dfax-vxus-comparison'),
]

# Wrap each code block in proper chunk syntax
for i, (pattern, chunk_name) in enumerate(code_patterns):
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        for match in matches:
            # Check if already wrapped
            if '```{r' not in content[max(0, content.find(match)-20):content.find(match)]:
                wrapped = f'\n```{{r {chunk_name}}}\n{match.strip()}\n```\n'
                content = content.replace(match, wrapped, 1)

# Write back
with open('../blog/international-equity-factor-tilts.Rmd', 'w', encoding='utf-8') as f:
    f.write(content)

print("R code chunks fixed!")
