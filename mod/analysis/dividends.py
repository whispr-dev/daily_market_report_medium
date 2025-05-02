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
        dict: Dictionary with dividend information for each symbol
    """
    # Convert to list if it's a single symbol
    if isinstance(symbols, str):
        symbols = [symbols]
    
    # Join symbols with space for yfinance
    symbols_str = ' '.join(symbols)
    
    try:
        tickers = yf.Tickers(symbols_str)
        
        # Get historical data with actions (dividends, splits)
        hist = tickers.history(period=period, actions=True)
        
        # Extract just the dividends
        dividends = hist['Dividends'] if 'Dividends' in hist.columns else pd.DataFrame()
        
        # Initialize dictionary for results
        dividend_stats = {}
        
        # Process each symbol
        for symbol in symbols:
            try:
                # Get symbol-specific dividends
                if isinstance(dividends, pd.DataFrame) and symbol in dividends.columns:
                    symbol_dividends = dividends[symbol].dropna()
                    
                    # Skip if no dividends
                    if len(symbol_dividends) == 0:
                        dividend_stats[symbol] = {
                            'latest_dividend': 0,
                            'annual_dividend': 0,
                            'dividend_count': 0,
                            'dividend_yield': 0
                        }
                        continue
                    
                    # Calculate dividend metrics
                    latest_dividend = float(symbol_dividends.iloc[-1]) if len(symbol_dividends) > 0 else 0
                    annual_dividend = float(symbol_dividends.sum()) if len(symbol_dividends) > 0 else 0
                    dividend_count = len(symbol_dividends)
                    
                    # Get current price for yield calculation
                    try:
                        ticker_info = tickers.tickers[symbol].info
                        current_price = ticker_info.get('regularMarketPrice')
                        if current_price is not None and current_price > 0 and annual_dividend > 0:
                            dividend_yield = (annual_dividend / current_price) * 100
                        else:
                            dividend_yield = 0
                    except:
                        dividend_yield = 0
                    
                    # Store results
                    dividend_stats[symbol] = {
                        'latest_dividend': latest_dividend,
                        'annual_dividend': annual_dividend,
                        'dividend_count': dividend_count,
                        'dividend_yield': dividend_yield
                    }
                else:
                    # No dividends for this symbol
                    dividend_stats[symbol] = {
                        'latest_dividend': 0,
                        'annual_dividend': 0,
                        'dividend_count': 0,
                        'dividend_yield': 0
                    }
            except Exception as e:
                print(f"Error analyzing dividends for {symbol}: {e}")
                dividend_stats[symbol] = {
                    'latest_dividend': 0,
                    'annual_dividend': 0,
                    'dividend_count': 0,
                    'dividend_yield': 0
                }
        
        return dividend_stats
        
    except Exception as e:
        print(f"Error in analyze_dividend_history: {e}")
        # Return empty dict for all symbols
        return {symbol: {
            'latest_dividend': 0,
            'annual_dividend': 0,
            'dividend_count': 0,
            'dividend_yield': 0
        } for symbol in symbols}

def get_current_bid_ask_spreads(symbols):
    """
    Get current bid-ask spreads for the given symbols.
    
    Args:
        symbols (list): List of ticker symbols
        
    Returns:
        dict: Dictionary with bid-ask spread information for each symbol
    """
    # Convert to list if it's a single symbol
    if isinstance(symbols, str):
        symbols = [symbols]
    
    # Join symbols with space for yfinance
    symbols_str = ' '.join(symbols)
    
    try:
        tickers = yf.Tickers(symbols_str)
        
        bid_ask_data = {}
        for symbol in symbols:
            try:
                ticker_info = tickers.tickers[symbol].info
                
                bid = ticker_info.get('bid', 0)
                ask = ticker_info.get('ask', 0)
                
                if bid is not None and ask is not None and bid > 0 and ask > 0:
                    spread = ask - bid
                    spread_pct = (spread / bid) * 100
                else:
                    spread = 0
                    spread_pct = 0
                
                bid_ask_data[symbol] = {
                    'bid': bid,
                    'ask': ask,
                    'spread': spread,
                    'spread_pct': spread_pct
                }
            except Exception as e:
                print(f"Error getting bid-ask data for {symbol}: {e}")
                bid_ask_data[symbol] = {
                    'bid': 0,
                    'ask': 0,
                    'spread': 0,
                    'spread_pct': 0
                }
        
        return bid_ask_data
        
    except Exception as e:
        print(f"Error in get_current_bid_ask_spreads: {e}")
        # Return empty dict for all symbols
        return {symbol: {
            'bid': 0,
            'ask': 0,
            'spread': 0,
            'spread_pct': 0
        } for symbol in symbols}