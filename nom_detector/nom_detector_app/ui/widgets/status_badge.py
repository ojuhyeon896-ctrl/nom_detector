"""Clean posture status label (no rotation / flip gimmicks)."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from nom_detector_app.core.posture import PostureLevel


class PostureStatusBadge(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusBadge")
        self.setAlignment(Qt.AlignCenter)
        self.set_state(PostureLevel.UNKNOWN)

    def set_state(self, level: PostureLevel) -> None:
        self.setProperty("nomState", level.value)
        self.style().unpolish(self)
        self.style().polish(self)
        if level == PostureLevel.UNKNOWN:
            self.setText("측정 대기 · 기준값을 먼저 등록하세요")
        else:
            self.setText(f"{level.label_ko}  [{level.value}]")
