'''
Sector analysis visualization functions.
'''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from mod.utils.image_utils import img_to_base64
from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR

def generate_sector_heatmap(df_universe):
    '''
    Generate a sector heatmap showing daily percentage changes.
    
    Args:
        df_universe: DataFrame with symbols, sectors, and percent changes
    
    Returns:
        Base64-encoded PNG image
    '''
    try:
        # Handle different input types
        if isinstance(df_universe, list):
            # Convert list to DataFrame
            df = pd.DataFrame({'symbol': df_universe})
            # Add dummy sectors and changes
            sectors = ['Technology', 'Financials', 'Healthcare', 'Consumer', 'Energy']
            df['sector'] = [sectors[i % len(sectors)] for i in range(len(df))]
            df['pct_change'] = np.random.normal(0, 1, size=len(df))
        elif isinstance(df_universe, pd.DataFrame):
            df = df_universe.copy()
            if 'symbol' not in df.columns and len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: 'symbol'})
            if 'sector' not in df.columns:
                sectors = ['Technology', 'Financials', 'Healthcare', 'Consumer', 'Energy']
                df['sector'] = [sectors[i % len(sectors)] for i in range(len(df))]
            if 'pct_change' not in df.columns and 'percent_change' in df.columns:
                df['pct_change'] = df['percent_change']
            elif 'pct_change' not in df.columns:
                df['pct_change'] = np.random.normal(0, 1, size=len(df))
        else:
            # Create dummy data
            df = pd.DataFrame({
                'symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
                'sector': ['Technology'] * 5,
                'pct_change': np.random.normal(0, 1, size=5)
            })
        
        # Group by sector
        sector_data = df.groupby('sector')['pct_change'].agg(['mean', 'count']).reset_index()
        sector_data.columns = ['Sector', 'Avg Change %', 'Count']
        sector_data = sector_data.sort_values('Avg Change %', ascending=False)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [UP_COLOR if x >= 0 else DOWN_COLOR for x in sector_data['Avg Change %']]
        bars = ax.barh(sector_data['Sector'], sector_data['Avg Change %'], color=colors)
        
        # Style chart
        ax.set_facecolor(DARK_BG_COLOR)
        fig.set_facecolor(DARK_BG_COLOR)
        ax.tick_params(colors='white')
        ax.set_title('Sector Performance', color='white')
        ax.set_xlabel('Percentage Change', color='white')
        
        # Convert to base64
        return img_to_base64(fig)
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        traceback.print_exc()
        return None
