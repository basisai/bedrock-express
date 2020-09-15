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

EXTRA_OPTS=""
if [ "$WORKERS" -gt 1 ]; then
    # Try not to override user defined variable
    export prometheus_multiproc_dir="${prometheus_multiproc_dir:-/tmp}"
    EXTRA_OPTS="--config gunicorn_config.py"
fi

# Add Bedrock model server directory to path
export PYTHONPATH="${PYTHONPATH:-}:/app"

exec gunicorn serve_http:app \
    "$EXTRA_OPTS" \
    --bind=":${BEDROCK_SERVER_PORT:-8080}" \
    --worker-class=gthread \
    --workers="$WORKERS" \
    --timeout=300 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level "${LOG_LEVEL}" \
    --log-config /app/gunicorn_logging.conf \
    --capture-output
