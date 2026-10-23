#!/bin/bash
# Mac / Linux launcher: double-click (Mac) or run "bash run.command".
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.11 or newer: https://www.python.org/downloads/"
  read -p "Press Enter to close..."
  exit 1
fi
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"; then
  echo "Python 3.11 or newer is required (current: $(python3 --version))."
  echo "Install a recent version: https://www.python.org/downloads/"
  read -p "Press Enter to close..."
  exit 1
fi
if [ ! -d .venv ]; then
  echo "Creating the environment (first run only)..."
  python3 -m venv .venv
fi
source .venv/bin/activate
if [ ! -f "$HOME/.streamlit/credentials.toml" ]; then
  mkdir -p "$HOME/.streamlit"
  printf '[general]\nemail = ""\n' > "$HOME/.streamlit/credentials.toml"
fi
echo "Installing packages (fast if already done)..."
python -m pip install -q -r requirements.txt
echo
echo "Starting the app... Close this window to stop it."
python -m streamlit run app.py
