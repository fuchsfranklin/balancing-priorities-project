import json

with open('blog/international-equity-factor-tilts.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update cell 5
src5 = ''.join(data['cells'][5]['source'])
old1 = """fig = go.Figure()
    for col in growth_df.columns:
        dash = 'dash' if '60%' in col else 'solid'
        width = 3 if '60%' in col else 2
        fig.add_trace(go.Scatter(x=growth_df.index, y=growth_df[col], name=col, 
                                line=dict(dash=dash, width=width)))
    fig.update_layout(title='Growth of $1: US vs International Mix',
                     xaxis_title='Year', yaxis_title='Portfolio Value ($)',
                     hovermode='x unified')
    fig.show()"""

new1 = """fig = go.Figure()
    colors = {'100% US (VTI)': '#1f77b4', '60% US / 40% Intl': '#ff7f0e', '100% Intl (VXUS)': '#2ca02c'}
    for col in growth_df.columns:
        dash = 'dash' if '60%' in col else 'solid'
        width = 2.5 if '60%' in col else 2
        fig.add_trace(go.Scatter(x=growth_df.index, y=growth_df[col], name=col, line=dict(dash=dash, width=width, color=colors[col]), hovertemplate='%{y:.2f}<extra></extra>'))
    fig.update_layout(title={'text': 'Growth of $1: US vs International Mix', 'x': 0.5, 'xanchor': 'center'}, xaxis_title='', yaxis_title='Portfolio Value ($)', hovermode='x unified', template='plotly_white', font=dict(size=12), height=450, legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(255,255,255,0.8)'))
    fig.show()"""

data['cells'][5]['source'] = [line + '\n' for line in src5.replace(old1, new1).split('\n')]

# Update cell 10
src10 = ''.join(data['cells'][10]['source'])
old2 = """fig = go.Figure()
fig.add_trace(go.Scatter(x=vti_norm.index, y=vti_norm, name='VTI (Total US Market)', line=dict(width=2)))
fig.add_trace(go.Scatter(x=dfus_norm.index, y=dfus_norm, name='DFUS (DFA US Core Equity)', line=dict(width=2, dash='dash')))
fig.update_layout(
    title='VTI vs DFUS: Growth of $1 Since DFUS Inception',
    xaxis_title='Date',
    yaxis_title='Growth of $1',
    hovermode='x unified',
    template='plotly_white'
)
fig.show()"""

new2 = """fig = go.Figure()
fig.add_trace(go.Scatter(x=vti_norm.index, y=vti_norm, name='VTI (Total US Market)', line=dict(width=2, color='#1f77b4'), hovertemplate='%{y:.2f}<extra></extra>'))
fig.add_trace(go.Scatter(x=dfus_norm.index, y=dfus_norm, name='DFUS (DFA US Core Equity)', line=dict(width=2, dash='dash', color='#d62728'), hovertemplate='%{y:.2f}<extra></extra>'))
fig.update_layout(title={'text': 'VTI vs DFUS: Growth of $1 Since DFUS Inception', 'x': 0.5, 'xanchor': 'center'}, xaxis_title='', yaxis_title='Growth of $1', hovermode='x unified', template='plotly_white', font=dict(size=12), height=450, legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(255,255,255,0.8)'))
fig.show()"""

data['cells'][10]['source'] = [line + '\n' for line in src10.replace(old2, new2).split('\n')]

# Update cell 14
src14 = ''.join(data['cells'][14]['source'])
old3 = """fig = go.Figure()
fig.add_trace(go.Scatter(x=vxus_norm.index, y=vxus_norm, name='VXUS (Total Intl Market)', line=dict(width=2)))
fig.add_trace(go.Scatter(x=dfax_norm.index, y=dfax_norm, name='DFAX (DFA World ex US Core Equity)', line=dict(width=2, dash='dash')))
fig.update_layout(
    title='VXUS vs DFAX: Growth of $1 Since DFAX Inception',
    xaxis_title='Date',
    yaxis_title='Growth of $1',
    hovermode='x unified',
    template='plotly_white'
)
fig.show()"""

new3 = """fig = go.Figure()
fig.add_trace(go.Scatter(x=vxus_norm.index, y=vxus_norm, name='VXUS (Total Intl Market)', line=dict(width=2, color='#2ca02c'), hovertemplate='%{y:.2f}<extra></extra>'))
fig.add_trace(go.Scatter(x=dfax_norm.index, y=dfax_norm, name='DFAX (DFA World ex US Core Equity)', line=dict(width=2, dash='dash', color='#9467bd'), hovertemplate='%{y:.2f}<extra></extra>'))
fig.update_layout(title={'text': 'VXUS vs DFAX: Growth of $1 Since DFAX Inception', 'x': 0.5, 'xanchor': 'center'}, xaxis_title='', yaxis_title='Growth of $1', hovermode='x unified', template='plotly_white', font=dict(size=12), height=450, legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(255,255,255,0.8)'))
fig.show()"""

data['cells'][14]['source'] = [line + '\n' for line in src14.replace(old3, new3).split('\n')]

with open('blog/international-equity-factor-tilts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=1)

print('Updated all 3 plots with production styling')
