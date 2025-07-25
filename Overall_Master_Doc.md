# DailyStonks: Complete System Guide

## 🚀 System Overview

DailyStonks is an AI-powered market analysis system that generates and distributes professional stock market reports via email. The system includes:

- **Data Collection**: Fetches market data, crypto info, and macroeconomic indicators
- **Analysis Engine**: Performs technical, sentiment, and ML/AI-powered analysis
- **Visualization System**: Creates beautiful charts and visual indicators
- **Email Distribution**: Sends reports to subscribers based on their tier
- **Subscription Management**: Handles PayPal subscriptions, upgrades, and unsubscribes
- **Security Features**: Protects premium content with watermarking and access controls

## ⚙️ System Architecture

```
DailyStonks/
├── mod/                   # Core Python modules
│   ├── analysis/          # Analysis modules (technical, market, etc.)
│   ├── data/              # Data fetching modules
│   ├── reporting/         # Reporting modules
│   ├── utils/             # Utility modules
│   └── visualization/     # Visualization modules
├── templates/             # Email and web templates
├── static/                # Static web files
├── logs/                  # Log files
├── cache/                 # Cached reports
├── reports/               # Generated reports
├── charts/                # Generated charts
├── data/                  # Data files
├── main_enhanced.py       # Main report generation script
├── paypal_webhook.py      # PayPal webhook handler
├── unsubscribe_server.py  # Unsubscribe server
├── main_app.py            # Main web application
├── pro_features.py        # Pro-tier features module
├── template_filters.py    # Jinja2 template filters
│
├── setup_pro_features.sh  # Setup script for Pro features
├── send_pro_reports.sh    # Script to send Pro reports
├── deploy.sh              # Deployment script
├── stop.sh                # Script to stop services
├── status.sh              # Script to check service status
└── logs.sh                # Script to view logs
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Nginx web server
- Redis (for background tasks)
- PayPal Developer Account (for subscriptions)

### Quick Start Setup

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/dailystonks.git
   cd dailystonks
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup_pro_features.sh
   ./setup_pro_features.sh
   ```

3. **Edit the `.env` file** with your credentials:
   ```bash
   nano .env
   ```
   
   Fill in:
   - Email configuration (SMTP server, credentials)
   - PayPal API keys
   - Security tokens
   - Server URL

4. **Test the system**:
   ```bash
   ./test_pro_report.sh
   ```

5. **Start the servers**:
   ```bash
   ./deploy.sh all
   ```

## 📊 Feature Tiers

The system offers three subscription tiers:

### Free Tier
- Basic market summary
- S&P 500 candlestick chart
- Weekly reports (Friday only)

### Basic Tier ($1c/week)
- Daily reports (Monday-Friday)
- Enhanced candlestick charts
- Sector heatmap
- Technical signals (52-week highs, MA crossovers)
- Macro trends chart

### Pro Tier ($1c/day)
- All Basic tier features
- AI-powered insights and predictions
- Options market analysis
- Volume profile analysis
- Asset correlation matrix
- Cryptocurrency dashboard
- Sentiment analysis
- Buy/sell signals
- Advanced ML features (see ML Features section)

## 🤖 ML/AI Features

### Composite Score Engine
- **What it is**: Weighted ranking system that combines multiple signals into one actionable score
- **How it works**: Blends signals with adjustable priority (40% ML, 20% trend, 20% reversal, 20% confidence)
- **Use case**: Rank stocks by total edge; find high-confidence setups or newsletter picks

### AI Forecast Overlay
- **What it is**: Directional short-term forecast (5-day slope) using Ridge regression
- **How it works**: Trains per ticker on recent data, predicts future trend vector (+/-%)
- **Use case**: Predict price action before earnings, exits, or re-entries

### Reversal Risk Heatmap
- **What it is**: Detects potential tops, bottoms, or neutral patterns across tickers
- **How it works**: Uses pattern detection logic (candles, momentum) to classify risk tier
- **Use case**: Portfolio risk checks; high-risk clusters suggest hedging

### Autoencoder Anomaly Detection
- **What it is**: Neural net that flags unusual market behavior
- **How it works**: An autoencoder compresses and reconstructs past returns/volatility/volume
- **Use case**: Spot stealth breakouts, liquidity shocks, or pre-news moves

### Kalman Filter Smoothing
- **What it is**: Probabilistic signal smoother that filters out noise while preserving trend
- **How it works**: Applies Kalman filter to close prices before ML processing
- **Use case**: Clean signal generation, avoiding fakeouts and whipsaws

### Regime Detection via HMM
- **What it is**: Hidden Markov Model that classifies market states
- **How it works**: Learns latent states and transitions from historical price data
- **Use case**: Dynamic strategy switching based on detected market regime

### Bayesian Forecasting
- **What it is**: Probabilistic trend forecast with credible intervals
- **How it works**: Fits Bayesian linear model to recent data and samples 1,000+ futures
- **Use case**: Confidence-aware decisions with probability ranges

