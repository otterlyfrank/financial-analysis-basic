#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

URL="http://127.0.0.1:8501"
VENV=".venv"

alert() {
  echo "$1"
  /usr/bin/osascript - "$1" <<'OSA'
on run argv
  display dialog (item 1 of argv) with title "Cash P&L" buttons {"OK"} default button 1 with icon stop
end run
OSA
}

if [[ ! -f app.py ]] || [[ ! -f requirements.txt ]]; then
  alert "Keep Run Cash P&L.command in the unzipped folder (next to app.py), then double-click again."
  exit 1
fi

find_python() {
  local candidate
  for candidate in \
    python3.12 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 \
    /opt/homebrew/bin/python3.12 \
    /usr/local/bin/python3.12
  do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

PY="$(find_python || true)"
if [[ -z "${PY}" ]]; then
  alert "Install Python 3.12 from python.org (tick Add to PATH) and double-click again."
  exit 1
fi

if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "First run: creating .venv (can take a minute)…"
  "$PY" -m venv "$VENV"
fi

echo "Installing packages if needed…"
if ! "${VENV}/bin/python" -m pip install -r requirements.txt; then
  alert "Could not install Python packages. Check the Terminal window, then double-click again."
  exit 1
fi

if curl -fsS -o /dev/null --max-time 1 "${URL}/_stcore/health" 2>/dev/null; then
  open "$URL"
  exit 0
fi

"${VENV}/bin/python" -m streamlit run app.py \
  --server.address=127.0.0.1 \
  --server.headless=true \
  --browser.gatherUsageStats=false \
  &
ST_PID=$!
trap 'kill "$ST_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  if curl -fsS -o /dev/null --max-time 1 "${URL}/_stcore/health" 2>/dev/null; then
    open "$URL"
    wait "$ST_PID"
    exit $?
  fi
  if ! kill -0 "$ST_PID" 2>/dev/null; then
    alert "Cash P&L failed to start. Check the Terminal window."
    exit 1
  fi
  sleep 0.5
done

alert "Cash P&L timed out waiting for ${URL}."
exit 1
