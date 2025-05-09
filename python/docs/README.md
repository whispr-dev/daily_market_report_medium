# Stock Market Analyzer

A modular Python application that generates and emails daily stock market reports with technical analysis and visualizations.

## Features

- Candlestick charts for S&P 500
- Technical indicator analysis (EWO, reversal signals)
- Sector performance heatmap
- Macroeconomic trend analysis (S&P, BTC, M2 money supply)
- 52-week high and 200-day MA crossover detection
- Buy/sell signal generation based on custom criteria
- Automated email reporting

## Project Structure

```
stock_analyzer/
├── main.py                 # Entry point
├── config.py               # Configuration and global settings
├── utils/                  # Utility functions
│   ├── image_utils.py      # Image utilities
│   └── data_utils.py       # Data processing utilities
├── analysis/               # Analysis modules
│   ├── technical.py        # Technical analysis functions
│   ├── market.py           # Market analysis functions
│   └── macro.py            # Macroeconomic analysis
├── visualization/          # Visualization modules
│   ├── candlestick.py      # Candlestick chart generation
│   ├── indicators.py       # Technical indicator visualizations
│   ├── sector.py           # Sector analysis visualizations
│   └── macro.py            # Macro trend visualizations
├── data/                   # Data modules
│   └── fetcher.py          # Data fetching functions
├── reporting/              # Reporting modules
│   ├── html_generator.py   # HTML report generation
│   └── email_sender.py     # Email functionality
├── templates/              # HTML templates
│   └── email_template.html
└── logs/                   # Log directory
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/stock-analyzer.git
   cd stock-analyzer
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Configure your stock universe by creating a `stocks_universe.csv` file with at least the following columns:
   - symbol: Stock ticker symbol
   - sector: Market sector

## Usage

Run the application with:

```
python -m stock_analyzer.main
```

Or if installed via pip:

```
stock-report
```

## Configuration

Edit `config.py` to customize:
- Chart styling
- Technical analysis parameters
- Time periods for analysis
- File paths

## Dependencies

- yfinance
- pandas
- numpy
- matplotlib
- mplfinance
- seaborn
- statsmodels
- pandas-datareader
- jinja2
- sendemail (custom module for email sending)

## License

[MIT License](LICENSE)