### CLI + Visual Dashboard
- **What it is**: Command-line tools for visualization and analysis
- **Use case**: Fast diagnostics, strategy reviews, and embedded terminal workflows

## 🚀 Deployment

### Starting Services

To start all services:
```bash
./deploy.sh all
```

To start individual services:
```bash
./deploy.sh paypal     # Start PayPal webhook server
./deploy.sh unsubscribe # Start unsubscribe server
./deploy.sh main       # Start main application
./deploy.sh celery     # Start background tasks
./deploy.sh nginx      # Configure and reload nginx
```

### Stopping Services

To stop all services:
```bash
./stop.sh all
```

To stop individual services:
```bash
./stop.sh paypal       # Stop PayPal webhook server
./stop.sh unsubscribe  # Stop unsubscribe server
./stop.sh main         # Stop main application
./stop.sh celery       # Stop background tasks
```

### Checking Status

To check the status of all services:
```bash
./status.sh
```

### Viewing Logs

To view logs for a service:
```bash
./logs.sh paypal       # View PayPal webhook server logs
./logs.sh unsubscribe  # View unsubscribe server logs
./logs.sh main         # View main application logs
./logs.sh nginx        # View nginx logs
./logs.sh celery       # View Celery logs
```

## 📧 Managing Reports

### Generating Reports

To manually generate a report:
```bash
./generate_report.sh [tier]  # Generate report for specified tier (Free, Basic, Pro)
```

### Sending Reports

To manually send reports to subscribers:
```bash
./send_report.sh [tier]  # Send reports for specified tier (Free, Basic, Pro)
```

For Pro-tier reports specifically:
```bash
./send_pro_reports.sh
```

### Testing Reports

To test report generation without sending emails:
```bash
./test_pro_report.sh
```

### Cleaning Up Old Reports

To clean up old reports:
```bash
./cleanup_reports.sh [days]  # Clean reports older than specified days (default: 7)
```

## 🔐 Security Features

DailyStonks implements several security features to protect premium content:

1. **Access Tokens** - Secure, time-limited tokens for accessing premium content
2. **Image Watermarking** - Subtle watermarks on charts that identify the subscriber
3. **Rate Limiting** - Email sending system has rate limiting to prevent abuse
4. **Signature Verification** - PayPal webhooks are verified using their signature system
5. **Subscriber IDs** - Unique, deterministic IDs for subscribers that can't be guessed

## 📊 Subscription Management

### PayPal Integration

1. Create a PayPal Developer account
2. Set up a webhook in the PayPal Developer Dashboard
3. Configure subscription plans in PayPal
4. Update the `.env` file with your PayPal credentials

### Mailing List Management

- Subscribers are stored in `mailing_list.txt`
- Pro subscribers have additional data in `pro_subscribers.json`
- Unsubscribe requests are logged in `unsubscribe_log.csv`

### Unsubscribe Handling

Unsubscribe tokens are generated for each subscriber and included in emails. When a subscriber clicks the unsubscribe link, the unsubscribe server verifies the token and removes the email from the mailing list.

## 🧠 Advanced ML Configuration

### Configuring Composite Score Engine

Edit `ml_config.json` to adjust signal weights:
```json
{
  "composite_score": {
    "weights": {
      "ml_signal": 0.4,
      "trend_score": 0.2,
      "reversal_score": 0.2,
      "confidence": 0.2
    }
  }
}
```

### Training Autoencoder Model

To train the anomaly detection model on fresh data:
```bash
python -m mod.analysis.ml.train_autoencoder --days 120 --tickers "SPY,QQQ,AAPL,MSFT"
```

### Adjusting Regime Detection

To adjust HMM parameters for regime detection:
```bash
python -m mod.analysis.ml.hmm_tuning --states 3 --lookback 365 --index "^GSPC"
```

### Running Bayesian Forecasts

To run Bayesian forecasts for specific tickers:
```bash
python -m mod.analysis.ml.bayesian_forecast --tickers "AAPL,MSFT,NVDA" --days_ahead 5 --samples 1000
```

## 🔧 Maintenance

### Regular Tasks

1. **Backup mailing list**:
   ```bash
   cp mailing_list.txt mailing_list_backup_$(date +%Y%m%d).txt
   ```

2. **Clean up old reports**:
   ```bash
   ./cleanup_reports.sh 30  # Keep reports for 30 days
   ```

3. **Check system health**:
   ```bash
   ./health_check.sh
   ```

4. **Monitor disk space**:
   ```bash
   df -h
   ```

5. **Rotate logs**:
   ```bash
   find logs -name "*.log" -size +100M -exec gzip {} \;
   ```

### Upgrading

1. Stop all services:
   ```bash
   ./stop.sh all
   ```

2. Backup your files:
   ```bash
   tar -czvf dailystonks_backup_$(date +%Y%m%d).tar.gz *
   ```

3. Pull the latest changes:
   ```bash
   git pull
   ```

