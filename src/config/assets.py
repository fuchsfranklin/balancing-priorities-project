"""
Asset universe definitions for the portfolio optimization project.

This module defines the assets, ETFs, and indices that will be used
in the multi-objective optimization analysis.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class AssetClass(Enum):
    """Asset class enumeration."""
    US_EQUITY = "US_Equity"
    INTERNATIONAL_EQUITY = "International_Equity"
    EMERGING_MARKETS = "Emerging_Markets"
    US_BONDS = "US_Bonds"
    INTERNATIONAL_BONDS = "International_Bonds"
    REAL_ESTATE = "Real_Estate"
    COMMODITIES = "Commodities"
    CASH = "Cash"

class AssetType(Enum):
    """Asset type enumeration."""
    ETF = "ETF"
    MUTUAL_FUND = "Mutual_Fund"
    INDEX = "Index"
    FACTOR = "Factor"

@dataclass
class Asset:
    """Asset definition with metadata."""
    symbol: str
    name: str
    asset_class: AssetClass
    asset_type: AssetType
    expense_ratio: float
    inception_date: str
    description: str
    yahoo_symbol: Optional[str] = None
    fred_symbol: Optional[str] = None
    
    def __post_init__(self):
        if self.yahoo_symbol is None:
            self.yahoo_symbol = self.symbol

# Core Index Funds (Vanguard ETFs)
CORE_ASSETS = {
    # US Equity
    "VTI": Asset(
        symbol="VTI",
        name="Vanguard Total Stock Market ETF",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0003,  # 0.03%
        inception_date="2001-05-24",
        description="Tracks the CRSP US Total Market Index"
    ),
    
    "VOO": Asset(
        symbol="VOO",
        name="Vanguard S&P 500 ETF",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0003,  # 0.03%
        inception_date="2010-09-07",
        description="Tracks the S&P 500 Index"
    ),
    
    # International Equity
    "VXUS": Asset(
        symbol="VXUS",
        name="Vanguard Total International Stock ETF",
        asset_class=AssetClass.INTERNATIONAL_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0008,  # 0.08%
        inception_date="2011-01-26",
        description="Tracks the FTSE Global All Cap ex US Index"
    ),
    
    "VTIAX": Asset(
        symbol="VTIAX",
        name="Vanguard Total International Stock Index Fund",
        asset_class=AssetClass.INTERNATIONAL_EQUITY,
        asset_type=AssetType.MUTUAL_FUND,
        expense_ratio=0.0011,  # 0.11%
        inception_date="2010-11-29",
        description="Admiral Shares of Total International Stock Index"
    ),
    
    # Bonds
    "BND": Asset(
        symbol="BND",
        name="Vanguard Total Bond Market ETF",
        asset_class=AssetClass.US_BONDS,
        asset_type=AssetType.ETF,
        expense_ratio=0.0003,  # 0.03%
        inception_date="2007-04-03",
        description="Tracks the Bloomberg US Aggregate Float Adjusted Index"
    ),
    
    "BNDX": Asset(
        symbol="BNDX",
        name="Vanguard Total International Bond ETF",
        asset_class=AssetClass.INTERNATIONAL_BONDS,
        asset_type=AssetType.ETF,
        expense_ratio=0.0007,  # 0.07%
        inception_date="2013-05-31",
        description="Tracks the Bloomberg Global Aggregate ex-USD Float Adjusted RIC Capped Index"
    ),
}

# Factor Tilts (Small-Cap Value)
FACTOR_ASSETS = {
    "VBR": Asset(
        symbol="VBR",
        name="Vanguard Small-Cap Value ETF",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0007,  # 0.07%
        inception_date="2004-01-26",
        description="Tracks the CRSP US Small Cap Value Index"
    ),
    
    "VTV": Asset(
        symbol="VTV",
        name="Vanguard Value ETF",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0004,  # 0.04%
        inception_date="2004-01-26",
        description="Tracks the CRSP US Large Cap Value Index"
    ),
    
    "VSS": Asset(
        symbol="VSS",
        name="Vanguard FTSE All-World ex-US Small-Cap ETF",
        asset_class=AssetClass.INTERNATIONAL_EQUITY,
        asset_type=AssetType.ETF,
        expense_ratio=0.0011,  # 0.11%
        inception_date="2009-04-02",
        description="Tracks the FTSE Global Small Cap ex US Index"
    ),
}

# Bond Duration Varieties
BOND_DURATION_ASSETS = {
    "VGSH": Asset(
        symbol="VGSH",
        name="Vanguard Short-Term Treasury ETF",
        asset_class=AssetClass.US_BONDS,
        asset_type=AssetType.ETF,
        expense_ratio=0.0007,  # 0.07%
        inception_date="2009-11-19",
        description="Tracks the Bloomberg US Treasury 1-3 Year Index"
    ),
    
    "VGIT": Asset(
        symbol="VGIT",
        name="Vanguard Intermediate-Term Treasury ETF",
        asset_class=AssetClass.US_BONDS,
        asset_type=AssetType.ETF,
        expense_ratio=0.0007,  # 0.07%
        inception_date="2009-11-19",
        description="Tracks the Bloomberg US Treasury 3-10 Year Index"
    ),
    
    "VGLT": Asset(
        symbol="VGLT",
        name="Vanguard Long-Term Treasury ETF",
        asset_class=AssetClass.US_BONDS,
        asset_type=AssetType.ETF,
        expense_ratio=0.0007,  # 0.07%
        inception_date="2009-11-19",
        description="Tracks the Bloomberg US Treasury 10+ Year Index"
    ),
}

# Market Indices for Benchmarking
BENCHMARK_INDICES = {
    "SP500": Asset(
        symbol="^GSPC",
        name="S&P 500 Index",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.INDEX,
        expense_ratio=0.0,
        inception_date="1957-03-04",
        description="Standard & Poor's 500 Index",
        yahoo_symbol="^GSPC"
    ),
    
    "NASDAQ": Asset(
        symbol="^IXIC",
        name="NASDAQ Composite Index",
        asset_class=AssetClass.US_EQUITY,
        asset_type=AssetType.INDEX,
        expense_ratio=0.0,
        inception_date="1971-02-05",
        description="NASDAQ Composite Index",
        yahoo_symbol="^IXIC"
    ),
    
    "TREASURY_10Y": Asset(
        symbol="^TNX",
        name="10-Year Treasury Yield",
        asset_class=AssetClass.US_BONDS,
        asset_type=AssetType.INDEX,
        expense_ratio=0.0,
        inception_date="1962-01-02",
        description="10-Year Treasury Note Yield",
        yahoo_symbol="^TNX",
        fred_symbol="GS10"
    ),
}

# Complete asset universe
ALL_ASSETS = {**CORE_ASSETS, **FACTOR_ASSETS, **BOND_DURATION_ASSETS, **BENCHMARK_INDICES}

# Pre-defined portfolio templates
PORTFOLIO_TEMPLATES = {
    "three_fund": {
        "name": "Three-Fund Portfolio",
        "description": "Classic Bogleheads three-fund portfolio",
        "assets": ["VTI", "VXUS", "BND"],
        "default_weights": [0.60, 0.30, 0.10]  # 60% US, 30% Intl, 10% Bonds
    },
    
    "two_fund_simple": {
        "name": "Two-Fund Simple",
        "description": "US stocks and bonds only",
        "assets": ["VTI", "BND"],
        "default_weights": [0.70, 0.30]  # 70% stocks, 30% bonds
    },
    
    "global_equity_bond": {
        "name": "Global Equity/Bond",
        "description": "Global diversification with bonds",
        "assets": ["VTI", "VXUS", "BND", "BNDX"],
        "default_weights": [0.40, 0.30, 0.20, 0.10]
    },
    
    "factor_tilt": {
        "name": "Factor Tilt Portfolio",
        "description": "Small-cap value tilt with international",
        "assets": ["VTI", "VBR", "VXUS", "BND"],
        "default_weights": [0.40, 0.20, 0.25, 0.15]
    },
    
    "bond_duration_diversified": {
        "name": "Bond Duration Diversified",
        "description": "Diversified across bond durations",
        "assets": ["VTI", "VXUS", "VGSH", "VGIT", "VGLT"],
        "default_weights": [0.50, 0.20, 0.10, 0.10, 0.10]
    }
}

# Asset class constraints for optimization
ASSET_CLASS_CONSTRAINTS = {
    AssetClass.US_EQUITY: {"min": 0.0, "max": 1.0},
    AssetClass.INTERNATIONAL_EQUITY: {"min": 0.0, "max": 0.5},
    AssetClass.US_BONDS: {"min": 0.0, "max": 0.5},
    AssetClass.INTERNATIONAL_BONDS: {"min": 0.0, "max": 0.2},
    AssetClass.REAL_ESTATE: {"min": 0.0, "max": 0.1},
    AssetClass.COMMODITIES: {"min": 0.0, "max": 0.1}
}

def get_assets_by_class(asset_class: AssetClass) -> Dict[str, Asset]:
    """Get all assets of a specific asset class."""
    return {symbol: asset for symbol, asset in ALL_ASSETS.items() 
            if asset.asset_class == asset_class}

def get_core_universe() -> List[str]:
    """Get the core asset universe for optimization."""
    return list(CORE_ASSETS.keys())

def get_expanded_universe() -> List[str]:
    """Get the expanded asset universe including factors."""
    return list(CORE_ASSETS.keys()) + list(FACTOR_ASSETS.keys())

def get_bond_duration_universe() -> List[str]:
    """Get assets for bond duration analysis."""
    return ["VTI", "VXUS"] + list(BOND_DURATION_ASSETS.keys())

def validate_portfolio_weights(assets: List[str], weights: List[float]) -> bool:
    """Validate that portfolio weights sum to 1 and are non-negative."""
    if len(assets) != len(weights):
        return False
    
    if abs(sum(weights) - 1.0) > 1e-6:
        return False
    
    if any(w < 0 for w in weights):
        return False
    
    return True
