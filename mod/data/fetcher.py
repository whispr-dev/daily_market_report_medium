"""
Module for fetching stock data from various sources.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os

# Changed from relative to absolute import
from mod.utils.data_utils import clean_yfinance_dataframe, fix_missing_values

def load_stock_universe(universe_file=None):
    """
    Load the stock universe from a file or use default tickers.
    
    Args:
        universe_file (str): Path to the stock universe file
        
    Returns:
        list: List of stock tickers
    """
    try:
        if universe_file and os.path.exists(universe_file):
            print(f"Loading stock universe from: {universe_file}")
            with open(universe_file, 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
        else:
            # Default universe: S&P 500 top components
            print("Using default stock universe")
            tickers = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'BRK-B', 'UNH', 'JPM']
        
        return tickers
    except Exception as e:
        print(f"Error loading stock universe: {e}")
        # Return minimal default universe
        return ['AAPL', 'MSFT', 'SPY']

def fetch_stock_data(tickers, period="1y", interval="1d"):
    """
    Fetch historical stock data for the given tickers.
    
    Args:
        tickers (list): List of stock tickers
        period (str): Period to fetch data for (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval (str): Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
    Returns:
        dict: Dictionary of DataFrames with stock data
    """
    stock_data = {}
    
    for ticker in tickers:
        try:
            # Fetch data
            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False
            )
            
            if not data.empty:
                # Clean the data
                data = clean_yfinance_dataframe(data)
                data = fix_missing_values(data)
                
                stock_data[ticker] = data
            else:
                print(f"No data found for {ticker}")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    return stock_data

def fetch_stock_info(tickers):
    """
    Fetch detailed information about each stock.
    
    Args:
        tickers (list): List of stock tickers
        
    Returns:
        dict: Dictionary of stock information
    """
    stock_info = {}
    
    for ticker in tickers:
        try:
            # Create ticker object
            tick = yf.Ticker(ticker)
            
            # Get info
            info = tick.info
            
            if info:
                stock_info[ticker] = info
            else:
                print(f"No info found for {ticker}")
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
    
    return stock_info

def fetch_market_data():
    """
    Fetch overall market data (indices).
    
    Returns:
        dict: Dictionary of DataFrames with market index data
    """
    indices = [
        '^GSPC',    # S&P 500
        '^DJI',     # Dow Jones
        '^IXIC',    # NASDAQ
        '^VIX',     # Volatility Index
        '^TNX',     # 10-Year Treasury Yield
    ]
    
    market_data = fetch_stock_data(indices, period="1y", interval="1d")
    
    return market_data

def fetch_symbol_data(symbol, period="1mo", interval="1d"):
    """
    Fetch data for a specific symbol.
    
    Args:
        symbol (str): Stock symbol to fetch
        period (str): Period to fetch (e.g. '1d', '5d', '1mo', '3mo', '6mo', '1y')
        interval (str): Interval between data points (e.g. '1m', '5m', '15m', '1h', '1d', '1wk')
        
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    try:
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Fetch historical data
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            print(f"No data found for {symbol}")
            return None
        
        # Clean the data
        data = clean_yfinance_dataframe(data)
        data = fix_missing_values(data)
        
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def fetch_stock_news(tickers, max_news=5):
    """
    Fetch news for the given tickers.
    
    Args:
        tickers (list): List of stock tickers
        max_news (int): Maximum number of news items per ticker
        
    Returns:
        dict: Dictionary of news items for each ticker
    """
    all_news = {}
    
    for ticker in tickers:
        try:
            # Create ticker object
            tick = yf.Ticker(ticker)
            
            # Get news
            news = tick.news
            
            if news:
                # Limit the number of news items
                all_news[ticker] = news[:max_news]
            else:
                print(f"No news found for {ticker}")
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
    
    return all_news

def fetch_fred_data(series_id, start_date=None, end_date=None):
    """
    Fetch data from FRED (Federal Reserve Economic Data).
    
    Since we don't have the actual FRED API key, this function will simulate some
    basic economic data using numpy and pandas.
    
    Args:
        series_id (str): FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        pd.DataFrame: DataFrame with the requested economic data
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # If no dates provided, use last 5 years
    if not end_date:
        end_date = datetime.now()
    else:
        end_date = pd.to_datetime(end_date)
    
    if not start_date:
        start_date = end_date - timedelta(days=365*5)  # 5 years
    else:
        start_date = pd.to_datetime(start_date)
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='M')
    
    # Dictionary mapping FRED series IDs to descriptions
    series_descriptions = {
        'GDP': 'US Gross Domestic Product',
        'UNRATE': 'US Unemployment Rate',
        'CPIAUCSL': 'Consumer Price Index',
        'FEDFUNDS': 'Federal Funds Rate',
        'T10Y2Y': '10-Year Treasury Constant Maturity Minus 2-Year',
        'MORTGAGE30US': '30-Year Fixed Rate Mortgage Average',
        'DEXUSEU': 'USD to EUR Exchange Rate',
        'DTWEXB': 'Trade Weighted US Dollar Index',
        'USREC': 'US Recession Probabilities',
        'INDPRO': 'Industrial Production Index'
    }
    
    # Get description or use series_id if not in dictionary
    description = series_descriptions.get(series_id, series_id)
    
    # Simulate different types of data based on series_id
    if series_id == 'GDP':
        # GDP typically grows over time with quarterly data
        base = 20000  # Starting value
        growth = np.linspace(0, 0.5, len(date_range))  # Gradual growth
        noise = np.random.normal(0, 0.02, len(date_range))  # Small random variations
        values = base * (1 + growth + noise)
        
    elif series_id == 'UNRATE':
            # Unemployment rate fluctuates, often counter-cyclical to economy
            base = 5.0  # Starting value
            trend = np.sin(np.linspace(0, 2*np.pi, len(date_range)))  # Cyclical
            noise = np.random.normal(0, 0.3, len(date_range))  # Random variations
            values = base + trend + noise
            values = np.clip(values, 3.0, 10.0)  # Keep within reasonable range
            
    elif series_id == 'CPIAUCSL':
        # CPI generally increases over time
        base = 240  # Starting value
        growth = np.linspace(0, 0.2, len(date_range))  # Gradual growth
        noise = np.random.normal(0, 0.01, len(date_range))  # Small random variations
        values = base * (1 + growth + noise)
        
    elif series_id == 'FEDFUNDS':
        # Fed funds rate changes in steps
        base = 2.0  # Starting value
        steps = np.cumsum(np.random.choice([-0.25, 0, 0.25], size=len(date_range), p=[0.2, 0.6, 0.2]))
        values = base + steps
        values = np.clip(values, 0.0, 5.0)  # Keep within reasonable range
        
    elif series_id == 'T10Y2Y':
        # Treasury yield spread can be negative
        base = 1.0  # Starting value
        trend = np.sin(np.linspace(0, 3*np.pi, len(date_range)))  # Cyclical
        noise = np.random.normal(0, 0.2, len(date_range))  # Random variations
        values = base + trend + noise
        
    elif series_id in ['DEXUSEU', 'DTWEXB']:
        # Exchange rates fluctuate
        if series_id == 'DEXUSEU':
            base = 0.85  # Starting value for EUR/USD
        else:
            base = 110  # Starting value for dollar index
            
        trend = np.sin(np.linspace(0, 4*np.pi, len(date_range))) * 0.1  # Cyclical
        noise = np.random.normal(0, 0.02, len(date_range))  # Random variations
        values = base + trend + noise
        
    else:
        # Default: Random walk with drift
        base = 100
        drift = np.random.normal(0.001, 0.01, len(date_range))
        random_walk = np.cumsum(drift)
        values = base + random_walk * 10
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'value': values,
        'series_id': series_id,
        'description': description
    })
    
    # Set date as index
    df.set_index('date', inplace=True)
    
    return df