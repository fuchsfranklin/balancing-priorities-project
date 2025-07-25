# Development Plan: Multi-Objective Portfolio Optimization

## Project Overview Summary

This project applies multi-objective optimization to validate and enhance the Bogleheads investment philosophy using:
- **Decision Variables**: Asset allocation, diversification, rebalancing frequency, bond duration, factor tilts, asset location
- **Objectives**: Maximize returns, minimize risk, minimize costs
- **Methods**: NSGA-II evolutionary algorithm, optional Multi-Objective Reinforcement Learning (MORL)
- **Data**: Yahoo Finance, Fama-French, FRED, fund literature
- **Output**: Pareto-efficient frontier analysis with publication-grade report

## Repository Structure

```
balancing-priorities-project/
├── README.md                          # Main project description (UNCHANGED)
├── DEVELOPMENT_PLAN.md               # This file
├── requirements.txt                   # Python dependencies
├── environment.yml                    # Conda environment specification
├── 
├── data/                             # Data collection and storage
│   ├── raw/                          # Raw downloaded data
│   ├── processed/                    # Cleaned and processed datasets
│   ├── external/                     # External data sources
│   └── collectors/                   # Data collection scripts
│       ├── __init__.py
│       ├── yahoo_finance.py          # Yahoo Finance data collection
│       ├── fama_french.py           # Fama-French factor data
│       ├── fred_data.py             # Federal Reserve data
│       └── fund_data.py             # Fund expense ratios and metadata
│
├── src/                             # Core source code
│   ├── __init__.py
│   ├── config/                      # Configuration files
│   │   ├── __init__.py
│   │   ├── settings.py              # Global settings and parameters
│   │   ├── assets.py                # Asset universe definitions
│   │   └── constraints.py           # Optimization constraints
│   │
│   ├── portfolio/                   # Portfolio construction and management
│   │   ├── __init__.py
│   │   ├── portfolio.py             # Portfolio class and basic operations
│   │   ├── rebalancing.py           # Rebalancing strategies and logic
│   │   ├── tax_efficiency.py        # Tax calculations and asset location
│   │   └── costs.py                 # Cost calculations (fees, taxes, trading)
│   │
│   ├── optimization/                # Multi-objective optimization algorithms
│   │   ├── __init__.py
│   │   ├── nsga2.py                 # NSGA-II implementation
│   │   ├── objectives.py            # Objective function definitions
│   │   ├── constraints.py           # Constraint definitions
│   │   └── morl/                    # Multi-Objective Reinforcement Learning
│   │       ├── __init__.py
│   │       ├── environment.py       # RL environment for portfolio management
│   │       ├── agents.py            # MORL agents
│   │       └── policies.py          # Policy implementations
│   │
│   ├── simulation/                  # Backtesting and simulation
│   │   ├── __init__.py
│   │   ├── backtest.py              # Main backtesting engine
│   │   ├── monte_carlo.py           # Monte Carlo simulations
│   │   ├── metrics.py               # Performance metrics calculation
│   │   └── validation.py            # Out-of-sample validation
│   │
│   ├── analysis/                    # Analysis and visualization
│   │   ├── __init__.py
│   │   ├── pareto_analysis.py       # Pareto frontier analysis
│   │   ├── sensitivity.py           # Sensitivity analysis
│   │   ├── comparison.py            # Portfolio comparison tools
│   │   └── visualization.py         # Plotting and visualization utilities
│   │
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── data_utils.py            # Data processing utilities
│       ├── math_utils.py            # Mathematical utilities
│       └── logging_utils.py         # Logging configuration
│
├── notebooks/                       # Jupyter notebooks for analysis
│   ├── 01_data_exploration.ipynb    # Initial data exploration
│   ├── 02_portfolio_basics.ipynb    # Basic portfolio analysis
│   ├── 03_optimization_nsga2.ipynb  # NSGA-II optimization
│   ├── 04_morl_experiments.ipynb    # MORL experiments (optional)
│   ├── 05_backtesting.ipynb         # Comprehensive backtesting
│   ├── 06_pareto_analysis.ipynb     # Pareto frontier analysis
│   ├── 07_visualizations.ipynb      # Final visualizations
│   └── 08_report_generation.ipynb   # Generate final report
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_portfolio.py
│   ├── test_optimization.py
│   ├── test_simulation.py
│   └── test_data_collectors.py
│
├── reports/                         # Generated reports and outputs
│   ├── figures/                     # Generated plots and charts
│   ├── tables/                      # Generated data tables
│   ├── final_report.md             # Main report output
│   └── technical_appendix.md       # Technical details
│
├── scripts/                         # Standalone scripts
│   ├── run_full_analysis.py         # Main execution script
│   ├── update_data.py               # Data update script
│   └── generate_report.py           # Report generation script
│
└── docs/                           # Documentation
    ├── methodology.md               # Detailed methodology
    ├── api_reference.md            # API documentation
    └── user_guide.md               # User guide for running analysis
```

