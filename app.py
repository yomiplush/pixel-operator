#!/usr/bin/env python3
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
import sys
import subprocess
import threading
import tempfile
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets as W
from core import prepare, Calibration
from automation import Desktop, draw, Cancelled
from i18n import LANGUAGES, tr, set_language

ROOT = Path(__file__).resolve().parent


class Worker(QtCore.QThread):
    progress = QtCore.Signal(int, str)
    result = QtCore.Signal(str)

    def __init__(self, art, calibration, wid, delay):
        super().__init__()
        self.args = art, calibration, wid
        self.delay = delay
        self.stop = threading.Event()

    def run(self):
        try:
            message = draw(*self.args, self.stop, self.progress.emit, self.delay)
        except Cancelled as exc:
            message = str(exc) + tr(' Partial drawing stays in LibreSprite.')
        except Exception as exc:
            message = tr('Operation stopped: {exc}').format(exc=exc)
        self.result.emit(message)


class Window(W.QMainWindow):
    def __init__(self):
        super().__init__()
        set_language(_lang_code())
        self.setWindowTitle('Pixel Operator for LibreSprite')
        self.source = None
        self.art = None
        self.points = {}
        self.worker = None
        self.capture_pending = False
        self.session = tempfile.TemporaryDirectory(prefix='pixel-operator-')
        self.setStyleSheet('''QWidget { background:#171c29; color:#e5eaf5; font-size:14px; }
            QPushButton { background:#303c54; border:1px solid #53627b; padding:9px; border-radius:6px; }
            QPushButton:hover { background:#435676; } QPushButton:disabled { color:#778196; }
            QSpinBox,QDoubleSpinBox { background:#232c40; padding:5px; }
            QProgressBar { border:1px solid #53627b; text-align:center; }
            QProgressBar::chunk { background:#3a998c; }
            QComboBox { background:#232c40; border:1px solid #53627b; padding:4px; }''')
        self._build()
        self.retranslate()
        self.optimize_geometry()

    # ---- UI construction (English strings; retranslate() localizes them) ----
    def _build(self):
        body = W.QWidget()
        self.setCentralWidget(body)
        self.layout = W.QVBoxLayout(body)
        self.title = W.QLabel('Pixel Operator for LibreSprite')
        self.title.setStyleSheet('font-size:22px; font-weight:bold; color:#8fdfca')
        self.layout.addWidget(self.title)
        self.subtitle = W.QLabel('')
        self.layout.addWidget(self.subtitle)
        langrow = W.QHBoxLayout()
        self.layout.addLayout(langrow)
        self.lang_label = W.QLabel('')
        langrow.addWidget(self.lang_label)
        self.lang = W.QComboBox()
        for code, name in LANGUAGES.items():
            self.lang.addItem(name, code)
        self.lang.setCurrentIndex(list(LANGUAGES).index(_lang_code()))
        self.lang.currentIndexChanged.connect(self._on_language)
        langrow.addWidget(self.lang)
        langrow.addStretch(1)
        self.controls = W.QWidget()
        controls = W.QVBoxLayout(self.controls)
        controls.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.controls)
        self.file_label = W.QLabel('')
        controls.addWidget(self.file_label)
        row = W.QHBoxLayout()
        controls.addLayout(row)
        self.open_button = self.button(row, '')
        self.open_button.clicked.connect(self.open_image)
        self.sample_button = self.button(row, '')
        self.sample_button.clicked.connect(self.sample)
        self.width, self.width_label = self.spin(row, '', 2, 256, 32, 'width')
        self.height, self.height_label = self.spin(row, '', 2, 256, 32, 'height')
        self.colors, self.colors_label = self.spin(row, '', 2, 64, 16, 'colors')
        self.dither = W.QCheckBox('')
        row.addWidget(self.dither)
        for control in (self.width, self.height, self.colors):
            control.valueChanged.connect(self.convert)
        self.dither.toggled.connect(self.convert)
        # Tone / palette controls
        tone = W.QGridLayout()
        controls.addLayout(tone)
        self.tone_controls = {}
        labels = [('Brightness', 'brightness', -100, 100), ('Contrast', 'contrast', -100, 100),
                  ('Saturation', 'saturation', -100, 100), ('Hue', 'hue', -180, 180)]
        for col, (key, name, lo, hi) in enumerate(labels):
            lab = W.QLabel('')
            lab.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            tone.addWidget(lab, 0, col)
            spin = W.QSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(0)
            spin.setSuffix('')
            tone.addWidget(spin, 1, col)
            self.tone_controls[name] = (lab, spin)
            spin.valueChanged.connect(self.convert)
        pal_label = W.QLabel('')
        tone.addWidget(pal_label, 0, 4)
        self.palette_label = pal_label
        self.palette = W.QComboBox()
        self.palette.addItem(tr('Auto'), 'auto')
        for code in ('DB32', 'PICO-8', 'Sweetie-16', 'GameBoy'):
            self.palette.addItem(code, code)
        tone.addWidget(self.palette, 1, 4)
        self.palette.currentIndexChanged.connect(self.convert)
        self.preview = W.QLabel('')
        self.preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(230)
        self.preview.setStyleSheet('background:#242d40; border-radius:8px')
        controls.addWidget(self.preview)
        self.stats = W.QLabel('')
        controls.addWidget(self.stats)
        row = W.QHBoxLayout()
        controls.addLayout(row)
        self.export_button = self.button(row, '')
        self.export_button.clicked.connect(self.export)
        self.template_button = self.button(row, '')
        self.template_button.clicked.connect(self.open_template)
        self.instructions = W.QLabel('')
        self.instructions.setWordWrap(True)
        controls.addWidget(self.instructions)
        row = W.QHBoxLayout()
        controls.addLayout(row)
        self.first_button = self.button(row, '')
        self.first_button.clicked.connect(lambda: self.capture('first'))
        self.last_button = self.button(row, '')
        self.last_button.clicked.connect(lambda: self.capture('last'))
        self.coords = W.QLabel('')
        controls.addWidget(self.coords)
        row = W.QHBoxLayout()
        controls.addLayout(row)
        self.delay_label = W.QLabel('')
        row.addWidget(self.delay_label)
        self.delay = W.QDoubleSpinBox()
        self.delay.setRange(.02, .5)
        self.delay.setDecimals(3)
        self.delay.setValue(.05)
        row.addWidget(self.delay)
        row.addStretch(1)
        self.ready = W.QCheckBox('')
        controls.addWidget(self.ready)
        self.start_button = self.button(controls, '')
        self.start_button.clicked.connect(self.start)
        self.bar = W.QProgressBar()
        self.layout.addWidget(self.bar)
        self.status = W.QLabel('')
        self.status.setWordWrap(True)
        self.layout.addWidget(self.status)
        self.stop_button = self.button(self.layout, '')
        self.stop_button.setStyleSheet('background:#833d52; padding:12px; font-weight:bold')
        self.stop_button.clicked.connect(self.stop)
        self.layout.addStretch(1)

    def optimize_geometry(self):
        """Fit the window to the current screen so nothing is cut off."""
        screen = self.screen() or W.QApplication.primaryScreen()
        area = screen.availableGeometry() if screen else None
        target = QtCore.QSize(760, 860)
        if area is not None:
            margin = 16
            target.setWidth(min(target.width(), area.width() - margin))
            target.setHeight(min(target.height(), area.height() - margin))
        self.resize(target.expandedTo(QtCore.QSize(560, 400)))
        scroll = W.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(W.QFrame.Shape.NoFrame)
        scroll.setWidget(self.centralWidget())
        scroll.setStyleSheet('QScrollArea { background:transparent; border:none; }')
        self.setCentralWidget(scroll)

    def retranslate(self):
        self.subtitle.setText(tr('Convert an image to pixel art and draw it into LibreSprite'))
        self.lang_label.setText(tr('Language'))
        self.file_label.setText(tr('Choose an image (PNG / JPEG / WebP / BMP / GIF)'))
        self.open_button.setText(tr('Open image'))
        self.sample_button.setText(tr('Sample'))
        self.width_label.setText(tr('Width'))
        self.height_label.setText(tr('Height'))
        self.colors_label.setText(tr('Colors'))
        self.dither.setText(tr('Dither'))
        self.tone_controls['brightness'][0].setText(tr('Brightness'))
        self.tone_controls['contrast'][0].setText(tr('Contrast'))
        self.tone_controls['saturation'][0].setText(tr('Saturation'))
        self.tone_controls['hue'][0].setText(tr('Hue'))
        self.palette_label.setText(tr('Palette'))
        self.palette.setItemText(self.palette.findData('auto'), tr('Auto'))
        self.preview.setText(tr('Preview'))
        self.export_button.setText(tr('Save PNG art'))
        self.template_button.setText(tr('Open transfer image in LibreSprite'))
        self.instructions.setText(tr('Instructions'))
        self.first_button.setText(tr('Specify top-left center (5 s)'))
        self.last_button.setText(tr('Specify bottom-right center (5 s)'))
        self.delay_label.setText(tr('Delay per operation (s)'))
        self.ready.setText(tr('Confirmed transfer image, 1 px pencil and zoom'))
        self.start_button.setText(tr('Start automatic transfer in 5 s'))
        self.stop_button.setText(tr('Stop automatic operation'))
        self.refresh_status()

    def refresh_status(self):
        if self.points:
            parts = []
            for kind in ('first', 'last'):
                name = tr('top-left') if kind == 'first' else tr('bottom-right')
                parts.append(f'{name}: {self.points[kind][0]}')
            self.coords.setText(' / '.join(parts))
        elif not self.art:
            self.coords.setText(tr('Coordinates not set'))
        else:
            self.coords.setText(tr('Coordinates not set (re-specify after changing the image)'))
        if self.art:
            count = sum(len(p) for _, p in self.art.groups)
            self.stats.setText(tr('{w} x {h} px ・ {n} colors ・ {clicks:,} clicks + picks ・ alpha<128 skipped')
                .format(w=self.art.image.width, h=self.art.image.height, n=len(self.art.groups), clicks=count))
        if not self.worker or not self.worker.isRunning():
            self.status.setText(tr('Idle - the source image is never modified.'))

    def _on_language(self):
        set_language(self.lang.currentData())
        self.retranslate()

    def button(self, layout, text):
        button = W.QPushButton(text)
        layout.addWidget(button)
        return button

    def spin(self, layout, label, lo, hi, value, kind):
        lab = W.QLabel(label)
        layout.addWidget(lab)
        control = W.QSpinBox()
        control.setRange(lo, hi)
        control.setValue(value)
        layout.addWidget(control)
        return control, lab

    def error(self, exc):
        W.QMessageBox.warning(self, 'Pixel Operator for LibreSprite', str(exc))

    def open_image(self):
        path, _ = W.QFileDialog.getOpenFileName(self, tr('Source image'), str(Path.home()/'Pictures'),
            tr('Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;All files (*)'))
        if path:
            self.source = path
            self.convert()

    def sample(self):
        self.source = str(ROOT/'sample.png')
        self.convert()

    def convert(self):
        if not self.source:
            return
        self.art = None
        self.points.clear()
        self.ready.setChecked(False)
        self.refresh_status()
        try:
            self.art = prepare(self.source, self.width.value(), self.height.value(),
                self.colors.value(), self.dither.isChecked(),
                brightness=self.tone_controls['brightness'][1].value(),
                contrast=self.tone_controls['contrast'][1].value(),
                saturation=self.tone_controls['saturation'][1].value(),
                hue=self.tone_controls['hue'][1].value(),
                palette=self.palette.currentData())
            self.file_label.setText(Path(self.source).name)
            data = self.art.image.tobytes()
            qimage = QtGui.QImage(data, self.art.image.width, self.art.image.height,
                self.art.image.width*4, QtGui.QImage.Format.Format_RGBA8888).copy()
            pixmap = QtGui.QPixmap.fromImage(qimage)
            self.preview.setPixmap(pixmap.scaled(500, 230, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.FastTransformation))
            count = sum(len(p) for _, p in self.art.groups)
            self.stats.setText(tr('{w} x {h} px ・ {n} colors ・ {clicks:,} clicks + picks ・ alpha<128 skipped')
                .format(w=self.art.image.width, h=self.art.image.height, n=len(self.art.groups), clicks=count))
        except Exception as exc:
            self.error(exc)

    def export(self):
        if not self.art:
            return self.error(tr('Choose a source image first.'))
        path, _ = W.QFileDialog.getSaveFileName(self, tr('Save pixel-art PNG'), 'pixel-art.png', 'PNG (*.png)')
        if path:
            try:
                self.art.image.save(path, format='PNG')
                self.status.setText(tr('Saved: {path}').format(path=path))
            except Exception as exc:
                self.error(exc)

    def open_template(self):
        if not self.art:
            return self.error(tr('Choose a source image first.'))
        try:
            import uuid
            path = Path(self.session.name)/f'transfer-{uuid.uuid4().hex[:8]}.png'
            self.art.template.save(path)
            env = dict(os.environ, SDL_VIDEODRIVER='x11')
            subprocess.Popen(['libresprite', str(path)], env=env)
            self.points.clear()
            self.refresh_status()
            self.status.setText(tr('Transfer image {w} x {h} px. The bottom row holds the color swatches.')
                .format(w=self.art.template.width, h=self.art.template.height))
        except Exception as exc:
            self.error(exc)

    def capture(self, which):
        if not self.art:
            return self.error(tr('Choose a source image first.'))
        self.controls.setEnabled(False)
        self.capture_pending = True
        self.status.setText(tr('Within 5 s click LibreSprite, then place the mouse on the requested position.'))
        QtCore.QTimer.singleShot(5000, lambda: self.capture_done(which))

    def capture_done(self, which):
        self.capture_pending = False
        desktop = None
        try:
            desktop = Desktop()
            point, wid = desktop.capture()
            other = 'last' if which == 'first' else 'first'
            if other in self.points and self.points[other][1] != wid:
                self.points.clear()
                raise ValueError(tr('Specify the two points in the same LibreSprite window.'))
            self.points[which] = point, wid
            self.refresh_status()
            self.status.setText(tr('Coordinates recorded.'))
        except Exception as exc:
            self.error(exc)
        finally:
            if desktop:
                desktop.close()
            self.controls.setEnabled(True)

    def start(self):
        try:
            if not self.art or len(self.points) != 2 or not self.ready.isChecked():
                raise ValueError(tr('A source image, two coordinate points and the ready checkbox are required.'))
            calibration = Calibration(self.points['first'][0], self.points['last'][0], self.art.template.size)
            calibration.validate()
            self.worker = Worker(self.art, calibration, self.points['first'][1], self.delay.value())
            self.worker.progress.connect(self.progress)
            self.worker.result.connect(self.on_result)
            self.worker.finished.connect(self.on_finished)
            self.controls.setEnabled(False)
            self.bar.setValue(0)
            self.worker.start()
        except Exception as exc:
            self.error(exc)

    def on_result(self, message):
        self.status.setText(message)

    def on_finished(self):
        self.controls.setEnabled(True)

    def progress(self, value, text):
        self.bar.setValue(value)
        self.status.setText(text)

    def stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop.set()

    def closeEvent(self, event):
        self.stop()
        if self.worker and self.worker.isRunning():
            self.worker.wait(3000)
            if self.worker.isRunning():
                event.ignore()
                return
        event.accept()


def _lang_code():
    from i18n import detect
    code = detect()
    if code not in LANGUAGES:
        code = 'en'
    return code


if __name__ == '__main__':
    from i18n import set_language_from_env
    set_language_from_env()
    app = W.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
