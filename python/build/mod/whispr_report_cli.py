import argparse
from mod.main_enhanced import main as generate_report
from plots.plot_risk_trend import plot_risk_trend
from plots.plot_forecast_slope import plot_forecast_slope
from plots.plot_composite_bars import plot_composite_scores
from whispr_cli.composite_cli import print_top_scores

def main():
    parser = argparse.ArgumentParser(description="Whispr Report CLI")
    parser.add_argument("--html", action="store_true", help="Generate full HTML report")
    parser.add_argument("--top", action="store_true", help="Show top composite scores")
    parser.add_argument("--risk", action="store_true", help="Plot reversal risk trend")
    parser.add_argument("--forecast", action="store_true", help="Plot forecast slope trend")
    parser.add_argument("--composite", action="store_true", help="Bar chart of composite scores")
    parser.add_argument("--all", action="store_true", help="Run everything")

    args = parser.parse_args()

    if args.all or args.html:
        print("Generating full Whispr Edge™ HTML report...")
        generate_report()

    if args.all or args.top:
        print("\n🧠 Top Whispr Edge™ Composite Scores:")
        print_top_scores()

    if args.all or args.risk:
        print("\n📈 Reversal Risk Trend:")
        plot_risk_trend()

    if args.all or args.forecast:
        print("\n📉 Forecast Slope Trend:")
        plot_forecast_slope()

    if args.all or args.composite:
        print("\n🎯 Composite Score Chart:")
        plot_composite_scores()

if __name__ == "__main__":
    main()
