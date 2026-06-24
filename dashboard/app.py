import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine

st.set_page_config(
    page_title='EnergyEurope | Analytics Platform',
    page_icon='⚡',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050A14 !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0A1628 0%, #050A14 50%) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080F1E 0%, #050A14 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(56,189,248,0.3) !important;
    background: linear-gradient(135deg, rgba(56,189,248,0.06) 0%, rgba(255,255,255,0.02) 100%) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748B !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%) !important;
    color: white !important;
    font-weight: 600 !important;
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly Base Layout ─────────────────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#94A3B8', size=12),
    legend=dict(
        bgcolor='rgba(255,255,255,0.04)',
        bordercolor='rgba(255,255,255,0.08)',
        borderwidth=1,
        font=dict(size=11, color='#94A3B8'),
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(
        bgcolor='#0F1729',
        bordercolor='rgba(255,255,255,0.1)',
        font=dict(family='DM Sans', size=12, color='#F1F5F9'),
    ),
)

AXIS_STYLE = dict(
    gridcolor='rgba(255,255,255,0.05)',
    linecolor='rgba(255,255,255,0.08)',
    tickfont=dict(size=11, color='#64748B'),
    showgrid=True,
    zeroline=False,
)

COUNTRY_COLORS = {
    'Germany': '#38BDF8', 'France': '#818CF8', 'Spain': '#34D399',
    'Italy': '#FB923C', 'Poland': '#F472B6', 'Netherlands': '#A78BFA',
    'Belgium': '#FBBF24', 'Sweden': '#2DD4BF', 'Norway': '#4ADE80',
    'Denmark': '#F87171', 'Austria': '#C084FC', 'Portugal': '#FCA5A5',
}

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_energy():
    engine = get_engine()
    return pd.read_sql('SELECT * FROM marts.fact_energy_analytics ORDER BY country, year', engine)

@st.cache_data(ttl=3600)
def load_predictions():
    engine = get_engine()
    return pd.read_sql('SELECT * FROM ml.wind_predictions ORDER BY predicted_wind_electricity DESC', engine)

@st.cache_data(ttl=3600)
def load_weather():
    engine = get_engine()
    return pd.read_sql('SELECT * FROM raw.raw_weather ORDER BY country, forecast_date', engine)

df = load_energy()
preds = load_predictions()
weather = load_weather()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 24px 0;'>
        <div style='font-size:22px;font-weight:800;color:#F1F5F9;'>⚡ EnergyEurope</div>
        <div style='font-size:11px;color:#475569;letter-spacing:0.08em;text-transform:uppercase;margin-top:4px;'>Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.06);margin-bottom:20px;'></div>", unsafe_allow_html=True)

    all_countries = sorted(df['country'].unique().tolist())
    selected = st.multiselect('Countries', all_countries, default=all_countries)

    min_y, max_y = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider('Year Range', min_y, max_y, (2000, max_y))

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    if col_a.button('🌿 Green', use_container_width=True):
        selected = ['Norway', 'Sweden', 'Denmark', 'Austria', 'Portugal']
    if col_b.button('🏭 Fossil', use_container_width=True):
        selected = ['Poland', 'Belgium', 'Netherlands', 'France', 'Italy']

    st.markdown(f"""
    <div style='margin-top:24px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 14px;'>
        <div style='font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>Data Status</div>
        <div style='font-size:12px;color:#34D399;'>● Live</div>
        <div style='font-size:11px;color:#64748B;margin-top:4px;'>12 countries · 26 years · Updated daily</div>
    </div>
    """, unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = df[df['country'].isin(selected) & df['year'].between(year_range[0], year_range[1])]
latest = filtered[filtered['year'] == filtered['year'].max()]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding:32px 0 24px 0;'>
    <div style='display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;'>
        <span style='font-family:"Playfair Display",serif;font-size:36px;font-weight:800;color:#F1F5F9;letter-spacing:-1px;'>European Energy</span>
        <span style='font-family:"Playfair Display",serif;font-size:36px;font-weight:800;background:linear-gradient(135deg,#38BDF8,#6366F1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>Analytics</span>
    </div>
    <div style='font-size:14px;color:#475569;margin-top:6px;'>
        Real-time renewable energy intelligence across {len(selected)} European nations · {year_range[0]}–{year_range[1]}
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
avg_ren  = latest['renewable_share_pct'].mean()
avg_fos  = latest['fossil_share_pct'].mean()
top_row  = latest.loc[latest['renewable_share_pct'].idxmax()]
total_gen = latest['electricity_generation'].sum()
avg_wind = latest['wind_share_pct'].mean()
prev_yr  = filtered[filtered['year'] == filtered['year'].max() - 1]
delta    = avg_ren - prev_yr['renewable_share_pct'].mean() if len(prev_yr) > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('Avg Renewable Share', f'{avg_ren:.1f}%',  f'{delta:+.1f}% YoY')
c2.metric('Avg Fossil Share',    f'{avg_fos:.1f}%',  f'{-delta:+.1f}% YoY')
c3.metric('Top Green Country',   top_row['country'], f'{top_row["renewable_share_pct"]:.0f}%')
c4.metric('Total Generation',    f'{total_gen:,.0f} TWh')
c5.metric('Avg Wind Share',      f'{avg_wind:.1f}%')

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📈  Trends', '🌍  Country Map', '🔮  Forecasts', '🌬️  Weather', '📊  Explorer'
])

