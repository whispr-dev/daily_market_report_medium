import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
import base64

def img_to_base64(fig):
    """Utility to convert a Matplotlib figure to base64-encoded PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)  # Close figure to free memory
    return img_data

def get_multiple_tickers_data(symbols, period='1mo'):
    """
    Get data for multiple tickers at once using the Tickers object.
    This is more efficient than making separate API calls.
    
    Args:
        symbols (list): List of ticker symbols
        period (str): Time period to fetch (default: '1mo')
        
    Returns:
        dict: Dictionary with various dataframes (price, volume, etc.)
    """
    # Convert list to space-separated string if needed
    if isinstance(symbols, list):
        symbols = ' '.join(symbols)
    
    # Create Tickers object
    tickers = yf.Tickers(symbols)
    
    # Get historical data for all tickers at once
    hist = tickers.history(period=period)
    
    # Also get the current info for each ticker
    current_data = {}
    for symbol in tickers.symbols:
        try:
            ticker_info = tickers.tickers[symbol].info
            current_data[symbol] = {
                'bid': ticker_info.get('bid', None),
                'ask': ticker_info.get('ask', None),
                'dayHigh': ticker_info.get('dayHigh', None),
                'dayLow': ticker_info.get('dayLow', None),
                'fiftyTwoWeekHigh': ticker_info.get('fiftyTwoWeekHigh', None),
                'fiftyTwoWeekLow': ticker_info.get('fiftyTwoWeekLow', None),
                'shortName': ticker_info.get('shortName', symbol),
                'sector': ticker_info.get('sector', 'Unknown')
            }
        except Exception as e:
            print(f"Error getting info for {symbol}: {e}")
            current_data[symbol] = {}
    
    return {
        'historical': hist,
        'current': current_data
    }

def analyze_dividend_history(symbols, period='1y'):
    """
    Analyze dividend history for the given symbols.
    
    Args:
        symbols (list): List of ticker symbols
        period (str): Time period to fetch
        
    Returns:
        pandas.DataFrame: DataFrame with dividend information
    """
    if isinstance(symbols, list):
        symbols = ' '.join(symbols)
    
    tickers = yf.Tickers(symbols)
    
    # Get historical data with actions (dividends, splits)
    hist = tickers.history(period=period, actions=True)
    
    # Extract just the dividends
    dividends = hist['Dividends']
    
    # Filter out zero dividends
    dividends = dividends[dividends > 0]
    
    # Calculate dividend stats
    dividend_stats = {}
    for symbol in tickers.symbols:
        try:
            # Get symbol-specific dividends
            if isinstance(dividends, pd.DataFrame):
                symbol_dividends = dividends[symbol].dropna()
            else:
                # Handle the case where there's only one ticker
                symbol_dividends = dividends.dropna()
            
            if len(symbol_dividends) > 0:
                latest_dividend = symbol_dividends.iloc[-1]
                annual_dividend = symbol_dividends.sum()
                dividend_count = len(symbol_dividends)
                
                # Get current price for yield calculation
                current_price = tickers.tickers[symbol].info.get('regularMarketPrice', None)
                if current_price:
                    dividend_yield = (annual_dividend / current_price) * 100
                else:
                    dividend_yield = None
                
                dividend_stats[symbol] = {
                    'latest_dividend': latest_dividend,
                    'annual_dividend': annual_dividend,
                    'dividend_count': dividend_count,
                    'dividend_yield': dividend_yield
                }
            else:
                dividend_stats[symbol] = {
                    'latest_dividend': 0,
                    'annual_dividend': 0,
                    'dividend_count': 0,
                    'dividend_yield': 0
                }
        except Exception as e:
            print(f"Error analyzing dividends for {symbol}: {e}")
            dividend_stats[symbol] = {
                'latest_dividend': None,
                'annual_dividend': None,
                'dividend_count': 0,
                'dividend_yield': None
            }
    
    return pd.DataFrame.from_dict(dividend_stats, orient='index')

def generate_long_term_comparison_chart(symbols, years=10):
    """
    Generate a chart comparing the long-term performance of multiple stocks.
    
    Args:
        symbols (list): List of ticker symbols
        years (int): Number of years of historical data to use
        
    Returns:
        str: Base64-encoded PNG image
    """
    # Calculate start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    # Download the historical data
    if isinstance(symbols, list):
        symbols_str = ' '.join(symbols)
    else:
        symbols_str = symbols
        symbols = symbols_str.split()
    
    # Download data for all symbols at once
    df = yf.download(symbols_str, start=start_date, end=end_date, interval='1mo')['Adj Close']
    
    # Normalize to the starting price (100%)
    normalized_df = pd.DataFrame()
    for symbol in symbols:
        if symbol in df.columns:
            first_valid_price = df[symbol].dropna().iloc[0]
            normalized_df[symbol] = df[symbol] / first_valid_price * 100
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot each symbol
    for symbol in normalized_df.columns:
        normalized_df[symbol].plot(ax=ax, linewidth=2, label=symbol)
    
    # Add styling
    ax.set_title(f'Normalized Stock Price Comparison (Last {years} Years)', fontsize=16)
    ax.set_ylabel('Normalized Price (%)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper left', fontsize=12)
    
    # Add annotations for final values
    for symbol in normalized_df.columns:
        final_value = normalized_df[symbol].dropna().iloc[-1]
        ax.annotate(f'{symbol}: {final_value:.1f}%', 
                   xy=(df.index[-1], final_value),
                   xytext=(10, 0),
                   textcoords='offset points',
                   fontsize=11,
                   va='center')
    
    plt.tight_layout()
    
    return img_to_base64(fig)

def generate_volatility_comparison(symbols, period='1y'):
    """
    Generate a volatility comparison chart for the given symbols.
    
    Args:
        symbols (list): List of ticker symbols
        period (str): Time period to fetch
        
    Returns:
        str: Base64-encoded PNG image
    """
    if isinstance(symbols, list):
        symbols_str = ' '.join(symbols)
    else:
        symbols_str = symbols
        symbols = symbols_str.split()
    
    # Download data for all symbols at once
    df = yf.download(symbols_str, period=period, interval='1d')['Adj Close']
    
    # Calculate daily returns
    returns = df.pct_change().dropna()
    
    # Calculate volatility (standard deviation of returns)
    volatility = returns.std() * np.sqrt(252) * 100  # Annualized and converted to percentage
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = volatility.sort_values(ascending=False).plot(kind='bar', ax=ax, color='skyblue')
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars.patches):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f'{bar.get_height():.1f}%',
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    # Add styling
    ax.set_title('Annualized Volatility Comparison', fontsize=16)
    ax.set_ylabel('Volatility (%)', fontsize=12)
    ax.set_xlabel('Symbol', fontsize=12)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    return img_to_base64(fig)

def get_current_bid_ask_spreads(symbols):
    """
    Get current bid-ask spreads for the given symbols.
    
    Args:
        symbols (list): List of ticker symbols
        
    Returns:
        pandas.DataFrame: DataFrame with bid-ask spread information
    """
    if isinstance(symbols, list):
        symbols_str = ' '.join(symbols)
    else:
        symbols_str = symbols
        symbols = symbols_str.split()
    
    tickers = yf.Tickers(symbols_str)
    
    bid_ask_data = {}
    for symbol in symbols:
        try:
            ticker_info = tickers.tickers[symbol].info
            
            bid = ticker_info.get('bid', None)
            ask = ticker_info.get('ask', None)
            
            if bid is not None and ask is not None and bid > 0 and ask > 0:
                spread = ask - bid
                spread_pct = (spread / bid) * 100
            else:
                spread = None
                spread_pct = None
            
            bid_ask_data[symbol] = {
                'bid': bid,
                'ask': ask,
                'spread': spread,
                'spread_pct': spread_pct
            }
        except Exception as e:
            print(f"Error getting bid-ask data for {symbol}: {e}")
            bid_ask_data[symbol] = {
                'bid': None,
                'ask': None,
                'spread': None,
                'spread_pct': None
            }
    
    return pd.DataFrame.from_dict(bid_ask_data, orient='index')

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
    
    # Save the charts to files
    with open("long_term_comparison.html", "w") as f:
        f.write(f"<img src='data:image/png;base64,{long_term_chart_b64}'>")
    
    with open("volatility_comparison.html", "w") as f:
        f.write(f"<img src='data:image/png;base64,{volatility_chart_b64}'>")
    
    print("\nDemo completed! Charts saved as HTML files.")

if __name__ == "__main__":
    main()