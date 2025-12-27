#!/usr/bin/env python3
"""
Create realistic factor investing data
Includes market, size, value, momentum factors
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Real historical factor premiums (Fama-French, 1927-2024)
FACTOR_STATS = {
    'Market': {'annual_return': 0.1020, 'annual_vol': 0.1850, 'sharpe': 0.42},
    'SMB': {'annual_return': 0.0320, 'annual_vol': 0.1580, 'sharpe': 0.20},  # Size premium
    'HML': {'annual_return': 0.0480, 'annual_vol': 0.1340, 'sharpe': 0.36},  # Value premium
    'MOM': {'annual_return': 0.0650, 'annual_vol': 0.1920, 'sharpe': 0.34},  # Momentum
    'RF': {'annual_return': 0.0330, 'annual_vol': 0.0050, 'sharpe': 0.00}    # Risk-free
}

# ETF mappings to factors
ETF_FACTORS = {
    'VTI': {'Market': 1.00, 'SMB': 0.05, 'HML': 0.00, 'MOM': 0.00},  # Market cap weighted
    'VOO': {'Market': 1.00, 'SMB': -0.10, 'HML': 0.00, 'MOM': 0.00}, # Large cap
    'VBR': {'Market': 0.95, 'SMB': 0.85, 'HML': 0.75, 'MOM': 0.00},  # Small value
    'VTV': {'Market': 0.98, 'SMB': -0.05, 'HML': 0.60, 'MOM': 0.00}, # Large value
    'MTUM': {'Market': 0.95, 'SMB': 0.00, 'HML': -0.20, 'MOM': 0.90}, # Momentum
    'VXUS': {'Market': 0.85, 'SMB': 0.10, 'HML': 0.15, 'MOM': 0.00}, # International
    'BND': {'Market': 0.00, 'SMB': 0.00, 'HML': 0.00, 'MOM': 0.00}   # Bonds
}

# Correlations between factors
FACTOR_CORR = pd.DataFrame([
    [1.00, 0.25, -0.30, -0.15, 0.00],  # Market
    [0.25, 1.00, 0.10, -0.05, 0.00],   # SMB
    [-0.30, 0.10, 1.00, -0.40, 0.00],  # HML
    [-0.15, -0.05, -0.40, 1.00, 0.00], # MOM
    [0.00, 0.00, 0.00, 0.00, 1.00]     # RF
], index=['Market', 'SMB', 'HML', 'MOM', 'RF'], 
   columns=['Market', 'SMB', 'HML', 'MOM', 'RF'])

def generate_factor_returns(n_days=2500, seed=42):
    """Generate correlated factor returns"""
    np.random.seed(seed)
    
    # Convert annual to daily
    daily_stats = {}
    for factor, stats in FACTOR_STATS.items():
        daily_stats[factor] = {
            'mean': stats['annual_return'] / 252,
            'std': stats['annual_vol'] / np.sqrt(252)
        }
    
    # Generate correlated returns
    L = np.linalg.cholesky(FACTOR_CORR.values)
    uncorrelated = np.random.standard_normal((n_days, 5))
    correlated = uncorrelated @ L.T
    
    # Scale to match statistics
    factor_returns = pd.DataFrame(
        index=pd.date_range('2015-01-01', periods=n_days, freq='D')
    )
    
    for i, factor in enumerate(['Market', 'SMB', 'HML', 'MOM', 'RF']):
        factor_returns[factor] = (correlated[:, i] * daily_stats[factor]['std'] + 
                                   daily_stats[factor]['mean'])
    
    return factor_returns

def calculate_etf_returns(factor_returns):
    """Calculate ETF returns from factor exposures"""
    etf_returns = pd.DataFrame(index=factor_returns.index)
    
    for etf, exposures in ETF_FACTORS.items():
        etf_return = factor_returns['RF'].copy()  # Start with risk-free
        
        for factor, loading in exposures.items():
            if factor != 'RF':
                etf_return += loading * (factor_returns[factor] - factor_returns['RF'])
        
        etf_returns[etf] = etf_return
    
    return etf_returns

def main():
    print("Creating factor-based data...")
    print("\nFactor Premiums (Historical 1927-2024):")
    for factor, stats in FACTOR_STATS.items():
        if factor != 'RF':
            print(f"  {factor:8s}: {stats['annual_return']:.1%} return, "
                  f"{stats['annual_vol']:.1%} vol, {stats['sharpe']:.2f} Sharpe")
    
    # Generate factor returns
    factor_returns = generate_factor_returns()
    
    # Calculate ETF returns
    etf_returns = calculate_etf_returns(factor_returns)
    
    # Verify statistics
    print("\nGenerated ETF Statistics:")
    for etf in ETF_FACTORS.keys():
        annual_ret = etf_returns[etf].mean() * 252
        annual_vol = etf_returns[etf].std() * np.sqrt(252)
        sharpe = annual_ret / annual_vol
        print(f"  {etf:6s}: {annual_ret:.1%} return, {annual_vol:.1%} vol, {sharpe:.2f} Sharpe")
    
    # Show factor loadings
    print("\nFactor Exposures:")
    print("ETF    Market   SMB    HML    MOM")
    print("-" * 40)
    for etf, exposures in ETF_FACTORS.items():
        if etf != 'BND':
            print(f"{etf:6s} {exposures['Market']:6.2f} {exposures['SMB']:6.2f} "
                  f"{exposures['HML']:6.2f} {exposures['MOM']:6.2f}")
    
    # Save
    Path('data').mkdir(exist_ok=True)
    etf_returns.to_csv('data/factor_returns.csv')
    factor_returns.to_csv('data/factor_data.csv')
    
    print(f"\nSaved {len(etf_returns)} days of factor-based data")
    print("  ETF returns: data/factor_returns.csv")
    print("  Factor data: data/factor_data.csv")

if __name__ == '__main__':
    main()
