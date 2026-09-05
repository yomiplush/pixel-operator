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
APP=dist/Pixel-Operator-for-LibreSprite.AppDir
rm -rf "$APP" && mkdir -p "$APP/usr/bin" "$APP/usr/lib/python" "$APP/usr/lib/pixel-operator"
cp -a /tmp/po-python/. "$APP/usr/lib/python/"
cp app.py automation.py core.py desktop_check.py i18n.py make_sample.py \
   test_core.py sample.png LICENSE README.md "$APP/usr/lib/pixel-operator/"

mkdir -p "$APP/usr/share/applications" "$APP/usr/share/icons/hicolor/256x256/apps"
cp packaging/pixel-operator.desktop "$APP/pixel-operator.desktop"
cp packaging/pixel-operator.desktop "$APP/usr/share/applications/"
python3 -c "from PIL import Image; Image.new('RGBA',(256,256),(63,153,140,255)).save('dist/Pixel-Operator-for-LibreSprite.AppDir/usr/share/icons/hicolor/256x256/apps/pixel-operator.png')"
cp "$APP/usr/share/icons/hicolor/256x256/apps/pixel-operator.png" "$APP/"

echo "[4/6] install AppRun"
chmod +x packaging/AppRun
cp packaging/AppRun "$APP/AppRun"

echo "[5/6] fetch appimagetool"
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
  -O /tmp/appimagetool && chmod +x /tmp/appimagetool

echo "[6/6] package"
ARCH=x86_64 /tmp/appimagetool --appimage-extract-and-run \
  "$APP" dist/Pixel-Operator-for-LibreSprite-x86_64.AppImage
ls -lh dist/Pixel-Operator-for-LibreSprite-x86_64.AppImage
echo "done"
