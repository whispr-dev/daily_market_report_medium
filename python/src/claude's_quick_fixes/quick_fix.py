"""
Quick fix script for the stock market analyzer issues.
This focuses on the three main issues:
1. Template errors with dividend data
2. Format mismatch in the failed_stocks section
3. load_stock_universe returning a list instead of a DataFrame
"""
import os
import shutil
import re
from datetime import datetime
import pandas as pd

def fix_email_template():
    """Fix the email_template.html file."""
    print("Fixing email_template.html...")
    
    # Backup the original template
    if os.path.exists("email_template.html"):
        backup_name = f"email_template_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        shutil.copy("email_template.html", backup_name)
        print(f"Original template backed up as {backup_name}")
    
    # Read the template
    with open("email_template.html", "r", encoding="utf-8") as f:
        template_content = f.read()
    
    # Fix 1: Fix the failed_stocks loop - handle both lists and dicts
    old_loop = r'{% for symbol, error in failed_stocks %}'
    new_loop = r'{% for item in failed_stocks %}{% if item is mapping %}{% set symbol = item.symbol if "symbol" in item else item.keys()|list|first %}{% set error = item.error if "error" in item else item.values()|list|first %}{% else %}{% set symbol = item %}{% set error = "" %}{% endif %}'
    template_content = template_content.replace(old_loop, new_loop)
    
    # Fix 2: Add safety checks for dividend data
    old_dividend_section = r'<td>{{ "%.2f"|format(data.latest_dividend|float) if data.latest_dividend != None else "N/A" }}</td>'
    new_dividend_section = r'<td>{{ "%.2f"|format(data.latest_dividend|float) if data is mapping and "latest_dividend" in data and data.latest_dividend != None else "N/A" }}</td>'
    template_content = template_content.replace(old_dividend_section, new_dividend_section)
    
    old_annual_section = r'<td>{{ "%.2f"|format(data.annual_dividend|float) if data.annual_dividend != None else "N/A" }}</td>'
    new_annual_section = r'<td>{{ "%.2f"|format(data.annual_dividend|float) if data is mapping and "annual_dividend" in data and data.annual_dividend != None else "N/A" }}</td>'
    template_content = template_content.replace(old_annual_section, new_annual_section)
    
    old_yield_section = r'<td>{{ "%.2f"|format(data.dividend_yield|float) + "%" if data.dividend_yield != None else "N/A" }}</td>'
    new_yield_section = r'<td>{{ "%.2f"|format(data.dividend_yield|float) + "%" if data is mapping and "dividend_yield" in data and data.dividend_yield != None else "N/A" }}</td>'
    template_content = template_content.replace(old_yield_section, new_yield_section)
    
    # Write the fixed template
    with open("email_template.html", "w", encoding="utf-8") as f:
        f.write(template_content)
    
    print("Template fixed successfully!")
    return True

def create_stock_universe_converter():
    """Create a module that converts between list and DataFrame formats."""
    print("Creating stock_universe_converter.py...")
    
    converter_code = """'''
Utility module to convert between different formats of stock universe data.
'''
import pandas as pd

def ensure_dataframe(universe):
    '''
    Convert any stock universe format to a DataFrame.
    
    Args:
        universe: List of tickers or DataFrame
        
    Returns:
        DataFrame with 'symbol' column
    '''
    if isinstance(universe, pd.DataFrame):
        # If already a DataFrame, ensure it has a 'symbol' column
        if 'symbol' not in universe.columns and len(universe.columns) > 0:
            # If there are columns but no 'symbol', use the first column
            universe = universe.rename(columns={universe.columns[0]: 'symbol'})
        return universe
    elif isinstance(universe, list):
        # Convert list to DataFrame
        return pd.DataFrame({'symbol': universe})
    else:
        # For any other type, try to convert to list then DataFrame
        try:
            tickers = list(universe)
            return pd.DataFrame({'symbol': tickers})
        except:
            # Default to empty DataFrame with symbol column
            return pd.DataFrame(columns=['symbol'])

