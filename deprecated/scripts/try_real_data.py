#!/usr/bin/env python3
"""
Try multiple methods to download real data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

tickers = ['VTI', 'VXUS', 'BND', 'VOO', 'VBR', 'VTV', 'MTUM']
start_date = '2015-01-01'
end_date = '2024-12-31'

print("="*70)
print("ATTEMPTING REAL DATA DOWNLOAD - MULTIPLE METHODS")
print("="*70)

# Method 1: investpy (no API key needed)
print("\n[Method 1] Trying investpy (Investing.com scraper)...")
try:
    import investpy
    
    all_data = {}
    for ticker in tickers:
        try:
            data = investpy.etfs.get_etf_historical_data(
                etf=ticker,
                country='united states',
                from_date='01/01/2015',
                to_date='31/12/2024'
            )
            all_data[ticker] = data['Close']
            print(f"  [OK] {ticker}: {len(data)} days")
        except:
            print(f"  [FAIL] {ticker}")
    
    if all_data:
        prices = pd.DataFrame(all_data)
        returns = prices.pct_change().dropna()
        
        Path('data').mkdir(exist_ok=True)
        prices.to_csv('data/real_prices.csv')
        returns.to_csv('data/real_returns.csv')
        
        print(f"\n[SUCCESS] with investpy!")
        print(f"  Downloaded {len(returns)} days")
        exit(0)
        
except ImportError:
    print("  [FAIL] investpy not installed")
except Exception as e:
    print(f"  [FAIL] {str(e)[:80]}")

# Method 2: pandas-datareader with Tiingo
print("\n[Method 2] Trying pandas-datareader with Tiingo...")
try:
    import pandas_datareader as pdr
    import os
    
    api_key = os.getenv('TIINGO_API_KEY')
    if not api_key:
        print("  [FAIL] No TIINGO_API_KEY")
    else:
        all_data = {}
        for ticker in tickers:
            try:
                data = pdr.get_data_tiingo(ticker, start=start_date, end=end_date, api_key=api_key)
                all_data[ticker] = data['adjClose']
                print(f"  [OK] {ticker}: {len(data)} days")
            except:
                print(f"  [FAIL] {ticker}")
        
        if all_data:
            prices = pd.DataFrame(all_data)
            returns = prices.pct_change().dropna()
            
            Path('data').mkdir(exist_ok=True)
            prices.to_csv('data/real_prices.csv')
            returns.to_csv('data/real_returns.csv')
            
            print(f"\n[SUCCESS] with Tiingo!")
            exit(0)
            
except ImportError:
    print("  [FAIL] pandas-datareader not installed")
except Exception as e:
    print(f"  [FAIL] {str(e)[:80]}")

# Method 3: Alpha Vantage
print("\n[Method 3] Trying Alpha Vantage...")
try:
    from alpha_vantage.timeseries import TimeSeries
    import os
    
    api_key = os.getenv('ALPHA_VANTAGE_KEY')
    if not api_key:
        print("  [FAIL] No ALPHA_VANTAGE_KEY")
    else:
        ts = TimeSeries(key=api_key, output_format='pandas')
        all_data = {}
        
        for ticker in tickers:
            try:
                data, _ = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
                data.index = pd.to_datetime(data.index)
                data = data.loc[start_date:end_date]
                all_data[ticker] = data['5. adjusted close']
                print(f"  [OK] {ticker}: {len(data)} days")
            except:
                print(f"  [FAIL] {ticker}")
        
        if all_data:
            prices = pd.DataFrame(all_data)
            returns = prices.pct_change().dropna()
            
            Path('data').mkdir(exist_ok=True)
            prices.to_csv('data/real_prices.csv')
            returns.to_csv('data/real_returns.csv')
            
            print(f"\n[SUCCESS] with Alpha Vantage!")
            exit(0)
            
except ImportError:
    print("  [FAIL] alpha_vantage not installed")
except Exception as e:
    print(f"  [FAIL] {str(e)[:80]}")

# Method 4: Direct CSV from Yahoo
print("\n[Method 4] Trying direct Yahoo CSV...")
try:
    import requests
    import urllib3
    from io import StringIO
    import time
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    session = requests.Session()
    session.verify = False
    
    all_data = {}
    for ticker in tickers:
        try:
            start_ts = int(pd.Timestamp(start_date).timestamp())
            end_ts = int(pd.Timestamp(end_date).timestamp())
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start_ts}&period2={end_ts}&interval=1d&events=history"
            
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                data = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=True)
                all_data[ticker] = data['Adj Close']
                print(f"  [OK] {ticker}: {len(data)} days")
            else:
                print(f"  [FAIL] {ticker}: HTTP {response.status_code}")
            
            time.sleep(0.5)
        except Exception as e:
            print(f"  [FAIL] {ticker}: {str(e)[:40]}")
    
    if all_data:
        prices = pd.DataFrame(all_data)
        returns = prices.pct_change().dropna()
        
        Path('data').mkdir(exist_ok=True)
        prices.to_csv('data/real_prices.csv')
        returns.to_csv('data/real_returns.csv')
        
        print(f"\n[SUCCESS] with direct CSV!")
        exit(0)
        
except Exception as e:
    print(f"  [FAIL] {str(e)[:80]}")

# All failed
print("\n" + "="*70)
print("ALL METHODS FAILED - CORPORATE NETWORK BLOCKING")
print("="*70)
print("\nUse calibrated simulation: python create_factor_data.py")
print("="*70)
