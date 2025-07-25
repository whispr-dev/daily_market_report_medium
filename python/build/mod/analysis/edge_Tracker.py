import os
import csv
from datetime import datetime, timedelta
import pandas as pd

EDGE_HISTORY_FILE = "edge_score_history.csv"

def save_edge_scores(edge_scores):
    """Append current run's Edge scores with timestamp to a CSV."""
    timestamp = datetime.utcnow().isoformat()

    with open(EDGE_HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for entry in edge_scores:
            writer.writerow([timestamp, entry["ticker"], entry["score"]])

def load_edge_history(days=5):
    """Load recent edge score history and return as DataFrame."""
    if not os.path.exists(EDGE_HISTORY_FILE):
        return pd.DataFrame(columns=["timestamp", "ticker", "score"])

    df = pd.read_csv(EDGE_HISTORY_FILE, names=["timestamp", "ticker", "score"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    cutoff = datetime.utcnow() - timedelta(days=days + 1)
    return df[df["timestamp"] > cutoff]
