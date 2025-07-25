from flask import Flask, request, jsonify, render_template
import os
import csv
import json
import hmac
import hashlib
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

app = Flask(__name__, template_folder="templates")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paypal_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAILING_LIST = "mailing_list.txt"
SUB_LOG = "subscription_log.csv"
PENDING_CACHE = "pending_subscriptions.json"
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID')
PAYPAL_API_URL = os.environ.get('PAYPAL_API_URL', 'https://api-m.paypal.com') 

def verify_paypal_signature(headers, request_body):
    """
    Verify the PayPal webhook signature to ensure the request is authentic.
    
    Args:
        headers: HTTP headers from the request
        request_body: Raw request body
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        auth_algo = headers.get('PAYPAL-AUTH-ALGO')
        cert_url = headers.get('PAYPAL-CERT-URL')
        transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
        transmission_sig = headers.get('PAYPAL-TRANSMISSION-SIG')
        transmission_time = headers.get('PAYPAL-TRANSMISSION-TIME')
        
        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time, PAYPAL_WEBHOOK_ID]):
            logger.error("Missing required PayPal verification headers")
            return False
        
        # Prepare verification request
        verification_data = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": PAYPAL_WEBHOOK_ID,
            "webhook_event": json.loads(request_body)
        }
        
        # Make API call to PayPal to verify signature
        paypal_auth = get_paypal_auth_token()
        if not paypal_auth:
            logger.error("Failed to get PayPal auth token")
            return False
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {paypal_auth}"
        }
        
        response = requests.post(
            f"{PAYPAL_API_URL}/v1/notifications/verify-webhook-signature",
            headers=headers,
            json=verification_data
        )
        
        if response.status_code == 200:
            verification_status = response.json().get("verification_status")
            if verification_status == "SUCCESS":
                return True
        
        logger.error(f"PayPal signature verification failed: {response.text}")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying PayPal signature: {e}")
        return False

def get_paypal_auth_token():
    """
    Get a PayPal OAuth token for API requests.
    
    Returns:
        str: OAuth token or None if failed
    """
    try:
        client_id = os.environ.get('PAYPAL_CLIENT_ID')
        client_secret = os.environ.get('PAYPAL_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("Missing PayPal API credentials")
            return None
        
        auth = (client_id, client_secret)
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            f"{PAYPAL_API_URL}/v1/oauth2/token",
            auth=auth,
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
            
        logger.error(f"Failed to get PayPal auth token: {response.text}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting PayPal auth token: {e}")
        return None

def generate_subscriber_id(email, subscription_id):
    """
    Generate a unique but deterministic subscriber ID.
    
    Args:
        email: Subscriber's email
        subscription_id: PayPal subscription ID
        
    Returns:
        str: Unique subscriber ID
    """
    secret_salt = os.environ.get('SECRET_SALT', 'dailystonks-secret-salt')
    unique_input = f"{email}:{subscription_id}:{secret_salt}"
    return hashlib.sha256(unique_input.encode()).hexdigest()[:16]

def generate_unsubscribe_token(email):
    """
    Generate a secure unsubscribe token.
    
    Args:
        email: Subscriber's email
        
    Returns:
        str: Secure unsubscribe token
    """
    secret_key = os.environ.get('SECRET_KEY', 'dailystonks-secret-key')
    timestamp = int(datetime.utcnow().timestamp())
    payload = f"{email}:{timestamp}"
    token = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
    return f"{token}:{timestamp}"

@app.route("/paypal/cache-subscription", methods=["POST"])
def cache_subscription():
    """
    Cache subscription information before webhook is received.
    """
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
        logger.error(f"Error caching subscription: {e}")
        return {"error": str(e)}, 500

def send_welcome_email(recipient, tier="Basic"):
    """
    Send welcome email to new subscriber.
    
    Args:
        recipient: Email address of recipient
        tier: Subscription tier (Basic, Pro, etc.)
    """
    try:
        sender = os.environ.get('EMAIL_SENDER')
        password = os.environ.get('EMAIL_PASSWORD')
        smtp_server = os.environ.get('EMAIL_SMTP')
        smtp_port = int(os.environ.get('EMAIL_PORT', 587))

        if not all([sender, password, smtp_server, recipient]):
            logger.error("Missing email configuration")
            return False

        subject = "Welcome to DailyStonks Market Analysis Email"

        # Generate unsubscribe token
        unsubscribe_token = generate_unsubscribe_token(recipient)
        
        # Generate subscriber ID
        subscriber_id = generate_subscriber_id(recipient, "welcome")

        html_content = render_template(
            "welcome_email.html", 
            email=recipient, 
            tier=tier,
            subscriber_id=subscriber_id,
            unsubscribe_token=unsubscribe_token
        )

        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg['List-Unsubscribe'] = f"<https://whispr.dev/unsubscribe?email={recipient}&token={unsubscribe_token}>"

        text_fallback = f"""Hi {recipient},

