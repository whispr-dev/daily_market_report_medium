#!/bin/bash
source /home/wofl/stonksenv/bin/activate
cd /home/wofl/whispr.dev/DailyStonks
exec gunicorn --bind 127.0.0.1:8081 unsubscribe_server:app
