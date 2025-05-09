import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mod.fetcher import get_stock_data
import os

LOG_FILE = "edge_prediction_log.csv"
RESULTS_FILE = "edge_backtest_results.csv"

def run_backtest(lookahead_days=5, min_confidence=50):
    if not os.path.exists(LOG_FILE):
        print("No prediction log found.")
        return

    df = pd.read_csv(LOG_FILE, names=[
        "timestamp", "ticker", "predicted_score", "confidence", "raw_score", "price_at_prediction"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[df["confidence"] >= min_confidence]

    results = []

    for _, row in df.iterrows():
        try:
            ticker = row["ticker"]
            date = row["timestamp"]
            predicted = row["predicted_score"]
            price_then = row["price_at_prediction"]

            df_hist = get_stock_data(ticker, period="3mo")
            if df_hist is None or df_hist.empty:
                continue

            df_hist.index = pd.to_datetime(df_hist.index)
            df_hist = df_hist[df_hist.index > date]

            if len(df_hist) < lookahead_days:
                continue

            future_price = df_hist.iloc[lookahead_days - 1]["close"]
            pct_change = (future_price - price_then) / price_then * 100

            results.append({
                "ticker": ticker,
                "predicted": predicted,
                "confidence": row["confidence"],
                "return": round(pct_change, 2),
                "timestamp": date
            })

        except Exception as e:
            print(f"Backtest fail on {ticker}: {e}")
            continue

    result_df = pd.DataFrame(results)
    result_df.to_csv(RESULTS_FILE, index=False)
    print(f"✅ Backtest complete. Saved to {RESULTS_FILE}")

    return result_df

def plot_backtest_summary(result_df):
    import seaborn as sns

    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="predicted", y="return", data=result_df, hue="confidence", palette="coolwarm")
    plt.axhline(0, color="gray", linestyle="--")
    plt.xlabel("Predicted Edge Score")
    plt.ylabel(f"Return over period")
    plt.title("Whispr Edge™ Score vs. Real Return")
    plt.tight_layout()
    plt.show()
