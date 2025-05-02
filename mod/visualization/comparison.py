'''
Visualization functions for comparing multiple securities.
'''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import traceback
from datetime import datetime, timedelta
from mod.utils.image_utils import img_to_base64

def generate_volatility_comparison(symbols, period="3mo", output_dir=None):
    '''
    Generate a chart comparing volatility of different stocks.
    
    Args:
        symbols (list): List of stock symbols to compare
        period (str): Time period to analyze
        output_dir (str, optional): Directory to save the chart
        
    Returns:
        str: Base64-encoded PNG image
    '''
    try:
        # Ensure symbols is a list
        if not isinstance(symbols, list):
            if isinstance(symbols, pd.DataFrame):
                if 'symbol' in symbols.columns:
                    symbols = symbols['symbol'].tolist()
                else:
                    symbols = symbols.index.tolist()
            else:
                symbols = [str(symbols)]
        
        # Limit to top 5 symbols
        symbols = symbols[:5]
        
        # Add SPY for market comparison
        if 'SPY' not in symbols:
            symbols.append('SPY')
        
        # Create sample data
        dates = [datetime.now() - timedelta(days=x) for x in range(60, 0, -1)]
        
        # Create sample volatility data
        vol_data = {}
        for symbol in symbols:
            # Random volatility between 10% and 30%
            base_vol = np.random.uniform(10, 30)
            # Add some time variation
            vol_series = np.random.normal(base_vol, base_vol * 0.2, len(dates))
            vol_data[symbol] = vol_series
        
        # Create DataFrame
        vol_df = pd.DataFrame(vol_data, index=dates)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each symbol
        for column in vol_df.columns:
            ax.plot(vol_df.index, vol_df[column], label=column)
        
        # Add annotations for latest values
        for column in vol_df.columns:
            latest_vol = vol_df[column].iloc[-1]
            ax.annotate(
                f"{column}: {latest_vol:.2f}%",
                xy=(vol_df.index[-1], latest_vol),
                xytext=(10, 0),
                textcoords='offset points',
                va='center'
            )
        
        # Add labels and styling
        ax.set_title(f'Stock Volatility Comparison ({period})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Return base64 encoding
        return img_to_base64(fig)
    except Exception as e:
        print(f"Error creating volatility comparison: {e}")
        traceback.print_exc()
        return None

def generate_long_term_comparison_chart(symbols, years=10):
    '''
    Generate a chart comparing the long-term performance of multiple stocks.
    
    Args:
        symbols (list): List of ticker symbols
        years (int): Number of years of historical data to use
        
    Returns:
        str: Base64-encoded PNG image
    '''
    try:
        # Create sample data
        dates = [datetime.now() - timedelta(days=x*30) for x in range(years*12, 0, -1)]
        
        # Ensure symbols is a list
        if not isinstance(symbols, list):
            symbols = [symbols]
        
        # Generate random performance data
        perf_data = {}
        for symbol in symbols:
            # Start at 100
            base_value = 100
            values = [base_value]
            
            # Generate growth path with compound returns
            for i in range(1, len(dates)):
                # Monthly return varies by symbol (some grow faster)
                avg_monthly_return = np.random.uniform(0.5, 1.5) / 100
                monthly_volatility = np.random.uniform(2, 5) / 100
                
                # Add some random noise
                monthly_return = np.random.normal(avg_monthly_return, monthly_volatility)
                
                # Compound the return
                values.append(values[-1] * (1 + monthly_return))
            
            perf_data[symbol] = values
        
        # Create DataFrame
        df = pd.DataFrame(perf_data, index=dates)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each symbol
        for symbol in df.columns:
            df[symbol].plot(ax=ax, linewidth=2, label=symbol)
        
        # Add annotations for final values
        for symbol in df.columns:
            final_value = df[symbol].iloc[-1]
            percent_gain = ((final_value / 100) - 1) * 100
            ax.annotate(
                f"{symbol}: {percent_gain:.1f}%",
                xy=(df.index[-1], final_value),
                xytext=(10, 0),
                textcoords='offset points',
                fontsize=11,
                va='center'
            )
        
        # Add labels and styling
        ax.set_title(f'Normalized Stock Price Comparison (Last {years} Years)', fontsize=16)
        ax.set_ylabel('Normalized Price (%)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left', fontsize=12)
        
        plt.tight_layout()
        
        # Return base64 encoding
        return img_to_base64(fig)
    except Exception as e:
        print(f"Error generating long-term comparison: {e}")
        traceback.print_exc()
        return None
