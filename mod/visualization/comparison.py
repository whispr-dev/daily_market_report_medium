"""
Visualization functions for comparing multiple securities.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from ..utils.image_utils import img_to_base64

def generate_long_term_comparison_chart(symbols, years=10):
    """
    Generate a chart comparing the long-term performance of multiple stocks.
    
    Args:
        symbols (list): List of ticker symbols
        years (int): Number of years of historical data to use
        
    Returns:
        str: Base64-encoded PNG image
    """
    # Calculate start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    # Download the historical data
    if isinstance(symbols, list):
        symbols_str = ' '.join(symbols)
    else:
        symbols_str = symbols
        symbols = symbols_str.split()
    
    # Download data for all symbols at once
    df = yf.download(symbols_str, start=start_date, end=end_date, interval='1mo')['Adj Close']
    
    # Normalize to the starting price (100%)
    normalized_df = pd.DataFrame()
    for symbol in symbols:
        if symbol in df.columns:
            first_valid_price = df[symbol].dropna().iloc[0]
            normalized_df[symbol] = df[symbol] / first_valid_price * 100
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot each symbol
    for symbol in normalized_df.columns:
        normalized_df[symbol].plot(ax=ax, linewidth=2, label=symbol)
    
    # Add styling
    ax.set_title(f'Normalized Stock Price Comparison (Last {years} Years)', fontsize=16)
    ax.set_ylabel('Normalized Price (%)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper left', fontsize=12)
    
    # Add annotations for final values
    for symbol in normalized_df.columns:
        final_value = normalized_df[symbol].dropna().iloc[-1]
        ax.annotate(f'{symbol}: {final_value:.1f}%', 
                   xy=(df.index[-1], final_value),
                   xytext=(10, 0),
                   textcoords='offset points',
                   fontsize=11,
                   va='center')
    
    plt.tight_layout()
    
    return img_to_base64(fig)

def generate_volatility_comparison(symbols, period='1y'):
    """
    Generate a volatility comparison chart for the given symbols.
    
    Args:
        symbols (list): List of ticker symbols
        period (str): Time period to fetch
        
    Returns:
        str: Base64-encoded PNG image
    """
    if isinstance(symbols, list):
        symbols_str = ' '.join(symbols)
    else:
        symbols_str = symbols
        symbols = symbols_str.split()
    
    # Download data for all symbols at once
    df = yf.download(symbols_str, period=period, interval='1d')['Adj Close']
    
    # Calculate daily returns
    returns = df.pct_change().dropna()
    
    # Calculate volatility (standard deviation of returns)
    volatility = returns.std() * np.sqrt(252) * 100  # Annualized and converted to percentage
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = volatility.sort_values(ascending=False).plot(kind='bar', ax=ax, color='skyblue')
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars.patches):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f'{bar.get_height():.1f}%',
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    # Add styling
    ax.set_title('Annualized Volatility Comparison', fontsize=16)
    ax.set_ylabel('Volatility (%)', fontsize=12)
    ax.set_xlabel('Symbol', fontsize=12)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    return img_to_base64(fig)