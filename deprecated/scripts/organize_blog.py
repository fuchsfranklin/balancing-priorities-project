import re

# Read the file
with open('../blog/international-equity-factor-tilts.Rmd', 'r', encoding='utf-8') as f:
    content = f.read()

# Split at the setup chunk
parts = content.split('```', 2)
header = parts[0] + '```' + parts[1] + '```\n\n'
body = parts[2]

# Add section headers at key points
replacements = [
    ('Investing can be mind-numbingly', '## Introduction: The Case for Index Funds\n\nInvesting can be mind-numbingly'),
    ('Personal finance author JL Collins', '\n\nPersonal finance author JL Collins'),
    ('Why do index funds win', '\n\nWhy do index funds win'),
    ('The Science Behind the Index Strategy', '## The Science Behind the Index Strategy'),
    ('If the idea of efficient', '\n\nIf the idea of efficient'),
    ('Building on that, the Capital', '\n\nBuilding on that, the Capital'),
    ('This ties nicely to the Efficient', '\n\nThis ties nicely to the Efficient'),
    ('So far we\'ve established', '\n\nSo far we\'ve established'),
    ('But (there\'s always a "but"', '\n\nBut (there\'s always a "but"'),
    ('Beyond the Market: Factor Investing 101', '## Beyond the Market: Factor Investing 101'),
    ('Let\'s say you\'ve embraced', '\n\nLet\'s say you\'ve embraced'),
    ('Think of the market like', '\n\nThink of the market like'),
    ('Where did these ideas', '\n\nWhere did these ideas'),
    ('In plainer language: factor', '\n\nIn plainer language: factor'),
    ('Even Burton Malkiel, in the 50th', '\n\nEven Burton Malkiel, in the 50th'),
    ('To sum up: Index funds', '\n\nTo sum up: Index funds'),
    ('Now, all this theory', '\n\nNow, all this theory'),
    ('The Classic Three-Fund Portfolio', '## The Classic Three-Fund Portfolio (Bogleheads Basics)'),
    ('First stop: the beloved', '\n\nFirst stop: the beloved'),
    ('Of course, you still have', '\n\nOf course, you still have'),
    ('For our purposes here', '\n\nFor our purposes here'),
    ('How has a basic VTI/VXUS', '\n\nHow has a basic VTI/VXUS'),
    ('Now, as a die-hard Boglehead', '\n\nNow, as a die-hard Boglehead'),
    ('Stage 2 – Tweaking the U.S. Core', '## Stage 2: Tweaking the U.S. Core (VTI vs DFUS)'),
    ('Imagine you love your Honda', '\n\nImagine you love your Honda'),
    ('What quirks, you ask?', '\n\nWhat quirks, you ask?'),
    ('Crucially, DFUS still holds', '\n\nCrucially, DFUS still holds'),
    ('The result? Since its mid-2021', '\n\nThe result? Since its mid-2021'),
    ('As an investor who wants', '\n\nAs an investor who wants'),
    ('Let\'s see how DFUS vs VTI', '\n\nLet\'s see how DFUS vs VTI'),
    ('The data likely shows', '\n\nThe data likely shows'),
    ('At this point, I was pretty', '\n\nAt this point, I was pretty'),
    ('Alright, U.S. stocks solved', '\n\nAlright, U.S. stocks solved'),
    ('The Elusive International Upgrade', '## The Elusive International Upgrade: DFAI, DFAE, and the Missing VXUS 2.0'),
    ('Vanguard\'s VXUS (Total International', '\n\nVanguard\'s VXUS (Total International'),
    ('Here\'s the landscape: DFA chose', '\n\nHere\'s the landscape: DFA chose'),
    ('What about performance and approach?', '\n\nWhat about performance and approach?'),
    ('To be fair, Dimensional does', '\n\nTo be fair, Dimensional does'),
    ('For a moment, though', '\n\nFor a moment, though'),
    ('Now, about that factor regression', '\n\nNow, about that factor regression'),
    ('From a practical perspective', '\n\nFrom a practical perspective'),
    ('Thus, my current plan', '\n\nThus, my current plan'),
    ('Avantis Investors, another shop', '\n\nAvantis Investors, another shop'),
    ('Why doesn\'t a DFA "DFIX"', '\n\nWhy doesn\'t a DFA "DFIX"'),
    ('As a result, I find myself', '\n\nAs a result, I find myself'),
    ('For now, my plan is to stick', '\n\nFor now, my plan is to stick'),
    ('In summary, here\'s the journey', '\n\n## Summary: The Journey So Far\n\nIn summary, here\'s the journey'),
    ('I\'ll admit, part of me', '\n\nI\'ll admit, part of me'),
    ('Until then, I\'ll practice', '\n\nUntil then, I\'ll practice'),
    ('Investing, like life, is a journey', '\n\n## Conclusion\n\nInvesting, like life, is a journey'),
    ('In the end, whether you\'re', '\n\nIn the end, whether you\'re'),
]

for old, new in replacements:
    body = body.replace(old, new, 1)

# Write the organized version
with open('../blog/international-equity-factor-tilts.Rmd', 'w', encoding='utf-8') as f:
    f.write(header + body)

print("Blog post reorganized successfully!")
