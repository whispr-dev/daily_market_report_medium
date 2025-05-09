"""
Script to install the package in development mode and all dependencies.
"""
import subprocess
import sys
import os

def main():
    print("Installing stock_analyzer package in development mode...")
    
    # Installing dependencies
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
        "premailer",
        "flask",
    ]
    
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}: {e}")
    
    # Install the current package in development mode
    try:
        print("\nInstalling this package in development mode...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("\nSuccess! Your package is now installed in development mode.")
        print("You can run your main script from anywhere with: python -m mod.main_enhanced")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package in development mode: {e}")
        print("Make sure you have a valid setup.py file.")

if __name__ == "__main__":
    main()