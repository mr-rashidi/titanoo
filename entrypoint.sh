#!/bin/bash
set -e

export PORT=${PORT:-8080}

echo "Starting Services on Port: $PORT"

envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf

/app/start_xray.sh &

cd /app
python -m uvicorn app.main:app --host 127.0.0.1 --port 10000 --workers 1 &

python /app/watchdog.py &

nginx -g 'daemon off;'
