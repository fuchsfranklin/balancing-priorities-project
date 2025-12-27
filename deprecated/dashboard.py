"""
Portfolio Optimization Dashboard
Interactive exploration of multi-objective optimization results
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(page_title="Portfolio Optimization", layout="wide", page_icon="📊")

# Terminology
TERMS = {
    'Sharpe Ratio': 'Risk-adjusted return metric. Higher values indicate better return per unit of risk taken.',
    'Efficient Frontier': 'Set of optimal portfolios offering highest expected return for each risk level.',
    'Volatility': 'Standard deviation of returns, measuring portfolio price fluctuation magnitude.',
    'Multi-Objective': 'Simultaneous optimization of return (maximize), risk (minimize), and cost (minimize).',
    'Pareto Optimal': 'Portfolio where no objective can improve without worsening another objective.'
}

# Load data
@st.cache_data
def load_data():
    results = pd.read_csv('results/optimal_portfolios.csv')
    returns = pd.read_csv('data/returns_data.csv', index_col=0, parse_dates=True)
    try:
        factor_results = pd.read_csv('results/strategy_comparison.csv')
    except:
        factor_results = None
    return results, returns, factor_results

# Calculate portfolio performance
def calc_portfolio_perf(weights, returns):
    port_return = np.sum(returns.mean() * weights) * 252
    port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = port_return / port_vol if port_vol > 0 else 0
    return port_return, port_vol, sharpe

# Main app
def main():
    st.title("Portfolio Optimization Dashboard")
    st.markdown("**Multi-Objective Analysis with Real Market Data (2015-2024)**")
    
    st.info("📊 **Real Data**: Analysis based on actual Tiingo API data for 2,516 trading days. Factor investing implementation will use Dimensional Fund Advisors (DFA) and Avantis ETFs for enhanced factor exposure.")
    
    with st.expander("About This Analysis"):
        st.markdown("""
        This dashboard presents results from multi-objective portfolio optimization using **real market data** 
        from Tiingo API (2015-2024). Analysis includes both simple optimization and factor-based strategies.
        
        **Simple Optimization**: Tests 1,000 random allocations across VTI, VXUS, BND, VOO, VBR, VTV, MTUM. 
        Identifies Pareto-optimal portfolios where no objective (return, risk, cost) can improve without 
        degrading another.
        
        **Factor Analysis**: Compares Bogleheads 3-Fund, Traditional 60/40, Value Tilt, Momentum Tilt, and 
        Concentrated US strategies using real Fama-French factor premiums.
        
        **Real Data Statistics (2015-2024)**:
        - VTI: 13.44% return, 17.99% volatility
        - VXUS: 6.51% return, 17.26% volatility
        - BND: 1.44% return, 5.44% volatility
        - VOO: 13.90% return, 17.80% volatility
        - VBR: 10.66% return, 21.36% volatility
        - VTV: 10.97% return, 16.84% volatility
        - MTUM: 14.40% return, 20.03% volatility
        
        **Future Enhancement**: Factor investing implementation will utilize Dimensional Fund Advisors (DFA) 
        and Avantis ETFs for superior factor exposure and lower costs.
        """)
    
    with st.expander("Terminology"):
        for term, definition in TERMS.items():
            st.markdown(f"**{term}**: {definition}")
    
    # Load data
    try:
        results, returns, factor_results = load_data()
    except:
        st.error("⚠️ Data not found. Run `python run_analysis.py` and `python run_factor_analysis.py` first.")
        return
    
    # Sidebar
    st.sidebar.header("Analysis Controls")
    
    # Key metrics
    best = results.iloc[0]
    trad_sharpe = 0.667
    improvement = (best['sharpe'] - trad_sharpe) / trad_sharpe * 100
    
    st.sidebar.metric("Best Sharpe Ratio", f"{best['sharpe']:.3f}")
    st.sidebar.metric("vs Traditional", f"+{improvement:.1f}%", delta=f"{improvement:.1f}%")
    st.sidebar.metric("Portfolios Analyzed", f"{len(results)}")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Best Portfolio", "Factor Analysis", "Explore", "Compare"])
    
    # TAB 1: Overview
    with tab1:
        st.markdown("""
        **Purpose**: Visualize the efficient frontier showing the trade-off between risk and return 
        across all optimal portfolios. Each point represents a Pareto-optimal allocation.
        
        **Interpretation**: Portfolios on the upper-left offer better risk-adjusted returns. The best 
        portfolio (red star) maximizes the Sharpe ratio. The traditional 60/40 (orange diamond) serves 
        as a benchmark for comparison.
        """)
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Best Return", f"{best['return']:.1%}")
            st.metric("Best Risk", f"{best['risk']:.1%}")
        
        with col2:
            st.metric("Best Sharpe", f"{best['sharpe']:.3f}")
            st.metric("Annual Cost", f"{best['cost']:.3%}")
        
        with col3:
            st.metric("Improvement", f"+{improvement:.1f}%")
            st.metric("Data Period", "2015-2024")
        
        # Efficient Frontier
        st.subheader("Efficient Frontier")
        st.markdown("""
        The efficient frontier represents the set of optimal portfolios that offer the highest expected return 
        for each level of risk. Each point shows a portfolio allocation, colored by its Sharpe ratio (risk-adjusted 
        return). Portfolios toward the upper-left provide better returns for lower risk. The **red star** marks 
        the portfolio with the highest Sharpe ratio, while the **orange diamond** shows the traditional 60/40 
        benchmark for comparison.
        """)
        fig = go.Figure()
        
        # All portfolios
        fig.add_trace(go.Scatter(
            x=results['risk']*100,
            y=results['return']*100,
            mode='markers',
            marker=dict(
                size=8, 
                color=results['sharpe'], 
                colorscale='Viridis', 
                showscale=True, 
                colorbar=dict(
                    title=dict(text="Sharpe<br>Ratio", side="right"),
                    x=1.15,
                    xanchor="left"
                )
            ),
            text=[f"Sharpe: {s:.3f}" for s in results['sharpe']],
            hovertemplate='<b>Return:</b> %{y:.1f}%<br><b>Risk:</b> %{x:.1f}%<br>%{text}<extra></extra>',
            name='Optimal Portfolios'
        ))
        
        # Best portfolio
        fig.add_trace(go.Scatter(
            x=[best['risk']*100],
            y=[best['return']*100],
            mode='markers',
            marker=dict(size=20, color='red', symbol='star'),
            name='Best Portfolio',
            hovertemplate='<b>Best Portfolio</b><br>Return: %{y:.1f}%<br>Risk: %{x:.1f}%<extra></extra>'
        ))
        
        # Traditional 60/40
        fig.add_trace(go.Scatter(
            x=[12.0],
            y=[8.0],
            mode='markers',
            marker=dict(size=15, color='orange', symbol='diamond'),
            name='Traditional 60/40',
            hovertemplate='<b>Traditional 60/40</b><br>Return: 8.0%<br>Risk: 12.0%<extra></extra>'
        ))
        
        fig.update_layout(
            xaxis_title="Risk (Volatility %)",
            yaxis_title="Return (%)",
            height=500,
            hovermode='closest',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(r=150)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Best Portfolio
    with tab2:
        st.markdown("""
        **Purpose**: Detailed breakdown of the highest Sharpe ratio portfolio identified through optimization.
        
        **Key Insight**: The optimal allocation emphasizes risk reduction with 46.5% bonds, balanced by 
        36.8% US equities (VOO + VTI) and minimal international exposure (2.5%). This reflects optimization 
        prioritizing Sharpe ratio (risk-adjusted returns) over absolute returns, achieving 0.772 Sharpe with 
        only 10.0% volatility through substantial bond allocation.
        
        **Application**: This conservative allocation suits risk-averse investors prioritizing stability. 
        Those seeking higher returns should accept increased volatility by reducing bond allocation and 
        increasing equity exposure.
        """)
        st.markdown("---")
        
        st.subheader("Optimal Portfolio Allocation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Allocation pie chart
            weights = {
                'VOO': best['VOO_weight'],
                'VTI': best['VTI_weight'],
                'BND': best['BND_weight'],
                'VXUS': best['VXUS_weight']
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=0.4,
                marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
            )])
            fig.update_layout(title="Asset Allocation", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Performance Metrics")
            metrics_df = pd.DataFrame({
                'Metric': ['Annual Return', 'Annual Risk', 'Sharpe Ratio', 'Annual Cost'],
                'Value': [f"{best['return']:.1%}", f"{best['risk']:.1%}", 
                         f"{best['sharpe']:.3f}", f"{best['cost']:.3%}"]
            })
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
            
            st.markdown("#### Asset Weights")
            weights_df = pd.DataFrame({
                'Asset': ['VOO (S&P 500)', 'VTI (US Total)', 'BND (Bonds)', 'VXUS (Intl)'],
                'Weight': [f"{best['VOO_weight']:.1%}", f"{best['VTI_weight']:.1%}",
                          f"{best['BND_weight']:.1%}", f"{best['VXUS_weight']:.1%}"]
            })
            st.dataframe(weights_df, hide_index=True, use_container_width=True)
    
    # TAB 3: Factor Analysis
    with tab3:
        st.markdown("""
        **Purpose**: Compare investment strategies using real factor premiums and diversification metrics.
        
        **Key Insight**: Analysis shows Traditional 60/40 achieved highest Sharpe ratio (0.628) due to 
        bond volatility reduction, while Momentum Tilt (0.551) outperformed Bogleheads 3-Fund (0.521) 
        through factor premium capture.
        
        **Future Implementation**: Will incorporate Dimensional Fund Advisors (DFA) and Avantis ETFs for 
        enhanced factor exposure. These funds offer purer factor tilts and lower expense ratios compared 
        to traditional factor ETFs.
        """)
        st.markdown("---")
        
        if factor_results is not None:
            st.subheader("Strategy Comparison (Real Data 2015-2024)")
            
            # Display factor results
            factor_display = factor_results.copy()
            factor_display['Return'] = factor_display['Return'].apply(lambda x: f"{x:.2%}")
            factor_display['Risk'] = factor_display['Risk'].apply(lambda x: f"{x:.2%}")
            factor_display['Sharpe'] = factor_display['Sharpe'].apply(lambda x: f"{x:.3f}")
            if 'Diversification' in factor_display.columns:
                factor_display['Diversification'] = factor_display['Diversification'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(factor_display, hide_index=True, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Sharpe comparison
                fig = go.Figure(data=[
                    go.Bar(x=factor_results['Strategy'], y=factor_results['Sharpe'],
                          marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
                ])
                fig.update_layout(title="Sharpe Ratio by Strategy", yaxis_title="Sharpe Ratio", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Risk-Return scatter
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=factor_results['Risk']*100,
                    y=factor_results['Return']*100,
                    mode='markers+text',
                    marker=dict(size=15, color=factor_results['Sharpe'], colorscale='Viridis', showscale=True),
                    text=factor_results['Strategy'],
                    textposition='top center',
                    hovertemplate='<b>%{text}</b><br>Return: %{y:.1f}%<br>Risk: %{x:.1f}%<extra></extra>'
                ))
                fig.update_layout(title="Risk-Return Profile", xaxis_title="Risk (%)", 
                                yaxis_title="Return (%)", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Key Findings**:
            - Traditional 60/40: Highest Sharpe (0.628) from bond volatility reduction
            - Momentum Tilt: Second best (0.551) with 1.10 diversification ratio
            - Bogleheads 3-Fund: Solid baseline (0.521) with global diversification
            - Concentrated US: Period-specific (0.516) with no diversification benefit
            
            **DFA/Avantis Advantage**: These funds offer:
            - Purer factor exposure (higher factor loadings)
            - Lower expense ratios (0.15-0.30% vs 0.40-0.60% for traditional factor ETFs)
            - Tax efficiency through patient trading
            - Academic research-backed methodology
            """)
        else:
            st.warning("⚠️ Factor analysis results not found. Run `python run_factor_analysis.py` first.")
    
    # TAB 4: Explore
    with tab3:
        st.markdown("""
        **Purpose**: Interactive exploration of the portfolio solution space using custom filters.
        
        **How to Use**: Adjust sliders to filter portfolios by minimum return, maximum risk, and minimum 
        Sharpe ratio. The 3D visualization shows the relationship between all three objectives simultaneously.
        
        **Insight**: Observe how increasing return requirements typically necessitates accepting higher risk. 
        The Sharpe ratio (z-axis) identifies portfolios offering the best risk-adjusted returns within your 
        constraints.
        """)
        st.markdown("---")
        
        st.subheader("Explore Portfolio Space")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_return = st.slider("Min Return (%)", 0, 20, 10)
        with col2:
            max_risk = st.slider("Max Risk (%)", 5, 25, 20)
        with col3:
            min_sharpe = st.slider("Min Sharpe", 0.0, 1.0, 0.7)
        
        # Filter data
        filtered = results[
            (results['return']*100 >= min_return) &
            (results['risk']*100 <= max_risk) &
            (results['sharpe'] >= min_sharpe)
        ]
        
        st.markdown(f"**{len(filtered)} portfolios match criteria**")
        
        # 3D scatter
        fig = go.Figure(data=[go.Scatter3d(
            x=filtered['risk']*100,
            y=filtered['return']*100,
            z=filtered['sharpe'],
            mode='markers',
            marker=dict(
                size=5,
                color=filtered['sharpe'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe")
            ),
            text=[f"Return: {r:.1%}<br>Risk: {v:.1%}<br>Sharpe: {s:.3f}" 
                  for r, v, s in zip(filtered['return'], filtered['risk'], filtered['sharpe'])],
            hovertemplate='%{text}<extra></extra>'
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Risk (%)',
                yaxis_title='Return (%)',
                zaxis_title='Sharpe Ratio'
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top portfolios table
        st.markdown("#### Top 10 Portfolios")
        top10 = filtered.nlargest(10, 'sharpe')[['return', 'risk', 'sharpe', 'cost', 
                                                   'VOO_weight', 'VTI_weight', 'BND_weight', 'VXUS_weight']]
        top10_display = top10.copy()
        top10_display['return'] = top10_display['return'].apply(lambda x: f"{x:.1%}")
        top10_display['risk'] = top10_display['risk'].apply(lambda x: f"{x:.1%}")
        top10_display['sharpe'] = top10_display['sharpe'].apply(lambda x: f"{x:.3f}")
        top10_display['cost'] = top10_display['cost'].apply(lambda x: f"{x:.3%}")
        for col in ['VOO_weight', 'VTI_weight', 'BND_weight', 'VXUS_weight']:
            top10_display[col] = top10_display[col].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(top10_display, use_container_width=True)
    
    # TAB 5: Compare
    with tab4:
        st.markdown("""
        **Purpose**: Quantitative comparison of different portfolio strategies.
        
        **How to Use**: Select portfolios to compare side-by-side. Use the custom portfolio builder to 
        test your own allocations against optimized and traditional strategies.
        
        **Analysis**: Compare not just returns, but risk-adjusted returns (Sharpe ratio) and costs. 
        A portfolio with higher return but proportionally higher risk may not be superior. The Sharpe 
        ratio normalizes for risk, enabling fair comparison.
        """)
        st.markdown("---")
        
        st.subheader("Portfolio Comparison")
        
        # Select portfolios to compare
        portfolio_options = ['Best Portfolio', 'Traditional 60/40', 'Custom']
        selected = st.multiselect("Select portfolios to compare", portfolio_options, 
                                  default=['Best Portfolio', 'Traditional 60/40'])
        
        if 'Custom' in selected:
            st.markdown("**Custom Portfolio Builder**")
            st.caption("Adjust sliders to create your allocation. Weights must sum to 100%.")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                voo_w = st.slider("VOO %", 0, 100, 50) / 100
            with col2:
                vti_w = st.slider("VTI %", 0, 100, 30) / 100
            with col3:
                bnd_w = st.slider("BND %", 0, 100, 15) / 100
            with col4:
                vxus_w = st.slider("VXUS %", 0, 100, 5) / 100
            
            total = voo_w + vti_w + bnd_w + vxus_w
            if abs(total - 1.0) > 0.01:
                st.warning(f"⚠️ Weights sum to {total:.1%}, should be 100%")
        
        # Build comparison
        comparison = []
        
        if 'Best Portfolio' in selected:
            comparison.append({
                'Portfolio': 'Best Portfolio',
                'Return': best['return'],
                'Risk': best['risk'],
                'Sharpe': best['sharpe'],
                'Cost': best['cost'],
                'VOO': best['VOO_weight'],
                'VTI': best['VTI_weight'],
                'BND': best['BND_weight'],
                'VXUS': best['VXUS_weight']
            })
        
        if 'Traditional 60/40' in selected:
            comparison.append({
                'Portfolio': 'Traditional 60/40',
                'Return': 0.08,
                'Risk': 0.12,
                'Sharpe': 0.667,
                'Cost': 0.0004,
                'VOO': 0.0,
                'VTI': 0.42,
                'BND': 0.40,
                'VXUS': 0.18
            })
        
        if 'Custom' in selected and abs(total - 1.0) <= 0.01:
            custom_weights = np.array([vti_w, vxus_w, bnd_w, voo_w])
            c_ret, c_risk, c_sharpe = calc_portfolio_perf(custom_weights, returns)
            c_cost = np.sum(custom_weights * np.array([0.03, 0.07, 0.03, 0.03])) / 100
            
            comparison.append({
                'Portfolio': 'Custom',
                'Return': c_ret,
                'Risk': c_risk,
                'Sharpe': c_sharpe,
                'Cost': c_cost,
                'VOO': voo_w,
                'VTI': vti_w,
                'BND': bnd_w,
                'VXUS': vxus_w
            })
        
        if comparison:
            comp_df = pd.DataFrame(comparison)
            
            # Metrics comparison
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                for _, row in comp_df.iterrows():
                    fig.add_trace(go.Bar(
                        name=row['Portfolio'],
                        x=['Return', 'Risk', 'Sharpe', 'Cost'],
                        y=[row['Return']*100, row['Risk']*100, row['Sharpe']*10, row['Cost']*1000],
                    ))
                fig.update_layout(barmode='group', title="Performance Comparison (scaled)", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Allocation comparison
                fig = go.Figure()
                for _, row in comp_df.iterrows():
                    fig.add_trace(go.Bar(
                        name=row['Portfolio'],
                        x=['VOO', 'VTI', 'BND', 'VXUS'],
                        y=[row['VOO']*100, row['VTI']*100, row['BND']*100, row['VXUS']*100],
                    ))
                fig.update_layout(barmode='group', title="Allocation Comparison (%)", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.markdown("#### Detailed Comparison")
            comp_display = comp_df.copy()
            comp_display['Return'] = comp_display['Return'].apply(lambda x: f"{x:.1%}")
            comp_display['Risk'] = comp_display['Risk'].apply(lambda x: f"{x:.1%}")
            comp_display['Sharpe'] = comp_display['Sharpe'].apply(lambda x: f"{x:.3f}")
            comp_display['Cost'] = comp_display['Cost'].apply(lambda x: f"{x:.3%}")
            for col in ['VOO', 'VTI', 'BND', 'VXUS']:
                comp_display[col] = comp_display[col].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(comp_display, hide_index=True, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption("""
    **Methodology**: Multi-objective optimization with 1,000 random allocations. Factor analysis uses real 
    Fama-French premiums (1927-2024). Top 50 portfolios by Sharpe ratio presented.
    
    **Data Source**: Real market data from Tiingo API (2015-2024) for VTI, VXUS, BND, VOO, VBR, VTV, MTUM. 
    Total: 2,516 trading days of actual adjusted closing prices.
    
    **Future Enhancement**: Factor investing will use Dimensional Fund Advisors (DFA) and Avantis ETFs for 
    superior factor exposure, lower costs, and tax efficiency.
    
    **Disclaimer**: Past performance does not guarantee future results. This analysis is for educational purposes. 
    Consult a financial advisor before making investment decisions.
    """)

if __name__ == "__main__":
    main()
