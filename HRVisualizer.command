#!/bin/zsh
# HRVisualizer – double-click to launch, or drag a .txt file onto it in Finder
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
exec "$DIR/every-breath-you-take/venv/bin/python" "$DIR/hrvisualizer.py" "$@"
