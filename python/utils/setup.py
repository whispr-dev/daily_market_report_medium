"""
Setup script for the stock_analyzer package.
"""
from setuptools import setup, find_packages
import subprocess
import sys
import os

# First, let's install the dependencies directly
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
    # Add sendemail or other custom dependencies here
]

# Install required packages upfront if --build flag is present
if "--build" in sys.argv:
    sys.argv.remove("--build")  # Remove the custom flag so setuptools doesn't complain
    print("Installing dependencies to user directory...")
    
    # Using --user flag to install to user directory without admin privileges
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            print("Trying without --user flag...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installed without --user flag")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install manually.")
    
    print("\nAll dependencies installed! You can now use the package.")
    
    # Skip the actual setup.py install part to avoid permission errors
    if len(sys.argv) == 1:  # Only --build was provided (and removed above)
        sys.exit(0)

setup(
    name="stock_analyzer",
    version="0.1.3",
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        "console_scripts": [
            "stock-report=stock_analyzer.main:main",
        ],
    },
    python_requires=">=3.7",
    author="whisprer",
    author_email="whisprer@whispr.dev",
    description="A daily stock market report generator",
    keywords="stocks, finance, market, analysis",
)