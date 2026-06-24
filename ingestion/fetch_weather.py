import pandas as pd
import requests
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine

LOCATIONS = {
    'Germany':     {'lat': 52.52,  'lon': 13.41},
    'France':      {'lat': 48.85,  'lon': 2.35},
    'Spain':       {'lat': 40.42,  'lon': -3.70},
    'Italy':       {'lat': 41.90,  'lon': 12.50},
    'Poland':      {'lat': 52.23,  'lon': 21.01},
    'Netherlands': {'lat': 52.37,  'lon': 4.90},
    'Belgium':     {'lat': 50.85,  'lon': 4.35},
    'Sweden':      {'lat': 59.33,  'lon': 18.07},
    'Norway':      {'lat': 59.91,  'lon': 10.75},
    'Denmark':     {'lat': 55.68,  'lon': 12.57},
    'Austria':     {'lat': 48.21,  'lon': 16.37},
    'Portugal':    {'lat': 38.72,  'lon': -9.14},
}

def fetch_weather_forecast():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Fetching weather forecasts...')
    all_records = []

    for country, loc in LOCATIONS.items():
        url = (
            f'https://api.open-meteo.com/v1/forecast'
            f'?latitude={loc["lat"]}'
            f'&longitude={loc["lon"]}'
            f'&daily=windspeed_10m_max,shortwave_radiation_sum,precipitation_sum'
            f'&forecast_days=7'
            f'&timezone=Europe%2FBerlin'
        )

        response = requests.get(url, timeout=30)
        data = response.json()

        for i, date in enumerate(data['daily']['time']):
            all_records.append({
                'country':            country,
                'forecast_date':      date,
                'wind_speed_max_kmh': data['daily']['windspeed_10m_max'][i],
                'solar_radiation_mj': data['daily']['shortwave_radiation_sum'][i],
                'precipitation_mm':   data['daily']['precipitation_sum'][i],
                'ingested_at':        datetime.now()
            })

    df = pd.DataFrame(all_records)
    engine = get_engine()
    df.to_sql('raw_weather', engine, schema='raw', if_exists='replace', index=False)
    print(f'  ✅ Saved {len(df)} rows to raw.raw_weather')
    return len(df)

if __name__ == '__main__':
    fetch_weather_forecast()