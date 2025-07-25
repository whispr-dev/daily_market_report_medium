from mod.utils.image_utils import fig_to_png_bytes
'''
Visualization functions for currency data.
'''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from datetime import datetime, timedelta

from mod.config import DARK_BG_COLOR, GRID_COLOR, LINE_COLOR, UP_COLOR, DOWN_COLOR

def generate_forex_chart(period="1mo", output_dir=None):
    '''
    Generate a chart showing major forex pairs.
    
    Args:
        period (str): Time period to fetch data for
        output_dir (str, optional): Directory to save the chart
        
    Returns:
        str: Base64-encoded PNG image
    '''
    plt.style.use('dark_background')

    try:
        # Create sample data
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        
        # Sample data for forex pairs
        pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD']
        forex_data = {}
        
        for pair in pairs:
            # Generate random normalized data
            base = 100
            values = [base]
            for i in range(1, len(dates)):
                change = np.random.normal(0, 0.5)
                values.append(values[-1] * (1 + change/100))
            forex_data[pair] = values
        
        # Create DataFrame
        df_forex = pd.DataFrame(forex_data, index=dates)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each forex pair
        for column in df_forex.columns:
            ax.plot(df_forex.index, df_forex[column], label=column)
        
        # Add labels and styling
        ax.set_title(f'Forex Comparison (Base 100, {period})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Normalized Value')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Return base64 encoding
        return fig_to_png_bytes(fig)
    except Exception as e:
        print(f"Error creating forex chart: {e}")
        traceback.print_exc()
        return None
