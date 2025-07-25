"""
Script to test HTML report generation with minimal data.
"""
import os
import sys
from datetime import datetime

def ensure_template_exists():
    """Make sure we have a template file to use."""
    template_file = "email_template.html"
    if not os.path.exists(template_file):
        print(f"ERROR: Template file '{template_file}' not found in the current directory!")
        print(f"Current directory: {os.getcwd()}")
        print("Please make sure the template file exists.")
        return False
    return True

def test_simple_html_generation():
    """Test HTML generation with minimal data."""
    try:
        from jinja2 import Environment, FileSystemLoader
        
        # Check if template exists
        if not ensure_template_exists():
            return
        
        # Create minimal test data
        test_data = {
            'sp500_value': '4,200.50',
            'sp500_date': datetime.now().strftime("%Y-%m-%d"),
            'sp500_pct_change': '0.75',
            'candle_chart': None,
            'enhanced_chart': None,
            'heatmap': None,
            'macro_chart': None,
            'fifty_two_week_high': [],
            'crossover_200d': [],
            'buy_signals': [],
            'sell_signals': [],
            'failed_stocks': [],
            'dividend_analysis': {},
            'currency_data': {},
            'etf_data': {},
            'forex_chart': None,
            'volatility_chart': None
        }
        
        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('email_template.html')
        
        # Render the template
        print("Rendering template...")
        html_output = template.render(**test_data)
        
        # Save the HTML to a file
        output_file = "test_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_output)
        
        print(f"Successfully generated test HTML file: {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
        
        # Print the first 100 characters to verify content
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read(200)
            print("\nFirst 200 characters of the file:")
            print(content)
        
        return True
    except Exception as e:
        print(f"Error testing HTML generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_imports():
    """Test importing key modules to identify any import issues."""
    modules_to_test = [
        "mod.reporting.html_generator",
        "mod.analysis.dividend",
        "mod.analysis.market",
        "mod.data.fetcher",
        "mod.visualization.indicators"
    ]
    
    print("\nTesting module imports:")
    for module_name in modules_to_test:
        try:
            print(f"Importing {module_name}...", end="")
            __import__(module_name)
            print(" Success!")
        except Exception as e:
            print(f" FAILED! Error: {e}")
    
    print("\nMake sure all __init__.py files are in place in your directory structure.")

if __name__ == "__main__":
    print("Testing HTML generation...\n")
    success = test_simple_html_generation()
    
    if success:
        print("\nHTML generation test passed! The template is rendering correctly.")
        print("The issue may be with the data being passed to the template.")
    else:
        print("\nHTML generation test failed.")
        print("There seems to be an issue with the template or Jinja2 setup.")
    
    # Test imports
    test_module_imports()