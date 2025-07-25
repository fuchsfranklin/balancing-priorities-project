"""
Yahoo Finance data collector for ETF and index data.

This module provides functionality to download historical price data,
dividends, and other financial information from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceCollector:
    """Collector for Yahoo Finance data."""
    
    def __init__(self, 
                 start_date: str = "1990-01-01",
                 end_date: Optional[str] = None,
                 auto_adjust: bool = True,
                 prepost: bool = False,
                 threads: bool = True):
        """
        Initialize the Yahoo Finance collector.
        
        Args:
            start_date: Start date for data collection (YYYY-MM-DD)
            end_date: End date for data collection (YYYY-MM-DD), defaults to today
            auto_adjust: Whether to auto-adjust prices for splits and dividends
            prepost: Include pre and post market data
            threads: Use threading for faster downloads
        """
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.auto_adjust = auto_adjust
        self.prepost = prepost
        self.threads = threads
        
        # Cache for downloaded data
        self._cache: Dict[str, pd.DataFrame] = {}
        
    def download_symbol(self, 
                       symbol: str, 
                       period: str = "max",
                       interval: str = "1d",
                       retry_count: int = 3) -> pd.DataFrame:
        """
        Download data for a single symbol.
        
        Args:
            symbol: Yahoo Finance symbol
            period: Period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            retry_count: Number of retries on failure
            
        Returns:
            DataFrame with OHLCV data
        """
        if symbol in self._cache:
            logger.info(f"Using cached data for {symbol}")
            return self._cache[symbol].copy()
        
        for attempt in range(retry_count):
            try:
                ticker = yf.Ticker(symbol)
                
                # Download historical data
                if period == "max":
                    data = ticker.history(
                        start=self.start_date,
                        end=self.end_date,
                        auto_adjust=self.auto_adjust,
                        prepost=self.prepost,
                        threads=self.threads,
                        interval=interval
                    )
                else:
                    data = ticker.history(
                        period=period,
                        interval=interval,
                        auto_adjust=self.auto_adjust,
                        prepost=self.prepost,
                        threads=self.threads
                    )
                
                if data.empty:
                    logger.warning(f"No data found for symbol {symbol}")
                    return pd.DataFrame()
                
                # Clean the data
                data = self._clean_data(data, symbol)
                
                # Cache the data
                self._cache[symbol] = data.copy()
                
                logger.info(f"Successfully downloaded {len(data)} records for {symbol}")
                return data
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to download data for {symbol} after {retry_count} attempts")
                    return pd.DataFrame()
    
    def download_multiple(self, 
                          symbols: List[str], 
                          period: str = "max",
                          interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple symbols.
        
        Args:
            symbols: List of Yahoo Finance symbols
            period: Period to download
            interval: Data interval
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        # Try bulk download first (faster)
        try:
            tickers = yf.Tickers(" ".join(symbols))
            
            if period == "max":
                bulk_data = tickers.history(
                    start=self.start_date,
                    end=self.end_date,
                    auto_adjust=self.auto_adjust,
                    prepost=self.prepost,
                    threads=self.threads,
                    interval=interval
                )
            else:
                bulk_data = tickers.history(
                    period=period,
                    interval=interval,
                    auto_adjust=self.auto_adjust,
                    prepost=self.prepost,
                    threads=self.threads
                )
            
            # Split bulk data by symbol
            for symbol in symbols:
                try:
                    if isinstance(bulk_data.columns, pd.MultiIndex):
                        symbol_data = bulk_data.xs(symbol, level=1, axis=1)
                    else:
                        symbol_data = bulk_data
                    
                    if not symbol_data.empty:
                        symbol_data = self._clean_data(symbol_data, symbol)
                        results[symbol] = symbol_data
                        self._cache[symbol] = symbol_data.copy()
                    
                except Exception as e:
                    logger.warning(f"Failed to extract data for {symbol} from bulk download: {str(e)}")
            
            logger.info(f"Bulk download successful for {len(results)} out of {len(symbols)} symbols")
            
        except Exception as e:
            logger.warning(f"Bulk download failed: {str(e)}. Falling back to individual downloads.")
        
        # Download individually for any missing symbols
        missing_symbols = [s for s in symbols if s not in results]
        for symbol in missing_symbols:
            data = self.download_symbol(symbol, period, interval)
            if not data.empty:
                results[symbol] = data
        
        return results
    
    def get_returns(self, 
                   symbols: Union[str, List[str]], 
                   return_type: str = "simple",
                   frequency: str = "daily") -> pd.DataFrame:
        """
        Calculate returns for given symbols.
        
        Args:
            symbols: Symbol or list of symbols
            return_type: Type of returns ('simple', 'log')
            frequency: Return frequency ('daily', 'monthly', 'quarterly', 'annual')
            
        Returns:
            DataFrame with returns
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        # Download price data
        price_data = {}
        for symbol in symbols:
            data = self.download_symbol(symbol)
            if not data.empty:
                price_data[symbol] = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
        
        if not price_data:
            return pd.DataFrame()
        
        # Combine into single DataFrame
        prices_df = pd.DataFrame(price_data)
        
        # Calculate returns
        if return_type == "simple":
            returns = prices_df.pct_change()
        elif return_type == "log":
            returns = np.log(prices_df / prices_df.shift(1))
        else:
            raise ValueError("return_type must be 'simple' or 'log'")
        
        # Adjust frequency if needed
        if frequency != "daily":
            returns = self._resample_returns(returns, frequency)
        
        # Drop NaN values
        returns = returns.dropna()
        
        return returns
    
    def get_dividends(self, symbols: Union[str, List[str]]) -> pd.DataFrame:
        """
        Get dividend data for symbols.
        
        Args:
            symbols: Symbol or list of symbols
            
        Returns:
            DataFrame with dividend data
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        dividend_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                dividends = ticker.dividends
                
                if not dividends.empty:
                    # Filter by date range
                    start = pd.to_datetime(self.start_date)
                    end = pd.to_datetime(self.end_date)
                    dividends = dividends[(dividends.index >= start) & (dividends.index <= end)]
                    dividend_data[symbol] = dividends
                
            except Exception as e:
                logger.warning(f"Failed to get dividends for {symbol}: {str(e)}")
        
        if not dividend_data:
            return pd.DataFrame()
        
        # Combine into single DataFrame
        dividends_df = pd.DataFrame(dividend_data)
        dividends_df = dividends_df.fillna(0)
        
        return dividends_df
    
    def get_info(self, symbol: str) -> Dict:
        """
        Get basic information about a symbol.
        
        Args:
            symbol: Yahoo Finance symbol
            
        Returns:
            Dictionary with symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            logger.error(f"Failed to get info for {symbol}: {str(e)}")
            return {}
    
    def _clean_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Clean and validate downloaded data."""
        if data.empty:
            return data
        
        # Remove timezone info if present
        if hasattr(data.index, 'tz') and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Sort by date
        data = data.sort_index()
        
        # Remove duplicates
        data = data[~data.index.duplicated(keep='last')]
        
        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Validate data quality
        if len(data) == 0:
            logger.warning(f"No valid data after cleaning for {symbol}")
            return pd.DataFrame()
        
        # Check for reasonable price ranges (basic sanity check)
        if 'Close' in data.columns:
            if (data['Close'] <= 0).any():
                logger.warning(f"Found non-positive prices for {symbol}")
                data = data[data['Close'] > 0]
        
        return data
    
    def _resample_returns(self, returns: pd.DataFrame, frequency: str) -> pd.DataFrame:
        """Resample returns to different frequencies."""
        if frequency == "monthly":
            # Compound daily returns to monthly
            monthly_returns = (1 + returns).resample('M').prod() - 1
            return monthly_returns
        elif frequency == "quarterly":
            quarterly_returns = (1 + returns).resample('Q').prod() - 1
            return quarterly_returns
        elif frequency == "annual":
            annual_returns = (1 + returns).resample('A').prod() - 1
            return annual_returns
        else:
            return returns
    
    def save_data(self, data: Dict[str, pd.DataFrame], filepath: Path, format: str = "csv"):
        """
        Save downloaded data to files.
        
        Args:
            data: Dictionary mapping symbols to DataFrames
            filepath: Base filepath (without extension)
            format: File format ('csv', 'parquet', 'pickle')
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            for symbol, df in data.items():
                filename = filepath.parent / f"{filepath.stem}_{symbol}.csv"
                df.to_csv(filename)
                logger.info(f"Saved {symbol} data to {filename}")
                
        elif format == "parquet":
            # Save as single parquet file with MultiIndex columns
            if data:
                combined_data = pd.concat(data, axis=1, keys=data.keys())
                filename = filepath.with_suffix('.parquet')
                combined_data.to_parquet(filename)
                logger.info(f"Saved combined data to {filename}")
                
        elif format == "pickle":
            filename = filepath.with_suffix('.pkl')
            pd.to_pickle(data, filename)
            logger.info(f"Saved data dictionary to {filename}")
            
        else:
            raise ValueError("format must be 'csv', 'parquet', or 'pickle'")
    
    def load_data(self, filepath: Path, format: str = "pickle") -> Dict[str, pd.DataFrame]:
        """
        Load previously saved data.
        
        Args:
            filepath: Path to data file
            format: File format ('csv', 'parquet', 'pickle')
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        if format == "pickle":
            filename = filepath.with_suffix('.pkl')
            if filename.exists():
                data = pd.read_pickle(filename)
                logger.info(f"Loaded data from {filename}")
                return data
            
        elif format == "parquet":
            filename = filepath.with_suffix('.parquet')
            if filename.exists():
                combined_data = pd.read_parquet(filename)
                # Split back into individual DataFrames
                data = {}
                for symbol in combined_data.columns.levels[0]:
                    data[symbol] = combined_data[symbol]
                logger.info(f"Loaded data from {filename}")
                return data
        
        logger.warning(f"No data file found at {filepath}")
        return {}

def main():
    """Example usage of YahooFinanceCollector."""
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from src.config.assets import get_core_universe
    
    # Initialize collector
    collector = YahooFinanceCollector(start_date="2010-01-01")
    
    # Get core assets
    symbols = get_core_universe()
    print(f"Downloading data for: {symbols}")
    
    # Download data
    data = collector.download_multiple(symbols)
    
    # Calculate returns
    returns = collector.get_returns(symbols, frequency="monthly")
    
    # Display summary
    print("\nData Summary:")
    for symbol, df in data.items():
        print(f"{symbol}: {len(df)} records from {df.index[0]} to {df.index[-1]}")
    
    print(f"\nReturns shape: {returns.shape}")
    print(f"Returns period: {returns.index[0]} to {returns.index[-1]}")
    
    # Save data
    save_path = Path("data/raw/yahoo_finance_data")
    collector.save_data(data, save_path, format="pickle")

if __name__ == "__main__":
    main()
