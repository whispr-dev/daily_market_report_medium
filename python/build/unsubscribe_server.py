"""
Unsubscribe server for DailyStonks.
Handles unsubscribe requests from users.
"""
from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import logging
import hmac
import time
import hashlib

app = Flask(__name__, template_folder="templates")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unsubscribe.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAILING_LIST = "mailing_list.txt"
UNSUB_LOG = "unsubscribe_log.csv"

def validate_unsubscribe_token(email, token, max_age=604800):  # Default 7 days
    """
    Validate an unsubscribe token.
    
    Args:
        email (str): Subscriber email
        token (str): Token to validate
        max_age (int): Maximum token age in seconds
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        # Parse token
        token_parts = token.split(':')
        if len(token_parts) != 2:
            return False
        
        signature, timestamp_str = token_parts
        timestamp = int(timestamp_str)
        
        # Check if token is expired
        current_time = int(time.time())
        if current_time - timestamp > max_age:
            return False
        
        # Verify signature
        secret_key = os.environ.get('SECRET_KEY', 'dailystonks-secret-key')
        payload = f"{email}:{timestamp}"
        expected_signature = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
        
        return signature == expected_signature
        
    except Exception as e:
        logger.error(f"Error validating unsubscribe token: {e}")
        return False

def remove_from_mailing_list(email):
    """
    Remove an email from the mailing list.
    
    Args:
        email (str): Email to remove
        
    Returns:
        bool: True if removed successfully, False otherwise
    """
    try:
        # Load mailing list
        if not os.path.exists(MAILING_LIST):
            logger.error(f"Mailing list file not found: {MAILING_LIST}")
            return False
        
        with open(MAILING_LIST, 'r') as f:
            emails = [line.strip().lower() for line in f if line.strip()]
        
        # Check if email exists
        email = email.lower().strip()
        if email not in emails:
            logger.warning(f"Email not found in mailing list: {email}")
            return True  # Consider it successful since it's not in the list
        
        # Remove email
        emails.remove(email)
        
        # Write back to file
        with open(MAILING_LIST, 'w') as f:
            for e in emails:
                f.write(f"{e}\n")
        
        # Log unsubscribe
        with open(UNSUB_LOG, 'a') as f:
            timestamp = int(time.time())
            f.write(f"{timestamp},{email}\n")
        
        logger.info(f"Email removed from mailing list: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing email from mailing list: {e}")
        return False

@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    """
    Handle unsubscribe requests.
    """
    # Get email from request
    email = request.args.get('email')
    token = request.args.get('token')
    
    # Handle POST request (feedback submission)
    if request.method == 'POST':
        feedback = request.form.get('feedback', '')
        
        # Log feedback
        if feedback:
            logger.info(f"Feedback from {email}: {feedback}")
            
            # Save feedback to file
            with open('feedback_log.csv', 'a') as f:
                timestamp = int(time.time())
                f.write(f"{timestamp},{email},{feedback.replace(',', ';')}\n")
        
        return render_template('unsubscribe_result.html', message="Thank you for your feedback!")
    
    # Handle GET request (unsubscribe)
    if not email:
        logger.warning("Unsubscribe request missing email parameter")
        return render_template('unsubscribe_result.html', message="Missing email parameter")
    
    # Validate token if provided
    if token:
        if not validate_unsubscribe_token(email, token):
            logger.warning(f"Invalid unsubscribe token for {email}")
            return render_template('unsubscribe_result.html', message="Invalid or expired unsubscribe token")
    
    # Remove from mailing list
    success = remove_from_mailing_list(email)
    
    if success:
        return render_template('unsubscribe_result.html', message="You have been unsubscribed successfully.", email=email)
    else:
        return render_template('unsubscribe_result.html', message="Failed to unsubscribe. Please try again or contact support.")

@app.route('/health')
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Create mailing list file if it doesn't exist
    if not os.path.exists(MAILING_LIST):
        with open(MAILING_LIST, 'w'):
            pass
    
    # Create unsubscribe log file if it doesn't exist
    if not os.path.exists(UNSUB_LOG):
        with open(UNSUB_LOG, 'w'):
            pass
    
    # Run app
    app.run(host='0.0.0.0', port=8081, debug=True)