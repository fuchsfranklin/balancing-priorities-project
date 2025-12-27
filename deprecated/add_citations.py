import json

with open('blog/international-equity-factor-tilts.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Add citations inline
citations = [
    ('economist Burton Malkiel boldly asserted', 'economist Burton Malkiel boldly asserted (Malkiel, 2019)'),
    ('In *The Simple Path to Wealth*, Collins', 'In *The Simple Path to Wealth* (Collins, 2016), Collins'),
    ('Harry Markowitz showed that by holding', 'Harry Markowitz showed that by holding a broad portfolio of assets, you can maximize your expected return for any given level of risk (Markowitz, 1952). He introduced'),
    ('the Capital Asset Pricing Model (CAPM) (Sharpe, 1964) took', 'the Capital Asset Pricing Model (CAPM) took Markowitz\'s work a step further (Sharpe, 1964).'),
    ('articulated by Eugene Fama in 1970. EMH', 'articulated by Eugene Fama in 1970 (Fama, 1970). EMH'),
    ('Andrew Ang famously put it this way: "Factors are to assets what nutrients are to food."', 'Andrew Ang famously put it this way: "Factors are to assets what nutrients are to food" (Ang, 2014).'),
    ('In 1992, Fama and French found that two', 'In 1992, Fama and French found that two simple characteristics – a stock\'s size (small vs. large) and valuation (cheap "value" stocks vs. expensive "growth" stocks) – explained a lot of differences in stock returns that the market alone didn\'t (Fama & French, 1992).'),
    ('as author Larry Swedroe notes, you only', 'as author Larry Swedroe notes, you only need a handful of the major ones to explain most of the differences in portfolio performance (Swedroe & Berkin, 2016). In fact'),
]

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        content = ''.join(cell['source'])
        for old, new in citations:
            if old in content:
                content = content.replace(old, new)
        cell['source'] = content.split('\n')

# Add bibliography at end
bib = """---

## References

### Books

**Malkiel, B. G.** (2019). *A Random Walk Down Wall Street: The Time-Tested Strategy for Successful Investing* (50th Anniversary Edition). W. W. Norton & Company. ISBN: 978-0393358389. [https://wwnorton.com/books/9780393358389](https://wwnorton.com/books/9780393358389)

**Collins, J. L.** (2016). *The Simple Path to Wealth*. JL Collins LLC. ISBN: 978-1533667922. [https://www.simplepathtowealth.com/](https://www.simplepathtowealth.com/)

**Swedroe, L. & Berkin, A.** (2016). *Your Complete Guide to Factor-Based Investing: The Way Smart Money Invests Today*. Harriman House. ISBN: 978-0857195387.

**Ang, A.** (2014). *Asset Management: A Systematic Approach to Factor Investing*. Oxford University Press. ISBN: 978-0199959327.

### Academic Papers

**Markowitz, H.** (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91. [https://doi.org/10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)

**Sharpe, W. F.** (1964). Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. *Journal of Finance*, 19(3), 425–442. [https://doi.org/10.2307/2977928](https://doi.org/10.2307/2977928)

**Fama, E. F.** (1970). Efficient Capital Markets: A Review of Theory and Empirical Work. *Journal of Finance*, 25(2), 383–417. [https://doi.org/10.2307/2325486](https://doi.org/10.2307/2325486)

**Fama, E. F. & French, K. R.** (1992). The Cross-Section of Expected Stock Returns. *Journal of Finance*, 47(2), 427–465. [https://doi.org/10.1111/j.1540-6261.1992.tb04398.x](https://doi.org/10.1111/j.1540-6261.1992.tb04398.x)

### Industry Sources

**Dimensional Fund Advisors.** DFUS - US Equity Market ETF. [https://us.dimensional.com/funds/us-equity-market-etf-dfus](https://us.dimensional.com/funds/us-equity-market-etf-dfus)

**Dimensional Fund Advisors.** DFAX - World ex-US Core Equity 2 ETF. [https://us.dimensional.com/funds/world-ex-us-core-equity-2-etf-dfax](https://us.dimensional.com/funds/world-ex-us-core-equity-2-etf-dfax)

**Vanguard.** VXUS - Total International Stock ETF. [https://investor.vanguard.com/investment-products/etfs/profile/vxus](https://investor.vanguard.com/investment-products/etfs/profile/vxus)

**Vanguard.** VTI - Total Stock Market ETF. [https://investor.vanguard.com/investment-products/etfs/profile/vti](https://investor.vanguard.com/investment-products/etfs/profile/vti)

**Bogleheads Wiki.** Three-Fund Portfolio. [https://www.bogleheads.org/wiki/Three-fund_portfolio](https://www.bogleheads.org/wiki/Three-fund_portfolio)"""

nb['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': bib.split('\n')
})

with open('blog/international-equity-factor-tilts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Citations added successfully')
