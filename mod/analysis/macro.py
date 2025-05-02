"""
Module for macroeconomic analysis functions.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import statsmodels.api as sm

def prepare_macro_data(start_date=None, end_date=None):
    """
    Prepare macroeconomic data for analysis.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        pd.DataFrame: DataFrame with normalized macroeconomic data
    """
    from mod.data.fetcher import fetch_symbol_data, fetch_fred_data
    
    try:
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = pd.to_datetime(end_date)
        
        if not start_date:
            start_date = end_date - timedelta(days=365*2)  # 2 years
        else:
            start_date = pd.to_datetime(start_date)
            
        # Calculate period string based on date range
        days_diff = (end_date - start_date).days
        
        if days_diff <= 7:
            period = "1wk"
        elif days_diff <= 30:
            period = "1mo" 
        elif days_diff <= 90:
            period = "3mo"
        elif days_diff <= 180:
            period = "6mo"
        elif days_diff <= 365:
            period = "1y"
        elif days_diff <= 730:
            period = "2y"
        elif days_diff <= 1825:
            period = "5y"
        else:
            period = "max"
        
        # Get S&P 500 data
        try:
            sp500_data = fetch_symbol_data('^GSPC', period=period)
            if sp500_data is None or sp500_data.empty:
                print("No S&P 500 data found")
                return None
            sp500 = sp500_data['Close']
        except Exception as e:
            print(f"Error downloading S&P 500 data: {e}")
            return None
        
        # Get economic data
        fred_series = {
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index',
            'FEDFUNDS': 'Federal Funds Rate',
            'T10Y2Y': 'Treasury Yield Spread',
            'MORTGAGE30US': 'Mortgage Rate'
        }
        
        macro_data = {}
        
        for series_id, name in fred_series.items():
            try:
                data = fetch_fred_data(series_id)
                if data is not None and not data.empty:
                    # Resample to daily frequency and forward fill
                    data = data.resample('D').ffill()
                    macro_data[name] = data['value']
            except Exception as e:
                print(f"Error fetching {name} data: {e}")
        
        # Combine all data
        df_combined = pd.DataFrame({'S&P 500': sp500})
        
        for name, series in macro_data.items():
            # Align dates
            if not series.empty:
                df_combined[name] = series
        
        # Forward fill and backward fill missing values
        df_combined = df_combined.fillna(method='ffill').fillna(method='bfill')
        
        # Normalize all series to 100 at the start
        df_normalized = df_combined.div(df_combined.iloc[0]) * 100
        
        return df_normalized
        
    except Exception as e:
        print(f"Warning: Could not prepare macro data for chart. {e}")
        return None

def generate_forecast(data, periods=30):
    """
    Generate a time series forecast using ARIMA model.
    
    Args:
        data (pd.Series): Time series data to forecast
        periods (int): Number of periods to forecast
        
    Returns:
        tuple: (forecast, confidence intervals)
    """
    try:
        # Create ARIMA model with auto-order selection
        model = sm.tsa.ARIMA(data, order=(2,1,2))
        fit = model.fit()
        
        # Generate forecast
        forecast = fit.forecast(steps=periods)
        conf_int = fit.get_forecast(steps=periods).conf_int()
        
        return forecast, conf_int
    except Exception as e:
        print(f"Error generating forecast: {e}")
        return None, None