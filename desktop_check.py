"""Local integration diagnostics, restricted to newly created operator documents."""
import sys
import os
import subprocess
import threading
import json
import time
from pathlib import Path
from automation import Desktop, draw
from core import prepare, Calibration

ROOT = Path(__file__).resolve().parent
mode = sys.argv[1]
if mode == 'open':
    art = prepare(ROOT/'sample.png', 16, 16, 4)
    art.template.save(ROOT/'integration-transfer.png')
    subprocess.run(['libresprite', str(ROOT/'integration-transfer.png')],
        env=dict(os.environ, SDL_VIDEODRIVER='x11'))
elif mode == 'inspect':
    d = Desktop()
    for w in d.root.query_tree().children:
        if w.get_wm_class():
            print(w.id, w.get_wm_class(), d.signature(w.id))
    print('pointer', d.root.query_pointer()._data)
    f = d.focused()
    print('focus', f.id if f else None)
    d.close()
elif mode in ('key', 'draw', 'shot', 'click', 'native'):
    d = Desktop()
    wid = int(sys.argv[2])
    sig = d.signature(wid)
    if 'integration-transfer' not in (sig[-1] or ''):
        raise RuntimeError('Only integration-transfer documents may be automated by this test.')
    windows = json.loads(subprocess.check_output(['niri', 'msg', '-j', 'windows']))
    target = next(w for w in windows if 'integration-transfer' in w['title'])
    subprocess.run(['niri', 'msg', 'action', 'focus-window', '--id', str(target['id'])], check=True)
    time.sleep(.3)
    if mode == 'native':
        from evdev import UInput, ecodes as E, AbsInfo
        caps = {E.EV_KEY: [E.BTN_LEFT, E.BTN_RIGHT, E.BTN_MIDDLE], E.EV_ABS: [
            (E.ABS_X, AbsInfo(0,0,65535,0,0,0)), (E.ABS_Y, AbsInfo(0,0,65535,0,0,0))]}
        with UInput(caps, name='Pixel Operator for LibreSprite Mouse') as mouse:
            time.sleep(1)
            mouse.write(E.EV_ABS,E.ABS_X,round(1526/1920*65535))
            mouse.write(E.EV_ABS,E.ABS_Y,round(607/1080*65535))
            mouse.syn()
            time.sleep(.3)
            print('pointer', d.root.query_pointer()._data)
            d.key('4', lambda: d.check(wid, sig))
            time.sleep(.5)
    elif mode == 'key':
        d.key(sys.argv[3], lambda: d.check(wid, sig))
    elif mode == 'click':
        d.click((int(sys.argv[3]), int(sys.argv[4])), lambda: d.check(wid, sig))
    elif mode == 'shot':
        from Xlib import X
        from PIL import Image
        w = d.d.create_resource_object('window', wid)
        g = w.get_geometry()
        raw = w.get_image(0, 0, g.width, g.height, X.ZPixmap, 0xffffffff)
        Image.frombytes('RGB', (g.width,g.height), raw.data, 'raw', 'BGRX').save('/tmp/pixel-operator-window.png')
    else:
        art = prepare(ROOT/'sample.png', 16,16,4)
        values = list(map(int, sys.argv[3:7]))
        c = Calibration(tuple(values[:2]), tuple(values[2:]), art.template.size)
        print(draw(art, c, wid, threading.Event(), lambda *a: print(*a), .05, countdown=0))
    d.close()