## Phase 1: Project Setup and Infrastructure

### 1.1 Environment Setup
- [ ] Create Python virtual environment
- [ ] Install core dependencies (pandas, numpy, scipy, matplotlib, seaborn)
- [ ] Install optimization libraries (DEAP, platypus-opt)
- [ ] Install data libraries (yfinance, pandas-datareader)
- [ ] Install optional ML libraries (gym, stable-baselines3) for MORL
- [ ] Set up Jupyter notebook environment

### 1.2 Repository Structure
- [ ] Create directory structure as outlined above
- [ ] Initialize git repository with proper .gitignore
- [ ] Create requirements.txt and environment.yml
- [ ] Set up basic logging configuration
- [ ] Create initial configuration files

### 1.3 Core Classes and Interfaces
- [ ] Design Portfolio class interface
- [ ] Design Optimizer interface
- [ ] Design Backtester interface
- [ ] Create basic data models for assets, returns, costs

## Phase 2: Data Collection and Processing

### 2.1 Data Collectors Implementation
- [ ] **Yahoo Finance Collector** (`data/collectors/yahoo_finance.py`)
  - ETF data: VTI, VXUS, BND, BNDX, VBR, VTV, etc.
  - Index data: S&P 500, FTSE Developed ex-US, Bloomberg Aggregate Bond
  - Daily/monthly returns, dividends, prices
  - Date range: 1990-present (or as available)

- [ ] **Fama-French Data Collector** (`data/collectors/fama_french.py`)
  - Market, SMB (Small Minus Big), HML (High Minus Low) factors
  - Risk-free rate data
  - International factors if needed

- [ ] **FRED Data Collector** (`data/collectors/fred_data.py`)
  - 10-year Treasury rates
  - Inflation data (CPI)
  - Short-term rates for bond modeling

- [ ] **Fund Data Collector** (`data/collectors/fund_data.py`)
  - Expense ratios for major index funds
  - Fund inception dates
  - Tax efficiency data

### 2.2 Data Processing Pipeline
- [ ] Data cleaning and validation
- [ ] Return calculation (including dividends)
- [ ] Risk-free rate alignment
- [ ] Missing data handling
- [ ] Data quality checks and validation

### 2.3 Initial Data Exploration
- [ ] Create `01_data_exploration.ipynb`
- [ ] Visualize historical returns and correlations
- [ ] Analyze risk-return characteristics
- [ ] Examine factor premiums (size, value)
- [ ] Document data quality and coverage

## Phase 3: Core Portfolio Engine 

### 3.1 Portfolio Class Implementation
- [ ] **Portfolio Class** (`src/portfolio/portfolio.py`)
  - Asset weights and allocations
  - Return calculation methods
  - Risk metrics (volatility, VaR, max drawdown)
  - Cost calculation integration
  - Rebalancing logic

- [ ] **Cost Calculator** (`src/portfolio/costs.py`)
  - Expense ratio calculations
  - Transaction cost modeling
  - Tax impact calculations (capital gains, dividends)
  - Total cost of ownership metrics

- [ ] **Tax Efficiency Module** (`src/portfolio/tax_efficiency.py`)
  - Asset location optimization
  - Tax-adjusted return calculations
  - Tax-loss harvesting simulation
  - Account type considerations (taxable vs. tax-advantaged)

