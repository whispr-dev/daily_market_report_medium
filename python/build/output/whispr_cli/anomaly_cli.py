from plots.plot_anomaly_trend import plot_anomaly_trend
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anomaly Score Viewer")
    parser.add_argument("--ticker", help="Ticker to focus on (optional)", default=None)
    args = parser.parse_args()

    plot_anomaly_trend(ticker=args.ticker)
