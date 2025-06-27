#!/bin/bash
# DailyStonks Deployment & Operation Guide
# This script contains instructions and commands for deploying and managing your DailyStonks system

##################################################
## 1. ENVIRONMENT SETUP
##################################################

# Create directory structure
setup_directories() {
  echo "Setting up directory structure..."
  
  # Create main directories
  mkdir -p dailystonks
  cd dailystonks
  
  # Create subdirectories
  mkdir -p logs cache reports charts data templates static
  mkdir -p logs/nginx logs/gunicorn
  
  echo "Directory structure created successfully."
}

# Create environment file
create_env_file() {
  echo "Creating environment file..."
  
  cat > .env << EOL
# Email configuration
EMAIL_SENDER=DailyStonks@whispr.dev
EMAIL_PASSWORD=your-secure-password
EMAIL_SMTP=in-v3.mailjet.com
EMAIL_PORT=587
EMAIL_RATE_LIMIT=10
EMAIL_RATE_PERIOD=3600

# PayPal configuration
PAYPAL_WEBHOOK_ID=your-webhook-id
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_API_URL=https://api-m.paypal.com

# Security
SECRET_KEY=your-secret-key
SECRET_SALT=your-secret-salt
ACCESS_TOKEN_SECRET=your-access-token-secret

# Server configuration
BASE_URL=https://whispr.dev
GUNICORN_BIND=0.0.0.0:8080
GUNICORN_WORKERS=2
GUNICORN_LOG_LEVEL=info
GUNICORN_ERROR_LOG=logs/gunicorn/error.log
GUNICORN_ACCESS_LOG=logs/gunicorn/access.log

# Background tasks (if using Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOL

  echo "Environment file created. Please edit .env with your actual credentials."
}

# Load environment variables
load_env() {
  if [ -f .env ]; then
    echo "Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
  else
    echo "Error: .env file not found. Please run create_env_file first."
    exit 1
  fi
}

##################################################
## 2. DEPLOYMENT SCRIPTS
##################################################

