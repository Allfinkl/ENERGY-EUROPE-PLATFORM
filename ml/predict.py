import pandas as pd
import numpy as np
import joblib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine
from datetime import datetime

def generate_predictions():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Generating predictions...')

    engine = get_engine()

    # Load model
    model = joblib.load('ml/models/wind_model.pkl')
    le = joblib.load('ml/models/label_encoder.pkl')

    # Load latest data
    df = pd.read_sql('''
        SELECT country, year, wind_electricity,
               renewable_share_pct
        FROM marts.fact_energy_analytics
        ORDER BY country, year
    ''', engine)

    df = df.sort_values(['country', 'year'])

    # Engineer features for prediction
    df['country_encoded'] = le.transform(df['country'])
    df['year_norm'] = (df['year'] - 2000) / 25
    df['wind_lag1'] = df.groupby('country')['wind_electricity'].shift(1)
    df['wind_lag2'] = df.groupby('country')['wind_electricity'].shift(2)
    df['renewable_lag1'] = df.groupby('country')['renewable_share_pct'].shift(1)
    df['wind_rolling3'] = df.groupby('country')['wind_electricity']\
                            .transform(lambda x: x.rolling(3, min_periods=1).mean())

    # Predict next year (2026)
    latest = df[df['year'] == df['year'].max()].copy()
    latest['year'] = latest['year'] + 1
    latest['year_norm'] = (latest['year'] - 2000) / 25
    latest['wind_lag2'] = latest['wind_lag1']
    latest['wind_lag1'] = latest['wind_electricity']

    features = ['country_encoded', 'year_norm', 'wind_lag1',
                'wind_lag2', 'wind_rolling3', 'renewable_lag1']

    latest['predicted_wind_electricity'] = model.predict(latest[features])
    latest['predicted_at'] = datetime.now()

    result = latest[['country', 'year', 'predicted_wind_electricity', 'predicted_at']]

    # Save to database
    result.to_sql('wind_predictions', engine, schema='ml',
                  if_exists='replace', index=False)

    print(f'✅ Predictions saved for {len(result)} countries')
    print(result[['country', 'predicted_wind_electricity']].to_string())
    return result

if __name__ == '__main__':
    generate_predictions()