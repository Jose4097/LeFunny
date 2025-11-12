"""
LeFunny.py
Desktop overlay app with random jumpscares (PyQt6)
"""

import sys
import random
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, QUrl, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QSpinBox,
    QFormLayout,
    QComboBox,
)
from PyQt6.QtGui import QMovie, QIcon, QPixmap, QAction
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QCheckBox


# ---------- Resource Helper ----------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(relative_path)


ASSETS_DIR = resource_path("assets")

# ---------- Config ----------
MIN_INTERVAL_SEC = 60
MAX_INTERVAL_SEC = 7200
SHOW_DURATION_MS = 700  # default if no override

# Per-jumpscare duration (ms)
# If you want to add more jumpscares, add them to the assets folder
# and specify their duration here.
JUMPSCARE_DURATIONS = {
    "Foxy": 700,
    "Skeleton": 1200,
    "Vibrations": 700,
    "Max": 7500,
    "Aatrox": 4000,
    "Ronaldo": 1600,
    "Earthbound": 4500,
    "Golem": 7000,
    "Luffy": 17000,
    "Sugarcoat": 500,
    "Wilkman": 500,
    "Minos": 700,
    "Lobotomy": 400,
    "Comboios": 2000,
    "Pluh": 700,
    "Prowler": 2150,
    "Twitch": 3000,
    "Tien": 13600,
    "Smoke": 300,
    "Fish": 300,
    "Cheese": 2100,
    "James": 1000,
    "LTG": 1000,
    "Regular": 4800,
    "Michael": 500,
    "Lobster": 2000,
    "Udrea": 4000,
    "Soccer": 12500,
    "Bird": 1500,
    "Osaka": 1500,
}


