from mod.utils.image_utils import fig_to_png_bytes
"""
Improved HTML report generation functions with better error handling.
"""
from jinja2 import Environment, FileSystemLoader
import os
import pandas as pd
from datetime import datetime
import traceback

def render_html_report(data):
    """
    Render HTML report using Jinja2 template.
    
    Args:
        data: Dictionary with data for the template
        
    Returns:
        str: Rendered HTML content
    """
    try:
        # Verify data is a dictionary
        if not isinstance(data, dict):
            print(f"ERROR: data must be a dictionary, got {type(data)}")
            data = {}  # Use empty dict as fallback
        
        # Print some debug info
        print(f"Template variables: {list(data.keys())}")
        
        # Make sure template directory exists
        template_dir = "."  # current directory
        template_file = "email_template.html"
        
        if not os.path.exists(os.path.join(template_dir, template_file)):
            print(f"ERROR: Template file '{template_file}' not found in {template_dir}")
            # Return a simple HTML as fallback
            return f"""
            <html>
            <head><title>Stock Market Report - Error</title></head>
            <body>
                <h1>Error: Template file not found</h1>
                <p>The template file '{template_file}' was not found in the directory '{template_dir}'.</p>
                <p>Please make sure the template file exists and is accessible.</p>
            </body>
            </html>
            """
        
        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)
        
        # Render the template with the provided data
        html_output = template.render(**data)
        
        # Verify we got some output
        if not html_output:
            print("WARNING: Empty HTML output from template rendering")
        
        return html_output
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        traceback.print_exc()
        return f"""
        <html>
        <head><title>Stock Market Report - Error</title></head>
        <body>
            <h1>Error generating report</h1>
            <p>{str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """

def save_html_report(html_content):
    """
    Save the HTML report to a file.
    
    Args:
        html_content: HTML content to save
        
    Returns:
        str: Filename of the saved report
    """
    try:
        # Validate input
        if not html_content:
            print("ERROR: Empty HTML content, cannot save report")
            return None
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.html"
        
        # Ensure we're saving as text, not binary
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Verify the file was created
        if os.path.exists(report_filename):
            print(f"HTML report saved as {report_filename}")
            file_size = os.path.getsize(report_filename)
            print(f"File size: {file_size} bytes")
            
            # Print the first few characters for debugging
            with open(report_filename, "r", encoding="utf-8") as f:
                first_chars = f.read(100)
                print(f"First 100 chars: {first_chars}")
        else:
            print(f"ERROR: Failed to create file {report_filename}")
            
        return report_filename
    except Exception as e:
        print(f"Error saving HTML report: {e}")
        traceback.print_exc()
        return None

def prepare_report_data(market_summary, charts, technical_signals, trading_signals, errors):
    """
    Prepare data dictionary for HTML report template.
    
    Args:
        market_summary: Dictionary with S&P 500 summary data
        charts: Dictionary with chart base64 images
        technical_signals: Dictionary with technical signals
        trading_signals: Dictionary with trading signals
        errors: List of errors encountered
        
    Returns:
        dict: Template data
    """
    # Handle market_summary being a dictionary or not
    if not isinstance(market_summary, dict):
        print(f"WARNING: market_summary is not a dict, got {type(market_summary)}")
        market_summary = {}
    
    # Format S&P 500 value and percent change
    sp500_data = market_summary.get('S&P 500', {}) if 'S&P 500' in market_summary else market_summary
    sp500_value = sp500_data.get('value', 'N/A') if isinstance(sp500_data, dict) else 'N/A'
    sp500_value_formatted = f"{sp500_value:.2f}" if isinstance(sp500_value, (float, int)) else str(sp500_value)
    
    sp500_pct_change = sp500_data.get('percent_change', 0) if isinstance(sp500_data, dict) else 0
    sp500_pct_change_formatted = f"{sp500_pct_change:.2f}" if isinstance(sp500_pct_change, (float, int)) else str(sp500_pct_change)
    
    # Handle trading_signals being None or not a dict
    if not isinstance(trading_signals, dict):
        print(f"WARNING: trading_signals is not a dict, got {type(trading_signals)}")
        trading_signals = {}
    
    # Handle technical_signals being None
    if not isinstance(technical_signals, dict):
        print(f"WARNING: technical_signals is not a dict, got {type(technical_signals)}")
        technical_signals = {}
    
    # Convert DataFrames to lists of dicts if needed
    fifty_two_week_high = technical_signals.get('fifty_two_week_high', [])
    if isinstance(fifty_two_week_high, pd.DataFrame) and not fifty_two_week_high.empty:
        fifty_two_week_high = fifty_two_week_high.to_dict('records')
    elif not isinstance(fifty_two_week_high, list):
        fifty_two_week_high = []
    
    crossover_200d = technical_signals.get('crossover_200d', [])
    if isinstance(crossover_200d, pd.DataFrame) and not crossover_200d.empty:
        crossover_200d = crossover_200d.to_dict('records')
    elif not isinstance(crossover_200d, list):
        crossover_200d = []
    
    buy_signals = trading_signals.get('buy_signals', [])
    if isinstance(buy_signals, pd.DataFrame) and not buy_signals.empty:
        buy_signals = buy_signals.to_dict('records')
    elif not isinstance(buy_signals, list):
        buy_signals = []
    
    sell_signals = trading_signals.get('sell_signals', [])
    if isinstance(sell_signals, pd.DataFrame) and not sell_signals.empty:
        sell_signals = sell_signals.to_dict('records')
    elif not isinstance(sell_signals, list):
        sell_signals = []
    
    # Ensure errors is a list
    if not isinstance(errors, list):
        print(f"WARNING: errors is not a list, got {type(errors)}")
        errors = []
    
    # Handle charts being None or not a dict
    if not isinstance(charts, dict):
        print(f"WARNING: charts is not a dict, got {type(charts)}")
        charts = {}
    
    # Prepare template data
    template_data = {
        'sp500_value': sp500_value_formatted,
        'sp500_date': datetime.now().strftime("%Y-%m-%d"),
        'sp500_pct_change': sp500_pct_change_formatted,
        'candle_chart': charts.get('candlestick'),
        'enhanced_chart': charts.get('enhanced'),
        'heatmap': charts.get('heatmap'),
        'macro_chart': charts.get('macro'),
        'fifty_two_week_high': fifty_two_week_high,
        'crossover_200d': crossover_200d,
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'failed_stocks': errors
    }
    
    return template_data