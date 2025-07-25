"""
Simple script to generate a stock market report with minimal processing.
This script bypasses most of the data processing steps and focuses on generating
a valid HTML report with placeholder data.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import io
import matplotlib.pyplot as plt
import traceback

def create_sample_chart():
    """Create a simple sample chart for testing."""
    try:
        # Create a simple chart
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Sample Chart")
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.grid(True)
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_data
    except Exception as e:
        print(f"Error creating sample chart: {e}")
        return None

def render_html_report(data):
    """
    Render HTML report using Jinja2 template.
    
    Args:
        data: Dictionary with data for the template
        
    Returns:
        str: Rendered HTML content
    """
    try:
        from jinja2 import Environment, FileSystemLoader
        
        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('email_template.html')
        
        # Render the template with the provided data
        html_output = template.render(**data)
        
        return html_output
    except Exception as e:
        print(f"Error rendering HTML template: {e}")
        traceback.print_exc()
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
        report_filename = f"simple_report_{timestamp}.html"
        
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"HTML report saved as {report_filename}")
        return report_filename
    except Exception as e:
        print(f"Error saving HTML report: {e}")
        return None

def main():
    """Generate a simple stock market report."""
    print("Generating simple stock market report...")
    
    try:
        # Check if template exists
        if not os.path.exists("email_template.html"):
            print("Error: email_template.html not found in current directory!")
            return
        
        # Create sample chart
        sample_chart = create_sample_chart()
        
        # Prepare minimal data for the template
        report_data = {
            'sp500_value': '4,356.78',
            'sp500_date': datetime.now().strftime("%Y-%m-%d"),
            'sp500_pct_change': '1.25',
            'candle_chart': sample_chart,
            'enhanced_chart': sample_chart,
            'heatmap': sample_chart,
            'macro_chart': sample_chart,
            'forex_chart': sample_chart,
            'volatility_chart': sample_chart,
            'fifty_two_week_high': [
                {'symbol': 'AAPL', 'current_price': 175.25, 'year_high': 177.50},
                {'symbol': 'MSFT', 'current_price': 345.75, 'year_high': 350.00}
            ],
            'crossover_200d': [
                {'symbol': 'AMZN', 'current_price': 125.30, 'ma_200': 124.75},
                {'symbol': 'GOOGL', 'current_price': 125.30, 'ma_200': 124.75}
            ],
            'buy_signals': [
                {'symbol': 'NVDA', 'reason': 'Strong momentum with good relative strength'},
                {'symbol': 'AMD', 'reason': 'Bullish crossover of 50-day MA'}
            ],
            'sell_signals': [
                {'symbol': 'XOM', 'reason': 'Bearish trend reversal'},
                {'symbol': 'T', 'reason': 'Breaking below support level'}
            ],
            'failed_stocks': ['BAC: No data', 'GE: API error'],
            'dividend_analysis': {
                'AAPL': {'latest_dividend': 0.24, 'annual_dividend': 0.96, 'dividend_count': 4, 'dividend_yield': 0.55},
                'MSFT': {'latest_dividend': 0.75, 'annual_dividend': 3.00, 'dividend_count': 4, 'dividend_yield': 0.85}
            },
            'currency_data': {
                'EURUSD=X': {'current_rate': 1.085, 'day_change': 0.25},
                'GBPUSD=X': {'current_rate': 1.265, 'day_change': -0.15}
            },
            'etf_data': {
                'SPY': {'yield': 1.45, 'ytd_return': 12.5},
                'QQQ': {'yield': 0.65, 'ytd_return': 15.8}
            }
        }
        
        # Render HTML report
        print("Rendering HTML template...")
        html_output = render_html_report(report_data)
        
        # Save HTML report
        report_filename = save_html_report(html_output)
        
        if report_filename:
            print(f"Simple report generated successfully: {report_filename}")
            print(f"Open {report_filename} in your web browser to view the report.")
        else:
            print("Failed to generate report.")
            
    except Exception as e:
        print(f"Error generating simple report: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()