"""
Enhanced Daily Stock Market Report Generator
Includes security features, background tasks, and monitoring.
"""
import os
import time
import traceback
import logging
import json
import pandas as pd
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup Celery for background tasks
try:
    from celery import Celery
    from celery.schedules import crontab
    
    # Create Celery app
    celery_app = Celery('dailystonks',
                        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))
    
    # Configure periodic tasks
    celery_app.conf.beat_schedule = {
        'generate-daily-report': {
            'task': 'main_enhanced.generate_daily_report',
            'schedule': crontab(hour=16, minute=30),  # 4:30 PM, after market close
        },
        'send-report-emails': {
            'task': 'main_enhanced.send_report_emails',
            'schedule': crontab(hour=17, minute=0),   # 5:00 PM, after report generation
        },
        'cleanup-old-reports': {
            'task': 'main_enhanced.cleanup_old_reports',
            'schedule': crontab(hour=3, minute=0),    # 3:00 AM, daily cleanup
        },
    }
    
    celery_enabled = True
    logger.info("Celery background tasks enabled")
except ImportError:
    celery_app = None
    celery_enabled = False
    logger.warning("Celery not available, background tasks disabled")

from mod.analysis.confluence import get_multi_timeframe_signals

from mod.analysis.volatility import detect_volatility_squeezes

print("Detecting volatility squeezes...")
squeeze_signals = detect_volatility_squeezes(universe)
report_data["volatility_squeezes"] = squeeze_signals

print("Analyzing multi-timeframe confluence...")
multi_signals = get_multi_timeframe_signals(universe)

report_data["multi_timeframe_signals"] = multi_signals

from mod.analysis.rotation import rank_relative_strength

print("Ranking relative strength...")
rs_ranks = rank_relative_strength(universe)
report_data["relative_strength"] = rs_ranks

from mod.analysis.edge_score import calculate_whispr_edge_score

print("Calculating Whispr Edge™ scores...")

edge_scores = []

for ticker in universe:
    rev = next((x["signal"] for x in buy_signals if x["ticker"] == ticker), None)
    con = any(x["ticker"] == ticker for x in multi_timeframe_signals)
    sqz = any(x["ticker"] == ticker for x in squeeze_signals)
    rs = next((x["rs_score"] for x in rs_ranks if x["ticker"] == ticker), None)

    score, reasons = calculate_whispr_edge_score(
        ticker,
        reversal=rev,
        squeeze=sqz,
        rs_score=rs,
        confluence=con
    )

    if score > 0:
        edge_scores.append({
            "ticker": ticker,
            "score": score,
            "reasons": reasons
        })

# Sort highest first
edge_scores.sort(key=lambda x: x["score"], reverse=True)
report_data["whispr_edge"] = edge_scores

from mod.analysis.edge_tracker import save_edge_scores, load_edge_history

from mod.ml.ml_fusion import train_models_from_edge_data

edge_data_for_training = []

for entry in edge_scores:
    edge_data_for_training.append({
        "ticker": entry["ticker"],
        "score": entry["score"],
        "reversal": next((x["signal"] for x in buy_signals if x["ticker"] == entry["ticker"]), None),
        "squeeze": any(x["ticker"] == entry["ticker"] for x in squeeze_signals),
        "confluence": any(x["ticker"] == entry["ticker"] for x in multi_timeframe_signals),
        "rs_score": next((x["rs_score"] for x in rs_ranks if x["ticker"] == entry["ticker"]), 0)
    })

train_models_from_edge_data(edge_data_for_training)

from mod.ml.ml_fusion import predict_confidence

entry["confidence"] = predict_confidence(entry)

# def predict_ml_score(entry):
#     import xgboost as xgb
#     import joblib
#
#     vec = [get_feature_vector(entry)]
# 
#     xgb_model = xgb.XGBRegressor()
#     xgb_model.load_model("models/xgboost_edge.model")
#     return xgb_model.predict(vec)[0]
# 
# Save current scores
# save_edge_scores(edge_scores)

from mod.backtest.edge_backtester import run_backtest, plot_backtest_summary

results = run_backtest(lookahead_days=5)
if results is not None:
    plot_backtest_summary(results)

