"""Startup environment detection & start-menu registration used by the GUI.
Runs quickly and prints a small "neofetch-like" report so the app can show a
DONE popup after registering itself in the start menu."""
import os
import platform
import shutil
import sys
from pathlib import Path

from i18n import tr


def _distro():
    try:
        for line in Path('/etc/os-release').read_text(errors='ignore').splitlines():
            if line.startswith('PRETTY_NAME='):
                return line.split('=', 1)[1].strip().strip('"')
    except OSError:
        pass
    return platform.system()


def _display():
    if os.environ.get('WAYLAND_DISPLAY'):
        return 'Wayland'
    if os.environ.get('DISPLAY'):
        return 'X11'
    return tr('No display server found (need Wayland or X11).')


def _desktop():
    return os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION') or '-'


def _exec_path():
    """Return the path a start-menu entry should exec."""
    if os.environ.get('APPIMAGE'):
        return os.environ['APPIMAGE']
    return shutil.which('python3') + ' ' + str(Path(__file__).resolve().parent / 'app.py')


def register_launcher():
    """Create ~/.local/share/applications/pixel-operator.desktop."""
    apps = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'applications'
    apps.mkdir(parents=True, exist_ok=True)
    entry = apps/'pixel-operator.desktop'
    entry.write_text(
        '[Desktop Entry]\n'
        'Type=Application\n'
        'Name=Pixel Operator for LibreSprite\n'
        'Comment=' + tr('Convert an image to pixel art and draw it into LibreSprite') + '\n'
        'Exec=' + _exec_path() + '\n'
        'Path=' + str(Path(__file__).resolve().parent) + '\n'
        'Icon=applications-graphics\n'
        'Terminal=false\n'
        'Categories=Graphics;2DGraphics;\n', encoding='utf-8')
    return str(entry)


def environment_report():
    """Return (lines, ok) - human readable report lines for the DONE popup."""
    lines = []
    ok = True
    lines.append(f"  {platform.system()} / {_distro()}")
    lines.append(f"  Display: {_display()}  Desktop: {_desktop()}")
    libresprite = shutil.which('libresprite')
    if libresprite:
        lines.append('  ' + tr('LibreSprite found'))
    else:
        lines.append('  ' + tr('LibreSprite not found. Install it to use the transfer feature.'))
        ok = False
    ime = shutil.which('fcitx5-remote')
    if ime:
        lines.append('  ' + tr('Input method (IME) available'))
    else:
        lines.append('  ' + tr('No IME found; keyboard shortcuts may behave differently.'))
    uinput = os.access('/dev/uinput', os.W_OK)
    if uinput:
        lines.append('  ' + tr('/dev/uinput writable'))
    else:
        lines.append('  ' + tr('No write access to /dev/uinput. Join the uinput group or add a udev rule.'))
        ok = False
    try:
        entry = register_launcher()
        lines.append('  ' + tr('Registered to the start menu.') + '  (' + entry + ')')
    except Exception as exc:
        lines.append('  ' + tr('Launcher registration failed: {exc}').format(exc=exc))
        ok = False
    return lines, ok
