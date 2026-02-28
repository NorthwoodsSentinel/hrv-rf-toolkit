#!/bin/zsh
# Every Breath You Take – double-click to launch
DIR="$(cd "$(dirname "$0")/every-breath-you-take" && pwd)"
cd "$DIR"
exec "$DIR/venv/bin/python" "$DIR/EBYT.py"
