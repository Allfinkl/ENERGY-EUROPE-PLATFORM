import pandas as pd
import sqlalchemy
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine

COUNTRIES = [
    'Germany', 'France', 'Spain', 'Italy', 'Poland',
    'Netherlands', 'Belgium', 'Sweden', 'Norway',
    'Denmark', 'Austria', 'Portugal'
]

KEEP_COLS = [
    'country', 'year',
    'electricity_generation',
    'renewables_electricity',
    'wind_electricity',
    'solar_electricity',
    'coal_electricity',
    'gas_electricity',
    'nuclear_electricity',
    'hydro_electricity',
]

def fetch_ember_data():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Fetching energy data...')

    url = 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv'
    df = pd.read_csv(url)
    print(f'  Downloaded {len(df)} rows')

    df = df[df['country'].isin(COUNTRIES)]
    df = df[df['year'] >= 2000]

    available_cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[available_cols].copy()
    df['ingested_at'] = datetime.now()

    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS raw.raw_energy CASCADE"))
        conn.commit()

    df.to_sql('raw_energy', engine, schema='raw', if_exists='append', index=False)
    print(f'  ✅ Saved {len(df)} rows to raw.raw_energy')
    return len(df)

if __name__ == '__main__':
    fetch_ember_data()