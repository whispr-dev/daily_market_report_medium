"""
Module for visualization of technical indicators.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_enhanced_candlestick_chart(df, ticker, output_dir=None, indicators=None, 
                                       volume=True, figsize=(12, 8), title=None):
    """
    Generate an enhanced candlestick chart with technical indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        ticker (str): Stock ticker symbol
        output_dir (str, optional): Directory to save the chart
        indicators (dict, optional): Dictionary of indicators to plot
        volume (bool, optional): Whether to include volume
        figsize (tuple, optional): Figure size
        title (str, optional): Chart title
        
    Returns:
        str: Path to the saved chart image or None if not saved
    """
    # Make a copy of the dataframe to avoid modifying the original
    df = df.copy()
    
    # Set index if not already a DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Check required columns
    required_columns = ['Open', 'High', 'Low', 'Close']
    if volume:
        required_columns.append('Volume')
    
    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            # Try lowercase versions
            lowercase_col = col.lower()
            if lowercase_col in df.columns:
                df[col] = df[lowercase_col]
            else:
                raise ValueError(f"Required column '{col}' not found in dataframe")
    
    # Set up style
    mc = mpf.make_marketcolors(
        up='green',
        down='red',
        edge='inherit',
        wick='inherit',
        volume='inherit'
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle=':',
        y_on_right=False,
        facecolor='white'
    )
    
    # Initialize plot parameters
    kwargs = {
        'type': 'candle',
        'style': s,
        'figsize': figsize,
        'title': title if title else f'{ticker} Stock Price',
        'ylabel': 'Price ($)',
        'volume': volume,
        'panel_ratios': (4, 1) if volume else None,
        'returnfig': True
    }
    
    # Add indicators if provided
    if indicators:
        apds = []
        
        # Process each indicator
        for indicator_name, indicator_data in indicators.items():
            if isinstance(indicator_data, dict) and 'data' in indicator_data:
                # Handle dictionary with data and parameters
                data = indicator_data['data']
                color = indicator_data.get('color', 'blue')
                panel = indicator_data.get('panel', 0)
                
                # Create plot
                apd = mpf.make_addplot(data, color=color, panel=panel)
                apds.append(apd)
            elif isinstance(indicator_data, pd.Series) or isinstance(indicator_data, np.ndarray):
                # Handle direct data
                apd = mpf.make_addplot(indicator_data, color='blue', panel=0)
                apds.append(apd)
        
        kwargs['addplot'] = apds
    
    # Create plot
    fig, axes = mpf.plot(df, **kwargs)
    
    # Save if output directory is provided
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_candlestick_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Save figure
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    else:
        # Display figure
        plt.show()
        return None

def generate_multi_indicator_chart(data, ticker, indicators, output_dir=None):
    """
    Generate a chart with multiple technical indicators in separate panels.
    
    Args:
        data (pd.DataFrame): DataFrame with OHLCV data
        ticker (str): Stock ticker symbol
        indicators (dict): Dictionary of indicators to plot with panel numbers
        output_dir (str, optional): Directory to save the chart
        
    Returns:
        str: Path to the saved chart image or None if not saved
    """
    # Make a copy of the dataframe to avoid modifying the original
    df = data.copy()
    
    # Set index if not already a DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Setup style
    mc = mpf.make_marketcolors(
        up='green',
        down='red',
        edge='inherit',
        wick='inherit',
        volume='inherit'
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle=':',
        y_on_right=False,
        facecolor='white'
    )
    
    # Count number of panels needed
    max_panel = 1  # Main price panel is 0, volume is 1
    for indicator_data in indicators.values():
        if isinstance(indicator_data, dict) and 'panel' in indicator_data:
            max_panel = max(max_panel, indicator_data['panel'])
    
    # Set panel ratios
    panel_ratios = [4] + [1] * max_panel
    
    # Prepare addplots
    apds = []
    for indicator_name, indicator_data in indicators.items():
        if isinstance(indicator_data, dict) and 'data' in indicator_data:
            data = indicator_data['data']
            color = indicator_data.get('color', 'blue')
            panel = indicator_data.get('panel', 0)
            secondary_y = indicator_data.get('secondary_y', False)
            
            apd = mpf.make_addplot(
                data, 
                color=color, 
                panel=panel,
                ylabel=indicator_name if panel > 0 else None,
                secondary_y=secondary_y
            )
            apds.append(apd)
    
    # Create plot
    fig, axes = mpf.plot(
        df,
        type='candle',
        style=s,
        figsize=(12, 8 + max_panel * 2),
        title=f'{ticker} Technical Analysis',
        ylabel='Price ($)',
        volume=True,
        panel_ratios=panel_ratios,
        addplot=apds,
        returnfig=True
    )
    
    # Save if output directory is provided
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_multi_indicator_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Save figure
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    else:
        # Display figure
        plt.show()
        return None