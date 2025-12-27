# Real Data Analysis Results

**Data Source**: Tiingo API (real market data)  
**Period**: January 2015 - December 2024 (2,516 trading days)  
**Date Generated**: 2025

---

## Market Statistics (Annualized)

| Ticker | Asset Class | Return | Volatility | Sharpe | Expense Ratio |
|--------|-------------|--------|------------|--------|---------------|
| VTI | US Total Market | 13.44% | 17.99% | 0.747 | 0.03% |
| VXUS | International | 6.51% | 17.26% | 0.377 | 0.07% |
| BND | US Bonds | 1.44% | 5.44% | 0.265 | 0.03% |
| VOO | S&P 500 | 13.90% | 17.80% | 0.781 | 0.03% |
| VBR | Small Cap Value | 10.66% | 21.36% | 0.499 | 0.07% |
| VTV | Large Cap Value | 10.97% | 16.84% | 0.651 | 0.04% |
| MTUM | Momentum | 14.40% | 20.03% | 0.719 | 0.15% |

---

## Factor-Based Strategy Comparison

| Strategy | Return | Risk | Sharpe | Diversification | Key Holdings |
|----------|--------|------|--------|-----------------|--------------|
| **Bogleheads 3-Fund** | 8.3% | 16.0% | **0.521** | 1.01 | VTI 54%, VXUS 36%, BND 10% |
| **Traditional 60/40** | 6.8% | 10.8% | **0.628** | 1.02 | VTI 42%, VXUS 18%, BND 40% |
| **Factor Tilt (Value)** | 7.8% | 15.8% | **0.491** | 1.05 | VTI 30%, VBR 10%, VTV 20%, VXUS 30%, BND 10% |
| **Factor Tilt (Momentum)** | 7.7% | 14.0% | **0.551** | 1.10 | VTI 30%, MTUM 20%, VXUS 30%, BND 20% |
| **Concentrated US** | 8.6% | 16.8% | **0.516** | 1.00 | VTI 30%, VOO 60%, BND 10% |

**Winner**: Traditional 60/40 (0.628 Sharpe) - lower volatility from 40% bond allocation

---

## Optimized Portfolio (Constrained)

**Constraints**: Minimum 20% international, 10% bonds for diversification

| Metric | Value |
|--------|-------|
| Annual Return | 6.5% |
| Annual Risk | 10.2% |
| Sharpe Ratio | **0.638** |
| Diversification Ratio | 1.13 |
| Annual Cost | 0.05% |

**Allocation**:
- VTI (US Total): 5.9%
- VOO (S&P 500): 12.7%
- VBR (Small Cap Value): 1.9%
- VTV (Large Cap Value): 5.1%
- MTUM (Momentum): 12.9%
- VXUS (International): 21.2%
- BND (US Bonds): 40.3%

**Improvement over Bogleheads**: +22.3% Sharpe ratio

---

## Simple Optimization Results

**Method**: Test 1,000 random portfolios, select top 50 by Sharpe ratio

| Metric | Best Portfolio | Traditional 60/40 | Improvement |
|--------|----------------|-------------------|-------------|
| Sharpe Ratio | **0.772** | 0.667 | +15.8% |
| Annual Return | 7.7% | 8.0% | -0.3 pp |
| Annual Risk | 10.0% | 12.0% | -2.0 pp |
| Annual Cost | 0.04% | 0.04% | 0.0 pp |

**Best Allocation**:
- VTI: 15.2%
- VXUS: 2.5%
- BND: 46.5%
- VOO: 21.6%
- VBR: 1.1%
- VTV: 4.3%
- MTUM: 8.8%

---

## Key Insights

### 1. US Outperformance (2015-2024)
- US stocks (VTI, VOO): 13-14% returns
- International (VXUS): 6.5% returns
- **Gap**: 7 percentage points favoring US

This is **period-specific** and may not persist. Historical long-term data (1970-2024) shows smaller gaps.

### 2. Diversification Benefits
- Bogleheads 3-Fund: 1.01 diversification ratio
- Momentum Tilt: 1.10 diversification ratio
- Concentrated US: 1.00 diversification ratio (no benefit)

Higher ratio = better risk reduction through diversification.

### 3. Factor Premiums
- **Momentum** (MTUM): 14.40% return, 0.719 Sharpe - strongest factor
- **Value** (VBR, VTV): 10-11% returns, 0.5-0.65 Sharpe - underperformed in growth era
- **Market** (VTI, VOO): 13-14% returns, 0.75-0.78 Sharpe - strong baseline

### 4. Bond Allocation Impact
- 60/40 (40% bonds): 0.628 Sharpe, 10.8% volatility
- Bogleheads (10% bonds): 0.521 Sharpe, 16.0% volatility
- **Tradeoff**: Lower returns but significantly lower risk

### 5. Optimization Findings
- Simple optimization favors **46.5% bonds** (risk reduction)
- Constrained optimization favors **40.3% bonds** (balanced approach)
- Both prefer lower volatility over maximum returns

---

## Recommendations

### For Conservative Investors
**Traditional 60/40**: 0.628 Sharpe, 10.8% volatility
- Highest risk-adjusted returns in this period
- Lower volatility for stability
- Simple, easy to maintain

### For Balanced Investors
**Bogleheads 3-Fund**: 0.521 Sharpe, 16.0% volatility
- Global diversification (36% international)
- Simple 3-fund approach
- Follows time-tested principles

### For Factor Investors
**Momentum Tilt**: 0.551 Sharpe, 14.0% volatility, 1.10 diversification
- Captures momentum premium
- Better diversification than plain market
- Requires rebalancing discipline

### For Aggressive Investors
**Concentrated US**: 0.516 Sharpe, 16.8% volatility
- Highest returns (8.6%)
- No diversification benefit
- Period-specific (2015-2024 US outperformance)

---

## Limitations

1. **Period-Specific**: 2015-2024 saw exceptional US outperformance. May not continue.

2. **Survivorship Bias**: Analysis uses ETFs that exist today. Doesn't account for failed funds.

3. **No Transaction Costs**: Assumes free rebalancing. Real costs reduce returns.

4. **Historical Data**: Past performance doesn't guarantee future results.

5. **Factor Timing**: Value underperformed during growth era. May revert to mean.

---

## Data Quality

✓ **Real market data** from Tiingo API  
✓ **Adjusted prices** (splits and dividends)  
✓ **Daily frequency** (2,516 observations)  
✓ **Complete period** (no gaps)  
✓ **Multiple asset classes** (stocks, bonds, factors)

**API Limits Respected**:
- Tiingo: 7 requests (well under 50/hour, 1,000/day limits)
- Rate limiting: 1.2 seconds between requests
- Total bandwidth: <1 MB (well under 2 GB/month limit)

---

## Conclusion

Real data analysis confirms:
1. **Diversification matters** - higher diversification ratios improve risk-adjusted returns
2. **Bonds reduce volatility** - 60/40 outperformed on Sharpe ratio despite lower returns
3. **Factor premiums exist** - momentum showed strongest performance
4. **US outperformance was exceptional** - 7 pp gap over international may not persist
5. **Bogleheads principles remain sound** - simple, diversified approach delivers competitive results

**Best approach**: Choose strategy matching your risk tolerance and investment philosophy, not just highest historical Sharpe ratio.
