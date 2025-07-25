# Email configuration
EMAIL_SENDER=DailyStonks@whispr.dev
EMAIL_PASSWORD=your-secure-password
EMAIL_SMTP=in-v3.mailjet.com
EMAIL_PORT=587

# PayPal configuration
PAYPAL_WEBHOOK_ID=your-webhook-id
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret

# Security
SECRET_KEY=your-secret-key
SECRET_SALT=your-secret-salt
ACCESS_TOKEN_SECRET=your-access-token-secret

# Background tasks (if using Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0