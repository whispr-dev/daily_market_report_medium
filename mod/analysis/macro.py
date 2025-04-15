"""
Macroeconomic analysis functions.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from ..config import MACRO_LOOKBACK_DAYS, FORECAST_STEPS

def prepare_macro_data():
    """
    Prepare macroeconomic data for analysis.
    Downloads data for S&P 500, BTC-USD, and FRED M2 money supply.
    
    Returns:
        DataFrame with normalized data for all three indicators
    """
    from ..data.fetcher import fetch_symbol_data, fetch_fred_data
    from ..utils.data_utils import normalize_to_percentage_change
    
    end = datetime.today()
    start = end - timedelta(days=MACRO_LOOKBACK_DAYS)
    
    # Get S&P 500 data
    try:
        df_spx = fetch_symbol_data("^GSPC", start=start)
        spx_col = "Adj Close" if "Adj Close" in df_spx.columns else "Close"
        if df_spx.empty or spx_col not in df_spx.columns:
            print("Warning: ^GSPC macro chart missing data.")
            return None
    except Exception as e:
        print(f"Error downloading S&P 500 data: {e}")
        return None
    
    # Get Bitcoin data
    try:
        df_btc = fetch_symbol_data("BTC-USD", start=start)
        btc_col = "Adj Close" if "Adj Close" in df_btc.columns else "Close"
        if df_btc.empty or btc_col not in df_btc.columns:
            print("Warning: BTC macro chart missing data.")
            return None
    except Exception as e:
        print(f"Error downloading Bitcoin data: {e}")
        return None
    
    # Get M2 data
    try:
        # Try to get M2 data from FRED
        df_m2 = fetch_fred_data("M2SL", start)
        if df_m2.empty or 'M2SL' not in df_m2.columns:
            print("Warning: M2 data is empty. Using placeholder values.")
            # Create empty DataFrame with same index as S&P
            df_m2 = pd.DataFrame(index=df_spx.index)
            df_m2['M2SL'] = np.nan
    except Exception as e:
        print(f"Warning: M2SL DataReader error: {e}")
        # Create empty DataFrame with same index as S&P
        df_m2 = pd.DataFrame(index=df_spx.index)
        df_m2['M2SL'] = np.nan
    
    # Combine into a single DataFrame
    df = pd.DataFrame({
        "S&P 500": df_spx[spx_col],
        "BTC": df_btc[btc_col],
        "M2": df_m2["M2SL"]
    })
    
    # Forward fill missing values and drop any completely empty rows
    df = df.ffill().dropna(how='all')
    if len(df) < 2:
        print("Warning: Not enough macro data to process.")
        return None
        
    # Normalize to percentage change from start
    df_normalized = normalize_to_percentage_change(df)
    
    return df_normalized

def generate_forecast(df_normalized, steps=FORECAST_STEPS):
    """
    Generate a forecast for S&P 500 based on exponential smoothing.
    
    Args:
        df_normalized: DataFrame with normalized data
        steps: Number of steps to forecast
        
    Returns:
        Series with forecasted values and index
    """
    forecast = None
    try:
        if "S&P 500" in df_normalized.columns and len(df_normalized["S&P 500"].dropna()) > 10:
            model = ExponentialSmoothing(
                df_normalized["S&P 500"].dropna(), 
                trend='add', 
                seasonal=None,
                initialization_method="estimated"
            )
            fit = model.fit()
            forecast = fit.forecast(steps=steps)
            
            # Create proper index for forecast
            last_date = df_normalized.index[-1]
            forecast_index = pd.date_range(
                last_date + pd.Timedelta(days=1), 
                periods=len(forecast), 
                freq='B'
            )
            forecast = pd.Series(forecast.values, index=forecast_index)
    except Exception as e:
        print(f"Forecast error: {e}")
        forecast = None
        
    return forecast