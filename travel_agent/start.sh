#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$SCRIPT_DIR/backend"

echo "🚀  India Travel Agent — startup"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌  python3 not found. Please install Python 3.9+."
  exit 1
fi

# Create virtualenv if missing
VENV="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV" ]; then
  echo "📦  Creating virtual environment…"
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "📦  Installing dependencies…"
pip install -q -r "$BACKEND/requirements.txt"

echo ""
echo "✅  Starting server on http://localhost:5000"
echo "   Press Ctrl+C to stop."
echo ""

cd "$BACKEND"
python app.py
