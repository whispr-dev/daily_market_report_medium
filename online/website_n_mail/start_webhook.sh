
#!/bin/bash
set -e

cd ~/stonksenv || { echo "Venv not found"; exit 1; }

source bin/activate

echo "[✓] Starting PayPal webhook server on port 8080..."
cd ~/  # assuming paypal_webhook.py is in home
python paypal_webhook.py >> webhook.log 2>&1 &
echo "[✔] Running in background, logging to webhook.log"
