from flask import Flask, request, jsonify, render_template
import os
import csv
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, template_folder="templates")

MAILING_LIST = "mailing_list.txt"
SUB_LOG = "subscription_log.csv"
PENDING_CACHE = "pending_subscriptions.json"

@app.route("/paypal/cache-subscription", methods=["POST"])
def cache_subscription():
    # (unchanged logic)

# Prefer user-captured email
email = resource.get("subscriber", {}).get("email_address", "").lower()
subscription_id = resource.get("id")

# Try cache override
if os.path.exists(PENDING_CACHE):
    with open(PENDING_CACHE, "r") as f:
        pending = json.load(f)
        if subscription_id in pending:
            email = pending[subscription_id]

def cache_subscription():
    try:
        data = request.get_json()
        sid = data.get("subscription_id")
        email = data.get("email")

        if not sid or not email:
            return {"error": "missing info"}, 400

        # Load or init cache
        if os.path.exists(PENDING_CACHE):
            with open(PENDING_CACHE, "r") as f:
                pending = json.load(f)
        else:
            pending = {}

        pending[sid] = email

        with open(PENDING_CACHE, "w") as f:
            json.dump(pending, f)

        return {"status": "cached"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def send_welcome_email(recipient):
    sender = os.environ.get('EMAIL_SENDER')
    password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('EMAIL_SMTP')
    smtp_port = int(os.environ.get('EMAIL_PORT', 587))

    subject = "Welcome to the DailyStonks Market Analyisis Email"

    html_content = render_template("welcome_email.html", email=recipient)

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    text_fallback = f"""Hi {recipient},

You're now subscribed to the DailyStonks Subscrtiption Email.

To unsubscribe: https://whispr.dev/unsubscribe?email={recipient}
"""

    msg.attach(MIMEText(text_fallback, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"HTML welcome email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

def paypal_webhook():
    event = request.get_json()

    event_type = event.get("event_type", "")
    resource = event.get("resource", {})
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow().isoformat()

    if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        email = resource.get("subscriber", {}).get("email_address", "").lower()

        # Log and add to list
        if email:
            try:
                with open(MAILING_LIST, "r") as f:
                    lines = [line.strip().lower() for line in f if line.strip()]
            except FileNotFoundError:
                lines = []

            if email not in lines:
                with open(MAILING_LIST, "a") as f:
                    f.write(email + "\n")

            with open(SUB_LOG, "a", newline="") as log:
                writer = csv.writer(log)
                writer.writerow([timestamp, email, resource.get("id"), ip])

            return jsonify({"status": "added"}), 200

# send_welcome_email(email)

    return jsonify({"status": "ignored"}), 200

plan_id = resource.get("plan_id")
if plan_id == "P-PRO001":
    tier = "Pro"
elif plan_id == "P-BASIC001":
    tier = "Basic"
else:
    tier = "Unknown"

@app.route("/paypal/webhook", methods=["POST"])
def paypal_webhook():
    event = request.get_json()
    event_type = event.get("event_type", "")
    resource = event.get("resource", {})
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow().isoformat()

    if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        email = resource.get("subscriber", {}).get("email_address", "").lower()
        subscription_id = resource.get("id")

        # Try override from cached email
        if os.path.exists(PENDING_CACHE):
            with open(PENDING_CACHE, "r") as f:
                pending = json.load(f)
                if subscription_id in pending:
                    email = pending[subscription_id]

        if email:
            try:
                with open(MAILING_LIST, "r") as f:
                    lines = [line.strip().lower() for line in f if line.strip()]
            except FileNotFoundError:
                lines = []

            if email not in lines:
                with open(MAILING_LIST, "a") as f:
                    f.write(email + "\n")

            with open(SUB_LOG, "a", newline='') as log:
                writer = csv.writer(log)
                writer.writerow([timestamp, email, subscription_id, ip])

            send_welcome_email(email)

            return jsonify({"status": "added"}), 200

    return jsonify({"status": "ignored"}), 200
