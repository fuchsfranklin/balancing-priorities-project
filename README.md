# Portfolio Optimization Dashboard

**Factor-based portfolio analysis with diversification and Bogleheads principles**

⚠️ **Note**: Original simple analysis overfitted to 2015-2024. See improved factor-based analysis for meaningful results.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys (see docs/SETUP.md)
echo "TIINGO_API_KEY=your_key" > .env

# 3. Download real market data
python scripts/download_real_data.py

# 4. Run factor analysis
python scripts/run_factor_analysis.py

# 5. Launch dashboard
streamlit run dashboard.py
```

**Dashboard**: http://localhost:8501  
**Full Setup Guide**: See [docs/SETUP.md](docs/SETUP.md)  
**Real Data Results**: See [docs/REAL_DATA_RESULTS.md](docs/REAL_DATA_RESULTS.md)

**Alternative** (simulated data):
```bash
python scripts/create_factor_data.py
python scripts/run_factor_analysis.py
```

---

## Repository Structure

```
balancing-priorities-project/
├── blog/                           # R Markdown blog posts
│   └── international-equity-factor-tilts.Rmd
├── data/                           # Market data (CSV files)
│   ├── prices_data.csv
│   └── returns_data.csv
├── docs/                           # Documentation
│   ├── SETUP.md
│   ├── REAL_DATA_RESULTS.md
│   └── API_INTEGRATION.md
├── results/                        # Analysis outputs
│   ├── optimal_portfolios.csv
│   └── strategy_comparison.csv
├── scripts/                        # Python analysis scripts
│   ├── download_real_data.py
│   ├── run_factor_analysis.py
│   └── run_analysis.py
├── dashboard.py                    # Streamlit dashboard
├── requirements.txt                # Python dependencies
├── .env                           # API keys (create this)
└── README.md
```

---

## What This Does

**Two Analyses**:

1. **Simple Analysis** (run_analysis.py): Basic optimization - overfits to recent US outperformance
2. **Factor Analysis** (run_factor_analysis.py): Includes factor premiums, diversification, Bogleheads principles

**Key Findings**:
- Bogleheads 3-Fund: 0.521 Sharpe (well-diversified, simple)
- Momentum Tilt: 0.551 Sharpe (factor premium with diversification)
- Concentrated US: 0.516 Sharpe (period-specific, no diversification)
- Traditional 60/40: 0.628 Sharpe (lower volatility from bonds)

---

## Dashboard Features

### Overview Tab
- Interactive efficient frontier visualization
- Comparison with traditional 60/40 allocation
- Real data from 2015-2024 (2,516 trading days)

### Best Portfolio Tab
- Detailed allocation breakdown
- Performance metrics comparison
- Risk-adjusted return analysis

### Factor Analysis Tab
- Strategy comparison (Bogleheads, 60/40, Factor Tilts)
- Diversification metrics
- DFA/Avantis implementation notes

### Explore Tab
- Interactive 3D portfolio visualization
- Custom filtering by return/risk/Sharpe
- Top 10 portfolios table

### Compare Tab
- Side-by-side portfolio comparison
- Custom portfolio builder
- Visual allocation charts

---

## Blog Post

See `blog/international-equity-factor-tilts.Rmd` for comprehensive analysis of:
- VXUS alternatives
- Factor investing with DFA/Avantis
- International equity allocation strategies

**To generate HTML**:
```r
rmarkdown::render("blog/international-equity-factor-tilts.Rmd")
```

---

## Data Source

**Real market data** from Tiingo API (2015-2024):
- VTI: 13.44% return, 17.99% volatility
- VXUS: 6.51% return, 17.26% volatility
- BND: 1.44% return, 5.44% volatility
- VOO: 13.90% return, 17.80% volatility
- VBR: 10.66% return, 21.36% volatility
- VTV: 10.97% return, 16.84% volatility
- MTUM: 14.40% return, 20.03% volatility

**API Setup**: Create `.env` file with:
```
TIINGO_API_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
```
Get free keys: [Tiingo](https://www.tiingo.com) (1000 req/day), [Alpha Vantage](https://www.alphavantage.co) (25 req/day)

---

## Key Results

| Metric | Traditional 60/40 | Optimized | Improvement |
|--------|-------------------|-----------|-------------|
| Sharpe Ratio | 0.667 | 0.772 | +15.8% |
| Annual Return | 8.0% | 7.7% | -0.3 pp |
| Annual Risk | 12.0% | 10.0% | -2.0 pp |
| Annual Cost | 0.04% | 0.04% | 0.0 pp |

**Optimal Allocation**: 46.5% BND, 21.6% VOO, 15.2% VTI, 8.8% MTUM, 4.3% VTV, 2.5% VXUS, 1.1% VBR

**Interpretation**: The optimized portfolio achieves 15.8% higher risk-adjusted returns through substantial bond allocation (46.5%), prioritizing Sharpe ratio over absolute returns.

---

## Methodology

**Optimization Approach**: Multi-objective optimization simultaneously maximizing return, minimizing risk (volatility), and minimizing cost (expense ratios).

**Process**:
1. Generate 1,000 random portfolio allocations
2. Calculate return, risk, and cost for each
3. Identify Pareto frontier (portfolios where no objective can improve without degrading another)
4. Select top 50 by Sharpe ratio

**Assets**: VTI, VXUS, BND, VOO, VBR, VTV, MTUM

**Data**: 2015-2024 real market data from Tiingo API

---

## Future Enhancement

Factor investing implementation will utilize **Dimensional Fund Advisors (DFA)** and **Avantis** ETFs for:
- Superior factor exposure
- Lower expense ratios (0.15-0.30%)
- Tax efficiency through patient trading
- Academic research-backed methodology

---

## Disclaimer

This analysis is for educational and research purposes only. Past performance does not guarantee future results. The optimized portfolio reflects 2015-2024 market conditions and may not be suitable for all investors or future market environments. Consult a qualified financial advisor before making investment decisions.

## License

MIT License - Free for educational and research use
