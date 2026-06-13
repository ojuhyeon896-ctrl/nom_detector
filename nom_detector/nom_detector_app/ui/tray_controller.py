"""System tray integration for background monitoring mode."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon

from nom_detector_app import config


class TrayController:
    def __init__(
        self,
        on_show: Callable[[], None],
        on_stop_monitoring: Callable[[], None],
        on_quit: Callable[[], None],
        parent=None,
    ) -> None:
        self._on_show = on_show
        self._on_stop = on_stop_monitoring
        self._on_quit = on_quit
        self._tray: Optional[QSystemTrayIcon] = None
        self._parent = parent

    def _build_icon(self) -> QIcon:
        path = config.CAT_IDLE if config.CAT_IDLE.exists() else config.CAT_PUNCH
        if path.exists():
            pix = QPixmap(str(path)).scaled(32, 32)
            return QIcon(pix)
        pix = QPixmap(32, 32)
        pix.fill()
        return QIcon(pix)

    def ensure_created(self) -> QSystemTrayIcon:
        if self._tray is not None:
            return self._tray
        tray = QSystemTrayIcon(self._build_icon(), self._parent)
        tray.setToolTip("거북놈 · 백그라운드 모니터링 중")

        menu = QMenu()
        act_show = QAction("창 열기", menu)
        act_show.triggered.connect(self._on_show)
        act_stop = QAction("모니터링 종료", menu)
        act_stop.triggered.connect(self._on_stop)
        act_quit = QAction("앱 종료", menu)
        act_quit.triggered.connect(self._on_quit)
        menu.addAction(act_show)
        menu.addAction(act_stop)
        menu.addSeparator()
        menu.addAction(act_quit)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_activated)
        self._tray = tray
        return tray

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self._on_show()

    def show(self) -> None:
        tray = self.ensure_created()
        tray.show()

    def hide(self) -> None:
        if self._tray is not None:
            self._tray.hide()

    def show_message(self, title: str, body: str) -> None:
        tray = self.ensure_created()
        tray.showMessage(title, body, QSystemTrayIcon.Information, 2500)
