#!/usr/bin/env bash
set -euo pipefail

exit_code=0

# Defaults to all targets
if [[ -z "${APP+x}" ]]; then
    targets=(flask-gunicorn fastapi-gunicorn)
else
    targets=("$APP")
fi

# Defaults to all frameworks
if [[ -z "${MODEL+x}" ]]; then
    frameworks=(lightgbm torchvision tf-vision transformers tf-transformers)
else
    frameworks=("$MODEL")
fi

# Append new server images to this list
for app in "${targets[@]}"; do
    ./style.sh -cf "$app"
    # Append new ML framework to this list
    for model in "${frameworks[@]}"; do
        ./style.sh -cf "tests/$model/model-server"

        echo "Testing $app:$model..."
        export APP="$app"
        export MODEL="$model"

        # Save exit code for use later
        docker compose -f tests/docker-compose.yml -p "$app" up \
        --build --abort-on-container-exit --always-recreate-deps || exit_code=$?

        # Clean up containers
        docker compose -f tests/docker-compose.yml -p "$app" down -v --remove-orphans

        # Abort early on failure
        if [[ $exit_code -ne 0 ]]; then
            exit $exit_code
        fi
    done
done

echo "All tests passed!"
