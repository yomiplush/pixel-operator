#!/usr/bin/env bash
# Local AppImage build (reference implementation).
# Normally run in CI (.github/workflows/appimage.yml); this mirrors its steps
# so you can reproduce a build on any Linux box with wget + docker-free tools.
set -euo pipefail
cd "$(dirname "$0")/.."

PYVER="3.12.8"
REL="20250115"
TAG="cpython-${PYVER}+${REL}-x86_64-unknown-linux-gnu-install_only"
URL="https://github.com/astral-sh/python-build-standalone/releases/download/${REL}/${TAG}.tar.gz"

echo "[1/6] fetch relocatable Python ${PYVER}"
wget -q "$URL" -O /tmp/cpython.tar.gz
rm -rf /tmp/po-python && mkdir -p /tmp/po-python
tar -xzf /tmp/cpython.tar.gz -C /tmp/po-python --strip-components=1

echo "[2/6] install deps"
/tmp/po-python/bin/python3 -m pip install --no-cache-dir --upgrade pip
/tmp/po-python/bin/python3 -m pip install --no-cache-dir PySide6==6.7.3 Pillow python-xlib evdev

echo "[3/6] assemble AppDir"
APP=dist/Pixel-Operator.AppDir
rm -rf "$APP" && mkdir -p "$APP/usr/bin" "$APP/usr/lib/python" "$APP/usr/lib/pixel-operator"
cp -a /tmp/po-python/. "$APP/usr/lib/python/"
cp app.py automation.py core.py desktop_check.py i18n.py make_sample.py \
   test_core.py sample.png LICENSE README.md "$APP/usr/lib/pixel-operator/"

mkdir -p "$APP/usr/share/applications" "$APP/usr/share/icons/hicolor/256x256/apps"
cat > "$APP/pixel-operator.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Pixel Operator
Comment=Convert an image to pixel art and draw it into LibreSprite
Exec=pixel-operator
Icon=pixel-operator
Terminal=false
Categories=Graphics;2DGraphics;
EOF
cp "$APP/pixel-operator.desktop" "$APP/usr/share/applications/"
python3 - <<'PY'
from PIL import Image
Image.new('RGBA',(256,256),(63,153,140,255)).save(
    'dist/Pixel-Operator.AppDir/usr/share/icons/hicolor/256x256/apps/pixel-operator.png')
PY
cp "$APP/usr/share/icons/hicolor/256x256/apps/pixel-operator.png" "$APP/"

echo "[4/6] write AppRun"
cat > "$APP/AppRun" <<'EOF'
#!/bin/sh
SELF="$(readlink -f "$0")"
APPDIR="$(dirname "$SELF")"
PY="$APPDIR/usr/lib/python"
export PYTHONHOME="$PY"
export PYTHONPATH="$PY/lib/python3.12/site-packages:$APPDIR/usr/lib/pixel-operator"
export LD_LIBRARY_PATH="$PY/lib:$LD_LIBRARY_PATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$PY/lib/python3.12/site-packages/PySide6/Qt/plugins"
export QT_PLUGIN_PATH="$PY/lib/python3.12/site-packages/PySide6/Qt/plugins"
if [ -z "$WAYLAND_DISPLAY" ] && [ -z "$DISPLAY" ]; then
  echo "No display server found (need Wayland or X11)." >&2; exit 1
fi
command -v libresprite >/dev/null 2>&1 || \
  echo "NOTE: LibreSprite not found. Install it to use the transfer feature." >&2
[ -w /dev/uinput ] || \
  echo "NOTE: /dev/uinput is not writable. Join the 'uinput' group or add a udev rule." >&2
if [ -n "$WAYLAND_DISPLAY" ]; then
  export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland}"
else
  export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
fi
cd "$APPDIR/usr/lib/pixel-operator" || exit 1
exec "$PY/bin/python3" app.py "$@"
EOF
chmod +x "$APP/AppRun"

echo "[5/6] fetch appimagetool"
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
  -O /tmp/appimagetool && chmod +x /tmp/appimagetool

echo "[6/6] package"
ARCH=x86_64 /tmp/appimagetool --appimage-extract-and-run \
  "$APP" dist/Pixel-Operator-x86_64.AppImage
ls -lh dist/Pixel-Operator-x86_64.AppImage
echo "done"
