import pandas as pd
import matplotlib.pyplot as plt

def plot_anomaly_trend(log_path="logs/anomaly_log.csv", ticker=None):
    df = pd.read_csv(log_path, names=["timestamp", "ticker", "score"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if ticker:
        df = df[df["ticker"] == ticker]
        plt.title(f"Anomaly Score Over Time — {ticker}")
    else:
        df = df.groupby("timestamp").mean(numeric_only=True).reset_index()
        plt.title("Average Market Anomaly Over Time")

    plt.plot(df["timestamp"], df["score"], label="Anomaly Score", color="magenta")
    plt.axhline(df["score"].mean(), linestyle="--", color="gray", label="Mean")
    plt.xlabel("Date")
    plt.ylabel("Anomaly Score")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
