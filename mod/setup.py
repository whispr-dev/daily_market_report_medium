"""
Setup script for the stock_analyzer package.
"""
from setuptools import setup, find_packages

setup(
    name="stock_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
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
    ],
    entry_points={
        "console_scripts": [
            "stock-report=stock_analyzer.main:main",
        ],
    },
    python_requires=">=3.7",
    author="Your Name",
    author_email="your.email@example.com",
    description="A daily stock market report generator",
    keywords="stocks, finance, market, analysis",
)