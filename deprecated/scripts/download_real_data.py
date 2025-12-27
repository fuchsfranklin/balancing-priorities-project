"""Download real market data with rate limiting for free API tiers."""
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load API keys
load_dotenv()
TIINGO_API_KEY = os.getenv('TIINGO_API_KEY')

# Tiingo limits: 50 req/hour, 1000 req/day
# We have 7 tickers, each needs 1 request = 7 total (well within limits)
TICKERS = ['VTI', 'VXUS', 'BND', 'VOO', 'VBR', 'VTV', 'MTUM', 'DFUS', 'DFAX', 'DFAI', 'DFAE']
START_DATE = '2010-01-01'  # Extended history for blog analysis
END_DATE = '2024-12-31'

def download_tiingo(ticker, api_key):
    """Download data from Tiingo with rate limiting."""
    url = f'https://api.tiingo.com/tiingo/daily/{ticker}/prices'
    params = {
        'startDate': START_DATE,
        'endDate': END_DATE,
        'token': api_key
    }
    
    try:
        df = pd.read_json(url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()]))
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        time.sleep(1.2)  # Rate limit: max 50/hour = 1 per 72 seconds, use 1.2s to be safe
        return df['adjClose']
    except Exception as e:
        print(f"  [FAIL] {ticker}: {e}")
        return None

print("=" * 70)
print("DOWNLOADING REAL DATA FROM TIINGO")
print("=" * 70)
print(f"Tickers: {', '.join(TICKERS)}")
print(f"Period: {START_DATE} to {END_DATE}")
print(f"Rate limit: 1.2 seconds between requests (50/hour limit)")
print("=" * 70)

# Download all tickers
data = {}
for i, ticker in enumerate(TICKERS, 1):
    print(f"[{i}/{len(TICKERS)}] Downloading {ticker}...", end=' ')
    series = download_tiingo(ticker, TIINGO_API_KEY)
    if series is not None:
        data[ticker] = series
        print(f"OK ({len(series)} days)")
    else:
        print("FAIL")

if data:
    # Combine into DataFrame
    df = pd.DataFrame(data)
    df.index.name = 'Date'
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/prices_data.csv')
    
    # Calculate returns
    returns = df.pct_change().dropna()
    returns.to_csv('data/returns_data.csv')
    
    print("=" * 70)
    print(f"SUCCESS: Downloaded {len(data)} tickers, {len(df)} days")
    print(f"Saved: data/prices_data.csv, data/returns_data.csv")
    print("=" * 70)
    
    # Show statistics
    print("\nAnnualized Statistics (2015-2024):")
    print("-" * 70)
    annual_return = returns.mean() * 252 * 100
    annual_vol = returns.std() * (252 ** 0.5) * 100
    for ticker in TICKERS:
        if ticker in data:
            print(f"{ticker:6s}: {annual_return[ticker]:6.2f}% return, {annual_vol[ticker]:6.2f}% volatility")
else:
    print("=" * 70)
    print("FAILED: No data downloaded")
    print("=" * 70)
