import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pandas_datareader import data as pdr

import base64
import io
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from jinja2 import Environment, FileSystemLoader
from sendemail import send_email
from datetime import datetime, timedelta

def img_to_base64(fig):
    """Utility to convert a Matplotlib figure to base64-encoded PNG."""
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)  # Close figure to free memory
        return img_data
    except Exception as e:
        print(f"Error in img_to_base64: {e}")
        plt.close(fig)  # Ensure figure is closed even on error
        return None

def generate_candlestick_chart():
    """Download 6mo of ^GSPC, produce a candlestick chart, return base64."""
    try:
        df = yf.download("^GSPC", period="6mo", interval="1d", progress=False)
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # Handle multi-index columns in yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[1] if len(col) > 1 and col[1] else col[0] for col in df.columns]

        # We only need these columns for mplfinance
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in required_cols:
            if c not in df.columns:
                print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
                return None

        # Coerce to numeric and handle missing values
        df = df[required_cols].apply(pd.to_numeric, errors='coerce')
        if df.isna().any().any():  # Check for any NaN values
            print("Warning: NaN values found in ^GSPC data. Filling forward.")
            df = df.ffill().bfill()  # Fill forward, then backward for any remaining NaNs
            
        if len(df) < 2:  # Ensure we have enough data points
            print("Warning: Not enough data points for ^GSPC candlestick chart.")
            return None

        df.index.name = 'Date'
        # Use a style that works well with dark background
        mpf_style = mpf.make_mpf_style(
            base_mpf_style='charles', 
            marketcolors=mpf.make_marketcolors(
                up='#4dfd5d', down='#fd4d4d',
                edge='inherit',
                wick='inherit',
                volume='in'
            ),
            figcolor='#1b1b1b',
            facecolor='#1b1b1b',
            edgecolor='#444444',
            gridcolor='#444444',
            gridstyle=':',
            gridaxis='both',
            y_on_right=True,
        )
        
        fig, axlist = mpf.plot(
            df, 
            type='candle', 
            style=mpf_style, 
            volume=True, 
            title="S&P 500 - 6 Month Candlestick Chart",
            returnfig=True, 
            figsize=(10, 6),
            tight_layout=True
        )
        
        # Adjust title color for dark background
        axlist[0].set_title("S&P 500 - 6 Month Candlestick Chart", color='white')
        
        # Adjust label colors
        for ax in axlist:
            ax.tick_params(colors='white')
            ax.set_ylabel(ax.get_ylabel(), color='white')
            
        return img_to_base64(fig)
    except Exception as e:
        print("Candlestick plot error:", e)
        import traceback
        traceback.print_exc()
        return None

def generate_sector_heatmap(df_universe):
    """Generate a sector heatmap showing daily percentage changes."""
    try:
        # Check if we have the necessary columns
        if 'symbol' not in df_universe.columns:
            print("Warning: Missing 'symbol' column for heatmap.")
            return None
            
        # Check if we have a sector column
        if 'sector' not in df_universe.columns:
            print("Warning: Missing 'sector' column for heatmap. Using default.")
            df_universe['sector'] = 'Unknown'
            
        # Ensure we have pct_change and that it's numeric
        if 'pct_change' not in df_universe.columns:
            print("Warning: Missing pct_change column for heatmap.")
            return None
            
        # Make a copy to avoid modifying the original
        df = df_universe.copy()
        
        # Force numeric and drop NaNs
        df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
        df.dropna(subset=['pct_change', 'sector'], inplace=True)
        
        # Filter out rows with empty sectors
        df = df[df['sector'].str.strip() != ""]
        
        if len(df) < 3:  # Arbitrary threshold - need enough data to make a meaningful heatmap
            print("Warning: Not enough valid data for sector heatmap.")
            return None

        # Group by sector to calculate average percent change per sector
        sector_data = df.groupby('sector')['pct_change'].agg(['mean', 'count']).reset_index()
        sector_data.columns = ['Sector', 'Avg Change %', 'Count']
        sector_data = sector_data.sort_values('Avg Change %', ascending=False)
        
        if len(sector_data) < 2:
            print("Warning: Not enough sectors for heatmap.")
            return None
            
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(10, max(6, len(sector_data) * 0.4)))
        
        # Set colors based on values (green for positive, red for negative)
        colors = ['#4dfd5d' if x >= 0 else '#fd4d4d' for x in sector_data['Avg Change %']]
        
        # Create horizontal bar chart
        bars = ax.barh(sector_data['Sector'], sector_data['Avg Change %'], color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width >= 0 else width - 0.2
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                    f'{width:.2f}%', va='center', ha='left' if width >= 0 else 'right',
                    color='black' if width >= 0 else 'white')
        
        # Style the chart
        ax.set_facecolor('#1b1b1b')
        fig.set_facecolor('#1b1b1b')
        ax.tick_params(colors='white')
        ax.set_xlabel('Percentage Change', color='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.grid(axis='x', linestyle=':', color='#444')
        
        ax.set_title('Sector Performance - Daily % Change', color='white')
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        import traceback
        traceback.print_exc()
        return None