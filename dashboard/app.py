import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine

st.set_page_config(
    page_title='EnergyEurope',
    page_icon='🌍',
    layout='wide'
)

@st.cache_data(ttl=3600)
def load_energy():
    engine = get_engine()
    return pd.read_sql(
        'SELECT * FROM marts.fact_energy_analytics ORDER BY country, year',
        engine
    )

@st.cache_data(ttl=3600)
def load_predictions():
    engine = get_engine()
    return pd.read_sql(
        'SELECT * FROM ml.wind_predictions ORDER BY country',
        engine
    )

@st.cache_data(ttl=3600)
def load_weather():
    engine = get_engine()
    return pd.read_sql(
        'SELECT * FROM raw.raw_weather ORDER BY country, forecast_date',
        engine
    )

# ── Sidebar ───────────────────────────────────────
with st.sidebar:
    st.title('🌍 EnergyEurope')
    st.caption('European Energy Analytics Platform')
    st.divider()

    df = load_energy()

    countries = sorted(df['country'].unique().tolist())
    selected = st.multiselect('Countries', countries, default=countries)

    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.slider('Year Range', min_year, max_year, (2010, max_year))

# ── Filter ────────────────────────────────────────
filtered = df[
    df['country'].isin(selected) &
    df['year'].between(year_range[0], year_range[1])
]
latest = filtered[filtered['year'] == filtered['year'].max()]

# ── Header ────────────────────────────────────────
st.title('🌍 European Energy Analytics Platform')
st.caption(f'Showing {len(filtered)} records | {len(selected)} countries | {year_range[0]}–{year_range[1]}')
st.divider()

# ── KPI Cards ─────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric('Avg Renewable Share', f"{latest['renewable_share_pct'].mean():.1f}%")
c2.metric('Avg Fossil Share', f"{latest['fossil_share_pct'].mean():.1f}%")
top = latest.loc[latest['renewable_share_pct'].idxmax()]
c3.metric('Top Renewable Country', f"{top['country']} ({top['renewable_share_pct']:.0f}%)")
c4.metric('Total Generation', f"{latest['electricity_generation'].sum():,.0f} TWh")

st.divider()

# ── Charts ────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader('Renewable Share Trend')
    fig = px.line(filtered, x='year', y='renewable_share_pct',
                  color='country', markers=True,
                  labels={'renewable_share_pct': 'Renewable Share (%)', 'year': 'Year'},
                  template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Renewable vs Fossil (Latest Year)')
    sorted_latest = latest.sort_values('renewable_share_pct', ascending=False)
    fig2 = px.bar(sorted_latest, x='country',
                  y=['renewable_share_pct', 'fossil_share_pct'],
                  barmode='group', template='plotly_white',
                  color_discrete_map={
                      'renewable_share_pct': '#2E8B57',
                      'fossil_share_pct': '#808080'
                  })
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Wind Predictions ──────────────────────────────
st.subheader('🔮 Wind Electricity Predictions (2026)')
preds = load_predictions()
fig3 = px.bar(preds.sort_values('predicted_wind_electricity', ascending=False),
              x='country', y='predicted_wind_electricity',
              color='predicted_wind_electricity',
              color_continuous_scale='Greens',
              labels={'predicted_wind_electricity': 'Predicted Wind (TWh)'},
              template='plotly_white')
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Weather Forecast ──────────────────────────────
st.subheader('🌬️ 7-Day Wind Forecast')
weather = load_weather()
if selected:
    weather_filtered = weather[weather['country'].isin(selected)]
    fig4 = px.line(weather_filtered, x='forecast_date', y='wind_speed_max_kmh',
                   color='country', markers=True,
                   labels={'wind_speed_max_kmh': 'Max Wind Speed (km/h)', 'forecast_date': 'Date'},
                   template='plotly_white')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Raw Data ──────────────────────────────────────
st.subheader('📊 Data Explorer')
st.dataframe(filtered, use_container_width=True)
csv = filtered.to_csv(index=False)
st.download_button('Download CSV', csv, 'energy_europe.csv', 'text/csv')