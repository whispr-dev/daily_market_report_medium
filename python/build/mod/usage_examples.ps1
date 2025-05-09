# Generate full report, show top scores, and display all plots
python whispr_report_cli.py --all

# Just email + HTML report
python whispr_report_cli.py --html

# View leaderboard of top tickers
python whispr_report_cli.py --top

# Plot reversal risk trend
python whispr_report_cli.py --risk

# Plot AI forecast slopes
python whispr_report_cli.py --forecast

# Bar plot of composite scores
python whispr_report_cli.py --composite

# Plot average market anomaly trend
python whispr_cli/anomaly_cli.py

# Plot anomaly trend for a single ticker
python whispr_cli/anomaly_cli.py --ticker TSLA

