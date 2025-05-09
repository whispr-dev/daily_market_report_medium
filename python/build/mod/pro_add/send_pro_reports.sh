#!/bin/bash
# Script to generate and send Pro-tier market reports

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found. Please create it first."
  exit 1
fi

# Create necessary directories
mkdir -p logs charts reports templates test_output

# Check for command line arguments
TEST_MODE=false
SUBSCRIBERS_FILE="pro_subscribers.json"

while [[ $# -gt 0 ]]; do
  case $1 in
    --test)
      TEST_MODE=true
      shift
      ;;
    --subscribers)
      SUBSCRIBERS_FILE="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --test           Test mode: Generate report but don't send emails"
      echo "  --subscribers    Path to JSON file with subscribers (default: pro_subscribers.json)"
      echo "  --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Check if Pro template exists
if [ ! -f "templates/pro_email_template.html" ]; then
  echo "Pro email template not found. Copying from artifacts..."
  
  # Copy from the artifact location if available
  if [ -f "artifacts/pro_email_template.html" ]; then
    cp "artifacts/pro_email_template.html" "templates/"
    echo "Template copied successfully."
  else
    echo "Error: Pro email template not found in artifacts."
    exit 1
  fi
fi

# Check if subscribers file exists
if [ ! -f "$SUBSCRIBERS_FILE" ]; then
  echo "Subscribers file not found: $SUBSCRIBERS_FILE"
  echo "Creating sample file..."
  
  # Copy from the artifact location if available
  if [ -f "artifacts/pro_subscribers.json" ]; then
    cp "artifacts/pro_subscribers.json" "$SUBSCRIBERS_FILE"
    echo "Sample subscribers file created."
  else
    echo "Error: Sample subscribers file not found in artifacts."
    exit 1
  fi
fi

# Set Python environment
if [ -d "venv" ]; then
  source venv/bin/activate
  echo "Activated Python virtual environment."
else
  echo "Warning: Python virtual environment not found."
fi

# Check if market is open today
DAY_OF_WEEK=$(date +%u)  # 1-5 is Monday-Friday
if [ "$DAY_OF_WEEK" -gt 5 ]; then
  echo "Today is a weekend. Markets are closed."
  if [ "$TEST_MODE" != "true" ]; then
    echo "Use --test flag to run in test mode on weekends."
    exit 0
  fi
fi

# Check if there are any US market holidays today
# This is a simplified check - in a real implementation, this would be more comprehensive
CURRENT_DATE=$(date +%Y-%m-%d)
HOLIDAY_LIST="2025-01-01 2025-01-20 2025-02-17 2025-04-18 2025-05-26 2025-06-19 2025-07-04 2025-09-01 2025-11-27 2025-12-25"

if [[ "$HOLIDAY_LIST" == *"$CURRENT_DATE"* ]]; then
  echo "Today is a US market holiday. Markets are closed."
  if [ "$TEST_MODE" != "true" ]; then
    echo "Use --test flag to run in test mode on holidays."
    exit 0
  fi
fi

# Run the Python script to generate and send reports
echo "Starting Pro-tier report generation..."

if [ "$TEST_MODE" == "true" ]; then
  echo "Running in TEST MODE - reports will not be sent"
  python generate_pro_report.py --test --subscribers "$SUBSCRIBERS_FILE"
else
  echo "Running in PRODUCTION MODE - reports will be sent to subscribers"
  python generate_pro_report.py --subscribers "$SUBSCRIBERS_FILE"
fi

# Check the result
RESULT=$?
if [ $RESULT -eq 0 ]; then
  echo "Pro-tier report generation completed successfully."
  
  # If in test mode, open the generated report
  if [ "$TEST_MODE" == "true" ]; then
    LATEST_REPORT=$(ls -t test_output/pro_report_*.html | head -1)
    if [ -n "$LATEST_REPORT" ]; then
      echo "Opening latest test report: $LATEST_REPORT"
      if [ "$(uname)" == "Darwin" ]; then
        # MacOS
        open "$LATEST_REPORT"
      elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        # Linux
        if [ -n "$(command -v xdg-open)" ]; then
          xdg-open "$LATEST_REPORT"
        else
          echo "Report generated: $LATEST_REPORT"
        fi
      else
        # Windows or other
        echo "Report generated: $LATEST_REPORT"
      fi
    fi
  fi
else
  echo "Error: Pro-tier report generation failed with exit code $RESULT."
  exit $RESULT
fi

# Cleanup old test reports (keep last 10)
if [ "$TEST_MODE" == "true" ]; then
  echo "Cleaning up old test reports..."
  ls -t test_output/pro_report_*.html | tail -n +11 | xargs -I {} rm {} 2>/dev/null
fi

echo "Done."
exit 0