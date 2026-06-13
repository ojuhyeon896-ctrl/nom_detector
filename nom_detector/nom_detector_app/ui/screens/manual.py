"""Usage manual — posture guide (1 step) + app walkthrough (5 steps)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nom_detector_app import config
from nom_detector_app.ui.widgets.background_screen import BackgroundScreen


class ManualScreen(BackgroundScreen):
    def __init__(self, parent=None) -> None:
        super().__init__(config.BG_SUB, parent)

        self.btn_back = QPushButton("뒤로 가기")
        self.btn_back.setMinimumHeight(48)
        self.btn_back.setCursor(Qt.PointingHandCursor)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 8, 0)
        content_lay.setSpacing(22)

        title = QLabel("사용 메뉴얼")
        title.setObjectName("ScreenTitle")
        content_lay.addWidget(title)

        content_lay.addWidget(self._section_title("올바른 자세 가이드"))
        content_lay.addWidget(self._posture_card())

        self._how_section_title = self._section_title("앱 사용 방법")
        content_lay.addWidget(self._how_section_title)

        for idx, (path, caption) in enumerate(config.HOW_TO_USE):
            content_lay.addWidget(self._make_step_card(path, caption, idx + 1))

        content_lay.addStretch(1)
        scroll.setWidget(content)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.addWidget(scroll, 1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btn_back)
        root.addLayout(row)

    @staticmethod
    def _section_title(text: str) -> QLabel:
        lab = QLabel(text)
        lab.setObjectName("SectionTitle")
        return lab

    def _posture_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame {"
            "  background: rgba(255,255,255,0.88);"
            "  border-radius: 10px;"
            "  border: 1px solid rgba(30,107,168,0.15);"
            "}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        cap = QLabel(config.POSTURE_GUIDE_TEXT)
        cap.setObjectName("ManualCaption")
        cap.setWordWrap(True)
        lay.addWidget(cap)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        path = config.POSTURE_GUIDE_IMAGE
        pix = QPixmap(str(path)) if path.exists() else QPixmap()
        if pix.isNull():
            img.setText("posture_guide.png")
            img.setMinimumHeight(220)
            img.setStyleSheet(
                "background: rgba(240,244,248,0.9); border-radius: 8px; "
                "color: #78909c; font-size: 15px; padding: 48px;"
            )
        else:
            scaled = pix.scaled(640, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(scaled)
            img.setMinimumHeight(scaled.height() + 8)
        lay.addWidget(img)

        return card

    def _make_step_card(self, path: Path, caption: str, step: int) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame {"
            "  background: rgba(255,255,255,0.82);"
            "  border-radius: 10px;"
            "  border: 1px solid rgba(30,107,168,0.15);"
            "}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setMinimumHeight(200)
        pix = QPixmap(str(path)) if path.exists() else QPixmap()
        if pix.isNull():
            img.setText(path.name)
            img.setStyleSheet(
                "background: rgba(240,244,248,0.9); border-radius: 8px; "
                "color: #78909c; font-size: 14px; padding: 40px;"
            )
        else:
            scaled = pix.scaled(560, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(scaled)
            img.setMinimumHeight(scaled.height() + 8)

        text_row = QHBoxLayout()
        text_row.setSpacing(10)
        badge = QLabel(str(step))
        badge.setObjectName("ManualStep")
        badge.setAlignment(Qt.AlignTop)
        badge.setFixedWidth(28)
        cap = QLabel(caption)
        cap.setObjectName("ManualCaption")
        cap.setWordWrap(True)
        text_row.addWidget(badge)
        text_row.addWidget(cap, 1)

        lay.addWidget(img)
        lay.addLayout(text_row)
        return card