# Load past scores for comparison
history_df = load_edge_history()

for entry in edge_scores:
    ticker = entry["ticker"]
    now = entry["score"]

    recent_scores = history_df[history_df["ticker"] == ticker].sort_values("timestamp")
    if not recent_scores.empty:
        past = recent_scores.iloc[0]["score"]
        delta = now - past
        entry["delta"] = round(delta, 2)
    else:
        entry["delta"] = None

from mod.overlay.dark_pool import detect_dark_pool_signals, log_dark_pool_alerts

from mod.overlay.risk_heatmap import compute_reversal_risk

print("Calculating reversal risk heatmap...")
risk_summary = compute_reversal_risk(universe)
report_data["reversal_risk"] = risk_summary

# Detect + log
dark_signals = detect_dark_pool_signals(universe)
log_dark_pool_alerts(dark_signals)
report_data["dark_pool_alerts"] = dark_signals

from mod.overlay.risk_heatmap import log_reversal_risk_summary
log_reversal_risk_summary(risk_summary)

from mod.forecast.simple_forecast import log_forecast_data
log_forecast_data(forecast_data)

from mod.analysis.edge_composite import compute_composite_score

print("Computing Whispr Edge™ composite scores...")

composite_scores = []

from mod.forecast.bayesian_forecast import bayesian_forecast

bayesian_outlooks = []

for ticker in universe[:5]:  # Limit to top 5 to save time
    df = get_stock_data(ticker, period="3mo")
    if df is None or len(df) < 30:
        continue

    forecast, low, high = bayesian_forecast(df, days=5)
    bayesian_outlooks.append({
        "ticker": ticker,
        "forecast": forecast[-1],
        "range": f"{round(low[-1],2)} – {round(high[-1],2)}"
    })

report_data["bayesian_outlook"] = bayesian_outlooks

for entry in edge_scores:
    ticker = entry["ticker"]
    pred = entry["score"]
    conf = entry.get("confidence", 50)

    forecast = next((f["slope"] for f in forecast_data if f["ticker"] == ticker), 0)
    if ticker in risk_summary["high_risk"]:
        risk = "high"
    elif ticker in risk_summary["low_risk"]:
        risk = "low"
    else:
        risk = "neutral"

    final_score, reasons = compute_composite_score(pred, forecast, risk, conf)

    composite_scores.append({
        "ticker": ticker,
        "edge_score": final_score,
        "explanation": reasons
    })

composite_scores.sort(key=lambda x: x["edge_score"], reverse=True)
report_data["whispr_composite"] = composite_scores

from mod.analysis.edge_composite import log_composite_scores

log_composite_scores(composite_scores)

from mod.ml.autoencoder_anomaly import detect_anomalies

print("Computing anomaly scores...")
anomaly_scores = {}

for ticker in universe:
    df = get_stock_data(ticker, period="3mo")
    if df is None or len(df) < 30:
        continue
    scores = detect_anomalies(df)
    anomaly_scores[ticker] = scores.iloc[-1]["anomaly_score"]

# Append to report data (top 5 unusual)
sorted_anoms = sorted(anomaly_scores.items(), key=lambda x: x[1], reverse=True)
report_data["anomaly_alerts"] = sorted_anoms[:5]

from mod.analysis.regime_hmm import detect_regimes

regimes = []

for ticker in universe[:5]:  # sample few for speed
    df = get_stock_data(ticker, period="3mo")
    if df is None or len(df) < 30:
        continue
    df_regime, model = detect_regimes(df)
    latest = df_regime.iloc[-1]["regime"]
    regimes.append({
        "ticker": ticker,
        "regime": f"State {int(latest)}"
    })

report_data["regime_states"] = regimes

from mod.filters.kalman_filter import apply_kalman_filter

for ticker in universe[:5]:
    df = get_stock_data(ticker, period="3mo")
    if df is None or len(df) < 30:
        continue

    df = apply_kalman_filter(df)
    # Optional: use smoothed price in other analyses (forecast, reversal, etc.)
    latest_smoothed = df.iloc[-1]["kalman_smooth"]
    report_data.setdefault("kalman_smooth", []).append({
        "ticker": ticker,
        "price": round(latest_smoothed, 2)
    })

