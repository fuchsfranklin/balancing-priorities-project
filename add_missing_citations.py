import json

with open('blog/international-equity-factor-tilts.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Add missing citations
updates = [
    ('three-fund portfolio typically consists of: (1) a total U.S. stock market index fund (like Vanguard Total Stock Market, ticker VTI)', 
     'three-fund portfolio typically consists of: (1) a total U.S. stock market index fund (like Vanguard Total Stock Market, ticker VTI; Vanguard, 2024)'),
    ('(2) a total international stock index fund (like Vanguard Total International, ticker VXUS)', 
     '(2) a total international stock index fund (like Vanguard Total International, ticker VXUS; Vanguard, 2024)'),
    ('Legendary Bogleheads like Taylor Larimore', 
     'Legendary Bogleheads like Taylor Larimore (Bogleheads Wiki, 2024)'),
    ('As an investor who wants to "do slightly better if possible, but never do worse," DFUS is intriguing',
     'As an investor who wants to "do slightly better if possible, but never do worse," DFUS is intriguing (DFA, 2024; Felix, 2024)'),
    ('Even DFA\'s own description is straightforward: "The fund actively selects US equities',
     'Even DFA\'s own description is straightforward (DFA, 2024): "The fund actively selects US equities'),
    ('DFAI (International Core Equity Market ETF, 0.18% fee)',
     'DFAI (International Core Equity Market ETF, 0.18% fee; DFA, 2024)'),
    ('DFAE (Emerging Core Equity Market ETF, 0.35% fee)',
     'DFAE (Emerging Core Equity Market ETF, 0.35% fee; DFA, 2024)'),
    ('DFAX (World ex-US Core Equity 2 ETF, 0.28% fee)',
     'DFAX (World ex-US Core Equity 2 ETF, 0.28% fee; DFA, 2024)'),
    ('Avantis Investors, another shop I admire (founded by ex-DFA folks',
     'Avantis Investors, another shop I admire (founded by ex-DFA folks; Avantis, 2024'),
    ('AVDE (developed int\'l, 0.23% fee)',
     'AVDE (developed int\'l, 0.23% fee; Avantis, 2024)'),
    ('AVEM (emerging, 0.33% fee)',
     'AVEM (emerging, 0.33% fee; Avantis, 2024)'),
]

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        content = ''.join(cell['source'])
        for old, new in updates:
            if old in content:
                content = content.replace(old, new)
        cell['source'] = content.split('\n')

with open('blog/international-equity-factor-tilts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Missing citations added')
