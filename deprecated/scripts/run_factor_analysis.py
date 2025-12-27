#!/usr/bin/env python3
"""
Factor-Based Portfolio Analysis
Addresses: diversification, factor premiums, Bogleheads principles
"""

import pandas as pd
import numpy as np
from pathlib import Path

ASSETS = {
    'VTI': 'US Total Market',
    'VOO': 'S&P 500 (Large Cap)',
    'VBR': 'Small Cap Value',
    'VTV': 'Large Cap Value',
    'MTUM': 'Momentum',
    'VXUS': 'International',
    'BND': 'US Bonds'
}

EXPENSE_RATIOS = {
    'VTI': 0.0003, 'VOO': 0.0003, 'VBR': 0.0007, 
    'VTV': 0.0004, 'MTUM': 0.0015, 'VXUS': 0.0007, 'BND': 0.0003
}

def load_data():
    """Load factor-based returns"""
    returns = pd.read_csv('data/factor_returns.csv', index_col=0, parse_dates=True)
    return returns

def portfolio_metrics(weights, returns):
    """Calculate portfolio metrics"""
    port_return = np.sum(returns.mean() * weights) * 252
    port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = port_return / port_vol if port_vol > 0 else 0
    
    # Calculate cost
    cost = sum(w * EXPENSE_RATIOS[asset] for w, asset in zip(weights, returns.columns))
    
    # Calculate diversification ratio
    weighted_vol = np.sum(returns.std() * np.sqrt(252) * weights)
    diversification = weighted_vol / port_vol if port_vol > 0 else 1.0
    
    return port_return, port_vol, sharpe, cost, diversification

def analyze_strategies(returns):
    """Compare different investment strategies"""
    
    strategies = {
        'Bogleheads 3-Fund': {
            'VTI': 0.54, 'VXUS': 0.36, 'BND': 0.10,
            'VOO': 0, 'VBR': 0, 'VTV': 0, 'MTUM': 0
        },
        'Traditional 60/40': {
            'VTI': 0.42, 'VXUS': 0.18, 'BND': 0.40,
            'VOO': 0, 'VBR': 0, 'VTV': 0, 'MTUM': 0
        },
        'Factor Tilt (Value)': {
            'VTI': 0.30, 'VTV': 0.20, 'VBR': 0.10, 'VXUS': 0.30, 'BND': 0.10,
            'VOO': 0, 'MTUM': 0
        },
        'Factor Tilt (Momentum)': {
            'VTI': 0.30, 'MTUM': 0.20, 'VXUS': 0.30, 'BND': 0.20,
            'VOO': 0, 'VBR': 0, 'VTV': 0
        },
        'Concentrated US': {
            'VOO': 0.60, 'VTI': 0.30, 'BND': 0.10,
            'VBR': 0, 'VTV': 0, 'MTUM': 0, 'VXUS': 0
        }
    }
    
    results = []
    for name, allocation in strategies.items():
        weights = np.array([allocation[asset] for asset in returns.columns])
        ret, vol, sharpe, cost, div_ratio = portfolio_metrics(weights, returns)
        
        results.append({
            'Strategy': name,
            'Return': ret,
            'Risk': vol,
            'Sharpe': sharpe,
            'Cost': cost,
            'Diversification': div_ratio,
            **{f'{asset}_weight': allocation[asset] for asset in returns.columns}
        })
    
    return pd.DataFrame(results)

def optimize_with_constraints(returns, n_portfolios=1000):
    """Optimize with diversification constraints"""
    results = []
    n_assets = len(returns.columns)
    
    for _ in range(n_portfolios):
        # Generate weights with minimum diversification
        weights = np.random.dirichlet(np.ones(n_assets) * 2)  # Encourages diversification
        
        # Enforce minimum international (Bogleheads principle)
        if weights[5] < 0.20:  # VXUS
            weights[5] = 0.20 + np.random.random() * 0.10
            weights = weights / weights.sum()
        
        # Enforce minimum bonds
        if weights[6] < 0.10:  # BND
            weights[6] = 0.10 + np.random.random() * 0.10
            weights = weights / weights.sum()
        
        ret, vol, sharpe, cost, div_ratio = portfolio_metrics(weights, returns)
        
        results.append({
            'return': ret,
            'risk': vol,
            'sharpe': sharpe,
            'cost': cost,
            'diversification': div_ratio,
            **{f'{asset}_weight': w for asset, w in zip(returns.columns, weights)}
        })
    
    df = pd.DataFrame(results)
    pareto = df.nlargest(50, 'sharpe')
    
    return df, pareto