# Import modules (with proper error handling)
try:
    # Core modules
    from mod.config import ensure_directories_exist
    from mod.config.mailing import load_mailing_list
    
    # Data modules
    from mod.data.fetcher import fetch_symbol_data, load_stock_universe
    from mod.data.multi_asset import generate_multi_asset_report
    
    # Analysis modules
    from mod.analysis.market import (
        calculate_percent_changes,
        find_technical_patterns,
        find_trading_opportunities,
        get_market_summary
    )
    from mod.analysis.dividend import analyze_dividend_history
    
    # Visualization modules
    from mod.visualization.candlestick import generate_candlestick_chart
    from mod.visualization.indicators import generate_enhanced_candlestick_chart
    from mod.visualization.sector import generate_sector_heatmap
    from mod.visualization.macro import generate_macro_chart
    from mod.visualization.currency import generate_forex_chart
    from mod.visualization.comparison import generate_volatility_comparison
    
    # Reporting modules
    from mod.reporting.html_generator import prepare_report_data, render_html_report, save_html_report
    from mod.reporting.email_sender import send_report_email
    
    # Utility modules
    from mod.utils.image_utils import (
        fig_to_png_bytes, 
        add_watermark_to_image, 
        add_copyright_notice,
        save_chart_to_disk
    )
    
    # Security modules
    from subscription_access import (
        generate_subscriber_id,
        generate_access_token,
        generate_report_url
    )
    
    modules_loaded = True
    logger.info("All modules loaded successfully")
except ImportError as e:
    modules_loaded = False
    logger.error(f"Error loading modules: {e}")

