"""
Subscription access control middleware for DailyStonks.
Provides functions to generate access tokens and validate subscriptions.
"""
import os
import time
import hmac
import hashlib
import functools
import logging
from urllib.parse import urlencode
from flask import request, redirect, render_template, url_for

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/subscription_access.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Subscription tiers and permissions
SUBSCRIPTION_TIERS = {
    'Free': {
        'access_level': 0,
        'features': ['basic_charts', 'market_summary'],
        'max_reports_per_week': 1
    },
    'Basic': {
        'access_level': 1,
        'features': ['basic_charts', 'market_summary', 'technical_signals', 'sector_heatmap'],
        'max_reports_per_week': 5
    },
    'Pro': {
        'access_level': 2,
        'features': ['basic_charts', 'market_summary', 'technical_signals', 'sector_heatmap', 
                    'buy_signals', 'sell_signals', 'forex_data', 'crypto_data'],
        'max_reports_per_week': float('inf')  # Unlimited
    }
}

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

def generate_access_token(email, subscriber_id, tier='Free', expires_in=86400):
    """
    Generate a secure access token for accessing protected content.
    
    Args:
        email: Subscriber's email
        subscriber_id: Unique subscriber ID
        tier: Subscription tier
        expires_in: Token validity in seconds (default: 24 hours)
        
    Returns:
        str: Secure access token
    """
    # Get secret key
    secret_key = os.environ.get('ACCESS_TOKEN_SECRET', 'dailystonks-access-token-secret')
    
    # Calculate expiry time
    expiry = int(time.time()) + expires_in
    
    # Create payload
    payload = f"{email}:{subscriber_id}:{tier}:{expiry}"
    
    # Sign payload
    signature = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
    
    # Return token
    return f"{signature}:{payload}"

def validate_access_token(token):
    """
    Validate an access token and extract user information.
    
    Args:
        token: Access token to validate
        
    Returns:
        dict: User information if token is valid, None otherwise
    """
    try:
        # Parse token
        token_parts = token.split(':', 1)
        if len(token_parts) != 2:
            logger.warning("Invalid token format")
            return None
        
        signature, payload = token_parts
        
        # Get secret key
        secret_key = os.environ.get('ACCESS_TOKEN_SECRET', 'dailystonks-access-token-secret')
        
        # Verify signature
        expected_signature = hmac.new(secret_key.encode(), payload.encode(), 'sha256').hexdigest()
        if signature != expected_signature:
            logger.warning("Invalid token signature")
            return None
        
        # Parse payload
        payload_parts = payload.split(':')
        if len(payload_parts) != 4:
            logger.warning("Invalid payload format")
            return None
        
        email, subscriber_id, tier, expiry_str = payload_parts
        
        # Check expiry
        try:
            expiry = int(expiry_str)
        except ValueError:
            logger.warning("Invalid expiry in token")
            return None
        
        if time.time() > expiry:
            logger.warning("Token expired")
            return None
        
        # Return user information
        return {
            'email': email,
            'subscriber_id': subscriber_id,
            'tier': tier,
            'expiry': expiry
        }
    except Exception as e:
        logger.error(f"Error validating access token: {e}")
        return None

def has_permission(user_info, feature):
    """
    Check if a user has permission to access a feature.
    
    Args:
        user_info: User information from validate_access_token
        feature: Feature to check permission for
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user_info:
        return False
    
    tier = user_info.get('tier', 'Free')
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS['Free'])
    
    return feature in tier_info.get('features', [])

def generate_report_url(email, report_id, tier='Free'):
    """
    Generate a secure URL for accessing a report.
    
    Args:
        email: Subscriber's email
        report_id: Unique report ID
        tier: Subscription tier
        
    Returns:
        str: Secure URL
    """
    # Try to get subscriber ID from database, fallback to generated one
    subscriber_id = get_subscriber_id_from_db(email) or generate_subscriber_id(email, "report")
    
    # Generate access token
    token = generate_access_token(email, subscriber_id, tier, expires_in=86400)  # 24 hours
    
    # Create query parameters
    params = {
        'token': token,
        'report': report_id
    }
    
    # Generate URL
    base_url = os.environ.get('BASE_URL', 'https://whispr.dev')
    return f"{base_url}/reports/view?{urlencode(params)}"

def get_subscriber_id_from_db(email):
    """
    Get subscriber ID from database.
    
    Args:
        email: Subscriber's email
        
    Returns:
        str: Subscriber ID or None if not found
    """
    try:
        # Placeholder for database lookup
        # In a real implementation, this would query a database
        # For now, just return None to fallback to generated ID
        return None
    except Exception as e:
        logger.error(f"Error getting subscriber ID from database: {e}")
        return None

def subscription_required(feature=None, min_tier='Basic'):
    """
    Decorator to require a valid subscription for a Flask route.
    
    Args:
        feature: Specific feature to check permission for
        min_tier: Minimum subscription tier required
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from request
            token = request.args.get('token')
            
            if not token:
                logger.warning("No access token provided")
                return redirect(url_for('subscribe'))
            
            # Validate token
            user_info = validate_access_token(token)
            
            if not user_info:
                logger.warning("Invalid access token")
                return redirect(url_for('subscribe'))
            
            # Check tier
            tier = user_info.get('tier', 'Free')
            tier_level = SUBSCRIPTION_TIERS.get(tier, {}).get('access_level', 0)
            min_tier_level = SUBSCRIPTION_TIERS.get(min_tier, {}).get('access_level', 1)
            
            if tier_level < min_tier_level:
                logger.warning(f"Insufficient tier: {tier} (required: {min_tier})")
                return render_template('upgrade_required.html', current_tier=tier, required_tier=min_tier)
            
            # Check feature permission if specified
            if feature and not has_permission(user_info, feature):
                logger.warning(f"Missing permission for feature: {feature}")
                return render_template('feature_unavailable.html', feature=feature, tier=tier)
            
            # Store user info in request for the view function
            request.user_info = user_info
            
            # Call the view function
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example usage in a Flask app:
"""
from flask import Flask, request, render_template
from subscription_access import subscription_required

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

@app.route('/reports/view')
@subscription_required(feature='technical_signals', min_tier='Basic')
def view_report():
    # Access user info
    user_info = request.user_info
    
    # Get report ID
    report_id = request.args.get('report')
    
    # Generate report
    report_html = generate_report(report_id, user_info)
    
    return render_template('report.html', report_html=report_html, user=user_info)

if __name__ == '__main__':
    app.run(debug=True)
"""

# For testing
if __name__ == "__main__":
    # Create necessary directories
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Test subscriber ID generation
    test_email = "test@example.com"
    test_sub_id = "sub_123456"
    subscriber_id = generate_subscriber_id(test_email, test_sub_id)
    print(f"Subscriber ID: {subscriber_id}")
    
    # Test access token generation and validation
    token = generate_access_token(test_email, subscriber_id, "Pro", 3600)
    print(f"Access Token: {token}")
    
    user_info = validate_access_token(token)
    print(f"User Info: {user_info}")
    
    # Test permission check
    has_perm = has_permission(user_info, "buy_signals")
    print(f"Has permission for buy_signals: {has_perm}")
    
    # Test report URL generation
    report_url = generate_report_url(test_email, "report_20240503", "Pro")
    print(f"Report URL: {report_url}")