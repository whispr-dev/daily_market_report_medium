location /paypal/webhook {
    proxy_pass http://localhost:8080/paypal/webhook;
}
location /paypal/cache-subscription {
    proxy_pass http://localhost:8080/paypal/cache-subscription;
}
location /static/ {
    alias /path/to/your/project/static/;
}
location = /subscribe {
    return 302 /static/subscribe.html;
}


gunicorn -w 2 -b 0.0.0.0:8080 paypal_webhook:app
