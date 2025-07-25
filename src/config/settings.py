"""
Global settings and configuration for the Balancing Priorities Project.

This module contains all the key parameters and settings used throughout
the multi-objective portfolio optimization project.
"""

import os
from pathlib import Path
from datetime import datetime, date

# Project Structure
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

# Data Collection Settings
START_DATE = "1990-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
DEFAULT_FREQUENCY = "M"  # Monthly data

# API Keys and External Data Sources
FRED_API_KEY = os.getenv("FRED_API_KEY", None)
YAHOO_FINANCE_TIMEOUT = 30
MAX_RETRIES = 3

# Risk-Free Rate Settings
RISK_FREE_SYMBOL = "^IRX"  # 3-Month Treasury Bill
RISK_FREE_FRED_SERIES = "TB3MS"  # 3-Month Treasury Bill from FRED

# Fama-French Data URLs
FAMA_FRENCH_BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FAMA_FRENCH_FACTORS = [
    "F-F_Research_Data_Factors",
    "F-F_Research_Data_5_Factors_2x3",
    "Portfolios_Formed_on_Size",
    "Portfolios_Formed_on_BE-ME"
]

# Portfolio Settings
DEFAULT_INITIAL_VALUE = 10000.0  # $10,000 initial portfolio value
REBALANCING_THRESHOLD = 0.05  # 5% threshold for threshold-based rebalancing
MIN_CASH_BUFFER = 0.01  # 1% minimum cash buffer

# Tax Settings (US Federal)
LONG_TERM_CAPITAL_GAINS_RATE = 0.15  # 15% long-term capital gains
SHORT_TERM_CAPITAL_GAINS_RATE = 0.22  # 22% short-term (ordinary income)
QUALIFIED_DIVIDEND_RATE = 0.15  # 15% qualified dividends
ORDINARY_INCOME_RATE = 0.22  # 22% ordinary income
STATE_TAX_RATE = 0.02  # 2% state tax (simplified)

# Transaction Costs
COMMISSION_PER_TRADE = 0.0  # $0 commission (modern brokers)
BID_ASK_SPREAD = 0.0005  # 0.05% bid-ask spread
MARKET_IMPACT = 0.001  # 0.1% market impact for large trades

# Optimization Settings
NSGA2_POPULATION_SIZE = 100
NSGA2_GENERATIONS = 500
NSGA2_CROSSOVER_PROB = 0.9
NSGA2_MUTATION_PROB = 0.1
RANDOM_SEED = 42

# Multi-Objective Reinforcement Learning Settings
MORL_EPISODES = 1000
MORL_STEPS_PER_EPISODE = 252  # Trading days per year
MORL_LEARNING_RATE = 0.001
MORL_DISCOUNT_FACTOR = 0.99

# Simulation Settings
MONTE_CARLO_SIMULATIONS = 1000
BOOTSTRAP_SAMPLES = 1000
CONFIDENCE_LEVELS = [0.05, 0.10, 0.90, 0.95]

# Visualization Settings
FIGURE_SIZE = (12, 8)
DPI = 300
COLOR_PALETTE = "viridis"
PLOTLY_THEME = "plotly_white"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = PROJECT_ROOT / "logs" / f"portfolio_optimization_{datetime.now().strftime('%Y%m%d')}.log"

# Parallel Processing
N_JOBS = -1  # Use all available cores
CHUNK_SIZE = 100

# Data Validation Thresholds
MAX_MISSING_DATA_RATIO = 0.05  # 5% maximum missing data
MIN_CORRELATION_THRESHOLD = -0.1  # Minimum correlation for sanity check
MAX_CORRELATION_THRESHOLD = 0.99  # Maximum correlation to avoid redundancy

# Performance Metrics Preferences
PREFERRED_RISK_METRICS = ["volatility", "max_drawdown", "var_95", "cvar_95"]
PREFERRED_RETURN_METRICS = ["cagr", "total_return", "real_return", "sharpe_ratio"]
PREFERRED_COST_METRICS = ["total_expense_ratio", "tax_drag", "turnover_cost"]

# Report Generation Settings
REPORT_TITLE = "Indexing Through a New Lens: Multi-Objective Portfolio Optimization"
REPORT_SUBTITLE = "Applying Operations Research to the Bogleheads Philosophy"
AUTHOR = "Balancing Priorities Research Team"
REPORT_DATE = datetime.now().strftime("%B %Y")

# Model Persistence
MODEL_SAVE_DIR = PROJECT_ROOT / "models"
RESULTS_SAVE_DIR = PROJECT_ROOT / "results"

def ensure_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR,
        REPORTS_DIR, FIGURES_DIR, TABLES_DIR, MODEL_SAVE_DIR, RESULTS_SAVE_DIR,
        PROJECT_ROOT / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_data_path(filename: str, data_type: str = "processed") -> Path:
    """Get the full path for a data file."""
    data_type_map = {
        "raw": RAW_DATA_DIR,
        "processed": PROCESSED_DATA_DIR,
        "external": EXTERNAL_DATA_DIR
    }
    
    if data_type not in data_type_map:
        raise ValueError(f"Invalid data_type: {data_type}. Must be one of {list(data_type_map.keys())}")
    
    return data_type_map[data_type] / filename

def get_figure_path(filename: str) -> Path:
    """Get the full path for a figure file."""
    return FIGURES_DIR / filename

def get_table_path(filename: str) -> Path:
    """Get the full path for a table file."""
    return TABLES_DIR / filename