def get_symbols_list(universe):
    '''
    Get a list of ticker symbols from any stock universe format.
    
    Args:
        universe: List of tickers or DataFrame
        
    Returns:
        List of ticker symbols
    '''
    if isinstance(universe, pd.DataFrame):
        if 'symbol' in universe.columns:
            return universe['symbol'].tolist()
        elif len(universe.columns) > 0:
            return universe[universe.columns[0]].tolist()
        else:
            return []
    elif isinstance(universe, list):
        return universe
    else:
        # For any other type, try to convert to list
        try:
            return list(universe)
        except:
            return []
"""
    
    # Write the converter module
    with open("mod/utils/stock_universe_converter.py", "w", encoding="utf-8") as f:
        f.write(converter_code)
    
    print("Converter module created successfully!")
    return True

def fix_sector_py():
    """Fix the sector.py file to handle both list and DataFrame inputs."""
    print("Fixing sector.py...")
    
    # Backup the original file
    if os.path.exists("mod/visualization/sector.py"):
        backup_name = f"mod/visualization/sector_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy("mod/visualization/sector.py", backup_name)
        print(f"Original sector.py backed up as {backup_name}")
    
    # Read the file
    with open("mod/visualization/sector.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add import for converter
    if "from mod.utils.stock_universe_converter import ensure_dataframe" not in content:
        import_pattern = r"from mod\.utils\.image_utils import img_to_base64"
        if import_pattern in content:
            new_imports = import_pattern + "\nfrom mod.utils.stock_universe_converter import ensure_dataframe"
            content = content.replace(import_pattern, new_imports)
        else:
            # Add at the top after the initial imports
            new_import = "from mod.utils.stock_universe_converter import ensure_dataframe"
            content = re.sub(r"('''.*?'''\s+import.*?\n)", r"\1\n" + new_import + "\n", content, flags=re.DOTALL)
    
    # Fix the function to use the converter
    function_pattern = r"def generate_sector_heatmap\(df_universe\):"
    if function_pattern in content:
        # Get the function content
        function_match = re.search(r"def generate_sector_heatmap\(df_universe\):(.*?)(?=\ndef|\Z)", content, re.DOTALL)
        if function_match:
            function_body = function_match.group(1)
            
            # Add the converter at the beginning of the function body
            converter_code = """
    # Convert list to DataFrame if needed
    df_universe = ensure_dataframe(df_universe)
