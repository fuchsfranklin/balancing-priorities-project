"""
Fama-French 5-Factor Regression: Simplified Blog Version
Shows factor exposures for VTI, DFUS, VXUS, and DFAX
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

# Load factor data (Fama-French 5 Factors from Ken French's Data Library)
# US factors for VTI/DFUS, International composite (77% Dev ex-US + 23% EM) for VXUS/DFAX

def load_factors(filepath):
    """Load and clean Fama-French factor data."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if ',Mkt-RF' in line)
    df = pd.read_csv(filepath, skiprows=header_idx)
    df.columns = ['Date'] + [c.strip() for c in df.columns[1:]]
    df['Date'] = df['Date'].astype(str).str.strip()
    df = df[df['Date'].str.match(r'^\d{6}$', na=False)]
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m') + pd.offsets.MonthEnd(0)
    df = df.set_index('Date')
    for col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
    return df / 100  # Convert percentages to decimals

# Load factors
ff_us = load_factors('data/F-F_Research_Data_5_Factors_2x3.csv')
ff_dev = load_factors('data/Developed_ex_US_5_Factors.csv')
ff_em = load_factors('data/Emerging_5_Factors.csv')

# Create international composite (VXUS is ~77% developed, ~23% emerging)
common_dates = ff_dev.index.intersection(ff_em.index)
ff_intl = pd.DataFrame(index=common_dates)
for col in ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']:
    ff_intl[col] = 0.77 * ff_dev.loc[common_dates, col] + 0.23 * ff_em.loc[common_dates, col]
ff_intl['RF'] = ff_us.loc[common_dates, 'RF']

# Load ETF prices and convert to monthly returns
prices = pd.read_csv('data/prices_data.csv', index_col=0, parse_dates=True)
if prices.index.tz is not None:
    prices.index = prices.index.tz_localize(None)
monthly_returns = prices[['VTI', 'DFUS', 'VXUS', 'DFAX']].resample('ME').last().pct_change().dropna()

# Run 5-factor regression
def run_regression(etf_returns, factors):
    common = etf_returns.index.intersection(factors.index)
    y = etf_returns.loc[common] - factors.loc[common, 'RF']  # Excess returns
    X = sm.add_constant(factors.loc[common, ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']])
    return sm.OLS(y, X).fit()

# Run regressions
results = {
    'VTI': run_regression(monthly_returns['VTI'], ff_us),
    'DFUS': run_regression(monthly_returns['DFUS'], ff_us),
    'VXUS': run_regression(monthly_returns['VXUS'], ff_intl),
    'DFAX': run_regression(monthly_returns['DFAX'], ff_intl),
}

# Print results
print("Fama-French 5-Factor Regression Results (2021-2024)")
print("=" * 70)
print(f"{'ETF':<6} {'Alpha%':>8} {'Mkt-RF':>8} {'SMB':>8} {'HML':>8} {'RMW':>8} {'CMA':>8} {'R²':>6}")
print("-" * 70)
for etf, model in results.items():
    alpha_ann = model.params['const'] * 12 * 100
    print(f"{etf:<6} {alpha_ann:>7.2f}% {model.params['Mkt-RF']:>8.3f} "
          f"{model.params['SMB']:>8.3f} {model.params['HML']:>8.3f} "
          f"{model.params['RMW']:>8.3f} {model.params['CMA']:>8.3f} {model.rsquared:>6.3f}")
