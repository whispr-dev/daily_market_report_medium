"""
Enhanced Daily Stock Market Report Generator
Main application entry point with multi-asset support.
"""
import os
import traceback
import pandas as pd
from datetime import datetime

# Internal imports
from mod.config import ensure_directories_exist

# Data handling
from mod.data.fetcher import fetch_symbol_data, load_stock_universe, fetch_stock_data, fetch_stock_info, fetch_market_data, fetch_stock_news
from mod.data.multi_asset import generate_multi_asset_report

# Analysis modules
from mod.analysis.market import calculate_percent_changes, find_technical_patterns, find_trading_opportunities, get_market_summary
from mod.analysis.dividend import analyze_dividend_history

# Visualization modules
from mod.visualization.candlestick import generate_candlestick_chart
from mod.visualization.indicators import generate_enhanced_candlestick_chart
from mod.visualization.sector import generate_sector_heatmap
from mod.visualization.macro import generate_macro_chart
from mod.visualization.currency import generate_forex_chart
from mod.visualization.comparison import generate_volatility_comparison

# Reporting modules
from mod.reporting.html_generator import prepare_report_data, render_html_report, save_html_report
from mod.reporting.email_sender import send_report_email

def main():
    """Main function to generate and send the enhanced daily market report."""
    print("Starting Enhanced Daily Market Report generation...")
    
    try:
        # Ensure required directories exist
        ensure_directories_exist()
            
        # 1) Load stock universe
        df_universe = load_stock_universe()
        print(f"Loaded {len(df_universe)} symbols.")

        # 2) Calculate daily percent changes
        print("Calculating daily percent changes...")
        df_universe = calculate_percent_changes(df_universe)

        # 3) Find technical patterns
        print("Finding 52-week highs and 200-day MA crossovers...")
        fifty_two_week_high, crossover_200d, technical_errors = find_technical_patterns(df_universe)
        
        # 4) Find trading opportunities
        print("Finding trading opportunities...")
        trading_signals = find_trading_opportunities(df_universe)
        
        # 5) Analyze dividend history for select stocks (e.g., top 5 by market cap)
        print("Analyzing dividends for top stocks...")
        top_stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        dividend_analysis = analyze_dividend_history(top_stocks)
        
        # 6) Generate multi-asset report
        print("Generating multi-asset report...")
        multi_asset_data = generate_multi_asset_report()
        
        # Combine error lists
        all_errors = technical_errors + (trading_signals.get('errors', []) if isinstance(trading_signals, dict) and 'errors' in trading_signals else [])

        # 7) Get S&P 500 market summary
        print("Getting S&P 500 data...")
        market_summary = get_market_summary()

        # 8) Generate charts
        print("Generating standard candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        print("Generating enhanced chart with reversal indicators...")
        # Get data for a representative stock (e.g., the first one or SPY)
        enhanced_b64 = None
        if isinstance(df_universe, list):
            # Handle if df_universe is a list
            if len(df_universe) > 0:
                # Use the first stock from the universe
                representative_ticker = df_universe[0]
                stock_data = fetch_symbol_data(representative_ticker, period="3mo", interval="1d")
                
                # Generate enhanced chart with the stock data if we got valid data
                if stock_data is not None and not stock_data.empty:
                    enhanced_b64 = generate_enhanced_candlestick_chart(
                        df=stock_data, 
                        ticker=representative_ticker,
                        output_dir="output/charts"
                    )
        else:
            # Handle if df_universe is a DataFrame
            if isinstance(df_universe, pd.DataFrame) and len(df_universe) > 0 and 'symbol' in df_universe.columns:
                # Use the first stock from the universe
                representative_ticker = df_universe['symbol'].iloc[0]
                stock_data = fetch_symbol_data(representative_ticker, period="3mo", interval="1d")
                
                # Generate enhanced chart with the stock data if we got valid data
                if stock_data is not None and not stock_data.empty:
                    enhanced_b64 = generate_enhanced_candlestick_chart(
                        df=stock_data, 
                        ticker=representative_ticker,
                        output_dir="output/charts"
                    )
        
        # Fallback to SPY if we couldn't generate an enhanced chart
        if enhanced_b64 is None:
            # Fallback to SPY if universe is empty
            spy_data = fetch_symbol_data("SPY", period="3mo", interval="1d")
            if spy_data is not None and not spy_data.empty:
                enhanced_b64 = generate_enhanced_candlestick_chart(
                    df=spy_data, 
                    ticker="SPY",
                    output_dir="output/charts")
        
        print("Generating sector heatmap...")
        heatmap_b64 = generate_sector_heatmap(df_universe)
        
        print("Generating macro chart...")
        macro_b64 = generate_macro_chart()
        
        print("Generating forex chart...")
        forex_b64 = generate_forex_chart()
        
        print("Generating volatility comparison...")
        volatility_b64 = generate_volatility_comparison(top_stocks)
        
        # Collect all charts
        charts = {
            'candlestick': candle_b64,
            'enhanced': enhanced_b64,
            'heatmap': heatmap_b64,
            'macro': macro_b64,
            'forex': forex_b64,
            'volatility': volatility_b64
        }
        
        # Collect technical signals
        technical_signals = {
            'fifty_two_week_high': fifty_two_week_high if isinstance(fifty_two_week_high, list) else 
                                  (fifty_two_week_high.to_dict('records') if hasattr(fifty_two_week_high, 'to_dict') else []),
            'crossover_200d': crossover_200d if isinstance(crossover_200d, list) else 
                             (crossover_200d.to_dict('records') if hasattr(crossover_200d, 'to_dict') else [])
        }
        
        # 9) Prepare expanded report data
        print("Preparing enhanced report data...")
        # Extend the standard report_data function with our new data
        report_data = prepare_report_data(
            market_summary,
            charts,
            technical_signals,
            trading_signals,
            all_errors
        )
        
        # Prepare the dividend_analysis properly depending on its type
        if isinstance(dividend_analysis, dict):
            dividend_data = dividend_analysis
        elif hasattr(dividend_analysis, 'to_dict'):
            dividend_data = dividend_analysis.to_dict('index')
        else:
            dividend_data = {}
        
        # Add additional data from our new modules
        report_data.update({
            'dividend_analysis': dividend_data,
            'currency_data': multi_asset_data.get('currency', {}),
            'etf_data': multi_asset_data.get('etfs', {}),
            'forex_chart': forex_b64,
            'volatility_chart': volatility_b64
        })
        
        # 10) Render extended HTML report template
        # NOTE: You'll need to update your email_template.html to include the new sections
        print("Rendering HTML template...")
        html_output = render_html_report(report_data)
        
        # Save a local copy of the report
        report_filename = save_html_report(html_output)
        
        # 11) Send the report
        print("Sending report email...")
        send_report_email(html_output)
        
        print("Enhanced Daily Market Report completed successfully!")
        print(f"Report saved locally as {report_filename}")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        traceback.print_exc()
        
if __name__ == "__main__":
    main()