- [ ] **Rebalancing Strategies** (`src/portfolio/rebalancing.py`)
  - Periodic rebalancing (monthly, quarterly, annual)
  - Threshold-based rebalancing
  - Tax-aware rebalancing
  - Cost-minimizing rebalancing

### 3.2 Basic Portfolio Analysis
- [ ] Create `02_portfolio_basics.ipynb`
- [ ] Implement classic efficient frontier
- [ ] Test portfolio construction with simple allocations
- [ ] Validate cost and tax calculations
- [ ] Compare against known benchmarks

## Phase 4: Multi-Objective Optimization Engine

### 4.1 Objective Functions
- [ ] **Return Maximization** (`src/optimization/objectives.py`)
  - CAGR calculation
  - Risk-adjusted return metrics
  - Real return calculations

- [ ] **Risk Minimization**
  - Portfolio volatility (standard deviation)
  - Maximum drawdown
  - Conditional Value at Risk (CVaR)
  - Downside deviation

- [ ] **Cost Minimization**
  - Total expense ratio
  - Trading costs
  - Tax drag
  - Combined cost metric

### 4.2 NSGA-II Implementation
- [ ] **NSGA-II Algorithm** (`src/optimization/nsga2.py`)
  - Multi-objective genetic algorithm
  - Pareto ranking and crowding distance
  - Crossover and mutation operators for portfolio weights
  - Constraint handling (weights sum to 1, non-negative)
  - Convergence criteria and stopping conditions

- [ ] **Constraint System** (`src/optimization/constraints.py`)
  - Weight constraints (sum to 1, bounds)
  - Practical constraints (max number of funds)
  - Asset class minimum/maximum allocations
  - Rebalancing frequency constraints

### 4.3 Optimization Testing
- [ ] Create `03_optimization_nsga2.ipynb`
- [ ] Test NSGA-II on simple problems
- [ ] Validate Pareto frontier generation
- [ ] Parameter sensitivity analysis
- [ ] Convergence analysis

## Phase 5: Backtesting and Simulation 

### 5.1 Backtesting Engine
- [ ] **Backtest Framework** (`src/simulation/backtest.py`)
  - Historical simulation with rebalancing
  - Transaction cost integration
  - Tax impact modeling
  - Multiple time period analysis
  - Rolling window optimization

- [ ] **Performance Metrics** (`src/simulation/metrics.py`)
  - Returns: CAGR, total return, real return
  - Risk: volatility, Sharpe ratio, max drawdown, VaR
  - Costs: total expense ratio, tax drag, turnover
  - Combined metrics: risk-adjusted after-tax returns

### 5.2 Validation Framework
- [ ] **Out-of-Sample Testing** (`src/simulation/validation.py`)
  - Train/test split for optimization
  - Walk-forward analysis
  - Regime-based validation
  - Robustness testing

- [ ] **Monte Carlo Analysis** (`src/simulation/monte_carlo.py`)
  - Bootstrap resampling of returns
  - Alternative market scenarios
  - Stress testing
  - Confidence intervals for metrics

### 5.3 Comprehensive Backtesting
- [ ] Create `05_backtesting.ipynb`
- [ ] Full historical analysis (1990-2024)
- [ ] Multiple optimization periods
- [ ] Comparison with benchmark portfolios
- [ ] Sensitivity to parameters

## Phase 6: Analysis and Visualization

### 6.1 Pareto Frontier Analysis
- [ ] **Pareto Analysis Tools** (`src/analysis/pareto_analysis.py`)
  - Pareto frontier visualization
  - Portfolio comparison tools
  - Trade-off quantification
  - Efficient portfolio identification

- [ ] **Sensitivity Analysis** (`src/analysis/sensitivity.py`)
  - Parameter sensitivity
  - Market regime sensitivity
  - Time period sensitivity
  - Assumption sensitivity

### 6.2 Visualization Suite
- [ ] **Visualization Tools** (`src/analysis/visualization.py`)
  - 3D Pareto frontier plots
  - Efficient frontier curves
  - Portfolio allocation heatmaps
  - Performance comparison charts
  - Risk-return scatter plots

