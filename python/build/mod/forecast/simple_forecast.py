import numpy as np
from sklearn.linear_model import Ridge
from mod.fetcher import get_stock_data

def forecast_trend(tickers, days=5):
    forecasts = []

    for ticker in tickers:
        try:
            df = get_stock_data(ticker, period="3mo")
            if df is None or len(df) < 40:
                continue

            closes = df["close"].values[-30:]
            X = np.arange(len(closes)).reshape(-1, 1)
            y = closes

            model = Ridge()
            model.fit(X, y)

            future_x = np.array([[len(closes) + i] for i in range(1, days+1)])
            preds = model.predict(future_x)
            slope = preds[-1] - preds[0]
            norm = slope / y[-1]  # normalize vs price

            forecasts.append({
                "ticker": ticker,
                "slope": round(norm * 100, 2)
            })

        except Exception as e:
            print(f"Forecast fail {ticker}: {e}")
            continue

    return forecasts

import os
import csv
from datetime import datetime

FORECAST_LOG = "forecast_overlay_log.csv"

def log_forecast_data(forecasts):
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", FORECAST_LOG), "a", newline="") as f:
        writer = csv.writer(f)
        now = datetime.utcnow().isoformat()
        for entry in forecasts:
            writer.writerow([now, entry["ticker"], entry["slope"]])

