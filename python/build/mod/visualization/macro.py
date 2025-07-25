from mod.utils.image_utils import fig_to_png_bytes
'''
Macroeconomic trend visualization functions.
'''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from datetime import datetime, timedelta

from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR, LINE_COLOR

def generate_macro_chart():
    '''
    Generate a chart comparing S&P 500, BTC-USD, and M2 money supply trends.
    
    Returns:
        Base64-encoded PNG image
    '''
    plt.style.use('dark_background')

    try:
        # Create sample data
        dates = [datetime.now() - timedelta(days=x) for x in range(180, 0, -1)]
        
        # Sample data for S&P 500
        sp500_base = 100
        sp500_trend = np.linspace(0, 15, len(dates))
        sp500_noise = np.random.normal(0, 2, len(dates))
        sp500_values = sp500_base + sp500_trend + sp500_noise
        
        # Sample data for BTC
        btc_base = 100
        btc_trend = np.linspace(0, 25, len(dates))
        btc_noise = np.random.normal(0, 8, len(dates))
        btc_values = btc_base + btc_trend + btc_noise
        
        # Sample data for M2 Money Supply
        m2_base = 100
        m2_trend = np.linspace(0, 10, len(dates))
        m2_noise = np.random.normal(0, 1, len(dates))
        m2_values = m2_base + m2_trend + m2_noise
        
        # Create DataFrame
        df_sample = pd.DataFrame({
            'S&P 500': sp500_values,
            'BTC-USD': btc_values,
            'M2 Money Supply': m2_values
        }, index=dates)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.set_facecolor(DARK_BG_COLOR)
        ax.set_facecolor(DARK_BG_COLOR)
        
        # Set color cycle
        colors = [LINE_COLOR, UP_COLOR, DOWN_COLOR]
        
        # Plot data
        for i, col in enumerate(df_sample.columns):
            df_sample[col].plot(
                ax=ax, 
                linewidth=2, 
                label=col,
                color=colors[i % len(colors)]
            )
        
        # Style chart
        ax.set_title("Macro Trends: S&P 500 vs BTC vs M2", color='white')
        ax.set_ylabel("% Change from Start", color='white')
        ax.grid(True, linestyle=':', color=GRID_COLOR)
        ax.tick_params(colors='white')
        
        # Set legend with white text
        legend = ax.legend(facecolor=DARK_BG_COLOR)
        for text in legend.get_texts():
            text.set_color('white')
        
        plt.tight_layout()
        
        return fig_to_png_bytes(fig)
    except Exception as e:
        print(f"Error creating macro chart: {e}")
        traceback.print_exc()
        return None
