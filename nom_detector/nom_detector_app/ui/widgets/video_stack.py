"""Camera preview layer with optional idle-cat wander (WARNING)."""

from __future__ import annotations

import random

from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from nom_detector_app import config
from nom_detector_app.ui.widgets.transparent_label import apply_transparent_cat_style


class VideoStack(QWidget):
    """Layers: BGR video + optional idle cat overlay."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background: #0f172a; border-radius: 8px;")
        self.video_label.setScaledContents(True)

        self.idle_cat_label = QLabel(self)
        apply_transparent_cat_style(self.idle_cat_label)
        idle = QPixmap(str(config.CAT_IDLE)) if config.CAT_IDLE.exists() else QPixmap()
        if not idle.isNull():
            idle = idle.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.idle_cat_label.setPixmap(idle)
            self.idle_cat_label.setFixedSize(idle.size())
        self.idle_cat_label.hide()

        self._wander_timer = QTimer(self)
        self._wander_timer.setInterval(int(config.CAT_WANDER_INTERVAL_MS))
        self._wander_timer.timeout.connect(self._wander_tick)
        self._wandering = False
        self._cat_x = 0.0
        self._cat_y = 0.0
        self._vx = 0.0
        self._vy = 0.0

    def set_video_visible(self, visible: bool) -> None:
        self.video_label.setVisible(visible)

    def resizeEvent(self, event) -> None:
        w, h = self.width(), self.height()
        self.video_label.setGeometry(0, 0, w, h)
        if self._wandering and not self.idle_cat_label.isHidden():
            cw = self.idle_cat_label.width()
            ch = self.idle_cat_label.height()
            if w >= cw and h >= ch:
                self._cat_x = max(0, min(self._cat_x, w - cw))
                self._cat_y = max(0, min(self._cat_y, h - ch))
                self.idle_cat_label.move(int(self._cat_x), int(self._cat_y))
        super().resizeEvent(event)

    def _spawn_wander_start(self) -> None:
        cw = self.idle_cat_label.width()
        ch = self.idle_cat_label.height()
        w, h = self.width(), self.height()
        if w <= cw + 10 or h <= ch + 10:
            self._cat_x = 0.0
            self._cat_y = 0.0
            return
        margin = 24.0
        self._cat_x = random.uniform(margin, float(w - cw - margin))
        self._cat_y = random.uniform(margin, float(h - ch - margin))
        self._vx = random.uniform(-1.4, 1.4)
        self._vy = random.uniform(-1.4, 1.4)
        self.idle_cat_label.move(int(self._cat_x), int(self._cat_y))

    def _wander_tick(self) -> None:
        if not self._wandering or self.idle_cat_label.isHidden():
            return
        self._vx += (random.random() - 0.5) * 1.0
        self._vy += (random.random() - 0.5) * 1.0
        self._vx = max(-3.5, min(3.5, self._vx)) * 0.988
        self._vy = max(-3.5, min(3.5, self._vy)) * 0.988
        self._cat_x += self._vx
        self._cat_y += self._vy
        cw = self.idle_cat_label.width()
        ch = self.idle_cat_label.height()
        w, h = self.width(), self.height()
        if w < cw or h < ch:
            return
        if self._cat_x <= 0 or self._cat_x >= w - cw:
            self._vx *= -0.75
        if self._cat_y <= 0 or self._cat_y >= h - ch:
            self._vy *= -0.75
        self._cat_x = max(0.0, min(self._cat_x, float(w - cw)))
        self._cat_y = max(0.0, min(self._cat_y, float(h - ch)))
        self.idle_cat_label.move(int(self._cat_x), int(self._cat_y))

    def stop_wander(self) -> None:
        self._wandering = False
        self._wander_timer.stop()

    def show_idle(self, show: bool) -> None:
        if not show:
            self.stop_wander()
            self.idle_cat_label.hide()
            return
        if not self.idle_cat_label.isVisible():
            self._spawn_wander_start()
        self.idle_cat_label.show()
        self.idle_cat_label.raise_()
        self._wandering = True
        self._wander_timer.start()

    def map_neck_to_stack(self, nx: int, ny: int, frame_w: int, frame_h: int) -> QPoint:
        if frame_w <= 0 or frame_h <= 0:
            return QPoint(self.width() // 2, self.height() // 2)
        sx = nx * self.width() / frame_w
        sy = ny * self.height() / frame_h
        return QPoint(int(sx), int(sy))