4. Start all services:
   ```bash
   ./deploy.sh all
   ```

## 📱 API Access

The system provides API endpoints for programmatic access:

### Authentication

All API requests require an access token:
```
GET /api/report/123?token=YOUR_ACCESS_TOKEN
```

### Endpoints

- `GET /api/reports` - List available reports
- `GET /api/report/{report_id}` - Get a specific report
- `POST /api/generate` - Generate a new report
- `GET /health` - Check system health

## 📄 Environment Variables

The `.env` file contains the following environment variables:

### Email Configuration
- `EMAIL_SENDER` - Email sender address
- `EMAIL_PASSWORD` - Email sender password
- `EMAIL_SMTP` - SMTP server address
- `EMAIL_PORT` - SMTP server port
- `EMAIL_RATE_LIMIT` - Maximum emails per period
- `EMAIL_RATE_PERIOD` - Rate limit period in seconds

### PayPal Configuration
- `PAYPAL_WEBHOOK_ID` - PayPal webhook ID
- `PAYPAL_CLIENT_ID` - PayPal client ID
- `PAYPAL_CLIENT_SECRET` - PayPal client secret
- `PAYPAL_API_URL` - PayPal API URL

### Security
- `SECRET_KEY` - Secret key for tokens
- `SECRET_SALT` - Salt for subscriber IDs
- `ACCESS_TOKEN_SECRET` - Secret for access tokens

### Server Configuration
- `BASE_URL` - Base URL for the application
- `GUNICORN_BIND` - Gunicorn bind address
- `GUNICORN_WORKERS` - Number of Gunicorn workers
- `GUNICORN_LOG_LEVEL` - Gunicorn log level
- `GUNICORN_ERROR_LOG` - Gunicorn error log path
- `GUNICORN_ACCESS_LOG` - Gunicorn access log path

### Background Tasks
- `CELERY_BROKER_URL` - Celery broker URL
- `CELERY_RESULT_BACKEND` - Celery result backend URL

## 📦 Dependencies

### Python Dependencies
- Flask - Web framework
- Gunicorn - WSGI HTTP server
- Pandas - Data analysis library
- NumPy - Numerical computing library
- Matplotlib - Plotting library
- mplfinance - Financial plotting library
- yfinance - Yahoo Finance API
- Premailer - CSS inlining for emails
- Celery - Distributed task queue
- Redis - Message broker for Celery
- scikit-learn - Machine learning library
- TensorFlow - Deep learning library
- PyMC - Bayesian modeling library

### System Dependencies
- Python 3.8+
- Nginx
- Redis

## 🔍 Troubleshooting

### Common Issues

1. **Services not starting**
   - Check logs for errors: `./logs.sh [service]`
   - Verify environment variables in `.env`
   - Ensure ports are not already in use

2. **PayPal webhooks not working**
   - Verify webhook URL in PayPal Developer Dashboard
   - Check PayPal credentials in `.env`
   - Ensure webhook server is running

3. **Emails not sending**
   - Check email credentials in `.env`
   - Verify mailing list contains valid emails
   - Check rate limits with your email provider

4. **Report generation failing**
   - Check data fetching errors in logs
   - Ensure network connectivity for fetching market data
   - Verify dependencies are installed correctly

5. **ML models failing**
   - Check if model files exist in `data/models/`
   - Ensure TensorFlow is installed correctly
   - Try retraining models with fresh data

### Log Locations

- **PayPal Webhook Server**: `logs/gunicorn/paypal_*.log`
- **Unsubscribe Server**: `logs/gunicorn/unsubscribe_*.log`
- **Main Application**: `logs/gunicorn/main_*.log`
- **Celery**: `logs/celery_*.log`
- **Nginx**: `/var/log/nginx/dailystonks.*.log`
- **ML Components**: `logs/ml_*.log`

## 🔮 Command-Line Tools

### ML Dashboard

Access the ML visualization dashboard:
```bash
python -m mod.cli.dashboard
```

### Top Scores Report

View top-ranked stocks by composite score:
```bash
python -m mod.cli.top_scores --limit 10
```

### Reversal Risk Analysis

Generate a reversal risk heatmap:
```bash
python -m mod.cli.reversal_risk --index "^GSPC"
```

### Anomaly Detection Report

Check for recent market anomalies:
```bash
python -m mod.cli.anomalies --days 5 --threshold 0.75
```

## ⚠️ Limitations & Known Issues

1. **Data Sources**: System relies on yfinance which may have rate limits and occasionally returns incomplete data
2. **ML Models**: Models require periodic retraining to maintain accuracy
3. **Email Deliverability**: High volume sending may trigger spam filters
4. **Chart Generation**: Creating many charts simultaneously can be memory-intensive

## 📚 Resources

- [yfinance API Documentation](https://pypi.org/project/yfinance/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [PyMC Documentation](https://www.pymc.io/welcome.html)

## 📞 Support

For support, please contact support@whispr.dev.