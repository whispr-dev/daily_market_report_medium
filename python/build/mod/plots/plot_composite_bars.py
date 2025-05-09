import pandas as pd
import matplotlib.pyplot as plt

def plot_composite_scores(path="logs/whispr_edge_composites.csv", top_n=10):
    df = pd.read_csv(path, names=["timestamp", "ticker", "score", "reasons"])
    latest = df[df["timestamp"] == df["timestamp"].max()]
    latest = latest.sort_values("score", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(latest["ticker"], latest["score"], color="limegreen")
    plt.xlabel("Composite Score")
    plt.title("Top Whispr Edge™ Composite Scores")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
