"""
Tax efficiency calculations and asset location optimization.

This module implements tax-aware portfolio management including asset location
optimization, tax-loss harvesting, and tax-adjusted return calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum
import warnings

class AccountType(Enum):
    """Types of investment accounts with different tax treatments."""
    TAXABLE = "taxable"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    HSA = "hsa"

class TaxEfficiencyCalculator:
    """
    Calculates tax efficiency metrics and optimizes asset location.
    
    This class handles:
    - Asset location optimization across account types
    - Tax-adjusted return calculations
    - Tax-loss harvesting simulation
    - After-tax portfolio analysis
    """
    
    def __init__(self,
                 ordinary_tax_rate: float = 0.24,      # 24% ordinary income rate
                 capital_gains_rate: float = 0.15,     # 15% long-term capital gains
                 dividend_tax_rate: float = 0.15,      # 15% qualified dividends
                 state_tax_rate: float = 0.05):        # 5% state taxes
        """
        Initialize tax efficiency calculator.
        
        Args:
            ordinary_tax_rate: Tax rate on ordinary income (traditional IRA withdrawals)
            capital_gains_rate: Tax rate on long-term capital gains
            dividend_tax_rate: Tax rate on qualified dividends
            state_tax_rate: State tax rate (applied to some income types)
        """
        self.ordinary_tax_rate = ordinary_tax_rate
        self.capital_gains_rate = capital_gains_rate  
        self.dividend_tax_rate = dividend_tax_rate
        self.state_tax_rate = state_tax_rate
    
    def calculate_tax_efficiency_score(self,
                                     asset_type: str,
                                     dividend_yield: float = 0.02,
                                     turnover_rate: float = 0.05,
                                     growth_rate: float = 0.07) -> float:
        """
        Calculate tax efficiency score for an asset.
        
        Args:
            asset_type: Type of asset ('stock', 'bond', 'reit', etc.)
            dividend_yield: Annual dividend yield
            turnover_rate: Portfolio turnover rate (triggers capital gains)
            growth_rate: Expected growth rate
        
        Returns:
            Tax efficiency score (higher is more tax efficient)
        """
        # Tax drag from dividends
        dividend_tax_drag = dividend_yield * self.dividend_tax_rate
        
        # Tax drag from turnover (realized gains)
        turnover_tax_drag = turnover_rate * growth_rate * self.capital_gains_rate
        
        # Total tax drag
        total_tax_drag = dividend_tax_drag + turnover_tax_drag
        
        # Tax efficiency score (1 - tax drag)
        efficiency_score = 1 - total_tax_drag
        
        return max(0, efficiency_score)  # Can't be negative
    
    def rank_assets_for_taxable_account(self,
                                      asset_data: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """
        Rank assets by their suitability for taxable accounts.
        
        Args:
            asset_data: Dictionary with asset data including dividend_yield, turnover_rate
        
        Returns:
            DataFrame with assets ranked by tax efficiency
        """
        results = []
        
        for asset, data in asset_data.items():
            dividend_yield = data.get('dividend_yield', 0.02)
            turnover_rate = data.get('turnover_rate', 0.05)
            growth_rate = data.get('growth_rate', 0.07)
            
            efficiency_score = self.calculate_tax_efficiency_score(
                asset_type=data.get('type', 'stock'),
                dividend_yield=dividend_yield,
                turnover_rate=turnover_rate,
                growth_rate=growth_rate
            )
            
            results.append({
                'asset': asset,
                'efficiency_score': efficiency_score,
                'dividend_yield': dividend_yield,
                'turnover_rate': turnover_rate,
                'dividend_tax_drag': dividend_yield * self.dividend_tax_rate,
                'turnover_tax_drag': turnover_rate * growth_rate * self.capital_gains_rate
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('efficiency_score', ascending=False)
        df['taxable_rank'] = range(1, len(df) + 1)
        
        return df
    
    def optimize_asset_location(self,
                              target_weights: Dict[str, float],
                              account_values: Dict[AccountType, float],
                              asset_characteristics: Dict[str, Dict[str, float]]) -> Dict[AccountType, Dict[str, float]]:
        """
        Optimize asset location across account types for tax efficiency.
        
        Args:
            target_weights: Overall target allocation
            account_values: Value available in each account type
            asset_characteristics: Asset data (dividend yield, growth rate, etc.)
        
        Returns:
            Dictionary with optimal allocation by account type
        """
        total_value = sum(account_values.values())
        
        # Calculate tax efficiency for each asset
        efficiency_df = self.rank_assets_for_taxable_account(asset_characteristics)
        asset_efficiency = dict(zip(efficiency_df['asset'], efficiency_df['efficiency_score']))
        
        # Initialize allocations
        allocations = {account_type: {} for account_type in account_values.keys()}
        
        # Sort assets by tax efficiency (least efficient first for tax-advantaged accounts)
        assets_by_efficiency = sorted(target_weights.keys(), 
                                    key=lambda x: asset_efficiency.get(x, 0.5))
        
        # Track remaining capacity in each account
        remaining_capacity = account_values.copy()
        
        # Allocation strategy:
        # 1. Put tax-inefficient assets in tax-advantaged accounts first
        # 2. Put remaining assets in taxable accounts
        
        for asset in assets_by_efficiency:
            target_value = target_weights[asset] * total_value
            remaining_to_allocate = target_value
            
            # Try to place in tax-advantaged accounts first (for tax-inefficient assets)
            efficiency = asset_efficiency.get(asset, 0.5)
            
            if efficiency < 0.8:  # Tax-inefficient assets
                # Prioritize traditional IRA, then Roth IRA, then HSA
                for account_type in [AccountType.TRADITIONAL_IRA, AccountType.ROTH_IRA, AccountType.HSA]:
                    if account_type in remaining_capacity and remaining_to_allocate > 0:
                        can_allocate = min(remaining_to_allocate, remaining_capacity[account_type])
                        
                        if can_allocate > 0:
                            allocations[account_type][asset] = can_allocate
                            remaining_capacity[account_type] -= can_allocate
                            remaining_to_allocate -= can_allocate
            
            # Place remaining amount in taxable account
            if remaining_to_allocate > 0 and AccountType.TAXABLE in remaining_capacity:
                can_allocate = min(remaining_to_allocate, remaining_capacity[AccountType.TAXABLE])
                
                if can_allocate > 0:
                    allocations[AccountType.TAXABLE][asset] = can_allocate
                    remaining_capacity[AccountType.TAXABLE] -= can_allocate
        
        # Convert to weights within each account
        for account_type in allocations:
            account_total = sum(allocations[account_type].values())
            if account_total > 0:
                for asset in allocations[account_type]:
                    allocations[account_type][asset] /= account_total
        
        return allocations
    
    def calculate_after_tax_returns(self,
                                  returns_data: pd.DataFrame,
                                  dividend_yields: Dict[str, float],
                                  account_type: AccountType = AccountType.TAXABLE) -> pd.DataFrame:
        """
        Calculate after-tax returns for assets.
        
        Args:
            returns_data: DataFrame with pre-tax returns
            dividend_yields: Annual dividend yields for each asset
            account_type: Account type for tax calculation
        
        Returns:
            DataFrame with after-tax returns
        """
        after_tax_returns = returns_data.copy()
        
        if account_type == AccountType.TAXABLE:
            # Apply taxes to dividend portion and capital gains
            for asset in returns_data.columns:
                if asset in dividend_yields:
                    # Approximate dividend contribution to daily returns
                    annual_dividend_yield = dividend_yields[asset]
                    daily_dividend_yield = annual_dividend_yield / 252
                    
                    # Split returns into dividend and capital gains components
                    dividend_component = daily_dividend_yield
                    capital_gains_component = returns_data[asset] - dividend_component
                    
                    # Apply taxes
                    after_tax_dividend = dividend_component * (1 - self.dividend_tax_rate)
                    after_tax_capital_gains = capital_gains_component * (1 - self.capital_gains_rate)
                    
                    after_tax_returns[asset] = after_tax_dividend + after_tax_capital_gains
        
        # For tax-advantaged accounts, returns are not taxed during accumulation
        elif account_type in [AccountType.TRADITIONAL_IRA, AccountType.ROTH_IRA, AccountType.HSA]:
            pass  # No current taxation
        
        return after_tax_returns
    
    def calculate_tax_alpha(self,
                          portfolio_returns: pd.Series,
                          benchmark_returns: pd.Series,
                          portfolio_dividend_yield: float = 0.02,
                          benchmark_dividend_yield: float = 0.02) -> float:
        """
        Calculate tax alpha - the after-tax outperformance vs benchmark.
        
        Args:
            portfolio_returns: Portfolio returns (pre-tax)
            benchmark_returns: Benchmark returns (pre-tax)
            portfolio_dividend_yield: Portfolio dividend yield
            benchmark_dividend_yield: Benchmark dividend yield
        
        Returns:
            Tax alpha (annualized)
        """
        # Calculate after-tax returns for both
        portfolio_after_tax = self._apply_tax_to_returns(portfolio_returns, portfolio_dividend_yield)
        benchmark_after_tax = self._apply_tax_to_returns(benchmark_returns, benchmark_dividend_yield)
        
        # Calculate annualized alpha
        portfolio_annual = (1 + portfolio_after_tax.mean()) ** 252 - 1
        benchmark_annual = (1 + benchmark_after_tax.mean()) ** 252 - 1
        
        tax_alpha = portfolio_annual - benchmark_annual
        
        return tax_alpha
    
    def _apply_tax_to_returns(self, returns: pd.Series, dividend_yield: float) -> pd.Series:
        """Helper method to apply taxes to returns."""
        daily_dividend_yield = dividend_yield / 252
        
        # Split returns into components
        dividend_component = daily_dividend_yield
        capital_gains_component = returns - dividend_component
        
        # Apply taxes
        after_tax_dividend = dividend_component * (1 - self.dividend_tax_rate)
        after_tax_capital_gains = capital_gains_component * (1 - self.capital_gains_rate)
        
        return after_tax_dividend + after_tax_capital_gains
    
    def simulate_tax_loss_harvesting(self,
                                   price_data: pd.DataFrame,
                                   portfolio_weights: Dict[str, float],
                                   loss_threshold: float = -0.05,
                                   wash_sale_days: int = 31) -> Dict[str, float]:
        """
        Simulate tax-loss harvesting opportunities.
        
        Args:
            price_data: Historical price data
            portfolio_weights: Portfolio weights
            loss_threshold: Minimum loss threshold to trigger harvesting
            wash_sale_days: Days to wait before repurchasing (wash sale rule)
        
        Returns:
            Dictionary with tax-loss harvesting analysis
        """
        results = {
            'total_losses_harvested': 0.0,
            'tax_savings': 0.0,
            'num_harvest_events': 0,
            'harvest_dates': []
        }
        
        # Calculate returns for each asset
        returns_data = price_data.pct_change().dropna()
        
        for asset in portfolio_weights.keys():
            if asset not in returns_data.columns:
                continue
            
            asset_returns = returns_data[asset]
            cumulative_returns = (1 + asset_returns).cumprod()
            
            # Find loss periods
            losses = cumulative_returns[cumulative_returns < (1 + loss_threshold)]
            
            if not losses.empty:
                # Calculate potential tax savings
                for date, cum_return in losses.items():
                    loss_amount = abs(cum_return - 1) * portfolio_weights[asset]
                    tax_savings = loss_amount * self.capital_gains_rate
                    
                    results['total_losses_harvested'] += loss_amount
                    results['tax_savings'] += tax_savings
                    results['num_harvest_events'] += 1
                    results['harvest_dates'].append(date)
        
        return results
    
    def account_type_comparison(self,
                              initial_investment: float,
                              annual_return: float,
                              dividend_yield: float,
                              years: int) -> pd.DataFrame:
        """
        Compare investment growth across different account types.
        
        Args:
            initial_investment: Initial investment amount
            annual_return: Expected annual return (pre-tax)
            dividend_yield: Annual dividend yield
            years: Investment time horizon
        
        Returns:
            DataFrame comparing account types
        """
        results = []
        
        for account_type in AccountType:
            if account_type == AccountType.TAXABLE:
                # Taxable account: tax on dividends each year, capital gains at end
                after_tax_dividend_return = annual_return - (dividend_yield * self.dividend_tax_rate)
                final_value = initial_investment * (1 + after_tax_dividend_return) ** years
                
                # Apply capital gains tax on growth
                growth = final_value - initial_investment
                capital_gains_tax = growth * self.capital_gains_rate
                final_after_tax = final_value - capital_gains_tax
                
            elif account_type == AccountType.TRADITIONAL_IRA:
                # Traditional IRA: no taxes during growth, ordinary income tax on withdrawal
                final_value = initial_investment * (1 + annual_return) ** years
                final_after_tax = final_value * (1 - self.ordinary_tax_rate)
                
            elif account_type == AccountType.ROTH_IRA:
                # Roth IRA: no taxes (already paid upfront)
                final_after_tax = initial_investment * (1 + annual_return) ** years
                
            elif account_type == AccountType.HSA:
                # HSA: no taxes if used for qualified expenses
                final_after_tax = initial_investment * (1 + annual_return) ** years
            
            effective_rate = (final_after_tax / initial_investment) ** (1/years) - 1
            
            results.append({
                'account_type': account_type.value,
                'final_value': final_after_tax,
                'effective_annual_return': effective_rate,
                'total_return': (final_after_tax / initial_investment) - 1
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('final_value', ascending=False)
        
        return df
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"TaxEfficiencyCalculator(ordinary_rate={self.ordinary_tax_rate:.2%}, "
                f"cap_gains_rate={self.capital_gains_rate:.2%})")
