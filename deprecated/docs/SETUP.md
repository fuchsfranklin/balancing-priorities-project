# Setup Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- streamlit (dashboard)
- pandas, numpy (data processing)
- plotly (visualizations)
- python-dotenv (API key management)

## 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# .env
TIINGO_API_KEY=your_tiingo_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

**Get Free API Keys:**

- **Tiingo**: https://www.tiingo.com/account/api/token
  - Limits: 50 req/hour, 1,000 req/day, 2 GB/month
  - Best for daily historical data

- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
  - Limits: 25 req/day
  - Backup option if Tiingo unavailable

**Important**: Never commit `.env` to version control (already in `.gitignore`)

## 3. Download Real Data

```bash
python download_real_data.py
```

This downloads 2015-2024 daily prices for 7 ETFs:
- VTI (US Total Market)
- VXUS (International)
- BND (US Bonds)
- VOO (S&P 500)
- VBR (Small Cap Value)
- VTV (Large Cap Value)
- MTUM (Momentum)

**Rate Limiting**: Script automatically waits 1.2 seconds between requests to stay within Tiingo's 50 req/hour limit.

**Output**: Creates `data/prices_data.csv` and `data/returns_data.csv`

## 4. Run Analysis

**Option A: Factor-Based Analysis (Recommended)**
```bash
python run_factor_analysis.py
```

Compares 5 strategies with diversification metrics and factor premiums.

**Option B: Simple Optimization**
```bash
python run_analysis.py
```

Tests 1,000 random portfolios and finds top 50 by Sharpe ratio.

## 5. Launch Dashboard

```bash
streamlit run dashboard.py
```

Opens at http://localhost:8501

## Alternative: Simulated Data

If API keys unavailable or network blocked:

```bash
python create_factor_data.py
python run_factor_analysis.py
streamlit run dashboard.py
```

Uses calibrated simulation based on real Fama-French factor premiums (1927-2024).

## Troubleshooting

**"No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"TIINGO_API_KEY not found"**
- Ensure `.env` file exists in project root
- Check key is correct (no quotes needed)
- Verify file is named exactly `.env` (not `.env.txt`)

**"HTTP 429" or rate limit errors**
- Wait 1 hour and retry
- Check daily limit not exceeded (1,000 req/day for Tiingo)
- Use simulated data as fallback

**"Corporate network blocking"**
- Try from personal network/device
- Use simulated data (academically valid alternative)

## File Structure After Setup

```
balancing-priorities-project/
├── .env                          # API keys (you create this)
├── .gitignore                    # Prevents committing .env
├── requirements.txt              # Python dependencies
├── download_real_data.py         # Data download script
├── run_factor_analysis.py        # Factor-based optimization
├── run_analysis.py               # Simple optimization
├── dashboard.py                  # Streamlit dashboard
├── data/
│   ├── prices_data.csv          # Daily prices (created by download)
│   └── returns_data.csv         # Daily returns (created by download)
└── results/
    ├── strategy_comparison.csv   # Strategy metrics
    └── optimal_portfolios.csv    # Top portfolios
```
