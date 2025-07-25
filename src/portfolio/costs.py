"""
Portfolio cost calculation module.

This module implements comprehensive cost calculations for portfolios including
expense ratios, transaction costs, tax impacts, and total cost of ownership.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import warnings

class CostCalculator:
    """
    Calculates various costs associated with portfolio management.
    
    This includes:
    - Fund expense ratios
    - Transaction costs (brokerage fees, spreads)
    - Tax costs (capital gains, dividend taxes)
    - Rebalancing costs
    """
    
    def __init__(self, 
                 expense_ratios: Dict[str, float] = None,
                 transaction_cost_rate: float = 0.0005,  # 5 bps default
                 tax_rate_dividends: float = 0.15,       # 15% qualified dividends
                 tax_rate_capital_gains: float = 0.15):   # 15% long-term capital gains
        """
        Initialize the cost calculator.
        
        Args:
            expense_ratios: Dictionary of asset expense ratios (annual, as decimal)
            transaction_cost_rate: Transaction cost as % of trade value (decimal)
            tax_rate_dividends: Tax rate on dividend income (decimal)
            tax_rate_capital_gains: Tax rate on capital gains (decimal)
        """
        self.expense_ratios = expense_ratios or {}
        self.transaction_cost_rate = transaction_cost_rate
        self.tax_rate_dividends = tax_rate_dividends
        self.tax_rate_capital_gains = tax_rate_capital_gains
    
    def set_expense_ratios(self, expense_ratios: Dict[str, float]) -> None:
        """Update expense ratios for assets."""
        self.expense_ratios.update(expense_ratios)
    
    def calculate_expense_ratio_cost(self, 
                                   weights: Union[Dict[str, float], pd.Series],
                                   portfolio_value: float = 1.0) -> float:
        """
        Calculate annual cost from expense ratios.
        
        Args:
            weights: Portfolio weights
            portfolio_value: Total portfolio value (default 1.0 for percentage calc)
        
        Returns:
            Annual expense ratio cost as decimal
        """
        if isinstance(weights, pd.Series):
            weights = weights.to_dict()
        
        total_expense_cost = 0.0
        
        for asset, weight in weights.items():
            if asset in self.expense_ratios:
                asset_expense_ratio = self.expense_ratios[asset]
                asset_cost = weight * asset_expense_ratio * portfolio_value
                total_expense_cost += asset_cost
            else:
                warnings.warn(f"No expense ratio data for {asset}, assuming 0%")
        
        return total_expense_cost
    
    def calculate_transaction_costs(self,
                                  old_weights: Union[Dict[str, float], pd.Series],
                                  new_weights: Union[Dict[str, float], pd.Series],
                                  portfolio_value: float = 1.0) -> Dict[str, float]:
        """
        Calculate transaction costs for rebalancing.
        
        Args:
            old_weights: Current portfolio weights
            new_weights: Target portfolio weights
            portfolio_value: Total portfolio value
        
        Returns:
            Dictionary with transaction cost details
        """
        if isinstance(old_weights, pd.Series):
            old_weights = old_weights.to_dict()
        if isinstance(new_weights, pd.Series):
            new_weights = new_weights.to_dict()
        
        # Calculate weight changes
        all_assets = set(old_weights.keys()) | set(new_weights.keys())
        
        total_turnover = 0.0
        asset_trades = {}
        
        for asset in all_assets:
            old_weight = old_weights.get(asset, 0.0)
            new_weight = new_weights.get(asset, 0.0)
            weight_change = abs(new_weight - old_weight)
            
            if weight_change > 1e-6:  # Ignore very small changes
                trade_value = weight_change * portfolio_value
                transaction_cost = trade_value * self.transaction_cost_rate
                
                asset_trades[asset] = {
                    'weight_change': weight_change,
                    'trade_value': trade_value,
                    'transaction_cost': transaction_cost
                }
                
                total_turnover += weight_change
        
        total_transaction_cost = sum(trade['transaction_cost'] for trade in asset_trades.values())
        
        return {
            'total_transaction_cost': total_transaction_cost,
            'total_turnover': total_turnover / 2,  # Divide by 2 to avoid double counting
            'transaction_cost_rate': self.transaction_cost_rate,
            'asset_trades': asset_trades
        }
    
    def calculate_tax_costs(self,
                           returns_data: pd.DataFrame,
                           weights: Union[Dict[str, float], pd.Series],
                           dividend_yields: Dict[str, float] = None,
                           holding_period_years: float = 1.0) -> Dict[str, float]:
        """
        Calculate tax costs on dividends and capital gains.
        
        Args:
            returns_data: DataFrame with asset returns
            weights: Portfolio weights
            dividend_yields: Annual dividend yields for each asset
            holding_period_years: Holding period for capital gains calculation
        
        Returns:
            Dictionary with tax cost details
        """
        if isinstance(weights, pd.Series):
            weights = weights.to_dict()
        
        dividend_yields = dividend_yields or {}
        
        # Calculate dividend tax costs
        dividend_tax_cost = 0.0
        for asset, weight in weights.items():
            if asset in dividend_yields:
                annual_dividend = dividend_yields[asset] * weight
                dividend_tax = annual_dividend * self.tax_rate_dividends
                dividend_tax_cost += dividend_tax
        
        # Calculate capital gains tax (simplified - assumes realization)
        capital_gains_tax_cost = 0.0
        if not returns_data.empty and len(returns_data) > 1:
            # Calculate total returns for each asset
            for asset, weight in weights.items():
                if asset in returns_data.columns:
                    asset_returns = returns_data[asset].dropna()
                    if len(asset_returns) > 0:
                        # Calculate capital gain over holding period
                        total_return = (1 + asset_returns).prod() - 1
                        capital_gain = total_return * weight
                        
                        # Apply tax only on positive gains
                        if capital_gain > 0:
                            capital_gains_tax = capital_gain * self.tax_rate_capital_gains
                            capital_gains_tax_cost += capital_gains_tax
        
        return {
            'dividend_tax_cost': dividend_tax_cost,
            'capital_gains_tax_cost': capital_gains_tax_cost,
            'total_tax_cost': dividend_tax_cost + capital_gains_tax_cost,
            'dividend_tax_rate': self.tax_rate_dividends,
            'capital_gains_tax_rate': self.tax_rate_capital_gains
        }
    
    def calculate_rebalancing_costs(self,
                                  weights_history: List[Dict[str, float]],
                                  portfolio_value: float = 1.0,
                                  rebalancing_frequency: str = 'quarterly') -> Dict[str, float]:
        """
        Calculate total costs from periodic rebalancing.
        
        Args:
            weights_history: List of portfolio weights over time
            portfolio_value: Portfolio value
            rebalancing_frequency: How often rebalancing occurs
        
        Returns:
            Dictionary with rebalancing cost analysis
        """
        if len(weights_history) < 2:
            return {'total_rebalancing_cost': 0.0, 'rebalancing_events': 0}
        
        frequency_multipliers = {
            'monthly': 12,
            'quarterly': 4,
            'semi-annual': 2,
            'annual': 1
        }
        
        annual_frequency = frequency_multipliers.get(rebalancing_frequency, 4)
        
        total_cost = 0.0
        rebalancing_events = len(weights_history) - 1
        
        for i in range(1, len(weights_history)):
            old_weights = weights_history[i-1]
            new_weights = weights_history[i]
            
            transaction_costs = self.calculate_transaction_costs(
                old_weights, new_weights, portfolio_value
            )
            total_cost += transaction_costs['total_transaction_cost']
        
        # Annualize the cost
        years_covered = rebalancing_events / annual_frequency
        annual_rebalancing_cost = total_cost / years_covered if years_covered > 0 else 0.0
        
        return {
            'total_rebalancing_cost': total_cost,
            'annual_rebalancing_cost': annual_rebalancing_cost,
            'rebalancing_events': rebalancing_events,
            'average_cost_per_rebalance': total_cost / rebalancing_events if rebalancing_events > 0 else 0.0,
            'rebalancing_frequency': rebalancing_frequency
        }
    
    def calculate_total_cost_of_ownership(self,
                                        weights: Union[Dict[str, float], pd.Series],
                                        returns_data: pd.DataFrame,
                                        rebalancing_frequency: str = 'quarterly',
                                        portfolio_value: float = 1.0,
                                        time_horizon_years: float = 1.0) -> Dict[str, float]:
        """
        Calculate comprehensive total cost of ownership.
        
        Args:
            weights: Portfolio weights
            returns_data: Historical returns data
            rebalancing_frequency: How often to rebalance
            portfolio_value: Portfolio value
            time_horizon_years: Investment time horizon
        
        Returns:
            Comprehensive cost breakdown
        """
        # Annual expense ratio cost
        expense_cost = self.calculate_expense_ratio_cost(weights, portfolio_value)
        
        # Estimate rebalancing costs (simplified)
        frequency_costs = {
            'monthly': 0.002,      # 20 bps per year
            'quarterly': 0.0005,   # 5 bps per year  
            'semi-annual': 0.0003, # 3 bps per year
            'annual': 0.0001       # 1 bp per year
        }
        annual_rebalancing_cost = frequency_costs.get(rebalancing_frequency, 0.0005) * portfolio_value
        
        # Tax costs (simplified - assume some dividend yield)
        estimated_dividend_yield = 0.02  # 2% average
        dividend_tax_cost = estimated_dividend_yield * self.tax_rate_dividends * portfolio_value
        
        total_annual_cost = expense_cost + annual_rebalancing_cost + dividend_tax_cost
        
        # Total cost over time horizon
        total_cost_over_horizon = total_annual_cost * time_horizon_years
        
        return {
            'annual_expense_cost': expense_cost,
            'annual_rebalancing_cost': annual_rebalancing_cost,
            'annual_dividend_tax_cost': dividend_tax_cost,
            'total_annual_cost': total_annual_cost,
            'total_cost_over_horizon': total_cost_over_horizon,
            'cost_as_percentage': total_annual_cost / portfolio_value if portfolio_value > 0 else 0,
            'time_horizon_years': time_horizon_years,
            'rebalancing_frequency': rebalancing_frequency
        }
    
    def cost_comparison(self,
                       portfolio_weights_list: List[Dict[str, float]],
                       portfolio_names: List[str] = None) -> pd.DataFrame:
        """
        Compare costs across multiple portfolio allocations.
        
        Args:
            portfolio_weights_list: List of portfolio weight dictionaries
            portfolio_names: Optional names for portfolios
        
        Returns:
            DataFrame comparing costs across portfolios
        """
        if portfolio_names is None:
            portfolio_names = [f"Portfolio_{i+1}" for i in range(len(portfolio_weights_list))]
        
        results = []
        
        for i, weights in enumerate(portfolio_weights_list):
            cost_breakdown = self.calculate_total_cost_of_ownership(weights)
            cost_breakdown['portfolio_name'] = portfolio_names[i]
            results.append(cost_breakdown)
        
        df = pd.DataFrame(results)
        df = df.set_index('portfolio_name')
        
        return df
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"CostCalculator(expense_ratios={len(self.expense_ratios)} assets, "
                f"transaction_rate={self.transaction_cost_rate:.4f})")
