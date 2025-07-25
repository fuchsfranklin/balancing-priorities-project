"""
Core Portfolio class for multi-objective portfolio optimization.

This module implements the central Portfolio class that represents a portfolio
of assets with their weights and provides methods for calculating returns,
risk metrics, and costs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings

class Portfolio:
    """
    Represents a portfolio of assets with their weights and provides
    methods for performance calculation and analysis.
    
    Attributes:
        weights (Dict[str, float]): Asset weights (must sum to 1.0)
        assets (List[str]): List of asset symbols/tickers
        creation_date (datetime): Portfolio creation date
        cash_weight (float): Weight allocated to cash (default 0.0)
    """
    
    def __init__(self, 
                 weights: Union[Dict[str, float], pd.Series], 
                 name: str = None,
                 creation_date: datetime = None):
        """
        Initialize a Portfolio.
        
        Args:
            weights: Dictionary or Series of asset weights (must sum to 1.0)
            name: Optional portfolio name
            creation_date: Portfolio creation date (defaults to today)
        
        Raises:
            ValueError: If weights don't sum to 1.0 or contain invalid values
        """
        if isinstance(weights, pd.Series):
            weights = weights.to_dict()
        
        self.weights = weights.copy()
        self.name = name or f"Portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.creation_date = creation_date or datetime.now()
        self.assets = list(weights.keys())
        self.cash_weight = 0.0
        
        # Validate weights
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        """Validate that portfolio weights are valid."""
        if not self.weights:
            raise ValueError("Portfolio must have at least one asset")
        
        # Check for negative weights
        negative_weights = {k: v for k, v in self.weights.items() if v < 0}
        if negative_weights:
            raise ValueError(f"Negative weights not allowed: {negative_weights}")
        
        # Check weight sum
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=1e-6):
            raise ValueError(f"Weights must sum to 1.0, got {total_weight:.6f}")
    
    def calculate_returns(self, 
                         price_data: pd.DataFrame,
                         method: str = 'simple') -> pd.Series:
        """
        Calculate portfolio returns from price data.
        
        Args:
            price_data: DataFrame with asset prices (columns=assets, index=dates)
            method: Return calculation method ('simple' or 'log')
        
        Returns:
            Series of portfolio returns
        """
        # Check that all portfolio assets are in price data
        missing_assets = set(self.assets) - set(price_data.columns)
        if missing_assets:
            raise ValueError(f"Missing price data for assets: {missing_assets}")
        
        # Calculate individual asset returns
        if method == 'simple':
            asset_returns = price_data.pct_change().dropna()
        elif method == 'log':
            asset_returns = np.log(price_data / price_data.shift(1)).dropna()
        else:
            raise ValueError(f"Unknown return method: {method}")
        
        # Calculate portfolio returns as weighted sum
        portfolio_returns = (asset_returns[self.assets] * pd.Series(self.weights)).sum(axis=1)
        
        return portfolio_returns
    
    def calculate_total_return(self, 
                              price_data: pd.DataFrame,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> float:
        """
        Calculate total portfolio return over a period.
        
        Args:
            price_data: DataFrame with asset prices
            start_date: Start date for calculation (defaults to first available)
            end_date: End date for calculation (defaults to last available)
        
        Returns:
            Total return as decimal (e.g., 0.15 for 15% return)
        """
        if start_date:
            price_data = price_data[price_data.index >= start_date]
        if end_date:
            price_data = price_data[price_data.index <= end_date]
        
        if len(price_data) < 2:
            raise ValueError("Need at least 2 data points to calculate returns")
        
        # Calculate portfolio value over time
        portfolio_value = (price_data[self.assets] * pd.Series(self.weights)).sum(axis=1)
        
        total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
        return total_return
    
    def calculate_volatility(self, 
                           price_data: pd.DataFrame,
                           annualize: bool = True,
                           trading_days: int = 252) -> float:
        """
        Calculate portfolio volatility (standard deviation of returns).
        
        Args:
            price_data: DataFrame with asset prices
            annualize: Whether to annualize the volatility
            trading_days: Number of trading days per year for annualization
        
        Returns:
            Portfolio volatility as decimal
        """
        returns = self.calculate_returns(price_data)
        volatility = returns.std()
        
        if annualize:
            volatility *= np.sqrt(trading_days)
        
        return volatility
    
    def calculate_sharpe_ratio(self,
                              price_data: pd.DataFrame,
                              risk_free_rate: float = 0.02,
                              trading_days: int = 252) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            price_data: DataFrame with asset prices
            risk_free_rate: Risk-free rate (annualized)
            trading_days: Number of trading days per year
        
        Returns:
            Sharpe ratio
        """
        returns = self.calculate_returns(price_data)
        
        # Annualize return and volatility
        annual_return = (1 + returns.mean()) ** trading_days - 1
        annual_volatility = returns.std() * np.sqrt(trading_days)
        
        if annual_volatility == 0:
            return 0.0
        
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        return sharpe_ratio
    
    def calculate_max_drawdown(self, price_data: pd.DataFrame) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            price_data: DataFrame with asset prices
        
        Returns:
            Maximum drawdown as positive decimal (e.g., 0.15 for 15% drawdown)
        """
        returns = self.calculate_returns(price_data)
        cumulative_returns = (1 + returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative_returns / running_max) - 1
        
        max_drawdown = abs(drawdown.min())
        return max_drawdown
    
    def calculate_var(self, 
                     price_data: pd.DataFrame,
                     confidence_level: float = 0.05) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            price_data: DataFrame with asset prices
            confidence_level: Confidence level (e.g., 0.05 for 5% VaR)
        
        Returns:
            VaR as negative value (loss)
        """
        returns = self.calculate_returns(price_data)
        var = np.percentile(returns, confidence_level * 100)
        return var
    
    def rebalance(self, new_weights: Union[Dict[str, float], pd.Series]) -> 'Portfolio':
        """
        Create a new portfolio with updated weights.
        
        Args:
            new_weights: New asset weights
        
        Returns:
            New Portfolio instance with updated weights
        """
        return Portfolio(weights=new_weights, name=f"{self.name}_rebalanced")
    
    def get_asset_contribution(self, price_data: pd.DataFrame) -> pd.Series:
        """
        Calculate each asset's contribution to portfolio return.
        
        Args:
            price_data: DataFrame with asset prices
        
        Returns:
            Series with asset contributions
        """
        asset_returns = price_data.pct_change().dropna()
        contributions = asset_returns[self.assets] * pd.Series(self.weights)
        
        return contributions.sum()  # Total contribution over period
    
    def summary_stats(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate comprehensive portfolio statistics.
        
        Args:
            price_data: DataFrame with asset prices
        
        Returns:
            Dictionary of portfolio statistics
        """
        returns = self.calculate_returns(price_data)
        
        stats = {
            'total_return': self.calculate_total_return(price_data),
            'annualized_return': (1 + returns.mean()) ** 252 - 1,
            'volatility': self.calculate_volatility(price_data),
            'sharpe_ratio': self.calculate_sharpe_ratio(price_data),
            'max_drawdown': self.calculate_max_drawdown(price_data),
            'var_5pct': self.calculate_var(price_data, 0.05),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'best_day': returns.max(),
            'worst_day': returns.min(),
            'positive_days': (returns > 0).sum() / len(returns),
            'num_observations': len(returns)
        }
        
        return stats
    
    def __repr__(self) -> str:
        """String representation of the portfolio."""
        weight_str = ", ".join([f"{k}: {v:.3f}" for k, v in self.weights.items()])
        return f"Portfolio(name='{self.name}', weights=[{weight_str}])"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [f"Portfolio: {self.name}"]
        lines.append(f"Created: {self.creation_date.strftime('%Y-%m-%d')}")
        lines.append(f"Assets: {len(self.assets)}")
        lines.append("Weights:")
        for asset, weight in self.weights.items():
            lines.append(f"  {asset}: {weight:.1%}")
        return "\\n".join(lines)