class ReportGenerator:
    """
    Class to handle report generation and distribution.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        # Ensure directories exist
        self.ensure_directories()
        
        # Initialize report cache
        self.report_cache = {}
        
        # Load report cache from disk if available
        self.load_cache()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        # Create directories
        directories = [
            'logs',
            'cache',
            'reports',
            'charts',
            'data'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("Directories created")
    
    def load_cache(self):
        """Load report cache from disk."""
        cache_file = 'cache/report_cache.json'
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.report_cache = json.load(f)
                logger.info(f"Loaded {len(self.report_cache)} reports from cache")
            except Exception as e:
                logger.error(f"Error loading report cache: {e}")
                self.report_cache = {}
    
    def save_cache(self):
        """Save report cache to disk."""
        cache_file = 'cache/report_cache.json'
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.report_cache, f)
            logger.info(f"Saved {len(self.report_cache)} reports to cache")
        except Exception as e:
            logger.error(f"Error saving report cache: {e}")
    
    def generate_report(self, tier='Basic', custom_symbols=None):
        """
        Generate a daily market report.
        
        Args:
            tier: Subscription tier to generate report for
            custom_symbols: Optional list of custom symbols to include
            
        Returns:
            dict: Report data including HTML content and images
        """
        logger.info(f"Starting report generation for tier: {tier}")
        start_time = time.time()
        
        try:
            # Check if we need to load the stock universe
            if custom_symbols:
                # Convert to DataFrame if it's a list
                if isinstance(custom_symbols, list):
                    df_universe = pd.DataFrame({'symbol': custom_symbols})
                else:
                    df_universe = custom_symbols
                logger.info(f"Using {len(df_universe)} custom symbols")
            else:
                # Load standard universe
                df_universe = load_stock_universe()
                logger.info(f"Loaded {len(df_universe)} symbols from universe")
            
            # Calculate daily percent changes
            logger.info("Calculating daily percent changes")
            df_universe = calculate_percent_changes(df_universe)
            
            # Find technical patterns
            logger.info("Finding 52-week highs and 200-day MA crossovers")
            fifty_two_week_high, crossover_200d, technical_errors = find_technical_patterns(df_universe)
            
            from mod.forecast.simple_forecast import forecast_trend

            print("Running forecast overlay...")
            forecast_data = forecast_trend(universe)
            report_data["forecast_overlay"] = forecast_data


            # Find trading opportunities (Pro tier only)
            trading_signals = {}
            if tier == 'Pro':
                logger.info("Finding trading opportunities")
                trading_signals = find_trading_opportunities(df_universe)
            
            # Analyze dividends for top stocks
            logger.info("Analyzing dividends for top stocks")
            top_stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
            dividend_analysis = analyze_dividend_history(top_stocks)
            
            # Generate multi-asset report (Pro tier only)
            multi_asset_data = {}
            if tier == 'Pro':
                logger.info("Generating multi-asset report")
                multi_asset_data = generate_multi_asset_report()
            
            # Collect all errors
            all_errors = technical_errors + (trading_signals.get('errors', []) if isinstance(trading_signals, dict) and 'errors' in trading_signals else [])
            
            # Get S&P 500 data and market summary
            logger.info("Getting S&P 500 data")
            market_summary = get_market_summary()
            
            # Generate standard candlestick chart
            logger.info("Generating standard candlestick chart")
            candle_png_bytes = generate_candlestick_chart()
            
            # Generate enhanced chart with reversal indicators
            enhanced_png_bytes = None
            if tier in ['Basic', 'Pro']:
                logger.info("Generating enhanced chart with reversal indicators")
                
                if isinstance(df_universe, pd.DataFrame) and len(df_universe) > 0 and 'symbol' in df_universe.columns:
                    representative_ticker = df_universe['symbol'].iloc[0]
                    stock_data = fetch_symbol_data(representative_ticker, period="3mo", interval="1d")
                    if stock_data is not None and not stock_data.empty:
                        enhanced_fig = generate_enhanced_candlestick_chart(
                            df=stock_data,
                            ticker=representative_ticker,
                            output_dir="charts"
                        )
                        if enhanced_fig:
                            enhanced_png_bytes = fig_to_png_bytes(enhanced_fig)
                
                if enhanced_png_bytes is None:
                    spy_data = fetch_symbol_data("SPY", period="3mo", interval="1d")
                    if spy_data is not None and not spy_data.empty:
                        enhanced_fig = generate_enhanced_candlestick_chart(
                            df=spy_data,
                            ticker="SPY",
                            output_dir="charts"
                        )
                        if enhanced_fig:
                            enhanced_png_bytes = fig_to_png_bytes(enhanced_fig)

            from mod.ml.autoencoder_anomaly import log_anomaly_scores

            log_anomaly_scores(anomaly_scores)


            # Generate sector heatmap
            logger.info("Generating sector heatmap")
            heatmap_png_bytes = generate_sector_heatmap(df_universe)
            
            # Generate macro chart
            logger.info("Generating macro chart")
            macro_png_bytes = generate_macro_chart()
            
            # Generate forex chart (Pro tier only)
            forex_png_bytes = None
            if tier == 'Pro':
                logger.info("Generating forex chart")
                forex_png_bytes = generate_forex_chart()
            
            # Generate volatility comparison (Pro tier only)
            volatility_png_bytes = None
            if tier == 'Pro':
                logger.info("Generating volatility comparison")
                volatility_png_bytes = generate_volatility_comparison(top_stocks)
            
            # Collect all charts
            charts = {
                'candlestick': candle_png_bytes,
                'enhanced': enhanced_png_bytes,
                'heatmap': heatmap_png_bytes,
                'macro': macro_png_bytes
            }
            
            # Add Pro tier charts
            if tier == 'Pro':
                charts.update({
                    'forex': forex_png_bytes,
                    'volatility': volatility_png_bytes
                })
            
            # Prepare technical signals
            technical_signals = {
                'fifty_two_week_high': fifty_two_week_high if isinstance(fifty_two_week_high, list) else
                                     (fifty_two_week_high.to_dict('records') if hasattr(fifty_two_week_high, 'to_dict') else []),
                'crossover_200d': crossover_200d if isinstance(crossover_200d, list) else
                                 (crossover_200d.to_dict('records') if hasattr(crossover_200d, 'to_dict') else [])
            }
            
            # Prepare report data
            logger.info("Preparing report data")
            report_data = prepare_report_data(
                market_summary,
                charts,
                technical_signals,
                trading_signals if tier == 'Pro' else {},
                all_errors
            )
            
            # Add dividend data
            if isinstance(dividend_analysis, dict):
                dividend_data = dividend_analysis
            elif hasattr(dividend_analysis, 'to_dict'):
                dividend_data = dividend_analysis.to_dict('index')
            else:
                dividend_data = {}
            
            report_data.update({'dividend_analysis': dividend_data})
            
            # Add multi-asset data for Pro tier
            if tier == 'Pro' and multi_asset_data:
                report_data.update({
                    'currency_data': multi_asset_data.get('currency', {}),
                    'etf_data': multi_asset_data.get('etfs', {})
                })
            
            # Render HTML report
            logger.info("Rendering HTML template")
            html_output = render_html_report(report_data)
            
            # Generate a unique report ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = f"report_{timestamp}_{tier.lower()}"
            
            # Save report to disk
            report_filename = save_html_report(html_output, f"reports/{report_id}.html")

            # Collect images for email
            images = {
                'candle_chart': candle_png_bytes,
                'enhanced_chart': enhanced_png_bytes,
                'heatmap': heatmap_png_bytes,
                'macro_chart': macro_png_bytes
            }
            
            # Add Pro tier images
            if tier == 'Pro':
                images.update({
                    'forex_chart': forex_png_bytes,
                    'volatility_chart': volatility_png_bytes
                })
            
            # Cache the report
            self.report_cache[report_id] = {
                'timestamp': timestamp,
                'tier': tier,
                'filename': report_filename,
                'html': html_output
            }
            
            # Save cache
            self.save_cache()
            
            # Log completion time
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Report generation completed in {duration:.2f} seconds")
            
            # Return report data
            return {
                'report_id': report_id,
                'timestamp': timestamp,
                'tier': tier,
                'html': html_output,
                'images': images,
                'filename': report_filename
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            traceback.print_exc()
            return None
    
    def get_cached_report(self, report_id):
        """
        Get a report from cache.
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            dict: Report data or None if not found
        """
        return self.report_cache.get(report_id)
    
    def send_report_to_subscribers(self, recipients=None, tier='Basic'):
        """
        Send the latest report to subscribers.
        
        Args:
            recipients: List of recipients or None to load from mailing list
            tier: Subscription tier to send
            
        Returns:
            dict: Results including success count and errors
        """
        logger.info(f"Starting to send {tier} report to subscribers")
        
        # Generate the report if it doesn't exist
        latest_report_id = None
        for report_id, report_data in self.report_cache.items():
            if report_data.get('tier') == tier:
                if not latest_report_id or report_data.get('timestamp', '') > self.report_cache.get(latest_report_id, {}).get('timestamp', ''):
                    latest_report_id = report_id
        
        if not latest_report_id:
            logger.info(f"No cached {tier} report found, generating new one")
            report_data = self.generate_report(tier=tier)
            if not report_data:
                logger.error("Failed to generate report")
                return {'success': 0, 'failed': 0, 'errors': ["Failed to generate report"]}
            
            latest_report_id = report_data['report_id']
        else:
            logger.info(f"Using cached report: {latest_report_id}")
            report_data = self.report_cache[latest_report_id]
        
        # Load recipients if not provided
        if recipients is None:
            recipients = load_mailing_list("mailing_list.txt")
            logger.info(f"Loaded {len(recipients)} recipients from mailing list")
        
        # Send emails
        success_count = 0
        fail_count = 0
        errors = []
        
        for recipient in recipients:
            try:
                # Get recipient email
                if isinstance(recipient, dict):
                    email = recipient.get('email')
                    recipient_tier = recipient.get('tier', 'Basic')
                else:
                    email = recipient
                    recipient_tier = 'Basic'  # Default tier
                
                # Skip recipients with lower tier than the report
                if tier == 'Pro' and recipient_tier != 'Pro':
                    logger.info(f"Skipping {email} (tier: {recipient_tier}) for Pro report")
                    continue
                
                # Get the HTML content
                html_content = report_data.get('html')
                
                # Create watermarked images for this recipient
                watermarked_images = {}
                for img_id, img_bytes in report_data.get('images', {}).items():
                    if img_bytes:
                        # Add watermark if possible
                        # (not implemented for bytes directly, would require converting back to figure)
                        watermarked_images[img_id] = img_bytes
                
                # Generate unique subscriber ID
                subscriber_id = generate_subscriber_id(email, latest_report_id)
                
                # Add subscriber-specific links
                report_url = generate_report_url(email, latest_report_id, recipient_tier)
                
                # Add view in browser link
                view_link = f'<p style="text-align: center;"><a href="{report_url}">View this report in your browser</a></p>'
                html_content = html_content.replace('</body>', f'{view_link}</body>')
                
                # Send email
                subject = f"DailyStonks Market Report - {datetime.now().strftime('%b %d, %Y')}"
                result = send_report_email(html_content, subject=subject, images=watermarked_images, recipients=[email])
                
                if result:
                    success_count += 1
                    logger.info(f"Email sent to {email} successfully")
                else:
                    fail_count += 1
                    errors.append(f"Failed to send email to {email}")
            except Exception as e:
                fail_count += 1
                error_msg = f"Error sending report to {recipient}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Sent report to {success_count} recipients, {fail_count} failed")
        
        return {
            'success': success_count,
            'failed': fail_count,
            'errors': errors
        }
    
    from mod.overlay.dark_pool import detect_dark_pool_signals
    from mod.overlay.sentiment import get_sample_sentiment

    print("Analyzing dark pool signals...")
    dark_signals = detect_dark_pool_signals(universe)
    report_data["dark_pool_alerts"] = dark_signals

    print("Getting market sentiment...")
    report_data["sentiment"] = get_sample_sentiment("SPY")

    def cleanup_old_reports(self, max_age_days=7):
        """
        Clean up old reports from cache and disk.
        
        Args:
            max_age_days: Maximum age of reports to keep
            
        Returns:
            int: Number of reports cleaned up
        """
        logger.info(f"Cleaning up reports older than {max_age_days} days")
        
        # Calculate cutoff time
        cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
        
        # Find reports to delete
        reports_to_delete = []
        for report_id, report_data in self.report_cache.items():
            # Get timestamp
            report_timestamp = report_data.get('timestamp')
            if not report_timestamp:
                continue
            
            # Convert to timestamp
            try:
                if isinstance(report_timestamp, str):
                    # Convert string timestamp to datetime
                    dt = datetime.strptime(report_timestamp, "%Y%m%d_%H%M%S")
                    report_time = dt.timestamp()
                else:
                    report_time = float(report_timestamp)
                
                # Check if older than cutoff
                if report_time < cutoff_time:
                    reports_to_delete.append(report_id)
            except Exception as e:
                logger.error(f"Error parsing timestamp for report {report_id}: {e}")
        
        # Delete reports
        deleted_count = 0
        for report_id in reports_to_delete:
            try:
                # Get filename
                filename = self.report_cache[report_id].get('filename')
                
                # Delete file if exists
                if filename and os.path.exists(filename):
                    os.remove(filename)
                
                # Remove from cache
                del self.report_cache[report_id]
                
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting report {report_id}: {e}")
        
        # Save updated cache
        self.save_cache()
        
        logger.info(f"Cleaned up {deleted_count} old reports")
        
        return deleted_count

# Initialize report generator
report_generator = ReportGenerator()

# Define Celery tasks if enabled
if celery_enabled:
    @celery_app.task
    def generate_daily_report(tier='Basic'):
        """
        Celery task to generate the daily market report.
        
        Args:
            tier: Subscription tier to generate report for
            
        Returns:
            str: Report ID or None if failed
        """
        try:
            report_data = report_generator.generate_report(tier=tier)
            if report_data:
                return report_data['report_id']
            return None
        except Exception as e:
            logger.error(f"Error in generate_daily_report task: {e}")
            return None
    
    @celery_app.task
    def send_report_emails(tier='Basic'):
        """
        Celery task to send report emails to all subscribers.
        
        Args:
            tier: Subscription tier to send
            
        Returns:
            dict: Results including success count and errors
        """
        try:
            return report_generator.send_report_to_subscribers(tier=tier)
        except Exception as e:
            logger.error(f"Error in send_report_emails task: {e}")
            return {'success': 0, 'failed': 0, 'errors': [str(e)]}
    
    @celery_app.task
    def cleanup_old_reports(max_age_days=7):
        """
        Celery task to clean up old reports.
        
        Args:
            max_age_days: Maximum age of reports to keep
            
        Returns:
            int: Number of reports cleaned up
        """
        try:
            return report_generator.cleanup_old_reports(max_age_days=max_age_days)
        except Exception as e:
            logger.error(f"Error in cleanup_old_reports task: {e}")
            return 0

# Health check function
def check_health():
    """
    Check the health of various system components.
    
    Returns:
        dict: Health check results
    """
    health = {
        'status': 'healthy',
        'checks': {
            'filesystem': check_filesystem_health(),
            'data_access': check_data_access(),
            'report_generation': check_report_generation(),
            'email': check_email_service()
        }
    }
    
    # Calculate overall status
    if any(not check for check in health['checks'].values()):
        health['status'] = 'unhealthy'
    
    return health

def check_filesystem_health():
    """
    Check filesystem health.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        # Check if critical directories exist
        directories = ['logs', 'cache', 'reports', 'charts', 'data']
        for directory in directories:
            if not os.path.exists(directory):
                logger.error(f"Directory {directory} does not exist")
                return False
        
        # Check if we can write to them
        for directory in directories:
            test_file = os.path.join(directory, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        
        return True
    except Exception as e:
        logger.error(f"Filesystem health check failed: {e}")
        return False

def check_data_access():
    """
    Check data access.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        # Try to fetch SPY data
        data = fetch_symbol_data("SPY", period="1d")
        if data is None or data.empty:
            logger.error("Failed to fetch SPY data")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Data access health check failed: {e}")
        return False

def check_report_generation():
    """
    Check report generation.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        # Check if we have any cached reports
        if len(report_generator.report_cache) > 0:
            return True
        
        # Try to generate a minimal report
        sample_universe = pd.DataFrame({'symbol': ['SPY']})
        report_data = report_generator.generate_report(tier='Free', custom_symbols=sample_universe)
        
        return report_data is not None
    except Exception as e:
        logger.error(f"Report generation health check failed: {e}")
        return False

def check_email_service():
    """
    Check email service.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        # Check if email settings are configured
        required_env = ['EMAIL_SENDER', 'EMAIL_PASSWORD', 'EMAIL_SMTP', 'EMAIL_PORT']
        for env_var in required_env:
            if not os.environ.get(env_var):
                logger.error(f"Missing environment variable: {env_var}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Email service health check failed: {e}")
        return False

# CLI entrypoint
def main():
    """
    Command-line entry point.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="DailyStonks Market Report Generator")
    parser.add_argument("--generate", action="store_true", help="Generate report")
    parser.add_argument("--send", action="store_true", help="Send report to subscribers")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old reports")
    parser.add_argument("--health", action="store_true", help="Check system health")
    parser.add_argument("--tier", choices=["Free", "Basic", "Pro"], default="Basic", help="Subscription tier")
    parser.add_argument("--days", type=int, default=7, help="Days to keep reports")
    
    args = parser.parse_args()
    
    # Default action is to generate and send
    if not (args.generate or args.send or args.cleanup or args.health):
        args.generate = True
        args.send = True
    
    # Check health if requested
    if args.health:
        health = check_health()
        print(f"System health: {health['status']}")
        for check, status in health['checks'].items():
            print(f"  {check}: {'OK' if status else 'FAIL'}")
        if health['status'] != 'healthy':
            return 1
    
    # Generate report if requested
    if args.generate:
        print(f"Generating {args.tier} report...")
        report_data = report_generator.generate_report(tier=args.tier)
        if report_data:
            print(f"Report generated: {report_data['report_id']}")
            print(f"Saved to: {report_data['filename']}")
        else:
            print("Failed to generate report")
            return 1
    
    # Send report if requested
    if args.send:
        print(f"Sending {args.tier} report to subscribers...")
        results = report_generator.send_report_to_subscribers(tier=args.tier)
        print(f"Sent to {results['success']} subscribers, {results['failed']} failed")
        if results['failed'] > 0:
            print("Errors:")
            for error in results['errors']:
                print(f"  {error}")
    
    # Clean up if requested
    if args.cleanup:
        print(f"Cleaning up reports older than {args.days} days...")
        deleted = report_generator.cleanup_old_reports(max_age_days=args.days)
        print(f"Cleaned up {deleted} reports")
    
    return 0

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Run main function
    exit(main())