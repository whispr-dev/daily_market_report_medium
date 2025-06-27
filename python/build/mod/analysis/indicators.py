from mod.utils.image_utils import fig_to_png_bytes
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

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_enhanced_candlestick_chart(df, ticker, output_dir="output/charts"):
    """
    Generate a candlestick chart with additional reversal indicators.
    
    Args:
        df (DataFrame): Price data with 'Open', 'High', 'Low', 'Close'
        ticker (str): Ticker symbol for title
        output_dir (str): Directory to optionally save the image (not used here)
    
    Returns:
        fig (matplotlib.figure.Figure): The chart figure
    """
    plt.style.use('dark_background')

    if df is None or df.empty:
        print(f"No data to plot for {ticker}")
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    df['Date'] = df.index
    df['Date_Num'] = mdates.date2num(df['Date'])

    width = 0.6
    up = df['Close'] >= df['Open']
    down = df['Close'] < df['Open']

    # Plot candlesticks
    ax.bar(df['Date_Num'][up], df['Close'][up] - df['Open'][up], width, bottom=df['Open'][up], color='green')
    ax.bar(df['Date_Num'][down], df['Close'][down] - df['Open'][down], width, bottom=df['Open'][down], color='red')
    ax.vlines(df['Date_Num'], df['Low'], df['High'], color='black', linewidth=0.5)

    # Format x-axis
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()

    ax.set_title(f"{ticker} Enhanced Candlestick with Reversal Indicators")
    ax.set_ylabel("Price")
    ax.set_xlabel("Date")

    # Tight layout and return figure
    plt.tight_layout()
    return fig

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