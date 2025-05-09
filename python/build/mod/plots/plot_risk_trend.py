import pandas as pd
import matplotlib.pyplot as plt

def plot_risk_trend(log_path="logs/risk_heatmap_log.csv"):
    df = pd.read_csv(log_path, names=["timestamp", "high", "low", "neutral"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["high"], label="High Risk", color="red")
    plt.plot(df["timestamp"], df["low"], label="Low Risk", color="green")
    plt.plot(df["timestamp"], df["neutral"], label="Neutral", color="gray")

    plt.title("Reversal Risk Levels Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Stocks")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
