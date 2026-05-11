import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.db_connect import get_engine

def load_data():
    engine = get_engine()
    df = pd.read_sql('''
        SELECT country, year, wind_electricity,
               renewables_electricity, electricity_generation,
               renewable_share_pct, fossil_share_pct
        FROM marts.fact_energy_analytics
        ORDER BY country, year
    ''', engine)
    print(f'Loaded {len(df)} rows')
    return df

def engineer_features(df):
    df = df.sort_values(['country', 'year']).copy()

    # Encode country as number
    le = LabelEncoder()
    df['country_encoded'] = le.fit_transform(df['country'])

    # Normalise year
    df['year_norm'] = (df['year'] - 2000) / 25

    # Lag features
    df['wind_lag1'] = df.groupby('country')['wind_electricity'].shift(1)
    df['wind_lag2'] = df.groupby('country')['wind_electricity'].shift(2)
    df['renewable_lag1'] = df.groupby('country')['renewable_share_pct'].shift(1)

    # Rolling average
    df['wind_rolling3'] = df.groupby('country')['wind_electricity']\
                            .transform(lambda x: x.rolling(3, min_periods=1).mean())

    # Drop NaN rows
    df = df.dropna(subset=['wind_lag1', 'wind_lag2'])

    return df, le

def train_model(df):
    print('Training wind electricity model...')

    features = ['country_encoded', 'year_norm', 'wind_lag1',
                'wind_lag2', 'wind_rolling3', 'renewable_lag1']
    target = 'wind_electricity'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f'RMSE: {rmse:.2f} TWh')
    print(f'R2 Score: {r2:.3f}')

    return model

def save_model(model, le):
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/wind_model.pkl')
    joblib.dump(le, 'ml/models/label_encoder.pkl')
    print('✅ Models saved to ml/models/')

if __name__ == '__main__':
    df = load_data()
    df, le = engineer_features(df)
    model = train_model(df)
    save_model(model, le)
    print('Training complete!')