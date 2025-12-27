import json

with open('blog/international-equity-factor-tilts.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove old bibliography
if nb['cells'][-1]['cell_type'] == 'markdown' and '## References' in ''.join(nb['cells'][-1]['source']):
    nb['cells'].pop()

# Add complete bibliography
bib = """---

## References

### Books

**Malkiel, B. G.** (2019). *A Random Walk Down Wall Street: The Time-Tested Strategy for Successful Investing* (50th Anniversary Edition). W. W. Norton & Company. ISBN: 978-0393358389. [https://wwnorton.com/books/9780393358389](https://wwnorton.com/books/9780393358389)

**Collins, J. L.** (2016). *The Simple Path to Wealth*. JL Collins LLC. ISBN: 978-1533667922. [https://www.simplepathtowealth.com/](https://www.simplepathtowealth.com/)

**Swedroe, L. & Berkin, A.** (2016). *Your Complete Guide to Factor-Based Investing: The Way Smart Money Invests Today*. Harriman House. ISBN: 978-0857195387. [https://www.harriman-house.com/completeguidefactorinvesting](https://www.harriman-house.com/completeguidefactorinvesting)

**Ang, A.** (2014). *Asset Management: A Systematic Approach to Factor Investing*. Oxford University Press. ISBN: 978-0199959327. [https://global.oup.com/academic/product/asset-management-9780199959327](https://global.oup.com/academic/product/asset-management-9780199959327)

### Academic Papers

**Markowitz, H.** (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91. [https://doi.org/10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)

**Sharpe, W. F.** (1964). Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. *Journal of Finance*, 19(3), 425–442. [https://doi.org/10.2307/2977928](https://doi.org/10.2307/2977928)

**Fama, E. F.** (1970). Efficient Capital Markets: A Review of Theory and Empirical Work. *Journal of Finance*, 25(2), 383–417. [https://doi.org/10.2307/2325486](https://doi.org/10.2307/2325486)

**Fama, E. F. & French, K. R.** (1992). The Cross-Section of Expected Stock Returns. *Journal of Finance*, 47(2), 427–465. [https://doi.org/10.1111/j.1540-6261.1992.tb04398.x](https://doi.org/10.1111/j.1540-6261.1992.tb04398.x)

### Videos & Multimedia

**Felix, B.** Why DFUS Outperformed VTI (And What It Means for Index Funds). *Rational Reminder / YouTube*. [https://www.youtube.com/watch?v=qTw-rDF9XOg](https://www.youtube.com/watch?v=qTw-rDF9XOg)

### Industry Sources

**Dimensional Fund Advisors.** DFUS - US Equity Market ETF. [https://us.dimensional.com/funds/us-equity-market-etf-dfus](https://us.dimensional.com/funds/us-equity-market-etf-dfus)

**Dimensional Fund Advisors.** DFAI - International Core Equity Market ETF. [https://us.dimensional.com/funds/international-core-equity-market-etf-dfai](https://us.dimensional.com/funds/international-core-equity-market-etf-dfai)

**Dimensional Fund Advisors.** DFAE - Emerging Core Equity Market ETF. [https://us.dimensional.com/funds/emerging-core-equity-market-etf-dfae](https://us.dimensional.com/funds/emerging-core-equity-market-etf-dfae)

**Dimensional Fund Advisors.** DFAX - World ex-US Core Equity 2 ETF. [https://us.dimensional.com/funds/world-ex-us-core-equity-2-etf-dfax](https://us.dimensional.com/funds/world-ex-us-core-equity-2-etf-dfax)

**Vanguard.** VXUS - Total International Stock ETF. [https://investor.vanguard.com/investment-products/etfs/profile/vxus](https://investor.vanguard.com/investment-products/etfs/profile/vxus)

**Vanguard.** VTI - Total Stock Market ETF. [https://investor.vanguard.com/investment-products/etfs/profile/vti](https://investor.vanguard.com/investment-products/etfs/profile/vti)

**Avantis Investors.** AVDE - International Equity ETF. [https://www.avantisinvestors.com/investments/avde](https://www.avantisinvestors.com/investments/avde)

**Avantis Investors.** AVEM - Emerging Markets Equity ETF. [https://www.avantisinvestors.com/investments/avem](https://www.avantisinvestors.com/investments/avem)

### Web Resources

**Bogleheads Wiki.** Three-Fund Portfolio. [https://www.bogleheads.org/wiki/Three-fund_portfolio](https://www.bogleheads.org/wiki/Three-fund_portfolio)

**Morningstar.** Fund Pages & Factor Exposures. [https://www.morningstar.com/](https://www.morningstar.com/)

**Yahoo Finance.** Price & Return Data. [https://finance.yahoo.com/](https://finance.yahoo.com/)"""

nb['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': bib.split('\n')
})

with open('blog/international-equity-factor-tilts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Complete bibliography added')
