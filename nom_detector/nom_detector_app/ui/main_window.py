"""Application shell: navigation, tray, background mode, statistics."""

from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QSystemTrayIcon

from nom_detector_app.app_settings import AppSettings
from nom_detector_app.stats.tracker import SessionStatsTracker
from nom_detector_app.ui.animations.screen_flash import ScreenFlashOverlay
from nom_detector_app.ui.screens.home import HomeScreen
from nom_detector_app.ui.screens.manual import ManualScreen
from nom_detector_app.ui.screens.monitoring import MonitoringScreen
from nom_detector_app.ui.screens.statistics import StatisticsScreen
from nom_detector_app.ui.tray_controller import TrayController


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("거북놈 · NOM Detector")
        self.resize(1100, 720)

        self.settings = AppSettings()
        self.session_stats = SessionStatsTracker()
        self.flash_overlay = ScreenFlashOverlay()

        self.tray = TrayController(
            on_show=self._tray_show_window,
            on_stop_monitoring=self._tray_stop_monitoring,
            on_quit=self._quit_application,
            parent=self,
        )

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(self.settings, self)
        self.monitoring = MonitoringScreen(self.session_stats, self.flash_overlay, self)
        self.statistics = StatisticsScreen(self.session_stats, self)
        self.manual = ManualScreen(self)

        self._idx_home = self.stack.addWidget(self.home)
        self._idx_monitor = self.stack.addWidget(self.monitoring)
        self._idx_stats = self.stack.addWidget(self.statistics)
        self._idx_manual = self.stack.addWidget(self.manual)

        self.stack.setCurrentIndex(self._idx_home)
        self._prev_stack_idx = self._idx_home
        self._in_background_shell = False

        self._wire_navigation()
        self.stack.currentChanged.connect(self._on_stack_changed)

    def _wire_navigation(self) -> None:
        self.home.btn_start.clicked.connect(self._open_monitoring)
        self.home.btn_stats.clicked.connect(self._open_statistics)
        self.home.btn_manual.clicked.connect(lambda: self.stack.setCurrentIndex(self._idx_manual))
        self.statistics.btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(self._idx_home))
        self.manual.btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(self._idx_home))
        self.monitoring.back_requested.connect(self._close_monitoring)

    def _open_monitoring(self) -> None:
        self.stack.setCurrentIndex(self._idx_monitor)

    def _open_statistics(self) -> None:
        self.statistics.refresh_chart()
        self.stack.setCurrentIndex(self._idx_stats)

    def _close_monitoring(self) -> None:
        self.monitoring.leave_page()
        self.exit_background_shell()
        self.stack.setCurrentIndex(self._idx_home)
        self.home.sync_from_settings()

    def enter_background_shell(self) -> None:
        if self._in_background_shell:
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(
                self,
                "시스템 트레이",
                "이 PC에서는 시스템 트레이를 사용할 수 없습니다.\n"
                "백그라운드 모드를 끄고 다시 시도해 주세요.",
            )
            self.settings.background_mode = False
            self.home.sync_from_settings()
            self.monitoring._background_mode = False
            self.monitoring._background_active = False
            self.monitoring._apply_foreground_ui()
            return
        self._in_background_shell = True
        QApplication.instance().setQuitOnLastWindowClosed(False)
        self.hide()
        self.tray.show()
        self.tray.show_message("거북놈", "백그라운드 모니터링이 시작되었습니다.")

    def exit_background_shell(self) -> None:
        if not self._in_background_shell:
            return
        self._in_background_shell = False
        self.tray.hide()
        self.show()
        self.raise_()
        self.activateWindow()
        if self.stack.currentIndex() != self._idx_monitor:
            QApplication.instance().setQuitOnLastWindowClosed(True)

    def _tray_show_window(self) -> None:
        self.exit_background_shell()

    def _tray_stop_monitoring(self) -> None:
        if self.stack.currentIndex() == self._idx_monitor:
            self._close_monitoring()
        else:
            self.exit_background_shell()

    def _quit_application(self) -> None:
        self.monitoring.leave_page()
        QApplication.instance().quit()

    def _on_stack_changed(self, _index: int) -> None:
        prev = self._prev_stack_idx
        now = self.stack.currentIndex()
        if prev == self._idx_monitor and now != self._idx_monitor:
            self.monitoring.leave_page()
        if now == self._idx_monitor:
            self.monitoring.enter_page()
        if now == self._idx_home:
            self.home.sync_from_settings()
        self._prev_stack_idx = self.stack.currentIndex()

    def closeEvent(self, event) -> None:
        if self._in_background_shell and self.stack.currentIndex() == self._idx_monitor:
            event.ignore()
            self.hide()
            self.tray.show_message("거북놈", "트레이에서 계속 모니터링 중입니다.")
            return
        self.monitoring.leave_page()
        super().closeEvent(event)
