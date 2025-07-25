"""
Visualization functions for currency data.
"""
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import traceback
from datetime import datetime, timedelta
from ..utils.image_utils import img_to_base64
from ..config import DARK_BG_COLOR, GRID_COLOR, LINE_COLOR, UP_COLOR, DOWN_COLOR

def generate_forex_chart(pairs=None):
    """
    Generate a chart comparing major currency pairs over 6 months.
    
    Args:
        pairs: Optional list of currency pairs, defaults to major pairs if None
        
    Returns:
        Base64-encoded PNG image
    """
    try:
        end = datetime.today()
        start = end - timedelta(days=180)
        
        # Default major forex pairs if none provided
        if pairs is None:
            pairs = ["EURUSD=X", "USDJPY=X", "GBPUSD=X"]
            
        forex_data = {}
        
        for pair in pairs:
            try:
                df = yf.download(pair, start=start, progress=False)
                forex_data[pair] = df['Close']
            except Exception as e:
                print(f"Error downloading {pair} data: {e}")
        
        # Create DataFrame with all forex data
        df_forex = pd.DataFrame(forex_data)
        
        # Normalize to percentage change from start
        df_normalized = df_forex.copy()
        for col in df_forex.columns:
            first_valid = df_forex[col].first_valid_index()
            if first_valid is not None:
                base_value = df_forex[col].loc[first_valid]
                df_normalized[col] = df_forex[col] / base_value * 100 - 100
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.set_facecolor(DARK_BG_COLOR)
        ax.set_facecolor(DARK_BG_COLOR)
        
        colors = [LINE_COLOR, UP_COLOR, DOWN_COLOR]
        for i, col in enumerate(df_normalized.columns):
            df_normalized[col].plot(ax=ax, linewidth=2, label=col, color=colors[i % len(colors)])
        
        # Style the chart
        ax.set_title("Major Currency Pairs - 6 Month Comparison", color='white')
        ax.set_ylabel("% Change from Start", color='white')
        ax.grid(True, linestyle=':', color=GRID_COLOR)
        ax.tick_params(colors='white')
        
        # Set legend with white text
        legend = ax.legend(facecolor=DARK_BG_COLOR)
        for text in legend.get_texts():
            text.set_color('white')
        
        plt.tight_layout()
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error creating forex chart: {e}")
        traceback.print_exc()
        return None