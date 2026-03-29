import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def load_dataset():
    file_path = os.path.join('dataset', 'climate_data_2000_2024.csv')
    df = pd.read_csv(file_path)

    # Rename columns
    df = df.rename(columns={
        'Temperature(C)': 'temperature',
        'Humidity(%)': 'humidity',
        'CO2(ppm)': 'co2',
        'Rainfall(mm)': 'rainfall'
    })

    # ✅ FORCE NUMERIC (CRITICAL FIX)
    numeric_cols = ['temperature', 'humidity', 'co2', 'rainfall', 'Year', 'Month']

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # ✅ REMOVE BAD ROWS (NaN)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    return df


def detect_anomalies(df):
    temp_col = df['temperature']

    mean = temp_col.mean()
    std = temp_col.std()

    df['z_score'] = (temp_col - mean) / std
    df['anomaly'] = df['z_score'].apply(lambda x: 1 if abs(x) > 2 else 0)

    return df

def train_models(df):

    # ✅ ADD IMPORTANT FEATURES
    X = df[['co2', 'humidity', 'rainfall', 'Year', 'Month']]
    y = df['temperature']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Models
    lr = LinearRegression()
    rf = RandomForestRegressor(n_estimators=100, random_state=42)

    lr.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    # Accuracy (R²)
    lr_score = r2_score(y_test, lr.predict(X_test))
    rf_score = r2_score(y_test, rf.predict(X_test))

    return {
        'Linear Regression': (lr, lr_score),
        'Random Forest': (rf, rf_score)
    }


def make_prediction(model, co2, humidity, rainfall, year, month):
    data = np.array([[co2, humidity, rainfall, year, month]])
    return round(model.predict(data)[0], 2)