You're now subscribed to the DailyStonks {tier} Subscription Email.

To unsubscribe: https://whispr.dev/unsubscribe?email={recipient}&token={unsubscribe_token}
"""

        msg.attach(MIMEText(text_fallback, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        
        logger.info(f"Welcome email sent to {recipient} (Tier: {tier})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return False

@app.route("/paypal/webhook", methods=["POST"])
def paypal_webhook():
    """
    Handle PayPal subscription webhooks.
    """
    # Get request information
    request_body = request.get_data(as_text=True)
    event = json.loads(request_body)
    event_type = event.get("event_type", "")
    resource = event.get("resource", {})
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow().isoformat()

    logger.info(f"PayPal webhook received: {event_type}")

    # Verify PayPal signature
    if not verify_paypal_signature(request.headers, request_body):
        logger.error("Invalid PayPal signature")
        return jsonify({"status": "error", "message": "Invalid signature"}), 401

    if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        # Get subscriber email
        email = resource.get("subscriber", {}).get("email_address", "").lower()
        subscription_id = resource.get("id")
        plan_id = resource.get("plan_id")
        
        # Set tier based on plan ID
        if plan_id == "P-PRO001":
            tier = "Pro"
        elif plan_id == "P-BASIC001":
            tier = "Basic"
        else:
            tier = "Unknown"

        # Try override from cached email if exists
        if os.path.exists(PENDING_CACHE):
            try:
                with open(PENDING_CACHE, "r") as f:
                    pending = json.load(f)
                    if subscription_id in pending:
                        email = pending[subscription_id]
                        # Remove from pending cache after use
                        del pending[subscription_id]
                        with open(PENDING_CACHE, "w") as f:
                            json.dump(pending, f)
            except Exception as e:
                logger.error(f"Error reading pending cache: {e}")

        if email:
            try:
                # Generate subscriber ID
                subscriber_id = generate_subscriber_id(email, subscription_id)
                
                # Load existing mailing list
                existing_emails = []
                if os.path.exists(MAILING_LIST):
                    with open(MAILING_LIST, "r") as f:
                        existing_emails = [line.strip().lower() for line in f if line.strip()]
                
                # Add email if not already in list
                if email not in existing_emails:
                    with open(MAILING_LIST, "a") as f:
                        f.write(email + "\n")
                
                # Log subscription
                with open(SUB_LOG, "a", newline='') as log:
                    writer = csv.writer(log)
                    writer.writerow([timestamp, email, subscription_id, subscriber_id, tier, ip])
                
                # Send welcome email
                send_welcome_email(email, tier)
                
                logger.info(f"Subscription activated: {email} - {tier}")
                return jsonify({"status": "added", "tier": tier}), 200
            except Exception as e:
                logger.error(f"Error processing subscription: {e}")
                return jsonify({"error": str(e)}), 500
        else:
            logger.error("No email found in subscription event")
            return jsonify({"status": "error", "message": "No email found"}), 400

    return jsonify({"status": "ignored", "event_type": event_type}), 200

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Run app for testing
    app.run(host="0.0.0.0", port=8080)