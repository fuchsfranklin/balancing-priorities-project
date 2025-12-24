#!/usr/bin/env python3
"""
Create sample real market data for testing
Based on actual historical ETF performance characteristics
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Real historical statistics (2015-2024)
# Source: Portfolio Visualizer, Morningstar
REAL_STATS = {
    'VTI': {'annual_return': 0.1142, 'annual_vol': 0.1789, 'sharpe': 0.58},
    'VXUS': {'annual_return': 0.0512, 'annual_vol': 0.1654, 'sharpe': 0.21},
    'BND': {'annual_return': 0.0089, 'annual_vol': 0.0589, 'sharpe': -0.05},
    'VOO': {'annual_return': 0.1289, 'annual_vol': 0.1802, 'sharpe': 0.66}
}

# Correlation matrix (approximate real correlations)
CORRELATIONS = pd.DataFrame([
    [1.00, 0.82, -0.05, 0.99],  # VTI
    [0.82, 1.00, 0.15, 0.81],   # VXUS
    [-0.05, 0.15, 1.00, -0.06], # BND
    [0.99, 0.81, -0.06, 1.00]   # VOO
], index=['VTI', 'VXUS', 'BND', 'VOO'], columns=['VTI', 'VXUS', 'BND', 'VOO'])

def generate_correlated_returns(n_days=2500, seed=42):
    """Generate correlated returns matching real statistics"""
    np.random.seed(seed)
    
    # Convert annual to daily
    daily_stats = {}
    for asset, stats in REAL_STATS.items():
        daily_stats[asset] = {
            'mean': stats['annual_return'] / 252,
            'std': stats['annual_vol'] / np.sqrt(252)
        }
    
    # Generate correlated random variables
    L = np.linalg.cholesky(CORRELATIONS.values)
    uncorrelated = np.random.standard_normal((n_days, 4))
    correlated = uncorrelated @ L.T
    
    # Scale to match statistics
    returns = pd.DataFrame(index=pd.date_range('2015-01-01', periods=n_days, freq='D'))
    for i, asset in enumerate(['VTI', 'VXUS', 'BND', 'VOO']):
        returns[asset] = correlated[:, i] * daily_stats[asset]['std'] + daily_stats[asset]['mean']
    
    return returns

def create_price_data(returns):
    """Convert returns to prices starting at $100"""
    prices = (1 + returns).cumprod() * 100
    return prices

def main():
    print("Creating sample data based on real market statistics...")
    print("\nReal Historical Performance (2015-2024):")
    for asset, stats in REAL_STATS.items():
        print(f"  {asset}: {stats['annual_return']:.1%} return, {stats['annual_vol']:.1%} vol, {stats['sharpe']:.2f} Sharpe")
    
    # Generate returns
    returns = generate_correlated_returns()
    
    # Create prices
    prices = create_price_data(returns)
    
    # Verify statistics match
    print("\nGenerated Data Statistics:")
    for asset in ['VTI', 'VXUS', 'BND', 'VOO']:
        annual_ret = returns[asset].mean() * 252
        annual_vol = returns[asset].std() * np.sqrt(252)
        sharpe = annual_ret / annual_vol
        print(f"  {asset}: {annual_ret:.1%} return, {annual_vol:.1%} vol, {sharpe:.2f} Sharpe")
    
    # Save
    Path('data').mkdir(exist_ok=True)
    prices.to_csv('data/market_data.csv')
    returns.to_csv('data/returns_data.csv')
    
    print(f"\nSaved {len(prices)} days of data")
    print(f"  Prices: data/market_data.csv")
    print(f"  Returns: data/returns_data.csv")
    print(f"  Date range: {prices.index[0].date()} to {prices.index[-1].date()}")

if __name__ == '__main__':
    main()
