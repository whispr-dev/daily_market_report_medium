"""
Data fetching module for retrieving stock data.
"""
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Change from relative import to absolute import
from utils.data_utils import clean_yfinance_dataframe, fix_missing_values
from config import DEFAULT_UNIVERSE, DEFAULT_LOOKBACK_PERIOD, STOCKS_UNIVERSE_FILE

def load_stock_universe():
    """Load the stock universe from a CSV file or use the default."""
    if os.path.exists(STOCKS_UNIVERSE_FILE):
        try:
            df = pd.read_csv(STOCKS_UNIVERSE_FILE)
            print(f"Loaded {len(df)} symbols from {STOCKS_UNIVERSE_FILE}")
            return df
        except Exception as e:
            print(f"Error loading {STOCKS_UNIVERSE_FILE}: {e}")
    else:
        print(f"File {STOCKS_UNIVERSE_FILE} not found, using default universe.")
    
    return DEFAULT_UNIVERSE.copy()

def get_stock_data(symbol, period=DEFAULT_LOOKBACK_PERIOD):
    """Fetch stock data for a given symbol and period."""
    try:
        data = yf.download(symbol, period=period, progress=False)
        if data.empty:
            return None
        
        # Clean the data
        data = clean_yfinance_dataframe(data)
        data = fix_missing_values(data)
        
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None