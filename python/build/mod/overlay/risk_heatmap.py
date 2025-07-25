from mod.analysis.indicators import detect_reversal_signals
from mod.fetcher import get_stock_data

def compute_reversal_risk(universe, period="3mo"):
    risk_summary = {
        "high_risk": [],
        "low_risk": [],
        "neutral": []
    }

    for ticker in universe:
        try:
            df = get_stock_data(ticker, period=period)
            if df is None or len(df) < 30:
                continue

            rev = detect_reversal_signals(df)

            if rev.get("bearish"):
                risk_summary["high_risk"].append(ticker)
            elif rev.get("bullish"):
                risk_summary["low_risk"].append(ticker)
            else:
                risk_summary["neutral"].append(ticker)

        except Exception as e:
            print(f"Risk heatmap error {ticker}: {e}")
            continue

    return risk_summary

import os
import csv
from datetime import datetime

RISK_LOG = "risk_heatmap_log.csv"

def log_reversal_risk_summary(summary):
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", RISK_LOG), "a", newline="") as f:
        writer = csv.writer(f)
        now = datetime.utcnow().isoformat()
        writer.writerow([
            now,
            len(summary.get("high_risk", [])),
            len(summary.get("low_risk", [])),
            len(summary.get("neutral", []))
        ])

