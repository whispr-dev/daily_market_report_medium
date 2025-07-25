"""
Macroeconomic trend visualization functions.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from ..utils.image_utils import img_to_base64
from ..config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR, LINE_COLOR

def generate_macro_chart():
    """
    Generate a chart comparing S&P 500, BTC-USD, and M2 money supply trends
    with a forecast for S&P 500.
    
    Returns:
        Base64-encoded PNG image
    """
    from ..analysis.macro import prepare_macro_data, generate_forecast
    
    try:
        # Get the normalized data
        df_normalized = prepare_macro_data()
        if df_normalized is None or df_normalized.empty:
            print("Warning: Could not prepare macro data for chart.")
            return None
            
        # Get the forecast
        forecast = generate_forecast(df_normalized)
        
        # Create the plot with dark theme
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.set_facecolor(DARK_BG_COLOR)
        ax.set_facecolor(DARK_BG_COLOR)
        
        # Set the color cycle to match theme
        colors = [LINE_COLOR, UP_COLOR, DOWN_COLOR]
        
        # Plot the data
        for i, col in enumerate(df_normalized.columns):
            df_normalized[col].dropna().plot(
                ax=ax, 
                linewidth=2, 
                label=col,
                color=colors[i % len(colors)]
            )
        
        # Add forecast if available
        if forecast is not None and not forecast.empty:
            forecast.plot(
                ax=ax, 
                style="--", 
                color=LINE_COLOR, 
                label="S&P 500 Forecast",
                linewidth=1.5
            )
        
        # Style the chart
        ax.set_title("Macro Trends: S&P 500 vs BTC vs M2 (6mo + forecast)", color='white')
        ax.set_ylabel("% Change from Start", color='white')
        ax.grid(True, linestyle=':', color=GRID_COLOR)
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(GRID_COLOR)
        ax.spines['left'].set_color(GRID_COLOR)
        
        # Set legend with white text
        legend = ax.legend(facecolor=DARK_BG_COLOR)
        for text in legend.get_texts():
            text.set_color('white')
        
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error creating macro chart: {e}")
        traceback.print_exc()
        return None