import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from core import prepare, Calibration, PRESET_PALETTES, _parse_palette, _tune, _nearest
import genai
from automation import EscapeLatch, Cancelled, draw, ime_state, ensure_half_width


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'input.png'
        im = Image.new('RGBA', (4, 4), (255, 0, 0, 255))
        im.putpixel((0, 0), (0, 0, 255, 0))
        im.putpixel((1, 0), (0, 255, 0, 255))
        im.save(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_reconstructs_image(self):
        art = prepare(self.path, 4, 4, 2)
        actual = Image.new('RGBA', art.image.size)
        for (color, points), swatch in zip(art.groups, art.swatches):
            self.assertEqual(art.template.getpixel(swatch), (*color, 255))
            for point in points:
                actual.putpixel(point, (*color, 255))
        self.assertEqual(actual.tobytes(), art.image.tobytes())
        self.assertEqual(sum(len(p) for _, p in art.groups), 15)
        self.assertEqual(art.template.crop((0, 0, 4, 4)).getbbox(), None)

    def test_calibration(self):
        c = Calibration((10, 20), (40, 80), (4, 7))
        self.assertEqual(c.point(2, 3), (30, 50))
        with self.assertRaises(ValueError):
            Calibration((40, 80), (10, 20), (4, 7)).validate()
        with self.assertRaises(ValueError):
            Calibration((0, 0), (30, 40), (4, 7)).validate()

    def test_escape_requires_two_presses_not_autorepeat(self):
        latch = EscapeLatch()
        self.assertFalse(latch.update(True, 0))
        self.assertFalse(latch.update(True, .1))
        self.assertFalse(latch.update(False, .2))
        self.assertTrue(latch.update(True, .3))

    def test_escape_timeout(self):
        latch = EscapeLatch()
        latch.update(True, 0)
        latch.update(False, .1)
        self.assertFalse(latch.update(True, 2))

    def test_cancel_before_first_input(self):
        art = prepare(self.path, 4, 4, 2)
        stop = threading.Event()
        stop.set()
        with patch('automation.Desktop') as desktop, patch('automation.watch_escape'):
            desktop.return_value.signature.return_value = (0, 0, 1000, 1000, 'test')
            with self.assertRaises(Cancelled):
                draw(art, Calibration((10, 10), (40, 70), art.template.size), 1, stop, lambda *a: None, countdown=0)
            desktop.return_value.click.assert_not_called()
            desktop.return_value.key.assert_not_called()

    def test_transparent_image_rejected(self):
        Image.new('RGBA', (4, 4)).save(self.path)
        with self.assertRaises(ValueError):
            prepare(self.path, 4, 4, 2)

    def test_tone_adjustment(self):
        self.assertEqual(_tune((200, 100, 50), brightness=-100), (0, 0, 0))
        self.assertEqual(_tune((128, 128, 128), saturation=100), (128, 128, 128))
        # hue shift rotates pure red towards green when +120 degrees.
        r, g, b = _tune((255, 0, 0), hue=120)
        self.assertGreater(g, 200)
        self.assertLess(r, 60)

    def test_nearest_palette(self):
        pal = _parse_palette(PRESET_PALETTES['GameBoy'])
        self.assertEqual(len(pal), 4)
        self.assertEqual(_nearest((255, 255, 255), pal), (155, 188, 15))
        self.assertEqual(_nearest((0, 0, 0), pal), (15, 56, 15))

    def test_preset_palette_limits_colors(self):
        art = prepare(self.path, 4, 4, 16, palette='GameBoy')
        used = {c for c, _ in art.groups}
        allowed = set(_parse_palette(PRESET_PALETTES['GameBoy']))
        self.assertTrue(used <= allowed)
        self.assertLessEqual(len(used), 4)

    def test_unknown_palette_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.path, 4, 4, 2, palette='Nope')

    @patch('automation.shutil.which', return_value='/usr/bin/fcitx5-remote')
    @patch('automation.subprocess.run')
    def test_ime_active_is_deactivated(self, run, _):
        run.return_value.stdout = '2\n'
        ensure_half_width()
        calls = [c.args[0] for c in run.call_args_list]
        self.assertIn(['fcitx5-remote'], calls)
        self.assertTrue(any(a == ['fcitx5-remote', '-c'] for a in calls))

    @patch('automation.shutil.which', return_value='/usr/bin/fcitx5-remote')
    @patch('automation.subprocess.run')
    def test_ime_inactive_is_left_alone(self, run, _):
        run.return_value.stdout = '1\n'
        ensure_half_width()
        calls = [c.args[0] for c in run.call_args_list]
        self.assertNotIn(['fcitx5-remote', '-c'], calls)

    def test_ime_state_parse(self):
        with patch('automation.subprocess.run') as run:
            run.return_value.stdout = '1\n'
            self.assertEqual(ime_state(), 1)
        with patch('automation.shutil.which', return_value=None):
            self.assertEqual(ime_state(), -1)

    def test_genai_config_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(genai, 'CONFIG_DIR', Path(tmp)), \
                patch.object(genai, 'CONFIG', Path(tmp)/'config.json'):
            genai.save_config(api_key='secret-key', model='gemini-2.5-flash-image')
            cfg = genai.load_config()
            self.assertEqual(cfg['api_key'], 'secret-key')
            self.assertEqual(cfg['model'], 'gemini-2.5-flash-image')
            mode = genai.CONFIG.stat().st_mode
            self.assertFalse(mode & 0o077)

    def test_genai_requires_key(self):
        with patch.object(genai, 'CONFIG', Path('/nonexistent/config.json')):
            with self.assertRaises(RuntimeError):
                genai.generate('a fox', api_key='', model='gemini-2.5-flash-image')


if __name__ == '__main__':
    unittest.main()