### 6.3 Portfolio Comparison
- [ ] **Comparison Framework** (`src/analysis/comparison.py`)
  - Benchmark portfolio definitions
  - Performance attribution
  - Statistical significance testing
  - Practical significance assessment

### 6.4 Final Analysis
- [ ] Create `06_pareto_analysis.ipynb`
- [ ] Generate all key visualizations in `07_visualizations.ipynb`
- [ ] Comprehensive portfolio comparison
- [ ] Statistical validation of results

## Phase 7: Report Generation and Documentation

### 7.1 Automated Report Generation
- [ ] **Report Generator** (`scripts/generate_report.py`)
  - Automated figure generation
  - Table compilation
  - Statistical summary generation
  - LaTeX/Markdown report compilation

### 7.2 Final Report
- [ ] Create `08_report_generation.ipynb`
- [ ] Generate `reports/final_report.md`
- [ ] Create `reports/technical_appendix.md`
- [ ] Generate executive summary

### 7.3 Documentation
- [ ] Complete API documentation
- [ ] User guide for running analysis
- [ ] Methodology documentation
- [ ] Code comments and docstrings

## Phase 8: Testing and Validation

### 8.1 Unit Testing
- [ ] Test data collection modules
- [ ] Test portfolio calculations
- [ ] Test optimization algorithms
- [ ] Test backtesting engine
- [ ] Test visualization functions

### 8.2 Integration Testing
- [ ] End-to-end pipeline testing
- [ ] Cross-validation of results
- [ ] Performance benchmarking
- [ ] Memory and runtime optimization

### 8.3 Reproducibility
- [ ] Ensure deterministic results
- [ ] Document random seeds
- [ ] Version control for data
- [ ] Docker containerization (optional)

## Key Deliverables

### Technical Outputs
1. **Multi-Objective Optimization Engine**: Complete NSGA-II implementation for portfolio optimization
2. **Comprehensive Backtesting Framework**: Historical simulation with costs and taxes
3. **Pareto Frontier Analysis**: Trade-off visualization and analysis tools
4. **MORL Implementation** (Phase 9 - optional enhancement): Dynamic portfolio allocation using reinforcement learning

### Research Outputs
1. **Publication-Grade Report**: Comprehensive analysis validating Bogleheads philosophy
2. **Interactive Visualizations**: 3D Pareto frontiers, efficient frontier plots
3. **Portfolio Recommendations**: Data-driven optimal allocations
4. **Sensitivity Analysis**: Robustness of results to assumptions

### Open Source Contribution
1. **Reproducible Research**: Complete code for replication
2. **Extensible Framework**: Modular design for future research
3. **Educational Resource**: Clear documentation and examples
4. **Real-Time Updates**: Framework for ongoing analysis

## Expected Timeline

- **Weeks 1-2**: Setup and data collection
- **Weeks 3-4**: Core portfolio engine
- **Weeks 4-5**: Optimization algorithms
- **Week 7**: Backtesting and simulation
- **Week 8**: Analysis and visualization
- **Week 9**: Report generation
- **Week 10**: Testing and validation
- **Future Enhancement**: Advanced methods (MORL) - optional

## Risk Mitigation

### Technical Risks
- **Data Quality**: Multiple data sources and validation
- **Optimization Convergence**: Parameter tuning and algorithm selection
- **Computational Complexity**: Efficient implementation and parallel processing

### Research Risks
- **Overfitting**: Out-of-sample validation and robustness testing
- **Market Regime Changes**: Multiple time periods and scenario analysis
- **Assumption Sensitivity**: Comprehensive sensitivity analysis

## Success Metrics

1. **Technical Success**: Working optimization pipeline with reproducible results
2. **Research Success**: Clear validation or refinement of Bogleheads principles
3. **Practical Success**: Actionable portfolio recommendations
4. **Academic Success**: Publication-quality analysis and methodology

This development plan provides a comprehensive roadmap for implementing the multi-objective portfolio optimization project while maintaining the integrity of the original research vision outlined in the README.
