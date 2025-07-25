import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.losses import MeanSquaredError

def compute_features(df):
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(5).std()
    df["volume_norm"] = df["volume"] / df["volume"].rolling(5).mean()
    df = df.dropna()
    return df[["returns", "volatility", "volume_norm"]]

def build_autoencoder(input_dim):
    model = Sequential([
        Dense(8, activation="relu", input_shape=(input_dim,)),
        Dense(3, activation="relu"),
        Dense(8, activation="relu"),
        Dense(input_dim, activation="linear")
    ])
    model.compile(optimizer="adam", loss=MeanSquaredError())
    return model

def detect_anomalies(df, ticker="???"):
    X = compute_features(df).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = build_autoencoder(X_scaled.shape[1])
    model.fit(X_scaled, X_scaled, epochs=20, batch_size=8, verbose=0)

    X_pred = model.predict(X_scaled)
    reconstruction_error = np.mean((X_scaled - X_pred) ** 2, axis=1)

    df = df.iloc[-len(reconstruction_error):]
    df["anomaly_score"] = reconstruction_error
    return df[["anomaly_score"]]

import os
import csv
from datetime import datetime

ANOMALY_LOG = "logs/anomaly_log.csv"

def log_anomaly_scores(anomaly_dict):
    os.makedirs("logs", exist_ok=True)
    now = datetime.utcnow().isoformat()
    with open(os.path.join("logs", ANOMALY_LOG), "a", newline="") as f:
        writer = csv.writer(f)
        for ticker, score in anomaly_dict.items():
            writer.writerow([now, ticker, round(score, 6)])

