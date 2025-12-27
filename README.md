# Pure Indexing, Flirting with Factor Tilts, and Finding Intermediaries

A blog post exploring index fund inefficiencies and DFA/Avantis alternatives to the traditional three-fund portfolio.

## Read the Post

**[blog/index.md](blog/index.md)** — Full blog post with analysis, code, and visualizations

## Overview

This post examines whether Dimensional Fund Advisors (DFA) ETFs can serve as improved replacements for traditional index funds like VTI and VXUS, without fully committing to factor investing.

**Key Points:**
- **DFUS, accounting for REITs, is equivalent to VTI**: Same factor exposure, ~1% CAGR advantage from implementation improvements
- **DFAX and other alternatives are not equivalent VXUS**: DFAX has meaningful factor tilts (+0.21 HML, +0.21 RMW, +0.17 SMB)
- **No "VXUS 2.0"**: No single DFA/Avantis ETF replicates VXUS without factor tilts

## Repository Structure

```
├── blog/
│   ├── index.md                      # Main blog post
│   ├── vti_vxus_mix_comparison.py    # US vs International mix analysis
│   ├── vti_dfus_comparison.py        # VTI vs DFUS comparison
│   ├── vxus_dfax_comparison.py       # VXUS vs DFAX comparison
│   ├── factor_regression_analysis.py # Fama-French 5-factor regressions
│   └── *.png                         # Generated visualizations
├── data/
│   ├── prices_data.csv               # ETF price data (from Tiingo API)
│   ├── F-F_Research_Data_5_Factors_2x3.csv    # US factors
│   ├── Developed_ex_US_5_Factors.csv          # Developed ex-US factors
│   └── Emerging_5_Factors.csv                 # Emerging market factors
├── deprecated/                       # Original portfolio dashboard project
├── .env                              # API keys (not committed)
├── requirements.txt                  # Python dependencies
└── README.md
```

## Data Sources

- **ETF Prices**: [Tiingo API](https://www.tiingo.com/) — Historical end-of-day prices
- **Factor Returns**: [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) — Fama-French 5-factor data

## Running the Analysis Yourself

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "TIINGO_API_KEY=your_key" > .env

# Run any analysis script
python blog/factor_regression_analysis.py
```

## License

MIT License, Free for educational and research use

## Disclaimer

This analysis is for educational purposes only. Not financial advice. Past performance does not guarantee future results.
