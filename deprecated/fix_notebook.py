"""Fix the corrupted notebook cell"""
import json

# Read the notebook
with open('blog/international-equity-factor-tilts.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The new source code for the VTI/VXUS cell
new_source = '''# VTI/VXUS Growth Comparison (Net of Expense Ratios)
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load pre-downloaded data
prices = pd.read_csv('../data/prices_data.csv', index_col=0, parse_dates=True)
prices = prices[['VTI', 'VXUS']].loc['2011-01-28':'2024-12-31']

# Daily returns
returns = prices.pct_change().dropna()

# Expense ratios (annual) - deducted daily
EXPENSE_RATIOS = {'VTI': 0.0003, 'VXUS': 0.0007}  # 0.03% and 0.07%
daily_cost = {k: v / 252 for k, v in EXPENSE_RATIOS.items()}

# Net returns after fees
returns_net = returns.copy()
for ticker in ['VTI', 'VXUS']:
    returns_net[ticker] = returns[ticker] - daily_cost[ticker]

# Portfolio allocations
allocations = {
    '100% US (VTI)': {'VTI': 1.0, 'VXUS': 0.0},
    '60/40 US/Intl': {'VTI': 0.6, 'VXUS': 0.4},
    '100% Intl (VXUS)': {'VTI': 0.0, 'VXUS': 1.0}
}

# Calculate cumulative growth
growth_df = pd.DataFrame({
    name: (1 + returns_net['VTI'] * w['VTI'] + returns_net['VXUS'] * w['VXUS']).cumprod()
    for name, w in allocations.items()
})

# Print summary
print('Growth of $1 (Net of Expense Ratios, 2011-2024)')
print('=' * 50)
for col in growth_df.columns:
    final = growth_df[col].iloc[-1]
    print(f'{col:<20}: ${final:.2f} ({(final-1)*100:+.1f}%)')

# Static plot - clean, minimal, blog-ready
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)

colors = {'100% US (VTI)': '#2563eb', '60/40 US/Intl': '#7c3aed', '100% Intl (VXUS)': '#059669'}

for col in growth_df.columns:
    style = {'linewidth': 2.2, 'linestyle': '--'} if '60/40' in col else {'linewidth': 1.8, 'linestyle': '-'}
    ax.plot(growth_df.index, growth_df[col], label=col, color=colors[col], **style)
    ax.annotate(f'${growth_df[col].iloc[-1]:.2f}', xy=(growth_df.index[-1], growth_df[col].iloc[-1]),
                xytext=(8, 0), textcoords='offset points', fontsize=9, color=colors[col], fontweight='medium')

ax.set_title('Growth of $1: US vs International Equity Mix\\n(2011–2024, Net of Expense Ratios)', 
             fontsize=13, fontweight='bold', pad=12)
ax.set_ylabel('Portfolio Value ($)', fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=10, edgecolor='none')
ax.spines[['top', 'right']].set_visible(False)
ax.grid(True, alpha=0.3, linewidth=0.5)
plt.tight_layout()
plt.show()
'''

# Find and fix the corrupted cell (should be around index 5-7 based on structure)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        # Check if this is the corrupted cell (contains plotlyServerURL in source)
        if 'plotlyServerURL' in source or (cell.get('execution_count') == 3 and 'VTI' in source[:200] if source else False):
            print(f"Found corrupted cell at index {i}")
            # Fix it
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]] + [new_source.split('\n')[-1]]
            cell['outputs'] = []
            cell['execution_count'] = None
            print("Fixed!")
            break
        # Also check for the cell that should have VTI/VXUS comparison
        if 'execution_count' in cell and cell['execution_count'] is None:
            source_preview = source[:100] if source else ''
            if 'config' in source_preview or 'plotly' in source_preview.lower():
                print(f"Found corrupted cell at index {i} (null execution)")
                cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]] + [new_source.split('\n')[-1]]
                cell['outputs'] = []
                print("Fixed!")
                break

# Write back
with open('blog/international-equity-factor-tilts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook saved!")
