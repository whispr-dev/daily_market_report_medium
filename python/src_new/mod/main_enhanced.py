"""
Final Enhanced Daily Stock Market Report Generator
Handles image bytes, inline email charts, and proper function wrapping.
"""
import os
import traceback
import pandas as pd
from datetime import datetime

from mod.config.mailing import load_mailing_list
recipients = load_mailing_list("mailing_list.txt")
from mod.config import ensure_directories_exist
from mod.data.fetcher import (
    fetch_symbol_data,
    load_stock_universe
)
from mod.data.multi_asset import generate_multi_asset_report
from mod.analysis.market import (
    calculate_percent_changes,
    find_technical_patterns,
    find_trading_opportunities,
    get_market_summary
)
from mod.analysis.dividend import analyze_dividend_history
from mod.visualization.candlestick import generate_candlestick_chart
from mod.visualization.indicators import generate_enhanced_candlestick_chart
from mod.visualization.sector import generate_sector_heatmap
from mod.visualization.macro import generate_macro_chart
from mod.visualization.currency import generate_forex_chart
from mod.visualization.comparison import generate_volatility_comparison
from mod.reporting.html_generator import prepare_report_data, render_html_report, save_html_report
from mod.reporting.email_sender import send_report_email
from mod.utils.image_utils import fig_to_png_bytes

def main():
    print("Starting Enhanced Daily Market Report generation...")

    try:
        ensure_directories_exist()
        df_universe = load_stock_universe()
        print(f"Loaded {len(df_universe)} symbols.")

        print("Calculating daily percent changes...")
        df_universe = calculate_percent_changes(df_universe)

        print("Finding 52-week highs and 200-day MA crossovers...")
        fifty_two_week_high, crossover_200d, technical_errors = find_technical_patterns(df_universe)

        print("Finding trading opportunities...")
        trading_signals = find_trading_opportunities(df_universe)

        print("Analyzing dividends for top stocks...")
        top_stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        dividend_analysis = analyze_dividend_history(top_stocks)

        print("Generating multi-asset report...")
        multi_asset_data = generate_multi_asset_report()

        all_errors = technical_errors + (trading_signals.get('errors', []) if isinstance(trading_signals, dict) and 'errors' in trading_signals else [])

        print("Getting S&P 500 data...")
        market_summary = get_market_summary()

        print("Generating standard candlestick chart...")
        candle_png_bytes = generate_candlestick_chart()

        print("Generating enhanced chart with reversal indicators...")
        enhanced_png_bytes = None

        if isinstance(df_universe, pd.DataFrame) and len(df_universe) > 0 and 'symbol' in df_universe.columns:
            representative_ticker = df_universe['symbol'].iloc[0]
            stock_data = fetch_symbol_data(representative_ticker, period="3mo", interval="1d")
            if stock_data is not None and not stock_data.empty:
                enhanced_fig = generate_enhanced_candlestick_chart(
                    df=stock_data,
                    ticker=representative_ticker,
                    output_dir="output/charts"
                )
                enhanced_png_bytes = fig_to_png_bytes(enhanced_fig)

        if enhanced_png_bytes is None:
            spy_data = fetch_symbol_data("SPY", period="3mo", interval="1d")
            if spy_data is not None and not spy_data.empty:
                enhanced_fig = generate_enhanced_candlestick_chart(
                    df=spy_data,
                    ticker="SPY",
                    output_dir="output/charts"
                )
                enhanced_png_bytes = fig_to_png_bytes(enhanced_fig)

        print("Generating sector heatmap...")
        heatmap_png_bytes = generate_sector_heatmap(df_universe)

        print("Generating macro chart...")
        macro_png_bytes = generate_macro_chart()

        print("Generating forex chart...")
        forex_png_bytes = generate_forex_chart()

        print("Generating volatility comparison...")
        volatility_png_bytes = generate_volatility_comparison(top_stocks)

        charts = {
            'candlestick': candle_png_bytes,
            'enhanced': enhanced_png_bytes,
            'heatmap': heatmap_png_bytes,
            'macro': macro_png_bytes,
            'forex': forex_png_bytes,
            'volatility': volatility_png_bytes
        }

        technical_signals = {
            'fifty_two_week_high': fifty_two_week_high if isinstance(fifty_two_week_high, list) else
                                  (fifty_two_week_high.to_dict('records') if hasattr(fifty_two_week_high, 'to_dict') else []),
            'crossover_200d': crossover_200d if isinstance(crossover_200d, list) else
                             (crossover_200d.to_dict('records') if hasattr(crossover_200d, 'to_dict') else [])
        }

        print("Preparing enhanced report data...")
        report_data = prepare_report_data(
            market_summary,
            charts,
            technical_signals,
            trading_signals,
            all_errors
        )

        if isinstance(dividend_analysis, dict):
            dividend_data = dividend_analysis
        elif hasattr(dividend_analysis, 'to_dict'):
            dividend_data = dividend_analysis.to_dict('index')
        else:
            dividend_data = {}

        report_data.update({
            'dividend_analysis': dividend_data,
            'currency_data': multi_asset_data.get('currency', {}),
            'etf_data': multi_asset_data.get('etfs', {})
        })

        print("Rendering HTML template...")
        html_output = render_html_report(report_data)

        report_filename = save_html_report(html_output)

        images = {
            'candle_chart': candle_png_bytes,
            'enhanced_chart': enhanced_png_bytes,
            'heatmap': heatmap_png_bytes,
            'macro_chart': macro_png_bytes,
            'forex_chart': forex_png_bytes,
            'volatility_chart': volatility_png_bytes,
        }

        print("Sending report email...")
        send_report_email(html_output, subject="Enhanced Market Report", images=images, recipients=recipients)

        print("Enhanced Daily Market Report completed successfully!")
        print(f"Report saved locally as {report_filename}")

    except Exception as e:
        print(f"Error generating report: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
