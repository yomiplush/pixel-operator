"""XWayland/X11 operator. Never sends input unless target owns focus."""
import shutil
import subprocess
import threading
import time
from Xlib import X, XK, display
from Xlib.ext import xtest
from evdev import UInput, ecodes
from i18n import tr


def ime_state():
    """Return fcitx5 state as int: 0 closed, 1 inactive, 2 active, -1 unknown."""
    if not shutil.which('fcitx5-remote'):
        return -1
    try:
        return int(subprocess.run(['fcitx5-remote'], capture_output=True, text=True,
            timeout=2).stdout.strip() or -1)
    except Exception:
        return -1


def ensure_half_width():
    """If the input method (mozc) is active, it intercepts Latin letters for
    kana conversion and LibreSprite shortcuts (B/I/zoom) stop working.
    Deactivate it so input returns to half-width direct entry."""
    try:
        if ime_state() == 2:
            subprocess.run(['fcitx5-remote', '-c'], capture_output=True, timeout=2)
            time.sleep(.1)
    except Exception:
        pass


class Cancelled(Exception):
    pass


class EscapeLatch:
    def __init__(self):
        self.down = False
        self.last = None

    def update(self, down, now):
        stop = False
        if down and not self.down:
            stop = self.last is not None and now-self.last <= 1.0
            self.last = now
        self.down = down
        return stop


class Desktop:
    def __init__(self):
        self.d = display.Display()
        self.root = self.d.screen().root
        self.keyboard = None
        if not self.d.has_extension('XTEST'):
            raise RuntimeError(tr('XTEST extension is not available.'))

    def close(self):
        if self.keyboard:
            self.keyboard.close()
        self.d.close()

    def owner(self, window):
        while hasattr(window, 'id') and window.id != self.root.id:
            if window.get_wm_class():
                return window
            window = window.query_tree().parent
        return None

    def focused(self):
        return self.owner(self.d.get_input_focus().focus)

    def capture(self):
        window = self.focused()
        if window is None or not any('libresprite' in s.lower() for s in window.get_wm_class()):
            raise ValueError(tr('Click LibreSprite first, then put the mouse on the image.'))
        p = self.root.query_pointer()
        return (p.root_x, p.root_y), window.id

    def signature(self, wid):
        w = self.d.create_resource_object('window', wid)
        g = w.get_geometry()
        pos = self.root.translate_coords(w, 0, 0)
        return (pos.x, pos.y, g.width, g.height, w.get_wm_name())

    def check(self, wid, signature):
        w = self.focused()
        if w is None or w.id != wid or self.signature(wid) != signature:
            raise Cancelled(tr('Stopped because focus, window position or the document changed.'))

    def key(self, name, guard):
        if self.keyboard is None:
            self.keyboard = UInput({ecodes.EV_KEY: list(range(1, 249))}, name='Pixel Operator for LibreSprite Keyboard')
            time.sleep(1)
        ensure_half_width()
        guard()
        code = getattr(ecodes, 'KEY_' + ('ESC' if name == 'Escape' else name.upper()))
        self.keyboard.write(ecodes.EV_KEY, code, 1)
        self.keyboard.syn()
        time.sleep(.1)
        self.keyboard.write(ecodes.EV_KEY, code, 0)
        self.keyboard.syn()
        time.sleep(.1)

    def click(self, point, guard):
        guard()
        xtest.fake_input(self.d, X.MotionNotify, x=point[0], y=point[1])
        self.d.sync()
        guard()
        xtest.fake_input(self.d, X.ButtonPress, 1)
        self.d.sync()
        time.sleep(.02)
        xtest.fake_input(self.d, X.ButtonRelease, 1)
        self.d.sync()

def watch_escape(stop, finished, reason):
    desktop = None
    try:
        desktop = Desktop()
        code = desktop.d.keysym_to_keycode(XK.XK_Escape)
        latch = EscapeLatch()
        while not finished.wait(.008):
            keys = desktop.d.query_keymap()
            if latch.update(bool(keys[code//8] & (1 << (code % 8))), time.monotonic()):
                reason.append(tr('Stopped: ESC pressed twice.'))
                stop.set()
                return
    except Exception as exc:
        reason.append(tr('Stop-key monitor failed: {exc}').format(exc=exc))
        stop.set()
    finally:
        if desktop:
            desktop.close()


def draw(art, calibration, wid, stop, progress, delay=.035, countdown=5):
    calibration.validate()
    desktop = Desktop()
    finished = threading.Event()
    reason = []
    monitor = threading.Thread(target=watch_escape, args=(stop, finished, reason), daemon=True)
    monitor.start()
    try:
        for second in range(countdown, 0, -1):
            progress(0, tr('{second} s to start. Click the LibreSprite transfer image.').format(second=second))
            if stop.wait(1):
                raise Cancelled(reason[-1] if reason else tr('Stopped.'))
        signature = desktop.signature(wid)
        x, y, w, h, _ = signature
        for point in (calibration.first, calibration.last):
            if not (x <= point[0] < x+w and y <= point[1] < y+h):
                raise ValueError(tr('The specified coordinates are outside the LibreSprite window.'))

        def guard():
            if stop.is_set():
                raise Cancelled(reason[-1] if reason else tr('Stopped.'))
            desktop.check(wid, signature)

        def pause():
            if stop.wait(delay):
                guard()

        guard()
        # Select pencil; user verifies 1px / opacity 255 in the preparation step.
        total = sum(len(points) for _, points in art.groups)
        done = 0
        for (_, points), swatch in zip(art.groups, art.swatches):
            desktop.key('i', guard)
            pause()
            desktop.click(calibration.point(*swatch), guard)
            pause()
            desktop.key('b', guard)
            pause()
            for point in points:
                desktop.click(calibration.point(*point), guard)
                pause()
                done += 1
                if done % 8 == 0 or done == total:
                    progress(round(done*100/total), tr('Drawing {done:,} / {total:,} px').format(done=done, total=total))
        return tr('Done: transferred {done:,} pixels by clicking.').format(done=done)
    finally:
        finished.set()
        monitor.join(timeout=2)
        desktop.close()
