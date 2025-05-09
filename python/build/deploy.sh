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