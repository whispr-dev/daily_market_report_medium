# DailyStonks: Technical Details

## Project Statistics

- **Total Files**: 85+
- **Lines of Code**: ~15,000
- **Project Size**: ~8MB (excluding virtual environment)
- **Language Distribution**: 
  - Python: 75%
  - HTML/CSS: 15%
  - Shell Scripts: 5%
  - JSON/Configuration: 5%

## Dependencies

### Python Libraries

| Library               | Version               | Purpose               |
|-------------------|---------------------------|-----------------------|
| Flask             | >=2.0.0                   | Web framework for API endpoints and servers |
| Gunicorn          | >=20.1.0                  | WSGI HTTP server      |
| Pandas            | >=1.3.0                   | Data analysis and manipulation |
| NumPy             | >=1.20.0                  | 0Numerical computing |
| Matplotlib        | >=3.5.0                   | Data visualization and chart generation |
| mplfinance        | >=0.12.9                  | Financial charting |
| yfinance | >=0.1.70 | Yahoo Finance API for market data |
| scikit-learn | >=1.0.0 | Traditional machine learning algorithms |
| TensorFlow | >=2.8.0 | Deep learning (autoencoder, neural networks) |
| PyMC | >=4.0.0 | Bayesian modeling and inference |
| hmmlearn | >=0.2.6 | Hidden Markov Models for regime detection |
| Jinja2 | >=3.0.0 | Template engine for email reports |
| Premailer | >=3.10.0 | CSS inlining for emails |
| Celery | >=5.2.0 | Distributed task queue for background processing |
| Redis | >=4.0.0 | Message broker and cache |
| requests | >=2.27.0 | HTTP library for API calls |

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+ (3.10 recommended)
- **Nginx**: 1.18+
- **Redis**: 6.0+
- **Disk Space**: 
  - 1GB minimum
  - 10GB+ recommended for log storage and report caching
- **RAM**:
  - 2GB minimum
  - 4GB+ recommended for ML model operations
- **CPU**:
  - 2 cores minimum
  - 4+ cores recommended for faster report generation

## File Structure Details

```
dailystonks/
├── mod/                              # 45+ files
│   ├── analysis/                     # 12+ files
│   │   ├── __init__.py
│   │   ├── dividend.py
│   │   ├── macro.py
│   │   ├── market.py
│   │   ├── technical.py
│   │   └── ml/                       # 6+ files
│   │       ├── __init__.py
│   │       ├── autoencoder.py
│   │       ├── bayesian.py
│   │       ├── composite_score.py
│   │       ├── hmm.py
│   │       └── kalman.py
│   ├── data/                         # 5+ files
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   ├── enhanced.py
│   │   └── multi_asset.py
│   ├── reporting/                    # 5+ files
│   │   ├── __init__.py
│   │   ├── html_generator.py
│   │   ├── email_sender.py
│   │   └── mailing.py
│   ├── utils/                        # 8+ files
│   │   ├── __init__.py
│   │   ├── data_utils.py
│   │   ├── image_utils.py
│   │   └── template_filters.py
│   ├── visualization/                # 10+ files
│   │   ├── __init__.py
│   │   ├── candlestick.py
│   │   ├── indicators.py
│   │   ├── sector.py
│   │   ├── macro.py
│   │   ├── currency.py
│   │   └── comparison.py
│   └── cli/                          # 5+ files
│       ├── __init__.py
│       ├── dashboard.py
│       ├── top_scores.py
│       ├── reversal_risk.py
│       └── anomalies.py
├── templates/                        # 10+ files
│   ├── email_template.html
│   ├── pro_email_template.html
│   ├── welcome_email.html
│   └── unsubscribe_result.html
├── static/                           # 5+ files
│   ├── css/
│   ├── js/
│   └── images/
├── scripts/                          # 12+ files
│   ├── deploy.sh
│   ├── stop.sh
│   ├── status.sh
│   ├── logs.sh
│   ├── startup.sh
│   ├── generate_report.sh
│   ├── send_report.sh
│   ├── send_pro_reports.sh
│   ├── cleanup_reports.sh
│   └── health_check.sh
├── docs/                             # 3+ files
│   ├── DailyStonks_Master_Guide.md
│   ├── API_Reference.md
│   └── ML_Features.md
└── core files                        # 10+ files
    ├── main_enhanced.py
    ├── paypal_webhook.py
    ├── unsubscribe_server.py
    ├── main_app.py
    ├── pro_features.py
    ├── subscription_access.py
    ├── gunicorn_config.py
    ├── template_filters.py
    ├── .env.example
    └── requirements.txt
```

## Memory Usage

- **Base System**: ~200MB
- **Email Generation**: 
  - Free tier: ~100MB additional
  - Basic tier: ~300MB additional
  - Pro tier: ~500-800MB additional
- **ML Models**:
  - Autoencoder: ~150MB per model
  - HMM: ~50MB per model
  - Bayesian models: ~100MB during sampling

## Network Requirements

- **Outbound**: 
  - yfinance API: ~5MB per full report generation
  - SMTP (email): ~1-5MB per email depending on tier
  - PayPal API: Minimal (<100KB per webhook)
- **Inbound**:
  - Webhook endpoints: Minimal (<100KB per request)
  - Web interface: ~1-5MB per session

## Performance Metrics

- **Report Generation Time**:
  - Free tier: 10-15 seconds
  - Basic tier: 30-60 seconds
  - Pro tier: 2-5 minutes
