import pandas as pd
import matplotlib.pyplot as plt

def plot_forecast_slope(log_path="logs/forecast_overlay_log.csv", ticker=None):
    df = pd.read_csv(log_path, names=["timestamp", "ticker", "slope"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if ticker:
        df = df[df["ticker"] == ticker]
        plt.title(f"Forecast Slope Over Time — {ticker}")
    else:
        df = df.groupby(["timestamp"]).mean(numeric_only=True).reset_index()
        plt.title("Average Forecast Slope Over Time")

    plt.plot(df["timestamp"], df["slope"], label="Forecast Slope", color="blue")
    plt.axhline(0, linestyle="--", color="gray")
    plt.xlabel("Date")
    plt.ylabel("Slope (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
