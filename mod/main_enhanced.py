"""
Enhanced Daily Stock Market Report Generator
Main application entry point with multi-asset support.
"""
import os
import traceback
from datetime import datetime

# Internal imports
from config import ensure_directories_exist

# Data handling
from data.fetcher import load_stock_universe
from data.multi_asset import generate_multi_asset_report

# Analysis modules
from analysis.market import calculate_percent_changes, find_technical_patterns, find_trading_opportunities, get_market_summary
from analysis.dividend import analyze_dividend_history

# Visualization modules
from visualization.candlestick import generate_candlestick_chart
from visualization.indicators import generate_enhanced_candlestick_chart
from visualization.sector import generate_sector_heatmap
from visualization.macro import generate_macro_chart
from visualization.currency import generate_forex_chart
from visualization.comparison import generate_volatility_comparison

# Reporting modules
from reporting.html_generator import prepare_report_data, render_html_report, save_html_report
from reporting.email_sender import send_report_email

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
        all_errors = technical_errors + trading_signals.get('errors', [])

        # 7) Get S&P 500 market summary
        print("Getting S&P 500 data...")
        market_summary = get_market_summary()

        # 8) Generate charts
        print("Generating standard candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        print("Generating enhanced chart with reversal indicators...")
        enhanced_b64 = generate_enhanced_candlestick_chart()
        
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
            'fifty_two_week_high': fifty_two_week_high,
            'crossover_200d': crossover_200d
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
        
        # Add additional data from our new modules
        report_data.update({
            'dividend_analysis': dividend_analysis.to_dict(),
            'currency_data': multi_asset_data['currency'],
            'etf_data': multi_asset_data['etfs'],
            'forex_chart': forex_b64,
            'volatility_chart': volatility_b64
        })
        
        # 10) Render extended HTML report template
        # NOTE: You'll need to update your email_template.html to include the new sections
        print("Rendering HTML template...")
        html_output = render_html_report(report_data)
        
        # Save a local copy of the report
        report_filename = save_html_report(html_output)
        
        print(f"Report saved as {report_filename}")
        
        # Option to email the report
        # Uncomment the following line to enable email sending
        # send_report_email(report_data, html_output)
        
        print("Enhanced Daily Market Report generated successfully!")
        
    except Exception as e:
        print(f"Error generating market report: {str(e)}")
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    main()