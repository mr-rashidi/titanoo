#!/bin/bash
set -e

if [ ! -f /data/paths.json ]; then
    python /app/genpaths.py
fi

source_paths=$(cat /data/paths.json | python -c "import sys, json; print(json.load(sys.stdin))")

python /app/generate_config.py

xray run -c /etc/xray/config.json
