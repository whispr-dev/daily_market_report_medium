"""
Sector analysis visualization functions.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from mod.utils.image_utils import img_to_base64
from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR

def generate_sector_heatmap(df_universe):
    """
    Generate a sector heatmap showing daily percentage changes.
    
    Args:
        df_universe: DataFrame with symbols, sectors, and percent changes
    
    Returns:
        Base64-encoded PNG image
    """
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
        colors = [UP_COLOR if x >= 0 else DOWN_COLOR for x in sector_data['Avg Change %']]
        
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
        ax.set_facecolor(DARK_BG_COLOR)
        fig.set_facecolor(DARK_BG_COLOR)
        ax.tick_params(colors='white')
        ax.set_xlabel('Percentage Change', color='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(GRID_COLOR)
        ax.spines['left'].set_color(GRID_COLOR)
        ax.grid(axis='x', linestyle=':', color=GRID_COLOR)
        
        ax.set_title('Sector Performance - Daily % Change', color='white')
        plt.tight_layout()
        
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        traceback.print_exc()
        return None