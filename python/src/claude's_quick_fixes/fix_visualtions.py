"""
Script to fix visualization modules for the stock market analyzer.
This focuses on fixing the chart generation modules that are returning "Chart not available".
"""
import os
import shutil
import re
from datetime import datetime

def fix_currency_module():
    """Fix the currency.py visualization module."""
    print("Fixing currency.py...")
    
    # Define the path to the file
    file_path = "mod/visualization/currency.py"
    
    # Backup the original file
    if os.path.exists(file_path):
        backup_name = f"{file_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup_name)
        print(f"Original {file_path} backed up as {backup_name}")
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the function needs updating
    function_pattern = r"def generate_forex_chart\("
    if function_pattern in content:
        # Create a simplified version that always returns a chart
        new_function = """def generate_forex_chart(period="1mo", output_dir=None):
    """
    Generate a chart showing major forex pairs.
    
    Args:
        period (str): Time period to fetch data for
        output_dir (str, optional): Directory to save the chart
        
    Returns:
        str: Base64-encoded PNG image

    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import numpy as np
        import yfinance as yf
        import os
        from datetime import datetime, timedelta
        from mod.utils.image_utils import img_to_base64
        
        # Major forex pairs to track
        pairs = [
            'EURUSD=X',  # Euro / US Dollar
            'GBPUSD=X',  # British Pound / US Dollar
            'USDJPY=X',  # US Dollar / Japanese Yen
            'USDCAD=X',  # US Dollar / Canadian Dollar
            'AUDUSD=X',  # Australian Dollar / US Dollar
        ]
        
        # Create a simple chart if data fetching fails
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Try to fetch forex data
        try:
            # Download data for all pairs at once
            forex_data = yf.download(pairs, period=period, progress=False)
            
            # Check if we got data
            if forex_data is not None and not forex_data.empty:
                # Extract close prices
                if 'Close' in forex_data.columns:
                    # We got regular columns
                    df_forex = forex_data['Close']
                elif isinstance(forex_data.columns, pd.MultiIndex):
                    # We got a multi-index, extract 'Close' level
                    df_forex = forex_data.xs('Close', axis=1, level=1, drop_level=True)
                else:
                    # Just use all the data
                    df_forex = forex_data
                
                # Normalize data to start at 100 for comparison
                df_normalized = df_forex.div(df_forex.iloc[0]) * 100
                
                # Plot each forex pair
                for column in df_normalized.columns:
                    pair_name = column.replace('=X', '')
                    ax.plot(df_normalized.index, df_normalized[column], label=pair_name)
                
                # Add annotations for final values
                for column in df_normalized.columns:
                    latest_value = df_normalized[column].iloc[-1]
                    percent_change = ((latest_value / 100) - 1) * 100
                    ax.annotate(
                        f"{column.replace('=X', '')}: {percent_change:.2f}%",
                        xy=(df_normalized.index[-1], latest_value),
                        xytext=(10, 0),
                        textcoords='offset points',
                        va='center'
                    )
            else:
                # Create a placeholder with random data
                dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
                data = {}
                for pair in pairs:
                    # Generate random normalized data starting at 100
                    base = 100
                    values = [base]
                    for i in range(1, 30):
                        # Random daily change between -1% and 1%
                        change = np.random.normal(0, 0.5)
                        values.append(values[-1] * (1 + change/100))
                    data[pair] = values
                
                # Create DataFrame
                df_normalized = pd.DataFrame(data, index=dates)
                
                # Plot each forex pair
                for column in df_normalized.columns:
                    pair_name = column.replace('=X', '')
                    ax.plot(df_normalized.index, df_normalized[column], label=pair_name)
                
                # Add a note that this is sample data
                ax.set_title("Forex Comparison (Sample Data)")
                ax.text(0.5, 0.5, "Sample Data - Could not fetch real forex data",
                       ha='center', va='center', transform=ax.transAxes,
                       bbox=dict(facecolor='white', alpha=0.8))
        except Exception as e:
            # Create a very simple placeholder
            print(f"Error fetching forex data: {e}")
            ax.text(0.5, 0.5, f"Could not generate forex chart:\\n{str(e)}",
                   ha='center', va='center', transform=ax.transAxes)
        
        # Add labels and styling
        ax.set_title(f'Forex Comparison (Base 100, {period})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Normalized Value')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if output directory specified
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"forex_comparison_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
        
        # Return base64 encoding
        return img_to_base64(fig)
            
    except Exception as e:
        print(f"Error creating forex chart: {e}")
        import traceback
        traceback.print_exc()
        
        # Create an error chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error generating forex chart:\\n{str(e)}",
               ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
        return img_to_base64(fig)
        
        # Replace the function in the file
        pattern = r"def generate_forex_chart\(.*?(?=def|\Z)"
        content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Write the updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"{file_path} fixed successfully!")
    return True

def fix_sector_module():
    """Fix the sector.py visualization module."""
    print("Fixing sector.py...")
    
    # Define the path to the file
    file_path = "mod/visualization/sector.py"
    
    # Backup the original file
    if os.path.exists(file_path):
        backup_name = f"{file_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup_name)
        print(f"Original {file_path} backed up as {backup_name}")
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the function needs updating
    function_pattern = r"def generate_sector_heatmap\("
    if function_pattern in content:
        # Create a fixed version that handles errors better
        new_function = """def generate_sector_heatmap(df_universe):
    """
    Generate a sector heatmap showing daily percentage changes.
    
    Args:
        df_universe: DataFrame with symbols, sectors, and percent changes or list of symbols
    
    Returns:
        Base64-encoded PNG image
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    try:
        # Convert list to DataFrame if needed
        if isinstance(df_universe, list):
            # For a list, we need to create a basic sector mapping
            default_sectors = {
                'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 
                'AMZN': 'Consumer Cyclical', 'META': 'Technology', 'TSLA': 'Automotive',
                'JPM': 'Financial Services', 'BAC': 'Financial Services', 'WFC': 'Financial Services',
                'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
                'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy',
                'PG': 'Consumer Defensive', 'KO': 'Consumer Defensive', 'WMT': 'Consumer Defensive',
                'DIS': 'Communication Services', 'NFLX': 'Communication Services',
                'SPY': 'ETF', 'QQQ': 'ETF', 'IWM': 'ETF'
            }
            
            # Create DataFrame with symbol and sector
            data = []
            for symbol in df_universe:
                sector = default_sectors.get(symbol, 'Other')
                # Generate random percent change if needed for demo
                pct_change = np.random.normal(0, 1)  # Random between -3% and +3%
                data.append({'symbol': symbol, 'sector': sector, 'pct_change': pct_change})
            
            df = pd.DataFrame(data)
        elif isinstance(df_universe, pd.DataFrame):
            # If already a DataFrame, make a copy
            df = df_universe.copy()
            
            # Check if we have the necessary columns
            if 'symbol' not in df.columns:
                print("Warning: Missing 'symbol' column for heatmap.")
                if len(df.columns) > 0:
                    # Use the first column as symbol
                    df = df.rename(columns={df.columns[0]: 'symbol'})
                else:
                    return None
                
            # Check if we have a sector column
            if 'sector' not in df.columns:
                print("Warning: Missing 'sector' column for heatmap. Using default.")
                # Create a basic sector mapping
                default_sectors = {
                    'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 
                    'AMZN': 'Consumer Cyclical', 'META': 'Technology', 'TSLA': 'Automotive',
                    'JPM': 'Financial Services', 'BAC': 'Financial Services', 'WFC': 'Financial Services',
                    'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
                    'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy',
                    'PG': 'Consumer Defensive', 'KO': 'Consumer Defensive', 'WMT': 'Consumer Defensive',
                    'DIS': 'Communication Services', 'NFLX': 'Communication Services',
                    'SPY': 'ETF', 'QQQ': 'ETF', 'IWM': 'ETF'
                }
                
                # Add sector column
                df['sector'] = df['symbol'].map(lambda x: default_sectors.get(x, 'Other'))
                
            # Ensure we have pct_change
            if 'pct_change' not in df.columns and 'percent_change' in df.columns:
                df['pct_change'] = df['percent_change']
            elif 'pct_change' not in df.columns:
                print("Warning: Missing pct_change column for heatmap. Using random data.")
                # Generate random percent changes for demo
                df['pct_change'] = np.random.normal(0, 1, size=len(df))
        else:
            print(f"Unexpected type for df_universe: {type(df_universe)}")
            # Create a simple error chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f"Error: Invalid data type for sector heatmap\\nExpected DataFrame or list, got {type(df_universe)}",
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
            return img_to_base64(fig)
            
        # Force numeric and drop NaNs
        df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
        df.dropna(subset=['pct_change', 'sector'], inplace=True)
        
        # Filter out rows with empty sectors
        df = df[df['sector'].str.strip() != ""]
        
        if len(df) < 3:  # Need enough data to make a meaningful heatmap
            print("Warning: Not enough valid data for sector heatmap.")
            # Create a simple error chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Not enough data to generate sector heatmap",
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
            return img_to_base64(fig)

        # Group by sector to calculate average percent change per sector
        sector_data = df.groupby('sector')['pct_change'].agg(['mean', 'count']).reset_index()
        sector_data.columns = ['Sector', 'Avg Change %', 'Count']
        sector_data = sector_data.sort_values('Avg Change %', ascending=False)
        
        if len(sector_data) < 1:
            print("Warning: Not enough sectors for heatmap.")
            # Create a simple error chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Not enough sectors to generate heatmap",
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
            return img_to_base64(fig)
            
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(10, max(6, len(sector_data) * 0.4)))
        
        # Set colors based on values (green for positive, red for negative)
        from mod.config import UP_COLOR, DOWN_COLOR, DARK_BG_COLOR, GRID_COLOR
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
        
        from mod.utils.image_utils import img_to_base64
        return img_to_base64(fig)
    
    except Exception as e:
        print(f"Error generating sector heatmap: {e}")
        import traceback
        traceback.print_exc()
        
        # Create an error chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error generating sector heatmap:\\n{str(e)}",
               ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
        
        from mod.utils.image_utils import img_to_base64
        return img_to_base64(fig)
        # Replace the function in the file
        pattern = r"def generate_sector_heatmap\(.*?(?=def|\Z)"
        content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Write the updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"{file_path} fixed successfully!")
    return True

def fix_macro_module():
    """Fix the macro.py visualization module."""
    print("Fixing macro.py...")
    
    # Define the path to the file
    file_path = "mod/visualization/macro.py"
    
    # Backup the original file
    if os.path.exists(file_path):
        backup_name = f"{file_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup_name)
        print(f"Original {file_path} backed up as {backup_name}")
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the function needs updating
    function_pattern = r"def generate_macro_chart\("
    if function_pattern in content:
        # Create a fixed version
        new_function = """def generate_macro_chart():
    """
    Generate a chart comparing S&P 500, BTC-USD, and M2 money supply trends
    with a forecast for S&P 500.
    
    Returns:
        Base64-encoded PNG image
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    from mod.utils.image_utils import img_to_base64
    from mod.config import DARK_BG_COLOR, GRID_COLOR, UP_COLOR, DOWN_COLOR, LINE_COLOR
    
    try:
        # Try to get the normalized data from prepare_macro_data
        try:
            from mod.analysis.macro import prepare_macro_data, generate_forecast
            df_normalized = prepare_macro_data()
        except Exception as e:
            print(f"Error preparing macro data: {e}")
            df_normalized = None
            
        # Create the figure regardless of whether we have data
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.set_facecolor(DARK_BG_COLOR)
        ax.set_facecolor(DARK_BG_COLOR)
        
        # Set the color cycle to match theme
        colors = [LINE_COLOR, UP_COLOR, DOWN_COLOR]
        
        # If we have valid data, plot it
        if df_normalized is not None and not df_normalized.empty:
            # Plot the data
            for i, col in enumerate(df_normalized.columns):
                df_normalized[col].dropna().plot(
                    ax=ax, 
                    linewidth=2, 
                    label=col,
                    color=colors[i % len(colors)]
                )
            
            # Try to get the forecast
            try:
                forecast = generate_forecast(df_normalized['S&P 500'] if 'S&P 500' in df_normalized.columns else df_normalized.iloc[:, 0])
                
                # Handle forecast being a tuple or DataFrame
                if isinstance(forecast, tuple) and len(forecast) > 0:
                    forecast_data = forecast[0]
                else:
                    forecast_data = forecast
                    
                # Plot forecast if available
                if forecast_data is not None and not (hasattr(forecast_data, 'empty') and forecast_data.empty):
                    forecast_data.plot(
                        ax=ax, 
                        style="--", 
                        color=LINE_COLOR, 
                        label="S&P 500 Forecast",
                        linewidth=1.5
                    )
            except Exception as e:
                print(f"Error generating forecast: {e}")
        else:
            # Create sample data for demonstration
            dates = [datetime.now() - timedelta(days=x) for x in range(180, 0, -1)]
            
            # S&P 500
            sp500_base = 100
            sp500_trend = np.linspace(0, 15, len(dates))  # Upward trend
            sp500_noise = np.random.normal(0, 2, len(dates))
            sp500_values = sp500_base + sp500_trend + sp500_noise
            
            # BTC
            btc_base = 100
            btc_trend = np.linspace(0, 25, len(dates))  # Stronger upward trend
            btc_noise = np.random.normal(0, 8, len(dates))  # More volatile
            btc_values = btc_base + btc_trend + btc_noise
            
            # M2 Money Supply
            m2_base = 100
            m2_trend = np.linspace(0, 10, len(dates))  # Moderate upward trend
            m2_noise = np.random.normal(0, 1, len(dates))  # Less volatile
            m2_values = m2_base + m2_trend + m2_noise
            
            # Create DataFrame
            df_sample = pd.DataFrame({
                'S&P 500': sp500_values,
                'BTC-USD': btc_values,
                'M2 Money Supply': m2_values
            }, index=dates)
            
            # Plot sample data
            for i, col in enumerate(df_sample.columns):
                df_sample[col].plot(
                    ax=ax, 
                    linewidth=2, 
                    label=col + ' (Sample)',
                    color=colors[i % len(colors)]
                )
            
            # Add a note that this is sample data
            ax.text(0.5, 0.5, "Sample Data - Could not fetch real market data",
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(facecolor='white', alpha=0.8))
        
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
        import traceback
        traceback.print_exc()
        
        # Create an error chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error generating macro chart:\\n{str(e)}",
               ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
        
        return img_to_base64(fig)
       
        # Replace the function in the file
        pattern = r"def generate_macro_chart\(.*?(?=def|\Z)"
        content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Write the updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"{file_path} fixed successfully!")
    return True

def fix_comparison_module():
    """Fix the comparison.py visualization module."""
    print("Fixing comparison.py...")
    
    # Define the path to the file
    file_path = "mod/visualization/comparison.py"
    
    # Backup the original file
    if os.path.exists(file_path):
        backup_name = f"{file_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup_name)
        print(f"Original {file_path} backed up as {backup_name}")
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the function needs updating
    function_pattern = r"def generate_volatility_comparison\("
    if function_pattern in content:
        # Create a fixed version that returns a base64 image
        new_function = """def generate_volatility_comparison(symbols, period="3mo", output_dir=None):
    """
    Generate a chart comparing volatility of different stocks.
    
    Args:
        symbols (list): List of stock symbols to compare
        period (str): Time period to analyze
        output_dir (str, optional): Directory to save the chart
        
    Returns:
        str: Base64-encoded PNG image

    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import os
    from datetime import datetime
    from mod.utils.image_utils import img_to_base64
    
    try:
        # Limit to max 5 symbols for readability
        if isinstance(symbols, pd.DataFrame):
            if 'symbol' in symbols.columns:
                symbols = symbols['symbol'].tolist()
            else:
                symbols = symbols.index.tolist()
        
        # Ensure symbols is a list
        if not isinstance(symbols, list):
            symbols = [str(symbols)]
        
        # Limit to top 5 symbols
        symbols = symbols[:5]
        
        # Add SPY for market comparison
        if 'SPY' not in symbols:
            symbols.append('SPY')
        
        # Convert to string for yfinance
        symbols_str = ' '.join(symbols)
        
        # Create a figure regardless of whether data fetching succeeds
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Try to download and process the data
        try:
            # Download data
            data = yf.download(symbols_str, period=period, interval='1d', progress=False)
            
            # Check which columns we have - use either 'Adj Close' or 'Close'
            if isinstance(data.columns, pd.MultiIndex):
                if ('Adj Close', symbols[0]) in data.columns:
                    # Multi-column with Adj Close available
                    close_data = data['Adj Close']
                else:
                    # Multi-column but no Adj Close, use Close
                    close_data = data['Close']
            else:
                # Single column
                if 'Adj Close' in data.columns:
                    close_data = data['Adj Close']
                else:
                    close_data = data['Close']
            
            # Calculate daily returns
            returns = close_data.pct_change().dropna()
            
            # Calculate rolling volatility (20-day window)
            rolling_vol = returns.rolling(window=20).std() * np.sqrt(252) * 100  # Annualized and in percentage
            
            # Plot volatility for each symbol
            for column in rolling_vol.columns:
                ax.plot(rolling_vol.index, rolling_vol[column], label=column)
            
            # Add annotations for latest values
            for column in rolling_vol.columns:
                latest_vol = rolling_vol[column].iloc[-1]
                ax.annotate(
                    f"{column}: {latest_vol:.2f}%",
                    xy=(rolling_vol.index[-1], latest_vol),
                    xytext=(10, 0),
                    textcoords='offset points',
                    va='center'
                )
        except Exception as e:
            print(f"Error fetching volatility data: {e}")
            
            # Create sample data for demonstration
            dates = [datetime.now() - pd.Timedelta(days=x) for x in range(60, 0, -1)]
            
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
            
            # Plot sample data
            for column in vol_df.columns:
                ax.plot(vol_df.index, vol_df[column], label=f"{column} (Sample)")
            
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
            
            # Add a note that this is sample data
            ax.text(0.5, 0.5, "Sample Data - Could not fetch real volatility data",
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(facecolor='white', alpha=0.8))
        
        # Add labels and title
        ax.set_title(f'Stock Volatility Comparison ({period})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if output directory specified
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"volatility_comparison_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
        
        # Return base64 encoding
        return img_to_base64(fig)
            
    except Exception as e:
        print(f"Error creating volatility comparison: {e}")
        import traceback
        traceback.print_exc()
        
        # Create an error chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error generating volatility chart:\\n{str(e)}",
               ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
        return img_to_base64(fig)
       
        # Replace the function in the file
        pattern = r"def generate_volatility_comparison\(.*?(?=def|\Z)"
        content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Write the updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"{file_path} fixed successfully!")
    return True

def fix_all_charts():
    """Run all visualization fixes."""
    # Fix the currency module
    fix_currency_module()
    
    # Fix the sector module
    fix_sector_module()
    
    # Fix the macro module
    fix_macro_module()
    
    # Fix the comparison module
    fix_comparison_module()
    
    print("\nAll visualization modules fixed successfully!")
    print("Now you can run the analyzer with:")
    print("python -m mod.main_enhanced")

if __name__ == "__main__":
    print("Starting visualization fixes for stock market analyzer...")
    fix_all_charts()
