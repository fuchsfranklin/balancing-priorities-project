"""
VTI/VXUS Mix Comparison - Blog-Ready Static Plot
Compares 100% US, 60/40, and 100% International allocations
Accounts for expense ratios, clean matplotlib styling
"""
import pandas as pd
import numpy as np
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

# Portfolio allocations with blended expense ratios
allocations = {
    '100% US (VTI)': {'VTI': 1.0, 'VXUS': 0.0, 'expense': 0.0003},
    '60/40 US/Intl': {'VTI': 0.6, 'VXUS': 0.4, 'expense': 0.6*0.0003 + 0.4*0.0007},
    '100% Intl (VXUS)': {'VTI': 0.0, 'VXUS': 1.0, 'expense': 0.0007}
}

# Calculate portfolio returns and cumulative growth
portfolio_returns = {}
growth_df = pd.DataFrame()
for name, w in allocations.items():
    port_ret = returns_net['VTI'] * w['VTI'] + returns_net['VXUS'] * w['VXUS']
    portfolio_returns[name] = port_ret
    growth_df[name] = (1 + port_ret).cumprod()

# Calculate metrics
years = len(returns_net) / 252

print('Expense Ratios')
print('=' * 56)
print(f"VTI: {EXPENSE_RATIOS['VTI']*100:.2f}%   VXUS: {EXPENSE_RATIOS['VXUS']*100:.2f}%")
print()
print('Growth of $1 (Net of Expense Ratios, 2011-2024)')
print('=' * 56)
print(f"{'Strategy':<20} {'Final':>8} {'Total':>10} {'CAGR':>8} {'Vol':>7}")
print('-' * 56)
for col in growth_df.columns:
    final = growth_df[col].iloc[-1]
    total_ret = (final - 1) * 100
    cagr = (final ** (1/years) - 1) * 100
    vol = portfolio_returns[col].std() * np.sqrt(252) * 100
    print(f'{col:<20} ${final:>6.2f} {total_ret:>+9.1f}% {cagr:>7.1f}% {vol:>6.1f}%')
print('-' * 56)

# ============================================================
# STATIC PLOT - FiveThirtyEight-inspired, clean, minimal
# ============================================================
plt.rcParams['font.family'] = ['Helvetica Neue', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.5

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)

# Cohesive muted palette
colors = {
    '100% US (VTI)': '#4a7c9b',      # Slate blue - stable baseline
    '60/40 US/Intl': '#8b7ea8',      # Muted purple - blend
    '100% Intl (VXUS)': '#7d8491'    # Warm gray - secondary
}
styles = {
    '100% US (VTI)': {'linewidth': 2.0, 'linestyle': '-'},
    '60/40 US/Intl': {'linewidth': 2.2, 'linestyle': ':'},
    '100% Intl (VXUS)': {'linewidth': 2.0, 'linestyle': '-'}
}

for col in growth_df.columns:
    ax.plot(growth_df.index, growth_df[col], label=col, 
            color=colors[col], **styles[col])

# End-point annotations with slight vertical offset to avoid overlap
offsets = {'100% US (VTI)': 0, '60/40 US/Intl': 0, '100% Intl (VXUS)': 0}
for col in growth_df.columns:
    final_val = growth_df[col].iloc[-1]
    ax.annotate(f'${final_val:.2f}', 
                xy=(growth_df.index[-1], final_val),
                xytext=(8, offsets[col]), textcoords='offset points',
                fontsize=9, color=colors[col], fontweight='semibold')

ax.set_title('Growth of $1: US vs International Equity Mix', 
             fontsize=14, fontweight='bold', pad=20, loc='left')
ax.text(0, 1.01, '2011–2024, Net of Expense Ratios', transform=ax.transAxes,
        fontsize=10, color='#666666', style='italic')

ax.set_ylabel('Portfolio Value', fontsize=11, fontweight='medium')
ax.set_xlabel('')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Legend - bottom right, subtle
ax.legend(loc='upper left', frameon=False, fontsize=9)

# Clean spines
ax.spines[['top', 'right']].set_visible(False)
ax.spines[['left', 'bottom']].set_color('#cccccc')
ax.spines[['left', 'bottom']].set_linewidth(0.8)
ax.tick_params(colors='#666666', labelsize=9)
ax.grid(True, axis='y', alpha=1.0)

plt.tight_layout()
plt.savefig('vti_vxus_mix_growth.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print(f"\nPlot saved as 'vti_vxus_mix_growth.png'")
