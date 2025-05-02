"""
Simple script to install all required dependencies for the stock analyzer package.
This avoids the deprecated setup.py install approach.
"""
import subprocess
import sys
import os

REQUIRED_PACKAGES = [
    "yfinance",
    "pandas",
    "numpy",
    "matplotlib",
    "mplfinance",
    "seaborn",
    "statsmodels",
    "pandas-datareader",
    "jinja2",
    # Add sendemail or other custom dependencies here
]

def main():
    print("Installing dependencies for stock_analyzer...")
    print("=" * 50)
    
    # Try to install packages with --user flag first
    success_count = 0
    for package in REQUIRED_PACKAGES:
        print(f"\nInstalling {package}...")
        try:
            # Using --user flag to avoid permission errors
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            success_count += 1
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"Couldn't install with --user flag, trying regular install...")
            try:
                # Try without --user flag in case in a virtual environment
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                success_count += 1
                print(f"✓ {package} installed without --user flag")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
    
    print("\n" + "=" * 50)
    print(f"Installation complete: {success_count}/{len(REQUIRED_PACKAGES)} packages installed successfully")
    
    if success_count != len(REQUIRED_PACKAGES):
        print("\nSome packages failed to install. You may need to:")
        print("1. Run this script as administrator")
        print("2. Install packages manually with: pip install <package-name>")
        print("3. Use a virtual environment")
    else:
        print("\nAll dependencies installed successfully! Your stock analyzer is ready to use.")

if __name__ == "__main__":
    main()