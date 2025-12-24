"""
VTI vs DFUS Comparison - Blog-Ready Static Plot
Accounts for expense ratios, clean matplotlib styling
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load data
df = pd.read_csv('../data/prices_data.csv', index_col=0, parse_dates=True)

# Filter to DFUS inception date
start_date = df['DFUS'].first_valid_index()
vti = df.loc[start_date:, 'VTI']
dfus = df.loc[start_date:, 'DFUS']

# Calculate daily returns
vti_returns = vti.pct_change().dropna()
dfus_returns = dfus.pct_change().dropna()

# Expense ratios (annual) - deducted daily
EXPENSE_RATIOS = {'VTI': 0.0003, 'DFUS': 0.0009}  # 0.03% and 0.09%
daily_cost = {k: v / 252 for k, v in EXPENSE_RATIOS.items()}

# Net returns after fees
vti_net = vti_returns - daily_cost['VTI']
dfus_net = dfus_returns - daily_cost['DFUS']

# Calculate cumulative growth (starting at $1)
vti_growth = (1 + vti_net).cumprod()
dfus_growth = (1 + dfus_net).cumprod()

# Align index (first day = 1.0)
vti_growth = pd.concat([pd.Series([1.0], index=[start_date]), vti_growth])
dfus_growth = pd.concat([pd.Series([1.0], index=[start_date]), dfus_growth])

# Calculate metrics
years = len(vti_net) / 252
vti_final = vti_growth.iloc[-1]
dfus_final = dfus_growth.iloc[-1]
vti_cagr = (vti_final ** (1/years) - 1) * 100
dfus_cagr = (dfus_final ** (1/years) - 1) * 100
vti_vol = vti_net.std() * np.sqrt(252) * 100
dfus_vol = dfus_net.std() * np.sqrt(252) * 100

print(f'Performance since DFUS inception ({start_date.date()}):')
print('=' * 56)
print(f"Expense Ratios: VTI {EXPENSE_RATIOS['VTI']*100:.2f}%, DFUS {EXPENSE_RATIOS['DFUS']*100:.2f}%")
print()
print(f"{'Fund':<8} {'Final':>8} {'Total':>10} {'CAGR':>8} {'Vol':>7}")
print('-' * 56)
print(f"{'VTI':<8} ${vti_final:>6.2f} {(vti_final-1)*100:>+9.1f}% {vti_cagr:>7.1f}% {vti_vol:>6.1f}%")
print(f"{'DFUS':<8} ${dfus_final:>6.2f} {(dfus_final-1)*100:>+9.1f}% {dfus_cagr:>7.1f}% {dfus_vol:>6.1f}%")
print('-' * 56)
print(f"DFUS Outperformance: {(dfus_final-vti_final)*100:+.1f}% total, {dfus_cagr-vti_cagr:+.1f}% CAGR")

# ============================================================
# STATIC PLOT - FiveThirtyEight-inspired, clean, minimal
# ============================================================
plt.rcParams['font.family'] = ['Helvetica Neue', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.5

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)

# Cohesive muted palette - VTI slate blue, DFUS teal (upgrade)
colors = {'VTI': '#4a7c9b', 'DFUS': '#2d9596'}

# Plot - index solid, factor dashed+thicker
ax.plot(vti_growth.index, vti_growth, label='VTI (Total US Market)', 
        color=colors['VTI'], linewidth=2.0, linestyle='-')
ax.plot(dfus_growth.index, dfus_growth, label='DFUS (DFA US Equity)', 
        color=colors['DFUS'], linewidth=2.4, linestyle='--')

# End-point annotations
for series, color, offset in [(vti_growth, colors['VTI'], -8), 
                               (dfus_growth, colors['DFUS'], 8)]:
    final_val = series.iloc[-1]
    ret = (final_val - 1) * 100
    ax.annotate(f'${final_val:.2f} ({ret:+.1f}%)', 
                xy=(series.index[-1], final_val),
                xytext=(8, offset), textcoords='offset points',
                fontsize=9, color=color, fontweight='semibold')

# Title - left-aligned, subtitle below
ax.set_title('VTI vs DFUS: Growth of $1 Since DFUS Inception', 
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
plt.savefig('vti_dfus_growth.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print(f"\nPlot saved as 'vti_dfus_growth.png'")
