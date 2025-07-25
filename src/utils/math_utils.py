"""
Mathematical utilities for portfolio optimization and analysis.

This module provides utility functions for mathematical operations
commonly used in portfolio optimization and financial analysis.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, List
from scipy import stats
from scipy.optimize import minimize
import warnings

def calculate_portfolio_return(weights: np.ndarray, 
                             returns: Union[pd.DataFrame, np.ndarray]) -> float:
    """
    Calculate expected portfolio return.
    
    Args:
        weights: Portfolio weights
        returns: Asset returns (DataFrame or array)
        
    Returns:
        Expected portfolio return
    """
    if isinstance(returns, pd.DataFrame):
        mean_returns = returns.mean().values
    else:
        mean_returns = np.mean(returns, axis=0)
    
    return np.dot(weights, mean_returns)

def calculate_portfolio_volatility(weights: np.ndarray,
                                 returns: Union[pd.DataFrame, np.ndarray]) -> float:
    """
    Calculate portfolio volatility (standard deviation).
    
    Args:
        weights: Portfolio weights
        returns: Asset returns
        
    Returns:
        Portfolio volatility
    """
    if isinstance(returns, pd.DataFrame):
        cov_matrix = returns.cov().values
    else:
        cov_matrix = np.cov(returns, rowvar=False)
    
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return np.sqrt(portfolio_variance)

def calculate_sharpe_ratio(returns: Union[pd.Series, np.ndarray],
                          risk_free_rate: float = 0.0,
                          periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Portfolio or asset returns
        risk_free_rate: Risk-free rate (annualized)
        periods_per_year: Number of periods per year for annualization
        
    Returns:
        Sharpe ratio
    """
    if isinstance(returns, pd.Series):
        returns_array = returns.values
    else:
        returns_array = returns
    
    # Annualize returns and volatility
    mean_return = np.mean(returns_array) * periods_per_year
    volatility = np.std(returns_array, ddof=1) * np.sqrt(periods_per_year)
    
    if volatility == 0:
        return 0.0
    
    return (mean_return - risk_free_rate) / volatility

