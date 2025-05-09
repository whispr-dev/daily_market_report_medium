"""
Script to fix Python package structure by creating __init__.py files
and fixing relative imports.
"""
import os
import re

def create_init_files():
    """Create necessary __init__.py files."""
    base_dir = r"D:\code\repos\GitHub_Desktop\daily_stonk_market_report"
    
    # Directories that need __init__.py files
    dirs = [
        os.path.join(base_dir, "mod"),
        os.path.join(base_dir, "mod", "data"),
        os.path.join(base_dir, "mod", "utils")
    ]
    
    for directory in dirs:
        init_file = os.path.join(directory, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# This file makes Python treat the directory as a package\n")
        print(f"Created {init_file}")

def fix_imports():
    """Fix relative imports in fetcher.py."""
    fetcher_file = r"D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\data\fetcher.py"
    
    # Read the file
    with open(fetcher_file, 'r') as f:
        content = f.read()
    
    # Replace the relative import with absolute import
    # Pattern matches:   from ..utils.data_utils import clean_yfinance_dataframe, fix_missing_values
    pattern = r"from \.\.(utils\.data_utils) import (.*)"
    replacement = r"from mod.\1 import \2"
    
    new_content = re.sub(pattern, replacement, content)
    
    # Write the modified content back
    with open(fetcher_file, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed imports in {fetcher_file}")

def fix_main_file():
    """Fix imports in main_enhanced.py."""
    main_file = r"D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\main_enhanced.py"
    
    # Read the file
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Replace local imports with absolute imports
    # Pattern matches: from data.fetcher import load_stock_universe
    pattern = r"from (data\.fetcher) import (.*)"
    replacement = r"from mod.\1 import \2"
    
    new_content = re.sub(pattern, replacement, content)
    
    # Write the modified content back
    with open(main_file, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed imports in {main_file}")

def main():
    """Run all fix functions."""
    print("===================================================")
    print("Fixing Python package structure for stock analyzer")
    print("===================================================\n")
    
    create_init_files()
    print("")
    fix_imports()
    print("")
    fix_main_file()
    
    print("\n===================================================")
    print("Setup complete! Now try one of these methods:")
    print("")
    print("OPTION 1: Run as a module (recommended)")
    print("  cd D:\\code\\repos\\GitHub_Desktop\\daily_stonk_market_report")
    print("  python -m mod.main_enhanced")
    print("")
    print("OPTION 2: Install as a package")
    print("  cd D:\\code\\repos\\GitHub_Desktop\\daily_stonk_market_report")
    print("  pip install -e .")
    print("  python -m mod.main_enhanced")
    print("===================================================")

if __name__ == "__main__":
    main()