from mod.utils.image_utils import fig_to_png_bytes
"""
Enhanced data fetching functions for multiple assets, metadata, and safe downloading.
"""
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timedelta

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

def safe_download(symbol, period=None, start=None, end=None, interval='1d'):
    """
    Safely download data with better error handling.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y')
        start: Start date (datetime or string)
        end: End date (datetime or string)
        interval: Data frequency ('1d', '1wk', '1mo')
        
    Returns:
        DataFrame with market data or None if download fails
    """
    try:
        # If using end parameter, make sure to specify start as well
        if end is not None and start is None:
            print(f"Warning: When using 'end' parameter, 'start' should also be specified for {symbol}")
            # Default to 1 year before end date
            end_date = pd.to_datetime(end)
            start = (end_date - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
        
        df = yf.download(symbol, period=period, start=start, end=end, 
                        interval=interval, progress=False)
        
        if df.empty:
            print(f"Warning: No data returned for {symbol}")
            return None
            
        return df
    except Exception as e:
        print(f"Error downloading {symbol}: {e}")
        return None

def get_instrument_metadata(symbol):
    """
    Get metadata about a financial instrument.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        dict with instrument metadata or None if retrieval fails
    """
    try:
        ticker = yf.Ticker(symbol)
        metadata = ticker.history_metadata
        return {
            'currency': metadata.get('currency', 'Unknown'),
            'exchange': metadata.get('exchangeName', 'Unknown'),
            'type': metadata.get('instrumentType', 'Unknown'),
            'timezone': metadata.get('timezone', 'Unknown')
        }
    except Exception as e:
        print(f"Error getting metadata for {symbol}: {e}")
        return None