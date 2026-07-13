# ⚡ EnergyEurope — European Energy Analytics Platform

[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://energy-europe-platform-gmmxhnamygxfgjhvfezngm.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?logo=postgresql&logoColor=white)](https://supabase.com/)
[![dbt](https://img.shields.io/badge/dbt-1.8.2-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-22C55E)](LICENSE)

A fully automated, production-style data platform that tracks, analyses, and forecasts renewable energy trends across **12 European countries**. Data is ingested daily from three external APIs, transformed through a dbt modelling layer in a cloud PostgreSQL warehouse, scored by a machine learning model, and served through a live interactive dashboard — with **zero manual intervention** after setup.

**🔗 Live Dashboard →** [energy-europe-platform.streamlit.app](https://energy-europe-platform-gmmxhnamygxfgjhvfezngm.streamlit.app/)

---

## 📋 Table of Contents

- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Dashboard Pages](#dashboard-pages)
- [Data Sources](#data-sources)
- [Machine Learning Model](#machine-learning-model)
- [Key Insights](#key-insights)
- [Project Structure](#project-structure)
- [Running Locally](#running-locally)
- [Automated Pipeline](#automated-pipeline)
- [dbt Models](#dbt-models)
- [Author](#author)

---

## What It Does

Every morning at **06:00 UTC**, a GitHub Actions pipeline runs automatically:

1. Pulls the latest European energy generation data from the OWID/Ember dataset
2. Fetches a 7-day wind speed and solar radiation forecast for all 12 countries from Open-Meteo
3. Loads raw data into a cloud PostgreSQL database (Supabase) in the `raw` schema
4. Runs dbt to rebuild the `staging` and `marts` transformation layers
5. Retrains and runs a Random Forest forecasting model, writing predictions to the `ml` schema
6. The live Streamlit dashboard reads from the database and shows fresh data automatically

No human involvement required after initial deployment.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions (06:00 UTC daily)              │
└────────────────────────────┬────────────────────────────────────────┘
                             │ triggers
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   fetch_ember.py     fetch_weather.py      (scheduled)
   OWID/Ember API     Open-Meteo API
          │                  │
          └──────────┬───────┘
                     ▼
          ┌─────────────────────┐
          │   PostgreSQL        │
          │   (Supabase cloud)  │
          │                     │
          │  schema: raw        │  ◄── raw ingested data
          │  schema: staging    │  ◄── dbt cleaned models
          │  schema: marts      │  ◄── dbt analytical models
          │  schema: ml         │  ◄── ML predictions
          └──────────┬──────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     dbt run               ml/train_model.py
     (SQL transforms)      ml/predict.py
                                │
                     ┌──────────┘
                     ▼
          ┌─────────────────────┐
          │   Streamlit Cloud   │
          │   Live Dashboard    │
          │   (auto-refreshes)  │
          └─────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11 | All ingestion, transformation, and ML scripts |
| **Database** | PostgreSQL (Supabase) | Cloud-hosted warehouse with 4 schema layers |
| **Transformation** | dbt 1.8.2 | SQL-based staging and marts models with window functions |
| **Machine Learning** | scikit-learn (Random Forest) | Wind electricity forecasting |
| **Dashboard** | Streamlit + Plotly | Live, interactive web application |
| **Orchestration** | GitHub Actions | Daily scheduled pipeline (cron) |
| **Containerisation** | Docker + docker-compose | Local development environment |
| **Data Sources** | OWID, Open-Meteo, Eurostat | Energy generation, weather forecasts, official EU stats |

---

## Dashboard Pages

| Tab | What It Shows |
|-----|--------------|
| 📈 **Trends** | 25-year renewable share evolution, stacked energy mix, fossil vs renewable comparison, year-over-year growth |
| 🌍 **Country Map** | Interactive choropleth map of Europe — switchable between renewable %, fossil %, wind %, total generation |
| 🔮 **Forecasts** | ML-predicted wind electricity for 2026, actual vs forecast comparison, historical trend with dotted forecast extension |
| 🌬️ **Weather** | 7-day wind speed and solar radiation forecast per country, wind heatmap across all 12 countries |
| 📊 **Explorer** | Filterable raw data table with CSV download |

Sidebar controls let you filter by country, year range, or use quick-select buttons (🌿 Green Leaders / 🏭 Fossil Dependent).

---

## Data Sources

| Source | What It Provides | Update Frequency |
|--------|-----------------|-----------------|
| [Our World in Data / Ember](https://github.com/owid/energy-data) | Electricity generation by source (wind, solar, coal, gas, nuclear, hydro) for 12 EU countries, 2000–present | Annual |
| [Open-Meteo](https://open-meteo.com/) | 7-day wind speed and solar radiation forecasts for capital cities of all 12 countries | Daily |
| [Eurostat](https://ec.europa.eu/eurostat) | Official EU renewable energy share (% of gross final energy consumption), 2004–2024 | Annual |

**Note on methodology:** OWID and Eurostat report different renewable share values for the same countries because they use different definitions. OWID measures renewable electricity as a share of total electricity generation. Eurostat measures renewable energy as a share of gross final energy consumption (which includes heating and transport). Both are loaded and cross-validated in the platform.

---

## Machine Learning Model

A **Random Forest Regressor** forecasts next-year wind electricity output per country.

### Features

| Feature | Description |
|---------|------------|
| `wind_lag1` | Wind electricity output in the previous year |
| `wind_lag2` | Wind electricity output two years prior |
| `wind_rolling3` | 3-year rolling average — smooths out anomalies |
| `renewable_lag1` | Renewable share % from the previous year |
| `year_norm` | Year normalised to 0–1 range (captures long-term trend) |
| `country_encoded` | Country encoded as an integer (label encoding) |

### Performance

| Metric | Value |
|--------|-------|
| RMSE | 3.33 TWh |
| R² | 0.989 |
| Train / Test split | 80 / 20 |

The model retrains daily on the latest data and writes predictions back to the `ml.wind_predictions` table, which the dashboard reads directly.

**Connection to MSc thesis:** This project extends the methodology from a thesis on Bi-LSTM deep learning for German wind energy forecasting (26,000+ hourly records, 92% RMSE improvement over baseline). The thesis covered hourly single-location deep learning; EnergyEurope applies the same feature engineering concepts — lag values, rolling averages — at annual multi-country scale with classical ML.

---

## Key Insights

Surfaced through SQL window functions and cross-source data integration:

- 🇩🇰 **Denmark** showed the largest renewable transition in Europe — from 15% to 91% renewable share over 25 years (+76 percentage points), driven almost entirely by offshore wind investment
- 🇳🇴 **Norway** has been at ~99% renewable since 2000 (hydropower), with no meaningful room to improve further — its slight decline is explained by industrial growth outpacing new capacity additions
- 🇵🇱 **Poland** remains Europe's most fossil-dependent grid at ~65% fossil share, reflecting structural barriers to coal transition — a political and economic problem as much as a technical one
- 🇫🇷 **France** ranks low on renewable share specifically because of heavy nuclear reliance — nuclear is low-carbon but not classified as renewable under EU methodology
- Cross-validating OWID vs Eurostat revealed a consistent methodology gap, reinforcing the importance of understanding a data source's definition before drawing conclusions

---

## Project Structure

```
energy-europe-platform/
│
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml        # Daily automated pipeline (06:00 UTC)
│
├── ingestion/
│   ├── db_connect.py                 # Reusable PostgreSQL connection helper
│   ├── fetch_ember.py                # OWID/Ember energy data ingestion
│   └── fetch_weather.py              # Open-Meteo weather forecast ingestion
│
├── dbt/
│   └── energy_europe/
│       └── models/
│           ├── staging/
│           │   └── stg_energy.sql    # Cleans raw energy data (NULL handling, filtering)
│           └── marts/
│               └── fact_energy_analytics.sql  # Window functions: RANK, LAG, running totals
│
├── ml/
│   ├── train_model.py                # Trains Random Forest on historical data
│   ├── predict.py                    # Generates next-year forecasts, writes to DB
│   └── models/                       # Saved model artifacts (.pkl)
│
├── dashboard/
│   └── app.py                        # Streamlit application (5 tabs)
│
├── docker-compose.yml                # Local: PostgreSQL + Redis + Streamlit
├── Dockerfile
├── requirements.txt
├── init.sql                          # Creates raw/staging/marts/ml schemas
└── README.md
```

---

## Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/Allfinkl/ENERGY-EUROPE-PLATFORM.git
cd ENERGY-EUROPE-PLATFORM

# 2. Create virtual environment with Python 3.11
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Copy .env.example to .env and fill in your PostgreSQL credentials
cp .env.example .env

# 5. Start local PostgreSQL with Docker
docker-compose up -d

# 6. Run ingestion
python ingestion/fetch_ember.py
python ingestion/fetch_weather.py

# 7. Run dbt transformations
cd dbt/energy_europe
dbt run
cd ../..

# 8. Train ML model and generate predictions
python ml/train_model.py
python ml/predict.py

# 9. Launch dashboard
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`.

### Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
POSTGRES_PORT=5432
POSTGRES_DB=energy_europe
```

---

## Automated Pipeline

The GitHub Actions workflow (`.github/workflows/daily_pipeline.yml`) runs at **06:00 UTC every day**:

```
Checkout → Install deps → Fetch energy data → Fetch weather data
→ Create dbt profiles → dbt run → Train ML model → Generate predictions
```

All package versions are pinned to prevent unexpected breakage from upstream updates:

```
dbt-core==1.8.2        dbt-postgres==1.8.2
pandas==2.2.2          numpy==1.26.4
scikit-learn==1.5.0    joblib==1.4.2
sqlalchemy==2.0.30     psycopg2-binary==2.9.9
requests==2.31.0       python-dotenv==1.0.1
```

Database credentials are stored as GitHub Secrets and injected at runtime — never stored in the repository.

---

## dbt Models

### `staging/stg_energy.sql`
Reads from `raw.raw_energy`. Applies:
- `COALESCE(column, 0)` to replace NULLs with zero across all energy columns
- Filters to year ≥ 2000 and non-null countries
- Filters out rows where `electricity_generation = 0`

### `marts/fact_energy_analytics.sql`
Reads from `stg_energy`. Computes:

| Column | Calculation |
|--------|------------|
| `renewable_share_pct` | `renewables / generation * 100` |
| `fossil_share_pct` | `(coal + gas) / generation * 100` |
| `wind_share_pct` | `wind / generation * 100` |
| `yoy_growth_pct` | `LAG() OVER (PARTITION BY country ORDER BY year)` |
| `renewable_rank` | `RANK() OVER (PARTITION BY year ORDER BY renewables DESC)` |

`NULLIF(denominator, 0)` is used throughout to prevent division-by-zero errors.

---

## Author

**Alfin Kodakkal Latheef**
MSc Data Science · University of Europe for Applied Sciences, Potsdam
📍 Berlin, Germany
🔗 [LinkedIn](https://linkedin.com/in/alfin-latheef) · [GitHub](https://github.com/Allfinkl)

---

## License

MIT License — see [LICENSE](LICENSE) for details.