# ══════════════ TAB 1 — TRENDS ══════════════
with tab1:
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Renewable Energy Share — Historical Trend</div>", unsafe_allow_html=True)
        fig = go.Figure()
        for country in sorted(selected):
            cdf = filtered[filtered['country'] == country].sort_values('year')
            color = COUNTRY_COLORS.get(country, '#94A3B8')
            fig.add_trace(go.Scatter(
                x=cdf['year'], y=cdf['renewable_share_pct'], name=country,
                mode='lines+markers',
                line=dict(color=color, width=2.5),
                marker=dict(size=5, color=color, line=dict(color='#050A14', width=1.5)),
                hovertemplate=f'<b>{country}</b><br>Year: %{{x}}<br>Renewable: %{{y:.1f}}%<extra></extra>',
            ))
        fig.update_layout(**BASE_LAYOUT, height=380)
        fig.update_xaxes(**AXIS_STYLE, title='')
        fig.update_yaxes(**AXIS_STYLE, title='Renewable Share (%)', ticksuffix='%')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Energy Mix — Latest Year</div>", unsafe_allow_html=True)
        mix_long = latest[['country','wind_electricity','solar_electricity','hydro_electricity',
                           'nuclear_electricity','coal_electricity','gas_electricity']]\
                   .melt(id_vars='country', var_name='source', value_name='twh')
        mix_long['source'] = mix_long['source'].str.replace('_electricity','').str.title()
        source_colors = {'Wind':'#38BDF8','Solar':'#FBBF24','Hydro':'#34D399',
                        'Nuclear':'#A78BFA','Coal':'#6B7280','Gas':'#F97316'}
        fig2 = px.bar(mix_long, x='country', y='twh', color='source',
                     color_discrete_map=source_colors,
                     labels={'twh':'TWh','country':'','source':'Source'})
        fig2.update_layout(**BASE_LAYOUT, height=380, barmode='stack')
        fig2.update_xaxes(**AXIS_STYLE, tickangle=-45)
        fig2.update_yaxes(**AXIS_STYLE, title='TWh')
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Renewable vs Fossil Comparison</div>", unsafe_allow_html=True)
        sl = latest.sort_values('renewable_share_pct', ascending=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(y=sl['country'], x=sl['renewable_share_pct'], name='Renewable',
                             orientation='h', marker=dict(color='#34D399', opacity=0.85),
                             hovertemplate='<b>%{y}</b><br>Renewable: %{x:.1f}%<extra></extra>'))
        fig3.add_trace(go.Bar(y=sl['country'], x=sl['fossil_share_pct'], name='Fossil',
                             orientation='h', marker=dict(color='#F87171', opacity=0.7),
                             hovertemplate='<b>%{y}</b><br>Fossil: %{x:.1f}%<extra></extra>'))
        fig3.update_layout(**BASE_LAYOUT, height=340, barmode='group')
        fig3.update_xaxes(**AXIS_STYLE, ticksuffix='%')
        fig3.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with col4:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Year-over-Year Growth</div>", unsafe_allow_html=True)
        yoy = latest[['country','yoy_growth_pct']].dropna().sort_values('yoy_growth_pct', ascending=True)
        colors_yoy = ['#F87171' if v < 0 else '#34D399' for v in yoy['yoy_growth_pct']]
        fig4 = go.Figure(go.Bar(
            y=yoy['country'], x=yoy['yoy_growth_pct'], orientation='h',
            marker=dict(color=colors_yoy, opacity=0.85),
            hovertemplate='<b>%{y}</b><br>YoY: %{x:.1f}%<extra></extra>'
        ))
        fig4.update_layout(**BASE_LAYOUT, height=340)
        fig4.update_xaxes(**AXIS_STYLE, ticksuffix='%')
        fig4.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

