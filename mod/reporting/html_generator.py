"""
HTML report generation functions.
"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from ..config import TEMPLATE_DIR, TEMPLATE_FILE

def render_html_report(data):
    """
    Render HTML report using Jinja2 template.
    
    Args:
        data: Dictionary with data for the template
        
    Returns:
        str: Rendered HTML content
    """
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(TEMPLATE_FILE)
        
        # Render the template with the provided data
        html_output = template.render(**data)
        
        return html_output
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        return f"<html><body><h1>Error generating report</h1><p>{str(e)}</p></body></html>"

def save_html_report(html_content):
    """
    Save the HTML report to a file.
    
    Args:
        html_content: HTML content to save
        
    Returns:
        str: Filename of the saved report
    """
    try:
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.html"
        
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"HTML report saved as {report_filename}")
        return report_filename
    except Exception as e:
        print(f"Error saving HTML report: {e}")
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
    # Format S&P 500 value and percent change
    sp500_value = market_summary.get('value')
    sp500_value_formatted = f"{sp500_value:.2f}" if isinstance(sp500_value, float) else sp500_value
    
    sp500_pct_change = market_summary.get('pct_change')
    sp500_pct_change_formatted = f"{sp500_pct_change:.2f}" if isinstance(sp500_pct_change, float) else sp500_pct_change
    
    # Prepare template data
    template_data = {
        'sp500_value': sp500_value_formatted,
        'sp500_date': market_summary.get('date', ''),
        'sp500_pct_change': sp500_pct_change_formatted,
        'candle_chart': charts.get('candlestick'),
        'enhanced_chart': charts.get('enhanced'),
        'heatmap': charts.get('heatmap'),
        'macro_chart': charts.get('macro'),
        'fifty_two_week_high': technical_signals.get('fifty_two_week_high', []),
        'crossover_200d': technical_signals.get('crossover_200d', []),
        'buy_signals': trading_signals.get('buy_signals', []),
        'sell_signals': trading_signals.get('sell_signals', []),
        'failed_stocks': errors
    }
    
    return template_data