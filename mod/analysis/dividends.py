"""
Functions for analyzing dividend history and metrics.
"""
import pandas as pd
import yfinance as yf

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