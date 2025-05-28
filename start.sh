#!/bin/bash

# Debug: Show all PORT-related environment variables
echo "🔍 Debug: Railway environment variables:"
env | grep -i port || echo "No PORT variables found"
env | grep -i railway || echo "No RAILWAY variables found"

# Use Railway's port or fallback to 8000
if [ -n "$PORT" ]; then
    echo "✅ Using Railway PORT: $PORT"
    BIND_PORT=$PORT
elif [ -n "$RAILWAY_PORT" ]; then
    echo "✅ Using RAILWAY_PORT: $RAILWAY_PORT"
    BIND_PORT=$RAILWAY_PORT
else
    echo "⚠️ No port found, using default 8000"
    BIND_PORT=8000
fi

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
echo "🚀 Starting gunicorn on port: $BIND_PORT"
gunicorn health_record_api.wsgi:application --bind 0.0.0.0:$BIND_PORT --workers 1 --timeout 120