# ---------- Overlay ----------
class OverlayWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self.movie = None
        self.frames = []
        self.frame_index = 0
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._advance_frame)

    def load_animation(self, gif_path=None, frames_dir=None):
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
        if self.frame_timer.isActive():
            self.frame_timer.stop()
        self.frames = []
        self.frame_index = 0
        self.label.clear()
        self.repaint()

        if gif_path and gif_path.exists():
            self.movie = QMovie(str(gif_path))
            if not self.movie.isValid():
                print("Invalid GIF:", gif_path)
                self.movie = None
            else:
                screen = QApplication.primaryScreen().availableGeometry()
                self.movie.setScaledSize(QSize(screen.width(), screen.height()))
                self.label.setMovie(self.movie)
                return
        # PNG fallback
        if frames_dir and frames_dir.exists():
            pngs = sorted(frames_dir.glob("*.png"))
            if not pngs:
                return
            self.frames = [QPixmap(str(p)) for p in pngs]
            self.label.setPixmap(self.frames[0])

    def _advance_frame(self):
        if not self.frames:
            return
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.stop()
            return
        self.label.setPixmap(self.frames[self.frame_index])

    def play(self, duration_ms):
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width(), screen.height())
        self.move(screen.x(), screen.y())
        self.show()
        if self.movie:
            self.movie.start()
            QTimer.singleShot(duration_ms, self.stop)
        elif self.frames:
            self.frame_index = 0
            self.label.setPixmap(self.frames[0])
            self.frame_timer.start(1000 // 24)
            QTimer.singleShot(duration_ms, self.stop)

    def stop(self):
        if self.movie:
            self.movie.stop()
        if self.frame_timer.isActive():
            self.frame_timer.stop()
        self.label.clear()
        self.repaint()
        self.hide()


# ---------- App ----------
class JumpscareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Le Funny - Control")
        self.setFixedSize(360, 180)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.overlay = OverlayWindow()
        self.sound = QSoundEffect(self)
        self.current_jumpscare = None  # Track current jumpscare name
        # Set volume to max; You can change it between 0.0 and 1.0
        try:
            self.sound.setVolume(1.0)
        except Exception:
            pass
        self.cycle_timer = QTimer(self)
        self.cycle_timer.setSingleShot(True)
        self.cycle_timer.timeout.connect(self._do_jumpscare)

        # UI
        self.min_spin = QSpinBox()
        self.min_spin.setRange(5, 86400)
        self.min_spin.setValue(MIN_INTERVAL_SEC)
        self.max_spin = QSpinBox()
        self.max_spin.setRange(5, 86400)
        self.max_spin.setValue(MAX_INTERVAL_SEC)
        form = QFormLayout()
        form.addRow("Min interval (s):", self.min_spin)
        form.addRow("Max interval (s):", self.max_spin)

        # If you want to add more jumpscares, add them to the assets folder and add the name here.
        self.jumpscare_select = QComboBox()
        self.jumpscare_map = {}
        desired_order = [
            "Foxy",
            "Skeleton",
            "Vibrations",
            "Max",
            "Aatrox",
            "Ronaldo",
            "Earthbound",
            "Golem",
            "Luffy",
            "Sugarcoat",
            "Wilkman",
            "Minos",
            "Lobotomy",
            "Comboios",
            "Pluh",
            "Prowler",
            "Twitch",
            "Tien",
            "Smoke",
            "Fish",
            "Cheese",
            "James",
            "LTG",
            "Regular",
            "Michael",
            "Lobster",
            "Udrea",
            "Soccer",
            "Bird",
            "Osaka",
        ]
        for name in desired_order:
            subdir = ASSETS_DIR / name
            gif = subdir / "animation.gif"
            wav = subdir / "sound.wav"
            if gif.exists() and wav.exists():
                self.jumpscare_select.addItem(name)
                self.jumpscare_map[name] = (gif, wav)
        form.addRow("Jumpscare:", self.jumpscare_select)

        self.random_checkbox = QCheckBox("Random jumpscare each time")
        form.addRow("", self.random_checkbox)

        start_btn = QPushButton("Start")
        stop_btn = QPushButton("Stop")
        try_btn = QPushButton("Try me")
        start_btn.clicked.connect(self.start)
        stop_btn.clicked.connect(self.stop)
        try_btn.clicked.connect(self.try_jumpscare)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(try_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(btn_layout)

        self.status_label = QLabel("Status: OFF")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: red; font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(self.status_label)

        ICON_PATH = ASSETS_DIR / "icon.ico"
        tray_icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon()
        self.tray = QSystemTrayIcon(tray_icon)
        self.setWindowIcon(tray_icon)
        menu = QMenu()
        act_show = QAction("Show Control", menu)
        act_quit = QAction("Quit", menu)
        act_show.triggered.connect(self.show)
        act_quit.triggered.connect(self._really_quit)
        menu.addAction(act_show)
        menu.addAction(act_quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def _load_selected_jumpscare(self):
        if not self.jumpscare_map:
            print("No jumpscares available")
            return SHOW_DURATION_MS

        try:
            # Use the pre-selected jumpscare or get one from the UI
            name = self.current_jumpscare or self.jumpscare_select.currentText()
            if not name or name not in self.jumpscare_map:
                print("Invalid jumpscare selected")
                return SHOW_DURATION_MS

            # Stop any existing animations and sounds first
            self.overlay.stop()
            self.sound.stop()

            # Load the resources
            gif, wav = self.jumpscare_map.get(name, (None, None))
            if not gif or not gif.exists():
                print(f"Missing or invalid GIF for {name}")
                return SHOW_DURATION_MS

            self.overlay.load_animation(gif_path=gif)

            if wav and wav.exists():
                self.sound.setSource(QUrl.fromLocalFile(str(wav)))
            else:
                self.sound.setSource(QUrl())

            return JUMPSCARE_DURATIONS.get(name, SHOW_DURATION_MS)

        except Exception as e:
            print(f"Error loading jumpscare: {e}")
            return SHOW_DURATION_MS

    def start(self):
        # Don't actually load the jumpscare yet, just validate and select one
        if self.random_checkbox.isChecked():
            available_jumpscares = list(self.jumpscare_map.keys())
            if not available_jumpscares:
                print("No jumpscares available for random selection")
                return
            name = random.choice(available_jumpscares)
            self.current_jumpscare = name
        else:
            name = self.jumpscare_select.currentText()
            if not name or name not in self.jumpscare_map:
                print("Invalid jumpscare selected")
                return
            self.current_jumpscare = name

        delay = random.randint(self.min_spin.value(), self.max_spin.value()) * 1000
        print(f"Next jumpscare in {delay/1000:.1f}s")
        self.cycle_timer.start(delay)
        self.status_label.setText("Status: ON")
        self.status_label.setStyleSheet(
            "color: green; font-weight: bold; font-size: 14px;"
        )

    def stop(self):
        self.cycle_timer.stop()
        self.overlay.stop()
        if self.sound:
            self.sound.stop()
        try:
            self.overlay.stop()
        except Exception:
            pass
        self.current_jumpscare = None  # Clear the current jumpscare
        self.status_label.setText("Status: OFF")
        self.status_label.setStyleSheet(
            "color: red; font-weight: bold; font-size: 14px;"
        )

    def _do_jumpscare(self):
        QApplication.processEvents()
        try:
            if not self.current_jumpscare and self.random_checkbox.isChecked():
                print("No jumpscare selected")
                self.stop()
                return

            # Load and prepare the jumpscare
            duration = self._load_selected_jumpscare()
            if not duration:
                print("Failed to prepare jumpscare")
                self.stop()
                return

            QApplication.processEvents()

            # Play the jumpscare
            try:
                self.sound.setLoopCount(1)
                self.sound.play()
                self.overlay.play(duration)
            except Exception as e:
                print("Error playing jumpscare:", e)
                self.stop()
                return

            # Only select new random jumpscare after current one starts successfully
            if self.random_checkbox.isChecked():
                self.current_jumpscare = random.choice(list(self.jumpscare_map.keys()))

            # Schedule next jumpscare
            delay = random.randint(self.min_spin.value(), self.max_spin.value()) * 1000
            print(f"Next jumpscare in {delay/1000:.1f}s")
            self.cycle_timer.start(delay)

        except Exception as e:
            print("Error during jumpscare sequence:", e)
            self.stop()

    def try_jumpscare(self):
        try:
            duration = self._load_selected_jumpscare()
            try:
                self.sound.setLoopCount(1)
                self.sound.play()
            except Exception:
                pass
            self.overlay.play(duration)
        except Exception as e:
            print("Error during try_jumpscare:", e)

    def closeEvent(self, event):
        self._really_quit()

    def _really_quit(self):
        self.stop()
        if self.tray:
            self.tray.hide()
        QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)
    window = JumpscareApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
