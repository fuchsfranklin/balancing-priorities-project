import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import time

# Load API key
load_dotenv()
TIINGO_API_KEY = os.getenv('TIINGO_API_KEY')

# Get historical prices for VTI and VXUS
symbols = ['VTI', 'VXUS']
prices = pd.DataFrame()

for symbol in symbols:
    url = f'https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate=2013-01-01&endDate=2023-12-31&token={TIINGO_API_KEY}'
    df = pd.read_json(url)
    df['symbol'] = symbol
    prices = pd.concat([prices, df])
    time.sleep(1.2)  # Rate limiting

# Pivot and calculate returns
prices['date'] = pd.to_datetime(prices['date'])
prices_wide = prices.pivot(index='date', columns='symbol', values='adjClose')
returns = prices_wide.pct_change().dropna()

# Define allocations
allocations = {
    '100% US (VTI)': {'VTI': 1.0, 'VXUS': 0.0},
    '60% US / 40% Intl': {'VTI': 0.6, 'VXUS': 0.4},
    '100% Intl (VXUS)': {'VTI': 0.0, 'VXUS': 1.0}
}

# Calculate growth
growth_data = {}
for name, weights in allocations.items():
    portfolio_returns = (returns['VTI'] * weights['VTI'] + 
                        returns['VXUS'] * weights['VXUS'])
    growth_data[name] = (1 + portfolio_returns).cumprod()

growth_df = pd.DataFrame(growth_data)

# Plot
plt.figure(figsize=(10, 6))
for col in growth_df.columns:
    linestyle = '--' if '60%' in col else '-'
    linewidth = 2.5 if '60%' in col else 1.5
    plt.plot(growth_df.index, growth_df[col], label=col, 
            linestyle=linestyle, linewidth=linewidth)

plt.title('Growth of $1: US vs International Mix', fontsize=14, fontweight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Portfolio Value ($)', fontsize=12)
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('vti_vxus_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nFinal Values:")
for col in growth_df.columns:
    print(f"{col}: ${growth_df[col].iloc[-1]:.2f}")
