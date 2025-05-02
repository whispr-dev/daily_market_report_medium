# Stock Market Analyzer Setup Guide

This guide will help you set up and run the Stock Market Analyzer application which generates daily reports with technical analysis and visualizations.

## Prerequisites

- Python 3.8+ installed
- Required Python packages (yfinance, pandas, matplotlib, etc.)
- Email credentials for sending reports (optional)

## Installation

1. **Set up directory structure**
   
   Make sure your directory structure matches the one in the README:

   ```
   stock_analyzer/
   ├── mod/
   │   ├── __init__.py
   │   ├── analysis/
   │   │   ├── __init__.py
   │   │   ├── technical.py
   │   │   ├── market.py
   │   │   ├── macro.py
   │   │   └── dividend.py
   │   ├── data/
   │   │   ├── __init__.py
   │   │   ├── fetcher.py
   │   │   └── multi_asset.py
   │   ├── utils/
   │   │   ├── __init__.py
   │   │   ├── image_utils.py
   │   │   ├── data_utils.py
   │   │   └── stock_universe_converter.py
   │   ├── visualization/
   │   │   ├── __init__.py
   │   │   ├── candlestick.py
   │   │   ├── indicators.py
   │   │   ├── sector.py
   │   │   ├── macro.py
   │   │   ├── currency.py
   │   │   └── comparison.py
   │   ├── reporting/
   │   │   ├── __init__.py
   │   │   ├── html_generator.py
   │   │   └── email_sender.py
   │   ├── config.py
   │   └── main_enhanced.py
   ├── email_template.html
   ├── output/
   │   └── charts/
   └── logs/
   ```

2. **Install dependencies**

   Run the dependency installation script:

   ```
   python install_Deps.py
   ```

   Or install them manually:

   ```
   pip install yfinance pandas numpy matplotlib mplfinance seaborn statsmodels pandas-datareader jinja2
   ```

3. **Setup Email (Optional)**

   Set the following environment variables for email functionality:

   - `EMAILSENDER`: Your email address
   - `EMAILPASSWORD`: Your email password or app-specific password
   - `EMAILSMTP`: SMTP server (e.g., smtp.gmail.com)
   - `EMAILPORT`: SMTP port (e.g., 587)
   - `EMAILRECIPIENT`: Recipient email address(es), comma-separated

   In Windows PowerShell:
   ```
   $env:EMAILSENDER="your-email@gmail.com"
   $env:EMAILPASSWORD="your-password"
   $env:EMAILSMTP="smtp.gmail.com"
   $env:EMAILPORT="587"
   $env:EMAILRECIPIENT="recipient@example.com"
   ```

   In Linux/Mac:
   ```
   export EMAILSENDER="your-email@gmail.com"
   export EMAILPASSWORD="your-password"
   export EMAILSMTP="smtp.gmail.com"
   export EMAILPORT="587"
   export EMAILRECIPIENT="recipient@example.com"
   ```

## Running the Application

To generate a stock market report:

```
python -m mod.main_enhanced
```

This will:
1. Load stock universe
2. Fetch market data
3. Perform technical and fundamental analysis
4. Generate visualizations
5. Create an HTML report
6. Send the report via email (if configured)

## Troubleshooting

If you encounter issues with visualization modules, run the visualization fix script:

```
python simple_chart_fix.py
```

For other issues:

1. Check all required directories and files are in place
2. Ensure __init__.py files exist in each directory
3. Verify email configuration if using email functionality
4. Check the logs directory for error messages

## Customization

- Edit `config.py` to customize chart styling and technical parameters
- Create a `stocks_universe.csv` file with your preferred stocks
- Modify `email_template.html` to change the report layout

## Additional Features

- **Multi-asset analysis**: The enhanced version supports stocks, ETFs, and forex
- **Dividend analysis**: Track dividend performance and history
- **Volatility comparison**: Compare volatility across different securities
- **Forex tracking**: Monitor major currency pairs

---

### Happy stonks scanning! Feel free to open issues or pull requests if you discover improvements or want to share your customizations.

---