# ══════════════ TAB 2 — MAP ══════════════
with tab2:
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    metric_choice = st.radio('', ['Renewable Share %','Fossil Share %','Wind Share %','Total Generation (TWh)'],
                             horizontal=True, label_visibility='collapsed')
    metric_map = {
        'Renewable Share %':       ('renewable_share_pct',    'Renewable Share (%)'),
        'Fossil Share %':          ('fossil_share_pct',       'Fossil Share (%)'),
        'Wind Share %':            ('wind_share_pct',         'Wind Share (%)'),
        'Total Generation (TWh)':  ('electricity_generation', 'Generation (TWh)'),
    }
    col, label = metric_map[metric_choice]
    color_scale = 'RdYlGn' if metric_choice in ['Renewable Share %','Wind Share %'] else 'RdYlGn_r'
    country_iso = {
        'Germany':'DEU','France':'FRA','Spain':'ESP','Italy':'ITA','Poland':'POL',
        'Netherlands':'NLD','Belgium':'BEL','Sweden':'SWE','Norway':'NOR',
        'Denmark':'DNK','Austria':'AUT','Portugal':'PRT',
    }
    map_data = latest.copy()
    map_data['iso'] = map_data['country'].map(country_iso)
    fig_map = px.choropleth(
        map_data, locations='iso', color=col, hover_name='country',
        color_continuous_scale=color_scale, scope='europe', labels={col: label}
    )
    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(0,0,0,0)', landcolor='rgba(255,255,255,0.05)',
                oceancolor='rgba(0,0,0,0)', showland=True, showocean=True,
                showcoastlines=True, coastlinecolor='rgba(255,255,255,0.15)',
                showsubunits=True, subunitcolor='rgba(255,255,255,0.1)'),
        coloraxis_colorbar=dict(bgcolor='rgba(255,255,255,0.04)',
                               bordercolor='rgba(255,255,255,0.08)',
                               tickfont=dict(color='#94A3B8', size=11)),
        margin=dict(l=0, r=0, t=0, b=0), height=500,
        font=dict(family='DM Sans', color='#94A3B8'),
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

    rank_df = latest[['country','renewable_share_pct','fossil_share_pct',
                      'wind_share_pct','electricity_generation','renewable_rank']]\
              .sort_values('renewable_share_pct', ascending=False).reset_index(drop=True)
    rank_df.index += 1
    rank_df.columns = ['Country','Renewable %','Fossil %','Wind %','Generation (TWh)','Rank']
    for c in ['Renewable %','Fossil %','Wind %']:
        rank_df[c] = rank_df[c].map('{:.1f}%'.format)
    rank_df['Generation (TWh)'] = rank_df['Generation (TWh)'].map('{:,.0f}'.format)
    st.dataframe(rank_df, use_container_width=True)