# Create deployment scripts
create_deployment_scripts() {
  echo "Creating deployment scripts..."
  
  # Main deployment script
  cat > deploy.sh << 'EOL'
#!/bin/bash
# Main deployment script for DailyStonks

# Load environment variables
source .env

# Check if user specified a component to deploy
if [ "$1" == "" ]; then
  echo "Usage: ./deploy.sh [all|paypal|unsubscribe|main|nginx|celery]"
  exit 1
fi

# Deploy all components
if [ "$1" == "all" ]; then
  echo "Deploying all components..."
  ./deploy.sh paypal
  ./deploy.sh unsubscribe
  ./deploy.sh main
  ./deploy.sh nginx
  ./deploy.sh celery
  exit 0
fi

# Deploy PayPal webhook server
if [ "$1" == "paypal" ]; then
  echo "Deploying PayPal webhook server..."
  
  # Check if server is already running
  if pgrep -f "gunicorn.*paypal_webhook:app" > /dev/null; then
    echo "PayPal webhook server is already running. Stopping it first..."
    pkill -f "gunicorn.*paypal_webhook:app"
    sleep 2
  fi
  
  # Start server
  echo "Starting PayPal webhook server..."
  gunicorn -c gunicorn_config.py paypal_webhook:app \
    --bind 0.0.0.0:8080 \
    --daemon \
    --pid logs/paypal_webhook.pid \
    --access-logfile logs/gunicorn/paypal_access.log \
    --error-logfile logs/gunicorn/paypal_error.log
  
  echo "PayPal webhook server deployed."
fi

# Deploy unsubscribe server
if [ "$1" == "unsubscribe" ]; then
  echo "Deploying unsubscribe server..."
  
  # Check if server is already running
  if pgrep -f "gunicorn.*unsubscribe_server:app" > /dev/null; then
    echo "Unsubscribe server is already running. Stopping it first..."
    pkill -f "gunicorn.*unsubscribe_server:app"
    sleep 2
  fi
  
  # Start server
  echo "Starting unsubscribe server..."
  gunicorn -c gunicorn_config.py unsubscribe_server:app \
    --bind 0.0.0.0:8081 \
    --daemon \
    --pid logs/unsubscribe_server.pid \
    --access-logfile logs/gunicorn/unsubscribe_access.log \
    --error-logfile logs/gunicorn/unsubscribe_error.log
  
  echo "Unsubscribe server deployed."
fi

# Deploy main application
if [ "$1" == "main" ]; then
  echo "Deploying main application..."
  
  # Check if app is already running
  if pgrep -f "gunicorn.*main_app:app" > /dev/null; then
    echo "Main application is already running. Stopping it first..."
    pkill -f "gunicorn.*main_app:app"
    sleep 2
  fi
  
  # Start app
  echo "Starting main application..."
  gunicorn -c gunicorn_config.py main_app:app \
    --bind 0.0.0.0:8082 \
    --daemon \
    --pid logs/main_app.pid \
    --access-logfile logs/gunicorn/main_access.log \
    --error-logfile logs/gunicorn/main_error.log
  
  echo "Main application deployed."
fi

# Deploy nginx
if [ "$1" == "nginx" ]; then
  echo "Configuring and deploying nginx..."
  
  # Create nginx configuration
  cat > nginx.conf << EOF
server {
    listen 80;
    server_name whispr.dev www.whispr.dev;

    access_log /var/log/nginx/dailystonks.access.log;
    error_log /var/log/nginx/dailystonks.error.log;

    # PayPal webhook handling
    location /paypal/webhook {
        proxy_pass http://localhost:8080/paypal/webhook;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /paypal/cache-subscription {
        proxy_pass http://localhost:8080/paypal/cache-subscription;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Unsubscribe handling
    location /unsubscribe {
        proxy_pass http://localhost:8081/unsubscribe;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Main application
    location / {
        proxy_pass http://localhost:8082;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
    }

    # Reports directory
    location /reports/ {
        alias $(pwd)/reports/;
        try_files \$uri =404;
        # Requires authentication
        auth_request /auth;
    }

    # Charts directory
    location /charts/ {
        alias $(pwd)/charts/;
        try_files \$uri =404;
        # Requires authentication
        auth_request /auth;
    }

    # Authentication endpoint
    location = /auth {
        internal;
        proxy_pass http://localhost:8082/auth;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI \$request_uri;
    }

    # Subscription page
    location = /subscribe {
        return 302 /static/subscribe.html;
    }
}
EOF

  # Copy to nginx config directory
  sudo cp nginx.conf /etc/nginx/sites-available/dailystonks
  
  # Enable site
  sudo ln -sf /etc/nginx/sites-available/dailystonks /etc/nginx/sites-enabled/
  
  # Test and reload
  sudo nginx -t && sudo systemctl reload nginx
  
  echo "Nginx deployed."
fi

# Deploy Celery
if [ "$1" == "celery" ]; then
  echo "Deploying Celery workers..."
  
  # Check if Celery is already running
  if pgrep -f "celery.*worker" > /dev/null; then
    echo "Celery worker is already running. Stopping it first..."
    pkill -f "celery.*worker"
    sleep 2
  fi
  
  # Check if Celery beat is already running
  if pgrep -f "celery.*beat" > /dev/null; then
    echo "Celery beat is already running. Stopping it first..."
    pkill -f "celery.*beat"
    sleep 2
  fi
  
  # Start Celery worker
  echo "Starting Celery worker..."
  celery -A main_enhanced worker --loglevel=info --logfile=logs/celery_worker.log --detach
  
  # Start Celery beat
  echo "Starting Celery beat..."
  celery -A main_enhanced beat --loglevel=info --logfile=logs/celery_beat.log --detach
  
  echo "Celery deployed."
fi
EOL

  # Create stop script
  cat > stop.sh << 'EOL'
#!/bin/bash
# Script to stop DailyStonks services

# Load environment variables
source .env

# Check if user specified a component to stop
if [ "$1" == "" ]; then
  echo "Usage: ./stop.sh [all|paypal|unsubscribe|main|celery]"
  exit 1
fi

# Stop all components
if [ "$1" == "all" ]; then
  echo "Stopping all components..."
  ./stop.sh paypal
  ./stop.sh unsubscribe
  ./stop.sh main
  ./stop.sh celery
  exit 0
fi

# Stop PayPal webhook server
if [ "$1" == "paypal" ]; then
  echo "Stopping PayPal webhook server..."
  if pgrep -f "gunicorn.*paypal_webhook:app" > /dev/null; then
    pkill -f "gunicorn.*paypal_webhook:app"
    echo "PayPal webhook server stopped."
  else
    echo "PayPal webhook server is not running."
  fi
fi

# Stop unsubscribe server
if [ "$1" == "unsubscribe" ]; then
  echo "Stopping unsubscribe server..."
  if pgrep -f "gunicorn.*unsubscribe_server:app" > /dev/null; then
    pkill -f "gunicorn.*unsubscribe_server:app"
    echo "Unsubscribe server stopped."
  else
    echo "Unsubscribe server is not running."
  fi
fi

# Stop main application
if [ "$1" == "main" ]; then
  echo "Stopping main application..."
  if pgrep -f "gunicorn.*main_app:app" > /dev/null; then
    pkill -f "gunicorn.*main_app:app"
    echo "Main application stopped."
  else
    echo "Main application is not running."
  fi
fi

# Stop Celery
if [ "$1" == "celery" ]; then
  echo "Stopping Celery workers and beat..."
  if pgrep -f "celery.*worker" > /dev/null; then
    pkill -f "celery.*worker"
    echo "Celery worker stopped."
  else
    echo "Celery worker is not running."
  fi
  
  if pgrep -f "celery.*beat" > /dev/null; then
    pkill -f "celery.*beat"
    echo "Celery beat stopped."
  else
    echo "Celery beat is not running."
  fi
fi
EOL

  # Create status script
  cat > status.sh << 'EOL'
#!/bin/bash
# Script to check status of DailyStonks services

# Check PayPal webhook server
echo "=== PayPal Webhook Server ==="
if pgrep -f "gunicorn.*paypal_webhook:app" > /dev/null; then
  pid=$(pgrep -f "gunicorn.*paypal_webhook:app" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check unsubscribe server
echo "=== Unsubscribe Server ==="
if pgrep -f "gunicorn.*unsubscribe_server:app" > /dev/null; then
  pid=$(pgrep -f "gunicorn.*unsubscribe_server:app" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check main application
echo "=== Main Application ==="
if pgrep -f "gunicorn.*main_app:app" > /dev/null; then
  pid=$(pgrep -f "gunicorn.*main_app:app" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check Celery worker
echo "=== Celery Worker ==="
if pgrep -f "celery.*worker" > /dev/null; then
  pid=$(pgrep -f "celery.*worker" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check Celery beat
echo "=== Celery Beat ==="
if pgrep -f "celery.*beat" > /dev/null; then
  pid=$(pgrep -f "celery.*beat" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check Redis
echo "=== Redis Server ==="
if pgrep -f "redis-server" > /dev/null; then
  pid=$(pgrep -f "redis-server" | head -1)
  uptime=$(ps -p $pid -o etime= | xargs)
  echo "Status: RUNNING (PID: $pid, Uptime: $uptime)"
else
  echo "Status: STOPPED"
fi
echo ""

# Check Nginx
echo "=== Nginx Server ==="
if systemctl is-active nginx > /dev/null; then
  echo "Status: RUNNING"
else
  echo "Status: STOPPED"
fi
echo ""

# Check system health
echo "=== System Health ==="
echo "Disk usage:"
df -h | grep -E "Filesystem|/$"
echo ""
echo "Memory usage:"
free -h
echo ""
echo "CPU load:"
uptime
EOL

  # Create logs script
  cat > logs.sh << 'EOL'
#!/bin/bash
# Script to view logs of DailyStonks services

# Check if user specified a component to view logs for
if [ "$1" == "" ]; then
  echo "Usage: ./logs.sh [paypal|unsubscribe|main|nginx|celery] [lines]"
  exit 1
fi

# Default number of lines
lines=${2:-100}

# View PayPal webhook server logs
if [ "$1" == "paypal" ]; then
  echo "=== PayPal Webhook Server Logs ==="
  echo "=== Access Log ==="
  tail -n $lines logs/gunicorn/paypal_access.log
  echo ""
  echo "=== Error Log ==="
  tail -n $lines logs/gunicorn/paypal_error.log
fi

# View unsubscribe server logs
if [ "$1" == "unsubscribe" ]; then
  echo "=== Unsubscribe Server Logs ==="
  echo "=== Access Log ==="
  tail -n $lines logs/gunicorn/unsubscribe_access.log
  echo ""
  echo "=== Error Log ==="
  tail -n $lines logs/gunicorn/unsubscribe_error.log
fi

# View main application logs
if [ "$1" == "main" ]; then
  echo "=== Main Application Logs ==="
  echo "=== Access Log ==="
  tail -n $lines logs/gunicorn/main_access.log
  echo ""
  echo "=== Error Log ==="
  tail -n $lines logs/gunicorn/main_error.log
fi

# View nginx logs
if [ "$1" == "nginx" ]; then
  echo "=== Nginx Logs ==="
  echo "=== Access Log ==="
  sudo tail -n $lines /var/log/nginx/dailystonks.access.log
  echo ""
  echo "=== Error Log ==="
  sudo tail -n $lines /var/log/nginx/dailystonks.error.log
fi

# View Celery logs
if [ "$1" == "celery" ]; then
  echo "=== Celery Logs ==="
  echo "=== Worker Log ==="
  tail -n $lines logs/celery_worker.log
  echo ""
  echo "=== Beat Log ==="
  tail -n $lines logs/celery_beat.log
fi
EOL

  # Create startup script
  cat > startup.sh << 'EOL'
#!/bin/bash
# Script to start all DailyStonks services on system boot

# Load environment variables
source .env

# Start all services
echo "Starting DailyStonks services..."

# Start Redis if needed
if ! pgrep -x redis-server > /dev/null; then
  echo "Starting Redis..."
  redis-server --daemonize yes
  sleep 2
fi

# Deploy all services
./deploy.sh all

echo "All services started."
EOL

  # Make scripts executable
  chmod +x deploy.sh stop.sh status.sh logs.sh startup.sh
  
  echo "Deployment scripts created successfully."
}

##################################################
## 3. MANUAL OPERATION SCRIPTS
##################################################

# Create manual operation scripts
create_operation_scripts() {
  echo "Creating operation scripts..."
  
  # Generate report script
  cat > generate_report.sh << 'EOL'
#!/bin/bash
# Script to manually generate a report

# Load environment variables
source .env

# Check if user specified a tier
if [ "$1" == "" ]; then
  tier="Basic"
else
  tier="$1"
fi

echo "Generating $tier report..."
python -c "from main_enhanced import report_generator; report = report_generator.generate_report(tier='$tier'); print(f'Report generated: {report[\"report_id\"] if report else \"Failed\"}');"
EOL

  # Send report script
  cat > send_report.sh << 'EOL'
#!/bin/bash
# Script to manually send a report to subscribers

# Load environment variables
source .env

# Check if user specified a tier
if [ "$1" == "" ]; then
  tier="Basic"
else
  tier="$1"
fi

echo "Sending $tier report to subscribers..."
python -c "from main_enhanced import report_generator; results = report_generator.send_report_to_subscribers(tier='$tier'); print(f'Report sent to {results[\"success\"]} subscribers, {results[\"failed\"]} failed');"
EOL

  # Clean old reports script
  cat > cleanup_reports.sh << 'EOL'
#!/bin/bash
# Script to clean up old reports

# Load environment variables
source .env

# Check if user specified days
if [ "$1" == "" ]; then
  days=7
else
  days="$1"
fi

echo "Cleaning up reports older than $days days..."
python -c "from main_enhanced import report_generator; deleted = report_generator.cleanup_old_reports(max_age_days=$days); print(f'Cleaned up {deleted} reports');"
EOL

  # Health check script
  cat > health_check.sh << 'EOL'
#!/bin/bash
# Script to check system health

# Load environment variables
source .env

echo "Checking system health..."
python -c "from main_enhanced import check_health; health = check_health(); print(f'System health: {health[\"status\"]}'); print('Checks:'); [print(f'  {check}: {\"OK\" if status else \"FAIL\"}') for check, status in health['checks'].items()];"
EOL

  # Make scripts executable
  chmod +x generate_report.sh send_report.sh cleanup_reports.sh health_check.sh
  
  echo "Operation scripts created successfully."
}

##################################################
## 4. SYSTEM REQUIREMENTS
##################################################

# Install system requirements
install_requirements() {
  echo "Installing system requirements..."
  
  # Update package list
  sudo apt-get update
  
  # Install required packages
  sudo apt-get install -y python3 python3-pip python3-venv nginx redis-server
  
  # Create virtual environment
  python3 -m venv venv
  
  # Activate virtual environment
  source venv/bin/activate
  
  # Install Python dependencies
  pip install -U pip
  pip install gunicorn flask celery redis pandas numpy matplotlib mplfinance yfinance premailer
  
  echo "System requirements installed successfully."
}

##################################################
## 5. COMPLETE DEPLOYMENT
##################################################

# Complete deployment
deploy_all() {
  echo "Starting complete deployment..."
  
  # Setup directories
  setup_directories
  
  # Create environment file
  create_env_file
  
  # Install requirements
  install_requirements
  
  # Create deployment scripts
  create_deployment_scripts
  
  # Create operation scripts
  create_operation_scripts
  
  echo "Deployment preparation complete."
  echo ""
  echo "Next steps:"
  echo "1. Edit .env file with your actual credentials"
  echo "2. Copy your Python files to the appropriate locations"
  echo "3. Start the services by running ./deploy.sh all"
  echo ""
  echo "For more information, see the README.md file."
}

##################################################
## 6. DEPLOYMENT INSTRUCTIONS
##################################################

# You can run this script directly to deploy everything
# Or you can run individual functions as needed

# Check for command-line arguments
if [ "$1" == "" ]; then
  echo "DailyStonks Deployment & Operation Guide"
  echo ""
  echo "Usage: $0 [setup|env|requirements|scripts|operation|deploy]"
  echo ""
  echo "  setup       - Setup directory structure"
  echo "  env         - Create environment file"
  echo "  requirements - Install system requirements"
  echo "  scripts     - Create deployment scripts"
  echo "  operation   - Create operation scripts"
  echo "  deploy      - Complete deployment"
  echo ""
  exit 0
fi

# Run requested function
case "$1" in
  setup)
    setup_directories
    ;;
  env)
    create_env_file
    ;;
  requirements)
    install_requirements
    ;;
  scripts)
    create_deployment_scripts
    ;;
  operation)
    create_operation_scripts
    ;;
  deploy)
    deploy_all
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac