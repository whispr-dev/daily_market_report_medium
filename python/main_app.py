"""
Main application server for DailyStonks.
Handles report viewing, access control, and API endpoints.
"""
from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file, abort
import os
import logging
import json
from datetime import datetime

# Import necessary modules
from subscription_access import (
    validate_access_token,
    has_permission,
    generate_report_url
)
from main_enhanced import (
    report_generator,
    check_health
)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """
    Main landing page.
    """
    return render_template('index.html')

@app.route('/subscribe')
def subscribe():
    """
    Subscription page.
    """
    return render_template('subscribe.html')

@app.route('/reports/view')
def view_report():
    """
    View a report.
    Requires a valid access token.
    """
    # Get token and report ID from request
    token = request.args.get('token')
    report_id = request.args.get('report')
    
    if not token or not report_id:
        logger.warning("Missing token or report ID")
        return redirect(url_for('subscribe'))
    
    # Validate token
    user_info = validate_access_token(token)
    
    if not user_info:
        logger.warning("Invalid access token")
        return redirect(url_for('subscribe'))
    
    # Get cached report
    cached_report = report_generator.get_cached_report(report_id)
    
    if not cached_report:
        logger.warning(f"Report not found: {report_id}")
        return render_template('error.html', message="Report not found")
    
    # Check tier
    user_tier = user_info.get('tier', 'Free')
    report_tier = cached_report.get('tier', 'Basic')
    
    # Check if user has access to this report tier
    if (report_tier == 'Pro' and user_tier != 'Pro') or (report_tier == 'Basic' and user_tier == 'Free'):
        logger.warning(f"Insufficient tier: {user_tier} (required: {report_tier})")
        return render_template('upgrade_required.html', current_tier=user_tier, required_tier=report_tier)
    
    # Store user info in request for the template
    request.user_info = user_info
    
    # Get HTML content
    html_content = cached_report.get('html')
    
    if not html_content:
        logger.warning(f"Report content missing: {report_id}")
        return render_template('error.html', message="Report content missing")
    
    # Return report
    return html_content

@app.route('/auth')
def auth():
    """
    Authentication endpoint for nginx auth_request.
    Used to protect access to report and chart files.
    """
    # Get token from query string
    token = request.args.get('token')
    
    if not token:
        # Check auth header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
    
    if not token:
        logger.warning("Missing access token")
        return '', 401
    
    # Validate token
    user_info = validate_access_token(token)
    
    if not user_info:
        logger.warning("Invalid access token")
        return '', 401
    
    # Check requested URI
    original_uri = request.headers.get('X-Original-URI', '')
    
    # Check if URI is for a Pro resource
    if '/pro/' in original_uri and user_info.get('tier') != 'Pro':
        logger.warning(f"Access denied to Pro resource: {original_uri}")
        return '', 403
    
    # Success
    return '', 200

@app.route('/api/report/<report_id>')
def get_report(report_id):
    """
    API endpoint to get a report.
    Requires a valid access token.
    """
    # Get token from query string or auth header
    token = request.args.get('token')
    
    if not token:
        # Check auth header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
    
    if not token:
        logger.warning("Missing access token")
        return jsonify({'error': 'Missing access token'}), 401
    
    # Validate token
    user_info = validate_access_token(token)
    
    if not user_info:
        logger.warning("Invalid access token")
        return jsonify({'error': 'Invalid access token'}), 401
    
    # Get cached report
    cached_report = report_generator.get_cached_report(report_id)
    
    if not cached_report:
        logger.warning(f"Report not found: {report_id}")
        return jsonify({'error': 'Report not found'}), 404
    
    # Check tier
    user_tier = user_info.get('tier', 'Free')
    report_tier = cached_report.get('tier', 'Basic')
    
    # Check if user has access to this report tier
    if (report_tier == 'Pro' and user_tier != 'Pro') or (report_tier == 'Basic' and user_tier == 'Free'):
        logger.warning(f"Insufficient tier: {user_tier} (required: {report_tier})")
        return jsonify({'error': 'Insufficient subscription tier'}), 403
    
    # Return report metadata
    return jsonify({
        'report_id': report_id,
        'timestamp': cached_report.get('timestamp'),
        'tier': report_tier,
        'url': generate_report_url(user_info.get('email'), report_id, user_tier)
    })

@app.route('/api/reports')
def list_reports():
    """
    API endpoint to list available reports.
    Requires a valid access token.
    """
    # Get token from query string or auth header
    token = request.args.get('token')
    
    if not token:
        # Check auth header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
    
    if not token:
        logger.warning("Missing access token")
        return jsonify({'error': 'Missing access token'}), 401
    
    # Validate token
    user_info = validate_access_token(token)
    
    if not user_info:
        logger.warning("Invalid access token")
        return jsonify({'error': 'Invalid access token'}), 401
    
    # Get user tier
    user_tier = user_info.get('tier', 'Free')
    
    # Filter reports by tier
    available_reports = []
    for report_id, report_data in report_generator.report_cache.items():
        report_tier = report_data.get('tier', 'Basic')
        
        # Check if user has access to this report tier
        if (report_tier == 'Pro' and user_tier == 'Pro') or (report_tier == 'Basic' and user_tier in ['Basic', 'Pro']) or (report_tier == 'Free'):
            available_reports.append({
                'report_id': report_id,
                'timestamp': report_data.get('timestamp'),
                'tier': report_tier,
                'url': generate_report_url(user_info.get('email'), report_id, user_tier)
            })
    
    # Sort by timestamp (newest first)
    available_reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({'reports': available_reports})

@app.route('/api/generate', methods=['POST'])
def generate_api():
    """
    API endpoint to generate a report.
    Requires a valid access token.
    """
    # Get token from query string or auth header
    token = request.args.get('token')
    
    if not token:
        # Check auth header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
    
    if not token:
        logger.warning("Missing access token")
        return jsonify({'error': 'Missing access token'}), 401
    
    # Validate token
    user_info = validate_access_token(token)
    
    if not user_info:
        logger.warning("Invalid access token")
        return jsonify({'error': 'Invalid access token'}), 401
    
    # Get request data
    data = request.get_json() or {}
    tier = data.get('tier') or user_info.get('tier', 'Basic')
    custom_symbols = data.get('symbols')
    
    # Check if user has permission to generate this tier
    user_tier = user_info.get('tier', 'Free')
    if (tier == 'Pro' and user_tier != 'Pro') or (tier == 'Basic' and user_tier == 'Free'):
        logger.warning(f"Insufficient tier: {user_tier} (required: {tier})")
        return jsonify({'error': 'Insufficient subscription tier'}), 403
    
    # Generate report
    report_data = report_generator.generate_report(tier=tier, custom_symbols=custom_symbols)
    
    if not report_data:
        logger.error("Failed to generate report")
        return jsonify({'error': 'Failed to generate report'}), 500
    
    # Return report metadata
    return jsonify({
        'report_id': report_data['report_id'],
        'timestamp': report_data['timestamp'],
        'tier': tier,
        'url': generate_report_url(user_info.get('email'), report_data['report_id'], user_tier)
    })

@app.route('/health')
def health_check():
    """
    Health check endpoint.
    """
    health = check_health()
    status_code = 200 if health['status'] == 'healthy' else 500
    return jsonify(health), status_code

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Run app
    app.run(host='0.0.0.0', port=8082, debug=True)