"""Widget that paints a full-bleed background pixmap."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class BackgroundScreen(QWidget):
    """Base screen with centered cover background image."""

    def __init__(self, bg_path, parent=None) -> None:
        super().__init__(parent)
        self._bg = QPixmap(str(bg_path)) if bg_path and str(bg_path) else QPixmap()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        if not self._bg.isNull():
            scaled = self._bg.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.end()
        super().paintEvent(event)
