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