- **Email Sending Rate**: 
  - 10 emails per minute (configurable)
- **API Response Time**:
  - Health check: <100ms
  - Report metadata: <500ms
  - Report generation request: <1s (starts async job)

## Version History

### v1.0.0 (Initial Release)
- Basic market data fetching
- Simple candlestick charts
- Basic email sending
- Single-tier reports

### v1.1.0
- Added subscription management
- Implemented watermarking
- Created unsubscribe functionality
- Added welcome emails

### v1.5.0
- Implemented tiered subscription model
- Enhanced visualization for each tier
- Added security features
- Improved email templates

### v2.0.0 (Major Release)
- Complete system architecture redesign
- Background task processing with Celery
- Web application for report viewing
- PayPal webhook integration
- Enhanced security with access tokens

### v2.5.0
- Added crypto market analysis
- Improved chart generation
- Enhanced technical indicators
- Added sentiment analysis

### v3.0.0 (Current Release)
- Added ML/AI capabilities
- Implemented autoencoder anomaly detection
- Added Bayesian forecasting
- Developed regime detection with HMM
- Created CLI tools and dashboard
- Added Kalman filter smoothing

## Database Schema

DailyStonks uses file-based storage rather than a traditional database:

- **mailing_list.txt**: Simple text file with one email per line
- **pro_subscribers.json**: JSON file with subscriber details:
  ```json
  [
    {
      "email": "subscriber@example.com",
      "subscription_id": "sub_12345",
      "tier": "Pro",
      "subscription_date": "2024-05-01",
      "payment_status": "active"
    }
  ]
  ```
- **subscription_log.csv**: CSV file with subscription events:
  ```
  timestamp,email,subscription_id,tier,ip
  ```
- **unsubscribe_log.csv**: CSV file with unsubscribe events:
  ```
  timestamp,email
  ```

## Caching Strategy

- **Report Cache**: 
  - Location: `cache/report_cache.json`
  - Policy: LRU (Least Recently Used)
  - Max size: 100 reports
  - Max age: 7 days (configurable)

- **Chart Cache**:
  - Location: `charts/`
  - Policy: Time-based expiration
  - Max age: 24 hours

- **Data Cache**:
  - In-memory caching of market data
  - TTL: 15 minutes for intraday, 24 hours for daily data

## ML Model Details

### Autoencoder Anomaly Detection
- **Architecture**: 3-layer encoder/decoder (Input → 64 → 32 → 16 → 32 → 64 → Output)
- **Training Time**: ~10 minutes per model
- **Batch Size**: 32
- **Epochs**: 100
- **Learning Rate**: 0.001
- **Activation**: ReLU, Sigmoid (output layer)
- **Loss Function**: Mean Squared Error

### Hidden Markov Model
- **States**: 3 (default, configurable)
- **Features**: Returns, Volatility
- **Covariance Type**: Full
- **Training Algorithm**: Baum-Welch
- **Convergence Tolerance**: 0.01
- **Max Iterations**: 100

### Bayesian Forecasting
- **Model**: Bayesian Linear Regression
- **Prior**: Normal (mean=0, sd=1)
- **Sampling**: NUTS (No U-Turn Sampler)
- **Chains**: 4
- **Samples**: 1000
- **Warmup**: 500
- **Target**: 5-day return

### Kalman Filter
- **State Dimension**: 2 (position, velocity)
- **Measurement Dimension**: 1 (price)
- **Process Noise**: Configurable
- **Measurement Noise**: Configurable

## API Rate Limits

- **Report Generation**: 10 per hour per user
- **Report Viewing**: 100 per hour per user
- **Health Check**: 600 per hour per user

## Security Implementation Details

- **Access Tokens**: 
  - HMAC-SHA256 signature
  - 7-day expiration (configurable)
  - Contains: email, subscriber_id, tier, expiry

- **Watermarking**:
  - Adds hashed email ID to charts
  - Opacity: 10%
  - Position: Center, rotated 45°
  - Font size: Relative to chart dimensions

- **Rate Limiting**: 
  - Redis-based token bucket algorithm
  - Per-email and per-IP limits
  - Configurable burst and sustain rates

- **PayPal Verification**:
  - Webhook ID verification
  - Signature validation against PayPal API
  - Request source IP validation

## Backup Strategy

- **Mailing List**: Daily backup with timestamp
- **Reports**: Weekly cleanup of old reports
- **Logs**: Monthly rotation and compression
- **Configuration**: Manual backup after changes

## Monitoring

- **System Health**: 
  - Filesystem checks
  - Data access checks
  - Email service checks
  - Memory/CPU monitoring
  - Disk space alerts

- **Service Status**:
  - Process uptime monitoring
  - Log monitoring for errors
  - Network connection checks

## Design Patterns Used

- **Factory Pattern**: For report generation
- **Strategy Pattern**: For ML algorithm selection
- **Decorator Pattern**: For access control middleware
- **Observer Pattern**: For event notifications
- **Singleton Pattern**: For configuration management

## Testing Coverage

- **Unit Tests**: ~65% coverage
- **Integration Tests**: ~40% coverage
- **End-to-End Tests**: Basic smoke tests for main flows

## Development Environment

- **IDE**: VSCode recommended with Python extension
- **Linting**: flake8, black
- **Virtual Environment**: venv
- **Version Control**: Git
- **CI/CD**: Basic GitHub Actions for testing