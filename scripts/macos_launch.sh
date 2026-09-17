#!/bin/bash
set -euo pipefail

export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

SELF="$(cd "$(dirname "$0")" && pwd)"
if [[ -d "$SELF/../Resources/app" ]]; then
  BUNDLE_APP="$(cd "$SELF/../Resources/app" && pwd)"
elif [[ -f "$SELF/../app.py" ]]; then
  BUNDLE_APP="$(cd "$SELF/.." && pwd)"
else
  BUNDLE_APP=""
fi

SUPPORT="${HOME}/Library/Application Support/CashPnL"
VENV="${SUPPORT}/venv"
REQ_STAMP="${SUPPORT}/requirements.sha256"
LOG="${SUPPORT}/launch.log"
URL="http://127.0.0.1:8501"

mkdir -p "$SUPPORT"

alert() {
  /usr/bin/osascript - "$1" <<'OSA'
on run argv
  display dialog (item 1 of argv) with title "Cash P&L" buttons {"OK"} default button 1 with icon stop
end run
OSA
}

if [[ -z "$BUNDLE_APP" ]]; then
  alert "Cash P&L is missing its app files."
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
  alert "Python 3.12 is required. Install it from python.org, tick Add Python to PATH, then open Cash P&L again."
  exit 1
fi

cp "$BUNDLE_APP/app.py" "$SUPPORT/app.py"
cp "$BUNDLE_APP/requirements.txt" "$SUPPORT/requirements.txt"
cp "$BUNDLE_APP/sample.xlsx" "$SUPPORT/sample.xlsx"
rm -rf "$SUPPORT/src"
mkdir -p "$SUPPORT/src"
cp "$BUNDLE_APP/src/"*.py "$SUPPORT/src/"
rm -rf "$SUPPORT/.streamlit"
mkdir -p "$SUPPORT/.streamlit"
cp "$BUNDLE_APP/.streamlit/"* "$SUPPORT/.streamlit/" 2>/dev/null || true

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PY" -m venv "$VENV"
fi

REQ_HASH="$(/usr/bin/shasum -a 256 "$SUPPORT/requirements.txt" | awk '{print $1}')"
NEED_PIP=0
if [[ ! -x "$VENV/bin/streamlit" ]]; then
  NEED_PIP=1
elif [[ ! -f "$REQ_STAMP" ]] || [[ "$(cat "$REQ_STAMP")" != "$REQ_HASH" ]]; then
  NEED_PIP=1
fi

if [[ "$NEED_PIP" -eq 1 ]]; then
  if ! "$VENV/bin/python" -m pip install -r "$SUPPORT/requirements.txt" >>"$LOG" 2>&1; then
    alert "Could not install Python packages. See ${LOG}"
    exit 1
  fi
  printf '%s\n' "$REQ_HASH" >"$REQ_STAMP"
fi

export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
cd "$SUPPORT"

if curl -fsS -o /dev/null --max-time 1 "${URL}/_stcore/health" 2>/dev/null; then
  open "$URL"
  exit 0
fi

"$VENV/bin/streamlit" run app.py \
  --server.address 127.0.0.1 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  >>"$LOG" 2>&1 &
ST_PID=$!
trap 'kill "$ST_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  if curl -fsS -o /dev/null --max-time 1 "${URL}/_stcore/health" 2>/dev/null; then
    open "$URL"
    wait "$ST_PID"
    exit $?
  fi
  if ! kill -0 "$ST_PID" 2>/dev/null; then
    alert "Cash P&L failed to start. See ${LOG}"
    exit 1
  fi
  sleep 0.5
done

alert "Cash P&L timed out waiting for ${URL}. See ${LOG}"
exit 1
