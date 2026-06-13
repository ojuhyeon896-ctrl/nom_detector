"""Fullscreen click-through flash overlay for background mode."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget

from nom_detector_app import config
from nom_detector_app.core.posture import PostureLevel


class ScreenFlashOverlay(QWidget):
    """
    Covers the primary screen with a semi-transparent color and fades 2–3 times.

    Mouse clicks pass through (``Qt.WindowTransparentForInput``).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowTransparentForInput
            | Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self._opacity = 0.0
        self._fill = QColor(255, 152, 0, 120)
        self._anim: Optional[QPropertyAnimation] = None
        self._cycles_done = 0

    def get_opacity(self) -> float:
        return self._opacity

    def set_opacity(self, value: float) -> None:
        self._opacity = max(0.0, min(1.0, float(value)))
        self.update()

    opacity_prop = pyqtProperty(float, get_opacity, set_opacity)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = QColor(self._fill)
        c.setAlpha(int(self._opacity * c.alpha()))
        painter.fillRect(self.rect(), c)
        painter.end()

    def flash(self, level: PostureLevel) -> None:
        if level == PostureLevel.WARNING:
            self._fill = QColor(255, 152, 0, 120)
        elif level == PostureLevel.DANGER:
            self._fill = QColor(229, 57, 53, 130)
        else:
            return

        screen = QApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())

        self._cycles_done = 0
        self._opacity = 0.0
        self.show()
        self._fade_in()

    def _fade_in(self) -> None:
        self._start_anim(0.0, 0.78, QEasingCurve.OutCubic, self._fade_out)

    def _fade_out(self) -> None:
        self._start_anim(self._opacity, 0.0, QEasingCurve.InCubic, self._cycle_done)

    def _cycle_done(self) -> None:
        self._cycles_done += 1
        if self._cycles_done >= int(config.FLASH_PULSE_COUNT):
            self.hide()
            return
        self._fade_in()

    def _start_anim(self, start: float, end: float, curve, done_slot) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim.deleteLater()
        anim = QPropertyAnimation(self, b"opacity_prop", self)
        anim.setDuration(360)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(curve)
        anim.finished.connect(done_slot)
        self._anim = anim
        anim.start()
