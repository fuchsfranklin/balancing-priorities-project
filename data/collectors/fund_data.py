"""
Fund data collector for expense ratios and fund metadata.

This module provides functionality to collect fund information,
expense ratios, and other metadata for ETFs and mutual funds.
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import json
import time
import logging
from pathlib import Path
from dataclasses import asdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundDataCollector:
    """Collector for fund data and metadata."""
    
    def __init__(self):
        """Initialize the fund data collector."""
        self._cache: Dict[str, Dict] = {}
        
        # Common headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_vanguard_fund_info(self, symbol: str) -> Dict:
        """
        Get Vanguard fund information from their website.
        
        Args:
            symbol: Fund symbol (e.g., VTI, VXUS)
            
        Returns:
            Dictionary with fund information
        """
        if symbol in self._cache:
            logger.info(f"Using cached data for {symbol}")
            return self._cache[symbol]
        
        # Vanguard URL format
        url = f"https://investor.vanguard.com/investment-products/etfs/profile/{symbol}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            fund_info = {
                'symbol': symbol,
                'fund_family': 'Vanguard',
                'expense_ratio': self._extract_vanguard_expense_ratio(soup),
                'net_assets': self._extract_vanguard_net_assets(soup),
                'inception_date': self._extract_vanguard_inception_date(soup),
                'fund_name': self._extract_vanguard_fund_name(soup),
                'category': self._extract_vanguard_category(soup),
                'benchmark': self._extract_vanguard_benchmark(soup),
                'minimum_investment': self._extract_vanguard_minimum(soup),
                'dividend_yield': self._extract_vanguard_dividend_yield(soup)
            }
            
            # Cache the result
            self._cache[symbol] = fund_info
            
            logger.info(f"Successfully retrieved Vanguard info for {symbol}")
            return fund_info
            
        except Exception as e:
            logger.error(f"Failed to get Vanguard info for {symbol}: {str(e)}")
            return self._get_fallback_fund_info(symbol)
    
    def get_morningstar_fund_info(self, symbol: str) -> Dict:
        """
        Get fund information from Morningstar (basic public data).
        
        Args:
            symbol: Fund symbol
            
        Returns:
            Dictionary with fund information
        """
        # This is a simplified version - full Morningstar API requires subscription
        try:
            # Try to get basic info from Yahoo Finance first
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                fund_info = {
                    'symbol': symbol,
                    'fund_name': info.get('longName', ''),
                    'expense_ratio': info.get('annualReportExpenseRatio', None),
                    'net_assets': info.get('totalAssets', None),
                    'category': info.get('category', ''),
                    'fund_family': info.get('fundFamily', ''),
                    'yield': info.get('yield', None),
                    'beta': info.get('beta', None),
                    'morningstar_rating': info.get('morningstarRiskRating', None)
                }
                
                # Convert expense ratio from decimal to percentage if needed
                if fund_info['expense_ratio'] and fund_info['expense_ratio'] < 0.1:
                    fund_info['expense_ratio'] = fund_info['expense_ratio'] * 100
                
                return fund_info
            
        except Exception as e:
            logger.warning(f"Failed to get Morningstar/Yahoo info for {symbol}: {str(e)}")
        
        return self._get_fallback_fund_info(symbol)
    
    def get_comprehensive_fund_info(self, symbol: str) -> Dict:
        """
        Get comprehensive fund information from multiple sources.
        
        Args:
            symbol: Fund symbol
            
        Returns:
            Dictionary with comprehensive fund information
        """
        # Known expense ratios for common ETFs (as reliable fallback)
        known_expense_ratios = {
            'VTI': 0.03,    # Total Stock Market ETF
            'VOO': 0.03,    # S&P 500 ETF
            'VXUS': 0.08,   # Total International Stock ETF
            'VTIAX': 0.11,  # Total International Stock Index (Admiral)
            'BND': 0.035,   # Total Bond Market ETF
            'BNDX': 0.06,   # Total International Bond ETF
            'VBR': 0.07,    # Small-Cap Value ETF
            'VTV': 0.04,    # Value ETF
            'VSS': 0.09,    # FTSE All-World ex-US Small-Cap ETF
            'VGSH': 0.035,  # Short-Term Treasury ETF
            'VGIT': 0.04,   # Intermediate-Term Treasury ETF
            'VGLT': 0.045,  # Long-Term Treasury ETF
            'SPY': 0.095,   # SPDR S&P 500 ETF
            'QQQ': 0.20,    # Invesco QQQ Trust
            'IWM': 0.19,    # iShares Russell 2000 ETF
            'EFA': 0.32,    # iShares MSCI EAFE ETF
            'EEM': 0.68,    # iShares MSCI Emerging Markets ETF
            'AGG': 0.04,    # iShares Core U.S. Aggregate Bond ETF
            'TLT': 0.15,    # iShares 20+ Year Treasury Bond ETF
            'GLD': 0.40,    # SPDR Gold Shares
            'VNQ': 0.12     # Vanguard Real Estate ETF
        }
        
        # Start with known data if available
        comprehensive_info = {
            'symbol': symbol,
            'fund_name': f"{symbol} Fund",
            'expense_ratio': known_expense_ratios.get(symbol, None),
            'fund_family': 'Vanguard' if symbol.startswith('V') or symbol in ['BND', 'BNDX'] else 'Unknown',
            'net_assets': None,
            'category': 'Index Fund',
            'data_source': 'known_data' if symbol in known_expense_ratios else 'unknown'
        }
        
        # Try to get more detailed info from yfinance
        try:
            import yfinance as yf
            
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info
            
            if info:
                # Update with yfinance data where available
                if info.get('longName'):
                    comprehensive_info['fund_name'] = info['longName']
                if info.get('fundFamily'):
                    comprehensive_info['fund_family'] = info['fundFamily']
                if info.get('totalAssets'):
                    comprehensive_info['net_assets'] = info['totalAssets']
                if info.get('category'):
                    comprehensive_info['category'] = info['category']
                
                # Try to extract expense ratio from yfinance
                yf_expense_ratio = self._extract_expense_ratio_from_yfinance(info)
                if yf_expense_ratio is not None:
                    comprehensive_info['expense_ratio'] = yf_expense_ratio
                    comprehensive_info['data_source'] = 'yfinance'
                
                logger.info(f"Enhanced {symbol} data with yfinance")
                
        except Exception as e:
            logger.warning(f"Failed to get yfinance data for {symbol}: {str(e)}")
        
        # Try Vanguard website for additional details (for Vanguard funds only)
        if symbol.startswith('V') or symbol in ['BND', 'BNDX']:
            try:
                vanguard_info = self.get_vanguard_fund_info(symbol)
                if vanguard_info.get('expense_ratio') is not None:
                    comprehensive_info['expense_ratio'] = vanguard_info['expense_ratio']
                    comprehensive_info['data_source'] = 'vanguard_website'
                
                # Update other fields from Vanguard if better
                for key in ['fund_name', 'net_assets', 'category']:
                    if vanguard_info.get(key):
                        comprehensive_info[key] = vanguard_info[key]
                        
                logger.info(f"Enhanced {symbol} data with Vanguard website")
                
            except Exception as e:
                logger.warning(f"Failed to get Vanguard data for {symbol}: {str(e)}")
        
        # Add calculated fields
        comprehensive_info['last_updated'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        return comprehensive_info
    
    def _extract_expense_ratio_from_yfinance(self, info: Dict) -> Optional[float]:
        """Extract expense ratio from yfinance info dictionary."""
        try:
            # Try various field names that might contain expense ratio
            expense_fields = [
                'annualReportExpenseRatio',
                'expenseRatio', 
                'totalExpenseRatio',
                'managementFee',
                'annualHoldingsTurnover'
            ]
            
            for field in expense_fields:
                value = info.get(field)
                if value is not None:
                    # Convert to percentage if it's in decimal form
                    if isinstance(value, (int, float)):
                        if value > 1:  # Assume it's already in percentage
                            return float(value)
                        else:  # Assume it's in decimal form, convert to percentage
                            return float(value * 100)
                    elif isinstance(value, str):
                        # Try to extract number from string
                        import re
                        match = re.search(r'(\d+\.?\d*)', value)
                        if match:
                            return float(match.group(1))
            
        except Exception as e:
            logger.warning(f"Failed to extract expense ratio from yfinance: {str(e)}")
        
        return None
    
    def get_fund_expense_ratios(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get expense ratios for multiple funds.
        
        Args:
            symbols: List of fund symbols
            
        Returns:
            DataFrame with expense ratios
        """
        expense_data = []
        
        for symbol in symbols:
            fund_info = self.get_comprehensive_fund_info(symbol)
            
            expense_data.append({
                'symbol': symbol,
                'fund_name': fund_info.get('fund_name', ''),
                'expense_ratio': fund_info.get('expense_ratio', None),
                'fund_family': fund_info.get('fund_family', ''),
                'net_assets': fund_info.get('net_assets', None)
            })
            
            time.sleep(0.5)  # Rate limiting
        
        df = pd.DataFrame(expense_data)
        
        # Clean expense ratio data
        df['expense_ratio'] = pd.to_numeric(df['expense_ratio'], errors='coerce')
        
        return df
    
    def get_tax_efficiency_data(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get tax efficiency metrics for funds (simplified version).
        
        Args:
            symbols: List of fund symbols
            
        Returns:
            DataFrame with tax efficiency metrics
        """
        tax_data = []
        
        for symbol in symbols:
            fund_info = self.get_comprehensive_fund_info(symbol)
            
            # Estimate tax efficiency based on fund type
            tax_efficiency = self._estimate_tax_efficiency(symbol, fund_info)
            
            tax_data.append({
                'symbol': symbol,
                'fund_name': fund_info.get('fund_name', ''),
                'estimated_tax_efficiency': tax_efficiency,
                'turnover_ratio': fund_info.get('turnover_ratio', None),
                'dividend_yield': fund_info.get('dividend_yield', None)
            })
        
        return pd.DataFrame(tax_data)
    
    def _extract_vanguard_expense_ratio(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract expense ratio from Vanguard page."""
        try:
            # Look for expense ratio in various possible locations
            expense_patterns = [
                "expense ratio",
                "annual operating expenses",
                "total annual operating expenses"
            ]
            
            for pattern in expense_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text.lower())
                for element in elements:
                    # Look for percentage in nearby text
                    parent = element.parent
                    if parent:
                        text = parent.get_text()
                        # Extract percentage using regex
                        import re
                        match = re.search(r'(\d+\.?\d*)\s*%', text)
                        if match:
                            return float(match.group(1))
            
        except Exception as e:
            logger.warning(f"Failed to extract Vanguard expense ratio: {str(e)}")
        
        return None
    
    def _extract_vanguard_net_assets(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract net assets from Vanguard page."""
        try:
            # Look for net assets
            asset_elements = soup.find_all(text=lambda text: text and "net assets" in text.lower())
            for element in asset_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    # Look for dollar amounts
                    import re
                    match = re.search(r'\$[\d,.]+ (billion|million|trillion)', text, re.IGNORECASE)
                    if match:
                        return match.group(0)
        except Exception:
            pass
        
        return None
    
    def _extract_vanguard_inception_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract inception date from Vanguard page."""
        try:
            # Look for inception date
            inception_elements = soup.find_all(text=lambda text: text and "inception" in text.lower())
            for element in inception_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    # Look for dates
                    import re
                    match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', text)
                    if match:
                        return match.group(0)
        except Exception:
            pass
        
        return None
    
    def _extract_vanguard_fund_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund name from Vanguard page."""
        try:
            # Look for title or h1 tag
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text()
                # Clean up the title
                if '|' in title:
                    return title.split('|')[0].strip()
                return title.strip()
        except Exception:
            pass
        
        return None
    
    def _extract_vanguard_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund category from Vanguard page."""
        # Simplified - would need more sophisticated parsing
        return None
    
    def _extract_vanguard_benchmark(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract benchmark from Vanguard page."""
        try:
            benchmark_elements = soup.find_all(text=lambda text: text and "benchmark" in text.lower())
            for element in benchmark_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    # Extract the benchmark name (simplified)
                    lines = text.split('\n')
                    for line in lines:
                        if 'index' in line.lower() and len(line) < 100:
                            return line.strip()
        except Exception:
            pass
        
        return None
    
    def _extract_vanguard_minimum(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract minimum investment from Vanguard page."""
        try:
            min_elements = soup.find_all(text=lambda text: text and "minimum" in text.lower())
            for element in min_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    import re
                    match = re.search(r'\$[\d,]+', text)
                    if match:
                        return match.group(0)
        except Exception:
            pass
        
        return None
    
    def _extract_vanguard_dividend_yield(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract dividend yield from Vanguard page."""
        try:
            yield_elements = soup.find_all(text=lambda text: text and "yield" in text.lower())
            for element in yield_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    import re
                    match = re.search(r'(\d+\.?\d*)\s*%', text)
                    if match:
                        return float(match.group(1))
        except Exception:
            pass
        
        return None
    
    def _get_fallback_fund_info(self, symbol: str) -> Dict:
        """Get fallback fund information from predefined data."""
        from ..config.assets import ALL_ASSETS
        
        if symbol in ALL_ASSETS:
            asset = ALL_ASSETS[symbol]
            return {
                'symbol': symbol,
                'fund_name': asset.name,
                'expense_ratio': asset.expense_ratio * 100,  # Convert to percentage
                'inception_date': asset.inception_date,
                'fund_family': 'Vanguard' if symbol.startswith('V') else 'Unknown',
                'asset_class': asset.asset_class.value,
                'data_source': 'Predefined'
            }
        
        # Absolute fallback
        return {
            'symbol': symbol,
            'fund_name': f'Unknown Fund ({symbol})',
            'expense_ratio': None,
            'data_source': 'Fallback'
        }
    
    def _estimate_tax_efficiency(self, symbol: str, fund_info: Dict) -> str:
        """Estimate tax efficiency based on fund characteristics."""
        # Simple heuristic based on fund type
        if 'bond' in fund_info.get('fund_name', '').lower():
            return 'Low'  # Bonds are tax-inefficient
        elif 'index' in fund_info.get('fund_name', '').lower():
            return 'High'  # Index funds are generally tax-efficient
        elif symbol.startswith('V'):  # Vanguard funds
            return 'High'  # Vanguard known for tax efficiency
        else:
            return 'Medium'
    
    def create_fund_database(self, symbols: List[str]) -> pd.DataFrame:
        """
        Create a comprehensive fund database.
        
        Args:
            symbols: List of fund symbols
            
        Returns:
            DataFrame with comprehensive fund data
        """
        fund_data = []
        
        for symbol in symbols:
            logger.info(f"Processing fund data for {symbol}")
            
            fund_info = self.get_comprehensive_fund_info(symbol)
            fund_data.append(fund_info)
            
            time.sleep(1)  # Rate limiting
        
        df = pd.DataFrame(fund_data)
        
        # Clean and standardize data types
        numeric_columns = ['expense_ratio', 'dividend_yield', 'yield', 'beta']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def save_fund_data(self, data: pd.DataFrame, filepath: Path, format: str = "csv"):
        """Save fund data to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            filename = filepath.with_suffix('.csv')
            data.to_csv(filename, index=False)
            logger.info(f"Saved fund data to {filename}")
            
        elif format == "json":
            filename = filepath.with_suffix('.json')
            data.to_json(filename, orient='records', indent=2)
            logger.info(f"Saved fund data to {filename}")
            
        elif format == "pickle":
            filename = filepath.with_suffix('.pkl')
            data.to_pickle(filename)
            logger.info(f"Saved fund data to {filename}")
            
        else:
            raise ValueError("format must be 'csv', 'json', or 'pickle'")
    
    def load_fund_data(self, filepath: Path, format: str = "csv") -> pd.DataFrame:
        """Load previously saved fund data."""
        if format == "csv":
            filename = filepath.with_suffix('.csv')
            if filename.exists():
                data = pd.read_csv(filename)
                logger.info(f"Loaded fund data from {filename}")
                return data
                
        elif format == "pickle":
            filename = filepath.with_suffix('.pkl')
            if filename.exists():
                data = pd.read_pickle(filename)
                logger.info(f"Loaded fund data from {filename}")
                return data
        
        logger.warning(f"No fund data file found at {filepath}")
        return pd.DataFrame()

def main():
    """Example usage of FundDataCollector."""
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from src.config.assets import get_core_universe
    
    # Initialize collector
    collector = FundDataCollector()
    
    # Get core fund symbols
    symbols = get_core_universe()
    print(f"Collecting fund data for: {symbols}")
    
    # Get expense ratios
    expense_ratios = collector.get_fund_expense_ratios(symbols[:3])  # Test with first 3
    print("\nExpense Ratios:")
    print(expense_ratios)
    
    # Create fund database
    print("\nCreating fund database...")
    fund_db = collector.create_fund_database(symbols[:2])  # Test with first 2
    print(fund_db)
    
    # Save data
    save_path = Path("data/raw/fund_data")
    collector.save_fund_data(fund_db, save_path)

if __name__ == "__main__":
    main()
