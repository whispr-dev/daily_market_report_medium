#!/bin/bash
# Setup script for DailyStonks Pro features

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================"
echo "DailyStonks Pro Features Setup"
echo "======================================"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs charts reports templates test_output
mkdir -p templates/pro
mkdir -p data/subscribers

# Check if running inside virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Warning: It's recommended to run this script inside a Python virtual environment."
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Exiting. Please create and activate a virtual environment first."
    exit 1
  fi
fi

# Install required Python packages
echo "Installing required Python packages..."
pip install -r requirements.txt || {
  echo "Failed to install packages from requirements.txt"
  echo "Creating a new requirements file..."
  
  # Create requirements file if it doesn't exist or failed
  cat > requirements.txt << EOL
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
yfinance>=0.1.70
jinja2>=3.0.0
premailer>=3.10.0
statsmodels>=0.13.0
mplfinance>=0.12.9b0
EOL
  
  echo "Trying again with new requirements file..."
  pip install -r requirements.txt || {
    echo "Error: Failed to install required packages."
    exit 1
  }
}

# Copy template files
echo "Setting up email templates..."

# Pro email template
if [ ! -f "templates/pro_email_template.html" ]; then
  if [ -f "artifacts/pro_email_template.html" ]; then
    cp "artifacts/pro_email_template.html" "templates/"
    echo "Pro email template installed."
  else
    echo "Warning: Pro email template not found in artifacts."
    echo "Please copy it manually to templates/pro_email_template.html"
  fi
else
  echo "Pro email template already exists."
fi

# Copy Python modules
echo "Setting up Python modules..."

# Pro features module
if [ ! -f "pro_features.py" ]; then
  if [ -f "artifacts/pro_tier_report_generator.py" ]; then
    cp "artifacts/pro_tier_report_generator.py" "pro_features.py"
    echo "Pro features module installed."
  else
    echo "Warning: Pro features module not found in artifacts."
    echo "Please copy it manually to pro_features.py"
  fi
else
  echo "Pro features module already exists."
fi

# Template filters module
if [ ! -f "template_filters.py" ]; then
  if [ -f "artifacts/template_filters.py" ]; then
    cp "artifacts/template_filters.py" "template_filters.py"
    echo "Template filters module installed."
  else
    echo "Warning: Template filters module not found in artifacts."
    echo "Please copy it manually to template_filters.py"
  fi
else
  echo "Template filters module already exists."
fi

# Pro report generator script
if [ ! -f "generate_pro_report.py" ]; then
  if [ -f "artifacts/generate_pro_report.py" ]; then
    cp "artifacts/generate_pro_report.py" "generate_pro_report.py"
    chmod +x "generate_pro_report.py"
    echo "Pro report generator script installed."
  else
    echo "Warning: Pro report generator script not found in artifacts."
    echo "Please copy it manually to generate_pro_report.py"
  fi
else
  echo "Pro report generator script already exists."
fi

# Sample subscribers file
if [ ! -f "pro_subscribers.json" ]; then
  if [ -f "artifacts/pro_subscribers.json" ]; then
    cp "artifacts/pro_subscribers.json" "pro_subscribers.json"
    echo "Sample subscribers file created."
  else
    echo "Warning: Sample subscribers file not found in artifacts."
    echo "Please copy it manually to pro_subscribers.json"
  fi
else
  echo "Subscribers file already exists."
fi

# Send Pro reports script
if [ ! -f "send_pro_reports.sh" ]; then
  if [ -f "artifacts/send_pro_reports.sh" ]; then
    cp "artifacts/send_pro_reports.sh" "send_pro_reports.sh"
    chmod +x "send_pro_reports.sh"
    echo "Send Pro reports script installed."
  else
    echo "Warning: Send Pro reports script not found in artifacts."
    echo "Please copy it manually to send_pro_reports.sh"
  fi
else
  echo "Send Pro reports script already exists."
fi

# Check for required environment variables
echo "Checking environment variables..."
if [ ! -f ".env" ]; then
  echo "Creating .env file template..."
  cat > .env << EOL
# Email configuration
EMAIL_SENDER=DailyStonks@whispr.dev
EMAIL_PASSWORD=your-secure-password
EMAIL_SMTP=in-v3.mailjet.com
EMAIL_PORT=587
EMAIL_RATE_LIMIT=10
EMAIL_RATE_PERIOD=3600

# Security
SECRET_KEY=replace-with-random-string
SECRET_SALT=replace-with-random-string
ACCESS_TOKEN_SECRET=replace-with-random-string

# Server configuration
BASE_URL=https://whispr.dev
EOL
  echo "Please edit the .env file with your actual credentials."
else
  echo ".env file already exists."
fi

# Create test script for quick testing
echo "Creating test script..."
cat > test_pro_report.sh << EOL
#!/bin/bash
# Quick test script for Pro report generation

# Set script directory
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
cd "\$SCRIPT_DIR"

# Load environment variables
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found. Please create it first."
  exit 1
fi

# Run in test mode
./send_pro_reports.sh --test
EOL
chmod +x test_pro_report.sh
echo "Test script created: test_pro_report.sh"

# Set up cron job for daily reports
echo "Would you like to set up a cron job to send reports daily at market close (4:30 PM EST)?"
read -p "Set up cron job? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Create temporary crontab file
  TEMP_CRON=$(mktemp)
  
  # Export current crontab
  crontab -l > "$TEMP_CRON" 2>/dev/null || echo "" > "$TEMP_CRON"
  
  # Check if entry already exists
  if grep -q "send_pro_reports.sh" "$TEMP_CRON"; then
    echo "Cron job already exists."
  else
    # Add new cron job (4:30 PM EST, which is +5 hours from UTC)
    echo "30 21 * * 1-5 cd $SCRIPT_DIR && ./send_pro_reports.sh >> logs/pro_cron.log 2>&1" >> "$TEMP_CRON"
    
    # Install new crontab
    crontab "$TEMP_CRON"
    echo "Cron job set up to run at 4:30 PM EST on weekdays."
  fi
  
  # Clean up
  rm "$TEMP_CRON"
else
  echo "Skipping cron job setup."
fi

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "To test the Pro report generation:"
echo "  ./test_pro_report.sh"
echo ""
echo "To send Pro reports to all subscribers:"
echo "  ./send_pro_reports.sh"
echo ""
echo "Don't forget to edit the .env file with your actual credentials."
echo "======================================"