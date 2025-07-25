"""
Debugging script for the Stock Market Analyzer.
This script performs a step-by-step execution of the main_enhanced.py file
with detailed logging to identify issues.
"""
import os
import sys
import traceback
import pandas as pd
from datetime import datetime
import importlib.util
import shutil

# Configure logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_directories():
    """Check if the necessary directories exist."""
    logger.info("Checking directories...")
    
    required_dirs = [
        "mod",
        "mod/analysis",
        "mod/data",
        "mod/utils",
        "mod/visualization",
        "mod/reporting",
        "output",
        "output/charts",
        "logs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        logger.error(f"Missing directories: {missing_dirs}")
        logger.info("Creating missing directories...")
        for dir_path in missing_dirs:
            os.makedirs(dir_path, exist_ok=True)
    else:
        logger.info("All required directories exist.")
    
    # Check for __init__.py files
    missing_inits = []
    for dir_path in required_dirs:
        if dir_path.startswith("mod") and not os.path.exists(os.path.join(dir_path, "__init__.py")):
            missing_inits.append(dir_path)
    
    if missing_inits:
        logger.error(f"Missing __init__.py files in: {missing_inits}")
        logger.info("Creating missing __init__.py files...")
        for dir_path in missing_inits:
            with open(os.path.join(dir_path, "__init__.py"), 'w') as f:
                f.write('"""Package initialization."""\n')
    else:
        logger.info("All required __init__.py files exist.")

def check_template_file():
    """Check if the email template file exists."""
    logger.info("Checking for email_template.html...")
    
    if not os.path.exists("email_template.html"):
        logger.error("email_template.html not found in the current directory!")
        
        # Check if it exists in the user-uploaded files
        doc_template = None
        for file_name in os.listdir('.'):
            if file_name.endswith('.html') and 'email' in file_name.lower() and 'template' in file_name.lower():
                doc_template = file_name
                break
        
        if doc_template:
            logger.info(f"Found similar template file: {doc_template}")
            logger.info(f"Copying {doc_template} to email_template.html...")
            shutil.copy(doc_template, "email_template.html")
        else:
            logger.error("No template file found. The report cannot be generated!")
            return False
    
    logger.info("email_template.html exists.")
    return True

def check_module_imports():
    """Test importing key modules to identify any import issues."""
    logger.info("Testing module imports...")
    
    modules_to_test = [
        "mod.config",
        "mod.analysis.technical",
        "mod.analysis.market",
        "mod.analysis.macro",
        "mod.analysis.dividend",
        "mod.data.fetcher",
        "mod.data.multi_asset",
        "mod.utils.data_utils",
        "mod.utils.image_utils",
        "mod.visualization.candlestick",
        "mod.visualization.indicators",
        "mod.visualization.sector",
        "mod.visualization.macro",
        "mod.visualization.currency",
        "mod.visualization.comparison",
        "mod.reporting.html_generator",
        "mod.reporting.email_sender"
    ]
    
    import_errors = []
    for module_name in modules_to_test:
        try:
            logger.info(f"Importing {module_name}...")
            __import__(module_name)
            logger.info(f"Successfully imported {module_name}")
        except Exception as e:
            logger.error(f"Failed to import {module_name}: {e}")
            import_errors.append((module_name, str(e)))
    
    if import_errors:
        logger.error("Import errors detected:")
        for module, error in import_errors:
            logger.error(f"  - {module}: {error}")
        return False
    
    logger.info("All modules imported successfully.")
    return True

def test_data_loading():
    """Test loading stock universe and data fetching."""
    logger.info("Testing data loading...")
    
    try:
        # Import the necessary modules
        from mod.data.fetcher import load_stock_universe, fetch_symbol_data
        
        # Load stock universe
        logger.info("Loading stock universe...")
        universe = load_stock_universe()
        logger.info(f"Loaded {len(universe)} symbols: {universe}")
        
        # Test fetching data for a single symbol
        logger.info("Testing data fetching for SPY...")
        spy_data = fetch_symbol_data("SPY", period="1mo")
        
        if spy_data is None or spy_data.empty:
            logger.error("Failed to fetch data for SPY")
            return False
        
        logger.info(f"Successfully fetched data for SPY: {len(spy_data)} rows")
        logger.info(f"Columns: {spy_data.columns.tolist()}")
        logger.info(f"First few rows: \n{spy_data.head(3)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing data loading: {e}")
        traceback.print_exc()
        return False

def test_dividend_analysis():
    """Test dividend analysis function."""
    logger.info("Testing dividend analysis...")
    
    try:
        from mod.analysis.dividend import analyze_dividend_history
        
        # Test with a single symbol known to pay dividends
        symbol = "AAPL"
        logger.info(f"Analyzing dividends for {symbol}...")
        
        result = analyze_dividend_history(symbol)
        
        if not isinstance(result, dict):
            logger.error(f"analyze_dividend_history returned {type(result)} instead of dict")
            return False
        
        logger.info(f"Dividend analysis result for {symbol}: {result}")
        return True
    except Exception as e:
        logger.error(f"Error testing dividend analysis: {e}")
        traceback.print_exc()
        return False

def test_html_generation():
    """Test HTML report generation with minimal data."""
    logger.info("Testing HTML generation...")
    
    try:
        # Check if template exists
        if not check_template_file():
            return False
        
        from mod.reporting.html_generator import render_html_report, save_html_report
        
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
        
        # Render the template
        logger.info("Rendering HTML template...")
        html_output = render_html_report(test_data)
        
        if not html_output:
            logger.error("HTML rendering failed - empty output")
            return False
        
        # Save the HTML to a file
        report_filename = save_html_report(html_output)
        
        if not report_filename:
            logger.error("Failed to save HTML report")
            return False
        
        logger.info(f"Successfully generated test HTML file: {report_filename}")
        
        # Check file content
        with open(report_filename, "r", encoding="utf-8") as f:
            content = f.read(200)
            logger.info(f"First 200 characters of the file: {content}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing HTML generation: {e}")
        traceback.print_exc()
        return False

def test_full_report_generation():
    """Test the full report generation process step by step."""
    logger.info("Testing full report generation process...")
    
    try:
        # Import necessary modules
        from mod.data.fetcher import load_stock_universe, fetch_symbol_data
        from mod.analysis.market import calculate_percent_changes, find_technical_patterns, find_trading_opportunities, get_market_summary
        from mod.analysis.dividend import analyze_dividend_history
        from mod.data.multi_asset import generate_multi_asset_report
        from mod.visualization.candlestick import generate_candlestick_chart
        from mod.visualization.indicators import generate_enhanced_candlestick_chart
        from mod.visualization.sector import generate_sector_heatmap
        from mod.visualization.macro import generate_macro_chart
        from mod.visualization.currency import generate_forex_chart
        from mod.visualization.comparison import generate_volatility_comparison
        from mod.reporting.html_generator import prepare_report_data, render_html_report, save_html_report
        
        # 1) Load stock universe
        logger.info("1. Loading stock universe...")
        df_universe = load_stock_universe()
        logger.info(f"Loaded {len(df_universe)} symbols")
        
        # 2) Calculate daily percent changes
        logger.info("2. Calculating daily percent changes...")
        df_percent_changes = calculate_percent_changes(df_universe)
        
        if isinstance(df_percent_changes, pd.DataFrame):
            logger.info(f"Percent changes calculated: {len(df_percent_changes)} rows")
        else:
            logger.warning(f"calculate_percent_changes returned {type(df_percent_changes)}, not DataFrame")
        
        # 3) Find technical patterns
        logger.info("3. Finding technical patterns...")
        fifty_two_week_high, crossover_200d, technical_errors = find_technical_patterns(df_universe)
        
        logger.info(f"Technical patterns found: {len(fifty_two_week_high)} 52-week highs, {len(crossover_200d)} 200-day MA crossovers")
        
        if technical_errors:
            logger.warning(f"Technical analysis errors: {len(technical_errors)}")
        
        # 4) Find trading opportunities
        logger.info("4. Finding trading opportunities...")
        trading_signals = find_trading_opportunities(df_universe)
        
        if isinstance(trading_signals, pd.DataFrame):
            logger.info(f"Trading opportunities found: {len(trading_signals)} signals")
        elif isinstance(trading_signals, dict):
            buy_signals = trading_signals.get('buy_signals', [])
            sell_signals = trading_signals.get('sell_signals', [])
            logger.info(f"Trading signals: {len(buy_signals)} buy, {len(sell_signals)} sell")
        else:
            logger.warning(f"find_trading_opportunities returned {type(trading_signals)}")
        
        # 5) Analyze dividend history
        logger.info("5. Analyzing dividends...")
        top_stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        dividend_analysis = analyze_dividend_history(top_stocks)
        
        if isinstance(dividend_analysis, dict):
            logger.info(f"Dividend analysis completed for {len(dividend_analysis)} stocks")
        else:
            logger.warning(f"analyze_dividend_history returned {type(dividend_analysis)}, not dict")
            # Convert to dict if needed
            if hasattr(dividend_analysis, 'to_dict'):
                dividend_analysis = dividend_analysis.to_dict('index')
                logger.info("Converted dividend_analysis to dict")
            else:
                dividend_analysis = {}
        
        # 6) Generate multi-asset report
        logger.info("6. Generating multi-asset report...")
        multi_asset_data = generate_multi_asset_report()
        
        if isinstance(multi_asset_data, dict):
            logger.info(f"Multi-asset report generated with keys: {list(multi_asset_data.keys())}")
        else:
            logger.warning(f"generate_multi_asset_report returned {type(multi_asset_data)}, not dict")
            multi_asset_data = {'currency': {}, 'etfs': {}}
        
        # 7) Get market summary
        logger.info("7. Getting market summary...")
        market_summary = get_market_summary()
        
        if isinstance(market_summary, dict):
            logger.info(f"Market summary generated with keys: {list(market_summary.keys())}")
        else:
            logger.warning(f"get_market_summary returned {type(market_summary)}, not dict")
            market_summary = {}
        
        # 8) Generate charts
        logger.info("8. Generating charts...")
        
        # Candlestick chart
        logger.info("  - Generating candlestick chart...")
        candle_b64 = generate_candlestick_chart()
        
        # Enhanced chart
        logger.info("  - Generating enhanced chart...")
        spy_data = fetch_symbol_data("SPY", period="3mo", interval="1d")
        enhanced_b64 = None
        if spy_data is not None and not spy_data.empty:
            enhanced_b64 = generate_enhanced_candlestick_chart(df=spy_data, ticker="SPY")
        
        # Sector heatmap
        logger.info("  - Generating sector heatmap...")
        heatmap_b64 = generate_sector_heatmap(df_universe)
        
        # Macro chart
        logger.info("  - Generating macro chart...")
        macro_b64 = generate_macro_chart()
        
        # Forex chart
        logger.info("  - Generating forex chart...")
        forex_b64 = generate_forex_chart()
        
        # Volatility comparison
        logger.info("  - Generating volatility comparison...")
        volatility_b64 = generate_volatility_comparison(top_stocks)
        
        # Collect all charts
        charts = {
            'candlestick': candle_b64,
            'enhanced': enhanced_b64,
            'heatmap': heatmap_b64,
            'macro': macro_b64,
            'forex': forex_b64,
            'volatility': volatility_b64
        }
        
        logger.info(f"Charts generated: {[key for key, val in charts.items() if val is not None]}")
        
        # Prepare technical signals data
        technical_signals = {
            'fifty_two_week_high': fifty_two_week_high if isinstance(fifty_two_week_high, list) else 
                                 (fifty_two_week_high.to_dict('records') if hasattr(fifty_two_week_high, 'to_dict') else []),
            'crossover_200d': crossover_200d if isinstance(crossover_200d, list) else 
                            (crossover_200d.to_dict('records') if hasattr(crossover_200d, 'to_dict') else [])
        }
        
        # Prepare errors list
        if not isinstance(technical_errors, list):
            technical_errors = []
        
        trading_errors = []
        if isinstance(trading_signals, dict) and 'errors' in trading_signals:
            trading_errors = trading_signals.get('errors', [])
        
        all_errors = technical_errors + trading_errors
        
        # 9) Prepare report data
        logger.info("9. Preparing report data...")
        report_data = prepare_report_data(
            market_summary,
            charts,
            technical_signals,
            trading_signals,
            all_errors
        )
        
        if isinstance(report_data, dict):
            logger.info(f"Report data prepared with keys: {list(report_data.keys())}")
        else:
            logger.error(f"prepare_report_data returned {type(report_data)}, not dict")
            return False
        
        # Add additional data
        report_data.update({
            'dividend_analysis': dividend_analysis,
            'currency_data': multi_asset_data.get('currency', {}),
            'etf_data': multi_asset_data.get('etfs', {}),
            'forex_chart': forex_b64,
            'volatility_chart': volatility_b64
        })
        
        # 10) Render HTML report
        logger.info("10. Rendering HTML report...")
        html_output = render_html_report(report_data)
        
        if not html_output:
            logger.error("HTML rendering failed - empty output")
            return False
        
        # Save HTML report
        logger.info("11. Saving HTML report...")
        report_filename = save_html_report(html_output)
        
        if not report_filename:
            logger.error("Failed to save HTML report")
            return False
        
        logger.info(f"Report saved successfully as: {report_filename}")
        
        # Check file content
        with open(report_filename, "r", encoding="utf-8") as f:
            content = f.read(200)
            logger.info(f"First 200 characters of the file: {content}")
        
        return True
    except Exception as e:
        logger.error(f"Error in full report generation: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to run all diagnostic tests."""
    logger.info("Starting Stock Market Analyzer diagnostic tests...")
    
    # Check directories and __init__.py files
    check_directories()
    
    # Check for email template
    if not check_template_file():
        logger.error("Cannot proceed without email_template.html")
        return
    
    # Check module imports
    if not check_module_imports():
        logger.error("Module import errors detected. Please fix before continuing.")
        return
    
    # Test data loading
    if not test_data_loading():
        logger.error("Data loading test failed.")
        return
    
    # Test dividend analysis
    if not test_dividend_analysis():
        logger.warning("Dividend analysis test failed. This may affect the final report.")
    
    # Test HTML generation
    if not test_html_generation():
        logger.error("HTML generation test failed.")
        return
    
    # Test full report generation
    logger.info("Running full report generation test...")
    if test_full_report_generation():
        logger.info("SUCCESS! Full report generation completed successfully.")
    else:
        logger.error("Full report generation test failed.")

if __name__ == "__main__":
    main()