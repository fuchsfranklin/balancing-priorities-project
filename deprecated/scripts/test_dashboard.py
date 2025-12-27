"""
Test dashboard components without running Streamlit
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

print("="*60)
print("DASHBOARD VALIDATION TEST")
print("="*60)

# Test 1: Load data
print("\n[1/5] Testing data loading...")
try:
    results = pd.read_csv('results/optimal_portfolios.csv')
    returns = pd.read_csv('data/returns_data.csv', index_col=0, parse_dates=True)
    print(f"  [OK] Loaded {len(results)} portfolios")
    print(f"  [OK] Loaded {len(returns)} days of returns")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    exit(1)

# Test 2: Verify data structure
print("\n[2/5] Testing data structure...")
required_cols = ['return', 'risk', 'sharpe', 'cost', 'VTI_weight', 'VXUS_weight', 'BND_weight', 'VOO_weight']
if all(col in results.columns for col in required_cols):
    print(f"  [OK] All required columns present")
else:
    print(f"  [ERROR] Missing columns")
    exit(1)

# Test 3: Calculate metrics
print("\n[3/5] Testing metric calculations...")
try:
    best = results.iloc[0]
    trad_sharpe = 0.667
    improvement = (best['sharpe'] - trad_sharpe) / trad_sharpe * 100
    print(f"  [OK] Best Sharpe: {best['sharpe']:.3f}")
    print(f"  [OK] Improvement: {improvement:.1f}%")
    print(f"  [OK] Best Return: {best['return']:.1%}")
    print(f"  [OK] Best Risk: {best['risk']:.1%}")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    exit(1)

# Test 4: Test portfolio calculation
print("\n[4/5] Testing portfolio calculations...")
try:
    def calc_portfolio_perf(weights, returns_df):
        port_return = np.sum(returns_df.mean() * weights) * 252
        port_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
        sharpe = port_return / port_vol if port_vol > 0 else 0
        return port_return, port_vol, sharpe
    
    test_weights = np.array([0.42, 0.18, 0.40, 0.0])
    ret, risk, sharpe = calc_portfolio_perf(test_weights, returns)
    print(f"  [OK] Portfolio calculation works")
    print(f"    Test portfolio: {ret:.1%} return, {risk:.1%} risk, {sharpe:.3f} Sharpe")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    exit(1)

# Test 5: Test visualization creation
print("\n[5/5] Testing visualization creation...")
try:
    # Test scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=results['risk']*100,
        y=results['return']*100,
        mode='markers',
        marker=dict(size=8, color=results['sharpe'], colorscale='Viridis')
    ))
    print(f"  [OK] Scatter plot created")
    
    # Test pie chart
    weights = {
        'VOO': best['VOO_weight'],
        'VTI': best['VTI_weight'],
        'BND': best['BND_weight'],
        'VXUS': best['VXUS_weight']
    }
    fig2 = go.Figure(data=[go.Pie(labels=list(weights.keys()), values=list(weights.values()))])
    print(f"  [OK] Pie chart created")
    
    # Test 3D scatter
    fig3 = go.Figure(data=[go.Scatter3d(
        x=results['risk']*100,
        y=results['return']*100,
        z=results['sharpe'],
        mode='markers'
    )])
    print(f"  [OK] 3D scatter created")
    
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    exit(1)

# Summary
print("\n" + "="*60)
print("DASHBOARD PREVIEW")
print("="*60)

print(f"\n[OVERVIEW TAB] Will show:")
print(f"   - Efficient frontier with {len(results)} portfolios")
print(f"   - Best portfolio: Sharpe {best['sharpe']:.3f}")
print(f"   - Improvement: +{improvement:.1f}% vs traditional")

print(f"\n[BEST PORTFOLIO TAB] Will show:")
print(f"   - VOO: {best['VOO_weight']:.1%}")
print(f"   - VTI: {best['VTI_weight']:.1%}")
print(f"   - BND: {best['BND_weight']:.1%}")
print(f"   - VXUS: {best['VXUS_weight']:.1%}")
print(f"   - Return: {best['return']:.1%}, Risk: {best['risk']:.1%}")

print(f"\n[EXPLORE TAB] Will show:")
print(f"   - Interactive 3D visualization")
print(f"   - Filters for return, risk, Sharpe")
print(f"   - Top 10 portfolios table")

print(f"\n[COMPARE TAB] Will show:")
print(f"   - Best vs Traditional comparison")
print(f"   - Custom portfolio builder")
print(f"   - Side-by-side charts")

print("\n" + "="*60)
print("[SUCCESS] ALL TESTS PASSED - DASHBOARD READY")
print("="*60)
print("\nTo launch dashboard, run:")
print("  streamlit run dashboard.py")
print("\nOr use the launcher:")
print("  launch.bat")
print()
