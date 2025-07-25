"""
Fama-French data collector for factor returns and research data.

This module provides functionality to download factor data from
Kenneth French's data library at Dartmouth.
"""

import pandas as pd
import numpy as np
import requests
import zipfile
import io
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FamaFrenchCollector:
    """Collector for Fama-French factor data."""
    
    BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    
    # Available datasets
    DATASETS = {
        "3_factors": "F-F_Research_Data_Factors_CSV.zip",
        "5_factors": "F-F_Research_Data_5_Factors_2x3_CSV.zip", 
        "momentum": "F-F_Momentum_Factor_CSV.zip",
        "size_portfolios": "Portfolios_Formed_on_Size_CSV.zip",
        "value_portfolios": "Portfolios_Formed_on_BE-ME_CSV.zip",
        "industry_portfolios": "10_Industry_Portfolios_CSV.zip",
        "international_3_factors": "Developed_3_Factors_CSV.zip",
        "emerging_3_factors": "Emerging_3_Factors_CSV.zip"
    }
    
    def __init__(self, start_date: str = "1990-01-01", end_date: Optional[str] = None):
        """
        Initialize the Fama-French collector.
        
        Args:
            start_date: Start date for data collection (YYYY-MM-DD)
            end_date: End date for data collection (YYYY-MM-DD), defaults to today
        """
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date) if end_date else pd.to_datetime(datetime.now())
        self._cache: Dict[str, pd.DataFrame] = {}
    
    def download_dataset(self, dataset_name: str) -> pd.DataFrame:
        """
        Download a specific Fama-French dataset.
        
        Args:
            dataset_name: Name of the dataset (see DATASETS keys)
            
        Returns:
            DataFrame with the factor data
        """
        if dataset_name in self._cache:
            logger.info(f"Using cached data for {dataset_name}")
            return self._cache[dataset_name].copy()
        
        if dataset_name not in self.DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(self.DATASETS.keys())}")
        
        url = self.BASE_URL + self.DATASETS[dataset_name]
        
        try:
            logger.info(f"Downloading {dataset_name} from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.CSV')]
                if not csv_files:
                    raise ValueError(f"No CSV file found in {dataset_name}")
                
                csv_content = zip_file.read(csv_files[0]).decode('utf-8')
            
            # Parse the CSV content
            data = self._parse_fama_french_csv(csv_content, dataset_name)
            
            # Filter by date range
            data = self._filter_by_date_range(data)
            
            # Cache the data
            self._cache[dataset_name] = data.copy()
            
            logger.info(f"Successfully downloaded {dataset_name}: {data.shape[0]} records, {data.shape[1]} columns")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_three_factor_data(self) -> pd.DataFrame:
        """
        Get the classic Fama-French 3-factor data (Market, SMB, HML).
        
        Returns:
            DataFrame with Mkt-RF, SMB, HML, and RF columns
        """
        return self.download_dataset("3_factors")
    
    def get_five_factor_data(self) -> pd.DataFrame:
        """
        Get the Fama-French 5-factor data (Market, SMB, HML, RMW, CMA).
        
        Returns:
            DataFrame with Mkt-RF, SMB, HML, RMW, CMA, and RF columns
        """
        return self.download_dataset("5_factors")
    
    def get_momentum_data(self) -> pd.DataFrame:
        """
        Get momentum factor data.
        
        Returns:
            DataFrame with momentum factor
        """
        return self.download_dataset("momentum")
    
    def get_size_portfolios(self) -> pd.DataFrame:
        """
        Get size-sorted portfolio returns.
        
        Returns:
            DataFrame with size portfolio returns
        """
        return self.download_dataset("size_portfolios")
    
    def get_value_portfolios(self) -> pd.DataFrame:
        """
        Get value-sorted portfolio returns.
        
        Returns:
            DataFrame with value portfolio returns
        """
        return self.download_dataset("value_portfolios")
    
    def get_industry_portfolios(self) -> pd.DataFrame:
        """
        Get industry portfolio returns.
        
        Returns:
            DataFrame with industry portfolio returns
        """
        return self.download_dataset("industry_portfolios")
    
    def get_international_factors(self, region: str = "developed") -> pd.DataFrame:
        """
        Get international factor data.
        
        Args:
            region: 'developed' or 'emerging'
            
        Returns:
            DataFrame with international factor data
        """
        if region == "developed":
            return self.download_dataset("international_3_factors")
        elif region == "emerging":
            return self.download_dataset("emerging_3_factors")
        else:
            raise ValueError("region must be 'developed' or 'emerging'")
    
    def calculate_factor_loadings(self, 
                                returns: pd.Series, 
                                factors: pd.DataFrame,
                                model: str = "3_factor") -> Dict[str, float]:
        """
        Calculate factor loadings for a return series.
        
        Args:
            returns: Series of portfolio/asset returns
            factors: DataFrame with factor returns
            model: Type of model ('3_factor', '5_factor', 'momentum')
            
        Returns:
            Dictionary with factor loadings and statistics
        """
        # Align data
        aligned_data = pd.concat([returns, factors], axis=1, join='inner')
        aligned_data = aligned_data.dropna()
        
        if len(aligned_data) < 24:  # Need at least 2 years of monthly data
            logger.warning("Insufficient data for factor regression")
            return {}
        
        # Define dependent and independent variables
        y = aligned_data.iloc[:, 0]  # Returns
        
        if model == "3_factor":
            if all(col in aligned_data.columns for col in ['Mkt-RF', 'SMB', 'HML']):
                X = aligned_data[['Mkt-RF', 'SMB', 'HML']]
            else:
                logger.error("Required 3-factor columns not found")
                return {}
        elif model == "5_factor":
            required_cols = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
            if all(col in aligned_data.columns for col in required_cols):
                X = aligned_data[required_cols]
            else:
                logger.error("Required 5-factor columns not found")
                return {}
        else:
            raise ValueError("model must be '3_factor' or '5_factor'")
        
        # Add constant for alpha
        X = X.copy()
        X.insert(0, 'Alpha', 1.0)
        
        # Run regression
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score
            
            reg = LinearRegression(fit_intercept=False)  # We already added constant
            reg.fit(X, y)
            
            # Calculate statistics
            y_pred = reg.predict(X)
            r_squared = r2_score(y, y_pred)
            
            # Build results
            results = {
                'alpha': reg.coef_[0],
                'r_squared': r_squared,
                'observations': len(y)
            }
            
            # Add factor loadings
            factor_names = X.columns[1:]  # Skip Alpha
            for i, factor in enumerate(factor_names):
                results[factor.lower() + '_loading'] = reg.coef_[i + 1]
            
            return results
            
        except Exception as e:
            logger.error(f"Factor regression failed: {str(e)}")
            return {}
    
    def _parse_fama_french_csv(self, csv_content: str, dataset_name: str) -> pd.DataFrame:
        """Parse Fama-French CSV format."""
        lines = csv_content.strip().split('\n')
        
        # Find the data section
        data_start = 0
        for i, line in enumerate(lines):
            if re.match(r'^\d{6}', line.strip()):  # Format: YYYYMM
                data_start = i
                break
        
        if data_start == 0:
            # Try alternative date formats
            for i, line in enumerate(lines):
                if re.match(r'^\d{4}', line.strip()):  # Format: YYYY
                    data_start = i
                    break
        
        # Find where data ends (usually indicated by empty line or annual data)
        data_end = len(lines)
        for i in range(data_start + 1, len(lines)):
            line = lines[i].strip()
            if not line or 'Annual' in line or 'Copyright' in line:
                data_end = i
                break
        
        # Extract header
        if data_start > 0:
            header_line = lines[data_start - 1]
            headers = [col.strip() for col in header_line.split(',')]
        else:
            # Guess headers based on dataset
            headers = self._get_default_headers(dataset_name)
        
        # Parse data lines
        data_rows = []
        for i in range(data_start, data_end):
            line = lines[i].strip()
            if line and re.match(r'^\d{4}', line):
                row = [col.strip() for col in line.split(',')]
                if len(row) >= len(headers):
                    data_rows.append(row[:len(headers)])
        
        if not data_rows:
            logger.warning(f"No data rows found for {dataset_name}")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Parse date column
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], format='%Y%m', errors='coerce')
        
        # Convert to numeric (except date column)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Set date as index
        df.set_index(date_col, inplace=True)
        
        # Convert percentages to decimals
        df = df / 100.0
        
        return df
    
    def _get_default_headers(self, dataset_name: str) -> List[str]:
        """Get default headers for datasets."""
        if dataset_name == "3_factors":
            return ["Date", "Mkt-RF", "SMB", "HML", "RF"]
        elif dataset_name == "5_factors":
            return ["Date", "Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]
        elif dataset_name == "momentum":
            return ["Date", "Mom"]
        elif dataset_name == "size_portfolios":
            return ["Date", "Lo 10", "Dec 2", "Dec 3", "Dec 4", "Dec 5", 
                   "Dec 6", "Dec 7", "Dec 8", "Dec 9", "Hi 10"]
        elif dataset_name == "value_portfolios":
            return ["Date", "Lo 10", "Dec 2", "Dec 3", "Dec 4", "Dec 5", 
                   "Dec 6", "Dec 7", "Dec 8", "Dec 9", "Hi 10"]
        elif dataset_name == "industry_portfolios":
            return ["Date", "NoDur", "Durbl", "Manuf", "Enrgy", "HiTec", 
                   "Telcm", "Shops", "Hlth", "Utils", "Other"]
        else:
            return ["Date", "Factor1", "Factor2", "Factor3"]
    
    def _filter_by_date_range(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter data by specified date range."""
        if data.empty:
            return data
        
        # Filter by date range
        mask = (data.index >= self.start_date) & (data.index <= self.end_date)
        return data.loc[mask]
    
    def save_data(self, data: Dict[str, pd.DataFrame], filepath: Path, format: str = "csv"):
        """
        Save Fama-French data to files.
        
        Args:
            data: Dictionary mapping dataset names to DataFrames
            filepath: Base filepath
            format: File format ('csv', 'parquet', 'pickle')
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            for dataset, df in data.items():
                filename = filepath.parent / f"{filepath.stem}_{dataset}.csv"
                df.to_csv(filename)
                logger.info(f"Saved {dataset} data to {filename}")
                
        elif format == "pickle":
            filename = filepath.with_suffix('.pkl')
            pd.to_pickle(data, filename)
            logger.info(f"Saved Fama-French data to {filename}")
            
        else:
            raise ValueError("format must be 'csv' or 'pickle'")
    
    def load_data(self, filepath: Path, format: str = "pickle") -> Dict[str, pd.DataFrame]:
        """Load previously saved Fama-French data."""
        if format == "pickle":
            filename = filepath.with_suffix('.pkl')
            if filename.exists():
                data = pd.read_pickle(filename)
                logger.info(f"Loaded Fama-French data from {filename}")
                return data
        
        logger.warning(f"No data file found at {filepath}")
        return {}

def main():
    """Example usage of FamaFrenchCollector."""
    
    # Initialize collector
    collector = FamaFrenchCollector(start_date="2000-01-01")
    
    # Download factor data
    print("Downloading Fama-French factor data...")
    
    three_factor = collector.get_three_factor_data()
    five_factor = collector.get_five_factor_data()
    momentum = collector.get_momentum_data()
    
    # Display summary
    print(f"\n3-Factor data: {three_factor.shape}")
    print(f"Period: {three_factor.index[0]} to {three_factor.index[-1]}")
    print("Columns:", three_factor.columns.tolist())
    
    print(f"\n5-Factor data: {five_factor.shape}")
    print("Columns:", five_factor.columns.tolist())
    
    print(f"\nMomentum data: {momentum.shape}")
    print("Columns:", momentum.columns.tolist())
    
    # Show summary statistics
    print("\n3-Factor Summary Statistics (annualized %):")
    print((three_factor * 12 * 100).describe().round(2))
    
    # Save data
    data_dict = {
        "3_factors": three_factor,
        "5_factors": five_factor,
        "momentum": momentum
    }
    
    save_path = Path("data/raw/fama_french_data")
    collector.save_data(data_dict, save_path)

if __name__ == "__main__":
    main()
