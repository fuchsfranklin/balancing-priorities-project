"""
VXUS vs DFAX Comparison - Blog-Ready Static Plot
Accounts for expense ratios, clean matplotlib styling
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load data
df = pd.read_csv('../data/prices_data.csv', index_col=0, parse_dates=True)

# Filter to DFAX inception date
start_date = df['DFAX'].first_valid_index()
vxus = df.loc[start_date:, 'VXUS']
dfax = df.loc[start_date:, 'DFAX']

# Calculate daily returns
vxus_returns = vxus.pct_change().dropna()
dfax_returns = dfax.pct_change().dropna()

# Expense ratios (annual) - deducted daily
EXPENSE_RATIOS = {'VXUS': 0.0007, 'DFAX': 0.0023}  # 0.07% and 0.23%
daily_cost = {k: v / 252 for k, v in EXPENSE_RATIOS.items()}

# Net returns after fees
vxus_net = vxus_returns - daily_cost['VXUS']
dfax_net = dfax_returns - daily_cost['DFAX']

# Calculate cumulative growth (starting at $1)
vxus_growth = (1 + vxus_net).cumprod()
dfax_growth = (1 + dfax_net).cumprod()

# Align index (first day = 1.0)
vxus_growth = pd.concat([pd.Series([1.0], index=[start_date]), vxus_growth])
dfax_growth = pd.concat([pd.Series([1.0], index=[start_date]), dfax_growth])

# Calculate metrics
years = len(vxus_net) / 252
vxus_final = vxus_growth.iloc[-1]
dfax_final = dfax_growth.iloc[-1]
vxus_cagr = (vxus_final ** (1/years) - 1) * 100
dfax_cagr = (dfax_final ** (1/years) - 1) * 100
vxus_vol = vxus_net.std() * np.sqrt(252) * 100
dfax_vol = dfax_net.std() * np.sqrt(252) * 100

print(f'Performance since DFAX inception ({start_date.date()}):')
print('=' * 56)
print(f"Expense Ratios: VXUS {EXPENSE_RATIOS['VXUS']*100:.2f}%, DFAX {EXPENSE_RATIOS['DFAX']*100:.2f}%")
print()
print(f"{'Fund':<8} {'Final':>8} {'Total':>10} {'CAGR':>8} {'Vol':>7}")
print('-' * 56)
print(f"{'VXUS':<8} ${vxus_final:>6.2f} {(vxus_final-1)*100:>+9.1f}% {vxus_cagr:>7.1f}% {vxus_vol:>6.1f}%")
print(f"{'DFAX':<8} ${dfax_final:>6.2f} {(dfax_final-1)*100:>+9.1f}% {dfax_cagr:>7.1f}% {dfax_vol:>6.1f}%")
print('-' * 56)
print(f"DFAX Outperformance: {(dfax_final-vxus_final)*100:+.1f}% total, {dfax_cagr-vxus_cagr:+.1f}% CAGR")

# ============================================================
# STATIC PLOT - FiveThirtyEight-inspired, clean, minimal
# ============================================================
plt.rcParams['font.family'] = ['Helvetica Neue', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.5

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)

# Cohesive muted palette - VXUS warm gray, DFAX coral/terracotta (upgrade)
colors = {'VXUS': '#7d8491', 'DFAX': '#c75b4a'}

# Plot - index solid, factor dashed+thicker
ax.plot(vxus_growth.index, vxus_growth, label='VXUS (Total Intl Market)', 
        color=colors['VXUS'], linewidth=2.0, linestyle='-')
ax.plot(dfax_growth.index, dfax_growth, label='DFAX (DFA World ex-US)', 
        color=colors['DFAX'], linewidth=2.4, linestyle='--')

# End-point annotations
for series, color, offset in [(vxus_growth, colors['VXUS'], -8), 
                               (dfax_growth, colors['DFAX'], 8)]:
    final_val = series.iloc[-1]
    ret = (final_val - 1) * 100
    ax.annotate(f'${final_val:.2f} ({ret:+.1f}%)', 
                xy=(series.index[-1], final_val),
                xytext=(8, offset), textcoords='offset points',
                fontsize=9, color=color, fontweight='semibold')

# Title - left-aligned, subtitle below
ax.set_title('VXUS vs DFAX: Growth of $1 Since DFAX Inception', 
             fontsize=14, fontweight='bold', pad=20, loc='left')
ax.text(0, 1.01, f'{start_date.strftime("%b %Y")}–Present, Net of Expense Ratios', 
        transform=ax.transAxes, fontsize=10, color='#666666', style='italic')

ax.set_ylabel('Portfolio Value', fontsize=11, fontweight='medium')
ax.set_xlabel('')

# Format axes
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.2f}'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45, ha='right')

# Legend
ax.legend(loc='upper left', frameon=False, fontsize=9)

# Clean spines
ax.spines[['top', 'right']].set_visible(False)
ax.spines[['left', 'bottom']].set_color('#cccccc')
ax.spines[['left', 'bottom']].set_linewidth(0.8)
ax.tick_params(colors='#666666', labelsize=9)
ax.grid(True, axis='y', alpha=1.0)

plt.tight_layout()
plt.savefig('vxus_dfax_growth.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print(f"\nPlot saved as 'vxus_dfax_growth.png'")
