#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "build_macos.sh must run on macOS (Darwin)." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
APP="${DIST}/Cash P&L.app"
CONTENTS="${APP}/Contents"
MACOS="${CONTENTS}/MacOS"
RES="${CONTENTS}/Resources"
APPDIR="${RES}/app"
ICON_PNG="${ROOT}/assets/icon.png"
ICONSET="${ROOT}/assets/icon.iconset"
ICNS="${RES}/app.icns"

if [[ ! -f "$ICON_PNG" ]]; then
  echo "missing ${ICON_PNG}" >&2
  exit 1
fi
if [[ ! -f "${ROOT}/app.py" ]] || [[ ! -f "${ROOT}/requirements.txt" ]] || [[ ! -f "${ROOT}/sample.xlsx" ]]; then
  echo "missing app.py, requirements.txt, or sample.xlsx" >&2
  exit 1
fi
if [[ ! -d "${ROOT}/src" ]] || [[ ! -d "${ROOT}/.streamlit" ]]; then
  echo "missing src/ or .streamlit/" >&2
  exit 1
fi

rm -rf "$APP"
mkdir -p "$MACOS" "$APPDIR/src" "$APPDIR/.streamlit"

cat >"${CONTENTS}/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>Cash P&amp;L</string>
  <key>CFBundleExecutable</key>
  <string>CashPnL</string>
  <key>CFBundleIconFile</key>
  <string>app.icns</string>
  <key>CFBundleIdentifier</key>
  <string>global.otterly.cashpnl</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>Cash P&amp;L</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundleVersion</key>
  <string>1.0.0</string>
  <key>LSMinimumSystemVersion</key>
  <string>12.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

cp "${ROOT}/scripts/macos_launch.sh" "${MACOS}/CashPnL"
chmod +x "${MACOS}/CashPnL" "${ROOT}/scripts/macos_launch.sh" "${ROOT}/scripts/build_macos.sh"

cp "${ROOT}/app.py" "${APPDIR}/app.py"
cp "${ROOT}/requirements.txt" "${APPDIR}/requirements.txt"
cp "${ROOT}/sample.xlsx" "${APPDIR}/sample.xlsx"
cp "${ROOT}/src/"*.py "${APPDIR}/src/"
cp "${ROOT}/.streamlit/"* "${APPDIR}/.streamlit/"

rm -rf "$ICONSET"
mkdir -p "$ICONSET"
sips -z 16 16 "$ICON_PNG" --out "${ICONSET}/icon_16x16.png" >/dev/null
sips -z 32 32 "$ICON_PNG" --out "${ICONSET}/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$ICON_PNG" --out "${ICONSET}/icon_32x32.png" >/dev/null
sips -z 64 64 "$ICON_PNG" --out "${ICONSET}/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$ICON_PNG" --out "${ICONSET}/icon_128x128.png" >/dev/null
sips -z 256 256 "$ICON_PNG" --out "${ICONSET}/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$ICON_PNG" --out "${ICONSET}/icon_256x256.png" >/dev/null
sips -z 512 512 "$ICON_PNG" --out "${ICONSET}/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$ICON_PNG" --out "${ICONSET}/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$ICON_PNG" --out "${ICONSET}/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$ICNS"
rm -rf "$ICONSET"

echo "Built: ${APP}"
echo "First launch: right-click Cash P&L.app → Open → Open."
