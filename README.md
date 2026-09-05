# Pixel Operator for LibreSprite

A GUI that downsizes and reduces the colors of an image, then draws it as
pixel art into **LibreSprite** through automated mouse operations.
It works on a fresh PNG separate from your source image, with a transparent
canvas and a color-swatch row at the bottom.

The UI is localized into **English / 日本語 / 中文 / русский / 조선말**.
The OS language is detected automatically at startup, and you can switch it
anytime from the language menu at the top-right of the window (no restart
needed).

> This repository is the source. To run from a checkout see
> [Running from source](#running-from-source); for the portable build see
> [AppImage distribution](#appimage-distribution).

## Running from source

```sh
python3 /home/yomiplush/Projects/pixel-operator/app.py
```

Dependencies: Python 3, PySide6, Pillow, python-xlib, evdev, LibreSprite.
Launch it from your running desktop session (Wayland or X11).

## Usage

1. Click **Open image**, pick your source image, and adjust width, height and
   color count. 32×32 with 16 colors is a good starting point.
   - **Tone**: brightness / contrast / saturation / hue sliders change the
     look before quantization.
   - **Palette**: choose `Auto` (adaptive colors from the image) or a preset
     palette (DB32, PICO-8, Sweetie-16, GameBoy). Preset palettes map every
     pixel to the nearest fixed color.
   - **Generate with AI (Gemini)**: type a prompt (e.g. "cute fox", "chibi
     cat", "furry") and the app downloads a free-tier Gemini image, then feeds
     it through the same pipeline. Only free-tier models are offered so you do
     not risk charges. Get a free API key at Google AI Studio
     (aistudio.google.com/apikey); it is stored in
     `~/.config/pixel-operator/config.json` (0600) and never committed.
2. Click **Open transfer image in LibreSprite**. The upper part of this image
   is the drawing area; the bottom row holds the color swatches.
3. In LibreSprite show the transfer image at an integer zoom level that keeps
   the whole image visible. **About 3200% is recommended** (press `6`, fine-tune
   with `Ctrl++` / `Ctrl+-`). Then pick the pencil (`B`): 1 px brush, opacity
   255, normal ink, mirroring **OFF**, and clear any selection.
4. Press each coordinate button in the GUI, then within 5 s click LibreSprite
   and place the mouse on the pixel center of the image's
   **top-left / bottom-right** corner. The bottom-right is the very edge of the
   whole transfer image, **including the empty pixel to the right of the swatches**.
5. Tick the confirmation box and start. Within 5 s, give focus to the transfer
   image in LibreSprite.
6. Pixel Operator for LibreSprite uses the eyedropper (`I`) to pick each swatch and the pencil
   (`B`) to click every pixel for you.
7. When finished, save under a new name in LibreSprite. If you do not want the
   swatch row, trim the canvas to your original width/height. **Save PNG art**
   writes the finished image without the swatches directly.

## Stopping

- Press **ESC twice within 1 s** (holding it does not count as two presses).
- Switch to another window.
- Click the GUI's **Stop** button, or close the GUI.

Do not change zoom, scroll, tool, layer or tab during automatic operation.
Moving, resizing or defocusing the window stops the transfer.
If you customized shortcuts, restore LibreSprite's `I` = eyedropper and
`B` = pencil.
Pixels with alpha below 128 are skipped; the rest are drawn opaque. The aspect
ratio is preserved and margins stay transparent.
About 3200% gives a good balance for clicking pixel centers accurately; for
larger images, lower the zoom until everything fits.
If mozc/fcitx is left in full-width input mode, keys such as `B`/`I` are
swallowed by the IME and shortcuts stop working. Before each synthetic key
press the app checks the IME state and, when active, switches it back to
half-width (direct) input automatically.
The source image is never saved over or modified during processing.

## AppImage distribution

The Pixel Operator for LibreSprite application (Python + PySide6 + Pillow + python-xlib +
evdev) is bundled into a single AppImage that **auto-detects the runtime
environment** at launch.

### Bundled vs. external

| Item | Handling |
|---|---|
| Python 3, PySide6, Pillow, python-xlib, evdev, i18n data | **Bundled inside the AppImage** (~150–250 MB) |
| LibreSprite itself | **Not bundled** — the system-installed copy is used (LibreSprite is only distributed from AUR/source) |
| X11/Wayland, `niri`, `fcitx5`, `/dev/uinput` permissions | Checked by runtime auto-detection, with hints if missing |

### Auto-detection (`packaging/AppRun`)

On startup the AppImage detects the following and prints guidance before the
GUI opens:

1. Display server — `$WAYLAND_DISPLAY` / `$DISPLAY`
2. Whether `libresprite` is installed (with install hints if not)
3. IME (`fcitx5-remote`) presence — the half-width guard is applied by the app
4. Write access to `/dev/uinput` (needed for the synthetic keyboard; hints to
   join the `uinput` group or add a udev rule)
5. Qt platform — `wayland` when available, otherwise `xcb`

### Automatic builds (`.github/workflows/appimage.yml`)

- Triggered by pushing a `v*` tag, or manually via `workflow_dispatch`
- Builds on Ubuntu: unpacks a relocatable Python + PySide6 etc. into an AppDir
  and packages it with `appimagetool`
- Uploads the artifact to the GitHub Release assets automatically

Manual release example:

```sh
git tag v1.0.0 && git push origin v1.0.0
```

## Development & tests

```sh
cd /home/yomiplush/Projects/pixel-operator
python3 -m unittest -v
```

- `core.py` — image processing and coordinates
- `automation.py` — input & stop monitoring
- `app.py` — GUI
- `i18n.py` — localization (EN/JA/ZH/RU/KO)
- `desktop_check.py` — on-desktop diagnostics that only operate on new
  integration-transfer test documents
- `packaging/` — AppImage launcher and build script

The sample is an original sprite made for this project.
Used OSS: [Pillow](https://github.com/python-pillow/Pillow),
[PySide6](https://doc.qt.io/qtforpython-6/),
[python-xlib](https://github.com/python-xlib/python-xlib),
[LibreSprite](https://github.com/LibreSprite/LibreSprite). Libraries are not
redistributed; installed copies are used.
