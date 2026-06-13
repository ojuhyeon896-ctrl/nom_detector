"""Main home screen — centered buttons, checkbox at bottom."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QVBoxLayout

from nom_detector_app import config
from nom_detector_app.app_settings import AppSettings
from nom_detector_app.ui.widgets.background_screen import BackgroundScreen


class HomeScreen(BackgroundScreen):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(config.BG_MAIN, parent)
        self.settings = settings

        title = QLabel("거북놈")
        title.setObjectName("HeroTitle")
        title.setAlignment(Qt.AlignHCenter)

        subtitle = QLabel("NOM_detector - 바른 자세를 지켜주세요")
        subtitle.setObjectName("HeroSubtitle")
        subtitle.setAlignment(Qt.AlignHCenter)

        self.btn_start = QPushButton("모니터링 시작")
        self.btn_start.setObjectName("Primary")
        self.btn_stats = QPushButton("내 거북목 통계")
        self.btn_manual = QPushButton("사용 메뉴얼")

        for b in (self.btn_start, self.btn_stats, self.btn_manual):
            b.setMinimumHeight(52)
            b.setMinimumWidth(280)
            b.setCursor(Qt.PointingHandCursor)

        self.chk_background = QCheckBox("백그라운드 모드 켜기")
        self.chk_background.setObjectName("HomeBackgroundCheck")
        self.chk_background.setToolTip(
            "[모니터링 시작] → 카메라에서 [기준값 측정] 완료 후\n"
            "창이 숨겨지고 트레이에서 모니터링합니다.\n"
            "경고·위험 시 화면이 잠깐 깜빡입니다 (클릭·키보드 입력 통과)."
        )
        self.chk_background.setChecked(bool(settings.background_mode))
        self.chk_background.toggled.connect(self._on_background_toggled)

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 44, 40, 28)
        root.setSpacing(12)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addStretch(3)

        buttons = QVBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self.btn_start, 0, Qt.AlignHCenter)
        buttons.addWidget(self.btn_stats, 0, Qt.AlignHCenter)
        buttons.addWidget(self.btn_manual, 0, Qt.AlignHCenter)
        root.addLayout(buttons)

        root.addStretch(2)
        root.addWidget(self.chk_background, 0, Qt.AlignHCenter)
        root.addSpacing(8)

    def _on_background_toggled(self, checked: bool) -> None:
        self.settings.background_mode = bool(checked)

    def sync_from_settings(self) -> None:
        self.chk_background.blockSignals(True)
        self.chk_background.setChecked(bool(self.settings.background_mode))
        self.chk_background.blockSignals(False)
