"""
Daily Stock Market Report Generator
Main application entry point.
"""
import os
import traceback
from datetime import datetime

# Internal imports
from config import ensure_directories_exist

# Data handling
from data.fetcher import load_stock_universe

# Analysis modules
from analysis.market import calculate_percent_changes, find_technical_patterns, find_trading_opportunities, get_market_summary

# Visualization modules
from visualization.candlestick import generate_candlestick_chart
from visualization.indicators import generate_enhanced_candlestick_chart
from visualization.sector import generate_sector_heatmap
from visualization.macro import generate_macro_chart

# Reporting modules
from reporting.html_generator import prepare_report_data, render_html_report, save_html_report
from reporting.email_sender import send_report_email

def main():
    """Main function to generate and send the daily stock market report."""
    print("Starting Daily Stonk Market Report generation...")
    
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
        
        # Combine error lists
        all_errors = technical_errors + trading_signals.get('errors', [])

        # 5) Get S&P 500 market summary
        print("Getting S&P 500 data...")
        market_summary = get_market_summary()

        # 6) Generate charts
        print("Generating standard candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        print("Generating enhanced chart with reversal indicators...")
        enhanced_b64 = generate_enhanced_candlestick_chart()
        
        print("Generating sector heatmap...")
        heatmap_b64 = generate_sector_heatmap(df_universe)
        
        print("Generating macro chart...")
        macro_b64 = generate_macro_chart()
        
        # Collect all charts
        charts = {
            'candlestick': candle_b64,
            'enhanced': enhanced_b64,
            'heatmap': heatmap_b64,
            'macro': macro_b64
        }
        
        # Collect technical signals
        technical_signals = {
            'fifty_two_week_high': fifty_two_week_high,
            'crossover_200d': crossover_200d
        }

        # 7) Prepare report data and render template
        print("