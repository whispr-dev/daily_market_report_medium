"""
Data fetching functions for financial data.
"""
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
import numpy as np
from datetime import datetime
from ..utils.data_utils import clean_yfinance_dataframe, fix_missing_values

def fetch_symbol_data(symbol, period=None, interval='1d', start=None, end=None):
    """
    Download market data for a symbol using yfinance.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y')
        interval: Data frequency ('1d', '1wk', '1mo')
        start: Start date (datetime or string)
        end: End date (datetime or string)
        
    Returns:
        DataFrame with market data
    """
    try:
        # Use either period or start/end dates
        if period and (start or end):
            print("Warning: Both period and start/end specified. Using start/end dates.")
            
        if start or end:
            df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
        else:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            
        # Clean the dataframe
        df = clean_yfinance_dataframe(df)
        df = fix_missing_values(df)
        
        return df
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()  # Return empty dataframe on error

def fetch_fred_data(series_id, start=None, end=None):
    """
    Download economic data from FRED.
    
    Args:
        series_id: FRED series identifier (e.g., 'M2SL')
        start: Start date
        end: End date (defaults to today)
        
    Returns:
        DataFrame with FRED data
    """
    try:
        if end is None:
            end = datetime.today()
            
        df = pdr.DataReader(series_id, "fred", start, end)
        return df
        
    except Exception as e:
        print(f"Error fetching FRED data for {series_id}: {e}")
        return pd.DataFrame()  # Return empty dataframe on error

def load_stock_universe():
    """
    Load stock universe from CSV file.
    
    Returns:
        DataFrame with stock universe
    """
    from ..config import STOCKS_UNIVERSE_FILE, DEFAULT_UNIVERSE
    
    try:
        df_universe = pd.read_csv(STOCKS_UNIVERSE_FILE)
        df_universe.columns = df_universe.columns.str.strip().str.lower()
        
        if 'symbol' not in df_universe.columns:
            raise KeyError("The 'symbol' column is missing from stocks_universe.csv")
            
        # Add sector column if missing (needed for heatmap)
        if 'sector' not in df_universe.columns and 'sectordisp' in df_universe.columns:
            df_universe['sector'] = df_universe['sectordisp']
        elif 'sector' not in df_universe.columns:
            print("Warning: 'sector' column missing. Adding default sector for heatmap.")
            df_universe['sector'] = "Unknown"
            
        return df_universe
        
    except Exception as e:
        print(f"Error reading stock universe: {e}")
        print("Using default S&P 500 symbols...")
        return DEFAULT_UNIVERSE.copy()