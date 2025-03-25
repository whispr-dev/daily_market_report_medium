# Automailer: Daily Email with Custom Market Analysis
20250325115224 Tue


This repository automates a [daily] email that includes:
- A custom stock analysis for certain tickers
- 52-week high trackers
- 200-day moving average (SMA) crossovers
- S&P 500 reference data


Originally inspired by [this Medium article](https://medium.com/@phitzi/automating-a-daily-email-with-custom-stock-analysis-with-python-b11eec1ab192).

## Table of Contents
1. [Overview](#overview)
2. [Project Contents Explained](#project-contents-explained)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Scheduling (Optional)](#scheduling-optional)
6. [License](#license)


---

## 1. Overview

**Goal**: Automatically email a customized daily market report. You can tailor the stocks of interest, the email template, and the logic for detecting interesting market events (like 52-week highs or SMA crossovers).

**How It Works**:
i. **`main.py`** reads a CSV file (`stocks_universe.csv`) to gather stock symbols.  
ii. It uses [yfinance](https://github.com/ranaroussi/yfinance) to download historical price data for each ticker.
iii. Each ticker is analyzed for:
   - 52-week highs
   - 200-day SMA crossovers
iv. It also fetches S&P 500 (`^GSPC`) data for context.
v. The results get rendered via a Jinja2 HTML template (`email_template.html`).
vi. **`sendemail.py`** handles SMTP email sending, pulling credentials from environment variables (or a `.env` file using `python-dotenv`).
vii. Finally, an email is generated and sent with the daily summary.


---

## 2. Project Contents Explained
root/ 
 ├── README.md # This README 
 ├── LICENSE # The license file 
 └── env/
     ├── requirements.txt # Python dependencies 
     ├── stocks_universe.csv # CSV of ticker symbols and associated data 
     ├── email_template.html # HTML template for the emailed report 
     ├── main.py # Main script that downloads data, analyzes, and triggers email 
     ├── sendemail.py # Helper script to send the email via SMTP 
     └── run_stonks.bat # (Optional) Windows batch file to run main.py on a schedule


### Files Explained In Detail

i. **`main.py`**  
   - The heart of the project.  
   - Reads in `stocks_universe.csv`, filters relevant tickers, and downloads their market data via yfinance.  
   - Analyzes each stock for 52-week highs and 200-day moving average crossovers.  
   - Fetches S&P 500 data for reference.  
   - Renders an HTML email using `email_template.html` and sends it via `send_email()`.

ii. **`sendemail.py`**  
   - Handles SMTP connection and email-sending logic.  
   - Pulls SMTP credentials and other settings from environment variables or a `.env` file, thanks to `python-dotenv`.  
   - Expects these environment variables:
     - `smtp_user`
     - `SMTP_PASSWORD`
     - `SMTP_SERVER`
     - `SMTP_PORT`
     - `SENDER_EMAIL`
     - `TO_EMAIL`

iii. **`email_template.html`**  
   - A [Jinja2](https://palletsprojects.com/p/jinja/) HTML template.  
   - Renders the S&P 500 stats, the 52-week high table, and the crossover table.  
   - Also displays any errors in a separate section.

iv. **`stocks_universe.csv`**  
   - A CSV listing all your ticker symbols plus additional metadata (CapCategory, sector, shortName, etc.).  
   - `main.py` filters and loops through these tickers for the daily analysis.

v. **`run_stonks.bat`**  
   - A convenience file for Windows.  
   - Can be scheduled via **Task Scheduler** to run `python main.py` automatically each day.  
   - Typical content:
     `bat`
     `@echo off`
     `cd /d "C:\path\to\your\project"` 
     `python main.py`

vi **`LICENSE`**  
   - Indicates the project’s license terms (MIT, Apache, or otherwise).

vii. **`requirements.txt`**  
   - Lists all Python dependencies (e.g., `pandas`, `yfinance`, `jinja2`, `python-dotenv`), so you can `pip install -r requirements.txt` easily.


---

## 3. Installation

i. **Clone this repo** (or download as ZIP and extract).
ii. **Install Python dependencies**:

`pip install -r requirements.txt`
Set up your environment variables (especially if using .env):

### Example .env contents:
`smtp_user=mysmtpuser`
`SMTP_PASSWORD=mysecretpassword`
`SMTP_SERVER=smtp.myserver.com`
`SMTP_PORT=587`
`SENDER_EMAIL=me@example.com`
`TO_EMAIL=recipient@example.com`
`Prepare stocks_universe.csv to include your desired tickers and metadata.`


---

## 4. Usage
To run the script manually:


`python main.py`
This will:

Grab data from Yahoo Finance.

Generate the HTML using Jinja2.

Send the daily email via the SMTP credentials you configured.

You’ll see console output indicating which tickers were processed and whether the email was successful.


---

## 5. Scheduling (Optional)
Windows Task Scheduler
Create a .bat file (run_stonks.bat) with:

`@echo off`
`cd /d "C:\path\to\this\repo"`
`python main.py`

Open Task Scheduler → Create Basic Task → Set daily trigger + point it to run_stonks.bat.

---

Linux/macOS (Cron)
Open crontab:

`crontab -e`
Add an entry to run once a day (say, at 9 AM):

`0 9 * * * /usr/bin/python /path/to/main.py`

Save. Cron will run the script automatically.


---

## 6. License
This project is released under the terms of the LICENSE file in this repository. Please see the license file for details.


---

### Happy stonks scanning! Feel free to open issues or pull requests if you discover improvements or want to share your customizations.

---
