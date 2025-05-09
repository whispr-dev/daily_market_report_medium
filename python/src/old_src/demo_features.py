"""
Demo script to demonstrate enhanced features of the financial analysis package.
"""
import os
from data.enhanced import get_multiple_tickers_data
from analysis.dividend import analyze_dividend_history, get_current_bid_ask_spreads
from visualization.comparison import generate_long_term_comparison_chart, generate_volatility_comparison
from visualization.currency import generate_forex_chart
from data.multi_asset import generate_multi_asset_report

def main():
    """Demo of all the enhanced features"""
    # Define a list of symbols to analyze
    symbols = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'AMZN', 'MSFT', 'GOOGL']
    
    # 1. Get data for multiple tickers at once
    print("Getting data for multiple tickers...")
    data = get_multiple_tickers_data(symbols)
    
    # Print some sample data
    print("\nSample of historical close prices:")
    print(data['historical']['Close'].tail())
    
    print("\nCurrent data for first symbol:")
    print(data['current'][symbols[0]])
    
    # 2. Analyze dividend history
    print("\nAnalyzing dividend history...")
    dividend_stats = analyze_dividend_history(symbols)
    print(dividend_stats)
    
    # 3. Generate long-term comparison chart
    print("\nGenerating long-term comparison chart...")
    long_term_chart_b64 = generate_long_term_comparison_chart(symbols, years=10)
    print("Chart generated!")
    
    # 4. Generate volatility comparison
    print("\nGenerating volatility comparison...")
    volatility_chart_b64 = generate_volatility_comparison(symbols)
    print("Chart generated!")
    
    # 5. Get current bid-ask spreads
    print("\nGetting current bid-ask spreads...")
    bid_ask_data = get_current_bid_ask_spreads(symbols)
    print(bid_ask_data)
    
    # 6. Generate forex chart
    print("\nGenerating forex chart...")
    forex_chart_b64 = generate_forex_chart()
    print("Forex chart generated!")
    
    # 7. Generate multi-asset report
    print("\nGenerating multi-asset report...")
    multi_asset_data = generate_multi_asset_report()
    print("Multi-asset report generated!")
    
    # Save the charts to files
    print("\nSaving charts to files...")
    os.makedirs("output", exist_ok=True)
    
    with open("output/long_term_comparison.html", "w") as f:
        f.write(f"<img src='data:image/png;base64,{long_term_chart_b64}'>")
    
    with open("output/volatility_comparison.html", "w") as f:
        f.write(f"<img src='data:image/png;base64,{volatility_chart_b64}'>")
        
    with open("output/forex_comparison.html", "w") as f:
        f.write(f"<img src='data:image/png;base64,{forex_chart_b64}'>")
    
    print("\nDemo completed! Charts saved as HTML files in the 'output' directory.")

if __name__ == "__main__":
    main()