def main():
    print("\n" + "="*70)
    print("FACTOR-BASED PORTFOLIO ANALYSIS")
    print("="*70)
    
    returns = load_data()
    
    # Analyze predefined strategies
    print("\n[1/2] Analyzing Investment Strategies...")
    strategies = analyze_strategies(returns)
    
    print("\nStrategy Comparison:")
    print("-" * 70)
    for _, row in strategies.iterrows():
        print(f"\n{row['Strategy']:25s}")
        print(f"  Return: {row['Return']:6.1%}  Risk: {row['Risk']:6.1%}  "
              f"Sharpe: {row['Sharpe']:.3f}  Div: {row['Diversification']:.2f}")
        
        # Show allocation
        alloc = []
        for asset in ASSETS.keys():
            w = row[f'{asset}_weight']
            if w > 0.01:
                alloc.append(f"{asset}:{w:.0%}")
        print(f"  Allocation: {', '.join(alloc)}")
    
    # Optimize with constraints
    print("\n[2/2] Optimizing with Diversification Constraints...")
    all_portfolios, pareto = optimize_with_constraints(returns)
    
    best = pareto.iloc[0]
    bogleheads = strategies[strategies['Strategy'] == 'Bogleheads 3-Fund'].iloc[0]
    
    print(f"\nBest Constrained Portfolio:")
    print(f"  Return: {best['return']:6.1%}  Risk: {best['risk']:6.1%}  "
          f"Sharpe: {best['sharpe']:.3f}")
    print(f"  Diversification Ratio: {best['diversification']:.2f}")
    print(f"  Allocation:")
    for asset in ASSETS.keys():
        w = best[f'{asset}_weight']
        if w > 0.01:
            print(f"    {asset:6s} ({ASSETS[asset]:20s}): {w:5.1%}")
    
    improvement = (best['sharpe'] - bogleheads['Sharpe']) / bogleheads['Sharpe'] * 100
    print(f"\nImprovement over Bogleheads 3-Fund: {improvement:+.1f}%")
    
    # Save results
    Path('results').mkdir(exist_ok=True)
    strategies.to_csv('results/strategy_comparison.csv', index=False)
    pareto.to_csv('results/factor_optimal_portfolios.csv', index=False)
    
    print(f"\nSaved results:")
    print(f"  Strategy comparison: results/strategy_comparison.csv")
    print(f"  Optimal portfolios: results/factor_optimal_portfolios.csv")
    
    # Key insights
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("\n1. DIVERSIFICATION MATTERS")
    print(f"   Bogleheads 3-Fund diversification: {bogleheads['Diversification']:.2f}")
    print(f"   Concentrated US diversification: {strategies[strategies['Strategy']=='Concentrated US'].iloc[0]['Diversification']:.2f}")
    print(f"   Higher ratio = better diversification")
    
    print("\n2. FACTOR PREMIUMS")
    print(f"   Value tilt Sharpe: {strategies[strategies['Strategy']=='Factor Tilt (Value)'].iloc[0]['Sharpe']:.3f}")
    print(f"   Momentum tilt Sharpe: {strategies[strategies['Strategy']=='Factor Tilt (Momentum)'].iloc[0]['Sharpe']:.3f}")
    print(f"   Plain market Sharpe: {bogleheads['Sharpe']:.3f}")
    
    print("\n3. INTERNATIONAL EXPOSURE")
    print(f"   Bogleheads (36% intl): {bogleheads['Sharpe']:.3f} Sharpe")
    print(f"   Concentrated US (0% intl): {strategies[strategies['Strategy']=='Concentrated US'].iloc[0]['Sharpe']:.3f} Sharpe")
    print(f"   Difference reflects 2015-2024 US outperformance")
    
    print("\n" + "="*70)
    print("CONCLUSION: Factor investing and diversification both matter.")
    print("Bogleheads principles remain sound for long-term investors.")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
