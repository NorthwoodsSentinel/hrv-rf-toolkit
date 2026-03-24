#!/bin/bash
# Quick launcher for RF test - handles venv activation automatically

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if duration argument provided
if [ $# -eq 0 ]; then
    echo "Starting full 15-minute Fisher & Lehrer RF test..."
    python test_fisher_lehrer_export.py
else
    echo "Starting $1-minute test..."
    python test_fisher_lehrer_export.py "$1"
fi