"""
            # Find where to insert the converter (after the first try block or docstring)
            try_match = re.search(r"(\s+try:)", function_body)
            if try_match:
                insertion_point = try_match.end()
                new_function_body = function_body[:insertion_point] + converter_code + function_body[insertion_point:]
                # Replace the old function body with the new one
                content = content.replace(function_body, new_function_body)
            else:
                # If no try block, add after the docstring
                docstring_match = re.search(r'(""".*?"""\s+)', function_body, re.DOTALL)
                if docstring_match:
                    insertion_point = docstring_match.end()
                    new_function_body = function_body[:insertion_point] + converter_code + function_body[insertion_point:]
                    # Replace the old function body with the new one
                    content = content.replace(function_body, new_function_body)
    
    # Write the fixed file
    with open("mod/visualization/sector.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("sector.py fixed successfully!")
    return True

def fix_macro_py():
    """Fix the macro.py file to handle the forecast tuple issue."""
    print("Fixing macro.py...")
    
    # Backup the original file
    if os.path.exists("mod/visualization/macro.py"):
        backup_name = f"mod/visualization/macro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy("mod/visualization/macro.py", backup_name)
        print(f"Original macro.py backed up as {backup_name}")
    
    # Read the file
    with open("mod/visualization/macro.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix the empty check for forecast
    empty_check_pattern = r"if forecast is not None and not forecast\.empty:"
    if empty_check_pattern in content:
        new_empty_check = """if forecast is not None:
            # Handle forecast being a tuple or DataFrame
            if isinstance(forecast, tuple) and len(forecast) > 0:
                forecast_data = forecast[0]
            else:
                forecast_data = forecast
                
            # Check if forecast data is valid
            if hasattr(forecast_data, 'empty') and not forecast_data.empty:"""
        content = content.replace(empty_check_pattern, new_empty_check)
        
        # Also fix the plotting code
        plot_pattern = r"forecast\.plot\("
        if plot_pattern in content:
            new_plot = "forecast_data.plot("
            content = content.replace(plot_pattern, new_plot)
    
    # Write the fixed file
    with open("mod/visualization/macro.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("macro.py fixed successfully!")
    return True

def fix_dividend_py():
    """Fix the dividend.py file to ensure it returns a properly formatted dictionary."""
    print("Fixing dividend.py...")
    
    # Backup the original file
    if os.path.exists("mod/analysis/dividend.py"):
        backup_name = f"mod/analysis/dividend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy("mod/analysis/dividend.py", backup_name)
        print(f"Original dividend.py backed up as {backup_name}")
    
    # Write a simple replacement function
    new_function = """def analyze_dividend_history(symbols, period='1y'):
    '''
    Analyze dividend history for the given symbols.
    
    Args:
        symbols (list or str): Symbol or list of symbols
        period (str): Time period (default: '1y')
        
    Returns:
        dict: Dictionary with dividend info for each symbol
    '''
    # Make sure symbols is a list
    if isinstance(symbols, str):
        symbols = [symbols]
    
    import yfinance as yf
    import pandas as pd
    
    results = {}
    
    for symbol in symbols:
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get dividend data
            hist = ticker.history(period=period)
            dividends = ticker.dividends
            
            # Check if dividends exist
            if dividends.empty:
                results[symbol] = {
                    'latest_dividend': 0,
                    'annual_dividend': 0,
                    'dividend_count': 0,
                    'dividend_yield': 0
                }
                continue
            
            # Calculate dividend metrics
            latest_dividend = float(dividends.iloc[-1]) if len(dividends) > 0 else 0
            annual_dividend = float(dividends.sum()) if len(dividends) > 0 else 0
            dividend_count = len(dividends)
            
            # Get current price for yield calculation
            ticker_info = ticker.info
            current_price = ticker_info.get('regularMarketPrice') or ticker_info.get('currentPrice')
            if current_price and annual_dividend > 0:
                dividend_yield = (annual_dividend / current_price) * 100
            else:
                dividend_yield = 0
            
            # Store results
            results[symbol] = {
                'latest_dividend': latest_dividend,
                'annual_dividend': annual_dividend,
                'dividend_count': dividend_count,
                'dividend_yield': dividend_yield
            }
        except Exception as e:
            print(f"Error analyzing dividends for {symbol}: {e}")
            results[symbol] = {
                'latest_dividend': 0,
                'annual_dividend': 0,
                'dividend_count': 0,
                'dividend_yield': 0,
                'error': str(e)
            }
    
    return results
"""
    
    # Read the file to find the function definition
    with open("mod/analysis/dividend.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the existing function with our fixed version
    if "def analyze_dividend_history" in content:
        pattern = r"def analyze_dividend_history.*?(?=def |$)"
        content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    else:
        # If function not found, append it
        content += "\n\n" + new_function
    
    # Write the fixed file
    with open("mod/analysis/dividend.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("dividend.py fixed successfully!")
    return True

def main():
    """Run all fixes."""
    print("Starting quick fixes for stock market analyzer...")
    
    # Fix the template
    fix_email_template()
    
    # Create the converter module
    create_stock_universe_converter()
    
    # Fix the visualization modules
    fix_sector_py()
    fix_macro_py()
    
    # Fix the dividend analysis
    fix_dividend_py()
    
    print("\nAll fixes applied successfully!")
    print("Now you can run the analyzer with:")
    print("python -m mod.main_enhanced")
    print("\nThe fixes should resolve the main issues. If you still encounter problems,")
    print("run the debug_stock_analyzer.py script for more detailed diagnostics.")

if __name__ == "__main__":
    main()