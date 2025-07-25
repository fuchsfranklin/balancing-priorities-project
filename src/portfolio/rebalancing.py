"""
Portfolio rebalancing strategies and logic.

This module implements various rebalancing strategies including periodic,
threshold-based, and cost-aware rebalancing approaches.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import warnings

class RebalancingFrequency(Enum):
    """Enumeration of rebalancing frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"

class RebalancingStrategy:
    """
    Base class for portfolio rebalancing strategies.
    
    Implements various rebalancing approaches including periodic rebalancing,
    threshold-based rebalancing, and cost-aware strategies.
    """
    
    def __init__(self, 
                 target_weights: Dict[str, float],
                 frequency: Union[RebalancingFrequency, str] = RebalancingFrequency.QUARTERLY,
                 threshold: float = 0.05,
                 min_trade_size: float = 0.001):
        """
        Initialize rebalancing strategy.
        
        Args:
            target_weights: Target allocation weights
            frequency: Rebalancing frequency
            threshold: Deviation threshold for threshold-based rebalancing
            min_trade_size: Minimum trade size to execute (as fraction of portfolio)
        """
        self.target_weights = target_weights.copy()
        
        if isinstance(frequency, str):
            frequency = RebalancingFrequency(frequency)
        self.frequency = frequency
        
        self.threshold = threshold
        self.min_trade_size = min_trade_size
        
        # Validate target weights
        if not np.isclose(sum(target_weights.values()), 1.0, atol=1e-6):
            raise ValueError(f"Target weights must sum to 1.0, got {sum(target_weights.values()):.6f}")
    
    def should_rebalance_periodic(self, 
                                 current_date: datetime,
                                 last_rebalance_date: datetime) -> bool:
        """
        Check if portfolio should be rebalanced based on time elapsed.
        
        Args:
            current_date: Current date
            last_rebalance_date: Date of last rebalancing
        
        Returns:
            True if rebalancing is due
        """
        time_delta = current_date - last_rebalance_date
        
        frequency_days = {
            RebalancingFrequency.DAILY: 1,
            RebalancingFrequency.WEEKLY: 7,
            RebalancingFrequency.MONTHLY: 30,
            RebalancingFrequency.QUARTERLY: 90,
            RebalancingFrequency.SEMI_ANNUAL: 180,
            RebalancingFrequency.ANNUAL: 365
        }
        
        required_days = frequency_days[self.frequency]
        return time_delta.days >= required_days
    
    def should_rebalance_threshold(self, current_weights: Dict[str, float]) -> bool:
        """
        Check if portfolio should be rebalanced based on weight deviation.
        
        Args:
            current_weights: Current portfolio weights
        
        Returns:
            True if any asset deviates from target by more than threshold
        """
        for asset, target_weight in self.target_weights.items():
            current_weight = current_weights.get(asset, 0.0)
            deviation = abs(current_weight - target_weight)
            
            if deviation > self.threshold:
                return True
        
        return False
    
    def calculate_rebalancing_trades(self, 
                                   current_weights: Dict[str, float],
                                   portfolio_value: float = 1.0) -> Dict[str, Dict[str, float]]:
        """
        Calculate trades needed to rebalance to target weights.
        
        Args:
            current_weights: Current portfolio weights
            portfolio_value: Total portfolio value
        
        Returns:
            Dictionary with trade details for each asset
        """
        all_assets = set(self.target_weights.keys()) | set(current_weights.keys())
        trades = {}
        
        for asset in all_assets:
            current_weight = current_weights.get(asset, 0.0)
            target_weight = self.target_weights.get(asset, 0.0)
            weight_change = target_weight - current_weight
            
            # Only include trades above minimum size
            if abs(weight_change) >= self.min_trade_size:
                trade_value = weight_change * portfolio_value
                
                trades[asset] = {
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'weight_change': weight_change,
                    'trade_value': trade_value,
                    'trade_type': 'buy' if weight_change > 0 else 'sell'
                }
        
        return trades
    
    def calculate_tracking_error(self, 
                               weights_history: List[Dict[str, float]]) -> float:
        """
        Calculate tracking error relative to target allocation.
        
        Args:
            weights_history: Historical portfolio weights
        
        Returns:
            Average tracking error (standard deviation of weight deviations)
        """
        if not weights_history:
            return 0.0
        
        deviations = []
        
        for weights in weights_history:
            total_deviation = 0.0
            for asset, target_weight in self.target_weights.items():
                current_weight = weights.get(asset, 0.0)
                deviation = abs(current_weight - target_weight)
                total_deviation += deviation
            
            deviations.append(total_deviation)
        
        return np.std(deviations) if deviations else 0.0
    
    def simulate_rebalancing(self,
                           price_data: pd.DataFrame,
                           initial_value: float = 10000,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Union[pd.DataFrame, List]]:
        """
        Simulate portfolio rebalancing over time.
        
        Args:
            price_data: DataFrame with asset prices
            initial_value: Initial portfolio value
            start_date: Simulation start date
            end_date: Simulation end date
        
        Returns:
            Dictionary with simulation results
        """
        # Filter price data by date range
        if start_date:
            price_data = price_data[price_data.index >= start_date]
        if end_date:
            price_data = price_data[price_data.index <= end_date]
        
        if price_data.empty:
            raise ValueError("No price data available for simulation period")
        
        # Check that all target assets are in price data
        missing_assets = set(self.target_weights.keys()) - set(price_data.columns)
        if missing_assets:
            raise ValueError(f"Missing price data for assets: {missing_assets}")
        
        dates = price_data.index
        results = {
            'portfolio_value': [],
            'weights_history': [],
            'rebalancing_dates': [],
            'total_trades': 0,
            'tracking_error': 0.0
        }
        
        # Initialize portfolio
        current_weights = self.target_weights.copy()
        current_value = initial_value
        last_rebalance_date = dates[0]
        
        # Track shares for each asset
        shares = {}
        for asset, weight in current_weights.items():
            asset_value = weight * current_value
            shares[asset] = asset_value / price_data[asset].iloc[0]
        
        for i, current_date in enumerate(dates):
            # Calculate current portfolio value and weights
            current_prices = price_data.iloc[i]
            
            current_value = sum(shares.get(asset, 0) * current_prices[asset] 
                              for asset in self.target_weights.keys())
            
            current_weights = {}
            for asset in self.target_weights.keys():
                asset_value = shares.get(asset, 0) * current_prices[asset]
                current_weights[asset] = asset_value / current_value if current_value > 0 else 0
            
            # Check if rebalancing is needed
            should_rebalance = (
                self.should_rebalance_periodic(current_date, last_rebalance_date) or
                self.should_rebalance_threshold(current_weights)
            )
            
            if should_rebalance and i > 0:  # Don't rebalance on first day
                # Rebalance to target weights
                for asset, target_weight in self.target_weights.items():
                    target_value = target_weight * current_value
                    shares[asset] = target_value / current_prices[asset]
                
                current_weights = self.target_weights.copy()
                results['rebalancing_dates'].append(current_date)
                results['total_trades'] += 1
                last_rebalance_date = current_date
            
            # Store results
            results['portfolio_value'].append(current_value)
            results['weights_history'].append(current_weights.copy())
        
        # Calculate tracking error
        results['tracking_error'] = self.calculate_tracking_error(results['weights_history'])
        
        # Convert to DataFrames
        results['portfolio_value'] = pd.Series(results['portfolio_value'], index=dates)
        results['weights_df'] = pd.DataFrame(results['weights_history'], index=dates)
        
        return results
    
    def optimize_frequency(self,
                          price_data: pd.DataFrame,
                          cost_calculator = None,
                          frequencies_to_test: List[RebalancingFrequency] = None) -> Dict[str, float]:
        """
        Find optimal rebalancing frequency by testing different options.
        
        Args:
            price_data: Historical price data
            cost_calculator: CostCalculator instance for cost analysis
            frequencies_to_test: List of frequencies to test
        
        Returns:
            Dictionary with results for each frequency
        """
        if frequencies_to_test is None:
            frequencies_to_test = [
                RebalancingFrequency.MONTHLY,
                RebalancingFrequency.QUARTERLY,
                RebalancingFrequency.SEMI_ANNUAL,
                RebalancingFrequency.ANNUAL
            ]
        
        results = {}
        
        for frequency in frequencies_to_test:
            # Create temporary strategy with this frequency
            temp_strategy = RebalancingStrategy(
                target_weights=self.target_weights,
                frequency=frequency,
                threshold=self.threshold
            )
            
            # Simulate rebalancing
            sim_results = temp_strategy.simulate_rebalancing(price_data)
            
            # Calculate metrics
            portfolio_returns = sim_results['portfolio_value'].pct_change().dropna()
            total_return = (sim_results['portfolio_value'].iloc[-1] / 
                          sim_results['portfolio_value'].iloc[0]) - 1
            volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate costs if cost calculator provided
            total_cost = 0.0
            if cost_calculator:
                rebalancing_cost = cost_calculator.calculate_rebalancing_costs(
                    sim_results['weights_history'],
                    rebalancing_frequency=frequency.value
                )
                total_cost = rebalancing_cost['annual_rebalancing_cost']
            
            results[frequency.value] = {
                'total_return': total_return,
                'volatility': volatility,
                'tracking_error': sim_results['tracking_error'],
                'num_rebalances': sim_results['total_trades'],
                'total_cost': total_cost,
                'net_return': total_return - total_cost  # Simplified
            }
        
        return results
    
    def update_target_weights(self, new_weights: Dict[str, float]) -> None:
        """Update target weights for the strategy."""
        if not np.isclose(sum(new_weights.values()), 1.0, atol=1e-6):
            raise ValueError(f"New weights must sum to 1.0, got {sum(new_weights.values()):.6f}")
        self.target_weights = new_weights.copy()
    
    def __repr__(self) -> str:
        """String representation."""
        assets_str = ", ".join([f"{k}: {v:.3f}" for k, v in self.target_weights.items()])
        return (f"RebalancingStrategy(frequency={self.frequency.value}, "
                f"threshold={self.threshold:.3f}, weights=[{assets_str}])")
