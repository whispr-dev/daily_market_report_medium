# DailyStonks 📈

AI-powered market analysis and report system with advanced ML features.

![License](https://img.shields.io/badge/license-MIT%2FCC0_Hybrid-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## Overview

DailyStonks is a complete system for generating and distributing professional stock market analysis reports via email. The system combines traditional technical analysis with cutting-edge machine learning algorithms to deliver actionable insights to subscribers.

### Key Features

- **Tiered Subscription Model** (Free, Basic, Pro)
- **PayPal Integration** for subscription management
- **Beautiful Dark-Mode Reports** with responsive design
- **AI-Powered Analysis** with predictive algorithms
- **Security Features** like watermarking and access controls
- **CLI + Dashboard Tools** for power users

## System Architecture

```
dailystonks/
├── mod/                   # Core Python modules
│   ├── analysis/          # Analysis modules
│   ├── data/              # Data fetching modules
│   ├── reporting/         # Reporting modules
│   ├── utils/             # Utility modules
│   └── visualization/     # Visualization modules
├── templates/             # Email templates
├── static/                # Static web files
├── scripts/               # Operation scripts
└── main_enhanced.py       # Main entry point
```

## ML Features

- **Composite Score Engine** - Weighted ranking system combining multiple signals
- **AI Forecast Overlay** - Short-term price prediction using Ridge regression
- **Reversal Risk Heatmap** - Pattern detection across market sectors
- **Autoencoder Anomaly Detection** - Neural net that flags unusual market behavior
- **Kalman Filter Smoothing** - Probabilistic noise filtering for clean signals
- **Regime Detection via HMM** - Hidden Markov Model for market state classification
- **Bayesian Forecasting** - Trend forecasts with credible intervals
- **CLI + Visual Dashboard** - Command-line tools for visualization and analysis

## Quick Start

### Prerequisites

- Python 3.8+
- Nginx web server
- Redis (for background tasks)
- PayPal Developer Account

### Installation

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

3. **Configure your environment**:
   ```bash
   nano .env
   ```

4. **Start the services**:
   ```bash
   ./deploy.sh all
   ```

5. **Generate a test report**:
   ```bash
   ./test_pro_report.sh
   ```

## Running the System

### Start/Stop Services

```bash
# Start all services
./deploy.sh all

# Stop all services
./stop.sh all

# Check status
./status.sh

# View logs
./logs.sh [service]
```

### Manage Reports

```bash
# Generate a report
./generate_report.sh [tier]

# Send reports to subscribers
./send_report.sh [tier]

# Pro-tier reports specifically
./send_pro_reports.sh
```

## Subscription Tiers

### Free Tier
- Basic market summary
- S&P 500 candlestick chart
- Weekly reports (Friday only)

### Basic Tier ($1c/week)
- Daily reports (Monday-Friday)
- Enhanced charts with indicators
- Sector heatmap
- Technical signals

### Pro Tier ($1c/day)
- All features from lower tiers
- AI-powered insights
- Options market analysis
- Crypto dashboard
- Sentiment analysis
- Advanced ML features

## Security Features

- **Access Tokens** - Time-limited tokens for premium content
- **Image Watermarking** - Subtle subscriber identification
- **Rate Limiting** - Protection against abuse
- **Signature Verification** - PayPal webhook security
- **Unique Subscriber IDs** - Deterministic but unguessable

## Maintenance

```bash
# Backup mailing list
cp mailing_list.txt mailing_list_backup_$(date +%Y%m%d).txt

# Clean old reports
./cleanup_reports.sh 30

# Check system health
./health_check.sh
```

## Command-Line Tools

Access the ML-powered tools:

```bash
# ML dashboard
python -m mod.cli.dashboard

# Top scores report
python -m mod.cli.top_scores --limit 10

# Reversal risk analysis
python -m mod.cli.reversal_risk --index "^GSPC"

# Anomaly detection
python -m mod.cli.anomalies --days 5 --threshold 0.75
```

## Documentation

For complete documentation:

- [System Guide](docs/DailyStonks_Master_Guide.md) - Complete system documentation
- [API Reference](docs/API_Reference.md) - API endpoints and usage
- [ML Features](docs/ML_Features.md) - Detailed ML/AI capabilities

## License

This project uses a hybrid licensing model:
- Code: MIT License
- Content/Documentation: CC0

## Support
