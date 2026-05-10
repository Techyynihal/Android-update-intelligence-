"""
ML Model Training Script for Android Update Predictor
Trains Random Forest models on synthetic historical data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

def train_model():
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'update_data.csv')
    df = pd.read_csv(data_path)

    print(f"[*] Loaded {len(df)} training samples")

    # Encode categorical features
    le_brand = LabelEncoder()
    le_model = LabelEncoder()

    df['brand_enc'] = le_brand.fit_transform(df['brand'])
    df['model_enc'] = le_model.fit_transform(df['model'])

    # Features
    feature_cols = ['brand_enc', 'model_enc', 'launch_year', 'android_ver', 'update_months', 'patch_freq']
    X = df[feature_cols].values

    # Targets
    y_eta = df['eta_months'].values
    y_conf = df['confidence'].values

    # Train ETA model
    X_train, X_test, y_train_eta, y_test_eta = train_test_split(X, y_eta, test_size=0.2, random_state=42)

    eta_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
    eta_model.fit(X_train, y_train_eta)

    eta_pred = eta_model.predict(X_test)
    print(f"[*] ETA model MAE: {mean_absolute_error(y_test_eta, eta_pred):.2f} months")

    # Train confidence model
    conf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
    conf_model.fit(X_train, y_conf[:len(X_train)])

    # Save all artifacts
    model_data = {
        'eta_model': eta_model,
        'conf_model': conf_model,
        'le_brand': le_brand,
        'le_model': le_model,
        'feature_cols': feature_cols,
        'brands': df['brand'].unique().tolist(),
        'brand_models': df.groupby('brand')['model'].apply(list).to_dict(),
    }

    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(model_data, model_path)
    print(f"[✓] Model saved to {model_path}")

    return model_data

if __name__ == '__main__':
    train_model()
