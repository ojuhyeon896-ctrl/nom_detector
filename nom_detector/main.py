"""Entry point for 거북놈 (NOM Detector)."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nom_detector_app.ui.main_window import MainWindow  # noqa: E402
from nom_detector_app.stats.matplotlib_font import configure_matplotlib_korean_font  # noqa: E402
from nom_detector_app.ui.styles import apply_app_style  # noqa: E402


def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    configure_matplotlib_korean_font()
    app = QApplication(sys.argv)
    app.setApplicationName("거북놈")
    app.setOrganizationName("NOMDetector")
    apply_app_style(app)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.information(
            None,
            "거북놈",
            "시스템 트레이를 사용할 수 없는 환경입니다.\n"
            "백그라운드 모드는 비활성화됩니다.",
        )

    win = MainWindow()
    win.show()
    return int(app.exec_())


if __name__ == "__main__":
    raise SystemExit(main())
