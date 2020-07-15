#!/bin/sh
set -eu

# LightGBM model expects an array of 66 numbers as input
BODY="[$(seq -s, 0 65)66]"
COUNT=4

# Send 4 prediction requests in a row
for _ in $(seq $COUNT); do
    # Verify each prediction response
    curl -sS "${HOST:-localhost}:8080" \
        -H "content-type: application/json" \
        -d "$BODY" | grep '"result":0.9793770021409441'
    sleep 0.5
done

# Verify that metrics sum up correctly
curl -sS "${HOST:-localhost}:8080/metrics" | grep "inference_value_count $COUNT.0"
