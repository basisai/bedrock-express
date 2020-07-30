#!/usr/bin/env bash
set -euo pipefail

isort .
black .
flake8
