dailystonks/
├── mod/
│   ├── __init__.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── dividend.py
│   │   ├── macro.py
│   │   ├── market.py
│   │   └── technical.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   └── multi_asset.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── email_sender.py
│   │   └── html_generator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_utils.py
│   │   └── image_utils.py
│   └── visualization/
│       ├── __init__.py
│       ├── candlestick.py
│       ├── comparison.py
│       ├── currency.py
│       ├── indicators.py
│       ├── macro.py
│       └── sector.py
├── templates/
│   ├── email_template.html
│   └── welcome_email.html
├── static/
│   └── logo.png
├── main.py
├── paypal_webhook.py
└── gunicorn_config.py