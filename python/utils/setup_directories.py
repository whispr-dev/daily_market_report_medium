"""
Script to set up the necessary directory structure and __init__.py files.
"""
import os
import sys

def create_dir_with_init(dir_path):
    """Create directory and add __init__.py file if it doesn't exist."""
    if not os.path.exists(dir_path):
        print(f"Creating directory: {dir_path}")
        os.makedirs(dir_path)
    
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        print(f"Creating __init__.py in: {dir_path}")
        with open(init_file, 'w') as f:
            f.write('"""Module initialization."""\n')

def main():
    """Set up the required directory structure."""
    # Define the project directory structure
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create mod directory if it doesn't exist
    mod_dir = os.path.join(root_dir, "mod")
    create_dir_with_init(mod_dir)
    
    # Create subdirectories
    subdirs = [
        "analysis",
        "data",
        "utils",
        "visualization",
        "reporting"
    ]
    
    for subdir in subdirs:
        create_dir_with_init(os.path.join(mod_dir, subdir))
    
    # Create output directories
    output_dirs = [
        "output",
        "output/charts",
        "logs"
    ]
    
    for output_dir in output_dirs:
        output_path = os.path.join(root_dir, output_dir)
        if not os.path.exists(output_path):
            print(f"Creating output directory: {output_path}")
            os.makedirs(output_path)
    
    # Create mod/__init__.py with imports to make imports cleaner
    mod_init_content = '''"""
Stock Market Analyzer package.
"""
# Import main modules to make imports cleaner
from .analysis import analyze_technicals, calculate_ewo, detect_reversal_signals
from .analysis import find_trading_opportunities, get_market_summary
from .analysis import prepare_macro_data, generate_forecast
from .analysis import analyze_dividend_history
'''
    
    with open(os.path.join(mod_dir, "__init__.py"), 'w') as f:
        f.write(mod_init_content)
    
    print("\nDirectory structure set up successfully!")
    print("Make sure to place your Python files in the appropriate directories.")
    print("Then you can run: python -m mod.main_enhanced")

if __name__ == "__main__":
    main()