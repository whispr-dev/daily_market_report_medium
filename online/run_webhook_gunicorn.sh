#!/bin/bash
cd /home/wofl/whispr.dev/DailyStonks
source ~/stonksenv/bin/activate
exec gunicorn --bind 127.0.0.1:5001 paypal_webhook_server:app