# ══════════════ TAB 3 — FORECASTS ══════════════
with tab3:
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(99,102,241,0.1) 0%,rgba(14,165,233,0.1) 100%);
                border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px 20px;margin-bottom:24px;'>
        <div style='font-size:13px;color:#818CF8;font-weight:600;margin-bottom:4px;'>🔮 ML Forecasting Model</div>
        <div style='font-size:12px;color:#64748B;line-height:1.6;'>
            Random Forest Regressor trained on 25 years of historical data with lag features and rolling averages.
            Extends the Bi-LSTM methodology from the MSc thesis on wind energy forecasting.
            <span style='color:#34D399;font-weight:600;'>R² = 0.989 · RMSE = 3.33 TWh</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Wind Electricity Forecast — 2026</div>", unsafe_allow_html=True)
        preds_filtered = preds[preds['country'].isin(selected)]
        colors_pred = [COUNTRY_COLORS.get(c, '#94A3B8') for c in preds_filtered['country']]
        fig_pred = go.Figure(go.Bar(
            x=preds_filtered['country'], y=preds_filtered['predicted_wind_electricity'],
            marker=dict(color=colors_pred, opacity=0.85),
            hovertemplate='<b>%{x}</b><br>Predicted: %{y:.1f} TWh<extra></extra>',
        ))
        fig_pred.update_layout(**BASE_LAYOUT, height=360)
        fig_pred.update_xaxes(**AXIS_STYLE)
        fig_pred.update_yaxes(**AXIS_STYLE, title='Predicted Wind (TWh)')
        st.plotly_chart(fig_pred, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Actual 2025 vs Forecast 2026</div>", unsafe_allow_html=True)
        actual = latest[latest['country'].isin(selected)][['country','wind_electricity']].copy()
        actual.columns = ['country','value']; actual['type'] = 'Actual 2025'
        pred2 = preds_filtered[['country','predicted_wind_electricity']].copy()
        pred2.columns = ['country','value']; pred2['type'] = 'Forecast 2026'
        compare = pd.concat([actual, pred2])
        fig_comp = px.bar(compare, x='country', y='value', color='type', barmode='group',
                         color_discrete_map={'Actual 2025':'#38BDF8','Forecast 2026':'#6366F1'})
        fig_comp.update_layout(**BASE_LAYOUT, height=360)
        fig_comp.update_xaxes(**AXIS_STYLE, tickangle=-45)
        fig_comp.update_yaxes(**AXIS_STYLE, title='Wind (TWh)')
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Historical Wind + 2026 Forecast</div>", unsafe_allow_html=True)
    fig_trend = go.Figure()
    for country in sorted(selected):
        cdf = filtered[filtered['country'] == country].sort_values('year')
        color = COUNTRY_COLORS.get(country, '#94A3B8')
        fig_trend.add_trace(go.Scatter(
            x=cdf['year'], y=cdf['wind_electricity'], name=country,
            mode='lines+markers', line=dict(color=color, width=2), marker=dict(size=4),
            hovertemplate=f'<b>{country}</b><br>%{{x}}: %{{y:.1f}} TWh<extra></extra>'
        ))
        pred_row = preds[preds['country'] == country]
        if len(pred_row) > 0 and len(cdf) > 0:
            last_val = cdf['wind_electricity'].iloc[-1]
            last_yr  = cdf['year'].iloc[-1]
            pred_val = pred_row['predicted_wind_electricity'].values[0]
            fig_trend.add_trace(go.Scatter(
                x=[last_yr, last_yr+1], y=[last_val, pred_val],
                mode='lines+markers', line=dict(color=color, width=2, dash='dot'),
                marker=dict(size=8, symbol='star', color=color), showlegend=False,
                hovertemplate=f'<b>{country} Forecast</b><br>2026: {pred_val:.1f} TWh<extra></extra>'
            ))
    fig_trend.update_layout(**BASE_LAYOUT, height=360,
                           legend=dict(**BASE_LAYOUT['legend'], orientation='h', y=-0.2, x=0))
    fig_trend.update_xaxes(**AXIS_STYLE)
    fig_trend.update_yaxes(**AXIS_STYLE, title='Wind Electricity (TWh)')
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

# ══════════════ TAB 4 — WEATHER ══════════════
with tab4:
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    weather_filtered = weather[weather['country'].isin(selected)]
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>7-Day Wind Speed Forecast</div>", unsafe_allow_html=True)
        fig_w1 = go.Figure()
        for country in sorted(selected):
            cdf = weather_filtered[weather_filtered['country'] == country].sort_values('forecast_date')
            color = COUNTRY_COLORS.get(country, '#94A3B8')
            fig_w1.add_trace(go.Scatter(
                x=cdf['forecast_date'], y=cdf['wind_speed_max_kmh'], name=country,
                mode='lines+markers', line=dict(color=color, width=2), marker=dict(size=6),
                hovertemplate=f'<b>{country}</b><br>%{{x}}<br>%{{y:.1f}} km/h<extra></extra>'
            ))
        fig_w1.update_layout(**BASE_LAYOUT, height=320)
        fig_w1.update_xaxes(**AXIS_STYLE)
        fig_w1.update_yaxes(**AXIS_STYLE, title='Max Wind Speed (km/h)')
        st.plotly_chart(fig_w1, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>7-Day Solar Radiation Forecast</div>", unsafe_allow_html=True)
        fig_w2 = go.Figure()
        for country in sorted(selected):
            cdf = weather_filtered[weather_filtered['country'] == country].sort_values('forecast_date')
            color = COUNTRY_COLORS.get(country, '#94A3B8')
            fig_w2.add_trace(go.Scatter(
                x=cdf['forecast_date'], y=cdf['solar_radiation_mj'], name=country,
                mode='lines+markers', line=dict(color=color, width=2), marker=dict(size=6),
                hovertemplate=f'<b>{country}</b><br>%{{x}}<br>%{{y:.1f}} MJ/m²<extra></extra>'
            ))
        fig_w2.update_layout(**BASE_LAYOUT, height=320)
        fig_w2.update_xaxes(**AXIS_STYLE)
        fig_w2.update_yaxes(**AXIS_STYLE, title='Solar Radiation (MJ/m²)')
        st.plotly_chart(fig_w2, use_container_width=True, config={'displayModeBar': False})

    if len(weather_filtered) > 0:
        st.markdown("<div style='font-size:13px;font-weight:600;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;'>Wind Speed Heatmap</div>", unsafe_allow_html=True)
        pivot = weather_filtered.pivot_table(index='country', columns='forecast_date',
                                            values='wind_speed_max_kmh', aggfunc='mean')
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values, x=[str(c)[:10] for c in pivot.columns], y=pivot.index.tolist(),
            colorscale='Blues',
            hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.1f} km/h<extra></extra>',
            colorbar=dict(bgcolor='rgba(255,255,255,0.04)', bordercolor='rgba(255,255,255,0.08)',
                         tickfont=dict(color='#94A3B8'))
        ))
        fig_heat.update_layout(**BASE_LAYOUT, height=300)
        fig_heat.update_xaxes(**AXIS_STYLE, title='')
        fig_heat.update_yaxes(**AXIS_STYLE, title='')
        st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

