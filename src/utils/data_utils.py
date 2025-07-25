"""
Data processing utilities for the Balancing Priorities Project.

This module provides utility functions for cleaning, transforming,
and validating financial data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings

def clean_price_data(data: pd.DataFrame, 
                    symbol: str = "Unknown",
                    min_price: float = 0.01,
                    max_price: float = 10000.0,
                    max_daily_change: float = 0.5) -> pd.DataFrame:
    """
    Clean price data by removing outliers and fixing common issues.
    
    Args:
        data: DataFrame with price data
        symbol: Symbol name for logging
        min_price: Minimum valid price
        max_price: Maximum valid price  
        max_daily_change: Maximum allowed daily price change (as decimal)
        
    Returns:
        Cleaned DataFrame
    """
    if data.empty:
        return data
    
    original_length = len(data)
    cleaned_data = data.copy()
    
    # Remove non-positive prices
    if 'Close' in cleaned_data.columns:
        price_col = 'Close'
    elif 'Adj Close' in cleaned_data.columns:
        price_col = 'Adj Close'
    else:
        price_col = cleaned_data.columns[0]  # Assume first column is price
    
    # Filter by price range
    mask = (cleaned_data[price_col] >= min_price) & (cleaned_data[price_col] <= max_price)
    cleaned_data = cleaned_data[mask]
    
    # Remove extreme daily changes
    if len(cleaned_data) > 1:
        returns = cleaned_data[price_col].pct_change().abs()
        extreme_change_mask = returns <= max_daily_change
        # Keep first row even if it has NaN return
        extreme_change_mask.iloc[0] = True
        cleaned_data = cleaned_data[extreme_change_mask]
    
    # Forward fill missing values
    cleaned_data = cleaned_data.fillna(method='ffill')
    
    # Drop any remaining NaN rows
    cleaned_data = cleaned_data.dropna()
    
    removed_count = original_length - len(cleaned_data)
    if removed_count > 0:
        warnings.warn(f"Removed {removed_count} invalid data points for {symbol}")
    
    return cleaned_data

def align_data_by_date(data_dict: Dict[str, pd.DataFrame], 
                      method: str = "inner") -> Dict[str, pd.DataFrame]:
    """
    Align multiple DataFrames by their date indices.
    
    Args:
        data_dict: Dictionary mapping symbols to DataFrames
        method: Alignment method ('inner', 'outer', 'left', 'right')
        
    Returns:
        Dictionary with aligned DataFrames
    """
    if not data_dict:
        return {}
    
    # Get all indices
    all_indices = [df.index for df in data_dict.values() if not df.empty]
    
    if not all_indices:
        return data_dict
    
    # Find common date range
    if method == "inner":
        # Use intersection of all indices
        common_index = all_indices[0]
        for idx in all_indices[1:]:
            common_index = common_index.intersection(idx)
    elif method == "outer":
        # Use union of all indices
        common_index = all_indices[0]
        for idx in all_indices[1:]:
            common_index = common_index.union(idx)
    else:
        # Use first DataFrame as reference
        common_index = all_indices[0]
    
    # Align all DataFrames
    aligned_data = {}
    for symbol, df in data_dict.items():
        if not df.empty:
            aligned_df = df.reindex(common_index, method='ffill')
            aligned_data[symbol] = aligned_df
    
    return aligned_data

def calculate_returns(prices: Union[pd.Series, pd.DataFrame],
                     return_type: str = "simple",
                     periods: int = 1,
                     dropna: bool = True) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate returns from price data.
    
    Args:
        prices: Price data (Series or DataFrame)
        return_type: Type of returns ('simple', 'log', 'percent')
        periods: Number of periods for return calculation
        dropna: Whether to drop NaN values
        
    Returns:
        Returns data
    """
    if return_type == "simple":
        returns = prices.pct_change(periods=periods)
    elif return_type == "log":
        returns = np.log(prices / prices.shift(periods))
    elif return_type == "percent":
        returns = prices.pct_change(periods=periods) * 100
    else:
        raise ValueError("return_type must be 'simple', 'log', or 'percent'")
    
    if dropna:
        returns = returns.dropna()
    
    return returns

def resample_data(data: pd.DataFrame, 
                 frequency: str,
                 aggregation: str = "last") -> pd.DataFrame:
    """
    Resample data to different frequency.
    
    Args:
        data: Input DataFrame
        frequency: Target frequency ('D', 'W', 'M', 'Q', 'A')
        aggregation: Aggregation method ('last', 'first', 'mean', 'sum')
        
    Returns:
        Resampled DataFrame
    """
    if data.empty:
        return data
    
    if aggregation == "last":
        resampled = data.resample(frequency).last()
    elif aggregation == "first":
        resampled = data.resample(frequency).first()
    elif aggregation == "mean":
        resampled = data.resample(frequency).mean()
    elif aggregation == "sum":
        resampled = data.resample(frequency).sum()
    else:
        raise ValueError("aggregation must be 'last', 'first', 'mean', or 'sum'")
    
    return resampled.dropna()

