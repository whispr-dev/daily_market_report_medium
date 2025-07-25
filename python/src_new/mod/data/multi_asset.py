from mod.utils.image_utils import fig_to_png_bytes
"""
Data fetching functions for multiple asset classes beyond equities.
"""
import yfinance as yf
from mod.utils.data_utils import clean_yfinance_dataframe

def get_equity_market_data():
    """
    Get equity market data.
    
    Returns:
        dict: Dictionary with equity market data
    """
    # Placeholder function, typically would call existing functions
    from .fetcher import fetch_symbol_data
    
    equity_data = {
        'sp500': fetch_symbol_data("^GSPC", period='1mo'),
        'dow': fetch_symbol_data("^DJI", period='1mo'),
        'nasdaq': fetch_symbol_data("^IXIC", period='1mo'),
    }
    
    return equity_data

def get_currency_data(symbols):
    """
    Extract currency data for the provided forex symbols.
    
    Args:
        symbols: List of currency pair symbols (e.g., 'EURUSD=X')
        
    Returns:
        dict: Dictionary with currency data for each symbol
    """
    results = {}
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.fast_info
            results[sym] = {
                'current_rate': info.get('lastPrice', None),
                'day_change': (info.get('lastPrice', 0) - info.get('previousClose', 0)) / info.get('previousClose', 1) * 100 
                               if info.get('previousClose', 0) != 0 else 0,
                '50d_avg': info.get('fiftyDayAverage', None),
                '200d_avg': info.get('twoHundredDayAverage', None)
            }
        except Exception as e:
            print(f"Error getting currency data for {sym}: {e}")
            results[sym] = {
                'current_rate': None,
                'day_change': None,
                '50d_avg': None,
                '200d_avg': None
            }
    
    return results

def get_etf_data(symbols):
    """
    Extract ETF data for the provided ETF symbols.
    
    Args:
        symbols: List of ETF symbols
        
    Returns:
        dict: Dictionary with ETF data for each symbol
    """
    results = {}
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            results[sym] = {
                'name': info.get('longName', ''),
                'yield': info.get('yield', 0) * 100 if 'yield' in info else 0,
                'category': info.get('category', ''),
                'ytd_return': info.get('ytdReturn', 0) * 100 if 'ytdReturn' in info else 0,
                'total_assets': info.get('totalAssets', 0)
            }
        except Exception as e:
            print(f"Error getting ETF data for {sym}: {e}")
            results[sym] = {
                'name': '',
                'yield': 0,
                'category': '',
                'ytd_return': 0,
                'total_assets': 0
            }
    
    return results

def generate_multi_asset_report():
    """
    Generate a comprehensive report covering multiple asset classes.
    
    Returns:
        dict: Dictionary with data for multiple asset classes
    """
    # Get equity data (already implemented)
    equity_data = get_equity_market_data()
    
    # Add currency data
    currency_data = get_currency_data(['EURUSD=X', 'USDJPY=X', 'GBPUSD=X'])
    
    # Add ETF data
    etf_data = get_etf_data(['GDX', 'SPY', 'QQQ'])
    
    # Combine into comprehensive report
    return {
        'equity': equity_data,
        'currency': currency_data,
        'etfs': etf_data
    }