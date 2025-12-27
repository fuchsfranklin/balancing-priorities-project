"""
Fama-French 5-Factor Regression Analysis for ETF Factor Exposures
Compares VTI, DFUS, VXUS, and DFAX to quantify their factor loadings
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 1. LOAD AND CLEAN FACTOR DATA
# =============================================================================

def load_ff_factors(filepath):
    """Load Fama-French factor data, handling their specific format."""
    # Read file and find the header row (starts with ,Mkt-RF)
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(',Mkt-RF'):
            header_idx = i
            break
    
    if header_idx is None:
        raise ValueError(f"Could not find header row in {filepath}")
    
    # Read CSV starting from header
    df = pd.read_csv(filepath, skiprows=header_idx)
    
    # First column is the date (YYYYMM format)
    df.columns = ['Date'] + list(df.columns[1:])
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean date column - remove whitespace and convert to string
    df['Date'] = df['Date'].astype(str).str.strip()
    
    # Remove any rows that aren't monthly data (annual summaries, blank rows, etc.)
    df = df[df['Date'].str.match(r'^\d{6}$', na=False)]
    
    # Convert date to datetime (YYYYMM -> last day of month)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m') + pd.offsets.MonthEnd(0)
    df = df.set_index('Date')
    
    # Convert all columns to numeric (strip whitespace first)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
    
    # Drop rows with missing data (-99.99 becomes NaN after coerce)
    df = df.replace(-99.99, np.nan)
    
    # Factor returns are in percentages, convert to decimals
    df = df / 100
    
    return df

print("Loading Fama-French factor data...")

# US Factors
ff_us = load_ff_factors('data/F-F_Research_Data_5_Factors_2x3.csv')
print(f"US Factors: {ff_us.index.min().strftime('%Y-%m')} to {ff_us.index.max().strftime('%Y-%m')}")

# Developed ex-US Factors
ff_dev = load_ff_factors('data/Developed_ex_US_5_Factors.csv')
print(f"Developed ex-US Factors: {ff_dev.index.min().strftime('%Y-%m')} to {ff_dev.index.max().strftime('%Y-%m')}")

# Emerging Markets Factors
ff_em = load_ff_factors('data/Emerging_5_Factors.csv')
print(f"Emerging Factors: {ff_em.index.min().strftime('%Y-%m')} to {ff_em.index.max().strftime('%Y-%m')}")

# =============================================================================
# 2. CREATE WEIGHTED COMPOSITE INTERNATIONAL FACTORS
# =============================================================================

# VXUS allocation: ~77% Developed, ~23% Emerging (approximate market-cap weights)
DEV_WEIGHT = 0.77
EM_WEIGHT = 0.23

print(f"\nCreating composite international factors ({DEV_WEIGHT:.0%} Dev / {EM_WEIGHT:.0%} EM)...")

# Align dates between developed and emerging
common_dates = ff_dev.index.intersection(ff_em.index)
ff_dev_aligned = ff_dev.loc[common_dates]
ff_em_aligned = ff_em.loc[common_dates]

# Create weighted composite
ff_intl = pd.DataFrame(index=common_dates)
for col in ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']:
    ff_intl[col] = DEV_WEIGHT * ff_dev_aligned[col] + EM_WEIGHT * ff_em_aligned[col]

# Use US RF (same globally)
ff_intl['RF'] = ff_us.loc[common_dates, 'RF']

print(f"International Composite: {ff_intl.index.min().strftime('%Y-%m')} to {ff_intl.index.max().strftime('%Y-%m')}")

# =============================================================================
# 3. LOAD ETF PRICES AND CONVERT TO MONTHLY RETURNS
# =============================================================================

print("\nLoading ETF price data...")

prices = pd.read_csv('data/prices_data.csv', index_col=0, parse_dates=True)
etfs = ['VTI', 'DFUS', 'VXUS', 'DFAX']

# Check available ETFs
available_etfs = [e for e in etfs if e in prices.columns]
print(f"Available ETFs: {available_etfs}")

# Remove timezone info if present (factor data is timezone-naive)
if prices.index.tz is not None:
    prices.index = prices.index.tz_localize(None)

# Convert daily prices to monthly returns (end-of-month)
monthly_prices = prices[available_etfs].resample('ME').last()
monthly_returns = monthly_prices.pct_change().dropna()

print(f"ETF Monthly Returns: {monthly_returns.index.min().strftime('%Y-%m')} to {monthly_returns.index.max().strftime('%Y-%m')}")

# =============================================================================
# 4. RUN 5-FACTOR REGRESSIONS
# =============================================================================

def run_factor_regression(etf_returns, factor_data, etf_name):
    """
    Run Fama-French 5-factor regression for an ETF.
    
    Model: R_etf - RF = alpha + b1*(Mkt-RF) + b2*SMB + b3*HML + b4*RMW + b5*CMA + epsilon
    """
    # Align dates
    common_idx = etf_returns.index.intersection(factor_data.index)
    
    if len(common_idx) < 12:
        print(f"  Warning: Only {len(common_idx)} months of data for {etf_name}")
        return None
    
    # Get aligned data
    y = etf_returns.loc[common_idx]
    factors = factor_data.loc[common_idx]
    
    # Calculate excess returns (ETF return - Risk-free rate)
    excess_returns = y - factors['RF']
    
    # Prepare X variables (the 5 factors)
    X = factors[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']]
    X = sm.add_constant(X)  # Add intercept (alpha)
    
    # Run OLS regression
    model = sm.OLS(excess_returns, X).fit()
    
    return {
        'etf': etf_name,
        'alpha': model.params['const'],
        'alpha_tstat': model.tvalues['const'],
        'Mkt-RF': model.params['Mkt-RF'],
        'Mkt-RF_tstat': model.tvalues['Mkt-RF'],
        'SMB': model.params['SMB'],
        'SMB_tstat': model.tvalues['SMB'],
        'HML': model.params['HML'],
        'HML_tstat': model.tvalues['HML'],
        'RMW': model.params['RMW'],
        'RMW_tstat': model.tvalues['RMW'],
        'CMA': model.params['CMA'],
        'CMA_tstat': model.tvalues['CMA'],
        'R2': model.rsquared,
        'R2_adj': model.rsquared_adj,
        'n_obs': len(common_idx),
        'start_date': common_idx.min(),
        'end_date': common_idx.max(),
        'model': model
    }

print("\nRunning 5-Factor Regressions...")
print("=" * 60)

results = []

# US ETFs use US factors
for etf in ['VTI', 'DFUS']:
    if etf in monthly_returns.columns:
        print(f"\n{etf} (using US factors):")
        result = run_factor_regression(monthly_returns[etf], ff_us, etf)
        if result:
            results.append(result)
            print(f"  Period: {result['start_date'].strftime('%Y-%m')} to {result['end_date'].strftime('%Y-%m')} ({result['n_obs']} months)")
            print(f"  R²: {result['R2']:.3f}")

# International ETFs use composite international factors
for etf in ['VXUS', 'DFAX']:
    if etf in monthly_returns.columns:
        print(f"\n{etf} (using International composite factors):")
        result = run_factor_regression(monthly_returns[etf], ff_intl, etf)
        if result:
            results.append(result)
            print(f"  Period: {result['start_date'].strftime('%Y-%m')} to {result['end_date'].strftime('%Y-%m')} ({result['n_obs']} months)")
            print(f"  R²: {result['R2']:.3f}")

# =============================================================================
# 5. CREATE RESULTS TABLE
# =============================================================================

print("\n" + "=" * 80)
print("FAMA-FRENCH 5-FACTOR REGRESSION RESULTS")
print("=" * 80)

# Create summary DataFrame
summary_data = []
for r in results:
    summary_data.append({
        'ETF': r['etf'],
        'Alpha (ann.)': r['alpha'] * 12,  # Annualize monthly alpha
        'Alpha t-stat': r['alpha_tstat'],
        'Mkt-RF (β)': r['Mkt-RF'],
        'SMB': r['SMB'],
        'HML': r['HML'],
        'RMW': r['RMW'],
        'CMA': r['CMA'],
        'R²': r['R2'],
        'N': r['n_obs']
    })

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.set_index('ETF')

# Print formatted table
print("\nFactor Loadings (coefficients):")
print("-" * 80)
print(f"{'ETF':<8} {'Alpha%':>8} {'t-stat':>7} {'Mkt-RF':>7} {'SMB':>7} {'HML':>7} {'RMW':>7} {'CMA':>7} {'R²':>6}")
print("-" * 80)

for idx, row in summary_df.iterrows():
    alpha_pct = row['Alpha (ann.)'] * 100
    print(f"{idx:<8} {alpha_pct:>7.2f}% {row['Alpha t-stat']:>7.2f} {row['Mkt-RF (β)']:>7.3f} "
          f"{row['SMB']:>7.3f} {row['HML']:>7.3f} {row['RMW']:>7.3f} {row['CMA']:>7.3f} {row['R²']:>6.3f}")

print("-" * 80)
print("Note: Alpha is annualized. |t-stat| > 2 indicates statistical significance at 5% level.")

# =============================================================================
# 6. INTERPRETATION
# =============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

# Compare VTI vs DFUS
if 'VTI' in summary_df.index and 'DFUS' in summary_df.index:
    vti = summary_df.loc['VTI']
    dfus = summary_df.loc['DFUS']
    
    print("\n📊 US COMPARISON: VTI vs DFUS")
    print("-" * 40)
    print(f"Market Beta:  VTI={vti['Mkt-RF (β)']:.3f}, DFUS={dfus['Mkt-RF (β)']:.3f}")
    print(f"Size (SMB):   VTI={vti['SMB']:.3f}, DFUS={dfus['SMB']:.3f}")
    print(f"Value (HML):  VTI={vti['HML']:.3f}, DFUS={dfus['HML']:.3f}")
    
    # Check if factor loadings are similar
    smb_diff = abs(dfus['SMB'] - vti['SMB'])
    hml_diff = abs(dfus['HML'] - vti['HML'])
    
    if smb_diff < 0.1 and hml_diff < 0.1:
        print("\n✅ DFUS has similar factor exposure to VTI (both are pure market beta)")
        print("   The outperformance comes from implementation, not factor tilts.")
    else:
        print("\n⚠️  DFUS shows different factor exposure than VTI")

# Compare VXUS vs DFAX
if 'VXUS' in summary_df.index and 'DFAX' in summary_df.index:
    vxus = summary_df.loc['VXUS']
    dfax = summary_df.loc['DFAX']
    
    print("\n📊 INTERNATIONAL COMPARISON: VXUS vs DFAX")
    print("-" * 40)
    print(f"Market Beta:  VXUS={vxus['Mkt-RF (β)']:.3f}, DFAX={dfax['Mkt-RF (β)']:.3f}")
    print(f"Size (SMB):   VXUS={vxus['SMB']:.3f}, DFAX={dfax['SMB']:.3f}")
    print(f"Value (HML):  VXUS={vxus['HML']:.3f}, DFAX={dfax['HML']:.3f}")
    print(f"Profit (RMW): VXUS={vxus['RMW']:.3f}, DFAX={dfax['RMW']:.3f}")
    
    # Check for factor tilts
    smb_tilt = dfax['SMB'] - vxus['SMB']
    hml_tilt = dfax['HML'] - vxus['HML']
    
    if abs(smb_tilt) > 0.1 or abs(hml_tilt) > 0.1:
        print(f"\n⚠️  DFAX shows factor tilts relative to VXUS:")
        if smb_tilt > 0.1:
            print(f"   • Size tilt (SMB): +{smb_tilt:.3f} (tilts toward smaller stocks)")
        if hml_tilt > 0.1:
            print(f"   • Value tilt (HML): +{hml_tilt:.3f} (tilts toward value stocks)")
        print("\n   DFAX is NOT a pure VXUS replacement — it's a factor-tilted fund.")
    else:
        print("\n✅ DFAX has similar factor exposure to VXUS")

# =============================================================================
# 7. CREATE VISUALIZATION
# =============================================================================

print("\nCreating visualization...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

factors = ['Mkt-RF (β)', 'SMB', 'HML', 'RMW', 'CMA']
x = np.arange(len(factors))
width = 0.35

# US Comparison (VTI vs DFUS)
ax1 = axes[0]
if 'VTI' in summary_df.index and 'DFUS' in summary_df.index:
    vti_vals = [summary_df.loc['VTI', f] for f in factors]
    dfus_vals = [summary_df.loc['DFUS', f] for f in factors]
    
    bars1 = ax1.bar(x - width/2, vti_vals, width, label='VTI', color='#1f77b4', alpha=0.8)
    bars2 = ax1.bar(x + width/2, dfus_vals, width, label='DFUS', color='#2ca02c', alpha=0.8)
    
    ax1.set_ylabel('Factor Loading')
    ax1.set_title('US ETFs: VTI vs DFUS\n(Similar loadings = same exposure)', fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Market\nBeta', 'Size\n(SMB)', 'Value\n(HML)', 'Profit\n(RMW)', 'Invest\n(CMA)'])
    ax1.legend()
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.axhline(y=1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_ylim(-0.3, 1.3)

# International Comparison (VXUS vs DFAX)
ax2 = axes[1]
if 'VXUS' in summary_df.index and 'DFAX' in summary_df.index:
    vxus_vals = [summary_df.loc['VXUS', f] for f in factors]
    dfax_vals = [summary_df.loc['DFAX', f] for f in factors]
    
    bars3 = ax2.bar(x - width/2, vxus_vals, width, label='VXUS', color='#1f77b4', alpha=0.8)
    bars4 = ax2.bar(x + width/2, dfax_vals, width, label='DFAX', color='#d62728', alpha=0.8)
    
    ax2.set_ylabel('Factor Loading')
    ax2.set_title('International ETFs: VXUS vs DFAX\n(Different loadings = different exposure)', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Market\nBeta', 'Size\n(SMB)', 'Value\n(HML)', 'Profit\n(RMW)', 'Invest\n(CMA)'])
    ax2.legend()
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_ylim(-0.3, 1.3)

plt.suptitle('Fama-French 5-Factor Exposures: Index vs DFA ETFs', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('blog/factor_loadings_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("✅ Saved: blog/factor_loadings_comparison.png")

# =============================================================================
# 8. SAVE RESULTS TO CSV
# =============================================================================

summary_df.to_csv('blog/factor_regression_results.csv')
print("✅ Saved: blog/factor_regression_results.csv")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
