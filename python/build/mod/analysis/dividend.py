from mod.utils.image_utils import fig_to_png_bytes
"""
Module for dividend analysis.
"""
import pandas as pd
import numpy as np
import yfinance as yf

def analyze_dividend_history(symbols, period='1y'):
    '''
    Analyze dividend history for the given symbols.
    
    Args:
        symbols (list or str): Symbol or list of symbols
        period (str): Time period (default: '1y')
        
    Returns:
        dict: Dictionary with dividend info for each symbol
    '''
    # Make sure symbols is a list
    if isinstance(symbols, str):
        symbols = [symbols]
    
    import yfinance as yf
    import pandas as pd
    
    results = {}
    
    for symbol in symbols:
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get dividend data
            hist = ticker.history(period=period)
            dividends = ticker.dividends
            
            # Check if dividends exist
            if dividends.empty:
                results[symbol] = {
                    'latest_dividend': 0,
                    'annual_dividend': 0,
                    'dividend_count': 0,
                    'dividend_yield': 0
                }
                continue
            
            # Calculate dividend metrics
            latest_dividend = float(dividends.iloc[-1]) if len(dividends) > 0 else 0
            annual_dividend = float(dividends.sum()) if len(dividends) > 0 else 0
            dividend_count = len(dividends)
            
            # Get current price for yield calculation
            ticker_info = ticker.info
            current_price = ticker_info.get('regularMarketPrice') or ticker_info.get('currentPrice')
            if current_price and annual_dividend > 0:
                dividend_yield = (annual_dividend / current_price) * 100
            else:
                dividend_yield = 0
            
            # Store results
            results[symbol] = {
                'latest_dividend': latest_dividend,
                'annual_dividend': annual_dividend,
                'dividend_count': dividend_count,
                'dividend_yield': dividend_yield
            }
        except Exception as e:
            print(f"Error analyzing dividends for {symbol}: {e}")
            results[symbol] = {
                'latest_dividend': 0,
                'annual_dividend': 0,
                'dividend_count': 0,
                'dividend_yield': 0,
                'error': str(e)
            }
    
    return results
def get_current_bid_ask_spreads(ticker):
    """
    Get the current bid-ask spread for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with bid-ask spread information
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Get stock info
        info = stock.info
        
        # Extract bid and ask data
        bid = info.get('bid', None)
        ask = info.get('ask', None)
        bid_size = info.get('bidSize', None)
        ask_size = info.get('askSize', None)
        
        if bid is None or ask is None:
            return {
                "ticker": ticker,
                "has_spread_data": False,
                "message": "Bid-ask data not available."
            }
        
        # Calculate spread
        spread = ask - bid
        spread_percent = (spread / ask) * 100 if ask > 0 else 0
        
        return {
            "ticker": ticker,
            "has_spread_data": True,
            "bid": bid,
            "ask": ask,
            "bid_size": bid_size,
            "ask_size": ask_size,
            "spread": spread,
            "spread_percent": spread_percent
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "has_spread_data": False,
            "error": str(e),
            "message": f"Error getting bid-ask spread for {ticker}."
        }