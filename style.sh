#!/usr/bin/env bash
set -euo pipefail

check=''
files='.'

print_usage() {
  printf "Usage: ./style.sh [-c] [-f <path>]"
}

while getopts 'cf:' flag; do
  case "${flag}" in
    c) check='true' ;;
    f) files="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if [ -z "$check" ]; then
    isort "$files" --check --diff
    black "$files" --check
else
    isort "$files"
    black "$files"
fi

flake8 "$files"
mypy "$files"
