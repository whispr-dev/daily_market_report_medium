import pandas as pd
from mod.fetcher import get_stock_data

def detect_dark_pool_signals(tickers, period="1mo", threshold=1.5):
    alerts = []

    for ticker in tickers:
        try:
            df = get_stock_data(ticker, period=period)
            if df is None or len(df) < 30:
                continue

            df['obv'] = (df['close'].diff() * df['volume']).fillna(0).cumsum()
            df['avg_vol'] = df['volume'].rolling(20).mean()
            df['vol_spike'] = df['volume'] > df['avg_vol'] * threshold

            # Recent divergence
            if df.iloc[-1]['vol_spike'] and df['close'].iloc[-1] <= df['close'].rolling(5).max().iloc[-1]:
                alerts.append({
                    "ticker": ticker,
                    "volume": int(df.iloc[-1]['volume']),
                    "avg_volume": int(df.iloc[-1]['avg_vol']),
                    "divergence": "stealth accumulation"
                })

        except Exception as e:
            print(f"Dark pool fail: {ticker}: {e}")
            continue

    return alerts

    import os
import csv
from datetime import datetime

DARK_LOG = "dark_pool_log.csv"

def log_dark_pool_alerts(alerts):
    if not alerts:
        return

    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", DARK_LOG), "a", newline="") as f:
        writer = csv.writer(f)
        for alert in alerts:
            writer.writerow([
                datetime.utcnow().isoformat(),
                alert["ticker"],
                alert["volume"],
                alert["avg_volume"],
                alert["divergence"]
            ])

