"""Live monitoring — foreground first; tray only after calibration."""

from __future__ import annotations

from typing import List, Optional

from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from nom_detector_app import config
from nom_detector_app.core.posture import PostureLevel, classify_posture
from nom_detector_app.stats.tracker import SessionStatsTracker
from nom_detector_app.ui.animations.cat_punch import CatPunchAnimator
from nom_detector_app.ui.animations.screen_flash import ScreenFlashOverlay
from nom_detector_app.ui.widgets.status_badge import PostureStatusBadge
from nom_detector_app.ui.widgets.video_stack import VideoStack
from nom_detector_app.vision.camera_select import select_camera_index
from nom_detector_app.vision.worker import VisionWorker


class MonitoringScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(
        self,
        stats: SessionStatsTracker,
        flash_overlay: ScreenFlashOverlay,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.stats = stats
        self.flash_overlay = flash_overlay

        self._worker: Optional[VisionWorker] = None
        self._camera_index_in_use: Optional[int] = None
        self._last_frame_size = (640, 480)
        self._neck_cam: tuple[int, int] = (320, 240)
        self._baseline: Optional[float] = None
        self._calib_samples: List[float] = []
        self._calib_timer = QTimer(self)
        self._calib_timer.setSingleShot(True)
        self._calib_timer.timeout.connect(self._finish_calibration)

        self._prev_level = PostureLevel.UNKNOWN
        self._background_mode = False
        self._background_active = False

        self.stack = VideoStack(self)
        self._punch = CatPunchAnimator(self.stack)

        self.lbl_bg_hint = QLabel("백그라운드 모니터링 중 — 트레이 아이콘을 확인하세요", self.stack)
        self.lbl_bg_hint.setAlignment(Qt.AlignCenter)
        self.lbl_bg_hint.setStyleSheet(
            "color: #eceff1; font-size: 16px; font-weight: 600; "
            "background: rgba(15, 23, 42, 0.88); border-radius: 8px; padding: 28px;"
        )
        self.lbl_bg_hint.hide()
        self.lbl_bg_hint.raise_()

        self.status_badge = PostureStatusBadge(self)
        self.btn_calibrate = QPushButton("기준값 측정 (3초)")
        self.btn_back = QPushButton("모니터링 종료")
        for b in (self.btn_calibrate, self.btn_back):
            b.setMinimumHeight(44)
            b.setCursor(Qt.PointingHandCursor)

        top = QHBoxLayout()
        top.addWidget(self.status_badge, 1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 20)
        lay.setSpacing(12)
        lay.addLayout(top)
        lay.addWidget(self.stack, 1)
        row = QHBoxLayout()
        row.addWidget(self.btn_calibrate)
        row.addStretch(1)
        row.addWidget(self.btn_back)
        lay.addLayout(row)

        self.btn_calibrate.clicked.connect(self._start_calibration)
        self.btn_back.clicked.connect(self.back_requested.emit)

    def _main_window(self):
        return self.window()

    def _wants_background_mode(self) -> bool:
        win = self._main_window()
        if win is not None and hasattr(win, "settings"):
            return bool(win.settings.background_mode)
        return False

    def enter_page(self) -> None:
        self._background_mode = self._wants_background_mode()
        self._background_active = False
        self._prev_level = PostureLevel.UNKNOWN
        self.status_badge.set_state(PostureLevel.UNKNOWN)
        self.stats.start()

        chosen, _ = select_camera_index(config.DEFAULT_CAMERA_INDEX)
        self._camera_index_in_use = chosen
        if chosen is None:
            QMessageBox.warning(
                self,
                "카메라",
                "카메라를 열 수 없습니다. 연결 상태를 확인한 뒤 다시 시도해 주세요.",
            )
            self.leave_page()
            self.back_requested.emit()
            return

        self._baseline = None
        self._apply_foreground_ui()
        self._start_worker()

    def leave_page(self) -> None:
        self._calib_timer.stop()
        self._punch.stop()
        self._stop_worker()
        self.stack.video_label.clear()
        self.stack.show_idle(False)
        self.stats.set_state(PostureLevel.UNKNOWN)
        self.stats.stop()
        self._background_active = False

        win = self._main_window()
        if win is not None and hasattr(win, "exit_background_shell"):
            win.exit_background_shell()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.lbl_bg_hint.setGeometry(0, 0, self.stack.width(), self.stack.height())

    def _apply_foreground_ui(self) -> None:
        self.stack.set_video_visible(True)
        self.lbl_bg_hint.hide()

    def _apply_background_ui(self) -> None:
        self.stack.set_video_visible(False)
        self.lbl_bg_hint.setGeometry(0, 0, self.stack.width(), self.stack.height())
        self.lbl_bg_hint.show()
        self.lbl_bg_hint.raise_()

    def _activate_background_after_calibration(self) -> None:
        if not self._wants_background_mode():
            return
        self._background_mode = True
        self._background_active = True
        self._apply_background_ui()
        win = self._main_window()
        if win is not None and hasattr(win, "enter_background_shell"):
            win.enter_background_shell()

    def _start_worker(self) -> None:
        self._stop_worker()
        index = self._camera_index_in_use if self._camera_index_in_use is not None else 0
        self._worker = VisionWorker(index, self)
        self._worker.frame_ready.connect(self._on_frame)
        self._worker.angle_ready.connect(self._on_angle)
        self._worker.neck_screen_pos.connect(self._on_neck_pos)
        self._worker.pose_lost.connect(self._on_pose_lost)
        self._worker.fatal_error.connect(self._on_vision_fatal)
        self._worker.start()

    def _stop_worker(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(3000)
            self._worker = None

    def _on_frame(self, img) -> None:
        self._last_frame_size = (img.width(), img.height())
        if not self._background_active:
            self.stack.video_label.setPixmap(QPixmap.fromImage(img))

    def _on_neck_pos(self, x: int, y: int) -> None:
        self._neck_cam = (x, y)

    def _on_pose_lost(self) -> None:
        self._apply_level(PostureLevel.UNKNOWN)

    def _on_vision_fatal(self, message: str) -> None:
        QMessageBox.critical(self, "거북놈 — 카메라/비전", message)
        self.leave_page()
        self.back_requested.emit()

    def _on_angle(self, angle: float) -> None:
        if self._calib_timer.isActive():
            self._calib_samples.append(float(angle))
            return
        level = classify_posture(angle, self._baseline)
        self._apply_level(level)

    def _apply_level(self, level: PostureLevel) -> None:
        edge = level != self._prev_level
        self.stats.set_state(level)
        self.status_badge.set_state(level)

        if self._background_active:
            if edge and level in (PostureLevel.WARNING, PostureLevel.DANGER):
                self.flash_overlay.flash(level)
            self._prev_level = level
            return

        if level == PostureLevel.UNKNOWN:
            self.stack.show_idle(False)
            self._prev_level = level
            return

        if level == PostureLevel.DANGER:
            self.stack.show_idle(False)
            if edge and not self._punch.is_running():
                fw, fh = self._last_frame_size
                neck = self.stack.map_neck_to_stack(self._neck_cam[0], self._neck_cam[1], fw, fh)
                self._punch.play(neck)
        elif level == PostureLevel.WARNING:
            self.stack.show_idle(True)
        else:
            self.stack.show_idle(False)

        self._prev_level = level

    def _start_calibration(self) -> None:
        if self._worker is not None:
            self._worker.reset_filter()
        self._calib_samples.clear()
        self._calib_timer.start(int(config.CALIBRATION_SECONDS * 1000))
        self.btn_calibrate.setEnabled(False)
        self.btn_calibrate.setText("측정 중… (3초)")

    def _finish_calibration(self) -> None:
        self.btn_calibrate.setEnabled(True)
        self.btn_calibrate.setText("기준값 측정 (3초)")
        if not self._calib_samples:
            QMessageBox.information(
                self,
                "기준값",
                "유효한 자세 데이터가 충분하지 않습니다. 다시 시도해 주세요.",
            )
            return

        self._baseline = sum(self._calib_samples) / len(self._calib_samples)
        self._prev_level = PostureLevel.UNKNOWN

        if self._wants_background_mode():
            QMessageBox.information(
                self,
                "기준값",
                f"바른 자세 기준값이 저장되었습니다. (평균 {self._baseline:.1f}°)\n\n"
                "백그라운드 모드로 전환합니다. 트레이 아이콘에서 계속 확인할 수 있습니다.",
            )
            self._activate_background_after_calibration()
        else:
            QMessageBox.information(
                self,
                "기준값",
                f"바른 자세 기준값이 저장되었습니다.\n평균 각도: {self._baseline:.1f}°",
            )
