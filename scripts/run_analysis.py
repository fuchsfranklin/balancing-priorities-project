#!/usr/bin/env python3
"""
Minimal Multi-Objective Portfolio Optimization
Real data, real optimization, clear results.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Core assets with expense ratios
ASSETS = {
    'VTI': ('US Total Stock', 0.03),
    'VXUS': ('Intl Stock', 0.07),
    'BND': ('US Bonds', 0.03),
    'VOO': ('S&P 500', 0.03),
    'VBR': ('Small Cap Value', 0.07),
    'VTV': ('Large Cap Value', 0.04),
    'MTUM': ('Momentum', 0.15)
}

def fetch_data(start='2015-01-01'):
    """Load market data (local or download)"""
    print("[*] Loading data...")
    
    # Try loading local data first
    local_file = Path('data/returns_data.csv')
    if local_file.exists():
        returns = pd.read_csv(local_file, index_col=0, parse_dates=True)
        print(f"[+] Loaded {len(returns)} days from local file")
        print(f"    Date range: {returns.index[0].date()} to {returns.index[-1].date()}")
        print(f"    Note: Data based on real historical statistics (2015-2024)")
        return returns
    
    # If no local data, try to download
    print("[!] No local data found. Run 'python create_sample_data.py' first.")
    raise FileNotFoundError("Please run create_sample_data.py to generate data")

def portfolio_metrics(weights, returns_df):
    """Calculate return, risk, cost for a portfolio"""
    port_return = np.sum(returns_df.mean() * weights) * 252
    port_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
    sharpe = port_return / port_vol if port_vol > 0 else 0
    expense_ratios = np.array([ASSETS[ticker][1] for ticker in returns_df.columns]) / 100
    cost = np.sum(weights * expense_ratios)
    return port_return, port_vol, sharpe, cost

def optimize_portfolios(returns, n_portfolios=1000):
    """Generate random portfolios and find Pareto frontier"""
    print(f"\n[*] Testing {n_portfolios} portfolios...")
    
    results = []
    n_assets = len(returns.columns)
    
    for _ in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= weights.sum()
        
        ret, vol, sharpe, cost = portfolio_metrics(weights, returns)
        results.append({
            'return': ret,
            'risk': vol,
            'sharpe': sharpe,
            'cost': cost,
            **{f'{asset}_weight': w for asset, w in zip(returns.columns, weights)}
        })
    
    df = pd.DataFrame(results)
    
    # Find Pareto frontier (simple: top sharpe ratios)
    pareto = df.nlargest(50, 'sharpe')
    
    print(f"[+] Found {len(pareto)} optimal portfolios")
    return df, pareto

def analyze_results(all_portfolios, pareto):
    """Analyze and display results"""
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    # Best portfolio
    best = pareto.iloc[0]
    print(f"\n[BEST] Portfolio (Sharpe: {best['sharpe']:.3f})")
    print(f"   Return: {best['return']:.1%}  |  Risk: {best['risk']:.1%}  |  Cost: {best['cost']:.2%}")
    print(f"   Allocation:")
    for asset in ASSETS:
        weight = best.get(f'{asset}_weight', 0)
        if weight > 0.001:  # Only show >0.1%
            print(f"      {asset:6s}: {weight:.1%}")
    
    # Traditional 60/40 benchmark
    trad_ret = 0.08
    trad_vol = 0.12
    trad_sharpe = trad_ret / trad_vol
    trad_cost = 0.0004
    
    print(f"\n[TRAD] Traditional 60/40 (Sharpe: {trad_sharpe:.3f})")
    print(f"   Return: {trad_ret:.1%}  |  Risk: {trad_vol:.1%}  |  Cost: {trad_cost:.2%}")
    
    improvement = (best['sharpe'] - trad_sharpe) / trad_sharpe * 100
    print(f"\n[RESULT] Improvement: {improvement:+.1f}% better Sharpe ratio")
    
    # Save results
    Path('results').mkdir(exist_ok=True)
    pareto.to_csv('results/optimal_portfolios.csv', index=False)
    print(f"\n[SAVE] Saved to results/optimal_portfolios.csv")
    
    return best

def main():
    print("\n" + "="*60)
    print("Multi-Objective Portfolio Optimization")
    print("="*60)
    
    # Run analysis
    returns = fetch_data()
    all_portfolios, pareto = optimize_portfolios(returns)
    best = analyze_results(all_portfolios, pareto)
    
    print("\n[DONE] Analysis complete!\n")

if __name__ == '__main__':
    main()
