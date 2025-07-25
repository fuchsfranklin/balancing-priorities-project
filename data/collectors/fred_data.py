"""
Federal Reserve Economic Data (FRED) collector for economic indicators.

This module provides functionality to download economic data from
the Federal Reserve Bank of St. Louis FRED database.
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from pathlib import Path
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FREDCollector:
    """Collector for FRED economic data."""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    # Common FRED series
    SERIES_INFO = {
        # Interest Rates
        "FEDFUNDS": {
            "name": "Federal Funds Rate",
            "description": "Effective Federal Funds Rate",
            "frequency": "Monthly",
            "units": "Percent"
        },
        "GS10": {
            "name": "10-Year Treasury Rate",
            "description": "10-Year Treasury Constant Maturity Rate",
            "frequency": "Daily",
            "units": "Percent"
        },
        "GS3M": {
            "name": "3-Month Treasury Rate", 
            "description": "3-Month Treasury Constant Maturity Rate",
            "frequency": "Daily",
            "units": "Percent"
        },
        "TB3MS": {
            "name": "3-Month Treasury Bill",
            "description": "3-Month Treasury Bill: Secondary Market Rate",
            "frequency": "Monthly",
            "units": "Percent"
        },
        "GS2": {
            "name": "2-Year Treasury Rate",
            "description": "2-Year Treasury Constant Maturity Rate", 
            "frequency": "Daily",
            "units": "Percent"
        },
        "GS5": {
            "name": "5-Year Treasury Rate",
            "description": "5-Year Treasury Constant Maturity Rate",
            "frequency": "Daily", 
            "units": "Percent"
        },
        "GS30": {
            "name": "30-Year Treasury Rate",
            "description": "30-Year Treasury Constant Maturity Rate",
            "frequency": "Daily",
            "units": "Percent"
        },
        
        # Inflation
        "CPIAUCSL": {
            "name": "CPI All Urban Consumers",
            "description": "Consumer Price Index for All Urban Consumers: All Items",
            "frequency": "Monthly",
            "units": "Index 1982-84=100"
        },
        "CPILFESL": {
            "name": "Core CPI",
            "description": "Consumer Price Index: All Items Less Food & Energy",
            "frequency": "Monthly", 
            "units": "Index 1982-84=100"
        },
        "PCEPI": {
            "name": "PCE Price Index",
            "description": "Personal Consumption Expenditures: Chain-type Price Index",
            "frequency": "Monthly",
            "units": "Index 2012=100"
        },
        
        # Economic Indicators
        "GDP": {
            "name": "Gross Domestic Product",
            "description": "Gross Domestic Product",
            "frequency": "Quarterly",
            "units": "Billions of Dollars"
        },
        "UNRATE": {
            "name": "Unemployment Rate",
            "description": "Unemployment Rate",
            "frequency": "Monthly",
            "units": "Percent"
        },
        "INDPRO": {
            "name": "Industrial Production Index",
            "description": "Industrial Production Index",
            "frequency": "Monthly",
            "units": "Index 2017=100"
        },
        
        # Money Supply
        "M1SL": {
            "name": "M1 Money Stock",
            "description": "M1 Money Stock",
            "frequency": "Monthly",
            "units": "Billions of Dollars"
        },
        "M2SL": {
            "name": "M2 Money Stock",
            "description": "M2 Money Stock", 
            "frequency": "Monthly",
            "units": "Billions of Dollars"
        },
        
        # Market Indicators
        "VIXCLS": {
            "name": "VIX",
            "description": "CBOE Volatility Index: VIX",
            "frequency": "Daily",
            "units": "Index"
        },
        "TEDRATE": {
            "name": "TED Spread",
            "description": "TED Spread",
            "frequency": "Daily",
            "units": "Percent"
        }
    }
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 start_date: str = "1990-01-01",
                 end_date: Optional[str] = None):
        """
        Initialize the FRED collector.
        
        Args:
            api_key: FRED API key (get from https://fred.stlouisfed.org/docs/api/api_key.html)
            start_date: Start date for data collection (YYYY-MM-DD)
            end_date: End date for data collection (YYYY-MM-DD), defaults to today
        """
        self.api_key = api_key
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self._cache: Dict[str, pd.DataFrame] = {}
        
        if not self.api_key:
            logger.warning("No FRED API key provided. Some features may not work.")
    
    def download_series(self, 
                       series_id: str,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       frequency: Optional[str] = None) -> pd.Series:
        """
        Download a single FRED series.
        
        Args:
            series_id: FRED series ID
            start_date: Override start date
            end_date: Override end date  
            frequency: Data frequency (d, w, bw, m, q, sa, a)
            
        Returns:
            Pandas Series with the data
        """
        cache_key = f"{series_id}_{start_date}_{end_date}_{frequency}"
        if cache_key in self._cache:
            logger.info(f"Using cached data for {series_id}")
            return self._cache[cache_key].iloc[:, 0]  # Return as Series
        
        # Use pandas_datareader as fallback if no API key
        if not self.api_key:
            return self._download_with_pandas_datareader(series_id, start_date, end_date)
        
        # Build parameters
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date or self.start_date,
            "observation_end": end_date or self.end_date
        }
        
        if frequency:
            params["frequency"] = frequency
        
        try:
            logger.info(f"Downloading FRED series {series_id}")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "observations" not in data:
                logger.error(f"No observations found for series {series_id}")
                return pd.Series(dtype=float)
            
            observations = data["observations"]
            
            # Convert to DataFrame
            df = pd.DataFrame(observations)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            
            # Convert values to numeric, handling '.' as NaN
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            
            # Clean the data
            series = df["value"].dropna()
            
            # Cache the result
            self._cache[cache_key] = pd.DataFrame(series)
            
            logger.info(f"Downloaded {len(series)} observations for {series_id}")
            return series
            
        except Exception as e:
            logger.error(f"Failed to download FRED series {series_id}: {str(e)}")
            return pd.Series(dtype=float)
    
    def download_multiple_series(self, 
                                series_ids: List[str],
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Download multiple FRED series.
        
        Args:
            series_ids: List of FRED series IDs
            start_date: Override start date
            end_date: Override end date
            
        Returns:
            DataFrame with series as columns
        """
        data = {}
        
        for series_id in series_ids:
            series = self.download_series(series_id, start_date, end_date)
            if not series.empty:
                data[series_id] = series
            time.sleep(0.1)  # Rate limiting
        
        if not data:
            return pd.DataFrame()
        
        # Combine series into DataFrame
        df = pd.DataFrame(data)
        
        # Add descriptive column names if available
        renamed_columns = {}
        for series_id in df.columns:
            if series_id in self.SERIES_INFO:
                renamed_columns[series_id] = f"{series_id} ({self.SERIES_INFO[series_id]['name']})"
        
        if renamed_columns:
            df = df.rename(columns=renamed_columns)
        
        return df
    
    def get_interest_rates(self) -> pd.DataFrame:
        """Get common interest rate series."""
        rate_series = ["FEDFUNDS", "GS3M", "GS2", "GS5", "GS10", "GS30", "TB3MS"]
        return self.download_multiple_series(rate_series)
    
    def get_inflation_data(self) -> pd.DataFrame:
        """Get inflation indicators."""
        inflation_series = ["CPIAUCSL", "CPILFESL", "PCEPI"]
        return self.download_multiple_series(inflation_series)
    
    def get_economic_indicators(self) -> pd.DataFrame:
        """Get key economic indicators."""
        econ_series = ["GDP", "UNRATE", "INDPRO"]
        return self.download_multiple_series(econ_series)
    
    def get_market_indicators(self) -> pd.DataFrame:
        """Get market-related indicators."""
        market_series = ["VIXCLS", "TEDRATE"]
        return self.download_multiple_series(market_series)
    
    def calculate_inflation_rate(self, 
                               price_index: str = "CPIAUCSL",
                               periods: int = 12) -> pd.Series:
        """
        Calculate inflation rate from price index.
        
        Args:
            price_index: FRED series ID for price index
            periods: Number of periods for year-over-year calculation
            
        Returns:
            Series with inflation rates
        """
        price_series = self.download_series(price_index)
        
        if price_series.empty:
            return pd.Series(dtype=float)
        
        # Calculate year-over-year percentage change
        inflation_rate = price_series.pct_change(periods=periods) * 100
        
        return inflation_rate.dropna()
    
    def calculate_real_rate(self, 
                          nominal_rate_series: str = "GS10",
                          inflation_series: str = "CPIAUCSL") -> pd.Series:
        """
        Calculate real interest rate (nominal - inflation).
        
        Args:
            nominal_rate_series: FRED series for nominal rate
            inflation_series: FRED series for inflation
            
        Returns:
            Series with real rates
        """
        nominal_rate = self.download_series(nominal_rate_series)
        inflation_rate = self.calculate_inflation_rate(inflation_series)
        
        # Align data
        aligned = pd.concat([nominal_rate, inflation_rate], axis=1, join='inner')
        aligned.columns = ['nominal_rate', 'inflation_rate']
        
        # Calculate real rate
        real_rate = aligned['nominal_rate'] - aligned['inflation_rate']
        
        return real_rate.dropna()
    
    def get_yield_curve_data(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Get yield curve data for a specific date or latest.
        
        Args:
            date: Specific date (YYYY-MM-DD), or None for latest
            
        Returns:
            DataFrame with yield curve
        """
        maturity_series = {
            "1M": "GS1M",
            "3M": "GS3M", 
            "6M": "GS6M",
            "1Y": "GS1",
            "2Y": "GS2",
            "3Y": "GS3",
            "5Y": "GS5",
            "7Y": "GS7", 
            "10Y": "GS10",
            "20Y": "GS20",
            "30Y": "GS30"
        }
        
        # Download all series
        yield_data = {}
        for maturity, series_id in maturity_series.items():
            series = self.download_series(series_id)
            if not series.empty:
                yield_data[maturity] = series
        
        if not yield_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(yield_data)
        
        if date:
            # Get specific date
            target_date = pd.to_datetime(date)
            if target_date in df.index:
                return df.loc[[target_date]]
            else:
                # Get closest date
                closest_date = df.index[df.index <= target_date].max()
                if pd.notna(closest_date):
                    return df.loc[[closest_date]]
                else:
                    return pd.DataFrame()
        else:
            # Return latest data
            return df.tail(1)
    
    def _download_with_pandas_datareader(self, 
                                       series_id: str,
                                       start_date: Optional[str] = None,
                                       end_date: Optional[str] = None) -> pd.Series:
        """Fallback method using pandas-datareader."""
        try:
            import pandas_datareader.data as web
            
            start = start_date or self.start_date
            end = end_date or self.end_date
            
            logger.info(f"Using pandas-datareader for {series_id}")
            data = web.DataReader(series_id, "fred", start, end)
            
            if isinstance(data, pd.DataFrame) and len(data.columns) == 1:
                return data.iloc[:, 0]
            elif isinstance(data, pd.Series):
                return data
            else:
                logger.warning(f"Unexpected data format for {series_id}")
                return pd.Series(dtype=float)
                
        except Exception as e:
            logger.error(f"pandas-datareader failed for {series_id}: {str(e)}")
            return pd.Series(dtype=float)
    
    def save_data(self, data: Dict[str, pd.DataFrame], filepath: Path, format: str = "csv"):
        """Save FRED data to files."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            for series_name, df in data.items():
                filename = filepath.parent / f"{filepath.stem}_{series_name}.csv"
                df.to_csv(filename)
                logger.info(f"Saved {series_name} data to {filename}")
                
        elif format == "pickle":
            filename = filepath.with_suffix('.pkl')
            pd.to_pickle(data, filename)
            logger.info(f"Saved FRED data to {filename}")
            
        else:
            raise ValueError("format must be 'csv' or 'pickle'")
    
    def load_data(self, filepath: Path, format: str = "pickle") -> Dict[str, pd.DataFrame]:
        """Load previously saved FRED data."""
        if format == "pickle":
            filename = filepath.with_suffix('.pkl')
            if filename.exists():
                data = pd.read_pickle(filename)
                logger.info(f"Loaded FRED data from {filename}")
                return data
        
        logger.warning(f"No data file found at {filepath}")
        return {}

def main():
    """Example usage of FREDCollector."""
    import os
    
    # Initialize collector
    api_key = os.getenv("FRED_API_KEY")  # Set your API key as environment variable
    collector = FREDCollector(api_key=api_key, start_date="2000-01-01")
    
    print("Downloading FRED economic data...")
    
    # Get different types of data
    interest_rates = collector.get_interest_rates()
    inflation_data = collector.get_inflation_data()
    economic_indicators = collector.get_economic_indicators()
    
    print(f"\nInterest Rates: {interest_rates.shape}")
    print("Columns:", interest_rates.columns.tolist())
    
    print(f"\nInflation Data: {inflation_data.shape}")
    print("Columns:", inflation_data.columns.tolist())
    
    print(f"\nEconomic Indicators: {economic_indicators.shape}")
    print("Columns:", economic_indicators.columns.tolist())
    
    # Calculate some derived measures
    inflation_rate = collector.calculate_inflation_rate()
    real_rate = collector.calculate_real_rate()
    
    print(f"\nInflation Rate: {len(inflation_rate)} observations")
    print(f"Latest inflation rate: {inflation_rate.iloc[-1]:.2f}%")
    
    print(f"\nReal Rate: {len(real_rate)} observations") 
    print(f"Latest real rate: {real_rate.iloc[-1]:.2f}%")
    
    # Get latest yield curve
    yield_curve = collector.get_yield_curve_data()
    print(f"\nLatest Yield Curve:")
    print(yield_curve.iloc[0].round(2))
    
    # Save data
    data_dict = {
        "interest_rates": interest_rates,
        "inflation": inflation_data,
        "economic_indicators": economic_indicators
    }
    
    save_path = Path("data/raw/fred_data")
    collector.save_data(data_dict, save_path)

if __name__ == "__main__":
    main()
