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

exec gunicorn serve_http:app \
    "$EXTRA_OPTS" \
    --worker-class "$WORKER_CLASS" \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --preload