# ══════════════ TAB 5 — EXPLORER ══════════════
with tab5:
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    country_filter = col1.selectbox('Country', ['All'] + sorted(selected))
    year_filter    = col2.selectbox('Year', ['All'] + sorted(filtered['year'].unique().tolist(), reverse=True))
    sort_col       = col3.selectbox('Sort By', ['renewable_share_pct','fossil_share_pct','wind_share_pct','electricity_generation'])

    exp_df = filtered.copy()
    if country_filter != 'All': exp_df = exp_df[exp_df['country'] == country_filter]
    if year_filter    != 'All': exp_df = exp_df[exp_df['year'] == int(year_filter)]
    exp_df = exp_df.sort_values(sort_col, ascending=False)

    display_cols = ['country','year','electricity_generation','renewable_share_pct',
                   'fossil_share_pct','wind_share_pct','yoy_growth_pct','renewable_rank']
    st.markdown(f"<div style='font-size:12px;color:#475569;margin-bottom:8px;'>Showing {len(exp_df)} records</div>", unsafe_allow_html=True)
    st.dataframe(exp_df[display_cols].reset_index(drop=True), use_container_width=True, height=400)

    csv = exp_df.to_csv(index=False)
    st.download_button('⬇  Download as CSV', csv,
                      f'energy_europe_{country_filter}_{year_filter}.csv', 'text/csv')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='border-top:1px solid rgba(255,255,255,0.06);padding-top:20px;'>
    <div style='font-size:11px;color:#334155;text-align:center;'>
        ⚡ EnergyEurope Analytics Platform · Alfin Kodakkal Latheef · MSc Data Science · Berlin 2026 ·
        Stack: PostgreSQL + dbt + Streamlit + Docker + Open-Meteo
    </div>
</div>
""", unsafe_allow_html=True)