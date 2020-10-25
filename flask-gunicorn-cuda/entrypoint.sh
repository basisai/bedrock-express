#!/bin/sh
set -eu

# Validate arguments
WORKERS="${WORKERS:-2}"
if [ "$WORKERS" -gt 0 ]; then
    echo "Starting gunicorn with $WORKERS workers"
else
    echo "Invalid argument: WORKERS=$WORKERS"
    exit 1
fi

# Add Bedrock model server directory to path
export PYTHONPATH="${PYTHONPATH:-}:/app"

exec gunicorn serve_http:app \
    "$EXTRA_OPTS" \
    --bind=":${BEDROCK_SERVER_PORT:-8080}" \
    --worker-class=gthread \
    --threads="$WORKERS" \
    --timeout=300 \
    --access-logfile - \
    --error-logfile - \
    --log-level "${LOG_LEVEL}" \
    --log-config /app/gunicorn_logging.conf \
    --capture-output
