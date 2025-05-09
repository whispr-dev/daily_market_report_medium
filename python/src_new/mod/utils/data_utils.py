from mod.utils.image_utils import fig_to_png_bytes
"""
Utilities for data processing and handling.
"""
import pandas as pd
import numpy as np

def clean_yfinance_dataframe(df):
    """
    Clean and standardize a DataFrame from yfinance.
    
    Args:
        df: DataFrame from yfinance download
        
    Returns:
        DataFrame with standardized column names
    """
    if df.empty:
        return df
        
    # Handle multi-index columns in yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df.columns]
    
    # Coerce to numeric and handle missing values
    numeric_cols = [col for col in df.columns if col in 
                   ["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    
    if numeric_cols:
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
    return df

def fix_missing_values(df):
    """
    Handle missing values in a DataFrame.
    
    Args:
        df: DataFrame with potential missing values
        
    Returns:
        DataFrame with forward and backward filled values
    """
    if df.isna().any().any():  # Check for any NaN values
        print("Warning: NaN values found in data. Filling forward.")
        df = df.ffill().bfill()  # Fill forward, then backward for any remaining NaNs
    
    return df

def get_preferred_close_column(df):
    """
    Get the preferred column for closing prices, prefer Adj Close over Close.
    
    Args:
        df: DataFrame potentially containing Close or Adj Close column
        
    Returns:
        str: Name of the preferred column
    """
    return 'Adj Close' if 'Adj Close' in df.columns else 'Close'

def ensure_required_columns(df, required_cols):
    """
    Check if DataFrame has all required columns.
    
    Args:
        df: DataFrame to check
        required_cols: List of required column names
        
    Returns:
        bool: True if all required columns exist, False otherwise
    """
    for col in required_cols:
        if col not in df.columns:
            return False
    return True

def normalize_to_percentage_change(df):
    """
    Normalize DataFrame columns to percentage change from first value.
    
    Args:
        df: DataFrame with numeric columns
        
    Returns:
        DataFrame with normalized values as percentage change
    """
    df_normalized = df.copy()
    for col in df.columns:
        if not df[col].isna().all():  # Skip columns that are all NaN
            first_valid = df[col].first_valid_index()
            if first_valid is not None:
                base_value = df[col].loc[first_valid]
                df_normalized[col] = df[col] / base_value * 100 - 100  # Show as % change from start
    
    # Only keep the columns that have data
    df_normalized = df_normalized.dropna(axis=1, how='all')
    
    return df_normalized