def detect_outliers(data: pd.Series, 
                   method: str = "iqr",
                   threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in a data series.
    
    Args:
        data: Input data series
        method: Detection method ('iqr', 'zscore', 'modified_zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean series indicating outliers
    """
    if method == "iqr":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (data < lower_bound) | (data > upper_bound)
        
    elif method == "zscore":
        z_scores = np.abs((data - data.mean()) / data.std())
        outliers = z_scores > threshold
        
    elif method == "modified_zscore":
        median = data.median()
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad
        outliers = np.abs(modified_z_scores) > threshold
        
    else:
        raise ValueError("method must be 'iqr', 'zscore', or 'modified_zscore'")
    
    return outliers

def validate_data_quality(data: pd.DataFrame,
                         min_observations: int = 100,
                         max_missing_ratio: float = 0.05,
                         min_date_coverage: int = 365) -> Dict[str, bool]:
    """
    Validate data quality against various criteria.
    
    Args:
        data: Input DataFrame
        min_observations: Minimum number of observations required
        max_missing_ratio: Maximum ratio of missing values allowed
        min_date_coverage: Minimum number of days of data coverage
        
    Returns:
        Dictionary with validation results
    """
    results = {}
    
    # Check minimum observations
    results['sufficient_observations'] = len(data) >= min_observations
    
    # Check missing data ratio
    missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
    results['acceptable_missing_data'] = missing_ratio <= max_missing_ratio
    
    # Check date coverage
    if len(data) > 1 and hasattr(data.index, 'dtype') and 'datetime' in str(data.index.dtype):
        date_range = (data.index[-1] - data.index[0]).days
        results['sufficient_date_coverage'] = date_range >= min_date_coverage
    else:
        results['sufficient_date_coverage'] = True  # Can't check without datetime index
    
    # Check for any data at all
    results['has_data'] = not data.empty
    
    # Check for non-numeric data in numeric columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        results['valid_numeric_data'] = not data[numeric_columns].isnull().all().any()
    else:
        results['valid_numeric_data'] = True
    
    # Overall quality
    results['overall_quality'] = all(results.values())
    
    return results

def standardize_column_names(data: pd.DataFrame, 
                           naming_convention: str = "snake_case") -> pd.DataFrame:
    """
    Standardize column names according to a naming convention.
    
    Args:
        data: Input DataFrame
        naming_convention: Naming convention ('snake_case', 'camel_case', 'lower')
        
    Returns:
        DataFrame with standardized column names
    """
    standardized_data = data.copy()
    
    if naming_convention == "snake_case":
        # Convert to snake_case
        new_columns = []
        for col in data.columns:
            # Replace spaces and special characters with underscores
            import re
            new_col = re.sub(r'[^a-zA-Z0-9]', '_', str(col))
            # Convert camelCase to snake_case
            new_col = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', new_col)
            # Convert to lowercase and remove multiple underscores
            new_col = re.sub(r'_+', '_', new_col.lower())
            # Remove leading/trailing underscores
            new_col = new_col.strip('_')
            new_columns.append(new_col)
        
    elif naming_convention == "camel_case":
        # Convert to camelCase
        new_columns = []
        for col in data.columns:
            # Split by non-alphanumeric characters
            import re
            words = re.split(r'[^a-zA-Z0-9]', str(col))
            # First word lowercase, rest title case
            new_col = words[0].lower() + ''.join(word.title() for word in words[1:] if word)
            new_columns.append(new_col)
            
    elif naming_convention == "lower":
        # Simple lowercase with spaces as underscores
        new_columns = [str(col).lower().replace(' ', '_') for col in data.columns]
        
    else:
        raise ValueError("naming_convention must be 'snake_case', 'camel_case', or 'lower'")
    
    standardized_data.columns = new_columns
    return standardized_data

def merge_data_sources(sources: Dict[str, pd.DataFrame],
                      on_column: Optional[str] = None,
                      how: str = "outer") -> pd.DataFrame:
    """
    Merge data from multiple sources.
    
    Args:
        sources: Dictionary mapping source names to DataFrames
        on_column: Column to merge on (None for index merge)
        how: Merge method ('inner', 'outer', 'left', 'right')
        
    Returns:
        Merged DataFrame
    """
    if not sources:
        return pd.DataFrame()
    
    # Start with first DataFrame
    source_names = list(sources.keys())
    merged_data = sources[source_names[0]].copy()
    
    # Add source suffix to columns
    if on_column is None:
        merged_data.columns = [f"{col}_{source_names[0]}" for col in merged_data.columns]
    else:
        # Don't rename the merge column
        renamed_cols = {col: f"{col}_{source_names[0]}" for col in merged_data.columns if col != on_column}
        merged_data = merged_data.rename(columns=renamed_cols)
    
    # Merge with subsequent DataFrames
    for source_name in source_names[1:]:
        df = sources[source_name].copy()
        
        # Add source suffix to columns
        if on_column is None:
            df.columns = [f"{col}_{source_name}" for col in df.columns]
            merged_data = merged_data.merge(df, left_index=True, right_index=True, how=how)
        else:
            renamed_cols = {col: f"{col}_{source_name}" for col in df.columns if col != on_column}
            df = df.rename(columns=renamed_cols)
            merged_data = merged_data.merge(df, on=on_column, how=how)
    
    return merged_data

def create_date_range(start_date: str, 
                     end_date: str, 
                     frequency: str = "D",
                     business_days_only: bool = False) -> pd.DatetimeIndex:
    """
    Create a date range for data processing.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        frequency: Frequency string ('D', 'B', 'W', 'M', etc.)
        business_days_only: Whether to include only business days
        
    Returns:
        DatetimeIndex with the date range
    """
    if business_days_only:
        frequency = "B"  # Business days
    
    date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)
    return date_range
