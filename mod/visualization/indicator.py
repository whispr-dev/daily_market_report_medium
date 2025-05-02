"""
Technical indicators visualization functions.
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mplfinance as mpf
import pandas as pd
import numpy as np
import traceback
from mod.utils.image_utils import img_to_base64
from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR, LINE_COLOR

def generate_enhanced_candlestick_chart(df=None):
    """
    Generate enhanced candlestick chart with EWO and reversal signals for S&P 500.
    
    Args:
        df: Optional pre-loaded dataframe, will fetch S&P 500 data if None
    
    Returns:
        Base64-encoded PNG image
    """
    from ..data.fetcher import fetch_symbol_data
    from ..analysis.technical import calculate_ewo, detect_reversal_signals
    
    try:
        if df is None:
            # Download the data
            df = fetch_symbol_data("^GSPC", period="6mo", interval="1d")
            
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # We need these columns for mplfinance
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in required_cols:
            if c not in df.columns:
                print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
                return None

        # Ensure we have enough data points
        if len(df) < 2:
            print("Warning: Not enough data points for ^GSPC candlestick chart.")
            return None

        # Calculate the Elliott Wave Oscillator
        df = calculate_ewo(df)
        
        # Add reversal signal detection
        df = detect_reversal_signals(df)
        
        # Create figure with two subplots (candlestick above, EWO below)
        fig = plt.figure(figsize=(12, 8), facecolor=DARK_BG_COLOR)
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        
        # Main chart (candlestick)
        ax1 = fig.add_subplot(gs[0])
        
        # Plot candlesticks
        mpf.plot(
            df, 
            type='candle', 
            style='charles', 
            ax=ax1,
            volume=False,  # We'll handle volume separately
            ylabel='Price ($)',
            datetime_format='%Y-%m-%d',
            xrotation=45,
            colorup=UP_COLOR, 
            colordown=DOWN_COLOR,
            edgecolor=DARK_BG_COLOR
        )
        
        # Add the "blue line" (20-day moving average)
        ax1.plot(df.index, df['blue_line'], color=LINE_COLOR, linewidth=1.5, label='20-Day MA')
        
        # Add reversal markers
        for idx, row in df.iterrows():
            if row['bull_reversal']:
                ax1.scatter(idx, row['Low'] * 0.995, marker='^', color=UP_COLOR, s=100, zorder=5)
            elif row['bear_reversal']:
                ax1.scatter(idx, row['High'] * 1.005, marker='v', color=DOWN_COLOR, s=100, zorder=5)
        
        # Style the main chart
        ax1.set_facecolor(DARK_BG_COLOR)
        ax1.set_title("S&P 500 with Reversal Signals", color='white', fontsize=16)
        ax1.tick_params(colors='white')
        ax1.grid(True, linestyle=':', color=GRID_COLOR, alpha=0.5)
        ax1.legend(facecolor='#333333', edgecolor=GRID_COLOR, labelcolor='white')
        
        # EWO chart
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        # Plot EWO as a histogram
        ewo_colors = [DOWN_COLOR if x < 0 else UP_COLOR for x in df['ewo']]
        ax2.bar(df.index, df['ewo'], color=ewo_colors, alpha=0.7)
        
        # Add a zero line
        ax2.axhline(y=0, color='#aaaaaa', linestyle='-', linewidth=0.5)
        
        # Style the EWO chart
        ax2.set_facecolor(DARK_BG_COLOR)
        ax2.set_title("Elliott Wave Oscillator (5-35)", color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, linestyle=':', color=GRID_COLOR, alpha=0.5)
        ax2.set_ylabel('EWO Value', color='white')
        
        # Adjust layout and style the figure
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)
        
        return img_to_base64(fig)
        
    except Exception as e:
        print("Enhanced candlestick plot error:", e)
        traceback.print_exc()
        return None