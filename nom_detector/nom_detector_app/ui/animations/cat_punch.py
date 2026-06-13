"""DANGER punch: transparent PNG cat flies to neck with OutBounce."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt5.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, pyqtProperty
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from nom_detector_app import config
from nom_detector_app.ui.widgets.transparent_label import apply_transparent_cat_style


class _PunchLabel(QLabel):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        apply_transparent_cat_style(self)

    def get_pos(self) -> QPoint:
        return self.pos()

    def set_pos(self, p: QPoint) -> None:
        self.move(p)

    pos_prop = pyqtProperty(QPoint, get_pos, set_pos)


class CatPunchAnimator:
    def __init__(self, host: QWidget, on_finished: Optional[Callable[[], None]] = None) -> None:
        self._host = host
        self._on_finished = on_finished
        self._label = _PunchLabel(host)
        self._label.hide()
        self._anim: Optional[QPropertyAnimation] = None
        self._load_pixmap()

    def _load_pixmap(self) -> None:
        punch = QPixmap(str(config.CAT_PUNCH)) if config.CAT_PUNCH.exists() else QPixmap()
        if punch.isNull():
            return
        scaled = punch.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._label.setPixmap(scaled)
        self._label.setFixedSize(scaled.size())

    def is_running(self) -> bool:
        return self._anim is not None and self._anim.state() == QPropertyAnimation.Running

    def stop(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim.deleteLater()
            self._anim = None
        self._label.hide()

    def play(self, neck_center: QPoint) -> None:
        if self._label.pixmap() is None or self._label.pixmap().isNull():
            if self._on_finished:
                self._on_finished()
            return

        self.stop()
        pw = self._label.width()
        ph = self._label.height()
        end = QPoint(int(neck_center.x() - pw / 2), int(neck_center.y() - ph / 2))
        start = self._offscreen_start(neck_center, end)

        self._label.move(start)
        self._label.show()
        self._label.raise_()

        anim = QPropertyAnimation(self._label, b"pos_prop", self._host)
        anim.setDuration(int(config.CAT_PUNCH_ANIM_MS))
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.finished.connect(self._finish)
        self._anim = anim
        anim.start()

    def _offscreen_start(self, neck: QPoint, end: QPoint) -> QPoint:
        w, h = self._host.width(), self._host.height()
        pw, ph = self._label.width(), self._label.height()
        candidates = [
            QPoint(-pw - 48, end.y()),
            QPoint(w + 48, end.y()),
            QPoint(end.x(), -ph - 48),
            QPoint(end.x(), h + 48),
        ]

        def dist2(a: QPoint, b: QPoint) -> int:
            return (a.x() - b.x()) ** 2 + (a.y() - b.y()) ** 2

        return max(candidates, key=lambda p: dist2(p, neck))

    def _finish(self) -> None:
        self._anim = None
        self._label.hide()
        if self._on_finished:
            self._on_finished()