def calculate_sortino_ratio(returns: Union[pd.Series, np.ndarray],
                           risk_free_rate: float = 0.0,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Sortino ratio (uses downside deviation instead of total volatility).
    
    Args:
        returns: Portfolio or asset returns
        risk_free_rate: Risk-free rate (annualized)
        periods_per_year: Number of periods per year
        
    Returns:
        Sortino ratio
    """
    if isinstance(returns, pd.Series):
        returns_array = returns.values
    else:
        returns_array = returns
    
    # Calculate excess returns
    excess_returns = returns_array - (risk_free_rate / periods_per_year)
    
    # Calculate downside deviation
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0:
        downside_deviation = 0.0
    else:
        downside_deviation = np.sqrt(np.mean(downside_returns**2)) * np.sqrt(periods_per_year)
    
    # Calculate annualized excess return
    mean_excess_return = np.mean(excess_returns) * periods_per_year
    
    if downside_deviation == 0:
        return np.inf if mean_excess_return > 0 else 0.0
    
    return mean_excess_return / downside_deviation

def calculate_maximum_drawdown(prices: Union[pd.Series, np.ndarray]) -> Tuple[float, int, int]:
    """
    Calculate maximum drawdown and its duration.
    
    Args:
        prices: Price series or cumulative returns
        
    Returns:
        Tuple of (max_drawdown, start_index, end_index)
    """
    if isinstance(prices, pd.Series):
        price_array = prices.values
    else:
        price_array = prices
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(price_array)
    
    # Calculate drawdown
    drawdown = (price_array - running_max) / running_max
    
    # Find maximum drawdown
    max_dd_idx = np.argmin(drawdown)
    max_drawdown = drawdown[max_dd_idx]
    
    # Find start of drawdown (last peak before max drawdown)
    start_idx = 0
    for i in range(max_dd_idx, -1, -1):
        if drawdown[i] == 0:
            start_idx = i
            break
    
    return abs(max_drawdown), start_idx, max_dd_idx

def calculate_var(returns: Union[pd.Series, np.ndarray],
                 confidence_level: float = 0.05) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Return series
        confidence_level: Confidence level (e.g., 0.05 for 5% VaR)
        
    Returns:
        VaR value (positive number representing loss)
    """
    if isinstance(returns, pd.Series):
        returns_array = returns.values
    else:
        returns_array = returns
    
    return -np.percentile(returns_array, confidence_level * 100)

def calculate_cvar(returns: Union[pd.Series, np.ndarray],
                  confidence_level: float = 0.05) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
    
    Args:
        returns: Return series
        confidence_level: Confidence level (e.g., 0.05 for 5% CVaR)
        
    Returns:
        CVaR value (positive number representing expected loss)
    """
    if isinstance(returns, pd.Series):
        returns_array = returns.values
    else:
        returns_array = returns
    
    var_threshold = -calculate_var(returns_array, confidence_level)
    tail_losses = returns_array[returns_array <= var_threshold]
    
    if len(tail_losses) == 0:
        return 0.0
    
    return -np.mean(tail_losses)

def calculate_information_ratio(portfolio_returns: Union[pd.Series, np.ndarray],
                              benchmark_returns: Union[pd.Series, np.ndarray],
                              periods_per_year: int = 252) -> float:
    """
    Calculate Information Ratio.
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        periods_per_year: Number of periods per year
        
    Returns:
        Information ratio
    """
    # Calculate excess returns
    excess_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
    
    # Calculate tracking error (standard deviation of excess returns)
    tracking_error = np.std(excess_returns, ddof=1) * np.sqrt(periods_per_year)
    
    if tracking_error == 0:
        return 0.0
    
    # Calculate annualized excess return
    mean_excess_return = np.mean(excess_returns) * periods_per_year
    
    return mean_excess_return / tracking_error

def calculate_beta(asset_returns: Union[pd.Series, np.ndarray],
                  market_returns: Union[pd.Series, np.ndarray]) -> float:
    """
    Calculate beta coefficient.
    
    Args:
        asset_returns: Asset return series
        market_returns: Market return series
        
    Returns:
        Beta coefficient
    """
    # Convert to arrays
    asset_array = np.array(asset_returns)
    market_array = np.array(market_returns)
    
    # Calculate covariance and variance
    covariance = np.cov(asset_array, market_array)[0, 1]
    market_variance = np.var(market_array, ddof=1)
    
    if market_variance == 0:
        return 0.0
    
    return covariance / market_variance

def calculate_treynor_ratio(returns: Union[pd.Series, np.ndarray],
                           market_returns: Union[pd.Series, np.ndarray],
                           risk_free_rate: float = 0.0,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Treynor ratio.
    
    Args:
        returns: Portfolio return series
        market_returns: Market return series
        risk_free_rate: Risk-free rate (annualized)
        periods_per_year: Number of periods per year
        
    Returns:
        Treynor ratio
    """
    # Calculate beta
    beta = calculate_beta(returns, market_returns)
    
    if beta == 0:
        return 0.0
    
    # Calculate annualized excess return
    mean_return = np.mean(returns) * periods_per_year
    excess_return = mean_return - risk_free_rate
    
    return excess_return / beta

def efficient_frontier_points(mean_returns: np.ndarray,
                            cov_matrix: np.ndarray,
                            num_points: int = 100,
                            risk_free_rate: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate efficient frontier points.
    
    Args:
        mean_returns: Expected returns for each asset
        cov_matrix: Covariance matrix
        num_points: Number of points on the frontier
        risk_free_rate: Risk-free rate
        
    Returns:
        Tuple of (returns, volatilities, sharpe_ratios)
    """
    n_assets = len(mean_returns)
    
    # Define optimization constraints
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    
    # Calculate minimum variance portfolio
    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    # Find minimum and maximum return portfolios
    min_vol_result = minimize(portfolio_volatility, 
                             x0=np.array([1/n_assets] * n_assets),
                             method='SLSQP',
                             bounds=bounds,
                             constraints=constraints)
    
    min_return = np.dot(min_vol_result.x, mean_returns)
    max_return = np.max(mean_returns)
    
    # Generate target returns
    target_returns = np.linspace(min_return, max_return, num_points)
    
    frontier_returns = []
    frontier_volatilities = []
    frontier_sharpe_ratios = []
    
    for target_return in target_returns:
        # Add return constraint
        return_constraint = {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_return}
        all_constraints = [constraints, return_constraint]
        
        # Optimize
        result = minimize(portfolio_volatility,
                         x0=np.array([1/n_assets] * n_assets),
                         method='SLSQP',
                         bounds=bounds,
                         constraints=all_constraints)
        
        if result.success:
            portfolio_return = np.dot(result.x, mean_returns)
            portfolio_vol = portfolio_volatility(result.x)
            sharpe = (portfolio_return - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
            
            frontier_returns.append(portfolio_return)
            frontier_volatilities.append(portfolio_vol)
            frontier_sharpe_ratios.append(sharpe)
    
    return np.array(frontier_returns), np.array(frontier_volatilities), np.array(frontier_sharpe_ratios)

def calculate_rolling_correlation(series1: pd.Series,
                                series2: pd.Series,
                                window: int = 60) -> pd.Series:
    """
    Calculate rolling correlation between two series.
    
    Args:
        series1: First time series
        series2: Second time series
        window: Rolling window size
        
    Returns:
        Rolling correlation series
    """
    return series1.rolling(window=window).corr(series2)

def calculate_rolling_beta(asset_returns: pd.Series,
                         market_returns: pd.Series,
                         window: int = 60) -> pd.Series:
    """
    Calculate rolling beta.
    
    Args:
        asset_returns: Asset return series
        market_returns: Market return series
        window: Rolling window size
        
    Returns:
        Rolling beta series
    """
    def rolling_beta_func(asset_rets, market_rets):
        if len(asset_rets) < 2 or len(market_rets) < 2:
            return np.nan
        covariance = np.cov(asset_rets, market_rets)[0, 1]
        market_variance = np.var(market_rets, ddof=1)
        return covariance / market_variance if market_variance != 0 else np.nan
    
    # Align the series
    aligned_data = pd.concat([asset_returns, market_returns], axis=1).dropna()
    if len(aligned_data.columns) != 2:
        return pd.Series(dtype=float)
    
    asset_col, market_col = aligned_data.columns
    
    rolling_betas = []
    for i in range(window, len(aligned_data) + 1):
        window_data = aligned_data.iloc[i-window:i]
        beta = rolling_beta_func(window_data[asset_col].values, window_data[market_col].values)
        rolling_betas.append(beta)
    
    # Create series with proper index
    result_index = aligned_data.index[window-1:]
    return pd.Series(rolling_betas, index=result_index)

def annualize_return(returns: Union[float, np.ndarray, pd.Series],
                    periods_per_year: int = 252) -> Union[float, np.ndarray, pd.Series]:
    """
    Annualize returns.
    
    Args:
        returns: Return data
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized returns
    """
    if isinstance(returns, (int, float)):
        return (1 + returns) ** periods_per_year - 1
    else:
        return (1 + returns) ** periods_per_year - 1

def annualize_volatility(volatility: Union[float, np.ndarray, pd.Series],
                        periods_per_year: int = 252) -> Union[float, np.ndarray, pd.Series]:
    """
    Annualize volatility.
    
    Args:
        volatility: Volatility data
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized volatility
    """
    return volatility * np.sqrt(periods_per_year)

def compound_returns(returns: Union[pd.Series, np.ndarray]) -> Union[pd.Series, np.ndarray]:
    """
    Calculate cumulative compounded returns.
    
    Args:
        returns: Return series
        
    Returns:
        Cumulative returns
    """
    if isinstance(returns, pd.Series):
        return (1 + returns).cumprod() - 1
    else:
        return np.cumprod(1 + returns) - 1

def calculate_cagr(start_value: float, 
                  end_value: float, 
                  num_years: float) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    
    Args:
        start_value: Starting value
        end_value: Ending value
        num_years: Number of years
        
    Returns:
        CAGR as decimal
    """
    if start_value <= 0 or end_value <= 0 or num_years <= 0:
        return 0.0
    
    return (end_value / start_value) ** (1 / num_years) - 1
