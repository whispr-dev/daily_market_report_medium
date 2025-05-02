"""
Candlestick chart visualization functions.
"""
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import traceback
from mod.utils.image_utils import img_to_base64
from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR

def generate_candlestick_chart(df=None):
    """
    Generate a simple candlestick chart for S&P 500 index (6 months).
    
    Args:
        df: Optional pre-loaded dataframe, will fetch S&P 500 data if None
    
    Returns:
        Base64-encoded PNG image
    """
    from ..data.fetcher import fetch_symbol_data
    
    try:
        if df is None:
            df = fetch_symbol_data("^GSPC", period="6mo", interval="1d")
            
        if df.empty:
            print("Warning: ^GSPC candlestick data is empty.")
            return None

        # We only need these columns for mplfinance
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for c in required_cols:
            if c not in df.columns:
                print(f"Warning: {c} column missing in ^GSPC for candlestick chart.")
                return None

        # Ensure we have enough data points
        if len(df) < 2:
            print("Warning: Not enough data points for ^GSPC candlestick chart.")
            return None

        df.index.name = 'Date'
        # Use a style that works well with dark background
        mpf_style = mpf.make_mpf_style(
            base_mpf_style='charles', 
            marketcolors=mpf.make_marketcolors(
                up=UP_COLOR, 
                down=DOWN_COLOR,
                edge='inherit',
                wick='inherit',
                volume='in'
            ),
            figcolor=DARK_BG_COLOR,
            facecolor=DARK_BG_COLOR,
            edgecolor=GRID_COLOR,
            gridcolor=GRID_COLOR,
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
        traceback.print_exc()
        return None